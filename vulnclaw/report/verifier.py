"""VulnClaw Vulnerability Verifier — validate findings before they enter the report.

Principio central: vulnerabilidad no verificada = falso positivo = no se incluye en el informe

Flujo de trabajo:
    1. Recibir la hipótesis de vulnerabilidad (pending finding)
    2. Generar el código PoC
    3. Ejecutar el PoC mediante python_execute
    4. Determinar el resultado: verified / rejected
    5. Solo las vulnerabilidades verified pueden incluirse en el informe
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: Eliminación de la infracción V2 — los tipos hoja se movieron a
#          config/domain_models.py.
from vulnclaw.config.domain_models import VulnerabilityFinding


class VerificationStatus(str, Enum):
    """Estado de verificación de la vulnerabilidad."""

    PENDING = "pending"  # Pendiente de verificación
    VERIFIED = "verified"  # Verificación aprobada
    REJECTED = "rejected"  # Verificación fallida/falso positivo
    SKIPPED = "skipped"  # Verificación omitida (p. ej. hecho ya confirmado)


class VerificationResult(str, Enum):
    """Detalle del resultado de la verificación."""

    # Verified outcomes
    VULN_CONFIRMED = "vuln_confirmed"  # Vulnerabilidad confirmada
    SENSITIVE_DATA_EXPOSED = "sensitive_data"  # Fuga de datos sensibles
    SECURITY_BYPASS = "security_bypass"  # Evasión de restricciones de seguridad

    # Rejected outcomes
    FALSE_POSITIVE = "false_positive"  # Falso positivo
    NO_RESPONSE_DIFF = "no_response_diff"  # Sin diferencia en la respuesta
    PARAM_INVALID = "param_invalid"  # Parámetro inválido
    NORMAL_RESPONSE = "normal_response"  # Respuesta normal
    TIMEOUT = "timeout"  # Tiempo de espera agotado
    ERROR_403_404 = "error_403_404"  # Rechazo normal 403/404
    EXECUTION_ERROR = "execution_error"  # Error del entorno de ejecución del PoC (p. ej. intérprete ausente)


@dataclass
class VerifiedFinding:
    """Hallazgo de vulnerabilidad ya verificado."""

    # Información proveniente del finding original
    original_finding: VulnerabilityFinding

    # Estado de verificación
    status: VerificationStatus = VerificationStatus.PENDING
    result: Optional[VerificationResult] = None

    # Información del PoC
    poc_code: Optional[str] = None
    poc_output: Optional[str] = None
    poc_executed_at: Optional[str] = None

    # Conclusión de la verificación
    verified_description: str = ""
    verified_evidence: str = ""
    verified_severity: str = ""  # Puede ajustarse según el resultado de la verificación

    # Motivo de exclusión (si la verificación falla)
    rejection_reason: str = ""

    # Verificador (metainformación)
    verified_by: str = "verifier_module"
    verified_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ── Generador de PoC ────────────────────────────────────────────────────────────────


class PoCGenerator:
    """Genera código PoC a partir de una hipótesis de vulnerabilidad."""

    # Mapeo de tipo de vulnerabilidad → plantilla de PoC
    #
    # ⚠️ Las plantillas usan *llaves simples* como sintaxis de Python (literales
    # dict, interpolación f-string). Los únicos marcadores de plantilla son
    # ``{target}`` / ``{payload}`` / ``{baseline_len}`` / ``{path}``, que
    # :meth:`generate_poc` sustituye con precisión mediante ``str.replace``.
    # No usar el escape ``{{`` / ``}}`` — el renderizador no es ``str.format``;
    # las llaves dobles quedarían literalmente en el PoC generado, provocando
    # que un literal ``dict`` se convierta en ``set`` (``TypeError``) o que un
    # f-string imprima el texto literal ``{var}`` en lugar del valor interpolado.
    POC_TEMPLATES: dict[str, str] = {
        "sql_injection": """
import requests

target = "{target}"
params = {
    "id": "{payload}",
}

