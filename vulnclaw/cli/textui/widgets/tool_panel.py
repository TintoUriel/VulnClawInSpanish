"""Tool call status panel."""

from __future__ import annotations

from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from vulnclaw.i18n import _


class ToolPanel(Static):
    """Panel displaying tool call status in a tree-like table."""

    DEFAULT_CSS = """
    ToolPanel {
        height: 1fr;
        margin: 0 1;
        border: solid $border;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tools: list[dict] = []

    def add_pending(self, tool_info: dict) -> None:
        """Add a pending tool call."""
        self._tools.append({"info": tool_info, "status": "pending", "result": None})
        self._refresh()

    def update_status(self, result: dict) -> None:
        """Update a tool call's status with its result."""
        tool_call_id = result.get("tool_call_id", "")
        for tool in self._tools:
            if tool.get("info", {}).get("id", "") == tool_call_id:
                tool["status"] = "done"
                tool["result"] = result.get("content", "")[:100]
                break
        self._refresh()

    def clear(self) -> None:
        """Clear all tool calls."""
        self._tools.clear()
        self._refresh()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        if not self._tools:
            self.update("[dim]暂无工具调用[/]")
            return

        table = Table.grid(expand=True)
        table.add_column(_("tui.widget.tool_panel.column_tool"), ratio=2)
        table.add_column(_("tui.widget.tool_panel.column_status"), ratio=1)
        table.add_column(_("tui.widget.tool_panel.column_result"), ratio=3)

        for tool in self._tools[-10:]:
            info = tool["info"]
            name = info.get("function", {}).get("name", "unknown")
            status = tool["status"]
            status_style = {
                "pending": "yellow",
                "done": "green",
                "error": "red",
            }.get(status, "white")
            result_text = (
                tool["result"][:80]
                if tool["result"]
                else ("..." if status == "pending" else "")
            )
            table.add_row(
                Text(name, style="bold"),
                Text(status, style=status_style),
                Text(result_text, style="dim"),
            )

        self.update(table)
