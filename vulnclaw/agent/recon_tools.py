"""Information-gathering tools: space-mapping, subdomain/JS/dir enumeration.

These are built-in agent tools (wired in builtin_tools.py) that give the agent
real reconnaissance capability instead of guessing:

- space_search      Cartografía de ciberespacio unificada (FOFA / Hunter / Quake / Shodan / ZoomEye / 0.zone)
- subdomain_enum    Enumeración de subdominios (agregación pasiva de cartografía + fuerza bruta DNS opcional con diccionario pequeño)
- js_recon          Reconocimiento de información en JS (basado en URLFinder: extrae endpoints/dominios/claves de los JS)
- dir_enum          Enumeración de directorios (basado en dirsearch: fuerza bruta concurrente con diccionario + línea base 404/detección de simulación)

Principios de diseño: prioridad a lo pasivo, cumplimiento estricto de las restricciones de host/path/port,
todas las llamadas externas con timeout y límite de concurrencia, nunca codificar ninguna API key en el
código fuente (se lee desde config.recon o variables de entorno).
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
import socket
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext

from urllib.parse import urljoin, urlparse

from vulnclaw.agent.builtin_tools import enforce_host_path_constraints

# ── Diccionario de directorios incorporado (versión compacta; config.recon.dir_wordlist_path puede reemplazarlo por un diccionario más grande) ────────
_BUILTIN_DIR_WORDLIST: tuple[str, ...] = (
    # Panel de administración / gestión
    "admin", "admin/login", "administrator", "manage", "manager", "backend", "system",
    "console", "ht", "qd", "dashboard", "admin.php", "admin.jsp", "admin.do", "login",
    "login.jsp", "login.php", "login.action", "signin", "auth", "sso", "cas",
    # API / documentación
    "api", "api/v1", "api/v2", "v1", "v2", "graphql", "swagger", "swagger-ui.html",
    "swagger/index.html", "v2/api-docs", "openapi.json", "api-docs", "actuator",
    "actuator/env", "actuator/health", "druid", "druid/index.html",
    # Configuración / depuración / filtración de información
    "config", "config.json", "config.php", "configuration", "env", ".env", ".git/config",
    ".git/HEAD", ".svn/entries", ".DS_Store", "debug", "test", "demo", "info", "info.php",
    "phpinfo.php", "status", "health", "metrics", "monitor", "console", "server-status",
    "robots.txt", "sitemap.xml", "crossdomain.xml", "web.config", "WEB-INF/web.xml",
    # Respaldo / temporal
    "backup", "backup.zip", "backup.tar.gz", "bak", "old", "www.zip", "web.zip",
    "site.zip", "data.zip", "db.sql", "database.sql", "dump.sql", "test.txt", "1.txt",
    # Carga / archivos
    "upload", "uploads", "files", "file", "download", "static", "assets", "public",
    "tmp", "temp", "images", "img", "data", "doc", "docs",
    # Comunes de negocio (mezcla de chino/inglés/pinyin)
    "user", "users", "member", "hy", "order", "dd", "pay", "payment", "list", "index",
    "home", "main", "portal", "wx", "mp", "xcx", "miniprogram", "h5", "mobile",
)

# ── Expresiones regulares de extracción de endpoints (basado en URLFinder) ──────────────────────────────────────────────
_URL_RE = re.compile(r"""https?://[a-zA-Z0-9.\-]+(?::\d+)?(?:/[^\s"'`<>()\\{}|^]*)?""")
# Extracción amplia de rutas: cualquier ruta entre comillas que empiece por / y tenga 2+ segmentos (basado en la estrategia de coincidencia amplia de URLFinder)
_PATH_RE = re.compile(
    r"""(?P<q>["'`])(?P<v>/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-./?=&%]*)(?P=q)""",
    re.IGNORECASE,
)
# Extracción de fragmentos cortos: cadenas entre comillas que no empiezan con / pero parecen endpoints REST (como "User/list")
# Después del verbo se permiten variantes de framework como ForXxx / All / ById (listForLayUI, getAllByType...)
_FRAG_RE = re.compile(
    r"""(?P<q>["'`])(?P<v>[A-Za-z][A-Za-z0-9_]*/(?:list|save|get|add|edit|delete|update|"""
    r"""detail|query|search|info|check|export|import|download|upload|count|page|batch|"""
    r"""remove|create|modify|status|enable|disable|reset|send|verify|login|logout|"""
    r"""register|authorize|token|refresh|config|setting|menu|role|permission|tree|"""
    r"""all|find|select|insert|submit|audit|approve|reject|publish|cancel|close|open|"""
    r"""start|stop|run|execute|invoke|call|notify|push|pull|sync|async)"""
    r"""(?:[A-Z][a-zA-Z0-9]*)*"""
    r"""[a-zA-Z0-9_\-./?=&%]*)(?P=q)""",
    re.IGNORECASE,
)
# Extracción de base path REST: como "/jalis/rest", "/smweb/rest", "/api/v1"
_BASE_PATH_RE = re.compile(
    r"""(?P<q>["'`])(?P<v>/[a-zA-Z0-9_\-]+/(?:rest|api(?:/v\d+)?))(?P=q)""",
    re.IGNORECASE,
)
_SCRIPT_SRC_RE = re.compile(r"""<script[^>]+src=["']?([^"'\s>]+)""", re.IGNORECASE)

