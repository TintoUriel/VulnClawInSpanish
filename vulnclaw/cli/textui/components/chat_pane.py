"""Main chat pane — Claude Code style chat interface.

This is the core UI component. It manages:

- Message display (user, assistant, tool calls, system)
- Slash command dispatch via :class:`CommandRegistry`
- Completion list (shown **below** the input bar)
- Chat history persistence (save / load)
- Streaming LLM interaction
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from vulnclaw.i18n import _
from vulnclaw.cli.textui.components.chat_input import ChatInput
from vulnclaw.cli.textui.components.message_widgets import (
    AssistantText,
    FormOperation,
    SystemMessage,
    ToolCallMessage,
    UserMessage,
)
from vulnclaw.cli.textui.utils.state import TuiStateWrapper
from vulnclaw.cli.textui.services.history import (
    ChatMessageData,
    get_history_store,
)
from vulnclaw.cli.textui.services.llm import LlmService
from vulnclaw.cli.textui.commands.registry import CommandRegistry
from vulnclaw.cli.textui.tools.registry import ToolRegistry
from vulnclaw.cli.textui.tools.bash import bash_tool
from vulnclaw.cli.textui.tools.file_read import file_read_tool
from vulnclaw.cli.textui.tools.web_fetch import web_fetch_tool


class ChatPane(Vertical):
    """Main chat pane — message area + completion list + input bar.

    Layout (top → bottom)::

        ┌─────────────────────────────┐
        │  #chat-messages (scroll)    │  ← fills remaining space
        ├─────────────────────────────┤
        │  #completion-list           │  ← hidden by default,
        │  (ListView, auto-height)    │     shown when user types /x
        ├─────────────────────────────┤
        │  ChatInput                  │  ← dock: bottom
        └─────────────────────────────┘
    """

    DEFAULT_CSS = """
    ChatPane {
        height: 1fr;
    }

    #chat-messages {
        height: 1fr;
        overflow-y: scroll;
        scrollbar-gutter: stable;
        padding: 0 1;
    }

    #completion-list {
        height: auto;
        max-height: 10;
        display: none;
        border-top: solid $primary;
        border-bottom: solid $primary;
        background: $surface;
        margin: 0;
        padding: 0 1;
    }

    #completion-list > ListItem {
        padding: 0 1;
    }

    #completion-list > ListItem.--highlighted {
        background: $accent 30%;
    }

    ChatInput {
        dock: bottom;
    }
    """

    # ------------------------------------------------------------------
    # Custom messages
    # ------------------------------------------------------------------

    class ExecuteRequest(Message):
        """Posted when a scan should be launched."""

        def __init__(self, config: dict[str, Any]) -> None:
            super().__init__()
            self.config = config

    class LoadHistoryRequest(Message):
        """Posted when a history load is requested."""

        def __init__(self, target: str) -> None:
            super().__init__()
            self.target = target

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def __init__(
        self,
        state: TuiStateWrapper,
        command_registry: CommandRegistry,
        llm: LlmService | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._state = state
        self._cmd_registry = command_registry
        self._llm = llm or LlmService()

        self._messages: list[UserMessage | AssistantText | ToolCallMessage | SystemMessage] = []
        self._current_assistant: AssistantText | None = None
        self._pending_tools: dict[str, ToolCallMessage] = {}

        # Tool registry for ReAct loop
        self._tool_registry = ToolRegistry()
        self._tool_registry.register(bash_tool)
        self._tool_registry.register(file_read_tool)
        self._tool_registry.register(web_fetch_tool)
        self._tool_defs = self._tool_registry.to_openai_tools()

        # Tool support flag — populated by check_tool_support() on mount.
        # Default is False (conservative): the LLM receives pure text only.
        # Only if the API confirms tool/function calling support, the ReAct
        # loop enables tools for direct LLM-invoked function calling.
        self._tools_supported: bool = False

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="chat-messages"):
            yield Static("")  # placeholder — messages are mounted here
        yield ListView(id="completion-list")
        yield ChatInput(id="chat-input")

    def on_mount(self) -> None:
        """Focus input and sync commands to ChatInput on mount."""
        self._focus_input()

        # Sync commands from registry to ChatInput
        chat_input = self.query_one("#chat-input", ChatInput)
        chat_input.update_commands(self._cmd_registry.list_commands())

        # Proactively check tool support in background
        self.call_later(self._async_check_tool_support)

    async def _async_check_tool_support(self) -> None:
        """Silently check LLM tool support and update the flag.

        This runs once at startup.  No UI feedback is shown — the result
        simply controls whether the ReAct loop uses function calling or
        falls back to external tool orchestration via slash commands.
        """
        try:
            self._tools_supported = await self._llm.check_tool_support()
        except Exception:
            self._tools_supported = False

    # ------------------------------------------------------------------
    # Message management
    # ------------------------------------------------------------------

    def add_user_message(self, text: str) -> None:
        """Add a user message bubble."""
        msg = UserMessage(text)
        self._mount_message(msg)
        self._messages.append(msg)

    def add_assistant_text(self, text: str) -> AssistantText:
        """Add an assistant text message (supports streaming)."""
        render_mode = self._state.config.session.render_mode
        msg = AssistantText(text, render_mode=render_mode)
        self._mount_message(msg)
        self._messages.append(msg)
        self._current_assistant = msg
        return msg

    def add_tool_call(self, name: str, params: str) -> ToolCallMessage:
        """Add a tool call message (supports status updates)."""
        msg = ToolCallMessage(name, params)
        self._mount_message(msg)
        self._messages.append(msg)
        return msg

    def update_tool_status(self, tool_id: str, status: str, **kwargs) -> None:
        """Update a tool call's status."""
        # tool_id not needed — just update the last ToolCallMessage
        for msg in reversed(self._messages):
            if isinstance(msg, ToolCallMessage):
                msg.update_status(status, **kwargs)
                break

    def add_form_operation(
        self,
        form_type: str,
        field: str,
        old_value: str,
        new_value: str,
    ) -> None:
        """Add a form field change record."""
        msg = FormOperation(form_type, field, old_value, new_value)
        self._mount_message(msg)
        self._messages.append(msg)

    def add_system_message(self, content: str) -> SystemMessage:
        """Add a system feedback message."""
        msg = SystemMessage(content)
        self._mount_message(msg)
        self._messages.append(msg)
        return msg

    def clear_messages(self) -> None:
        """Clear all messages from the chat area."""
        self._messages.clear()
        # Rebuild the messages container
        container = self.query_one("#chat-messages", VerticalScroll)
        container.remove_children()
        container.mount(Static(""))

    def _mount_message(self, msg) -> None:
        """Mount a message into the scrollable container."""
        container = self.query_one("#chat-messages", VerticalScroll)
        container.mount(msg)
        container.scroll_end(animate=False)

    # ------------------------------------------------------------------
    # ChatInput message handlers  (completion delegation)
    # ------------------------------------------------------------------

    @staticmethod
    def _cmd_name_from_item(item: ListItem) -> str:
        """Extract the command name from a completion ListItem's label.

        Label format: ``{name}  — {desc}``  (Textual markup stripped).
        """
        if not item.children:
            return ""
        try:
            raw = str(item.children[0].render())
            return raw.split(" \u2014 ")[0].strip().lstrip("/")
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # ChatInput message handlers  (completion delegation)
    # ------------------------------------------------------------------

    def on_chat_input_show_completions(
        self,
        event: ChatInput.ShowCompletions,
    ) -> None:
        """Populate and show the completion list."""
        list_view = self.query_one("#completion-list", ListView)
        list_view.clear()
        for name, desc in event.matches:
            item = ListItem(Static(f"[cyan]/{name}[/]  \u2014 [dim]{desc}[/]"))
            list_view.append(item)
        list_view.display = True

        chat_input = self.query_one("#chat-input", ChatInput)
        chat_input.completion_active = True

    def on_chat_input_hide_completions(
        self,
        event: ChatInput.HideCompletions,
    ) -> None:
        """Hide the completion list."""
        list_view = self.query_one("#completion-list", ListView)
        list_view.display = False
        list_view.clear()

        chat_input = self.query_one("#chat-input", ChatInput)
        chat_input.completion_active = False

    def on_chat_input_navigate_completions(
        self,
        event: ChatInput.NavigateCompletions,
    ) -> None:
        """Move selection within the completion list (wraps around)."""
        list_view = self.query_one("#completion-list", ListView)
        children = list(list_view.children)
        if not children:
            return

        if event.direction == "up":
            if list_view.index is None or list_view.index <= 0:
                list_view.index = len(children) - 1  # wrap to last
            else:
                list_view.action_cursor_up()
        else:
            if list_view.index is None or list_view.index >= len(children) - 1:
                list_view.index = 0  # wrap to first
            else:
                list_view.action_cursor_down()

    def _get_highlighted_cmd_name(self) -> str:
        """Extract command name from the highlighted completion item."""
        list_view = self.query_one("#completion-list", ListView)
        selected = list_view.highlighted_child
        if selected is None:
            return ""
        return self._cmd_name_from_item(selected)

    # ── ListView mouse-click ──────────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle mouse click on a completion item."""
        if event.list_view.id != "completion-list":
            return

        cmd_name = self._cmd_name_from_item(event.item)
        if not cmd_name:
            return

        chat_input = self.query_one("#chat-input", ChatInput)
        chat_input.value = f"/{cmd_name}"
        chat_input._submit(f"/{cmd_name}")

        list_view = self.query_one("#completion-list", ListView)
        list_view.display = False
        list_view.clear()
        chat_input.completion_active = False

    # ------------------------------------------------------------------
    # ChatInput.Submitted handler
    # ------------------------------------------------------------------

    def on_chat_input_submitted(self, event: ChatInput.Submitted) -> None:
        """Handle user input submission.

        If the completion list is visible with a highlighted item, the
        input is silently replaced with the selected command ("Enter to
        select + submit").  Otherwise the raw input is used.
        """
        text = event.value.strip()
        if not text:
            return

        # Auto-select highlighted completion item
        if text.startswith("/") and len(text) > 1:
            list_view = self.query_one("#completion-list", ListView)
            if list_view.display:
                selected = list_view.highlighted_child
                if selected:
                    cmd_name = self._cmd_name_from_item(selected)
                    if cmd_name:
                        text = f"/{cmd_name}"
                        # Hide completions after auto-select
                        list_view.display = False
                        list_view.clear()
                        chat_input = self.query_one("#chat-input", ChatInput)
                        chat_input.completion_active = False

        self._input_task = asyncio.create_task(self._handle_input(text))

    # ------------------------------------------------------------------
    # Input processing
    # ------------------------------------------------------------------

    # Cancel/abort support
    _input_task: asyncio.Task | None = None
    _cancel_requested: bool = False

    @property
    def is_busy(self) -> bool:
        """Whether an LLM interaction is currently in progress."""
        if self._cancel_requested:
            return True
        if self._input_task and not self._input_task.done():
            return True
        return False

    def cancel_current(self) -> None:
        """Request cancellation of the ongoing LLM interaction."""
        self._cancel_requested = True
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()

    async def _handle_input(self, text: str) -> None:  # noqa: C901
        """Route input: command vs chat."""
        self._cancel_requested = False
        if text.startswith("/"):
            cmd_name = await self._handle_command(text)
            # Recognised commands are handled entirely by the registry
            if cmd_name is not None:
                return
        # Normal chat or unknown command — show user message
        self.add_user_message(text)
        if not text.startswith("/"):
            await self._handle_chat(text)

    async def _handle_command(self, command_line: str) -> str | None:
        """Dispatch a slash command via the registry.

        Returns the command name if found, ``None`` if unknown.
        """
        cmd_name = await self._cmd_registry.dispatch(
            command_line,
            chat_pane=self,
            state=self._state,
            app=self.app,
        )

        if cmd_name is None:
            # Unknown command
            self.add_system_message(
                _("tui.component.chat_pane.unknown_command").format(
                    cmd=command_line.split()[0]
                )
            )
        return cmd_name

    async def _handle_chat(self, text: str) -> None:
        """Handle a normal chat message (LLM interaction) with ReAct loop.

        Follows the original agent pattern:
        1. Stream with tools → collect text in real-time
        2. After stream: if tool calls were made, execute them
        3. Append tool results to messages, then stream again (no tools)
        4. Repeat until no more tool calls (max 5 rounds safety limit)
        """
        history = self._build_context()
        messages = self._llm.build_messages(text, history)
        max_rounds = 8

        for round_idx in range(max_rounds):
            # Check for cancellation request
            if self._cancel_requested:
                if round_idx > 0:
                    self.add_system_message(_("tui.component.chat_pane.operation_cancelled"))
                return
            # Use the pre-detected tool support flag
            has_tools = self._tools_supported

            # Show thinking indicator (only for first round)
            # Subsequent rounds skip this to avoid visual gaps — the tool
            # execution result area already signals the ongoing analysis.
            if round_idx == 0:
                thinking = self.add_system_message(_("tui.component.chat_pane.thinking"))
            else:
                thinking = None

            # Create assistant message placeholder
            assistant = self.add_assistant_text("")

            # Pending tool calls collected during this round
            pending_tools: list[dict[str, Any]] = []

            # ── Callbacks ───────────────────────────────────────

            async def _on_text(chunk: str) -> None:
                if thinking is not None:
                    _remove_thinking()
                assistant.append(chunk)
                self._scroll_to_bottom()

            async def _on_reasoning(chunk: str) -> None:
                """Capture raw reasoning_content for message history."""
                assistant._reasoning += chunk

            async def _on_tool_call(
                name: str,
                args: dict[str, Any],
                tool_content: str = "",
                tool_reasoning: str = "",
            ) -> None:
                if thinking is not None:
                    _remove_thinking()
                # Show the tool call in UI immediately (running state)
                params = ", ".join(f"{k}={v}" for k, v in args.items())
                tool_msg = self.add_tool_call(name, params)
                tool_msg.update_status("running")
                pending_tools.append({
                    "name": name,
                    "args": args,
                    "msg": tool_msg,
                    "content": tool_content,
                    "reasoning": tool_reasoning,
                })

            def _remove_thinking() -> None:
                nonlocal thinking
                if thinking is not None:
                    if thinking in self._messages:
                        self._messages.remove(thinking)
                    try:
                        thinking.remove()
                    except Exception:
                        pass
                    thinking = None

            # ── Stream this round ───────────────────────────────

            try:
                await self._llm.stream_chat(
                    messages=messages,
                    on_text=_on_text,
                    on_tool_call=_on_tool_call if has_tools else None,
                    on_reasoning=_on_reasoning,
                    tools=self._tool_defs if has_tools else None,
                )
            except Exception as exc:
                _remove_thinking()
                assistant.append(_("tui.component.chat_pane.error_format").format(exc=exc))
                self._scroll_to_bottom()
                break

            # ── After stream: execute collected tools ────────────

            if not pending_tools:
                break  # no tools → done

            for tc in pending_tools:
                name, args, tool_msg = tc["name"], tc["args"], tc["msg"]

                tool = self._tool_registry.get(name)
                if tool is None:
                    tool_msg.update_status("error", error=_("tui.component.chat_pane.unknown_tool").format(name=name))
                    continue

                result = await tool.run(args)
                tool_msg.update_status(
                    result.status.value,
                    output=result.output,
                    error=result.error,
                    duration_s=result.duration_s,
                )

                # Append tool call + result to messages for LLM context
                # Include reasoning_content for APIs (e.g. DeepSeek) that require
                # it to be passed back in subsequent requests.
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": tc.get("content") or None,
                    "tool_calls": [{
                        "id": f"call_{id(tool_msg)}",
                        "type": "function",
                        "function": {"name": name, "arguments": json.dumps(args)},
                    }],
                }
                if tc.get("reasoning"):
                    assistant_msg["reasoning_content"] = tc["reasoning"]
                messages.append(assistant_msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": f"call_{id(tool_msg)}",
                    "content": (
                        result.output[:5000]
                        if result.status.value == "done"
                        else result.error
                    ),
                })

                self._scroll_to_bottom()

                # Allow cancellation between tool executions
                if self._cancel_requested:
                    self.add_system_message(_("tui.component.chat_pane.operation_cancelled"))
                    return

            # Continue the loop for the next round (with tool results in messages)
        else:
            # Max rounds reached without breaking
            self.add_system_message(_("tui.component.chat_pane.max_rounds_reached"))

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------

    def _build_context(self) -> list[dict[str, str]]:
        """Build LLM context from message history (user + assistant only)."""
        context: list[dict[str, str]] = []
        for msg in self._messages:
            if isinstance(msg, UserMessage):
                context.append({"role": "user", "content": msg.text})
            elif isinstance(msg, AssistantText):
                entry: dict[str, str] = {
                    "role": "assistant",
                    "content": msg._full_text,
                }
                if msg._reasoning:
                    entry["reasoning_content"] = msg._reasoning
                context.append(entry)
        return context

    def _save_current_history(self) -> None:
        """Save current chat messages to persistent storage."""
        target = self._state.target
        if not target:
            return

        messages: list[ChatMessageData] = []
        for msg in self._messages:
            if isinstance(msg, UserMessage):
                messages.append(ChatMessageData(
                    type="user",
                    content=msg.text,
                ))
            elif isinstance(msg, AssistantText):
                messages.append(ChatMessageData(
                    type="assistant",
                    content=msg._full_text,
                ))

        store = get_history_store()
        store.save(target, messages)

    def _load_history(self, target: str) -> None:
        """Load chat history from persistent storage."""
        store = get_history_store()
        data = store.load(target)
        if not data:
            self.add_system_message(_("tui.component.chat_pane.no_history_for_target").format(target=target))
            return

        self.clear_messages()
        self.add_system_message(_("tui.component.chat_pane.loaded_history").format(target=target, count=len(data)))

        # Replay history messages
        for msg_data in data:
            if msg_data.type == "user":
                self.add_user_message(msg_data.content)
            elif msg_data.type == "assistant":
                self.add_assistant_text(msg_data.content)

    # ------------------------------------------------------------------
    # Configuration apply
    # ------------------------------------------------------------------

    def _apply_sc_config(self, config: dict[str, Any]) -> None:
        """Apply scan configuration from modal result."""
        old_state = self._state.to_dict()

        self._state.update_from_dict(config)

        # Show form operations for each changed value
        for key, new_val in config.items():
            if key == "_execute":
                continue
            old_val = old_state.get(key, "")
            new_str = str(new_val)
            old_str = str(old_val)
            if new_str != old_str:
                self.add_form_operation("Config", key, old_str, new_str)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _focus_input(self) -> None:
        """Focus the input field."""
        try:
            inp = self.query_one("#chat-input", ChatInput)
            inp.focus_input()
        except Exception:
            pass

    def _scroll_to_bottom(self) -> None:
        """Scroll the message area to the bottom."""
        try:
            container = self.query_one("#chat-messages", VerticalScroll)
            container.scroll_end(animate=False)
        except Exception:
            pass

    def on_unmount(self) -> None:
        """Auto-save history when the pane is removed."""
        if self._state.target:
            self._save_current_history()

    # ------------------------------------------------------------------
    # Property access for command handlers
    # ------------------------------------------------------------------

    @property
    def messages(self) -> list:
        """Read-only access to messages (for external use)."""
        return self._messages
