"""Anti-loop and phase-detection helpers for AgentCore."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext


from vulnclaw.agent.context import PentestPhase

FAILED_ACCESS_PATTERNS = [
    "SSLError",
    "ReadTimeout",
    "tiempo de conexión agotado",
    "conexión fallida",
    "502 Bad Gateway",
    "502",
    "503",
    "no se puede acceder",
    "acceso fallido",
    "Connection refused",
    "ConnectionError",
    "TimeoutError",
    "Name or service not known",
    "No route to host",
    "SSL: CERTIFICATE_VERIFY_FAILED",
    "tiempo agotado",
]


def detect_phase_from_output(output: str) -> Optional[PentestPhase]:
    """Detect phase transition signals from LLM output."""
    output_lower = output.lower()
    transitions = [
        (
            PentestPhase.VULN_DISCOVERY,
            ["entrando en descubrimiento de vulnerabilidades", "iniciando escaneo de vulnerabilidades", "detección de vulnerabilidades", "cambiando a descubrimiento de vulnerabilidades", "phase: vuln_discovery"],
        ),
        (
            PentestPhase.EXPLOITATION,
            ["entrando en explotación", "iniciando explotación", "intentando explotar", "cambiando a explotación", "phase: exploitation"],
        ),
        (
            PentestPhase.POST_EXPLOITATION,
            ["entrando en post-explotación", "penetración de red interna", "movimiento lateral", "cambiando a post-explotación", "phase: post_exploitation"],
        ),
        (
            PentestPhase.REPORTING,
            ["generando informe", "organizando resultados", "pentest completado", "cambiando a informe", "phase: reporting"],
        ),
    ]

    for phase, signals in transitions:
        if any(signal in output_lower for signal in signals):
            return phase
    return None


def is_completion_signal(output: str) -> bool:
    """Check if the LLM output signals task completion."""
    completion_signals = [
        "[DONE]",
        "[COMPLETE]",
        "pentest completado",
        "prueba finalizada",
        "tarea completada",
    ]
    return any(signal in output for signal in completion_signals)


def track_failed_target(agent: AgentContext, response_text: str) -> Optional[str]:
    """Track target-level failures and detect repeatedly failed targets."""
    hostname = None
    url_match = re.search(r'https?://([^\s/<>"\')\]]+)', response_text)
    if url_match:
        hostname = url_match.group(1)

    if not hostname:
        return None

    is_failed_access = any(pattern in response_text for pattern in FAILED_ACCESS_PATTERNS)

    if is_failed_access:
        agent.runtime.failed_targets[hostname] = agent.runtime.failed_targets.get(hostname, 0) + 1
        if agent.runtime.failed_targets[hostname] >= 3:
            agent.runtime.blocked_targets.add(hostname)
            return hostname
    else:
        if hostname in agent.runtime.failed_targets and agent.runtime.failed_targets[hostname] > 0:
            agent.runtime.failed_targets[hostname] -= 1

    return None


def is_meaningful_step(step: str) -> bool:
    """Check if a step represents meaningful progress (not just a failed retry)."""
    failure_only_keywords = [
        "SSLError",
        "ReadTimeout",
        "tiempo de conexión agotado",
        "conexión fallida",
        "502 Bad Gateway",
        "no se puede acceder",
        "acceso fallido",
        "Connection refused",
        "ConnectionError",
        "TimeoutError",
        "solicitud fallida",
    ]
    progress_keywords = [
        "hallazgo",
        "confirmación",
        "vulnerabilidad",
        "puerto",
        "ruta",
        "flag",
        "éxito",
        "CVE",
        "filtración",
        "bypass",
        "verificación aprobada",
        "confirmado",
    ]

    if any(keyword in step for keyword in progress_keywords):
        return True
    if any(keyword in step for keyword in failure_only_keywords):
        return False
    return True


def detect_attack_path(output: str) -> Optional[str]:
    """Detect the current attack path/technique from LLM output."""
    output_lower = output.lower()
    path_patterns = [
        (
            "regex_bypass",
            ["preg_replace", "preg_match", "bypass de regex", "bypass de mayúsculas/minúsculas", "bypass con array", "bypass de doble escritura"],
        ),
        (
            "file_inclusion",
            ["php://filter", "inclusión de archivos", "include", "require", "pseudo-protocolo", "php://input", "data://"],
        ),
        ("rce", ["eval(", "system(", "exec(", "passthru(", "shell_exec(", "ejecución de comandos", "rce"]),
        ("sqli", ["inyección sql", "union select", "information_schema", "sqli", "sqlmap"]),
        ("ssti", ["ssti", "template", "jinja2", "twig", "{{", "inyección de plantillas"]),
        ("deserialization", ["deserialización", "unserialize", "serialize", "cadena pop", "wakeup"]),
        ("file_upload", ["subida de archivos", "upload", "webshell", "webshell de una línea"]),
        ("ssrf", ["ssrf", "gopher://", "dict://", "acceso a red interna"]),
        ("xxe", ["xxe", "entidad externa xml", "entity"]),
        ("info_leak", ["filtración de código fuente", ".git", ".svn", "archivo de respaldo", "traversal de directorios", "robots.txt"]),
        ("brute_force", ["fuerza bruta", "contraseña débil", "diccionario", "brute"]),
    ]

    for path_name, keywords in path_patterns:
        if any(keyword in output_lower for keyword in keywords):
            return path_name
    return None
