"""Agent built-in tools and OpenAI tool schema helpers."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext

from urllib.parse import urlparse

from vulnclaw.agent.constraint_policy import validate_tool_action
from vulnclaw.agent.network_scan import (
    attach_network_scan_to_session,
    build_nmap_command,
    build_nmap_plan,
    deescalate_nmap_argv,
    nmap_failure_needs_deescalation,
    nmap_has_raw_socket_access,
    parse_nmap_xml_structured,
    summarize_network_scan,
    target_is_private_literal,
    without_privileged_nmap_args,
)
from vulnclaw.agent.roles import role_tool_violation, tool_allowed_for_role

# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: elimina la violación V1 — infer_port_from_url se
#          movió a config/url_utils.py; aquí se reexporta por compatibilidad hacia atrás.
from vulnclaw.config.url_utils import infer_port_from_url  # noqa: F401 — re-export
from vulnclaw.intel.tools import (
    INTEL_TOOL_NAMES,
    dispatch_intel_tool,
    intel_tool_schemas,
)
from vulnclaw.traffic.tools import (
    TRAFFIC_TOOL_NAMES,
    dispatch_traffic_tool,
    traffic_tool_schemas,
)


def role_allows_tool(role: str | None, tool_name: str) -> bool:
    """Return whether the active team role may see or call a tool."""
    return tool_allowed_for_role(tool_name, role)

BLOCKED_PATTERNS: list[str] = [
    r"os\.\s*system\s*\(",
    r"subprocess\.\s*Popen\s*\(",
    r"shutil\.\s*rmtree\s*\(",
    r"__import__\s*\(\s*['\"]os['\"]",
    r"open\s*\(\s*['\"].*vulnclaw.*config",
    r"open\s*\(\s*['\"].*\.vulnclaw",
]

RESERVED_IP_RANGES: list[tuple[str, str, str]] = [
    ("198.18.0.0", "198.19.255.255", "dirección de benchmarking RFC 2544"),
    ("10.0.0.0", "10.255.255.255", "dirección privada RFC 1918"),
    ("172.16.0.0", "172.31.255.255", "dirección privada RFC 1918"),
    ("192.168.0.0", "192.168.255.255", "dirección privada RFC 1918"),
    ("127.0.0.0", "127.255.255.255", "dirección de loopback RFC 1122"),
    ("169.254.0.0", "169.254.255.255", "link-local RFC 3927"),
    ("0.0.0.0", "0.255.255.255", "red actual RFC 1122"),
    ("224.0.0.0", "239.255.255.255", "dirección multicast RFC 5771"),
    ("240.0.0.0", "255.255.255.255", "dirección reservada RFC 1112"),
]

SAFE_MODE_PATTERNS: list[str] = [
    r"open\s*\(",
    r"with\s+open\s*\(",
    r"socket\.",
    r"urllib",
    r"http\.client",
    r"ftplib",
    r"smtplib",
    r"requests\.",
    r"import\s+os",
    r"from\s+os\s+import",
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"import\s+shutil",
    r"from\s+shutil\s+import",
    r"import\s+pathlib",
    r"from\s+pathlib\s+import",
    r"__import__",
]

LAB_MODE_PATTERNS: list[str] = [
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"os\.\s*system\s*\(",
    r"subprocess\.\s*Popen\s*\(",
    r"shutil\.\s*rmtree\s*\(",
]


def resolve_traffic_store(agent: AgentContext) -> Any:
    """Resolve the per-run traffic evidence store for this agent.

    Prefers a run/evidence directory carried on the session (once the run-dir
    PRD lands); otherwise falls back to the config-scoped evidence directory so
    headless/CI runs still get a durable store.
    """
    from vulnclaw.traffic.paths import resolve_traffic_store as _resolve

    session = getattr(agent, "session_state", None)
    base = getattr(session, "evidence_dir", None) or getattr(session, "run_dir", None)
    return _resolve(base)


def enforce_traffic_repeat_constraints(
    agent: AgentContext, store: Any, args: dict[str, Any]
) -> str | None:
    """Gate a ``traffic_repeat`` against task host/path/port constraints.

    The effective target is the ``url`` override if supplied, else the stored
    request's URL. Returns a violation message when the target is out of scope,
    or ``None`` when the replay is allowed.
    """
    target_url = str(args.get("url") or "").strip()
    if not target_url:
        entry = store.find(str(args.get("request_id", "")))
        target_url = str((entry or {}).get("url", "")).strip()
    if not target_url:
        return None

    parsed = urlparse(target_url)
    host = parsed.hostname or ""
    path = parsed.path or ""
    violation = enforce_host_path_constraints(agent, host=host, path=path, target=host)
    if violation is not None:
        return violation

    port = infer_port_from_url(target_url)
    if port is not None:
        violation = enforce_port_constraints(agent, [port], target=host or target_url)
        if violation is not None:
            return violation
    return None


async def execute_mcp_tool(agent: AgentContext, tool_name: str, args: dict[str, Any]) -> str:
    """Execute a tool call via MCP manager or built-in tools."""
    violation = role_tool_violation(getattr(agent, "active_role", None), tool_name)
    if violation is not None:
        return violation

    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is not None:
        tool_violation = validate_tool_action(tool_name, args, constraints)
        if tool_violation is not None:
            if session is not None and hasattr(session, "add_constraint_violation_event"):
                from vulnclaw.agent.constraint_policy import infer_tool_action

                session.add_constraint_violation_event(
                    source="tool",
                    action=infer_tool_action(tool_name, args),
                    tool_name=tool_name,
                    code="tool_action_blocked",
                    severity="high",
                    summary=tool_violation,
                    detail=json.dumps(args, ensure_ascii=False)[:500],
                )
            return f"[constraint_violation] {tool_violation}"

    if tool_name in INTEL_TOOL_NAMES:
        return await dispatch_intel_tool(agent, tool_name, args)

    if tool_name in TRAFFIC_TOOL_NAMES:
        store = resolve_traffic_store(agent)
        if tool_name == "traffic_repeat":
            # A url override could aim the replay at a blocked/out-of-scope host,
            # so gate it with the same host/path/port guards other network tools
            # use — the generic action check above does not see the target URL.
            violation = enforce_traffic_repeat_constraints(agent, store, args)
            if violation is not None:
                return violation
        # traffic_repeat issues a real network request; keep the loop responsive.
        return await asyncio.to_thread(dispatch_traffic_tool, store, tool_name, args)

    if tool_name == "python_execute":
        return await execute_python(agent, args)

    if tool_name == "load_skill_reference":
        try:
            from vulnclaw.skills.loader import load_skill_reference

            skill_name = args.get("skill_name", "")
            ref_name = args.get("reference_name", "")
            content = load_skill_reference(skill_name, ref_name)
            if content:
                state = getattr(agent, "session_state", None) or getattr(
                    getattr(agent, "context", None), "state", None
                )
                if state is not None and hasattr(state, "record_loaded_reference"):
                    state.record_loaded_reference(skill_name, ref_name)
                return content
            return f"[!] Documento de referencia no encontrado: {skill_name}/{ref_name}"
        except Exception as e:
            return f"[!] Error al cargar el documento de referencia: {e}"

    if tool_name == "nmap_scan":
        return await execute_nmap(agent, args)

    if tool_name == "crypto_decode":
        try:
            from vulnclaw.skills.crypto_tools import execute as crypto_execute

            operation = args.get("operation", "")
            input_str = args.get("input", "")
            kwargs: dict[str, Any] = {}
            for key in ("key", "iv", "shift", "secret", "header", "algorithm"):
                if key in args and args[key]:
                    kwargs[key] = args[key]
                    if key == "shift":
                        kwargs[key] = int(args[key])
            result = crypto_execute(operation=operation, input_str=input_str, **kwargs)
            if result.get("success"):
                return f"[✓] Resultado de {operation}:\n{result['result']}"
            return f"[!] {operation} falló: {result.get('error', 'Error desconocido')}"
        except Exception as e:
            return f"[!] Error al ejecutar la herramienta de criptografía: {e}"

    if tool_name == "brute_force_login":
        return await execute_brute_force(agent, args)

    if tool_name in {"space_search", "subdomain_enum", "js_recon", "dir_enum", "unauth_test"}:
        from vulnclaw.agent import recon_tools

        dispatch = {
            "space_search": recon_tools.execute_space_search,
            "subdomain_enum": recon_tools.execute_subdomain_enum,
            "js_recon": recon_tools.execute_js_recon,
            "dir_enum": recon_tools.execute_dir_enum,
            "unauth_test": recon_tools.execute_unauth_test,
        }
        try:
            return await dispatch[tool_name](agent, args)
        except Exception as e:
            return f"[!] Error al ejecutar la herramienta ({tool_name}): {e}"

    if not agent.mcp_manager:
        return f"[!] El gestor MCP no está inicializado, no se puede ejecutar la herramienta: {tool_name}"

    try:
        result = await agent.mcp_manager.call_tool(tool_name, args)
        if isinstance(result, dict):
            if result.get("ok", False):
                content = result.get("content")
                structured = result.get("structured_content")
                summary_parts: list[str] = []
                if content is not None:
                    summary_parts.append(str(content))
                if isinstance(structured, dict) and structured:
                    summary_parts.append(
                        f"[structured] {json.dumps(structured, ensure_ascii=False)}"
                    )
                if summary_parts:
                    return "\n".join(summary_parts)
                return f"[tool:{tool_name}] completed"

            message = str(result.get("message") or "")
            suggestion = str(result.get("suggestion") or "")
            error_type = str(result.get("error_type") or "error")
            if suggestion:
                return f"[{error_type}] {message}\n[suggestion] {suggestion}".strip()
            return f"[{error_type}] {message}".strip()

        text = str(result)
        if text.strip() in ("undefined", "null", "None"):
            return f"[!] La herramienta {tool_name} devolvió un resultado vacío (undefined), la llamada pudo haber fallado"
        return text
    except Exception as e:
        return f"[!] Error al ejecutar la herramienta ({tool_name}): {e}"


def enforce_port_constraints(agent: AgentContext, ports: list[int], *, target: str = "") -> str | None:
    """Return a user-facing violation message when requested ports are out of scope."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return None

    if constraints.allowed_ports:
        disallowed = [port for port in ports if port not in constraints.allowed_ports]
        if disallowed:
            allowed = ", ".join(str(p) for p in constraints.allowed_ports)
            denied = ", ".join(str(p) for p in disallowed)
            suffix = f" for target {target}" if target else ""
            return f"[constraint_violation] Port(s) {denied} are outside allowed scope [{allowed}]{suffix}."

    blocked = [port for port in ports if port in constraints.blocked_ports]
    if blocked:
        denied = ", ".join(str(p) for p in blocked)
        suffix = f" for target {target}" if target else ""
        return f"[constraint_violation] Port(s) {denied} are blocked by task constraints{suffix}."

    return None


