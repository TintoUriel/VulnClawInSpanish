"""Natural language input bar at the bottom of the TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Input, Static

from vulnclaw.i18n import _


class InputBar(Horizontal):
    """Bottom input bar with natural language prompt."""

    DEFAULT_CSS = """
    InputBar {
        height: 3;
        background: $panel;
        border-top: solid $primary;
        padding: 0 1;
    }

    InputBar > .input-prefix {
        width: auto;
        content-align: left middle;
        color: $text-disabled;
        padding: 0 1;
        text-style: bold;
    }

    InputBar > Input {
        height: 3;
    }
    """

    class Submitted(Message):
        """Posted when the user submits a natural language command."""

        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    def __init__(self) -> None:
        super().__init__()
        self._input: Input | None = None

    def compose(self) -> ComposeResult:
        yield Static(" > ", classes="input-prefix")
        yield Input(
            placeholder=_("tui.widget.input_bar.placeholder"),
            id="nl-input",
        )

    def on_mount(self) -> None:
        self._input = self.query_one("#nl-input", Input)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.value.strip():
            self.post_message(self.Submitted(event.value.strip()))
            event.input.clear()

    def focus_input(self) -> None:
        """Focus the input bar."""
        if self._input:
            self._input.focus()
