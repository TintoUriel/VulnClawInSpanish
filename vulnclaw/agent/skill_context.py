"""Skill context selection helpers for AgentCore."""

from __future__ import annotations

import re
from typing import Optional

_EXPLICIT_SKILL_RE = re.compile(
    r"\buse\s+vulnclaw\s+skill\s+([A-Za-z0-9][A-Za-z0-9_-]*)\b",
    re.IGNORECASE,
)


def get_active_skill_context(user_input: Optional[str] = None) -> Optional[str]:
    """Get context from the most relevant Skill based on user input."""
    if user_input:
        try:
            explicit_skill = _load_explicit_skill(user_input)
            if explicit_skill:
                return _format_skill_context(explicit_skill)

            from vulnclaw.skills.dispatcher import SkillDispatcher

            dispatcher = SkillDispatcher()
            skill = dispatcher.dispatch(user_input)
            if skill:
                return _format_skill_context(skill)
        except Exception:
            pass

    try:
        from vulnclaw.skills.loader import load_skill_by_name

        skill = load_skill_by_name("pentest-flow")
        if skill:
            return skill.get("content", "")
    except Exception:
        pass
    return None


def _load_explicit_skill(user_input: str) -> Optional[dict]:
    match = _EXPLICIT_SKILL_RE.search(user_input)
    if not match:
        return None

    from vulnclaw.skills.loader import load_skill_by_name

    return load_skill_by_name(match.group(1))


def _format_skill_context(skill: dict) -> str:
    context = skill.get("content", "")
    refs = skill.get("references", [])
    if refs:
        ref_list = ", ".join(refs[:10])
        if len(refs) > 10:
            ref_list += f", ... ({len(refs)} total)"
        context += f"\n\n## 可用参考文档\n以下参考文档可在需要时通过 load_skill_reference 加载: {ref_list}"
    return context
