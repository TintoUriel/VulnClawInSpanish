"""VulnClaw MCP Router — route natural language intents to MCP tool calls."""

from __future__ import annotations

import re
from typing import Any, Optional

# ── Intent → Tool mapping ───────────────────────────────────────────

INTENT_TOOL_MAP: dict[str, list[dict[str, Any]]] = {
    # Browser automation
    "abrir página|acceder a url|visitar página|navigate": [
        {"tool": "new_page", "server": "chrome-devtools"},
        {"tool": "navigate", "server": "chrome-devtools"},
    ],
    "captura de pantalla|screenshot|capturar pantalla": [
        {"tool": "screenshot", "server": "chrome-devtools"},
    ],
    "ejecutar js|eval js|ejecutar javascript": [
        {"tool": "evaluate_js", "server": "chrome-devtools"},
    ],
    # HTTP requests
    "enviar solicitud|solicitud http|fetch|acceder a la api|llamar api": [
        {"tool": "fetch", "server": "fetch"},
        {"tool": "send_http1_request", "server": "burp"},
    ],
    # Burp Suite
    "capturar tráfico|ver solicitudes|interceptar solicitud|proxy": [
        {"tool": "get_proxy_http_history", "server": "burp"},
    ],
    "modificar paquete|repetir|replay|manipular": [
        {"tool": "send_http1_request", "server": "burp"},
    ],
    # Memory
    "recordar|guardar|save memory": [
        {"tool": "save", "server": "memory"},
    ],
    "recuperar|consultar historial|retrieve memory": [
        {"tool": "retrieve", "server": "memory"},
    ],
}


class MCPRouter:
    """Routes natural language intents to MCP tool calls."""

    def route(self, user_input: str) -> list[dict[str, Any]]:
        """Analyze user input and return suggested tool calls.

        Returns a list of dicts with keys: tool, server, confidence.
        """
        input_lower = user_input.lower()
        results = []

        for pattern, tools in INTENT_TOOL_MAP.items():
            keywords = pattern.split("|")
            if any(kw in input_lower for kw in keywords):
                for tool_entry in tools:
                    results.append(
                        {
                            "tool": tool_entry["tool"],
                            "server": tool_entry["server"],
                            "confidence": 0.8,
                        }
                    )

        return results

    def extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text."""
        url_match = re.search(r"(https?://\S+)", text)
        return url_match.group(1) if url_match else None

    def extract_ip(self, text: str) -> Optional[str]:
        """Extract IP address from text."""
        ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text)
        return ip_match.group(1) if ip_match else None

    def suggest_tools_for_phase(self, phase: str) -> list[dict[str, Any]]:
        """Suggest tools based on pentest phase."""
        phase_tools = {
            "Reconocimiento": [
                {"tool": "fetch", "server": "fetch", "reason": "Solicitud HTTP para sondear el objetivo"},
                {"tool": "new_page", "server": "chrome-devtools", "reason": "Acceso al objetivo mediante navegador"},
                {"tool": "screenshot", "server": "chrome-devtools", "reason": "Captura de pantalla para registrar la página objetivo"},
            ],
            "Descubrimiento de vulnerabilidades": [
                {"tool": "fetch", "server": "fetch", "reason": "Enviar solicitud de sondeo de vulnerabilidades"},
                {"tool": "send_http1_request", "server": "burp", "reason": "Construir solicitud de detección a través del proxy"},
            ],
            "Explotación": [
                {"tool": "send_http1_request", "server": "burp", "reason": "Construir solicitud de explotación"},
                {"tool": "fetch", "server": "fetch", "reason": "Enviar payload de explotación"},
                {"tool": "evaluate_js", "server": "chrome-devtools", "reason": "Explotación dentro del navegador"},
            ],
        }

        return phase_tools.get(phase, [])
