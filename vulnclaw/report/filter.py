"""VulnClaw Report Content Filter — clean raw LLM output into pure report text.

Objetivos del filtrado:
    - Marcadores y contenido de TOOL_CALL
    - Bloques de código Python (print/open/import, etc.)
    - Marcadores de Round/Context
    - Salida de depuración
    - Contenido de etiquetas think

Solo se genera texto de informe en Markdown puro.
"""

from __future__ import annotations

import re
from typing import Optional


class ReportContentFilter:
    """Filtro de contenido de informes — extrae texto de informe puro a partir de la salida cruda del LLM."""

    # ── Patrones de filtrado ──────────────────────────────────────────────────────────

    # Marcadores TOOL_CALL (varios formatos)
    TOOL_CALL_PATTERNS = [
        # Formato estándar
        re.compile(r"\[TOOL_CALL\]\s*\{[^}]+\}", re.DOTALL),
        # Formato con tool =>
        re.compile(r'\[TOOL_CALL\]\s*\{tool\s*=>\s*"[^"]+"\s*,\s*args\s*=>\s*\{[^}]+\}', re.DOTALL),
        # Formato python_execute
        re.compile(r'\{tool\s*=>\s*"python_execute"\s*,\s*args\s*=>\s*\{[^}]+\}', re.DOTALL),
        # Formato nmap_scan
        re.compile(r'\{tool\s*=>\s*"nmap_scan"\s*,\s*args\s*=>\s*\{[^}]+\}', re.DOTALL),
        # Formato fetch
        re.compile(r"\[TOOL_CALL\]\s*```\s*\{[^}]+\}\s*```", re.DOTALL),
        # Llamada a herramienta simplificada
        re.compile(r"\[TOOL_CALL\]\s*[\s\S]+?\[/TOOL_CALL\]"),
        # Formato tool_call
        re.compile(r"tool_call\s*\(\s*\{[^}]+\}\s*\)", re.DOTALL),
    ]

    # Marcadores de Round
    ROUND_PATTERNS = [
        re.compile(r"──\s*Cycle\s*\d+\s*\|\s*Round\s*\d+\s*──", re.DOTALL),
        re.compile(r"──\s*Round\s*\d+\s*──", re.DOTALL),
        re.compile(r"Cycle\s*\d+\s*\|\s*Round\s*\d+", re.IGNORECASE),
        re.compile(r"Round\s+\d+:", re.IGNORECASE),
        re.compile(r"Ronda\s*\d+", re.IGNORECASE),
    ]

    # Etiquetas think (proceso de razonamiento del LLM)
    THINK_PATTERNS = [
        re.compile(
            r"</?(?:think|thinking|result_info)>?[\s\S]*?</?(?:think|thinking|result_info)>?",
            re.IGNORECASE,
        ),
        re.compile(r"</?(?:think|thinking|result_info)>?[\s\S]*", re.IGNORECASE),
        re.compile(r"<thinking>[\s\S]*?</thinking>?", re.IGNORECASE),
        re.compile(r"<thinking>[\s\S]*", re.IGNORECASE),
        re.compile(r"<reasoning>[\s\S]*?</reasoning>?", re.IGNORECASE),
        re.compile(r"<reasoning>?[\s\S]*", re.IGNORECASE),
        re.compile(r"\[think\]", re.IGNORECASE),
        re.compile(r"##\s*Pensamiento\s*", re.IGNORECASE),
        re.compile(r"###\s*Razonamiento\s*", re.IGNORECASE),
    ]

    # Bloques de código Python (varios formatos)
    PYTHON_CODE_PATTERNS = [
        # Formato estándar ```python ```
        re.compile(r"```python\s*[\s\S]*?```"),
        # Formato ``` ``` (sin indicador de lenguaje)
        re.compile(r"```\s*[\s\S]*?```"),
        # Sentencias print/import de una sola línea
        re.compile(r"^\s*print\s*\(", re.MULTILINE),
        re.compile(r"^\s*import\s+", re.MULTILINE),
        re.compile(r"^\s*from\s+\w+\s+import", re.MULTILINE),
        re.compile(r"^\s*with\s+open\s*\(", re.MULTILINE),
        # Sentencia with
        re.compile(r"with\s+open\s*\([^)]+\)\s+as\s+\w+:", re.DOTALL),
        # if __name__ == "__main__"
        re.compile(r'if\s+__name__\s*==\s*["\']__main__["\']:', re.DOTALL),
    ]

    # Marcadores de salida de depuración
    DEBUG_PATTERNS = [
        re.compile(r"^\s*──.*──\s*$", re.MULTILINE),  # Línea separadora
        re.compile(r"^\s*\[=\]+\s*$", re.MULTILINE),  # Estilo =====
        re.compile(r"llamada a herramienta|tool_call", re.IGNORECASE),
        re.compile(r"invocar herramienta|resultado de invocación", re.IGNORECASE),
        re.compile(r"\[LLM\s+[A-Z_]+\]", re.IGNORECASE),  # [LLM THINKING], etc.
    ]

    # Solicitudes/respuestas HTTP (filtrado opcional)
    HTTP_PATTERNS = [
        re.compile(r"HTTP/\d\.\d\s+\d+\s+[^\n]+", re.IGNORECASE),
        re.compile(r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+/[^\n]+", re.MULTILINE | re.IGNORECASE),
    ]

    # Marcadores de cambio de fase
    PHASE_PATTERNS = [
        re.compile(r"cambio de fase\s*[→\-]>\s*\w+", re.IGNORECASE),
        re.compile(r"entra en fase\s*\w+", re.IGNORECASE),
        re.compile(r"fase actual:\s*\w+", re.IGNORECASE),
    ]

    @classmethod
    def filter(cls, content: str) -> str:
        """Filtra el contenido, conservando solo texto de informe puro.

        Args:
            content: Salida cruda del LLM

        Returns:
            Texto de informe puro tras el filtrado
        """
        result = content

        # 1. Eliminar bloques TOOL_CALL
        result = cls._remove_tool_calls(result)

        # 2. Eliminar marcadores Round
        result = cls._remove_round_markers(result)

        # 3. Eliminar etiquetas think
        result = cls._remove_think_tags(result)

        # 4. Eliminar bloques de código Python
        result = cls._remove_python_code(result)

        # 5. Eliminar salida de depuración
        result = cls._remove_debug_output(result)

        # 6. Eliminar marcadores de cambio de fase
        result = cls._remove_phase_markers(result)

        # 7. Limpiar líneas en blanco sobrantes
        result = cls._cleanup_whitespace(result)

        return result.strip()

    @classmethod
    def _remove_tool_calls(cls, content: str) -> str:
        """Elimina el contenido relacionado con TOOL_CALL."""
        result = content

        for pattern in cls.TOOL_CALL_PATTERNS:
            result = pattern.sub("", result)

        # Eliminar líneas independientes de tool_call
        result = re.sub(r"^\s*tool_call\s*\(.*$", "", result, flags=re.MULTILINE)
        result = re.sub(r"^\s*\[TOOL_CALL\]\s*$", "", result, flags=re.MULTILINE)

        return result

    @classmethod
    def _remove_round_markers(cls, content: str) -> str:
        """Elimina los marcadores de Round/Cycle."""
        result = content

        for pattern in cls.ROUND_PATTERNS:
            result = pattern.sub("", result)

        return result

    @classmethod
    def _remove_think_tags(cls, content: str) -> str:
        """Elimina las etiquetas think y el proceso de razonamiento."""
        result = content

        for pattern in cls.THINK_PATTERNS:
            result = pattern.sub("", result)

        return result

    @classmethod
    def _remove_python_code(cls, content: str) -> str:
        """Elimina bloques de código Python.

        Nota: esto filtra el código crudo de la salida del LLM, no los ejemplos
        de código del informe. Los ejemplos de código del informe (PoC, etc.)
        deben añadirse a través de la plantilla, no procesarse aquí.
        """
        result = content

        for pattern in cls.PYTHON_CODE_PATTERNS:
            result = pattern.sub("", result)

        # Eliminar bloques grandes de sentencias import/print sueltas
        lines = result.split("\n")
        filtered_lines = []
        in_code_block = False

        for line in lines:
            # Detectar los límites del bloque de código
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Si está dentro de un bloque de código, omitir
            if in_code_block:
                continue

            # Filtrar líneas de código sospechosas
            stripped = line.strip()
            if any(
                stripped.startswith(prefix)
                for prefix in [
                    "import ",
                    "from ",
                    "print(",
                    "with open",
                    "if __name__",
                    "def ",
                    "class ",
                    "return ",
                    "try:",
                    "except:",
                    "requests.",
                    "socket.",
                    "subprocess.",
                ]
            ):
                continue

            filtered_lines.append(line)

        result = "\n".join(filtered_lines)
        return result

    @classmethod
    def _remove_debug_output(cls, content: str) -> str:
        """Elimina la salida de depuración."""
        result = content

        for pattern in cls.DEBUG_PATTERNS:
            result = pattern.sub("", result)

        # Eliminar marcadores de resultado de herramienta
        result = re.sub(r"\[Resultado\]\s*:?\s*", "", result)
        result = re.sub(r"\[Salida\]\s*:?\s*", "", result)

        return result

    @classmethod
    def _remove_phase_markers(cls, content: str) -> str:
        """Elimina los marcadores de cambio de fase."""
        result = content

        for pattern in cls.PHASE_PATTERNS:
            result = pattern.sub("", result)

        return result

    @classmethod
    def _cleanup_whitespace(cls, content: str) -> str:
        """Limpia líneas en blanco y espacios sobrantes."""
        # Eliminar líneas en blanco consecutivas (más de 2)
        result = re.sub(r"\n{3,}", "\n\n", content)

        # Eliminar espacios al inicio/final de cada línea
        lines = result.split("\n")
        result = "\n".join(line.strip() for line in lines if line.strip())

        return result

    @classmethod
    def is_pure_markdown(cls, content: str) -> bool:
        """Comprueba si el contenido es Markdown puro (sin marcadores de interferencia).

        Se usa para verificar que el resultado del filtrado sea válido.
        """
        # Comprobar si contiene marcadores de interferencia
        interference_patterns = [
            r"\[TOOL_CALL\]",
            r"\{tool\s*=>",
            r"──\s*Round",
            r"──\s*Cycle",
            r"<thinking>",
            r"```python",
            r"^\s*print\s*\(",
            r"^\s*import\s+",
        ]

        for pattern in interference_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return False

        return True


# ── Funciones auxiliares ────────────────────────────────────────────────────────────────


def filter_report_content(content: str) -> str:
    """Filtra el contenido del informe, conservando solo texto Markdown puro.

    Es un envoltorio de conveniencia para ReportContentFilter.filter().
    """
    return ReportContentFilter.filter(content)


def deduplicate_report_findings(findings: list, threshold: float = 0.75) -> list:
    """Semantically deduplicate a list of VulnerabilityFinding before rendering.

    Deduplicación semántica en la capa de informes: además de la deduplicación exacta
    de SessionState, se aplica una capa adicional de fusión semántica para asegurar
    que el informe no contenga varias formulaciones distintas de la misma
    vulnerabilidad. Se conserva la que tenga evidencia más completa.

    Args:
        findings: Lista de VulnerabilityFinding.
        threshold: Umbral de similitud, por defecto 0.75.

    Returns:
        Lista deduplicada, conservando el orden de primera aparición.
    """
    # Modificado por: Nyaecho
    # Fecha de modificación: 2026-07-08
    # Motivo de la modificación: Corrección V2 — se importa desde config/finding_similarity,
    #          eliminando la dependencia report→agent.
    from vulnclaw.config.finding_similarity import deduplicate_findings

    return deduplicate_findings(findings, threshold=threshold)


def extract_findings_section(content: str) -> Optional[str]:
    """Extrae la sección de la lista de vulnerabilidades del informe.

    Si no se encuentra una lista de vulnerabilidades dedicada, devuelve None.
    """
    patterns = [
        r"(##+\s*(?:\d+\.\s*)?Hallazgos de Vulnerabilidades[^\n]*\n[\s\S]*?)(?=##|\Z)",
        r"(##+\s*(?:\d+\.\s*)?Hallazgos Detallados[^\n]*\n[\s\S]*?)(?=##|\Z)",
        r"(##\s*Findings\s*\n[\s\S]*?)(?=##|\Z)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def remove_unverified_findings(content: str) -> str:
    """Elimina del contenido del informe las vulnerabilidades no verificadas.

    Se eliminarán las vulnerabilidades marcadas como [No verificado].
    """
    # Eliminar las secciones de vulnerabilidades marcadas como [No verificado]
    pattern = re.compile(
        r"(###\s*\[[^\]]*\]\s*[^\n]*No verificado[^\n]*\n[\s\S]*?)(?=###|\Z)",
        re.IGNORECASE,
    )
    result = pattern.sub("", content)

    # Eliminar las líneas que contienen [No verificado]
    lines = result.split("\n")
    filtered_lines = []
    skip_section = False

    for line in lines:
        # Detectar el inicio de una sección no verificada
        if "[No verificado]" in line and line.strip().startswith("###"):
            skip_section = True
            continue

        # Detectar el fin de la sección
        if skip_section and line.startswith("##"):
            skip_section = False

        if not skip_section:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)
