"""MCP diagnostics service for the Web UI backend.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de modificación: Corrección V6 — get_mcp_diagnostics se movió a mcp/diagnostics.py;
         aquí se vuelve a exportar para mantener la compatibilidad retroactiva con la capa web.
"""

from __future__ import annotations

from vulnclaw.mcp.diagnostics import get_mcp_diagnostics  # noqa: F401
from vulnclaw.mcp.schemas import MCPDiagnosticsView, MCPServiceView  # noqa: F401