# Plantilla de verbos CRUD — se combina con el base path y los nombres de entidad que aparecen en el JS
_CRUD_VERBS = ("list", "get", "save", "add", "delete", "update", "detail", "query",
               "info", "export", "tree", "page", "count", "all", "search")
# Extracción dinámica de nombres de entidad: busca en el JS todos los identificadores PascalCase (mayúscula inicial, 2+ letras),
# en lugar de una lista de entidades codificada — así se captura cualquier entidad de negocio
_PASCAL_CASE_RE = re.compile(
    r"""(?P<q>["'`])(?P<v>[A-Z][a-zA-Z0-9]{1,30}(?:[A-Z][a-zA-Z0-9]*)*)(?P=q)"""
)

# Huellas de información sensible / filtración de credenciales
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws_ak", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("google_api", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PRIVATE) ?(?:PRIVATE )?KEY-----")),
    ("generic_key", re.compile(
        r"""(?i)(?:api[_-]?key|access[_-]?key|secret[_-]?key|app[_-]?secret|token|password|passwd)"""
        r"""["'`]?\s*[:=]\s*["'`]([A-Za-z0-9_\-]{12,64})["'`]"""
    )),
    ("aliyun_ak", re.compile(r"LTAI[0-9A-Za-z]{12,24}")),
)


def _get_recon_cfg(agent: AgentContext) -> Any:
    from vulnclaw.config.schema import ReconConfig

    cfg = getattr(getattr(agent, "config", None), "recon", None)
    return cfg if cfg is not None else ReconConfig()


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _host_of(url_or_host: str) -> str:
    if "://" in url_or_host:
        return (urlparse(url_or_host).hostname or "").lower()
    return url_or_host.split("/")[0].split(":")[0].lower()


def _dedup_cap(items: list[str], cap: int) -> list[str]:
    return list(dict.fromkeys(i for i in items if i))[:cap]


# ── Motores de cartografía de ciberespacio ───────────────────────────────────────────────────────────────


async def _engine_fofa(client: Any, query: str, size: int, cfg: Any) -> tuple[list[dict], str]:
    if not (cfg.fofa_email and cfg.fofa_key):
        return [], "fofa: fofa_email/fofa_key no configurados"
    fields = "host,ip,port,title,domain,server,protocol"
    params = {
        "email": cfg.fofa_email,
        "key": cfg.fofa_key,
        "qbase64": _b64(query),
        "fields": fields,
        "size": str(min(size, 10000)),
    }
    r = await client.get("https://fofa.info/api/v1/search/all", params=params)
    data = r.json()
    if data.get("error"):
        return [], f"fofa: {data.get('errmsg', 'error')}"
    recs = []
    for row in data.get("results", []) or []:
        row = (list(row) + [""] * 7)[:7]
        recs.append({
            "host": row[0], "ip": row[1], "port": row[2], "title": row[3],
            "domain": row[4], "server": row[5], "url": row[0],
        })
    return recs, f"fofa: {data.get('size', len(recs))} resultados"


async def _engine_hunter(client: Any, query: str, size: int, cfg: Any) -> tuple[list[dict], str]:
    if not cfg.hunter_key:
        return [], "hunter: hunter_key no configurado"
    end = datetime.now()
    start = end - timedelta(days=365)
    params = {
        "api-key": cfg.hunter_key,
        "search": _b64(query),
        "page": "1",
        # Hunter solo acepta page_size en [10,100]; un valor demasiado pequeño genera el error "tamaño de página no válido"
        "page_size": str(min(max(size, 10), 100)),
        "is_web": "3",
        "start_time": start.strftime("%Y-%m-%d"),
        "end_time": end.strftime("%Y-%m-%d"),
    }
    r = await client.get("https://hunter.qianxin.com/openApi/search", params=params)
    data = r.json()
    if data.get("code") != 200:
        return [], f"hunter: {data.get('message', data.get('code'))}"
    arr = (data.get("data") or {}).get("arr") or []
    recs = []
    for it in arr:
        recs.append({
            "host": it.get("url") or it.get("domain", ""), "ip": it.get("ip", ""),
            "port": it.get("port", ""), "title": it.get("web_title", ""),
            "domain": it.get("domain", ""), "server": it.get("component", ""),
            "url": it.get("url", ""),
        })
    return recs, f"hunter: {(data.get('data') or {}).get('total', len(recs))} resultados"