try:
    r = requests.get(target, params=params, timeout=10, verify=False)
    text = r.text.lower()

    # Firmas de error SQL
    sql_errors = [
        "sql syntax", "mysql", "sqlite", "postgres", "oracle",
        "sqlstate", "microsoft sql", "odbc", "syntax error",
        "you have an error in your sql", "warning: mysql",
    ]

    for err in sql_errors:
        if err in text:
            print(f"[CONFIRMED] Vulnerabilidad de inyección SQL: se detectó la firma de error SQL '{err}'")
            print(f"[INFO] Código de estado de la respuesta: {r.status_code}")
            exit(0)

    # Comprobar diferencia en la respuesta (si se proporciona un baseline normal)
    baseline_len = {baseline_len}
    if len(r.content) != baseline_len and baseline_len > 0:
        print(f"[POSSIBLE] Longitud de respuesta anómala: {len(r.content)} vs baseline {baseline_len}")

    print("[REJECTED] No se detectaron firmas de inyección SQL")
except requests.Timeout:
    print("[REJECTED] Tiempo de espera de la solicitud agotado")
except Exception as e:
    print(f"[ERROR] {e}")
""",
        "xss": """
import requests

target = "{target}"
payload = "{payload}"

try:
    r = requests.get(target, params={"q": payload}, timeout=10, verify=False)

    if payload in r.text:
        print("[CONFIRMED] Vulnerabilidad XSS: el payload aparece en la respuesta")
        print("[INFO] Payload XSS enviado; se detectó reflexión tal cual")
        exit(0)

    print("[REJECTED] El payload XSS no apareció en la respuesta")
except Exception as e:
    print(f"[ERROR] {e}")
""",
        "command_injection": """
import requests

target = "{target}"
params = {
    "cmd": "{payload}",
}

try:
    r = requests.get(target, params=params, timeout=10, verify=False)
    text = r.text

    # Firmas de inyección de comandos
    cmd_indicators = ["uid=", "gid=", "root:", "/bin/bash", "whoami", "linux"]

    for indicator in cmd_indicators:
        if indicator in text:
            print(f"[CONFIRMED] Vulnerabilidad de inyección de comandos: se detectó '{indicator}'")
            exit(0)

    print("[REJECTED] No se detectaron firmas de inyección de comandos")
except Exception as e:
    print(f"[ERROR] {e}")
""",
        "debug_mode": """
import requests

target = "{target}"

try:
    # Solicitud normal
    r_normal = requests.get(target, timeout=10, verify=False)
    len_normal = len(r_normal.content)

    # Solicitud en modo debug
    r_debug = requests.get(target + "/?debug=1", timeout=10, verify=False)
    len_debug = len(r_debug.content)

    print(f"[INFO] Longitud de respuesta normal: {len_normal}")
    print(f"[INFO] Longitud de respuesta con debug=1: {len_debug}")

    # Comprobar fuga de información de depuración
    if len_debug != len_normal:
        diff = len_debug - len_normal
        print(f"[POSSIBLE] La respuesta en modo debug difiere de la normal, diferencia: {diff} bytes")

        # Comprobar si realmente se filtra información sensible
        debug_content = r_debug.text.replace(r_normal.text, "")
        if debug_content:
            sensitive_keywords = ["password", "secret", "api_key", "token", "db_", "connection"]
            for kw in sensitive_keywords:
                if kw.lower() in debug_content.lower():
                    print(f"[CONFIRMED] El modo debug filtra información sensible: se detectó '{kw}'")
                    exit(0)

        # Si solo hay diferencia de longitud sin información sensible, degradar a Info
        print("[INFO] La respuesta en modo debug difiere pero no se encontró fuga de información sensible; se degrada a Info")

    # Comprobar palabras clave relacionadas con debug
    if "debug" in r_debug.text.lower() and r_debug.text.lower().count("debug") > r_normal.text.lower().count("debug"):
        print("[POSSIBLE] El modo debug contiene información adicional de depuración")

    print("[REJECTED] No se encontró fuga evidente de información sensible en el modo debug")

except Exception as e:
    print(f"[ERROR] {e}")
""",
        "lfi": """
import requests

target = "{target}"
payload = "{payload}"

