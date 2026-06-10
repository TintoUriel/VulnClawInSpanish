"""Agent loop — ReAct cycle (Reasoning + Acting).

Mirrors Claude Code's queryLoop():
1. Build context from history
2. Call LLM (streaming)
3. If tool_use → execute tool → append result → loop
4. If no tool_use → done
"""

from __future__ import annotations

import json
import time
from typing import Any, AsyncGenerator

from vulnclaw.cli.textui.services.llm import LlmService
from vulnclaw.cli.textui.tools.registry import ToolRegistry
from vulnclaw.cli.textui.agent.context import ContextBuilder
from vulnclaw.cli.textui.agent.permission import PermissionModel, PermissionDecision
from vulnclaw.i18n import _


class AgentLoop:
    """ReAct loop — single turn of LLM + optional tool execution.

    Each ``run()`` call completes one user message → response cycle.
    If the LLM requests a tool, it executes the tool and appends
    the result to the context, then returns the full result.
    """

    def __init__(
        self,
        llm: LlmService,
        tools: ToolRegistry,
        context_builder: ContextBuilder,
        permission: PermissionModel,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._context_builder = context_builder
        self._permission = permission

        # Callbacks for UI updates
        self.on_text: callable | None = None  # async (str) -> None
        self.on_tool_start: callable | None = None  # async (name, params) -> str (tool_id)
        self.on_tool_end: callable | None = None  # async (tool_id, status, result) -> None
        self.on_confirm: callable | None = None  # async (tool_name) -> bool

    async def run(
        self,
        history: list[dict[str, str]],
        user_text: str,
    ) -> str:
        """Execute one user message → response cycle.

        Parameters
        ----------
        history:
            Previous user/assistant message pairs.
        user_text:
            The current user input.

        Returns
        -------
        The full assistant response text.
        """
        messages = self._context_builder.build(history, user_text)
        full_text = ""

        async def _on_text(chunk: str) -> None:
            nonlocal full_text
            full_text += chunk
            if self.on_text:
                await self.on_text(chunk)

        async def _on_tool_call(
            name: str,
            args: dict[str, Any],
            tool_content: str = "",
            tool_reasoning: str = "",
        ) -> None:
            nonlocal full_text, messages

            # Permission check
            decision = self._permission.check(name, args)
            if decision == PermissionDecision.DENY:
                full_text += _("tui.agent.loop.denied", name=name)
                return

            if decision == PermissionDecision.ASK and self.on_confirm:
                confirmed = await self.on_confirm(name)
                if not confirmed:
                    full_text += _("tui.agent.loop.cancelled", name=name)
                    return

            # Execute tool
            tool = self._tools.get(name)
            if tool is None:
                full_text += _("tui.agent.loop.unknown_tool", name=name)
                return

            tool_id = ""
            if self.on_tool_start:
                tool_id = await self.on_tool_start(name, args)

            result = await tool.run(args)

            if self.on_tool_end:
                await self.on_tool_end(tool_id, result.status.value, result)

            # Append tool result to messages so LLM can see it
            # Include reasoning_content for APIs (e.g. DeepSeek) that require
            # it to be passed back in subsequent requests.
            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": tool_content or None,
                "tool_calls": [
                    {
                        "id": f"call_{time.time_ns()}",
                        "type": "function",
                        "function": {"name": name, "arguments": json.dumps(args)},
                    }
                ],
            }
            if tool_reasoning:
                assistant_msg["reasoning_content"] = tool_reasoning
            messages.append(assistant_msg)
            messages.append({
                "role": "tool",
                "tool_call_id": f"call_{time.time_ns()}",
                "content": result.output[:5000] if result.status.value == "done" else result.error,
            })

            # Re-call LLM with tool result
            if self.on_text:
                exec_result = _("tui.agent.loop.success") if result.status.value == "done" else _("tui.agent.loop.failure")
                await self.on_text(_("tui.agent.loop.execution_result", status=result.status.value.upper(), name=name, result=exec_result))

            # Stream another response after tool result
            await self._llm.stream_chat(
                messages=messages,
                on_text=_on_text,
                on_tool_call=_on_tool_call if self._tools.list_tools() else None,
                on_reasoning=None,
            )

        await self._llm.stream_chat(
            messages=messages,
            on_text=_on_text,
            on_tool_call=_on_tool_call if self._tools.list_tools() else None,
            on_reasoning=None,
        )

        return full_text