async def _engine_quake(client: Any, query: str, size: int, cfg: Any) -> tuple[list[dict], str]:
    if not cfg.quake_key:
        return [], "quake: quake_key no configurado"
    body = {"query": query, "start": 0, "size": min(size, 100), "ignore_cache": True}
    r = await client.post(
        "https://quake.360.net/api/v3/search/quake_service",
        headers={"X-QuakeToken": cfg.quake_key, "Content-Type": "application/json"},
        content=json.dumps(body),
    )
    data = r.json()
    if data.get("code") not in (0, "0"):
        return [], f"quake: {data.get('message', data.get('code'))}"
    recs = []
    for it in data.get("data", []) or []:
        svc = it.get("service", {}) or {}
        http = svc.get("http", {}) or {}
        recs.append({
            "host": http.get("host") or it.get("ip", ""), "ip": it.get("ip", ""),
            "port": it.get("port", ""), "title": http.get("title", ""),
            "domain": it.get("domain", ""), "server": svc.get("name", ""),
            "url": http.get("host", ""),
        })
    return recs, f"quake: {(data.get('meta') or {}).get('pagination', {}).get('total', len(recs))} resultados"


async def _engine_shodan(client: Any, query: str, size: int, cfg: Any) -> tuple[list[dict], str]:
    if not cfg.shodan_key:
        return [], "shodan: shodan_key no configurado"
    r = await client.get(
        "https://api.shodan.io/shodan/host/search",
        params={"key": cfg.shodan_key, "query": query},
    )
    data = r.json()
    if "matches" not in data:
        return [], f"shodan: {data.get('error', 'no matches')}"
    recs = []
    for it in data.get("matches", []):
        hostnames = it.get("hostnames") or []
        recs.append({
            "host": (hostnames[0] if hostnames else it.get("ip_str", "")),
            "ip": it.get("ip_str", ""), "port": it.get("port", ""),
            "title": (it.get("http", {}) or {}).get("title", ""),
            "domain": ",".join(it.get("domains") or []),
            "server": it.get("product", ""), "url": (hostnames[0] if hostnames else ""),
        })
    return recs, f"shodan: {data.get('total', len(recs))} resultados"


async def _engine_zoomeye(client: Any, query: str, size: int, cfg: Any) -> tuple[list[dict], str]:
    if not cfg.zoomeye_key:
        return [], "zoomeye: zoomeye_key no configurado"
    body = {"qbase64": _b64(query), "page": 1, "pagesize": min(size, 100)}
    r = await client.post(
        "https://api.zoomeye.org/v2/search",
        headers={"API-KEY": cfg.zoomeye_key, "Content-Type": "application/json"},
        content=json.dumps(body),
    )
    data = r.json()
    if data.get("code") not in (60000, 0, None) and "data" not in data:
        return [], f"zoomeye: {data.get('message', data.get('code'))}"
    recs = []
    for it in data.get("data", []) or []:
        recs.append({
            "host": it.get("url") or it.get("domain") or it.get("ip", ""),
            "ip": it.get("ip", ""), "port": it.get("port", ""),
            "title": it.get("title", ""), "domain": it.get("domain", ""),
            "server": it.get("product", ""), "url": it.get("url", ""),
        })
    return recs, f"zoomeye: {data.get('total', len(recs))} resultados"


async def _engine_zerozone(client: Any, query: str, size: int, cfg: Any) -> tuple[list[dict], str]:
    if not cfg.zerozone_key:
        return [], "zerozone: zerozone_key no configurado"
    body = {
        "title": query, "query_type": "site", "page": 1,
        "pagesize": min(size, 100), "zone_key_id": cfg.zerozone_key,
    }
    r = await client.post(
        "https://0.zone/api/data/",
        headers={"Content-Type": "application/json"},
        content=json.dumps(body),
    )
    data = r.json()
    items = data.get("data") if isinstance(data.get("data"), list) else []
    if not items and data.get("code") not in (0, 200, None):
        return [], f"zerozone: {data.get('message', data.get('code'))}"
    recs = []
    for it in items:
        recs.append({
            "host": it.get("url") or it.get("domain", ""), "ip": it.get("ip", ""),
            "port": it.get("port", ""), "title": it.get("title", ""),
            "domain": it.get("domain", ""), "server": it.get("server", ""),
            "url": it.get("url", ""),
        })
    return recs, f"zerozone: {data.get('total', len(recs))} resultados"


_ENGINES = {
    "fofa": _engine_fofa, "hunter": _engine_hunter, "quake": _engine_quake,
    "shodan": _engine_shodan, "zoomeye": _engine_zoomeye, "zerozone": _engine_zerozone,
}

# Sintaxis de consulta por defecto de cada motor cuando solo se da domain
_DOMAIN_QUERY = {
    "fofa": 'domain="{d}"', "hunter": 'domain="{d}"', "quake": 'domain:"{d}"',
    "shodan": "hostname:{d}", "zoomeye": 'hostname:"{d}"', "zerozone": "{d}",
}


def _make_client(cfg: Any):
    import httpx

    return httpx.AsyncClient(verify=False, timeout=cfg.http_timeout, follow_redirects=True)


