"""MCP diagnostics service for the Web UI backend.

修改者: Nyaecho
修改时间: 2026-07-08
修改原因: V6 修复 — get_mcp_diagnostics 已移至 mcp/diagnostics.py，
         此处重新导出以保持 web 层向后兼容。
"""

from __future__ import annotations

from vulnclaw.mcp.diagnostics import get_mcp_diagnostics  # noqa: F401
from vulnclaw.mcp.schemas import MCPDiagnosticsView, MCPServiceView  # noqa: F401
