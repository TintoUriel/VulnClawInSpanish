"""VulnClaw Finding Parser - three-layer vulnerability detection from LLM responses."""

from __future__ import annotations

import re

from vulnclaw.agent.context import ContextManager, VulnerabilityFinding
from vulnclaw.agent.runtime_state import RuntimeState
from vulnclaw.agent.think_filter import strip_think_tags

# NOTA: los patrones de esta sección hacen coincidencia contra el TEXTO
# GENERADO POR EL LLM (respuesta del modelo), cuyo idioma depende de
# agent/prompts.py y agent/system_prompt.py (fuera del alcance de esta
# traducción). Los tercer elementos de tupla `vuln_type` que coinciden con
# claves del diccionario de alias en config/finding_similarity.py
# (_VULN_TYPE_ALIASES, fuera de alcance) se mantienen en chino a propósito
# para no romper la normalización/deduplicación entre módulos.
PROOF_PATTERNS: list[str] = [
    r"diferencia[：: ]*\d+",
    r"\d+\s*bytes",
    r"(?:código de estado|código de respuesta)?[：: ]*5\d{2}",
    r"SQL.*error|mysql.*error|sql.*error",
    r"SLEEP\(|BENCHMARK\(|EXTRACTVALUE\(|UPDATEXML\(",
    r"ejecución de comando exitosa|whoami|id\s+",
    r"root[:\s]|administrator",
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"CVE-\d{4}-\d{4,}",
    r"extracción exitosa|obtención exitosa|obtenido",
]

NATURAL_LANG_PATTERNS: list[tuple[str, str, str]] = [
    (r"inyección SQL|SQLi|inyección", "High", "SQL注入"),
    (r"RCE|ejecución remota de código|inyección de comandos|ejecución de comandos", "Critical", "远程代码执行"),
    (r"sin autorización|sin autenticación|no requiere autenticación|bypass de autenticación|autenticación.*bypass", "High", "认证绕过"),
    (r"SSRF|falsificación de solicitud del lado del servidor", "High", "SSRF"),
    (r"XSS|cross-site scripting|XSS almacenado|XSS reflejado", "Medium", "XSS跨站脚本"),
    (r"CSRF|falsificación de petición en sitios cruzados", "Medium", "CSRF"),
    (r"inclusión de archivos|traversal de directorios|LFI|RFI", "Medium", "文件包含/遍历"),
    (r"contraseña débil|credencial por defecto|contraseña por defecto|fuerza bruta|bruteforce", "Medium", "Contraseña débil/fuerza bruta"),
    (r"error de configuración|defecto de configuración|fuga.*configuración", "Medium", "Error de configuración"),
    (r"directorio sensible|archivo sensible.*encontrado|directorio.*encontrado", "Info", "Directorio/archivo sensible encontrado"),
    (r"versión.*desactualizada|versión de middleware|fingerprint.*identificad[oa]", "Info", "Información de versión"),
    (r"CVE-\d{4}-\d{4,}", "High", "Vulnerabilidad CVE conocida"),
]

ELEVATION_KEYWORDS: list[tuple[str, str, str]] = [
    (r"fuga|información sensible|fuga de datos|información personal|\d+\s*registros de datos", "High", "数据泄露"),
    (r"sin autorización|sin autenticación|bypass de autenticación|no requiere autenticación", "High", "未授权访问"),
    (r"RCE|ejecución de comandos|código remoto", "Critical", "远程代码执行"),
    (r"inyección SQL|SQLi|inyección", "High", "注入漏洞"),
    (r"CVE-\d{4}-\d{4,}", "High", "Vulnerabilidad CVE conocida"),
    (r"contraseña débil|credencial por defecto|fuerza bruta", "High", "Contraseña débil/fuerza bruta"),
    (r"XSS|cross-site scripting", "Medium", "XSS"),
    (r"inclusión de archivos|traversal de directorios", "High", "文件包含/遍历"),
    (r"devuelve 200.*no existe|200.*contenido vacío|respuesta vacía.*posición", "Medium", "Posible bypass de autorización"),
    (r"403.*endpoint|endpoint.*403", "Medium", "Bloqueo de autenticación 403"),
]

