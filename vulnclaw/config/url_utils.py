"""URL utility functions — shared across infrastructure and domain layers.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: Eliminar la violación V1 — la capa de infraestructura
         mcp/lifecycle.py no debía depender inversamente de la capa de dominio
         agent/builtin_tools.py; se extrajeron las funciones utilitarias puras
         de URL a la capa de infraestructura config/.
"""

from __future__ import annotations

from urllib.parse import urlparse


def infer_port_from_url(url: str) -> int | None:
    """Infer request port from URL.

    Returns the explicit port if present in the URL, otherwise infers
    from the scheme (443 for https, 80 for http), or None if unknown.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if parsed.port:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    if parsed.scheme == "http":
        return 80
    return None