async def execute_space_search(agent: AgentContext, args: dict[str, Any]) -> str:
    """Consulta unificada de cartografía de ciberespacio. engine ∈ {fofa,hunter,quake,shodan,zoomeye,zerozone,all}."""
    cfg = _get_recon_cfg(agent)
    engine = str(args.get("engine", "fofa") or "fofa").strip().lower()
    query = str(args.get("query", "") or "").strip()
    domain = str(args.get("domain", "") or "").strip()
    size = int(args.get("size", cfg.space_size) or cfg.space_size)

    if not query and not domain:
        return "[!] space_search requiere el parámetro query o domain"

    engines = list(_ENGINES) if engine == "all" else [engine]
    invalid = [e for e in engines if e not in _ENGINES]
    if invalid:
        return f"[!] engine no soportado: {', '.join(invalid)}; opciones: {', '.join(_ENGINES)}, all"

    out: list[str] = [f"# Cartografía de ciberespacio — {'/'.join(engines)}  query={query or domain}"]
    try:
        async with _make_client(cfg) as client:
            async def run(eng: str) -> tuple[str, list[dict], str]:
                q = query or _DOMAIN_QUERY[eng].format(d=domain)
                try:
                    recs, note = await _ENGINES[eng](client, q, size, cfg)
                    return eng, recs, note
                except Exception as e:  # Un fallo en un motor no afecta a los demás
                    return eng, [], f"{eng}: excepción en la solicitud {e}"

            results = await asyncio.gather(*(run(e) for e in engines))
    except Exception as e:
        return f"[!] Error de ejecución en space_search: {e}"

    for eng, recs, note in results:
        out.append(f"\n## {note}")
        for rec in recs[:size]:
            line = f"  {rec.get('ip',''):<16}:{str(rec.get('port','')):<6} {rec.get('host','')}"
            extra = " | ".join(x for x in (rec.get("title", ""), rec.get("server", "")) if x)
            out.append(line + (f"  [{extra}]" if extra else ""))
        if not recs:
            out.append("  (sin resultados o key no configurada)")
    return "\n".join(out)


# ── Enumeración de subdominios ─────────────────────────────────────────────────────────────────

_SUBDOMAIN_BRUTE = (
    "www", "api", "app", "m", "mail", "admin", "test", "dev", "stage", "uat", "pre",
    "static", "cdn", "img", "static1", "oa", "vpn", "sso", "cas", "auth", "portal",
    "gateway", "gw", "open", "service", "wx", "mp", "h5", "pay", "passport", "id",
    "data", "db", "file", "files", "upload", "download", "docs", "wiki", "git", "svn",
    "jenkins", "ci", "monitor", "grafana", "kibana", "es", "redis", "mysql", "nacos",
)


async def execute_subdomain_enum(agent: AgentContext, args: dict[str, Any]) -> str:
    """Enumeración de subdominios: agregación pasiva de cartografía + fuerza bruta DNS opcional con diccionario pequeño."""
    cfg = _get_recon_cfg(agent)
    domain = str(args.get("domain", "") or "").strip().lower()
    if not domain:
        return "[!] subdomain_enum requiere el parámetro domain"
    if "://" in domain:
        domain = _host_of(domain)

    do_brute = bool(args.get("brute", True))
    found: set[str] = set()
    notes: list[str] = []

    # 1) Pasivo: agregación desde los distintos motores de cartografía de ciberespacio
    engines = [e for e in _ENGINES if getattr(cfg, _key_field(e))]
    if engines:
        try:
            async with _make_client(cfg) as client:
                async def run(eng: str):
                    q = _DOMAIN_QUERY[eng].format(d=domain)
                    try:
                        recs, note = await _ENGINES[eng](client, q, cfg.space_size, cfg)
                        notes.append(note)
                        for rec in recs:
                            for f in (rec.get("domain", ""), _host_of(rec.get("host", ""))):
                                if f and f.endswith(domain):
                                    found.add(f.lstrip("*.").lower())
                    except Exception as e:
                        notes.append(f"{eng}: excepción {e}")
                await asyncio.gather(*(run(e) for e in engines))
        except Exception as e:
            notes.append(f"Excepción en la agregación pasiva: {e}")
    else:
        notes.append("No hay ninguna key de cartografía de ciberespacio configurada, se omite la agregación pasiva")

    # 2) Activo: fuerza bruta de resolución DNS con diccionario pequeño
    if do_brute:
        sem = asyncio.Semaphore(cfg.max_concurrency)
        loop = asyncio.get_running_loop()

        async def resolve(sub: str) -> None:
            host = f"{sub}.{domain}"
            async with sem:
                try:
                    await asyncio.wait_for(
                        loop.run_in_executor(None, socket.gethostbyname, host), timeout=5
                    )
                    found.add(host)
                except Exception:
                    pass

        await asyncio.gather(*(resolve(s) for s in _SUBDOMAIN_BRUTE))
        notes.append(f"Diccionario de fuerza bruta DNS: {len(_SUBDOMAIN_BRUTE)} entradas")

    subs = sorted(found)
    head = [f"# Enumeración de subdominios — {domain}  total {len(subs)}", "  " + "; ".join(notes)]
    return "\n".join(head + [f"  {s}" for s in subs]) if subs else "\n".join(head + ["  (no se encontraron subdominios)"])