def enforce_host_path_constraints(
    agent: AgentContext, *, host: str = "", path: str = "", target: str = ""
) -> str | None:
    """Return a user-facing violation when host/path are out of scope."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return None

    if constraints.allowed_hosts and host and host not in constraints.allowed_hosts:
        allowed = ", ".join(constraints.allowed_hosts)
        return f"[constraint_violation] Host {host} is outside allowed scope [{allowed}] for target {target or host}."

    if host and host in constraints.blocked_hosts:
        return f"[constraint_violation] Host {host} is blocked by task constraints for target {target or host}."

    if constraints.allowed_paths and path and path not in constraints.allowed_paths:
        allowed = ", ".join(constraints.allowed_paths)
        return f"[constraint_violation] Path {path} is outside allowed scope [{allowed}] for target {target or host}."

    if path and path in constraints.blocked_paths:
        return f"[constraint_violation] Path {path} is blocked by task constraints for target {target or host}."

    return None


def infer_ports_from_nmap_args(args: dict[str, Any]) -> list[int]:
    """Infer concrete target ports from nmap arguments for constraint checks."""
    custom_ports = str(args.get("ports", "") or "").strip()
    scan_type = str(args.get("scan_type", "top_ports") or "top_ports")

    if custom_ports:
        ports: list[int] = []
        for chunk in custom_ports.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                start_text, end_text = chunk.split("-", 1)
                try:
                    start = int(start_text)
                    end = int(end_text)
                except ValueError:
                    continue
                if 0 < start <= end <= 65535:
                    ports.extend(range(start, end + 1))
                continue
            try:
                port = int(chunk)
            except ValueError:
                continue
            if 0 < port <= 65535:
                ports.append(port)
        return sorted(set(ports))

    if scan_type == "top_ports":
        return []
    return []


def build_openai_tools(mcp_manager: Any, *, active_role: str | None = None) -> list[dict[str, Any]]:
    """Build OpenAI function calling schema from MCP tools + built-in tools."""
    tools: list[dict[str, Any]] = []

    def append_tool(tool: dict[str, Any]) -> None:
        name = str(tool.get("function", {}).get("name", ""))
        if role_allows_tool(active_role, name):
            tools.append(tool)

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "load_skill_reference",
                "description": "Carga el documento de referencia de un Skill específico para obtener metodología, flujo de trabajo o referencia de comandos detallada de pentesting. Usa esta herramienta cuando el system prompt mencione 'documentos de referencia disponibles' para obtener el contenido concreto.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Nombre del Skill, por ejemplo client-reverse, web-security-advanced, ai-mcp-security, intranet-pentest-advanced, pentest-tools, rapid-checklist, crypto-toolkit, ctf-web, ctf-crypto, ctf-misc, osint-recon, secknowledge-skill",
                        },
                        "reference_name": {
                            "type": "string",
                            "description": "Nombre del archivo de referencia, por ejemplo 02-client-api-reverse-and-burp.md, web-injection.md, encoding-cheatsheet.md",
                        },
                    },
                    "required": ["skill_name", "reference_name"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "python_execute",
                "description": (
                    "Ejecuta un fragmento de código Python. Se usa para: construir solicitudes "
                    "HTTP complejas y analizar la respuesta, hacer conversión de codificación y "
                    "procesamiento de datos, probar distintos payloads en lote, comparar diferencias "
                    "de respuesta, hacer cálculos matemáticos, etc. El código se ejecuta en un "
                    "entorno restringido con un timeout de 30 segundos. "
                    "Librerías preinstaladas: requests, beautifulsoup4, pycryptodome, base64, json, re, etc. "
                    "Importante: usa esta herramienta para construir solicitudes HTTP en vez de suponer el contenido de la respuesta."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Código Python a ejecutar. Admite varias líneas, se pueden importar librerías estándar y requests/bs4, etc.",
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Breve descripción del propósito de la ejecución (para el registro de auditoría), por ejemplo 'construir solicitud HTTP para probar bypass de comparación débil'",
                        },
                    },
                    "required": ["code"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "crypto_decode",
                "description": (
                    "Herramienta de codificación/decodificación y cifrado/descifrado. Úsala ante "
                    "cadenas codificadas en base64/hex/URL/HTML/Unicode, o cuando necesites calcular "
                    "un hash, descifrar AES/DES, parsear un JWT, etc. "
                    "Importante: no adivines el resultado de la decodificación por tu cuenta, usa "
                    "siempre esta herramienta para asegurar la precisión. "
                    "Operaciones soportadas: base64_encode/decode, base32_encode/decode, base58_encode/decode, "
                    "hex_encode/decode, url_encode/decode, html_encode/decode, unicode_encode/decode, "
                    "rot13_encode/decode, caesar_encode/decode, morse_encode/decode, "
                    "md5_hash, sha1_hash, sha256_hash, sha512_hash, "
                    "aes_encrypt/decrypt, jwt_decode/encode, auto_decode"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "description": "Nombre de la operación"},
                        "input": {
                            "type": "string",
                            "description": "Cadena de entrada a procesar (texto a codificar/decodificar/hashear/cifrar)",
                        },
                        "key": {
                            "type": "string",
                            "description": "Clave de cifrado/descifrado (necesaria para AES/DES, 16/24/32 bytes)",
                        },
                        "iv": {"type": "string", "description": "Vector de inicialización AES (16 bytes, opcional)"},
                        "shift": {
                            "type": "integer",
                            "description": "Desplazamiento del cifrado César (por defecto 3; si no se indica al decodificar, se prueban todos los desplazamientos por fuerza bruta)",
                        },
                        "secret": {"type": "string", "description": "Clave de firma JWT"},
                    },
                    "required": ["operation", "input"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "nmap_scan",
                "description": (
                    "Herramienta de escaneo de puertos de red nmap. Se usa en la fase de "
                    "reconocimiento para descubrir puertos abiertos, versión de servicios y huella "
                    "del sistema operativo del objetivo.\n"
                    "Ejemplos de uso:\n"
                    "  Escanear puertos comunes: scan_type=top_ports, target=1.2.3.4\n"
                    "  Escaneo SYN: scan_type=syn, target=1.2.3.4 (requiere permisos de administrador)\n"
                    "  Detección de versión de servicio: scan_type=service, target=1.2.3.4\n"
                    "  Escaneo de vulnerabilidades: scan_type=vuln, target=1.2.3.4\n"
                    "  Escaneo completo: scan_type=full, target=1.2.3.4\n"
                    "Prioriza nmap_scan en vez de construir un escaneo por socket con python_execute; nmap es más profesional y preciso."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Dirección IP o dominio objetivo (obligatorio), por ejemplo 192.168.1.1 o scanme.nmap.org",
                        },
                        "scan_type": {
                            "type": "string",
                            "description": "Tipo de escaneo: top_ports/syn/tcp/service/os/vuln/full",
                        },
                        "ports": {
                            "type": "string",
                            "description": "Puerto o rango específico (opcional), por ejemplo 80,443,8080 o 1-1000",
                        },
                        "timing": {
                            "type": "integer",
                            "description": "Plantilla de velocidad de escaneo 0-5 (por defecto 4); a mayor número, más rápido pero más fácil de detectar",
                        },
                        "profile": {
                            "type": "string",
                            "description": "Perfil de escaneo de red opcional: adaptive/fast/thorough/stealth. El perfil ajusta conjuntamente puertos, velocidad, detección de servicios y scripts de seguridad.",
                        },
                    },
                    "required": ["target"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "brute_force_login",
                "description": (
                    "Fuerza bruta de contraseñas contra un formulario de login. Gestiona "
                    "automáticamente la Session Cookie, extrae y actualiza automáticamente el "
                    "CSRF Token, y determina si el login tuvo éxito o falló. "
                    "Completa todos los intentos de contraseña en una sola llamada, devolviendo el resultado de cada una."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL de la página de login",
                        },
                        "username_field": {
                            "type": "string",
                            "description": "Nombre del campo de usuario, por ejemplo 'username'",
                        },
                        "password_field": {
                            "type": "string",
                            "description": "Nombre del campo de contraseña, por ejemplo 'password'",
                        },
                        "csrf_field": {
                            "type": "string",
                            "description": "Nombre del campo del token CSRF, por ejemplo 'user_token'",
                        },
                        "username": {
                            "type": "string",
                            "description": "Nombre de usuario a atacar por fuerza bruta",
                        },
                        "passwords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de contraseñas a probar (máximo 20)",
                        },
                        "success_keyword": {
                            "type": "string",
                            "description": "Palabra característica que aparece en la página tras un login exitoso, por ejemplo 'Welcome', 'Dashboard'",
                        },
                        "failure_keyword": {
                            "type": "string",
                            "description": "Palabra característica que aparece en la página tras un login fallido, por ejemplo 'Login failed'",
                        },
                        "submit_action": {
                            "type": "string",
                            "description": "URL de destino del envío del formulario (opcional; si no se indica, se extrae del atributo action del formulario)",
                        },
                        "extra_data": {
                            "type": "object",
                            "description": "Campos de formulario adicionales, por ejemplo {\"Login\": \"Login\"}",
                        },
                    },
                    "required": ["url", "password_field", "passwords"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "space_search",
                "description": (
                    "Búsqueda de activos por mapeo de superficie (FOFA/Hunter/Quake/Shodan/ZoomEye/0.zone). "
                    "En la fase de reconocimiento se usa para descubrir de forma pasiva activos, IPs, "
                    "puertos, subdominios, títulos y huellas de componentes del objetivo, sin contactarlo directamente. "
                    "Al indicar domain se construye automáticamente la consulta según la sintaxis de cada motor; también se puede pasar la sintaxis completa de query. "
                    "Con engine=all se consultan en paralelo todos los motores con clave configurada."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "engine": {
                            "type": "string",
                            "description": "fofa/hunter/quake/shodan/zoomeye/zerozone/all, por defecto fofa",
                        },
                        "query": {
                            "type": "string",
                            "description": "Sintaxis de consulta nativa del motor, por ejemplo 'domain=\"x.com\"', 'app=\"Struts2\"' (opcional)",
                        },
                        "domain": {
                            "type": "string",
                            "description": "Dominio principal objetivo; construye automáticamente la consulta domain de cada motor (se usa cuando no se indica query)",
                        },
                        "size": {"type": "integer", "description": "Cantidad de resultados a devolver, por defecto 100"},
                    },
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "subdomain_enum",
                "description": (
                    "Enumeración de subdominios. Primero agrega pasivamente con los motores de "
                    "mapeo de superficie configurados, y luego hace fuerza bruta de resolución DNS "
                    "con un diccionario integrado, devolviendo la lista deduplicada de subdominios "
                    "activos. Prioriza esto sobre escribir tu propia fuerza bruta con python_execute."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Dominio principal, por ejemplo nju.edu.cn"},
                        "brute": {
                            "type": "boolean",
                            "description": "Si se habilita la fuerza bruta DNS con diccionario integrado (por defecto true)",
                        },
                    },
                    "required": ["domain"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "js_recon",
                "description": (
                    "Reconocimiento de información en JS (inspirado en URLFinder). Descarga la "
                    "página objetivo y todos los archivos .js que referencia, extrayendo "
                    "interfaces/rutas de API, dominios relacionados, URLs absolutas y posibles "
                    "claves codificadas de forma fija (AK/SK, token, JWT, clave privada, etc.). "
                    "Por defecto auto_probe=true: sondea automáticamente cada interfaz del mismo "
                    "origen recolectada en busca de acceso sin autorización (solo GET seguro, "
                    "salta interfaces destructivas). "
                    "Priorízala en la fase de reconocimiento, y usa los endpoints realmente "
                    "extraídos para alimentar las pruebas siguientes, en vez de adivinar interfaces."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL de la página objetivo"},
                        "max_js": {
                            "type": "integer",
                            "description": "Cantidad máxima de archivos JS a descargar (por defecto 30)",
                        },
                        "auto_probe": {
                            "type": "boolean",
                            "description": "Si se sondean automáticamente las interfaces recolectadas en busca de acceso sin autorización (por defecto true)",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "Cabecera de autenticación opcional para comparación diferencial, por ejemplo 'Authorization: Bearer xxx', para verificar si también se pueden obtener datos sin token",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "unauth_test",
                "description": (
                    "Sondeo de acceso sin autorización. Para un lote de interfaces (normalmente "
                    "endpoints recolectados por js_recon), envía solicitudes sin credenciales una "
                    "por una y determina, según el código de estado/cuerpo de respuesta/tipo de "
                    "contenido: ⚠posible acceso sin autorización (devuelve datos) / ✓bloqueado por "
                    "autenticación / ↪redirige a login / —no existe. "
                    "Si se indica auth_header, hace comparación diferencial con/sin token; si sin "
                    "token se obtienen los mismos datos, se determina 🔴acceso sin autorización confirmado. "
                    "Cumple estrictamente la separación lectura/escritura: solo envía GET seguros, "
                    "salta automáticamente interfaces destructivas como delete/update/sms, y no recorre IDs en lote."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base_url": {"type": "string", "description": "URL base del objetivo (determina el alcance del mismo origen)"},
                        "endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de rutas/URLs de interfaces a probar (provenientes de las interfaces/rutas de js_recon)",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "Cabecera de autenticación opcional para comparación diferencial, por ejemplo 'Authorization: Bearer xxx' o 'Cookie: session=...'",
                        },
                        "max_endpoints": {
                            "type": "integer",
                            "description": "Cantidad máxima de interfaces a sondear (por defecto 60)",
                        },
                    },
                    "required": ["base_url", "endpoints"],
                },
            },
        }
    )

    append_tool(
        {
            "type": "function",
            "function": {
                "name": "dir_enum",
                "description": (
                    "Enumeración de directorios/archivos (inspirada en dirsearch). Fuerza bruta de "
                    "diccionario concurrente, con línea base de 404 y detección global de "
                    "respuestas simuladas (si una ruta aleatoria devuelve 200, se determina que es "
                    "simulada y se detiene), además de filtrado por código de estado y longitud de respuesta. "
                    "Solo hace sondeo GET seguro, no toca rutas destructivas como delete/update."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL base del objetivo, por ejemplo https://x.com/"},
                        "extensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Expansión de extensiones, por ejemplo ['php','jsp','bak','zip'] (opcional)",
                        },
                        "wordlist": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Rutas personalizadas adicionales (diccionario heurístico basado en patrones de nomenclatura, opcional)",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    for tool in intel_tool_schemas():
        append_tool(tool)

    for tool in traffic_tool_schemas():
        append_tool(tool)

    if mcp_manager:
        for schema in mcp_manager.get_tool_schemas():
            append_tool(
                {
                    "type": "function",
                    "function": {
                        "name": schema.get("name", ""),
                        "description": schema.get("description", ""),
                        "parameters": schema.get(
                            "inputSchema", {"type": "object", "properties": {}}
                        ),
                    },
                }
            )

    return tools


async def execute_nmap(agent: AgentContext, args: dict[str, Any]) -> str:
    target = args.get("target", "").strip()
    if not target:
        return "[!] nmap_scan requiere el parámetro target (IP o dominio objetivo)"

    host_violation = enforce_host_path_constraints(agent, host=target.lower(), target=target)
    if host_violation:
        return host_violation

    violation = enforce_port_constraints(agent, infer_ports_from_nmap_args(args), target=target)
    if violation:
        return violation

    try:
        ips = socket.getaddrinfo(target, None, socket.AF_INET)
        if ips:
            ip = ips[0][4][0]
            is_reserved, reason = is_reserved_ip(ip)
            if is_reserved and not target_is_private_literal(target):
                return (
                    f"[SKIP] El objetivo {target} resuelve a una dirección reservada/interna ({reason}, IP: {ip})\n"
                    f"Se omite el escaneo nmap. Se recomienda recolectar información directamente "
                    f"mediante huella web, enumeración de directorios, etc.; no gastes rondas en direcciones reservadas."
                )
    except Exception:
        pass

    scan_type = args.get("scan_type", "top_ports")
    custom_ports = args.get("ports", "")
    timing = int(args.get("timing", 4))
    profile = str(args.get("profile", "") or "").strip().lower()

    nmap_cmd = shutil.which("nmap")
    if not nmap_cmd:
        try:
            result = subprocess.run(
                ["where.exe", "nmap"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                nmap_cmd = result.stdout.strip().split("\n")[0]
        except Exception:
            pass
    if not nmap_cmd:
        return "[!] nmap no está instalado o no está en el PATH. Confirma que nmap esté instalado y agregado al PATH del sistema."

    if profile:
        plan = build_nmap_plan(
            profile=profile,
            scan_type=str(scan_type or ""),
            ports=str(custom_ports or ""),
            timing=timing,
            prior_recon=getattr(getattr(agent, "session_state", None), "recon_data", {}),
        )
        privileged = nmap_has_raw_socket_access()
        cmd = build_nmap_command(nmap_cmd, target, plan, privileged=privileged)
        deescalated_note = (
            ""
            if privileged or plan.args == without_privileged_nmap_args(plan.args)
            else "[i] Ejecutando sin permisos de administrador: se omitió la huella de sistema operativo (-O), el escaneo SYN se degradó a connect scan (-sT).\n"
        )
    else:
        plan = None
        privileged = nmap_has_raw_socket_access()
        deescalated_note = ""
        cmd = [nmap_cmd, "-v" if scan_type == "full" else "-q", f"-T{max(0, min(5, timing))}"]
        if scan_type == "top_ports":
            cmd.extend(["--top-ports", "100", "-oX", "-"])
        elif scan_type == "syn":
            cmd.extend(["-sS" if privileged else "-sT", "-oX", "-"])
            if not privileged:
                deescalated_note = "[i] Ejecutando sin permisos de administrador: se usa connect scan (-sT) en vez de SYN scan (-sS).\n"
        elif scan_type == "tcp":
            cmd.extend(["-sT", "-oX", "-"])
        elif scan_type == "service":
            cmd.extend(["-sV", "-oX", "-"])
        elif scan_type == "os":
            if privileged:
                cmd.extend(["-O", "-oX", "-"])
            else:
                cmd.extend(["-sV", "-oX", "-"])
                deescalated_note = (
                    "[i] Ejecutando sin permisos de administrador: la huella de sistema operativo (-O) no está disponible, se usa detección de servicios (-sV) en su lugar.\n"
                )
        elif scan_type == "vuln":
            cmd.extend(["--script", "vuln", "-oX", "-"])
        elif scan_type == "full":
            if privileged:
                cmd.extend(["-sS", "-O", "-sV", "--script", "default,safe", "-oX", "-"])
            else:
                cmd.extend(["-sT", "-sV", "--script", "default,safe", "-oX", "-"])
                deescalated_note = (
                    "[i] Ejecutando sin permisos de administrador: se omitió la huella de sistema operativo (-O), "
                    "el escaneo SYN se degradó a connect scan (-sT).\n"
                )
        else:
            cmd.extend(["-sV", "-oX", "-"])

        if custom_ports:
            cmd.extend(["-p", custom_ports])
        cmd.append(target)

    try:
        kwargs: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": 120,
        }
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = startupinfo
        result = subprocess.run(cmd, **kwargs)
        if (
            result.returncode != 0
            and not result.stdout
            and nmap_failure_needs_deescalation(result.stderr or "")
        ):
            fallback_cmd = deescalate_nmap_argv(cmd)
            if fallback_cmd != cmd:
                fallback = subprocess.run(fallback_cmd, **kwargs)
                if fallback.returncode == 0 or fallback.stdout:
                    result = fallback
                    deescalated_note = "[i] Tras un error de permisos, se reintentó con parámetros nmap sin privilegios.\n"
    except subprocess.TimeoutExpired:
        return "[!] El escaneo nmap superó el tiempo límite (120 segundos), reduce el alcance del escaneo o usa un timing más rápido"
    except PermissionError:
        return "[!] La ejecución de nmap fue rechazada (permisos insuficientes). En Windows, ejecuta la terminal como administrador."
    except Exception as e:
        return f"[!] Error al ejecutar nmap: {e}"

    if result.returncode != 0 and not result.stdout:
        return f"[!] El escaneo nmap falló ({result.returncode}): {result.stderr[:500]}"
    output = result.stdout or result.stderr
    human_summary = parse_nmap_xml(output, target)
    structured = parse_nmap_xml_structured(output, target)
    if getattr(agent, "session_state", None) is not None:
        attach_network_scan_to_session(
            agent.session_state,
            structured,
            profile=profile or str(scan_type or "top_ports"),
            safe_probes=profile != "vuln",
        )
    if profile:
        network_summary = summarize_network_scan(structured)
        return f"{deescalated_note}{human_summary}\n\n{network_summary}"
    return f"{deescalated_note}{human_summary}"


def is_reserved_ip(ip: str) -> tuple[bool, str]:
    try:
        import ipaddress

        addr = ipaddress.ip_address(ip)
        for start, end, desc in RESERVED_IP_RANGES:
            if ipaddress.ip_address(start) <= addr <= ipaddress.ip_address(end):
                return True, desc
        return False, ""
    except Exception:
        return False, ""


def validate_scan_target(target: str) -> str:
    try:
        ips = socket.getaddrinfo(target, None, socket.AF_INET)
        if not ips:
            return ""
        ip = ips[0][4][0]
        is_reserved, reason = is_reserved_ip(ip)
        if is_reserved:
            return (
                f"\n\n⚠️ **Advertencia: el objetivo {target} resuelve a una dirección reservada/interna ({reason})\n"
                f"   IP: {ip}\n"
                f"   El resultado de escanear esta dirección no representa el estado de seguridad del sistema real.\n"
                f"   La información de puertos en el resultado de nmap puede no tener relación con el objetivo real.**"
            )
    except Exception:
        pass
    return ""


def parse_nmap_xml(xml_output: str, target: str) -> str:
    if not xml_output or "<nmaprun" not in xml_output:
        lines = xml_output.strip().splitlines()[:80]
        return "Salida cruda de nmap:\n" + "\n".join(lines)

    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError:
        lines = xml_output.strip().splitlines()[:80]
        return "Salida cruda de nmap:\n" + "\n".join(lines)

    lines = [f"Resultado del escaneo nmap — {target}", "=" * 60]
    for host in root.findall(".//host"):
        hostname = host.find(".//hostname[@type='user']")
        addrs = [a.get("addr", "") for a in host.findall("address")]
        status = host.find("status")
        status_val = status.get("state", "unknown") if status is not None else "unknown"
        host_ip = addrs[0] if addrs else target
        reserved, reason = is_reserved_ip(host_ip)
        if reserved:
            host_str = (
                f"\n[Host] {host_ip} ⚠️ **dirección reservada ({reason}), el resultado de la prueba de red no representa el estado de seguridad del objetivo real**"
            )
        else:
            host_str = f"\n[Host] {host_ip}"
        if hostname is not None:
            host_str += f" ({hostname.get('name', '')})"
        host_str += f" — {status_val}"
        lines.append(host_str)

        for port in host.findall(".//port"):
            port_id = port.get("portid", "")
            proto = port.get("protocol", "tcp")
            port_state = port.find("state")
            svc = port.find("service")
            state_val = port_state.get("state", "unknown") if port_state is not None else "unknown"
            svc_name = svc.get("name", "") if svc is not None else ""
            svc_product = svc.get("product", "") if svc is not None else ""
            svc_version = svc.get("version", "") if svc is not None else ""
            lines.append(
                f"  {proto.upper():5} {port_id}/{'s' if svc is not None and svc.get('tunnel') == 'ssl' else ''} "
                f"{state_val:8}{svc_name:15}{(svc_product + ' ' + svc_version).rstrip()}"
            )
            for script in port.findall("script"):
                lines.append(f"    | {script.get('id', '')}: {script.get('output', '')[:120]}")

    runstats = root.find(".//runstats")
    if runstats is not None:
        finished = runstats.find("finished")
        if finished is not None:
            elapsed = finished.get("elapsed", "")
            summary = finished.get("summary", "")
            lines.append(f"\nTiempo de finalización: {elapsed}s | {summary}")
    return "\n".join(lines) or f"Escaneo nmap completado (sin salida): {target}"


def _resolve_python_execute_mode(agent: AgentContext) -> str:
    safety = getattr(agent.config, "safety", None)
    if safety is None:
        return "trusted-local"

    mode = str(getattr(safety, "python_execute_mode", "") or "").strip().lower()
    if not mode and getattr(safety, "python_execute_restricted", False):
        return "safe"
    if mode in {"safe", "lab", "trusted-local"}:
        return mode
    return "trusted-local"


def _validate_python_execute_mode(mode: str, code: str) -> str | None:
    patterns = SAFE_MODE_PATTERNS if mode == "safe" else LAB_MODE_PATTERNS if mode == "lab" else []
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return pattern
    return None


def _write_python_audit(
    agent: AgentContext,
    *,
    purpose: str,
    code: str,
    mode: str,
    outcome: str,
    blocked_reason: str = "",
) -> None:
    safety = getattr(agent.config, "safety", None)
    if safety is None or not getattr(safety, "python_execute_audit_enabled", True):
        return

    try:
        from datetime import datetime

        from vulnclaw.config.settings import PYTHON_EXECUTE_AUDIT_FILE, ensure_dirs

        ensure_dirs()
        record = {
            "timestamp": datetime.now().isoformat(),
            "target": getattr(getattr(agent, "session_state", None), "target", None),
            "mode": mode,
            "purpose": purpose,
            "outcome": outcome,
            "blocked_reason": blocked_reason,
            "code_preview": code[:300],
            "code_lines": code.count("\n") + 1,
        }
        with open(PYTHON_EXECUTE_AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        return


async def execute_python(agent: AgentContext, args: dict[str, Any]) -> str:
    code = args.get("code", "")
    purpose = args.get("purpose", "")
    if not code.strip():
        return "[!] Code is empty; nothing executed"

    url_matches = re.findall(r"https?://([a-zA-Z0-9._:-]+)(/[^\s'\"`]*)?", code)
    for raw_host, path in url_matches:
        # Strip the port before the scope check so an in-scope target referenced
        # with a port (e.g. localhost:3000) is not falsely flagged out of scope.
        # The fetch tool already compares against urlparse().hostname (no port);
        # this keeps python_execute consistent with that behavior.
        host = raw_host.split(":", 1)[0].lower()
        host_violation = enforce_host_path_constraints(
            agent,
            host=host,
            path=(path or "").rstrip("/"),
            target=host,
        )
        if host_violation:
            return host_violation

    safety = getattr(agent.config, "safety", None)
    if safety is None or not safety.enable_python_execute:
        return (
            "[!] python_execute is disabled. Set safety.enable_python_execute = true to enable it"
        )

    mode = _resolve_python_execute_mode(agent)
    max_lines = getattr(safety, "python_execute_max_lines", 50)
    if code.count("\n") + 1 > max_lines:
        _write_python_audit(
            agent,
            purpose=purpose,
            code=code,
            mode=mode,
            outcome="blocked",
            blocked_reason="max_lines",
        )
        return f"[!] Code exceeds the max line limit ({max_lines})"

    show_warning = getattr(safety, "python_execute_show_warning", True)
    warning_prefix = ""
    if show_warning:
        warning_prefix = (
            f"[!] Security warning: python_execute runs local Python code in {mode} mode.\n"
            "Review the code carefully before execution.\n"
            "---\n"
        )

    recon_keywords = ["recon", "crawl", "spider", "scan", "enum", "probe"]
    timeout_seconds = 60 if any(kw in purpose.lower() for kw in recon_keywords) else 30

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            _write_python_audit(
                agent,
                purpose=purpose,
                code=code,
                mode=mode,
                outcome="blocked",
                blocked_reason=pattern,
            )
            return f"[!] Code contains a blocked operation pattern: {pattern}"

    blocked_pattern = _validate_python_execute_mode(mode, code)
    if blocked_pattern:
        _write_python_audit(
            agent,
            purpose=purpose,
            code=code,
            mode=mode,
            outcome="blocked",
            blocked_reason=blocked_pattern,
        )
        if mode == "safe":
            return f"[!] safe mode blocked operation: {blocked_pattern}"
        return f"[!] lab mode blocked operation: {blocked_pattern}"

    max_output_chars = getattr(safety, "python_execute_max_output_chars", 8000)
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            preamble = (
                "import sys, json, re, os, base64, hashlib, itertools, collections, datetime, struct, binascii, textwrap\n"
                "try:\n    import requests\nexcept ImportError:\n    pass\n"
                "try:\n    from bs4 import BeautifulSoup\nexcept ImportError:\n    pass\n"
                "try:\n    from Crypto.Cipher import AES\nexcept ImportError:\n    pass\n\n"
            )
            f.write(preamble)
            f.write(code)
            tmp_path = f.name

        base_env = {"PYTHONIOENCODING": "utf-8"}
        env = {**os.environ, **base_env} if mode == "trusted-local" else base_env

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                cwd=tempfile.gettempdir(),
                env=env,
            ),
        )

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        output_parts: list[str] = []
        if result.stdout:
            output_parts.append(result.stdout)
        if result.stderr:
            stderr_lines = [
                line
                for line in result.stderr.splitlines()
                if "ImportError" not in line and "No module named" not in line
            ]
            if stderr_lines:
                output_parts.append("[stderr]\n" + "\n".join(stderr_lines))

        if not output_parts:
            _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="success")
            return f"{warning_prefix}[+] Python executed successfully with no output"

        output = "\n".join(output_parts)
        for sig in ["[DONE]", "[COMPLETE]"]:
            output = output.replace(sig, f"[BLOCKED_{sig[1:-1]}]")
        if len(output) > max_output_chars:
            clip = max_output_chars // 2
            output = output[:clip] + "\n...[truncated]...\n" + output[-clip:]
        _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="success")
        return f"{warning_prefix}[+] Python execution result ({mode}):\n{output}"
    except subprocess.TimeoutExpired:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        agent.runtime.python_timeout_rounds += 1
        _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="timeout")
        return f"[!] Python execution timed out after {timeout_seconds} seconds"
    except Exception as e:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        _write_python_audit(
            agent, purpose=purpose, code=code, mode=mode, outcome="error", blocked_reason=str(e)
        )
        return f"[!] Python execution error: {e}"


def _sync_cookies_to_shared_jar(
    agent: AgentContext, cookies: list[tuple[str, str, str, str]]
) -> None:
    """Copy session cookies into the agent's shared _fetch_cookies jar.

    This allows the ``fetch`` tool (which uses ``_fetch_cookies``) to
    immediately use the authenticated session obtained by
    ``brute_force_login`` without requiring a separate re-login.
    """
    if not agent or not cookies:
        return
    mcp = getattr(agent, "mcp_manager", None)
    if not mcp:
        return
    try:
        import httpx

        jar = getattr(mcp, "_fetch_cookies", None)
        if jar is None:
            jar = httpx.Cookies()
            mcp._fetch_cookies = jar
        for name, value, domain, path in cookies:
            if name and value:
                jar.set(name, value, domain=domain or "", path=path or "/")
    except Exception:
        pass


async def execute_brute_force(agent: AgentContext, args: dict[str, Any]) -> str:
    """Execute a login brute-force with automatic CSRF/session management.

    Handles the full flow in one call:
    GET login page → extract CSRF + session → POST passwords → detect result
    """
    import asyncio
    import re
    import time

    url = str(args.get("url", "") or "").strip()
    password_field = str(args.get("password_field", "") or "").strip()
    csrf_field = str(args.get("csrf_field", "") or "").strip()
    username_field = str(args.get("username_field", "") or "").strip()
    username = str(args.get("username", "") or "").strip()
    passwords = args.get("passwords", [])
    success_keyword = str(args.get("success_keyword", "") or "").strip()
    failure_keyword = str(args.get("failure_keyword", "") or "").strip()
    submit_action = str(args.get("submit_action", "") or "").strip()
    extra_data = args.get("extra_data", {}) or {}
    submit_url = submit_action or url

    if not url or not password_field or not passwords:
        return "[!] Faltan parámetros obligatorios: url, password_field, passwords"

    if not isinstance(passwords, list) or not passwords:
        return "[!] passwords debe ser una lista no vacía"

    passwords = passwords[:20]
    total = len(passwords)

    try:
        import httpx
    except ImportError:
        return "[!] httpx no está instalado, no se puede ejecutar la fuerza bruta"

    def extract_csrf(html: str, field_name: str) -> str | None:
        """Extract CSRF token from HTML input field."""
        if not field_name:
            return None
        pattern = re.compile(
            rf'name=["\']{re.escape(field_name)}["\'][^>]*value=["\']([^"\']+)',
            re.IGNORECASE,
        )
        m = pattern.search(html)
        if m:
            return m.group(1)
        # Try alternative: value before name
        pattern2 = re.compile(
            rf'value=["\']([^"\']+)[^>]*name=["\']{re.escape(field_name)}',
            re.IGNORECASE,
        )
        m = pattern2.search(html)
        return m.group(1) if m else None

    results: list[str] = []
    start_time = time.time()
    attempts = 0
    found_password: str | None = None

    # Collect cookies from the internal client so we can sync them
    # back to the shared _fetch_cookies jar after a successful login.
    session_cookies: list[tuple[str, str, str, str]] = []  # name, value, domain, path

    async with httpx.AsyncClient(
        verify=False,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        # Step 1: Get login page for initial CSRF and session
        try:
            resp = await asyncio.wait_for(
                client.get(url),
                timeout=30.0,
            )
            html = resp.text
        except Exception as e:
            return f"[!] Error al obtener la página de login: {e}"

        csrf_token = extract_csrf(html, csrf_field)
        if csrf_token is None and csrf_field:
            results.append(f"[!] Advertencia: no se encontró el campo CSRF '{csrf_field}' en la página de login")

        # Auto-detect submit button values from login page HTML.
        # Many forms (DVWA, etc.) check isset($_POST['SubmitButtonName'])
        # before processing authentication. Without the button's name=value,
        # the server skips auth and just re-renders the page.
        auto_fields: dict[str, str] = {}
        for input_match in re.finditer(
            r'<(?:input|button)\s[^>]*type=["\']submit["\'][^>]*>',
            html,
            re.IGNORECASE,
        ):
            tag = input_match.group()
            name_m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            val_m = re.search(r'value\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
            if name_m:
                auto_fields[name_m.group(1)] = val_m.group(1) if val_m else name_m.group(1)

        # Step 2: Try each password
        for i, password in enumerate(passwords, 1):
            form_data: dict[str, str] = {}
            if username_field and username:
                form_data[username_field] = username
            form_data[password_field] = password
            if csrf_token and csrf_field:
                form_data[csrf_field] = csrf_token
            # Auto-detected submit buttons come first so they can be
            # overridden by explicit extra_data if needed.
            form_data.update(auto_fields)
            form_data.update({k: str(v) for k, v in extra_data.items()})

            try:
                resp = await asyncio.wait_for(
                    client.post(submit_url, data=form_data),
                    timeout=30.0,
                )
                attempts += 1
                response_html = resp.text
                status = resp.status_code

                # Determine success or failure
                is_success = False
                reason = ""
                csrf_markers = ["csrf token is incorrect", "csrf token mismatch",
                                "token mismatch", "invalid token"]

                if success_keyword and success_keyword.lower() in response_html.lower():
                    is_success = True
                    reason = f"'{success_keyword}'"
                elif failure_keyword and failure_keyword.lower() in response_html.lower():
                    is_success = False
                    reason = f"'{failure_keyword}'"
                elif any(m in response_html.lower() for m in csrf_markers):
                    is_success = False
                    reason = "Token CSRF incorrecto (se sincronizó automáticamente el nuevo token)"
                elif status == 302:
                    is_success = True
                    reason = "Status 302 (redirect)"
                elif "logout" in response_html.lower() or "welcome" in response_html.lower():
                    is_success = True
                    reason = "Se detectó estado de sesión iniciada"
                else:
                    # Include a short snippet from the response so the model
                    # can diagnose what the server actually returned.
                    snippet = response_html.strip()[:200].replace("\n", " ")
                    is_success = False
                    reason = snippet

                prefix = "[✓]" if is_success else "[✗]"
                pw_preview = password[:40].replace("\n", "\\n")
                results.append(f"{prefix} {pw_preview} → {'éxito' if is_success else 'falló'} ({reason})")

                # Extract new CSRF from response for next attempt
                new_token = extract_csrf(response_html, csrf_field)
                if new_token:
                    csrf_token = new_token

                # Stop early on success if keyword matched
                if is_success and success_keyword:
                    found_password = password
                    break

            except Exception as e:
                pw_preview = password[:30].replace("\n", "\\n")
                results.append(f"[!] {pw_preview} → Solicitud fallida: {e}")
                continue

        # Save cookies from the internal client for potential sharing with
        # the fetch tool's cookie jar.
        try:
            for cookie in client.cookies.jar:
                session_cookies.append(
                    (cookie.name, cookie.value, cookie.domain, cookie.path)
                )
        except Exception:
            pass

    elapsed = time.time() - start_time

    # Sync session cookies to the shared _fetch_cookies jar so that
    # subsequent `fetch` calls from the agent are already authenticated.
    if found_password and session_cookies:
        _sync_cookies_to_shared_jar(agent, session_cookies)

    summary = [
        f"[+] Fuerza bruta completada — {url}",
        f"    Usuario: {username or '(no especificado)'}",
        "",
        "    Resultados:",
    ]
    for r in results:
        summary.append(f"    {r}")
    summary.append("")
    summary.append(f"    Tiempo: {elapsed:.1f}s")
    summary.append(f"    Intentos: {attempts}/{total}")

    return "\n".join(summary)
