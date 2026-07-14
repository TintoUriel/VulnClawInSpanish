from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from vulnclaw.agent.anti_loop import FAILED_ACCESS_PATTERNS


class FailureCategory(str, Enum):
    ENV_CONSTRAINT = "env_constraint"
    PATH_ERROR = "path_error"
    PARAM_ERROR = "param_error"
    INFO_NEEDED = "info_needed"
    UNKNOWN = "unknown"


class Attempt(BaseModel):
    path: str
    success: bool
    category: FailureCategory | None = None
    details: str = ""
    vuln_type: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReflexionState(BaseModel):
    attempts: list[Attempt] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    failed_paths: list[str] = Field(default_factory=list)
    reflections: list[dict[str, Any]] = Field(default_factory=list)
    consecutive_failures: int = 0
    last_vuln_type: str = ""
    vuln_type_fail_count: int = 0


class ReflexionEngine(BaseModel):
    max_same_vuln_fails: int = 2
    max_total_no_progress: int = 5
    max_reflections_before_escalate: int = 3
    escalation_max_level: int = 4
    state: ReflexionState = Field(default_factory=ReflexionState)

    def record_attempt(
        self,
        path: str,
        success: bool,
        category: FailureCategory | None = None,
        details: str = "",
        vuln_type: str = "",
    ) -> None:
        attempt = Attempt(
            path=path,
            success=success,
            category=category,
            details=details,
            vuln_type=vuln_type,
        )
        self.state.attempts.append(attempt)

        if success:
            self.state.consecutive_failures = 0
            self.state.vuln_type_fail_count = 0
            if vuln_type:
                self.state.last_vuln_type = vuln_type
            return

        self.state.consecutive_failures += 1
        # No se añaden marcadores de posición "unknown"/rutas vacías a la lista de
        # rutas fallidas, para evitar contaminar el historial de fallos y su atribución
        if path and path != "unknown":
            self.state.failed_paths.append(path)

        if vuln_type:
            if vuln_type == self.state.last_vuln_type:
                self.state.vuln_type_fail_count += 1
            else:
                self.state.last_vuln_type = vuln_type
                self.state.vuln_type_fail_count = 1

        if category and category != FailureCategory.UNKNOWN and details:
            self.state.constraints.append(details)

    def should_reflect(self) -> bool:
        same_vuln_stale = self.state.vuln_type_fail_count >= self.max_same_vuln_fails
        no_progress_stale = self.state.consecutive_failures >= self.max_total_no_progress
        return same_vuln_stale or no_progress_stale

    def should_escalate(self) -> bool:
        return len(self.state.reflections) >= self.max_reflections_before_escalate

    def get_escalation_level(self) -> int:
        level = (self.state.consecutive_failures // 2) + len(self.state.reflections)
        return min(self.escalation_max_level, max(0, level))

    def get_escalation_hints(self) -> list[str]:
        hints_by_level = {
            0: ["Primero prueba el payload original (sin codificar)."],
            1: [
                "Codifica los caracteres especiales en URL.",
                "Alterna mayúsculas/minúsculas en las palabras clave (SeLeCt).",
                "Prueba variantes de espacios en blanco (/**/, salto de línea, tabulación).",
            ],
            2: [
                "Prueba la doble codificación URL.",
                "Inserta comentarios en línea, como /**/.",
                "Usa codificación de entidades HTML en puntos de inyección orientados al navegador.",
            ],
            3: [
                "Prueba el escape Unicode (\\u0027).",
                "Prueba la codificación hexadecimal (0x...).",
                "Divide las palabras clave mediante concatenación de cadenas (con||cat).",
                "Usa funciones alternativas equivalentes para eludir las funciones bloqueadas.",
            ],
            4: [
                "Combina varias capas de codificación para ofuscar.",
                "Usa una sintaxis alternativa para lograr el mismo objetivo (como HANDLER en lugar de SELECT).",
                "Cambia a inyección ciega basada en tiempo o confirmación mediante un canal fuera de banda (OOB).",
                "Cambia a un tipo de vulnerabilidad/superficie de ataque completamente distinto.",
            ],
        }
        return hints_by_level[self.get_escalation_level()]

    def record_reflection(self, old_path: str, new_path: str, reasoning: str) -> None:
        self.state.reflections.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "old_path": old_path,
                "new_path": new_path,
                "reasoning": reasoning,
            }
        )
        self.state.consecutive_failures = 0
        self.state.vuln_type_fail_count = 0

    def analyze_failure_patterns(self) -> list[dict[str, Any]]:
        patterns: dict[str, dict[str, Any]] = {}
        for attempt in self.state.attempts:
            if attempt.success:
                continue
            category = attempt.category.value if attempt.category else FailureCategory.UNKNOWN.value
            if category not in patterns:
                patterns[category] = {"count": 0, "paths": set(), "examples": []}
            patterns[category]["count"] += 1
            patterns[category]["paths"].add(attempt.path)
            if attempt.details and len(patterns[category]["examples"]) < 3:
                patterns[category]["examples"].append(attempt.details[:200])

        result = []
        for category, info in sorted(patterns.items(), key=lambda item: item[1]["count"], reverse=True):
            result.append(
                {
                    "category": category,
                    "occurrences": info["count"],
                    "affected_paths": sorted(info["paths"]),
                    "example_details": info["examples"],
                    "suggested_action": self._suggest_for_category(category),
                }
            )
        return result

    def get_failed_paths(self) -> list[str]:
        return list(dict.fromkeys(self.state.failed_paths))

    def to_prompt_block(self) -> str:
        """Bloque de estado ligero (se inyecta en cada ronda). Los patrones de fallo
        detallados y las sugerencias de escalado solo se generan en to_reflection_prompt
        cuando se activa la reflexión, para evitar inyectarlos de forma duplicada con
        este bloque y desperdiciar tokens."""
        if not self.state.attempts and not self.state.reflections:
            return ""

        lines = [
            "🔁 Estado de reflexión:",
            f"- Rondas consecutivas sin progreso: {self.state.consecutive_failures}",
            f"- Fallos del mismo tipo de vulnerabilidad: {self.state.vuln_type_fail_count}",
            f"- Nivel de escalado actual: L{self.get_escalation_level()}",
        ]

        failed_paths = self.get_failed_paths()
        if failed_paths:
            lines.append(f"- Rutas ya fallidas (no repetir): {', '.join(failed_paths[:8])}")

        return "\n".join(lines)

    def to_reflection_prompt(self) -> str:
        """Instrucción de toma de control por reflexión, solo se genera cuando se
        activa should_reflect(); contiene la atribución detallada de fallos +
        sugerencias de escalado."""
        if not self.should_reflect():
            return ""

        lines = [
            "🔴 Toma de control por reflexión (el mismo tipo de ataque ha fallado "
            "repetidamente, es necesario cambiar de estrategia):",
            "- Deja de cambiar payloads repetidamente en la ruta de ataque actual.",
            "- Revisa el historial de fallos y determina claramente qué suposición "
            "anterior probablemente era incorrecta.",
            "- Antes de probar el siguiente payload, elige una ruta de ataque/tipo "
            "de vulnerabilidad sustancialmente diferente.",
            f"- Nivel de escalado actual: L{self.get_escalation_level()}",
        ]

        if self.should_escalate():
            lines.append(
                "- ⚠️ Escalado obligatorio: cambia a un tipo de vulnerabilidad o "
                "superficie de ataque completamente distinto; no insistas en la "
                "dirección actual."
            )

        patterns = self.analyze_failure_patterns()
        if patterns:
            lines.append("- Análisis de patrones de fallo:")
            for pattern in patterns[:3]:
                lines.append(
                    f"  - {pattern['category']} ×{pattern['occurrences']}: "
                    f"{pattern['suggested_action']}"
                )

        hints = self.get_escalation_hints()
        if hints:
            lines.append(f"- Sugerencias de bypass para este nivel (L{self.get_escalation_level()}):")
            for hint in hints:
                lines.append(f"  - {hint}")

        return "\n".join(lines)

    def extract_experience(self) -> dict[str, Any] | None:
        if not self.state.attempts:
            return None

        successful_paths = [attempt.path for attempt in self.state.attempts if attempt.success]
        return {
            "total_attempts": len(self.state.attempts),
            "successful_paths": successful_paths,
            "failed_paths": self.get_failed_paths(),
            "constraints": list(dict.fromkeys(self.state.constraints)),
            "reflections": self.state.reflections,
            "failure_patterns": self.analyze_failure_patterns(),
            "last_vuln_type": self.state.last_vuln_type,
            "escalation_level": self.get_escalation_level(),
        }

    @staticmethod
    def _suggest_for_category(category: str) -> str:
        suggestions = {
            FailureCategory.ENV_CONSTRAINT.value: (
                "Usa codificación/ofuscación para eludir el filtro, cambia de "
                "protocolo o endpoint, y verifica las restricciones de acceso "
                "(WAF/permisos/límite de tasa)."
            ),
            FailureCategory.PATH_ERROR.value: (
                "Reduce la prioridad de esta ruta y cambia a una superficie de "
                "ataque/tipo de vulnerabilidad diferente."
            ),
            FailureCategory.PARAM_ERROR.value: (
                "Ajusta el nombre del parámetro, el delimitador, la sintaxis del "
                "payload o el punto de inyección."
            ),
            FailureCategory.INFO_NEEDED.value: (
                "Recopila más información de reconocimiento antes de reintentar esta ruta."
            ),
        }
        return suggestions.get(category, "Revisa el historial de fallos y prueba un enfoque diferente.")