try:
    r = requests.get(target, params={"file": payload}, timeout=10, verify=False)
    text = r.text.lower()

    # Firmas de LFI
    lfi_indicators = ["root:", "/bin/bash", "/bin/sh", "[boot loader]", "windows"]

    for indicator in lfi_indicators:
        if indicator in text:
            print(f"[CONFIRMED] Vulnerabilidad LFI: se detectó '{indicator}'")
            exit(0)

    print("[REJECTED] No se detectaron firmas de LFI")
except Exception as e:
    print(f"[ERROR] {e}")
""",
        "sensitive_file": """
import requests

target = "{target}"
path = "{path}"

try:
    r = requests.get(target + path, timeout=10, verify=False)

    if r.status_code == 200 and len(r.content) > 10:
        print(f"[CONFIRMED] Archivo sensible accesible: {path}")
        print(f"[INFO] Código de estado: {r.status_code}, longitud: {len(r.content)}")

        # Comprobar el tipo de contenido
        ct = r.headers.get("content-type", "")
        print(f"[INFO] Content-Type: {ct}")

        exit(0)

    print(f"[REJECTED] Archivo no accesible o vacío: {r.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")
""",
        "info_disclosure": """
import requests

target = "{target}"

try:
    r = requests.get(target, timeout=10, verify=False)
    headers = {k.lower(): v.lower() for k, v in r.headers.items()}

    # Comprobar headers sensibles
    sensitive_headers = {
        "x-powered-by": "Información de la pila tecnológica",
        "server": "Información del servidor",
        "x-aspnet-version": "Versión de ASP.NET",
        "x-generator": "Información del generador",
    }

    found = []
    for header, desc in sensitive_headers.items():
        if header in headers:
            found.append(f"{header}: {headers[header][:50]}")

    if found:
        print(f"[CONFIRMED] Fuga de información: {len(found)} headers sensibles")
        for item in found:
            print(f"  - {item}")
        exit(0)

    print("[INFO] No se encontró fuga de información evidente; es un problema de configuración normal")
    print("[REJECTED] Fuga de información en los headers de respuesta - es un problema de configuración, no una vulnerabilidad")
except Exception as e:
    print(f"[ERROR] {e}")
""",
    }

    @classmethod
    def generate_poc(
        cls,
        finding: VulnerabilityFinding,
        target: str,
        baseline_len: int = 0,
    ) -> str:
        """Genera el código PoC según el tipo de vulnerabilidad.

        Args:
            finding: Hallazgo de vulnerabilidad
            target: URL objetivo
            baseline_len: Longitud de la respuesta normal (para comparación)

        Returns:
            Cadena de código Python del PoC
        """
        vuln_type = (finding.vuln_type or "").lower().replace(" ", "_")
        template = cls.POC_TEMPLATES.get(vuln_type)

        if not template:
            # Plantilla de PoC genérica
            template = cls._generic_template()

        payload = cls._guess_payload(finding)
        replacements = {
            "{target}": target,
            "{payload}": payload,
            "{baseline_len}": str(baseline_len),
            "{path}": payload,
        }
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        return template

    @classmethod
    def _generic_template(cls) -> str:
        """Genera una plantilla de PoC genérica.

        Se usa cuando el tipo de vulnerabilidad no tiene una plantilla dedicada.
        Realiza una verificación heurística sobre parámetros de inyección comunes
        comparando la respuesta base con la respuesta tras inyectar el payload:
        detección de reflexión, escaneo de firmas de error/sensibles, y
        diferencias de código de estado/longitud de respuesta, e imprime
        marcadores ``[CONFIRMED]`` / ``[POSSIBLE]`` / ``[REJECTED]`` consistentes
        con :meth:`VerifierExecutor.parse_result`.
        """
        return """
import requests

target = "{target}"
payload = "{payload}"

# Nombres de parámetros inyectables comunes; se prueba el payload en cada uno
# y se compara con la respuesta base
CANDIDATE_PARAMS = ["id", "q", "search", "name", "file", "page", "cmd", "url"]

