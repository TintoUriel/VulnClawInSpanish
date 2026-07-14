"""Input analysis helpers for AgentCore."""

from __future__ import annotations

import re
from typing import Optional

from vulnclaw.agent.context import PentestPhase, TaskConstraints

# A ``/skill`` launch is dispatched as the prompt ``Use VulnClaw skill <name>. …``
# (see ``dispatch_skill_slash_command``). Captured so we can tell a self-discovering
# skill launch apart from an ordinary target-first task.
_SKILL_LAUNCH_RE = re.compile(r"^\s*Use VulnClaw skill\s+([A-Za-z0-9_-]+)\.", re.IGNORECASE)


def _is_self_discovering_skill_launch(text: str) -> bool:
    """Return True when ``text`` launches a ``requires_target: false`` skill.

    Such a skill (e.g. ``hackerone``) receives a *discovery seed* — a scope link —
    rather than a scan target. Deriving ``allowed_hosts`` from that seed would lock
    the run to the seed's host (e.g. ``hackerone.com``) and block the in-scope assets
    the skill later discovers, so the implicit host constraint is skipped for these
    launches. The skill's own scope-guard, plus ``BLOCKED_PATTERNS`` /
    ``RESERVED_IP_RANGES`` / target validation, remain in force. Explicit constraint
    language in the prompt is unaffected.
    """
    match = _SKILL_LAUNCH_RE.match(text or "")
    if not match:
        return False
    try:
        from vulnclaw.skills.loader import load_skill_by_name

        skill = load_skill_by_name(match.group(1))
    except Exception:
        return False
    return bool(skill) and skill.get("requires_target", True) is False


def detect_phase(user_input: str) -> Optional[PentestPhase]:
    """Detect pentest phase from user input using keyword matching."""
    input_lower = user_input.lower()
    phase_keywords = {
        PentestPhase.RECON: [
            "recolección de información",
            "reconocimiento",
            "escaneo de puertos",
            "subdominio",
            "fingerprinting",
            "escaneo de directorios",
            "recon",
            "scan",
            "puerto",
            "nmap",
            "recopilar",
        ],
        PentestPhase.VULN_DISCOVERY: [
            "descubrimiento de vulnerabilidades",
            "escaneo de vulnerabilidades",
            "qué vulnerabilidades hay",
            "cve",
            "detección de seguridad",
            "vulnerability",
            "vulnerabilidad",
            "inyección",
            "xss",
            "sqli",
        ],
        PentestPhase.EXPLOITATION: [
            "explotar",
            "exploit",
            "poc",
            "verificar vulnerabilidad",
            "ejecutar comando",
            "rce",
            "getshell",
            "obtener privilegios",
            "dale una probada",
            "intentar",
        ],
        PentestPhase.POST_EXPLOITATION: [
            "post-explotación",
            "red interna",
            "movimiento lateral",
            "escalación de privilegios",
            "mantener acceso",
            "pivot",
            "post-exploitation",
            "túnel",
            "proxy",
        ],
        PentestPhase.REPORTING: ["informe", "report", "resumen", "organizar", "generar informe"],
    }
    for phase, keywords in phase_keywords.items():
        if any(keyword in input_lower for keyword in keywords):
            return phase
    for pattern in (r"\d{1,3}(?:\.\d{1,3}){3}", r"https?://\S+"):
        if re.search(pattern, user_input):
            return PentestPhase.RECON
    return None


def detect_target(user_input: str) -> Optional[str]:
    """Extract target from user input."""
    for pattern in (
        r"(https?://[a-zA-Z0-9][-a-zA-Z0-9.:]*)",
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        r"([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)",
    ):
        match = re.search(pattern, user_input)
        if match:
            return match.group(1).rstrip("/.") if match.groups() else match.group(0)
    return None


