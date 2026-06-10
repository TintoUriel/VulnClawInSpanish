"""Web fetch tool — retrieve content from HTTP URLs."""

from __future__ import annotations

import time
from typing import Any

import httpx

from vulnclaw.cli.textui.tools.base import BaseTool, ToolResult, ToolStatus
from vulnclaw.i18n import _


class WebFetchTool(BaseTool):
    """Fetch content from a URL via HTTP GET."""

    name = "web_fetch"
    description = _("tui.tool.web_fetch.description")
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": _("tui.tool.web_fetch.input_desc"),
            },
        },
        "required": ["url"],
    }

    async def run(self, inputs: dict[str, Any]) -> ToolResult:
        url = inputs.get("url", "")
        if not url:
            return ToolResult(status=ToolStatus.ERROR, error=_("tui.tool.web_fetch.no_url"))

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "VulnClaw/1.0"})
                duration = time.monotonic() - start

                if resp.status_code >= 400:
                    return ToolResult(
                        status=ToolStatus.ERROR,
                        output=f"HTTP {resp.status_code}",
                        error=_("tui.tool.web_fetch.request_failed", status=resp.status_code, reason=resp.reason_phrase),
                        duration_s=round(duration, 2),
                    )

                return ToolResult(
                    status=ToolStatus.DONE,
                    output=resp.text[:10000],
                    duration_s=round(duration, 2),
                )
        except httpx.TimeoutException:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=_("tui.tool.web_fetch.timeout"),
                duration_s=round(time.monotonic() - start, 2),
            )
        except Exception as exc:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=str(exc),
                duration_s=round(time.monotonic() - start, 2),
            )


# Singleton
web_fetch_tool = WebFetchTool()