URL_PATTERN = re.compile(r'https?://[^\s<>"\')\]]+')
PATH_PATTERN = re.compile(r"(?:/[\w%&=?\-]+)+")


def _collect_location_summary(text: str, max_items: int = 4) -> str:
    seen: set[str] = set()
    items: list[str] = []

    for value in re.findall(URL_PATTERN, text):
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= max_items:
            return " | ".join(items)

    for value in re.findall(PATH_PATTERN, text):
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= max_items:
            break

    return " | ".join(items)


class FindingParser:
    """Parses LLM responses to extract vulnerability findings and discoveries."""

    def __init__(self, context: ContextManager, runtime: RuntimeState) -> None:
        self.context = context
        self.runtime = runtime

    def parse(self, response: str) -> None:
        """Three-layer detection:
        1. Explicit [Severity] tags
        2. Natural-language vulnerability descriptions
        3. confirmed_facts elevation
        """
        existing_titles = {f.title for f in self.context.state.findings}

        severity_patterns = [
            (r"\[Critical\]\s*(.+?)(?:\n|$)", "Critical"),
            (r"\[High\]\s*(.+?)(?:\n|$)", "High"),
            (r"\[Medium\]\s*(.+?)(?:\n|$)", "Medium"),
            (r"\[Low\]\s*(.+?)(?:\n|$)", "Low"),
        ]
        for pattern, severity in severity_patterns:
            for match in re.findall(pattern, response):
                title = match.strip()
                title = re.sub(r"\*+", "", title).strip(" -—–")
                if title and title not in existing_titles:
                    self.context.state.add_finding(
                        VulnerabilityFinding(
                            title=title,
                            severity=severity,
                            evidence_level="L1",
                            lifecycle_status="candidate",
                        )
                    )
                    existing_titles.add(title)

        clean_response = strip_think_tags(response)
        notes = self.context.state.notes
        if notes:
            clean_notes = [strip_think_tags(n) for n in notes[-5:]]
            evidence_pool = clean_response + " " + " ".join(clean_notes)
        else:
            evidence_pool = clean_response

        for pattern, severity, vuln_type in NATURAL_LANG_PATTERNS:
            canonical_title = f"[自动] {vuln_type}"
            if canonical_title in existing_titles:
                continue

            vuln_matches = re.findall(pattern, clean_response, re.IGNORECASE)
            if not vuln_matches:
                continue

            has_proof = any(
                re.search(p, clean_response + " " + " ".join(notes[-3:]), re.IGNORECASE)
                for p in PROOF_PATTERNS
            )
            has_confirmed_fact = any(
                re.search(
                    p, " ".join(getattr(self.context.state, "confirmed_facts", [])), re.IGNORECASE
                )
                for p in PROOF_PATTERNS
            )
            if not has_proof and not has_confirmed_fact:
                continue

            proof_snippets: list[str] = []
            for pattern_text in PROOF_PATTERNS:
                for match in re.finditer(pattern_text, evidence_pool, re.IGNORECASE):
                    snippet = match.group(0).strip()[:80]
                    if snippet and snippet not in proof_snippets:
                        proof_snippets.append(snippet)
                    if len(proof_snippets) >= 3:
                        break

            location = _collect_location_summary(evidence_pool)
            proof_text = " | ".join(proof_snippets) if proof_snippets else ""
            evidence = (
                f"{location} | {proof_text}" if location and proof_text else location or proof_text
            )

            self.context.state.add_finding(
                VulnerabilityFinding(
                    title=canonical_title,
                    severity=severity,
                    vuln_type=vuln_type,
                    description=f"Detección automática: {vuln_matches[0].strip()[:100]}"
                    if vuln_matches
                    else "Detectado automáticamente mediante patrones de lenguaje natural",
                    evidence=evidence[:300],
                    evidence_level="L2",
                    lifecycle_status="needs_manual_review"
                    if severity in ("Critical", "High")
                    else "pending_verification",
                )
            )
            existing_titles.add(canonical_title)

        confirmed_facts = getattr(self.context.state, "confirmed_facts", [])
        for fact in confirmed_facts:
            for pattern, severity, vuln_type in ELEVATION_KEYWORDS:
                if re.search(pattern, fact, re.IGNORECASE):
                    title = f"[已确认] {fact.strip()[:120]}"
                    if title not in existing_titles:
                        location = _collect_location_summary(evidence_pool)
                        evidence = (
                            f"{location} | Confirmado mediante verificación con herramientas: {fact}"
                            if location
                            else f"Confirmado mediante verificación con herramientas: {fact}"
                        )
                        finding = VulnerabilityFinding(
                            title=title,
                            severity=severity,
                            vuln_type=vuln_type,
                            description=f"Confirmado mediante verificación con herramientas: {fact}",
                            evidence=evidence[:300],
                            evidence_level="L4",
                            lifecycle_status="verified",
                        )
                        finding.mark_verified(note=fact[:200], evidence_level="L4")
                        added = self.context.state.add_finding(finding)
                        if not added:
                            for existing in self.context.state.findings:
                                if existing.finding_id == finding.finding_id or (
                                    existing.vuln_type == finding.vuln_type
                                    and existing.verification_status != "verified"
                                ):
                                    existing.title = finding.title
                                    existing.severity = finding.severity
                                    existing.vuln_type = finding.vuln_type
                                    existing.description = finding.description
                                    existing.evidence = finding.evidence
                                    existing.verified = True
                                    existing.verification_status = "verified"
                                    existing.lifecycle_status = "verified"
                                    existing.evidence_level = "L4"
                                    existing.verified_at = finding.verified_at
                                    existing.verification_note = finding.verification_note
                                    break
                        existing_titles.add(title)
                    break

        clean_response = strip_think_tags(response)
        discovery_markers = [
            r"\[\+\]\s*(.+?)(?:\n|$)",
            r"(?:descubrimiento|encontrado)[：: ]\s*(.+?)(?:\n|$)",
            r"(flag\{[^}]+\})",
            r"(NSSCTF\{[^}]+\})",
            r"(CTF\{[^}]+\})",
        ]
        for pattern in discovery_markers:
            for match in re.findall(pattern, clean_response, re.IGNORECASE):
                note = match.strip()[:200]
                if note and note not in self.context.state.notes:
                    self.context.state.add_note(note)

        confirmed_markers = [
            r"confirmado[：: ]\s*(.+?)(?:\n|$)",
            r"confirmación[：: ]\s*(.+?)(?:\n|$)",
            r"verificación exitosa[：: ]\s*(.+?)(?:\n|$)",
            r"\[✅\]\s*(.+?)(?:\n|$)",
            r"confirmado.*existe",
            r"vulnerabilidad.*confirmada",
            r"ya.*verificad[oa].*éxito",
            r"payload.*diferencia[：: ]*\s*\d+",
            r"diferencia[：: ]*\s*\d+.*éxito",
            r"SLEEP\([^)]+\).*tiempo",
            r"extraído con éxito[：: ]*\s*\S+",
            r"se extrajo[：: ]*\s*\S+",
            r"ejecución de comando exitosa",
            r"se puede extraer[：: ]*\s*\S+",
            r"booleano.*éxito|booleano.*válido",
            r"basado en errores.*éxito|basado en errores.*válido",
            r"UNION.*éxito|UNION.*válido",
            r"vulnerabilidad confirmada",
        ]
        for pattern in confirmed_markers:
            for match in re.findall(pattern, response, re.IGNORECASE):
                fact = match.strip()[:200]
                if fact and hasattr(self.context.state, "add_confirmed_fact"):
                    self.context.state.add_confirmed_fact(fact)

        assumption_markers = [
            r"hipótesis[：: ]\s*(.+?)(?:\n|$)",
            r"conjetura[：: ]\s*(.+?)(?:\n|$)",
        ]
        for pattern in assumption_markers:
            for match in re.findall(pattern, response, re.IGNORECASE):
                assumption = match.strip()[:200]
                if assumption and assumption not in self.runtime.unverified_assumptions:
                    self.runtime.unverified_assumptions.append(assumption)