def _key_field(engine: str) -> str:
    return {
        "fofa": "fofa_key", "hunter": "hunter_key", "quake": "quake_key",
        "shodan": "shodan_key", "zoomeye": "zoomeye_key", "zerozone": "zerozone_key",
    }[engine]


# ── Reconocimiento de información en JS (basado en URLFinder) ──────────────────────────────────────────────


def extract_from_js(content: str, base_host: str = "") -> dict[str, list[str]]:
    """Extrae urls / paths / domains / secrets del texto HTML/JS (función pura, facilita las pruebas).

    Mejoras clave (basado en URLFinder):
    1. Coincidencia amplia de rutas — se extrae cualquier /xxx/yyy entre comillas, sin limitarse a una lista de palabras clave
    2. Extracción de fragmentos cortos — también se capturan fragmentos CRUD que no empiezan con / como "User/list"
    3. Inferencia por combinación de base path + nombre de entidad + verbo CRUD — incluso si en el JS solo aparecen "/jalis/rest"
       y "User", se puede inferir automáticamente el endpoint implícito /jalis/rest/User/list, entre otros
    """
    urls = _URL_RE.findall(content)
    paths = [m.group("v") for m in _PATH_RE.finditer(content)]

    # Fragmentos cortos (como "User/list")
    frags = [m.group("v") for m in _FRAG_RE.finditer(content)]

    # Extracción de base path (como "/jalis/rest", "/smweb/rest")
    bases = list(dict.fromkeys(m.group("v").rstrip("/") for m in _BASE_PATH_RE.finditer(content)))

    # Extracción dinámica de nombres de entidad: busca en el JS todos los identificadores PascalCase (excluyendo ruido de palabras clave/nombres de clase comunes de JS)
    _JS_NOISE = frozenset({
        "Object", "Array", "String", "Number", "Boolean", "Function", "Date", "Error",
        "Math", "JSON", "Promise", "RegExp", "Map", "Set", "Symbol", "Proxy", "Reflect",
        "Infinity", "NaN", "Null", "True", "False", "Undefined", "Arguments", "This",
        "Window", "Document", "Element", "Node", "Event", "Console", "Navigator",
        "History", "Location", "Storage", "XMLHttpRequest", "FormData", "Headers",
        "Request", "Response", "Blob", "File", "FileReader", "FileList", "Image",
        "Canvas", "Context", "Worker", "WebSocket", "AbortController", "AbortSignal",
        "TypeError", "RangeError", "SyntaxError", "ReferenceError", "URIError",
        "EvalError", "InternalError", "AggregateError", "WeakMap", "WeakSet",
        "ArrayBuffer", "DataView", "Float32Array", "Float64Array", "Int8Array",
        "Int16Array", "Int32Array", "Uint8Array", "Uint16Array", "Uint32Array",
        "Intl", "Atomics", "SharedArrayBuffer", "Generator", "AsyncFunction",
        "Iterator", "AsyncIterator", "BigInt", "FinalizationRegistry",
        "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
        "Content", "Accept", "Authorization", "Cache", "Origin", "Referer",
        "Script", "Link", "Style", "Div", "Span", "Input", "Button", "Form",
        "Table", "Html", "Body", "Head", "Meta", "Title", "Base", "Href",
    })
    entities = list(dict.fromkeys(
        m.group("v") for m in _PASCAL_CASE_RE.finditer(content)
        if m.group("v") not in _JS_NOISE and len(m.group("v")) <= 30
    ))

    # Inferencia base + entity + CRUD
    inferred: list[str] = []
    if bases and entities:
        for base in bases[:5]:
            for entity in entities[:30]:
                for verb in _CRUD_VERBS:
                    inferred.append(f"{base}/{entity}/{verb}")
    # Concatenación de base + fragmento corto
    for base in bases[:5]:
        for frag in frags:
            if not frag.startswith("/"):
                inferred.append(f"{base}/{frag}")

    all_paths = paths + [f"/{f}" if not f.startswith("/") else f for f in frags] + inferred

    domains = sorted({_host_of(u) for u in urls if _host_of(u)})
    if base_host:
        base_root = ".".join(base_host.split(".")[-2:])
        domains = [d for d in domains if base_root in d] + [d for d in domains if base_root not in d]
    secrets: list[str] = []
    for label, pat in _SECRET_PATTERNS:
        for m in pat.finditer(content):
            secrets.append(f"{label}: {m.group(0)[:80]}")
    return {
        "urls": _dedup_cap(urls, 200),
        "paths": _dedup_cap(all_paths, 500),
        "domains": _dedup_cap(domains, 100),
        "secrets": _dedup_cap(secrets, 50),
    }


