"""OpenAI tool schema definitions for built-in tools.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: Corrección S5 — Se extrajo el código de construcción
         del esquema de herramientas de builtin_tools.py (1357 líneas) a un
         módulo independiente, separando la lógica de ejecución de la
         definición del esquema para mejorar la mantenibilidad.
"""

from __future__ import annotations

from typing import Any

from vulnclaw.intel.tools import intel_tool_schemas


def build_openai_tools(mcp_manager: Any) -> list[dict[str, Any]]:
    """Build OpenAI function calling schema from MCP tools + built-in tools."""
    tools: list[dict[str, Any]] = []

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "load_skill_reference",
                "description": "Carga el documento de referencia del Skill especificado para obtener metodologías detalladas de pentesting, flujos de trabajo o referencias de comandos. Cuando el mensaje del sistema mencione 'documentación de referencia disponible', usa esta herramienta para obtener el contenido específico.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Nombre del Skill, como client-reverse, web-security-advanced, ai-mcp-security, intranet-pentest-advanced, pentest-tools, rapid-checklist, crypto-toolkit, ctf-web, ctf-crypto, ctf-misc, osint-recon, secknowledge-skill",
                        },
                        "reference_name": {
                            "type": "string",
                            "description": "Nombre del archivo de documentación de referencia, como 02-client-api-reverse-and-burp.md, web-injection.md, encoding-cheatsheet.md",
                        },
                    },
                    "required": ["skill_name", "reference_name"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "python_execute",
                "description": (
                    "Ejecuta fragmentos de código Python. Se usa para: construir solicitudes "
                    "HTTP complejas y analizar respuestas, realizar conversiones de "
                    "codificación y procesamiento de datos, probar diferentes payloads en "
                    "lote, comparar diferencias de respuesta, realizar cálculos matemáticos, "
                    "etc. El código se ejecuta en un entorno restringido, con un tiempo "
                    "límite de 30 segundos. Bibliotecas preinstaladas: requests, "
                    "beautifulsoup4, pycryptodome, base64, json, re, entre otras. "
                    "Importante: al construir solicitudes HTTP, usa esta herramienta en "
                    "lugar de adivinar el contenido de la respuesta."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Código Python a ejecutar. Admite múltiples líneas, se pueden importar bibliotecas estándar y requests/bs4, entre otras.",
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

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "crypto_decode",
                "description": (
                    "Herramienta de codificación/decodificación y cifrado/descifrado. Úsala "
                    "cuando encuentres cadenas codificadas en base64/hex/URL/HTML/Unicode, "
                    "necesites calcular hashes, descifrar AES/DES, analizar JWT, etc. "
                    "Importante: no inventes el resultado de la decodificación por tu "
                    "cuenta; usa siempre esta herramienta para garantizar la precisión. "
                    "Operaciones admitidas: base64_encode/decode, base32_encode/decode, base58_encode/decode, "
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
                            "description": "Cadena de entrada a procesar (texto a codificar/decodificar/calcular hash/cifrar)",
                        },
                        "key": {
                            "type": "string",
                            "description": "Clave de cifrado/descifrado (necesaria para AES/DES, 16/24/32 bytes)",
                        },
                        "iv": {"type": "string", "description": "Vector de inicialización AES (16 bytes, opcional)"},
                        "shift": {
                            "type": "integer",
                            "description": "Desplazamiento del cifrado César (por defecto 3; si no se proporciona al decodificar, se prueban todos los desplazamientos por fuerza bruta)",
                        },
                        "secret": {"type": "string", "description": "Clave de firma JWT"},
                    },
                    "required": ["operation", "input"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "nmap_scan",
                "description": (
                    "Herramienta de escaneo de puertos de red nmap. Se usa durante el "
                    "reconocimiento para descubrir puertos abiertos, versiones de "
                    "servicios y huellas del sistema operativo del objetivo.\n"
                    "Ejemplos de uso:\n"
                    "  Escanear puertos comunes: scan_type=top_ports, target=1.2.3.4\n"
                    "  Escaneo SYN: scan_type=syn, target=1.2.3.4 (requiere privilegios de administrador)\n"
                    "  Detección de versión de servicio: scan_type=service, target=1.2.3.4\n"
                    "  Escaneo de vulnerabilidades: scan_type=vuln, target=1.2.3.4\n"
                    "  Escaneo completo: scan_type=full, target=1.2.3.4\n"
                    "Prioriza nmap_scan sobre construir un escaneo de sockets con python_execute; nmap es más profesional y preciso."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Dirección IP o dominio objetivo (obligatorio), como 192.168.1.1 o scanme.nmap.org",
                        },
                        "scan_type": {
                            "type": "string",
                            "description": "Tipo de escaneo: top_ports/syn/tcp/service/os/vuln/full",
                        },
                        "ports": {
                            "type": "string",
                            "description": "Puertos o rango específico (opcional), como 80,443,8080 o 1-1000",
                        },
                        "timing": {
                            "type": "integer",
                            "description": "Plantilla de velocidad de escaneo 0-5 (por defecto 4); cuanto mayor el número, más rápido pero más fácil de detectar",
                        },
                        "profile": {
                            "type": "string",
                            "description": "Perfil de escaneo de red opcional: adaptive/fast/thorough/stealth. El perfil ajusta de forma conjunta los puertos, la velocidad, la detección de servicios y los scripts de seguridad.",
                        },
                    },
                    "required": ["target"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "brute_force_login",
                "description": (
                    "Realiza ataques de fuerza bruta de contraseñas contra formularios de "
                    "inicio de sesión. Gestiona automáticamente la Session Cookie, extrae "
                    "y actualiza el CSRF Token, y determina si el inicio de sesión fue "
                    "exitoso o fallido. Completa todos los intentos de contraseña en una "
                    "sola llamada y devuelve el resultado de cada una."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL de la página de inicio de sesión",
                        },
                        "username_field": {
                            "type": "string",
                            "description": "Nombre del campo de usuario, como 'username'",
                        },
                        "password_field": {
                            "type": "string",
                            "description": "Nombre del campo de contraseña, como 'password'",
                        },
                        "csrf_field": {
                            "type": "string",
                            "description": "Nombre del campo del token CSRF, como 'user_token'",
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
                            "description": "Palabra característica que aparece en la página tras un inicio de sesión exitoso, como 'Welcome' o 'Dashboard'",
                        },
                        "failure_keyword": {
                            "type": "string",
                            "description": "Palabra característica que aparece en la página tras un inicio de sesión fallido, como 'Login failed'",
                        },
                        "submit_action": {
                            "type": "string",
                            "description": "URL de destino del envío del formulario (opcional; si no se especifica, se extrae del atributo action del formulario)",
                        },
                        "extra_data": {
                            "type": "object",
                            "description": "Campos adicionales del formulario, como {\"Login\": \"Login\"}",
                        },
                    },
                    "required": ["url", "password_field", "passwords"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "space_search",
                "description": (
                    "Búsqueda de activos mediante motores de cartografía de ciberespacio "
                    "(FOFA/Hunter/Quake/Shodan/ZoomEye/0.zone Lingling Xin'an). Se usa en "
                    "la fase de reconocimiento para descubrir de forma pasiva activos "
                    "objetivo, IPs, puertos, subdominios, títulos y huellas de "
                    "componentes, sin contactar directamente al objetivo. Al proporcionar "
                    "domain, construye automáticamente la consulta de dominio según la "
                    "sintaxis de cada motor; también admite pasar la sintaxis de consulta "
                    "completa. Cuando engine=all, consulta en paralelo todos los motores "
                    "con clave configurada."
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
                            "description": "Sintaxis de consulta nativa del motor, como 'domain=\"x.com\"', 'app=\"Struts2\"' (opcional)",
                        },
                        "domain": {
                            "type": "string",
                            "description": "Dominio principal objetivo; construye automáticamente la consulta de dominio de cada motor (se usa cuando no se proporciona query)",
                        },
                        "size": {"type": "integer", "description": "Número de resultados a devolver, por defecto 100"},
                    },
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "subdomain_enum",
                "description": (
                    "Enumeración de subdominios. Primero agrega de forma pasiva usando los "
                    "motores de cartografía de ciberespacio configurados, luego realiza "
                    "fuerza bruta de resolución DNS con un pequeño diccionario incorporado, "
                    "y devuelve una lista deduplicada de subdominios activos. Prioriza esta "
                    "herramienta sobre escribir la fuerza bruta manualmente con python_execute."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Dominio principal, como nju.edu.cn"},
                        "brute": {
                            "type": "boolean",
                            "description": "Si se habilita la fuerza bruta DNS con el diccionario incorporado (por defecto true)",
                        },
                    },
                    "required": ["domain"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "js_recon",
                "description": (
                    "Reconocimiento de información en JS (basado en URLFinder). Rastrea la "
                    "página objetivo y todos los archivos .js que referencia, extrayendo "
                    "interfaces/rutas de API, dominios relacionados, URLs absolutas y "
                    "posibles claves codificadas en el código (AK/SK, tokens, JWT, claves "
                    "privadas, etc.). Por defecto auto_probe=true: realiza automáticamente "
                    "pruebas de acceso no autorizado en cada interfaz del mismo origen "
                    "recopilada (solo GET seguros, omitiendo interfaces destructivas). Debe "
                    "llamarse con prioridad durante la fase de reconocimiento, usando los "
                    "endpoints realmente extraídos para alimentar las pruebas posteriores, "
                    "en lugar de adivinar interfaces."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL de la página objetivo"},
                        "max_js": {
                            "type": "integer",
                            "description": "Número máximo de archivos JS a rastrear (por defecto 30)",
                        },
                        "auto_probe": {
                            "type": "boolean",
                            "description": "Si se realiza automáticamente la prueba de acceso no autorizado en las interfaces recopiladas (por defecto true)",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "Cabecera de autenticación opcional para comparación diferencial, como 'Authorization: Bearer xxx', para verificar si también se pueden obtener datos sin token",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "unauth_test",
                "description": (
                    "Prueba de acceso no autorizado. Envía solicitudes sin credenciales a "
                    "un conjunto de interfaces (normalmente endpoints recopilados por "
                    "js_recon) una por una, y determina el resultado según el código de "
                    "estado/cuerpo de respuesta/tipo de contenido: ⚠posible acceso no "
                    "autorizado (devuelve datos) / ✓bloqueado por autenticación / "
                    "↪redirige al inicio de sesión / —no existe. Si se proporciona "
                    "auth_header, realiza una comparación diferencial con/sin token; si "
                    "sin token se obtienen los mismos datos, se determina 🔴acceso no "
                    "autorizado confirmado. Mantiene estrictamente la separación entre "
                    "lectura y escritura: solo envía GET seguros, omite automáticamente "
                    "interfaces destructivas como delete/update/sms, y no recorre IDs en lote."
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
                            "description": "Cabecera de autenticación opcional para comparación diferencial, como 'Authorization: Bearer xxx' o 'Cookie: session=...'",
                        },
                        "max_endpoints": {
                            "type": "integer",
                            "description": "Número máximo de interfaces a probar (por defecto 60)",
                        },
                    },
                    "required": ["base_url", "endpoints"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "dir_enum",
                "description": (
                    "Enumeración de directorios/archivos (basado en dirsearch). Fuerza "
                    "bruta concurrente con diccionario, con línea base 404 incorporada e "
                    "identificación global de respuestas falsas (si una ruta aleatoria "
                    "devuelve 200, se determina como falsa y se detiene), además de "
                    "filtrado por código de estado y longitud de respuesta. Solo realiza "
                    "pruebas GET seguras, sin tocar rutas destructivas como delete/update."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL base del objetivo, como https://x.com/"},
                        "extensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Expansión de extensiones, como ['php','jsp','bak','zip'] (opcional)",
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

    tools.extend(intel_tool_schemas())

    if mcp_manager:
        for schema in mcp_manager.get_tool_schemas():
            tools.append(
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
