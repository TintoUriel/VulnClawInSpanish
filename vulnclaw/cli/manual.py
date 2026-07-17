"""Full CLI manual rendering for VulnClaw."""

from __future__ import annotations

from vulnclaw import __version__
from vulnclaw.config.cli_constants import (
    ACTION_NAMES,
    COMMANDS,
    COMMON_TASK_FLAGS,
    ROOT_OPTIONS,
    TASK_COMMAND_NAMES,
    ManualTopic,
)
from vulnclaw.config.schema import PROVIDER_PRESETS


def render_manual(output_format: str = "text", topic: str | None = None) -> str:
    """Render the VulnClaw manual in text, markdown, or roff man-page format."""

    fmt = output_format.strip().lower()
    if fmt not in {"text", "markdown", "man"}:
        raise ValueError("el formato del manual debe ser uno de: text, markdown, man")

    topics = _select_topics(topic)
    normalized_topic = _normalize_topic(topic)
    if fmt == "markdown":
        return _render_markdown(topics, normalized_topic)
    if fmt == "man":
        return _render_man(topics, normalized_topic)
    return _render_text(topics, normalized_topic)


def available_topics() -> list[str]:
    """Return the user-facing topic names accepted by the manual command."""

    return [topic.name for topic in COMMANDS]


def _select_topics(topic: str | None) -> tuple[ManualTopic, ...]:
    normalized = _normalize_topic(topic)
    if not normalized:
        return COMMANDS

    by_name = {item.name: item for item in COMMANDS}
    for item in COMMANDS:
        by_name.update({alias: item for alias in item.aliases})

    selected = by_name.get(normalized)
    if not selected:
        raise ValueError(
            f"tema de manual desconocido '{topic}'. Temas disponibles: {', '.join(available_topics())}"
        )
    return (selected,)


def _normalize_topic(topic: str | None) -> str:
    return (topic or "").strip().lower().replace("_", "-")


def _provider_names() -> str:
    return ", ".join(provider.value for provider in PROVIDER_PRESETS)