async def execute_js_recon(agent: AgentContext, args: dict[str, Any]) -> str:
    """Rastrea la página objetivo y los archivos JS que referencia, extrayendo endpoints / dominios / claves."""
    cfg = _get_recon_cfg(agent)
    url = str(args.get("url", "") or "").strip()
    if not url:
        return "[!] js_recon requiere el parámetro url"
    if "://" not in url:
        url = "http://" + url
    host = _host_of(url)

    violation = enforce_host_path_constraints(agent, host=host, target=host)
    if violation:
        return violation

    max_js = int(args.get("max_js", cfg.js_max_files) or cfg.js_max_files)
    agg = {"urls": [], "paths": [], "domains": [], "secrets": []}
    fetched = 0
    try:
        async with _make_client(cfg) as client:
            resp = await client.get(url)
            html = resp.text
            for k, v in extract_from_js(html, host).items():
                agg[k].extend(v)

            # Recopila <script src> y los completa como URL absolutas
            js_urls = []
            for src in _SCRIPT_SRC_RE.findall(html):
                full = urljoin(url, src)
                if full.lower().split("?")[0].endswith(".js"):
                    js_urls.append(full)
            js_urls = _dedup_cap(js_urls, max_js)

            sem = asyncio.Semaphore(cfg.max_concurrency)

            async def grab(js_url: str) -> None:
                nonlocal fetched
                async with sem:
                    try:
                        jr = await client.get(js_url)
                        fetched += 1
                        for k, v in extract_from_js(jr.text, host).items():
                            agg[k].extend(v)
                    except Exception:
                        pass

            await asyncio.gather(*(grab(j) for j in js_urls))
    except Exception as e:
        return f"[!] Error de ejecución en js_recon: {e}"

    for k in agg:
        agg[k] = _dedup_cap(agg[k], 200 if k != "secrets" else 50)

    out = [f"# Reconocimiento de información en JS — {url}  (se rastrearon {fetched} archivos JS)"]

    # Los hallazgos clave se colocan primero: la información sensible y los resultados de la prueba de acceso no autorizado se ponen al inicio, reduciendo llamadas repetidas del LLM tras el truncado
    if agg["secrets"]:
        out.append(f"\n## ⚠ Posible información sensible ({len(agg['secrets'])})")
        out += [f"  {s}" for s in agg["secrets"]]

    auto_probe = args.get("auto_probe", True)
    probe_targets = agg["paths"] + [u for u in agg["urls"] if _host_of(u) == host]
    if auto_probe and probe_targets:
        probe_out = await execute_unauth_test(
            agent,
            {
                "base_url": url,
                "endpoints": probe_targets,
                "auth_header": args.get("auth_header"),
                "max_endpoints": int(args.get("max_endpoints", 60) or 60),
            },
        )
        out.append("\n" + probe_out)

    out.append(f"\n## Interfaces/rutas ({len(agg['paths'])})")
    out += [f"  {p}" for p in agg["paths"][:120]]
    out.append(f"\n## Dominios relacionados ({len(agg['domains'])})")
    out += [f"  {d}" for d in agg["domains"][:60]]
    out.append(f"\n## URL absolutas ({len(agg['urls'])})")
    out += [f"  {u}" for u in agg["urls"][:60]]
    return "\n".join(out)


# ── Prueba de acceso no autorizado (verifica una por una las interfaces recopiladas por JS) ────────────────────────────────────

# Acciones destructivas: incluso enviando solo GET pueden provocar efectos secundarios (bombardeo de SMS/modificación de datos), se omiten siempre
_DESTRUCTIVE_RE = re.compile(
    r"(?i)(delete|remove|destroy|update|modify|edit|/add|/create|insert|/save|clear|"
    r"reset|drop|logout|sign ?out|sms|sendcode|send_?sms|captcha|verifycode|/pay|/order/cancel)"
)
# Señal fuerte de muro de autenticación: si aparece, se determina que es una página de inicio de sesión/bloqueo (evita clasificar erróneamente páginas públicas que contienen enlaces de navegación con "login")
_AUTHWALL_MARKERS = (
    "inicia sesión", "inicie sesión primero", "no ha iniciado sesión", "no autorizado", "sin permiso", "permisos insuficientes", "inicie sesión para ver",
    "unauthorized", "access denied", "not logged in", "please log in",
    "authentication required", "se requiere iniciar sesión",
)
_PASSWORD_FIELD_RE = re.compile(r"""(?i)(?:type|name)\s*=\s*["']password["']""")


def _parse_auth_header(raw: Any) -> dict[str, str]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    text = str(raw)
    if ":" in text:
        name, _, value = text.partition(":")
        return {name.strip(): value.strip()}
    # Token sin prefijo → se trata como Bearer
    return {"Authorization": f"Bearer {text.strip()}"}


def _is_auth_wall(body: str) -> bool:
    """Determina si es una página de bloqueo de inicio de sesión/autenticación: señal textual fuerte o presencia de un campo de contraseña (no se basa solo en la palabra "login" para evitar falsos positivos)."""
    head = body[:4000]
    low = head.lower()
    if any(m.lower() in low for m in _AUTHWALL_MARKERS):
        return True
    return bool(_PASSWORD_FIELD_RE.search(head))


