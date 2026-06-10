"""Chat input widget with slash-command autocomplete.

When the user types ``/`` followed by at least one character,
a completion list is surfaced below the input (managed by the parent).
:bdg-primary:`/` alone shows nothing — only ``/x`` triggers.

Key design decisions:

* **Tab / Shift+Tab** — navigate the completion list highlight.
* **Enter** — sends the current input value; if completions are active
  the parent auto-selects the highlighted item before processing.
* **Escape** — hides the completion list.
"""

from __future__ import annotations

from vulnclaw.i18n import _

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Static


class ChatInput(Horizontal):
    """Bottom input bar with command autocomplete."""

    DEFAULT_CSS = """
    ChatInput {
        height: auto;
        padding: 0 1;
        background: $surface;
        border-top: solid $primary;
    }

    ChatInput > Static {
        width: auto;
        color: $text-accent;
        text-style: bold;
        margin: 0 0 0 0;
        padding: 0 0;
    }

    ChatInput > Input {
        width: 1fr;
        height: 3;
        margin: 0;
        padding: 0 1;
    }
    """

    # ------------------------------------------------------------------
    # Custom messages
    # ------------------------------------------------------------------

    class Submitted(Message):
        """Posted when the user submits a chat message."""

        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    class ShowCompletions(Message):
        """Ask the parent to display the completion list."""

        def __init__(self, matches: list[tuple[str, str]]) -> None:
            super().__init__()
            self.matches = matches

    class HideCompletions(Message):
        """Ask the parent to hide the completion list."""
        pass

    class NavigateCompletions(Message):
        """Ask the parent to move selection in the completion list."""

        def __init__(self, direction: str) -> None:
            super().__init__()
            self.direction = direction  # "up" or "down"

    # ------------------------------------------------------------------
    # Reactive
    # ------------------------------------------------------------------

    completion_active: reactive[bool] = reactive(False)

    # ------------------------------------------------------------------
    # Command catalogue (synced from CommandRegistry via update_commands)
    # ------------------------------------------------------------------

    _commands: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Static(">")
        yield Input(
            placeholder=_("tui.component.chat_input.placeholder"),
            id="chat-input-field",
        )

    @property
    def value(self) -> str:
        inp = self.query_one("#chat-input-field", Input)
        return inp.value

    @value.setter
    def value(self, new_value: str) -> None:
        inp = self.query_one("#chat-input-field", Input)
        inp.value = new_value

    def clear(self) -> None:
        """Clear the input field and hide completions."""
        self.value = ""
        self.post_message(self.HideCompletions())

    def focus_input(self) -> None:
        """Focus the input field."""
        inp = self.query_one("#chat-input-field", Input)
        inp.focus()

    # ------------------------------------------------------------------
    # Sync commands from registry
    # ------------------------------------------------------------------

    def update_commands(self, commands: list[dict[str, str]]) -> None:
        """Replace the command catalogue with entries from CommandRegistry.

        Each entry must have ``name`` and ``description`` keys.
        ``name`` may include a leading ``/`` which is stripped automatically.
        """
        self._commands = {c["name"].lstrip("/"): c["description"] for c in commands}

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show/hide completions based on partial input."""
        text = event.value

        # trigger: "/" + at least one keyword character
        if text.startswith("/") and len(text) > 1:
            prefix = text[1:]
            matches = self._filter_commands(prefix)
            if matches:
                self.post_message(self.ShowCompletions(matches))
                return

        # everything else: hide if currently visible
        if self.completion_active:
            self.post_message(self.HideCompletions())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter — submit current input text."""
        event.stop()
        self._submit(event.value)

    def on_key(self, event) -> None:
        """Intercept navigation and completion keys."""
        if event.key == "escape":
            if self.completion_active:
                event.stop()
                self.post_message(self.HideCompletions())
        elif event.key == "tab":
            if self.completion_active:
                event.stop()
                self.post_message(self.NavigateCompletions("down"))
        elif event.key == "shift+tab":
            if self.completion_active:
                event.stop()
                self.post_message(self.NavigateCompletions("up"))
        elif self.completion_active:
            if event.key == "up":
                event.stop()
                self.post_message(self.NavigateCompletions("up"))
            elif event.key == "down":
                event.stop()
                self.post_message(self.NavigateCompletions("down"))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _filter_commands(self, prefix: str) -> list[tuple[str, str]]:
        """Return ``(name, desc)`` tuples matching *prefix*."""
        prefix_lower = prefix.lower()
        return [
            (k, v)
            for k, v in self._commands.items()
            if k.startswith(prefix_lower) or prefix_lower in v
        ]

    def _submit(self, value: str) -> None:
        """Post :class:`Submitted` and clear."""
        text = value.strip()
        if text:
            self.post_message(self.Submitted(text))
        self.clear()