def _render_text(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines: list[str] = [
        "VULNCLAW(1) - Manual de la CLI de VulnClaw",
        f"Versión: {__version__}",
        "",
        "SINOPSIS",
        "  vulnclaw [--help] [--version] [--man] [COMANDO] [ARGUMENTOS]...",
        "  vulnclaw manual [TEMA] [--format text|markdown|man]",
        "",
        "DESCRIPCIÓN",
        "  VulnClaw es una CLI asistida por IA para pruebas de seguridad autorizadas.",
        "  Combina asignación de tareas en lenguaje natural, bucles autónomos con",
        "  alcance definido, historial de objetivos, informes, herramientas MCP e",
        "  integradas, un banco de trabajo de terminal y una Web UI local opcional.",
        "",
        "OPCIONES RAÍZ",
    ]
    lines.extend(_render_text_pairs(ROOT_OPTIONS, indent_spaces=2))
    lines.extend(
        [
            "",
            "INICIO RÁPIDO",
            "  vulnclaw init",
            "  vulnclaw config provider deepseek",
            "  vulnclaw config set llm.api_key <clave>",
            "  vulnclaw doctor",
            "  vulnclaw run https://objetivo-autorizado.example --allow-actions recon,scan",
            "",
            "MAPA DE COMANDOS",
        ]
    )
    for item in COMMANDS:
        lines.append(f"  {item.name:<13} {item.summary}")

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend(_common_sections_text())

    lines.extend(["", "DETALLES DE COMANDOS"])
    for item in topics:
        lines.extend(_topic_text(item))

    lines.extend(
        [
            "",
            "CONFIGURACIÓN Y ENTORNO",
            f"  Presets de proveedor: {_provider_names()}",
            "  Directorio de configuración: ~/.vulnclaw por defecto, o VULNCLAW_CONFIG_DIR si está definido.",
            "  Variables de entorno de alto valor: VULNCLAW_LLM_API_KEY, VULNCLAW_LLM_API_KEYS,",
            "  VULNCLAW_LLM_PROVIDER, VULNCLAW_LLM_BASE_URL, VULNCLAW_LLM_MODEL,",
            "  VULNCLAW_SESSION_OUTPUT_DIR, VULNCLAW_SESSION_MAX_ROUNDS,",
            "  VULNCLAW_SESSION_SHOW_THINKING, VULNCLAW_SAFETY_PYTHON_EXECUTE_ENABLED.",
            "",
            "SEGURIDAD",
            "  VulnClaw es solo para pruebas autorizadas. Los indicadores de alcance y las",
            "  restricciones de acciones existen para hacer explícitos y exigibles los límites",
            "  permitidos, pero no reemplazan una autorización por escrito ni un documento",
            "  claro de reglas de enfrentamiento (rules of engagement).",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _common_sections_text() -> list[str]:
    lines = [
        "",
        "FLAGS COMUNES DE TAREA",
    ]
    lines.extend(_render_text_pairs(COMMON_TASK_FLAGS, indent_spaces=2))
    lines.extend(
        [
            "",
            "RESTRICCIONES DE ACCIÓN",
            f"  Nombres de acción reconocidos: {', '.join(ACTION_NAMES)}.",
            "  Ejemplo: --allow-actions recon,scan bloquea los comandos directos de",
            "  explotación/informe y también restringe las transiciones de herramientas",
            "  y fases durante la ejecución del agente.",
        ]
    )
    return lines


def _topic_text(topic: ManualTopic) -> list[str]:
    lines = [
        "",
        topic.name.upper(),
        f"  {topic.summary}",
        "",
        "  Uso:",
    ]
    for usage_line in topic.usage.splitlines():
        lines.append(f"    {usage_line}")

    if topic.flags:
        lines.extend(["", "  Argumentos y flags:"])
        lines.extend(_render_text_pairs(topic.flags, indent_spaces=4))
    if topic.notes:
        lines.extend(["", "  Notas:"])
        lines.extend(f"    - {note}" for note in topic.notes)
    if topic.examples:
        lines.extend(["", "  Ejemplos:"])
        lines.extend(f"    {example}" for example in topic.examples)
    return lines


def _render_text_pairs(pairs: tuple[tuple[str, str], ...], indent_spaces: int) -> list[str]:
    pad = " " * indent_spaces
    lines: list[str] = []
    for name, description in pairs:
        lines.append(f"{pad}{name}")
        lines.append(f"{pad}  {description}")
    return lines


def _render_markdown(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines: list[str] = [
        "# Manual de la CLI de VulnClaw",
        "",
        f"Versión: `{__version__}`",
        "",
        "## Sinopsis",
        "",
        "```bash",
        "vulnclaw [--help] [--version] [--man] [COMANDO] [ARGUMENTOS]...",
        "vulnclaw manual [TEMA] [--format text|markdown|man]",
        "```",
        "",
        "## Descripción",
        "",
        "VulnClaw es una CLI asistida por IA para pruebas de seguridad autorizadas. Combina asignación de tareas en lenguaje natural, bucles autónomos con alcance definido, historial de objetivos, informes, herramientas MCP e integradas, un banco de trabajo de terminal y una Web UI local opcional.",
        "",
        "## Opciones raíz",
        "",
    ]
    lines.extend(_markdown_table(["Opción", "Significado"], ROOT_OPTIONS))
    lines.extend(
        [
            "",
            "## Inicio rápido",
            "",
            "```bash",
            "vulnclaw init",
            "vulnclaw config provider deepseek",
            "vulnclaw config set llm.api_key <clave>",
            "vulnclaw doctor",
            "vulnclaw run https://objetivo-autorizado.example --allow-actions recon,scan",
            "```",
            "",
            "## Mapa de comandos",
            "",
        ]
    )
    lines.extend(_markdown_table(["Comando", "Resumen"], tuple((c.name, c.summary) for c in COMMANDS)))

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend(
            [
                "",
                "## Flags comunes de tarea",
                "",
            ]
        )
        lines.extend(_markdown_table(["Flag", "Significado"], COMMON_TASK_FLAGS))
        lines.extend(
            [
                "",
                "## Restricciones de acción",
                "",
                f"Nombres de acción reconocidos: `{', '.join(ACTION_NAMES)}`.",
                "",
                "Ejemplo: `--allow-actions recon,scan` bloquea los comandos directos de explotación/informe y también restringe las transiciones de herramientas y fases durante la ejecución del agente.",
            ]
        )

    lines.extend(["", "## Detalles de comandos", ""])
    for item in topics:
        lines.extend(_topic_markdown(item))

    lines.extend(
        [
            "",
            "## Configuración y entorno",
            "",
            f"Presets de proveedor: `{_provider_names()}`.",
            "",
            "Directorio de configuración: `~/.vulnclaw` por defecto, o `VULNCLAW_CONFIG_DIR` si está definido.",
            "",
            "Variables de entorno de alto valor: `VULNCLAW_LLM_API_KEY`, `VULNCLAW_LLM_API_KEYS`, `VULNCLAW_LLM_PROVIDER`, `VULNCLAW_LLM_BASE_URL`, `VULNCLAW_LLM_MODEL`, `VULNCLAW_SESSION_OUTPUT_DIR`, `VULNCLAW_SESSION_MAX_ROUNDS`, `VULNCLAW_SESSION_SHOW_THINKING`, `VULNCLAW_SAFETY_PYTHON_EXECUTE_ENABLED`.",
            "",
            "## Seguridad",
            "",
            "VulnClaw es solo para pruebas autorizadas. Los indicadores de alcance y las restricciones de acciones hacen explícitos y exigibles los límites permitidos, pero no reemplazan una autorización por escrito ni un documento claro de reglas de enfrentamiento (rules of engagement).",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _topic_markdown(topic: ManualTopic) -> list[str]:
    lines = [
        f"### `{topic.name}`",
        "",
        topic.summary,
        "",
        "```bash",
        *topic.usage.splitlines(),
        "```",
    ]
    if topic.flags:
        lines.extend(["", "Argumentos y flags:", ""])
        lines.extend(_markdown_table(["Nombre", "Significado"], topic.flags))
    if topic.notes:
        lines.extend(["", "Notas:", ""])
        lines.extend(f"- {note}" for note in topic.notes)
    if topic.examples:
        lines.extend(["", "Ejemplos:", "", "```bash", *topic.examples, "```"])
    lines.append("")
    return lines


def _markdown_table(headers: list[str], rows: tuple[tuple[str, str], ...]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for left, right in rows:
        lines.append(f"| `{left}` | {right} |")
    return lines


def _render_man(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines = [
        f'.TH VULNCLAW 1 "" "VulnClaw {__version__}" "Manual de VulnClaw"',
        ".SH NOMBRE",
        "vulnclaw \\- CLI asistida por IA para pruebas de seguridad autorizadas",
        ".SH SINOPSIS",
        ".B vulnclaw",
        "[--help] [--version] [--man] [COMANDO] [ARGUMENTOS]...",
        ".br",
        ".B vulnclaw manual",
        "[TEMA] [--format text|markdown|man]",
        ".SH DESCRIPCIÓN",
        "VulnClaw combina asignación de tareas en lenguaje natural, bucles autónomos con alcance definido, historial de objetivos, informes, herramientas MCP e integradas, un banco de trabajo de terminal y una Web UI local opcional.",
        ".SH OPCIONES RAÍZ",
    ]
    lines.extend(_roff_pairs(ROOT_OPTIONS))
    lines.extend(
        [
            ".SH MAPA DE COMANDOS",
        ]
    )
    lines.extend(_roff_pairs(tuple((item.name, item.summary) for item in COMMANDS)))

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend([".SH FLAGS COMUNES DE TAREA"])
        lines.extend(_roff_pairs(COMMON_TASK_FLAGS))
        lines.extend(
            [
                ".SH RESTRICCIONES DE ACCIÓN",
                f"Nombres de acción reconocidos: {', '.join(ACTION_NAMES)}.",
            ]
        )

    lines.append(".SH DETALLES DE COMANDOS")
    for item in topics:
        lines.extend(_topic_roff(item))

    lines.extend(
        [
            ".SH CONFIGURACIÓN Y ENTORNO",
            f"Presets de proveedor: {_provider_names()}.",
            ".PP",
            "Directorio de configuración: ~/.vulnclaw por defecto, o VULNCLAW_CONFIG_DIR si está definido.",
            ".PP",
            "Variables de entorno de alto valor: VULNCLAW_LLM_API_KEY, VULNCLAW_LLM_API_KEYS, VULNCLAW_LLM_PROVIDER, VULNCLAW_LLM_BASE_URL, VULNCLAW_LLM_MODEL, VULNCLAW_SESSION_OUTPUT_DIR, VULNCLAW_SESSION_MAX_ROUNDS, VULNCLAW_SESSION_SHOW_THINKING, VULNCLAW_SAFETY_PYTHON_EXECUTE_ENABLED.",
            ".SH SEGURIDAD",
            "VulnClaw es solo para pruebas autorizadas. Los indicadores de alcance y las restricciones de acciones hacen explícitos y exigibles los límites permitidos, pero no reemplazan una autorización por escrito ni un documento claro de reglas de enfrentamiento (rules of engagement).",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _topic_roff(topic: ManualTopic) -> list[str]:
    lines = [
        ".SS " + _roff_escape(topic.name),
        _roff_escape(topic.summary),
        ".PP",
        ".B Uso:",
    ]
    for usage_line in topic.usage.splitlines():
        lines.extend([".br", _roff_escape(usage_line)])
    if topic.flags:
        lines.extend([".PP", ".B Argumentos y flags:"])
        lines.extend(_roff_pairs(topic.flags))
    if topic.notes:
        lines.extend([".PP", ".B Notas:"])
        for note in topic.notes:
            lines.extend([".IP \\[bu] 2", _roff_escape(note)])
    if topic.examples:
        lines.extend([".PP", ".B Ejemplos:"])
        for example in topic.examples:
            lines.extend([".br", _roff_escape(example)])
    return lines


def _roff_pairs(pairs: tuple[tuple[str, str], ...]) -> list[str]:
    lines: list[str] = []
    for name, description in pairs:
        lines.extend(
            [
                f".TP\n.B {_roff_escape(name)}",
                _roff_escape(description),
            ]
        )
    return lines


def _roff_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("-", "\\-")
