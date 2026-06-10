"""Bash tool — execute shell commands on the host system."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from vulnclaw.cli.textui.tools.base import BaseTool, ToolResult, ToolStatus
from vulnclaw.i18n import _


class BashTool(BaseTool):
    """Execute a shell command and capture its output."""

    name = "bash"
    description = _("tui.tool.bash.description")
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": _("tui.tool.bash.input_desc"),
            },
        },
        "required": ["command"],
    }

    async def run(self, inputs: dict[str, Any]) -> ToolResult:
        command = inputs.get("command", "")
        if not command:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=_("tui.tool.bash.no_command"),
            )

        start = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            duration = time.monotonic() - start

            output = stdout.decode("utf-8", errors="replace")
            if stderr:
                error_out = stderr.decode("utf-8", errors="replace")
                if error_out.strip():
                    output += f"\n[stderr]\n{error_out}"

            if proc.returncode != 0:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output=output[:10000],
                    error=_("tui.tool.bash.exit_code", code=proc.returncode),
                    duration_s=round(duration, 2),
                )

            return ToolResult(
                status=ToolStatus.DONE,
                output=output[:10000],
                duration_s=round(duration, 2),
            )
        except asyncio.TimeoutError:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=_("tui.tool.bash.timeout"),
                duration_s=round(time.monotonic() - start, 2),
            )
        except Exception as exc:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=str(exc),
                duration_s=round(time.monotonic() - start, 2),
            )


# Singleton
bash_tool = BashTool()