# Firmas genéricas de error / información sensible
SIGNATURES = [
    "sql syntax", "sqlstate", "mysql", "odbc", "you have an error in your sql",
    "traceback (most recent call last)", "stack trace", "fatal error",
    "warning:", "exception", "root:", "/bin/bash", "uid=", "gid=",
]


def fetch(params=None):
    return requests.get(target, params=params, timeout=10, verify=False)


try:
    baseline = fetch()
    base_status = baseline.status_code
    base_len = len(baseline.content)
    print(f"[*] Respuesta base: status={base_status}, len={base_len}")

    confirmed = False
    for name in CANDIDATE_PARAMS:
        try:
            r = fetch(params={name: payload})
        except Exception:
            continue

        # 1) Detección de reflexión: el payload aparece tal cual en la respuesta (posible XSS / inyección de plantillas)
        if payload and payload in r.text:
            print(f"[CONFIRMED] El payload fue reflejado tal cual en la respuesta a través del parámetro '{name}'")
            confirmed = True
            break

        # 2) Escaneo de firmas de error / información sensible
        low = r.text.lower()
        hit = next((s for s in SIGNATURES if s in low), None)
        if hit:
            print(f"[CONFIRMED] El parámetro '{name}' desencadenó una firma anómala/sensible: '{hit}'")
            confirmed = True
            break

        # 3) Diferencia de respuesta: cambio de código de estado o de longitud significativa
        if r.status_code != base_status:
            print(f"[POSSIBLE] El parámetro '{name}' cambió el código de estado de la respuesta: {base_status} -> {r.status_code}")
        elif base_len and abs(len(r.content) - base_len) > max(50, int(base_len * 0.2)):
            print(f"[POSSIBLE] El parámetro '{name}' cambió significativamente la longitud de la respuesta: {base_len} -> {len(r.content)}")

    if not confirmed:
        print("[REJECTED] La verificación genérica no detectó firmas claras de vulnerabilidad")

except requests.Timeout:
    print("[REJECTED] Tiempo de espera de la solicitud agotado")
except Exception as e:
    print(f"[ERROR] {e}")