def _classify_unauth(status: int, body: str, ctype: str) -> tuple[str, bool]:
    """Devuelve (texto del veredicto, si es un posible indicio de acceso no autorizado)."""
    if status in (401, 403):
        return "✓ Bloqueado por autenticación", False
    if status in (301, 302, 307, 308):
        return "↪ Redirección (posible inicio de sesión)", False
    if status == 404:
        return "— No existe", False
    if status == 405:
        return "· Método no permitido", False
    if status == 200:
        if not body.strip():
            return "· 200 respuesta vacía", False
        if _is_auth_wall(body):
            return "· 200 muro de inicio de sesión/autenticación", False
        is_data = ("json" in ctype.lower()) or body.lstrip()[:1] in ("{", "[")
        if is_data:
            return "⚠ Posible acceso no autorizado (devuelve datos)", True
        if "html" in ctype.lower() or body.lstrip()[:1] == "<":
            return "· 200 página HTML (no es una interfaz)", False  # Página pública, no es un caso de interfaz no autorizada
        return "⚠ 200 requiere confirmación manual", True
    return f"? HTTP {status}", False


async def _probe_endpoints(
    client: Any, base: str, endpoints: list[str], auth: dict[str, str],
    cap: int, sem: asyncio.Semaphore,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    base_host = _host_of(base)
    seen: set[str] = set()
    todo: list[str] = []
    for ep in endpoints:
        full = ep if "://" in ep else urljoin(base, ep)
        if _host_of(full) != base_host:  # No se ataca a dominios relacionados fuera del alcance autorizado
            continue
        if _DESTRUCTIVE_RE.search(full):  # Línea roja de separación lectura/escritura: se omiten las interfaces destructivas
            results.append({"url": full, "status": "-", "verdict": "🚫 Omitido (interfaz destructiva)", "lead": False, "length": 0})
            continue
        if full in seen:
            continue
        seen.add(full)
        todo.append(full)
    todo = todo[:cap]

    # Los endpoints REST CRUD list/query/search suelen requerir POST (incluye variantes de framework como listForLayUI)
    _POST_VERBS_RE = re.compile(
        r"(?i)/(?:list|query|search|page|find|select|export|count|batch|all)"
        r"(?:[A-Z][a-zA-Z0-9]*)*(?:\?|$)"
    )

    async def one(url: str) -> None:
        async with sem:
            # Se prioriza GET; para endpoints REST CRUD list/query se prueba adicionalmente POST
            methods = ["GET"]
            if _POST_VERBS_RE.search(url):
                methods.append("POST")

            best_row: dict[str, Any] | None = None
            for method in methods:
                try:
                    if method == "GET":
                        r = await client.get(url)
                    else:
                        r = await client.post(url, content="{}", headers={"Content-Type": "application/json"})
                except Exception as e:
                    if best_row is None:
                        best_row = {"url": url, "status": "ERR", "verdict": f"Solicitud fallida:{e}",
                                    "lead": False, "length": 0, "method": method}
                    continue
                body = r.text
                ctype = r.headers.get("content-type", "")
                verdict, lead = _classify_unauth(r.status_code, body, ctype)
                row = {"url": url, "status": r.status_code, "verdict": verdict,
                       "lead": lead, "length": len(r.content), "method": method}
                if lead and auth:
                    try:
                        hdrs = dict(auth)
                        if method == "POST":
                            hdrs["Content-Type"] = "application/json"
                            ra = await client.post(url, content="{}", headers=hdrs)
                        else:
                            ra = await client.get(url, headers=hdrs)
                        if ra.status_code == 200 and abs(len(ra.content) - len(r.content)) <= max(50, len(r.content) * 0.1):
                            row["verdict"] = "🔴 Acceso no autorizado confirmado (sin token = con token)"
                    except Exception:
                        pass
                # Se conserva el método con el indicio de hallazgo más fuerte
                if best_row is None or (lead and not best_row.get("lead")) or (lead and len(r.content) > best_row.get("length", 0)):
                    best_row = row
            if best_row is not None:
                results.append(best_row)

    await asyncio.gather(*(one(u) for u in todo))
    # Se prioriza el indicio y luego se ordena por estado
    results.sort(key=lambda x: (not x.get("lead"), str(x.get("status"))))
    return results


async def execute_unauth_test(agent: AgentContext, args: dict[str, Any]) -> str:
    """Realiza una prueba de acceso no autorizado en cada una de las interfaces de un lote (solo GET seguros, se omiten las interfaces destructivas)."""
    cfg = _get_recon_cfg(agent)
    base = str(args.get("base_url") or args.get("url") or "").strip()
    endpoints = args.get("endpoints") or []
    if isinstance(endpoints, str):
        endpoints = [e.strip() for e in re.split(r"[\s,]+", endpoints) if e.strip()]
    if not base and endpoints:
        base = endpoints[0]
    if not base:
        return "[!] unauth_test requiere base_url (o indicar una URL completa en endpoints)"
    if "://" not in base:
        base = "http://" + base
    host = _host_of(base)

    violation = enforce_host_path_constraints(agent, host=host, target=host)
    if violation:
        return violation
    if not endpoints:
        return "[!] unauth_test requiere endpoints (lista de rutas/URLs de interfaces, normalmente provenientes de js_recon)"

    auth = _parse_auth_header(args.get("auth_header"))
    cap = int(args.get("max_endpoints", 60) or 60)
    try:
        async with _make_client(cfg) as client:
            sem = asyncio.Semaphore(cfg.max_concurrency)
            rows = await _probe_endpoints(client, base, endpoints, auth, cap, sem)
    except Exception as e:
        return f"[!] Error de ejecución en unauth_test: {e}"

    leads = [r for r in rows if r.get("lead")]
    out = [f"# Prueba de acceso no autorizado — {host}  se probaron {len(rows)} interfaces, indicios posibles {len(leads)}"]
    if auth:
        out.append("  (comparación diferencial con/sin token habilitada)")
    for r in rows:
        st = r.get("status")
        method = r.get("method", "GET")
        tag = f"[{str(st):>3}]" if method == "GET" else f"[{str(st):>3} {method}]"
        out.append(f"  {tag:>12} {str(r.get('length','')):>7}B  {r['verdict']:<22} {r['url']}")
    if leads:
        out.append("\n⚠ Revisión manual prioritaria (confirmar si se pueden leer datos de otros usuarios / si son sensibles):")
        out += [f"  {r['url']}" for r in leads]
    return "\n".join(out)


# ── Enumeración de directorios (basado en dirsearch) ──────────────────────────────────────────────────


def _load_wordlist(cfg: Any) -> list[str]:
    path = (cfg.dir_wordlist_path or "").strip()
    if path:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                words = [ln.strip().lstrip("/") for ln in f if ln.strip() and not ln.startswith("#")]
            if words:
                return words
        except OSError:
            pass
    return list(_BUILTIN_DIR_WORDLIST)


_HIT_CODES = {200, 201, 204, 301, 302, 307, 401, 403, 405, 500}


async def execute_dir_enum(agent: AgentContext, args: dict[str, Any]) -> str:
    """Enumeración de directorios: fuerza bruta concurrente con diccionario, con línea base 404 / detección global de simulación y filtrado por código de estado."""
    cfg = _get_recon_cfg(agent)
    base = str(args.get("url", "") or "").strip()
    if not base:
        return "[!] dir_enum requiere el parámetro url"
    if "://" not in base:
        base = "http://" + base
    base = base.rstrip("/") + "/"
    host = _host_of(base)

    violation = enforce_host_path_constraints(agent, host=host, target=host)
    if violation:
        return violation

    extensions = args.get("extensions") or []
    if isinstance(extensions, str):
        extensions = [e.strip() for e in extensions.split(",") if e.strip()]
    words = _load_wordlist(cfg)
    if args.get("wordlist"):
        extra = args["wordlist"]
        words = (extra if isinstance(extra, list) else [extra]) + words

    # Expansión de extensiones
    candidates: list[str] = []
    for w in words:
        candidates.append(w)
        for ext in extensions:
            ext = ext.lstrip(".")
            if "." not in w.split("/")[-1]:
                candidates.append(f"{w}.{ext}")
    candidates = _dedup_cap(candidates, cfg.dir_max_requests)

    try:
        async with _make_client(cfg) as client:
            # Línea base 404 + detección global de simulación: solicita una ruta aleatoria que no existe
            baseline_len = None
            try:
                rnd = await client.get(urljoin(base, "vulnclaw_nope_8f3a2c1e9b/"))
                if rnd.status_code in (200, 301, 302):
                    baseline_len = len(rnd.text)
                    # La ruta aleatoria devolvió 200 → respuesta de simulación global, se detiene la fuerza bruta (regla inquebrantable de CLAUDE.md)
                    if rnd.status_code == 200:
                        return (
                            f"[!] dir_enum finalizado: la ruta aleatoria {base}vulnclaw_nope_... devolvió 200"
                            f" (longitud {baseline_len}); el objetivo parece devolver 200 para cualquier ruta, la enumeración de directorios no tiene sentido."
                        )
            except Exception:
                pass

            sem = asyncio.Semaphore(cfg.max_concurrency)
            hits: list[tuple[int, int, str]] = []

            async def probe(path: str) -> None:
                target = urljoin(base, path)
                async with sem:
                    try:
                        r = await client.get(target)
                    except Exception:
                        return
                code = r.status_code
                length = len(r.content)
                if code in _HIT_CODES:
                    if baseline_len is not None and code in (200, 301, 302) and length == baseline_len:
                        return  # Misma longitud que la línea base de simulación, se considera ruido
                    hits.append((code, length, path))

            await asyncio.gather(*(probe(p) for p in candidates))
    except Exception as e:
        return f"[!] Error de ejecución en dir_enum: {e}"

    hits.sort(key=lambda x: (x[0], -x[1]))
    out = [f"# Enumeración de directorios — {base}  {len(candidates)} solicitudes, {len(hits)} coincidencias"]
    if baseline_len is not None:
        out.append(f"  (longitud de línea base 404 ≈ {baseline_len})")
    for code, length, path in hits:
        out.append(f"  [{code}] {length:>8}B  {base}{path}")
    return "\n".join(out) if hits else "\n".join(out + ["  (sin coincidencias válidas)"])
