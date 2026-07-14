"""MCP diagnostics schemas — shared view models for MCP service state.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: Eliminación de la infracción V6 — la vista de diagnósticos de MCP se
         extrajo de web/schemas.py al paquete mcp/, de modo que tanto la CLI
         como la capa de entrada Web puedan obtener datos de diagnóstico desde la capa de infraestructura.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MCPServiceView(BaseModel):
    """View model for a single MCP service's state."""

    name: str
    enabled: bool
    priority: int
    transport_type: str
    execution_mode: str
    health_status: str
    attach_attempted: bool = False
    attach_succeeded: bool = False
    running: bool
    can_execute: bool
    tool_count: int = 0
    tools: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    last_error_type: Optional[str] = None
    started_at: Optional[str] = None
    description: str = ""
    call_count: int = 0
    success_count: int = 0
    failure_count: int = 0


class MCPDiagnosticsView(BaseModel):
    """View model for aggregated MCP diagnostics."""

    total_services: int = 0
    running_services: int = 0
    local_services: int = 0
    placeholder_services: int = 0
    tool_count: int = 0
    services: list[MCPServiceView] = Field(default_factory=list)
