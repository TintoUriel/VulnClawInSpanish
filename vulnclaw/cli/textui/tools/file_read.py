"""File read tool — read file contents from the local filesystem."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from vulnclaw.cli.textui.tools.base import BaseTool, ToolResult, ToolStatus
from vulnclaw.i18n import _


class FileReadTool(BaseTool):
    """Read a file from the local filesystem."""

    name = "read_file"
    description = _("tui.tool.file_read.description")
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": _("tui.tool.file_read.input_desc"),
            },
        },
        "required": ["path"],
    }

    async def run(self, inputs: dict[str, Any]) -> ToolResult:
        path_str = inputs.get("path", "")
        if not path_str:
            return ToolResult(status=ToolStatus.ERROR, error=_("tui.tool.file_read.no_path"))

        start = time.monotonic()
        try:
            file_path = Path(path_str).expanduser().resolve()
            if not file_path.exists():
                return ToolResult(
                    status=ToolStatus.ERROR,
                    error=_("tui.tool.file_read.not_found", path=path_str),
                    duration_s=round(time.monotonic() - start, 2),
                )
            if not file_path.is_file():
                return ToolResult(
                    status=ToolStatus.ERROR,
                    error=_("tui.tool.file_read.not_file", path=path_str),
                    duration_s=round(time.monotonic() - start, 2),
                )

            content = file_path.read_text("utf-8", errors="replace")
            return ToolResult(
                status=ToolStatus.DONE,
                output=content[:10000],
                duration_s=round(time.monotonic() - start, 2),
            )
        except Exception as exc:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=str(exc),
                duration_s=round(time.monotonic() - start, 2),
            )


# Singleton
file_read_tool = FileReadTool()