def classify_failure(response_text: str) -> FailureCategory | None:
    text = response_text.lower()
    if not text.strip():
        return None

    if any(pattern.lower() in text for pattern in FAILED_ACCESS_PATTERNS):
        return FailureCategory.ENV_CONSTRAINT

    category_patterns = {
        FailureCategory.ENV_CONSTRAINT: [
            # English
            "waf",
            "403",
            "forbidden",
            "blocked",
            "filtered",
            "permission denied",
            "unauthorized",
            "rate limit",
            "timeout",
            "connection refused",
            "bad gateway",
            "service unavailable",
            # Español
            "bloqueado",
            "filtrado",
            "bloqueado por waf",
            "bloqueo",
            "filtrado por completo",
            "escapado",
            "acceso prohibido",
            "sin permiso",
            "permisos insuficientes",
            "límite de frecuencia",
            "limitación de tasa",
        ],
        FailureCategory.PATH_ERROR: [
            # English
            "vulnerability does not exist",
            "not vulnerable",
            "no injection",
            "not injectable",
            "false positive",
            "dead end",
            "wrong attack surface",
            # Español
            "esta vulnerabilidad no existe",
            "no hay vulnerabilidad",
            "sin vulnerabilidad",
            "no es un punto de inyección",
            "sin inyección",
            "aquí no hay",
            "falso positivo",
            "callejón sin salida",
            "no es viable",
            "cambiar de superficie de ataque",
            "cambiar de dirección",
        ],
        FailureCategory.PARAM_ERROR: [
            # English
            "invalid payload",
            "syntax error",
            "bad parameter",
            "wrong parameter",
            "encoding error",
            "malformed",
            "parse error",
            "delimiter",
            # Español
            "parámetro incorrecto",
            "parámetro erróneo",
            "payload no válido",
            "payload inválido",
            "error de sintaxis",
            "error de codificación",
            "error de formato",
            "delimitador",
        ],
        FailureCategory.INFO_NEEDED: [
            # English
            "need more information",
            "need more recon",
            "unknown parameter",
            "insufficient information",
            "collect more",
            "fingerprint first",
            "enumerate first",
            # Español
            "se necesita más información",
            "información insuficiente",
            "parámetro desconocido",
            "recopilar primero",
            "reconocer primero",
            "enumerar primero",
            "identificar huella primero",
            "recopilar de nuevo",
        ],
    }

    for category, patterns in category_patterns.items():
        if any(pattern in text for pattern in patterns):
            return category

    return FailureCategory.UNKNOWN
