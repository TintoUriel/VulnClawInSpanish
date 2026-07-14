"""Skill context selection helpers for AgentCore.

Thin adapter over the deterministic :mod:`vulnclaw.skills.resolver`. It derives
typed routing signals (phase, target type, vuln hints, technologies) from the
turn's request and session state, resolves a single bundle, records its
provenance on the session, and renders it as a prompt block (concise primary
body, support summaries, resolver reason, on-demand reference hints).

Resolving *once* per turn is deliberate: the recorded provenance (attached to
findings) must name the same bundle that was placed in the prompt.
"""

from __future__ import annotations

from typing import Any, Optional

from vulnclaw.skills.loader import load_skill_by_name
from vulnclaw.skills.resolver import SkillQuery, SkillResolver, SkillSelection
from vulnclaw.skills.routing import keyword_present, normalize_token

# Internal (Chinese) phase labels → resolver's canonical phase tokens. The IDLE
# label is intentionally absent so "not started" contributes no phase signal.
_PHASE_TOKEN: dict[str, str] = {
    "信息收集": "recon",
    "漏洞发现": "vuln_discovery",
    "漏洞利用": "exploitation",
    "后渗透": "post_exploitation",
    "报告生成": "reporting",
}

# Free-text vuln keyword (bilingual) → canonical vulnerability_class token.
_VULN_HINT_KEYWORDS: dict[str, str] = {
    "inyección sql": "sqli",
    "sqli": "sqli",
    "xss": "xss",
    "rce": "rce",
    "inyección de comandos": "rce",
    "ejecución remota de código": "rce",
    "ssrf": "ssrf",
    "ssti": "ssti",
    "xxe": "xxe",
    "csrf": "csrf",
    "deserialización": "deserialization",
    "control de acceso indebido": "idor",
    "idor": "idor",
    "carga de archivos": "file_upload",
    "recorrido de directorios": "path_traversal",
    "salto de directorio": "path_traversal",
    "lfi": "path_traversal",
    "rfi": "path_traversal",
    "jwt": "jwt",
    "oauth": "oauth",
    "bypass de autenticación": "auth_bypass",
    "inyección de prompt": "prompt_injection",
    "prompt injection": "prompt_injection",
    "escalación de privilegios": "privilege_escalation",
    "movimiento lateral": "lateral_movement",
}

# Technology keywords worth passing as a routing signal.
_TECH_KEYWORDS = ("php", "java", "python", "nodejs", "node.js", "wordpress", "django", "spring")


def _infer_target_type(target: Optional[str], text: str) -> Optional[str]:
    """Conservatively infer a target type from the target string / request text."""
    blob = f"{target or ''} {text}".lower()
    if target:
        low = target.lower()
        if low.startswith(("http://", "https://")):
            return "web"
        if _looks_like_ip(low):
            return "network"
    if any(kw in blob for kw in ("apk", "android")):
        return "android"
    if "http://" in blob or "https://" in blob:
        return "web"
    return None


def _looks_like_ip(value: str) -> bool:
    parts = value.split(":")[0].split(".")
    return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)


def _extract_vuln_hints(text: str) -> list[str]:
    low = text.lower()
    hints: list[str] = []
    for keyword, token in _VULN_HINT_KEYWORDS.items():
        if token not in hints and keyword_present(keyword, low):
            hints.append(token)
    return hints


def _extract_technologies(text: str, recon_data: Optional[dict[str, Any]]) -> list[str]:
    low = text.lower()
    techs: list[str] = []
    for keyword in _TECH_KEYWORDS:
        if keyword_present(keyword, low):
            token = normalize_token(keyword)
            if token not in techs:
                techs.append(token)
    if isinstance(recon_data, dict):
        raw = recon_data.get("technologies")
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, str):
                    token = normalize_token(item)
                    if token and token not in techs:
                        techs.append(token)
    return techs


def _build_query(
    user_input: Optional[str],
    *,
    phase_label: Optional[str] = None,
    target: Optional[str] = None,
    recon_data: Optional[dict[str, Any]] = None,
    task_summary: Optional[str] = None,
) -> SkillQuery:
    text = f"{user_input or ''} {task_summary or ''}"
    return SkillQuery.from_input(
        user_input,
        phase=_PHASE_TOKEN.get(phase_label or ""),
        target_type=_infer_target_type(target, text),
        vuln_hints=_extract_vuln_hints(text),
        technologies=_extract_technologies(text, recon_data),
        task_summary=task_summary,
    )


def resolve_active_skill_selection(
    user_input: Optional[str] = None,
    **kwargs: Any,
) -> Optional[SkillSelection]:
    """Resolve the active skill bundle for a turn, or None on no input/error."""
    task_summary = kwargs.get("task_summary")
    if not (user_input or task_summary):
        return None
    try:
        selection = SkillResolver().resolve(_build_query(user_input, **kwargs))
        return selection if not selection.is_empty() else None
    except Exception:
        return None


def apply_skill_selection(state: Any, user_input: Optional[str] = None) -> Optional[str]:
    """Resolve, record provenance on ``state``, and return the prompt context.

    Single entry point for :class:`AgentCore`: resolves the bundle once from the
    session's phase/target/recon signals, stores the selection so findings this
    turn inherit it, and returns the formatted context for the same bundle.
    """
    phase_label = getattr(getattr(state, "phase", None), "value", None)
    selection = resolve_active_skill_selection(
        user_input,
        phase_label=phase_label,
        target=getattr(state, "target", None),
        recon_data=getattr(state, "recon_data", None),
    )
    try:
        state.set_active_skill_selection(selection.to_provenance() if selection else None)
    except Exception:
        pass

    if selection and selection.primary:
        return format_selection_context(selection)
    if user_input:
        # Explicit input that matched nothing (non-security) → inject nothing.
        return None
    return _default_playbook()


def get_active_skill_context(user_input: Optional[str] = None, **kwargs: Any) -> Optional[str]:
    """Get prompt context for the most relevant bundle (no provenance recording).

    Standalone helper for callers that only need the rendered context. Non-
    security input yields nothing; absent any input, the ``pentest-flow``
    playbook is the session default.
    """
    if user_input or kwargs.get("task_summary"):
        selection = resolve_active_skill_selection(user_input, **kwargs)
        if selection and selection.primary:
            return format_selection_context(selection)
        return None
    return _default_playbook()


def _default_playbook() -> Optional[str]:
    try:
        skill = load_skill_by_name("pentest-flow")
        if skill:
            return skill.get("content", "")
    except Exception:
        pass
    return None


def format_selection_context(selection: SkillSelection) -> str:
    """Render a resolved bundle into a prompt block."""
    parts: list[str] = []

    primary = load_skill_by_name(selection.primary) if selection.primary else None
    if primary:
        parts.append(primary.get("content", ""))

    for name in selection.supporting:
        skill = load_skill_by_name(name)
        if not skill:
            continue
        desc = skill.get("description", "").strip()
        summary = desc.splitlines()[0] if desc else ""
        parts.append(f"## Skill de apoyo: {name}\n{summary}")

    refs = primary.get("references", []) if primary else []
    if refs:
        ref_list = ", ".join(refs[:10])
        if len(refs) > 10:
            ref_list += f", ... ({len(refs)} total)"
        parts.append(
            "## Documentación de referencia disponible\n"
            f"Los siguientes documentos de referencia se pueden cargar cuando sea "
            f"necesario mediante load_skill_reference: {ref_list}"
        )

    if selection.reason:
        parts.append(f"<!-- skill routing: {selection.reason} -->")

    return "\n\n".join(p for p in parts if p)
