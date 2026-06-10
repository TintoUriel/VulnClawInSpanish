"""Log panel widget with RichLog for streaming output."""

from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static

from vulnclaw.i18n import _


class LogPanel(Static):
    """Panel wrapping a RichLog for streaming LLM output display."""

    DEFAULT_CSS = """
    LogPanel {
        height: 1fr;
        margin: 0 1;
        border: solid $border;
        padding: 0 1;
    }
    """

    content: reactive[str] = reactive("", init=False)

    def __init__(self, title: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._lines: list[str] = []

    def on_mount(self) -> None:
        self._refresh()

    def write(self, text: str) -> None:
        """Append text to the log."""
        self._lines.append(text)
        self.content = "".join(self._lines[-200:])

    def clear(self) -> None:
        """Clear all log content."""
        self._lines.clear()
        self.content = ""
        self._refresh()

    def watch_content(self, value: str) -> None:
        self._refresh()

    def _refresh(self) -> None:
        display = self.content[-5000:] if len(self.content) > 5000 else self.content
        self.update(display or _("tui.widget.log_panel.waiting_output"))
