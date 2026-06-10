"""Permission model — allow/ask/deny rules for tool execution.

Inspired by Claude Code's permission model, this provides
a simple allow-list mechanism where certain tool+argument
patterns can be automatically allowed or require confirmation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum

from vulnclaw.i18n import _


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


@dataclass
class PermissionRule:
    """A single permission rule.

    Parameters
    ----------
    tool_pattern:
        Tool name pattern, e.g. ``"bash"`` or ``"read_file"``.
        Supports simple glob: ``"bash"`` matches only bash,
        ``"*"`` matches all tools.
    decision:
        What to do when this rule matches.
    reason:
        Human-readable explanation shown to the user.
    """

    tool_pattern: str
    decision: PermissionDecision
    reason: str = ""


class PermissionModel:
    """Permission model with allow/deny rules.

    Default policy:
    - Read-only tools (read_file, web_fetch) → auto-allow
    - Bash → ask
    - Unknown tools → deny
    """

    def __init__(self) -> None:
        self._rules: list[PermissionRule] = [
            PermissionRule("read_file", PermissionDecision.ALLOW, _("tui.agent.permission.read_file")),
            PermissionRule("web_fetch", PermissionDecision.ALLOW, _("tui.agent.permission.web_fetch")),
            PermissionRule("bash", PermissionDecision.ASK, _("tui.agent.permission.bash")),
        ]

    def check(self, tool_name: str, inputs: dict[str, Any]) -> PermissionDecision:
        """Check whether a tool call is allowed.

        Parameters
        ----------
        tool_name:
            The tool being requested.
        inputs:
            The arguments passed to the tool.

        Returns
        -------
        PermissionDecision (ALLOW, DENY, or ASK).
        """
        for rule in self._rules:
            if rule.tool_pattern == "*" or rule.tool_pattern == tool_name:
                return rule.decision
        return PermissionDecision.DENY

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a custom permission rule."""
        self._rules.append(rule)

    def remove_rule(self, tool_pattern: str) -> None:
        """Remove all rules matching a tool pattern."""
        self._rules = [r for r in self._rules if r.tool_pattern != tool_pattern]