def extract_task_constraints(user_input: str) -> TaskConstraints:
    """Extract structured hard constraints from natural-language user input."""
    text = user_input or ""
    lowered = text.lower()
    constraints = TaskConstraints()
    detected_target = detect_target(text)

    allowed_port_patterns = [
        r"(?:solo|únicamente)\s+(?:se\s+permite\s+)?(?:probar|prueba|escanear|escanea|testear|testea)\s+(?:el\s+)?puerto\s+(\d{1,5})",
        r"(?:only|just)\s+(?:test|scan)\s+(?:port\s+)?(\d{1,5})",
    ]
    for pattern in allowed_port_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            port = int(match)
            if 0 < port <= 65535 and port not in constraints.allowed_ports:
                constraints.allowed_ports.append(port)

    blocked_group_patterns = [
        r"(?:no\s+toques|no\s+pruebes|prohibido\s+probar|prohibido\s+escanear|no\s+escanees)\s*([0-9,\s y]+)(?:\s*puertos?)?",
    ]
    for pattern in blocked_group_patterns:
        for group in re.findall(pattern, text):
            for match in re.findall(r"\d{1,5}", group):
                port = int(match)
                if 0 < port <= 65535 and port not in constraints.blocked_ports:
                    constraints.blocked_ports.append(port)

    if any(
        token in lowered
        for token in [
            "solo hacer reconocimiento",
            "únicamente reconocimiento",
            "recon only",
            "only recon",
        ]
    ):
        constraints.allowed_actions = ["recon"]
    if any(
        token in lowered
        for token in ["no explotar", "prohibido explotar", "do not exploit", "no exploit"]
    ):
        constraints.blocked_actions.append("exploit")

    allow_match = re.search(r"only allowed actions:\s*([a-z_,\s-]+)", lowered)
    if allow_match:
        constraints.allowed_actions = [
            item.strip() for item in allow_match.group(1).split(",") if item.strip()
        ]

    block_match = re.search(r"blocked actions:\s*([a-z_,\s-]+)", lowered)
    if block_match:
        constraints.blocked_actions.extend(
            [
                item.strip()
                for item in block_match.group(1).split(",")
                if item.strip() and item.strip() not in constraints.blocked_actions
            ]
        )

    if any(
        token in lowered
        for token in [
            "solo prueba esta ruta",
            "únicamente prueba esta ruta",
            "solo probar esta ruta",
            "solo esta ruta",
        ]
    ):
        path_match = re.search(r"https?://[^\s]+(/[^\s?#]*)", text)
        if not path_match:
            path_match = re.search(r"(/[A-Za-z0-9._/\-]+)", text)
        if path_match:
            path = path_match.group(1).rstrip("/")
            if path and path not in constraints.allowed_paths:
                constraints.allowed_paths.append(path)

    blocked_host_match = re.search(r"blocked host\s+([a-z0-9.-]+)", lowered)
    if blocked_host_match:
        host = blocked_host_match.group(1).strip()
        if host and host not in constraints.blocked_hosts:
            constraints.blocked_hosts.append(host)

    blocked_path_match = re.search(r"blocked path\s+(/[^\s]+)", lowered)
    if blocked_path_match:
        path = blocked_path_match.group(1).rstrip("/")
        if path and path not in constraints.blocked_paths:
            constraints.blocked_paths.append(path)

    if detected_target and not _is_self_discovering_skill_launch(text):
        target_lower = detected_target.lower()
        if target_lower.startswith("http://") or target_lower.startswith("https://"):
            host_match = re.search(r"^https?://([^/:?#]+)", target_lower)
            if host_match:
                host = host_match.group(1)
                if host and host not in constraints.allowed_hosts:
                    constraints.allowed_hosts.append(host)
        elif "." in target_lower:
            if target_lower not in constraints.allowed_hosts:
                constraints.allowed_hosts.append(target_lower)

    if (
        constraints.allowed_ports
        or constraints.blocked_ports
        or constraints.allowed_hosts
        or constraints.blocked_hosts
        or constraints.allowed_paths
        or constraints.blocked_paths
        or constraints.allowed_actions
        or constraints.blocked_actions
    ):
        constraints.strict_mode = True

    return constraints


