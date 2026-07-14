"""Agent-facing traffic tools (in-process builtins).

``traffic_list`` / ``traffic_view`` / ``traffic_repeat`` / ``traffic_sitemap``
read and write the in-sandbox store directly — no MCP round-trip. They return
agent-readable strings (like ``python_execute``), with ``request_id`` surfaced
so the model can chain list → view → repeat and cite a capture in a finding.
"""

from __future__ import annotations

from typing import Any

from vulnclaw.traffic.replay import ReplayError, replay_request
from vulnclaw.traffic.store import TrafficStore

TRAFFIC_TOOL_NAMES = frozenset(
    {"traffic_list", "traffic_view", "traffic_repeat", "traffic_sitemap"}
)

_MAX_BLOB_CHARS = 4000


def traffic_tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "traffic_list",
                "description": (
                    "Lista las solicitudes/respuestas HTTP capturadas durante esta ejecución "
                    "(provenientes de proxy, navegador o repetición manual). "
                    "Se usa para consultar el índice de tráfico, filtrar por método/host/código de estado/origen, "
                    "y obtener el request_id para poder referenciarlo en traffic_view / traffic_repeat."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "description": "Filtrar por método HTTP, p. ej. GET/POST"},
                        "host": {"type": "string", "description": "Filtrar por host, p. ej. app.test"},
                        "status": {"type": "integer", "description": "Filtrar por código de estado de la respuesta, p. ej. 200"},
                        "source": {
                            "type": "string",
                            "description": "Filtrar por origen: proxy/browser/manual-replay",
                        },
                        "limit": {"type": "integer", "description": "Límite de resultados devueltos (por defecto 50)"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "traffic_view",
                "description": (
                    "Consulta el mensaje original de solicitud y respuesta de una petición capturada "
                    "(localizada mediante request_id). Se usa para confirmar evidencia de vulnerabilidades, "
                    "extraer detalles de la respuesta y como evidencia http_capture de un hallazgo."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string", "description": "request_id devuelto por traffic_list"}
                    },
                    "required": ["request_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "traffic_repeat",
                "description": (
                    "Repite una solicitud ya capturada, permitiendo sobrescribir method/url/headers/body; "
                    "se usa para verificar vulnerabilidades, probar modificando parámetros o comparar "
                    "diferencias en la respuesta. El resultado de la repetición se registra en el almacén "
                    "de tráfico con source=manual-replay y devuelve un nuevo request_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string", "description": "request_id original que se va a repetir"},
                        "method": {"type": "string", "description": "Sobrescribir el método HTTP (opcional)"},
                        "url": {"type": "string", "description": "Sobrescribir la URL de la solicitud (opcional)"},
                        "headers": {
                            "type": "object",
                            "description": "Sobrescribir/agregar encabezados de solicitud (un valor null indica eliminar ese encabezado)",
                        },
                        "body": {"type": "string", "description": "Sobrescribir el cuerpo de la solicitud (opcional)"},
                    },
                    "required": ["request_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "traffic_sitemap",
                "description": (
                    "Consulta el mapa del sitio capturado durante esta ejecución: rutas, métodos y "
                    "número de coincidencias agrupados por host. Se usa para comprender rápidamente "
                    "la superficie de ataque del objetivo y los endpoints ya cubiertos."
                ),
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


def traffic_list(
    store: TrafficStore,
    *,
    method: str | None = None,
    host: str | None = None,
    status: int | None = None,
    source: str | None = None,
    limit: int = 50,
) -> str:
    rows = store.entries()
    if method:
        rows = [r for r in rows if str(r.get("method", "")).upper() == method.upper()]
    if host:
        rows = [r for r in rows if host.lower() in str(r.get("host", "")).lower()]
    if status is not None:
        rows = [r for r in rows if int(r.get("status", 0)) == int(status)]
    if source:
        rows = [r for r in rows if str(r.get("source", "")) == source]

    total = len(rows)
    if limit and limit > 0:
        rows = rows[-limit:]
    if not rows:
        return "[traffic] No hay registros de captura coincidentes."

    lines = [f"[traffic] Total de {total} registros de captura (mostrando {len(rows)}):"]
    for r in rows:
        lines.append(
            f"  {r.get('request_id')}  {r.get('method')} {r.get('url')} "
            f"-> {r.get('status')} [{r.get('source')}] {r.get('content_length')}B"
        )
    return "\n".join(lines)


def _truncate(text: str) -> str:
    if len(text) <= _MAX_BLOB_CHARS:
        return text
    return text[:_MAX_BLOB_CHARS] + f"\n... [truncated {len(text) - _MAX_BLOB_CHARS} chars]"


def traffic_view(store: TrafficStore, request_id: str) -> str:
    view = store.view(request_id)
    if view is None:
        return f"[traffic] No se encontró el request_id: {request_id}"
    parts = [
        f"[traffic] {request_id}  {view.get('method')} {view.get('url')} "
        f"-> {view.get('status')} [{view.get('source')}]",
        "── Request ──",
        _truncate(view.get("request_text", "")) or "(vacío)",
    ]
    if view.get("response_text"):
        parts += ["── Response ──", _truncate(view["response_text"])]
    return "\n".join(parts)


def traffic_repeat(
    store: TrafficStore,
    request_id: str,
    overrides: dict[str, Any] | None = None,
    *,
    transport: Any | None = None,
) -> str:
    try:
        record = replay_request(store, request_id, overrides, transport=transport)
    except ReplayError as exc:
        return f"[traffic] Fallo en la repetición: {exc}"
    except Exception as exc:  # network / transport errors
        return f"[traffic] Error al repetir la solicitud: {exc}"
    return (
        f"[traffic] Se repitió {request_id} -> nuevo request_id={record.request_id} "
        f"({record.method} {record.url} -> {record.status}, source=manual-replay)"
    )


def traffic_sitemap(store: TrafficStore) -> str:
    sitemap = store.sitemap()
    if not sitemap:
        return "[traffic] El mapa del sitio está vacío (aún no hay capturas)."
    lines = ["[traffic] Mapa del sitio:"]
    for host, paths in sitemap.items():
        lines.append(f"  {host}")
        for leaf in paths:
            methods = ",".join(leaf["methods"])
            lines.append(f"    [{methods}] {leaf['path']} (x{leaf['count']})")
    return "\n".join(lines)


def dispatch_traffic_tool(
    store: TrafficStore, tool_name: str, args: dict[str, Any]
) -> str:
    """Route a traffic tool call to its handler and return an agent string."""
    if tool_name == "traffic_list":
        status = args.get("status")
        return traffic_list(
            store,
            method=args.get("method"),
            host=args.get("host"),
            status=int(status) if status not in (None, "") else None,
            source=args.get("source"),
            limit=int(args.get("limit", 50) or 50),
        )
    if tool_name == "traffic_view":
        return traffic_view(store, str(args.get("request_id", "")))
    if tool_name == "traffic_repeat":
        overrides: dict[str, Any] = {}
        for key in ("method", "url", "headers", "body"):
            if key in args and args[key] is not None:
                overrides[key] = args[key]
        return traffic_repeat(store, str(args.get("request_id", "")), overrides)
    if tool_name == "traffic_sitemap":
        return traffic_sitemap(store)
    return f"[traffic] Herramienta desconocida: {tool_name}"
