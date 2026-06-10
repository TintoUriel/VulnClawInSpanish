"""Message type widgets for the chat UI.

Each class renders a different type of chat message:
- UserMessage:  ``> {user text}``
- AssistantText: streamable assistant response (supports Markdown rendering)
- ToolCallMessage: tool execution with dynamic status updates
- FormOperation: diff-style form field change record
- SystemMessage: feedback / notification messages
"""

from __future__ import annotations

from typing import Any

from vulnclaw.i18n import _

from rich.markdown import Markdown
from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import RichLog, Static

from vulnclaw.cli.textui.tools.base import ToolStatus


# ── User message ────────────────────────────────────────────────────


class UserMessage(Static):
    """User input message — displayed as ``> {text}``."""

    DEFAULT_CSS = """
    UserMessage {
        color: $text-accent;
        margin: 1 0 0 0;
    }
    """

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(f"[bold]> {text}[/]", **kwargs)
        self.text = text  # 保存原始文本，供 _build_context 可靠提取


# ── Assistant text ──────────────────────────────────────────────────


class AssistantText(Static):
    """Assistant response text — supports streaming ``append()``.

    When *render_mode* is ``"markdown"``, text is rendered via
    ``rich.markdown.Markdown`` for a richer display.  Partial /
    incomplete Markdown is handled gracefully — if rendering fails,
    the raw (escaped) text is shown as a fallback.

    Parameters
    ----------
    text:
        Initial text content.
    render_mode:
        ``"plain"`` (default, raw text) or ``"markdown"`` (Rich Markdown).
    """

    DEFAULT_CSS = """
    AssistantText {
        color: $text;
        margin: 0 0 1 0;
    }
    """

    def __init__(self, text: str = "", render_mode: str = "plain", **kwargs) -> None:
        super().__init__(text, **kwargs)
        self._full_text = text
        self._reasoning: str = ""
        self._render_mode = render_mode

    def append(self, chunk: str) -> None:
        """Append text chunk for streaming response."""
        self._full_text += chunk
        self._refresh()

    def _refresh(self) -> None:
        """Re-render the current text according to the active render mode."""
        if self._render_mode == "markdown":
            try:
                md = Markdown(self._full_text)
                self.update(md)
                return
            except Exception:
                pass  # fall through to escaped-plain fallback
        self.update(escape(self._full_text))

    def set_render_mode(self, mode: str) -> None:
        """Change render mode and refresh the display immediately."""
        self._render_mode = mode
        self._refresh()


# ── Clickable toggle ────────────────────────────────────────────────


class _ToggleStatic(Static):
    """A clickable Static used as an expand/collapse toggle.

    Textual's event system dispatches ``on_click`` via class method lookup,
    so we must subclass rather than assign a lambda to an instance attribute.
    """

    def __init__(self, text: str, on_toggle=None) -> None:
        super().__init__(text)
        self._on_toggle = on_toggle

    def on_click(self) -> None:
        if self._on_toggle:
            self._on_toggle()


# ── Tool call message ───────────────────────────────────────────────


class ToolCallMessage(Vertical):
    """Tool call with dynamic status/stat update and collapsible output.

    Layout::

        • ToolName(params...)
          ✓ Done  (0.3s)
          ▶ Show output              ← collapsed by default
    """

    DEFAULT_CSS = """
    ToolCallMessage {
        height: auto;
        margin: 0 0 1 0;
    }

    ToolCallMessage > Static {
        margin: 0 0 0 0;
    }

    ToolCallMessage > RichLog {
        height: auto;
        max-height: 20;
        margin: 0 0 0 1;
        border: none;
    }
    """

    def __init__(self, name: str, params: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._params = params
        self._status_widget: Static | None = None
        self._stats_widget: Static | None = None
        self._output_toggle: Static | None = None
        self._output_widget: RichLog | None = None
        self._expanded: bool = False

    def compose(self) -> ComposeResult:
        yield Static(f"[bold blue]• {self._name}[/][dim]({self._params})[/]", id="tool-header")
        self._status_widget = Static("[yellow]Running...[/]", id="tool-status")
        yield self._status_widget

    def _toggle_output(self) -> None:
        """Toggle tool output visibility."""
        if self._output_widget is None:
            return
        self._expanded = not self._expanded
        self._output_widget.display = self._expanded
        if self._output_toggle:
            icon = "▼" if self._expanded else "▶"
            label = "Hide" if self._expanded else "Show"
            self._output_toggle.update(f"{icon} [dim]{label} output[/]")

    def update_status(
        self,
        status: str,
        output: str = "",
        error: str = "",
        duration_s: float = 0.0,
    ) -> None:
        """Update the tool's status and optionally add collapsible output."""
        if self._status_widget is None:
            return

        if status == ToolStatus.DONE.value:
            self._status_widget.update("[green]✓ Done[/]")
        elif status == ToolStatus.ERROR.value:
            msg = f"[red]✗ Failed[/]"
            if error:
                msg += f"\n[red]{error[:200]}[/]"
            self._status_widget.update(msg)
        elif status == ToolStatus.WAITING.value:
            self._status_widget.update("[dim]Waiting...[/]")
        else:
            self._status_widget.update("[yellow]Running...[/]")

        # Show stats for completed calls
        if duration_s > 0:
            stats = f"[dim]({duration_s:.1f}s)[/]"
            if self._stats_widget is None:
                self._stats_widget = Static(stats)
                self.mount(self._stats_widget)
            else:
                self._stats_widget.update(stats)

        # Collapsible output — hidden by default to keep layout compact
        if output:
            # Toggle line (clickable — uses _ToggleStatic for proper event routing)
            self._output_toggle = _ToggleStatic(
                "▶ [dim]Show output[/]", on_toggle=self._toggle_output
            )
            self.mount(self._output_toggle)

            # RichLog output (hidden initially)
            log = RichLog(highlight=True, markup=True)
            log.write(output[:500])
            log.display = False  # collapsed by default
            self._output_widget = log
            self.mount(log)


# ── Form operation ──────────────────────────────────────────────────


class FormOperation(Vertical):
    """Form field change record — shows before → after diff."""

    DEFAULT_CSS = """
    FormOperation {
        height: auto;
        margin: 0 0 1 0;
    }
    """

    def __init__(self, form_type: str, field: str, old_value: str, new_value: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._form_type = form_type
        self._field = field
        self._old_value = old_value
        self._new_value = new_value

    def compose(self) -> ComposeResult:
        yield Static(f"[bold blue]• {self._form_type}[/][dim]({self._field})[/]")
        yield Static(f"  [dim]{_('tui.component.message_widgets.old_value')}:[/] {self._old_value}")
        yield Static(f"  [dim]{_('tui.component.message_widgets.new_value')}:[/] {self._new_value}")
        yield Static(_("tui.component.message_widgets.updated"))


# ── System message ──────────────────────────────────────────────────


class SystemMessage(Static):
    """System feedback — configuration updates, notifications, errors."""

    DEFAULT_CSS = """
    SystemMessage {
        color: $success;
        margin: 0 0 1 0;
    }
    """

    def __init__(self, content: str, **kwargs) -> None:
        super().__init__(content, **kwargs)