"""

    @classmethod
    def _guess_payload(cls, finding: VulnerabilityFinding) -> str:
        """Adivina el payload según el tipo de vulnerabilidad."""
        vuln_type = (finding.vuln_type or "").lower()

        payloads = {
            "sql": "1' OR '1'='1",
            "xss": "<script>alert(1)</script>",
            "command": ";id",
            "lfi": "../../../etc/passwd",
        }

        for key, payload in payloads.items():
            if key in vuln_type:
                return payload

        return "test"


# ── Ejecutor de verificación ───────────────────────────────────────────────────────────────


class VerifierExecutor:
    """Ejecuta la verificación del PoC y determina el resultado."""

    # Ruta del intérprete Python: se usa el intérprete en ejecución actual para
    # evitar que "python" no exista en entornos que solo tienen "python3",
    # lo cual daría un falso fallo en la verificación de la vulnerabilidad.
    PYTHON_CMD = sys.executable or "python"

    @classmethod
    def execute_poc(cls, poc_code: str, timeout: int = 30) -> tuple[int, str]:
        """Ejecuta el código del PoC.

        Args:
            poc_code: Código Python del PoC
            timeout: Segundos de tiempo de espera

        Returns:
            (código de retorno, contenido de la salida)
        """
        # Escribir en un archivo temporal
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(poc_code)
            temp_path = f.name

        try:
            # Ejecutar el PoC
            result = subprocess.run(
                [cls.PYTHON_CMD, temp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout + result.stderr
            return result.returncode, output

        except subprocess.TimeoutExpired:
            return -1, "[TIMEOUT] Tiempo de espera agotado en la ejecución del PoC"
        except FileNotFoundError:
            return -2, f"[ERROR] No se encontró el intérprete de Python: {cls.PYTHON_CMD}"
        except Exception as e:
            return -3, f"[ERROR] Fallo en la ejecución: {e}"
        finally:
            # Limpiar el archivo temporal
            try:
                Path(temp_path).unlink()
            except Exception:
                pass

    @classmethod
    def parse_result(cls, output: str, returncode: int) -> VerificationResult:
        """Analiza la salida del PoC y determina el resultado de la verificación.

        Args:
            output: Contenido de la salida del PoC
            returncode: Código de retorno

        Returns:
            Resultado de la verificación
        """
        output_lower = output.lower()

        # Fallo de ejecución
        if returncode == -1:
            return VerificationResult.TIMEOUT
        if returncode in (-2, -3):
            # -2: falta el intérprete de Python; -3: la propia ejecución del PoC
            # lanzó una excepción. Ambos son problemas del entorno de ejecución,
            # no un 403/404 devuelto por el objetivo.
            return VerificationResult.EXECUTION_ERROR
        if returncode != 0:
            return VerificationResult.FALSE_POSITIVE

        # Comprobar marcador de confirmación
        if "[CONFIRMED]" in output or "[VERIFIED]" in output:
            if "敏感信息" in output or "información sensible" in output_lower or "sensitive" in output_lower:
                return VerificationResult.SENSITIVE_DATA_EXPOSED
            if "绕过" in output or "evasión" in output_lower or "bypass" in output_lower:
                return VerificationResult.SECURITY_BYPASS
            return VerificationResult.VULN_CONFIRMED

        # Comprobar marcador de rechazo
        if "[REJECTED]" in output or "[FALSE]" in output:
            return VerificationResult.FALSE_POSITIVE

        # Comprobar diferencia en la respuesta
        if "[POSSIBLE]" in output:
            return VerificationResult.NO_RESPONSE_DIFF

        # Comprobar respuesta normal
        if returncode == 0 and "[CONFIRMED]" not in output:
            return VerificationResult.NORMAL_RESPONSE

        return VerificationResult.FALSE_POSITIVE


# ── Verificador principal ────────────────────────────────────────────────────────────────


class VulnerabilityVerifier:
    """Verificador de vulnerabilidades — flujo de verificación central."""

    def __init__(self, target: str, baseline_len: int = 0) -> None:
        """Inicializa el verificador.

        Args:
            target: URL objetivo
            baseline_len: Longitud de la respuesta normal
        """
        self.target = target
        self.baseline_len = baseline_len
        self.verified_findings: list[VerifiedFinding] = []
        self.rejected_findings: list[VerifiedFinding] = []

    def verify(self, finding: VulnerabilityFinding) -> VerifiedFinding:
        """Verifica un hallazgo de vulnerabilidad.

        Args:
            finding: Hallazgo de vulnerabilidad

        Returns:
            Hallazgo verificado (con estado y evidencia)
        """
        vf = VerifiedFinding(original_finding=finding)

        # Generar el PoC
        poc_code = PoCGenerator.generate_poc(
            finding=finding,
            target=self.target,
            baseline_len=self.baseline_len,
        )
        vf.poc_code = poc_code

        # Ejecutar el PoC
        returncode, output = VerifierExecutor.execute_poc(poc_code)
        vf.poc_output = output
        vf.poc_executed_at = datetime.now().isoformat()

        # Analizar el resultado
        result = VerifierExecutor.parse_result(output, returncode)
        vf.result = result

        # Determinar el estado según el resultado
        if result in (
            VerificationResult.VULN_CONFIRMED,
            VerificationResult.SENSITIVE_DATA_EXPOSED,
            VerificationResult.SECURITY_BYPASS,
        ):
            vf.status = VerificationStatus.VERIFIED
            vf._build_verified_finding(output)
        else:
            vf.status = VerificationStatus.REJECTED
            vf._build_rejected_finding(result, output)

        # Almacenar clasificado
        if vf.status == VerificationStatus.VERIFIED:
            self.verified_findings.append(vf)
        else:
            self.rejected_findings.append(vf)

        return vf

    def verify_batch(self, findings: list[VulnerabilityFinding]) -> list[VerifiedFinding]:
        """Verifica hallazgos de vulnerabilidad en lote.

        Args:
            findings: Lista de hallazgos de vulnerabilidad

        Returns:
            Lista de hallazgos verificados (solo incluye los verified)
        """
        verified = []

        for finding in findings:
            vf = self.verify(finding)
            if vf.status == VerificationStatus.VERIFIED:
                verified.append(vf)

        return verified

    def _build_verified_finding(self, output: str) -> None:
        """Construye el detalle del hallazgo que pasó la verificación."""
        vf = self.verified_findings[-1] if self.verified_findings else None
        if not vf:
            return

        original = vf.original_finding

        # Extraer la información de confirmación de la salida
        confirmed_lines = [
            line.strip()
            for line in output.split("\n")
            if "[CONFIRMED]" in line or "[VERIFIED]" in line
        ]

        vf.verified_description = (
            f"Verificación con PoC aprobada. Descripción original: {original.description}"
            if original.description
            else "La verificación con PoC confirmó la existencia de la vulnerabilidad"
        )
        vf.verified_evidence = "\n".join(confirmed_lines) if confirmed_lines else output[:500]
        vf.verified_severity = original.severity  # Se mantiene la severidad original, se puede ajustar según el resultado

    def _build_rejected_finding(
        self,
        result: VerificationResult,
        output: str,
    ) -> None:
        """Construye el detalle del hallazgo que falló la verificación."""
        vf = self.rejected_findings[-1] if self.rejected_findings else None
        if not vf:
            return

        original = vf.original_finding

        # Mapeo de motivos de exclusión
        rejection_reasons = {
            VerificationResult.FALSE_POSITIVE: "No se detectaron firmas de vulnerabilidad tras ejecutar el PoC; se determinó como falso positivo",
            VerificationResult.NO_RESPONSE_DIFF: "Sin diferencia en la respuesta; el parámetro es inválido o no se activó la vulnerabilidad",
            VerificationResult.PARAM_INVALID: "Parámetro inválido; no fue posible verificar la hipótesis de vulnerabilidad",
            VerificationResult.NORMAL_RESPONSE: "Se obtuvo una respuesta normal; la vulnerabilidad no existe",
            VerificationResult.TIMEOUT: "Tiempo de espera agotado en la ejecución del PoC",
            VerificationResult.ERROR_403_404: "Solicitud rechazada (403/404); el objetivo no es explotable",
            VerificationResult.EXECUTION_ERROR: "Error del entorno de ejecución del PoC (p. ej. intérprete ausente); no fue posible verificar la vulnerabilidad",
        }

        vf.rejection_reason = rejection_reasons.get(
            result,
            f"Verificación fallida, motivo: {result.value}",
        )

        # Registrar el motivo de exclusión, pero no se incluye en el informe
        print(f"[VERIFIER] Vulnerabilidad excluida: {original.title} | Motivo: {vf.rejection_reason}")

    def get_verified_report_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades que pueden incluirse en el informe.

        Solo devuelve las vulnerabilidades que pasaron la verificación; las que
        fallaron no se devuelven.
        """
        result = []

        for vf in self.verified_findings:
            if vf.status == VerificationStatus.VERIFIED:
                # Clonar el finding y actualizar la información de verificación
                finding = vf.original_finding.model_copy()
                finding.evidence = vf.verified_evidence
                finding.description = vf.verified_description
                finding.severity = vf.verified_severity
                # Stamp verification state so the produced finding passes the
                # report/SARIF/findings.json inclusion gate (verification_status
                # == "verified"), recording the actual PoC execution time.
                finding.mark_verified(
                    note=vf.verified_evidence[:200], evidence_level="L4"
                )
                if vf.poc_executed_at:
                    finding.verified_at = vf.poc_executed_at
                result.append(finding)

        return result

    def get_summary(self) -> dict[str, Any]:
        """Obtiene el resumen de la verificación."""
        return {
            "total": len(self.verified_findings) + len(self.rejected_findings),
            "verified": len(self.verified_findings),
            "rejected": len(self.rejected_findings),
            "target": self.target,
            "verified_findings": [
                {
                    "title": vf.original_finding.title,
                    "severity": vf.verified_severity,
                    "result": vf.result.value if vf.result else None,
                }
                for vf in self.verified_findings
            ],
            "rejected_findings": [
                {
                    "title": vf.original_finding.title,
                    "reason": vf.rejection_reason,
                }
                for vf in self.rejected_findings
            ],
        }
