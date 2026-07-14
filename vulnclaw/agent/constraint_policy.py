"""Constraint policy helpers for task, phase, and tool enforcement."""

from __future__ import annotations

# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: eliminación de violaciones V2/V3/V4 — los tipos hoja se trasladaron a config/domain_models.py,
#          este archivo los importa desde config y reexporta las funciones de política compartidas.
from vulnclaw.config.domain_models import (
    PHASE_TO_ACTION,
    PentestPhase,
    TaskConstraints,
    normalize_action_name,
    validate_action_constraints,
)

# Re-export for backward compatibility
__all__ = [
    "PHASE_TO_ACTION",
    "PentestPhase",
    "TaskConstraints",
    "normalize_action_name",
    "validate_action_constraints",
    "validate_phase_transition",
    "validate_tool_action",
    "infer_tool_action",
]


def validate_phase_transition(
    next_phase: PentestPhase,
    constraints: TaskConstraints,
) -> str | None:
    """Return a constraint violation message when a phase transition is out of scope."""
    action = PHASE_TO_ACTION.get(next_phase)
    if action is None:
        return None
    violation = validate_action_constraints(action, constraints)
    if violation is None:
        return None
    return f"{violation} (phase transition to {next_phase.value})"


# Herramientas puramente locales/de conocimiento: no interactúan con el objetivo, no están sujetas a la restricción de "alcance de acción"
LOCAL_META_TOOLS = {"load_skill_reference", "crypto_decode"}

# Características de carga útil que realmente representan intención de "explotación" — independientes del medio de transporte (método HTTP/biblioteca de red)
EXPLOIT_PAYLOAD_MARKERS = [
    "union select",
    " or 1=1",
    "'or'",
    "../",
    "..\\",
    "<script",
    "cmd=",
    "php://",
    "data://",
    "extractvalue(",
    "updatexml(",
    "load_file(",
    "into outfile",
    "{{",  # SSTI
    "${",  # SSTI/EL
    "%00",
    "/etc/passwd",
    "/bin/sh",
    "bash -i",
    "nc -e",
    "powershell -e",
]

# Características en python_execute que representan ejecución de comandos locales/reverse shell
PYTHON_EXPLOIT_MARKERS = [
    "os.system",
    "subprocess",
    "pty.spawn",
    "/bin/sh",
    "bash -i",
    "nc -e",
    "reverse_shell",
]


def infer_tool_action(tool_name: str, args: dict[str, object]) -> str:
    """Infer the effective action class of a tool invocation.

    Principio clave: solo una "carga útil de ataque real" se infiere como exploit; el método HTTP,
    el uso de requests/urllib u otros detalles de transporte no constituyen intención de explotación
    (las fases de recon/scan de por sí necesitan enviar POST/OPTIONS o sondear con requests).
    """
    normalized_tool = (tool_name or "").strip().lower()

    if normalized_tool in LOCAL_META_TOOLS:
        return "recon"  # Solo operación local, exenta en conjunto con validate_tool_action

    # Intel tools: read-only lookups (no target egress) and active recon
    # (low-impact target/3rd-party contact) both classify as passive "recon".
    from vulnclaw.intel.tools import READ_ONLY_INTEL_TOOLS, RECON_INTEL_TOOLS

    if normalized_tool in READ_ONLY_INTEL_TOOLS or normalized_tool in RECON_INTEL_TOOLS:
        return "recon"

    if normalized_tool == "nmap_scan":
        return "recon"

    if normalized_tool == "fetch":
        url = str(args.get("url", "") or "").lower()
        method = str(args.get("method", "GET") or "GET").upper()
        body = str(args.get("body", "") or "").lower()
        if any(marker in url or marker in body for marker in EXPLOIT_PAYLOAD_MARKERS):
            return "exploit"
        # El método en sí no representa explotación: GET/HEAD/OPTIONS son reconocimiento, otros (POST para probar formularios, etc.) son escaneo
        if method in ("GET", "HEAD", "OPTIONS"):
            return "recon"
        return "scan"

    if normalized_tool == "python_execute":
        code = str(args.get("code", "") or "").lower()
        if any(marker in code for marker in EXPLOIT_PAYLOAD_MARKERS + PYTHON_EXPLOIT_MARKERS):
            return "exploit"
        # Usar requests/httpx/urllib/socket para sondeo HTTP es escaneo, no explotación
        if any(m in code for m in ("requests.", "httpx.", "urllib", "http.client", "socket")):
            return "scan"
        return "recon"

    if normalized_tool == "brute_force_login":
        return "scan"

    return "scan"


def validate_tool_action(
    tool_name: str, args: dict[str, object], constraints: TaskConstraints
) -> str | None:
    """Return a constraint violation when a tool invocation implies a blocked action."""
    # Las herramientas puramente locales/de conocimiento no están sujetas a la restricción de alcance de acción (cargar documentos, codificar/decodificar no tocan el objetivo)
    if (tool_name or "").strip().lower() in LOCAL_META_TOOLS:
        return None
    inferred = infer_tool_action(tool_name, args)
    violation = validate_action_constraints(inferred, constraints)
    if violation is None:
        return None
    return f"{violation} (tool '{tool_name}' inferred action '{inferred}')"