def extract_user_vuln_hint(user_input: str) -> str:
    """Extract explicit vulnerability hints from user input."""
    vuln_keywords = [
        "inyección SQL",
        "SQLi",
        "XSS",
        "RCE",
        "inyección de comandos",
        "inclusión de archivos",
        "traversal de directorios",
        "LFI",
        "RFI",
        "SSRF",
        "CSRF",
        "contraseña débil",
        "fuerza bruta",
        "bypass de autenticación",
        "acceso no autorizado",
        "fuga de información",
        "fuga de información sensible",
    ]
    user_lower = user_input.lower()
    found_vulns = [v for v in vuln_keywords if v.lower() in user_lower]
    if not found_vulns:
        return ""
    url_match = re.search(r"https?://\S+", user_input)
    path_match = re.search(r"/[\w\-./?=&%#]+", user_input)
    target = url_match.group(0) if url_match else (path_match.group(0) if path_match else "")
    vuln_str = "/".join(found_vulns[:3])
    if target:
        return (
            f"[Indicación explícita del usuario — Ronda 1]\n"
            f"El usuario te indica explícitamente que [{target}] tiene la vulnerabilidad [{vuln_str}].\n"
            f"\n"
            f"→ ¡Debes construir y enviar de inmediato una solicitud de prueba PoC!\n"
            f"→ Usa la herramienta fetch para enviar la solicitud directamente y observar la respuesta real.\n"
            f"→ No explores rutas primero ni hagas recolección de información antes; prueba la vulnerabilidad directamente.\n"
            f"\n"
            f"{get_payload_examples(found_vulns, target)}"
        )
    return (
        f"[Indicación explícita del usuario]\n"
        f"El usuario te pide que pruebes la vulnerabilidad [{vuln_str}].\n"
        f"→ Construye de inmediato una prueba PoC basada en la información del objetivo ya descubierta; no hagas recolección de información adicional."
    )


def get_payload_examples(found_vulns: list[str], target: str) -> str:
    """Return concrete PoC payload examples for the given vulnerability types."""
    lines = ["[Ejemplos de payload PoC]"]
    for vuln in found_vulns[:2]:
        if "SQL" in vuln:
            lines += [
                "Prueba de inyección SQL (blind boolean):",
                f"  GET {target}?id=1' AND 1=1--  → observa la longitud de la respuesta",
                f"  GET {target}?id=1' AND 1=2--  → ¿la longitud es distinta?",
                "Prueba de inyección SQL (basada en errores):",
                f"  GET {target}?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--",
            ]
        elif "XSS" in vuln:
            lines += [
                "Prueba de XSS:",
                f"  GET {target}?q=<script>alert(1)</script>  → ¿la página refleja este contenido?",
                f"  GET {target}?q=<img src=x onerror=alert(1)>",
            ]
        elif "RCE" in vuln or "inyección de comandos" in vuln:
            lines += [
                "Prueba de RCE/inyección de comandos:",
                f"  GET {target}?cmd=whoami  → observa si hay salida del comando",
                f"  GET {target}?c=whoami  → prueba distintos nombres de parámetro",
            ]
        elif "inclusión de archivos" in vuln or "traversal de directorios" in vuln:
            lines += [
                "Prueba de inclusión de archivos/traversal de directorios:",
                f"  GET {target}?f=/etc/passwd  → lee un archivo del sistema",
                f"  GET {target}?f=../../../../etc/passwd",
            ]
        elif "SSRF" in vuln:
            lines += [
                "Prueba de SSRF:",
                f"  GET {target}?url=http://127.0.0.1  → ¿hay respuesta?",
                f"  GET {target}?url=http://169.254.169.254/latest/meta-data/",
            ]
    return "\n".join(lines[:12])


def build_user_vuln_directive(user_input: str) -> str:
    """Backward-compatible alias for explicit vulnerability hint extraction."""
    return extract_user_vuln_hint(user_input)
