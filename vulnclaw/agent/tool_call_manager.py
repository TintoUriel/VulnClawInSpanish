"""Tool-call orchestration helpers for AgentCore."""

from __future__ import annotations

import asyncio
import json
import re
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext


# Default concurrency cap used when the agent config does not specify one.
DEFAULT_TOOL_MAX_CONCURRENT = 5


async def handle_tool_calls(agent: AgentContext, message: Any) -> str:
    """Handle tool calls from the LLM response (legacy single-turn)."""
    results: list[str] = []
    # [Modificado] 2026-06-10 Nyaecho - Corrige el problema de acceso al atributo tool_calls, usa getattr para evitar AttributeError
    for tool_call in (getattr(message, "tool_calls", None) or []):
        func_name = tool_call.function.name
        func_args = safe_parse_tool_args(tool_call.function.arguments)
        tool_result = await agent._execute_mcp_tool(func_name, func_args)
        results.append(f"[tool:{func_name}] {tool_result}")
    return "\n".join(results)


async def handle_tool_calls_with_results(
    agent: AgentContext, message: Any
) -> tuple[list[dict[str, Any]], list[str]]:
    """Handle tool calls with deduplication and rate limiting."""
    max_calls_per_round = 10

    seen: dict[str, dict[str, Any]] = {}
    # [Modificado] 2026-06-10 Nyaecho - Corrige el problema de acceso al atributo tool_calls, usa getattr para evitar AttributeError
    for tool_call in (getattr(message, "tool_calls", None) or []):
        func_name = tool_call.function.name
        func_args = safe_parse_tool_args(tool_call.function.arguments)
        args_key = json.dumps(func_args, sort_keys=True, ensure_ascii=False)
        key = f"{func_name}::{args_key}"
        if key not in seen:
            seen[key] = {
                "tool_call": tool_call,
                "func_name": func_name,
                "func_args": func_args,
            }

    deduplicated = list(seen.values())
    # [Modificado] 2026-06-10 Nyaecho - Corrige el problema de acceso al atributo tool_calls, usa getattr para evitar AttributeError
    total_count = len(getattr(message, "tool_calls", None) or [])
    dedup_count = len(deduplicated)

    to_execute = deduplicated[:max_calls_per_round]
    skipped_calls = deduplicated[max_calls_per_round:]
    skipped_info: list[str] = []

    if total_count > dedup_count:
        skipped_info.append(f"[Deduplicado] {total_count - dedup_count} llamadas duplicadas se combinaron")
    if skipped_calls:
        for sc in skipped_calls:
            skipped_info.append(
                f"[Omitido] {sc['func_name']}({str(sc['func_args'])[:100]}) — se alcanzó el límite de esta ronda, continuará en la siguiente"
            )

    parallel, max_concurrent = _resolve_parallel_settings(agent)

    if parallel and max_concurrent > 1 and len(to_execute) > 1:
        executed = await _execute_parallel(agent, to_execute, max_concurrent)
    else:
        executed = [await _execute_single(agent, item) for item in to_execute]

    # Drop failed calls (preserves legacy behavior) while keeping original order.
    results = [r for r in executed if r is not None]

    return results, skipped_info


def _resolve_parallel_settings(agent: AgentContext) -> tuple[bool, int]:
    """Read tool parallelization settings from the agent config with safe defaults."""
    safety = getattr(getattr(agent, "config", None), "safety", None)
    if safety is None:
        return True, DEFAULT_TOOL_MAX_CONCURRENT
    parallel = bool(getattr(safety, "tool_parallel", True))
    max_concurrent = int(getattr(safety, "tool_max_concurrent", DEFAULT_TOOL_MAX_CONCURRENT) or 1)
    if max_concurrent < 1:
        max_concurrent = 1
    return parallel, max_concurrent


async def _execute_parallel(
    agent: AgentContext, to_execute: list[dict[str, Any]], max_concurrent: int
) -> list[dict[str, Any] | None]:
    """Run independent tool calls concurrently, capped by a semaphore.

    Each call is isolated: an exception in one does not affect the others, and
    the returned list preserves the original ``to_execute`` ordering.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _guarded(item: dict[str, Any]) -> dict[str, Any] | None:
        async with semaphore:
            return await _execute_single(agent, item)

    return await asyncio.gather(*(_guarded(item) for item in to_execute))


def _extract_structured_content(tool_result: Any) -> dict[str, Any] | None:
    """Recover the structured payload embedded by execute_mcp_tool.

    On a successful MCP call, ``execute_mcp_tool`` appends
    ``[structured] {json}`` to the result string. Parse it back so callers get a
    separate ``structured_content`` field without re-executing the tool.
    """
    if not isinstance(tool_result, str):
        return None
    marker = "[structured] "
    idx = tool_result.rfind(marker)
    if idx == -1:
        return None
    try:
        parsed = json.loads(tool_result[idx + len(marker):].strip())
    except (json.JSONDecodeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


async def _execute_single(agent: AgentContext, item: dict[str, Any]) -> dict[str, Any] | None:
    """Execute one tool call with isolated error handling.

    Returns a result dict on success, or ``None`` when the call raised — matching
    the legacy behavior of dropping failed calls from the result set.
    """
    tool_call = item["tool_call"]
    func_name = item["func_name"]
    func_args = item["func_args"]
    try:
        tool_result = await agent._execute_mcp_tool(func_name, func_args)
        # NOTE: do not re-invoke agent.mcp_manager.call_tool here. _execute_mcp_tool
        # already dispatches MCP tools through call_tool (running the side effect
        # once) and embeds any structured content into tool_result as
        # "[structured] {...}". A second call_tool would run the side effect twice,
        # so we recover the structured payload from the result string instead.
        structured_content = _extract_structured_content(tool_result)
        return {
            "tool_call": tool_call,
            "tool_call_id": tool_call.id,
            "content": f"[tool:{func_name}] {tool_result}",
            "structured_content": structured_content,
        }
    except Exception as e:
        print(f"[!] Error al ejecutar la herramienta {func_name}: {e}", file=sys.stderr)
        return None


def safe_parse_tool_args(arguments: str | None) -> dict[str, Any]:
    """Safely parse tool call arguments JSON, with fallback for malformed input."""
    if not arguments:
        return {}
    try:
        return json.loads(arguments)
    except json.JSONDecodeError:
        for suffix in ['"}', '"}]', '"}}', '"}}]', '"]', "}"]:
            try:
                return json.loads(arguments + suffix)
            except json.JSONDecodeError:
                continue
        partial: dict[str, Any] = {}
        kv_pattern = r'"(\w+)"\s*:\s*"([^"]*?)"'
        for match in re.finditer(kv_pattern, arguments):
            partial[match.group(1)] = match.group(2)
        return partial
