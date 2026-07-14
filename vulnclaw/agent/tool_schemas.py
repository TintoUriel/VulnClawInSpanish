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
                    "编码解码与加解密工具。遇到 base64/hex/URL/HTML/Unicode 编码字符串、"
                    "需要计算哈希、解密 AES/DES、解析 JWT 等场景时调用此工具。"
                    "重要：不要自行脑补解码结果，始终使用此工具确保准确性。"
                    "支持操作：base64_encode/decode, base32_encode/decode, base58_encode/decode, "
                    "hex_encode/decode, url_encode/decode, html_encode/decode, unicode_encode/decode, "
                    "rot13_encode/decode, caesar_encode/decode, morse_encode/decode, "
                    "md5_hash, sha1_hash, sha256_hash, sha512_hash, "
                    "aes_encrypt/decrypt, jwt_decode/encode, auto_decode"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "description": "操作名称"},
                        "input": {
                            "type": "string",
                            "description": "待处理的输入字符串（待编码/解码/哈希/加密的文本）",
                        },
                        "key": {
                            "type": "string",
                            "description": "加密/解密密钥（AES/DES 需要，16/24/32字节）",
                        },
                        "iv": {"type": "string", "description": "AES 初始化向量（16字节，可选）"},
                        "shift": {
                            "type": "integer",
                            "description": "Caesar 密码位移量（默认3，解码时不提供则暴力所有位移）",
                        },
                        "secret": {"type": "string", "description": "JWT 签名密钥"},
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
                    "nmap 网络端口扫描工具。信息收集时用于发现目标开放端口、服务版本和操作系统指纹。\n"
                    "用法示例：\n"
                    "  扫描常见端口: scan_type=top_ports, target=1.2.3.4\n"
                    "  SYN扫描: scan_type=syn, target=1.2.3.4（需要管理员权限）\n"
                    "  服务版本检测: scan_type=service, target=1.2.3.4\n"
                    "  漏洞扫描: scan_type=vuln, target=1.2.3.4\n"
                    "  全量扫描: scan_type=full, target=1.2.3.4\n"
                    "优先使用 nmap_scan 而非 python_execute 构造 socket 扫描，nmap 更专业更准确。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "目标 IP 地址或域名（必填），如 192.168.1.1 或 scanme.nmap.org",
                        },
                        "scan_type": {
                            "type": "string",
                            "description": "扫描类型：top_ports/syn/tcp/service/os/vuln/full",
                        },
                        "ports": {
                            "type": "string",
                            "description": "指定端口或范围（可选），如 80,443,8080 或 1-1000",
                        },
                        "timing": {
                            "type": "integer",
                            "description": "扫描速度模板 0-5（默认4），数字越大越快但越容易被检测",
                        },
                        "profile": {
                            "type": "string",
                            "description": "可选网络扫描画像：adaptive/fast/thorough/stealth。画像会联动调整端口、速度、服务探测与安全脚本。",
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
                    "对登录表单进行密码爆破。自动管理 Session Cookie、"
                    "自动提取和更新 CSRF Token、判断登录成功/失败。"
                    "单次调用内完成所有密码尝试，返回每个密码的结果。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "登录页面 URL",
                        },
                        "username_field": {
                            "type": "string",
                            "description": "用户名字段名，如 'username'",
                        },
                        "password_field": {
                            "type": "string",
                            "description": "密码字段名，如 'password'",
                        },
                        "csrf_field": {
                            "type": "string",
                            "description": "CSRF token 字段名，如 'user_token'",
                        },
                        "username": {
                            "type": "string",
                            "description": "要爆破的用户名",
                        },
                        "passwords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "要尝试的密码列表（最多 20 个）",
                        },
                        "success_keyword": {
                            "type": "string",
                            "description": "登录成功后页面出现的特征词，如 'Welcome'、'Dashboard'",
                        },
                        "failure_keyword": {
                            "type": "string",
                            "description": "登录失败后页面出现的特征词，如 'Login failed'",
                        },
                        "submit_action": {
                            "type": "string",
                            "description": "表单提交的目标 URL（可选，不指定则从表单 action 属性提取）",
                        },
                        "extra_data": {
                            "type": "object",
                            "description": "额外表单字段，如 {\"Login\": \"Login\"}",
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
                    "空间测绘资产搜索（FOFA/Hunter/Quake/Shodan/ZoomEye/0.zone 零零信安）。"
                    "信息收集阶段用于被动发现目标资产、IP、端口、子域、标题、组件指纹，不直接接触目标。"
                    "给 domain 自动按各引擎语法构造 domain 查询；也可传完整 query 语法。"
                    "engine=all 时并发查询所有已配置 key 的引擎。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "engine": {
                            "type": "string",
                            "description": "fofa/hunter/quake/shodan/zoomeye/zerozone/all，默认 fofa",
                        },
                        "query": {
                            "type": "string",
                            "description": "引擎原生查询语法，如 'domain=\"x.com\"'、'app=\"Struts2\"'（可选）",
                        },
                        "domain": {
                            "type": "string",
                            "description": "目标主域名，自动构造各引擎 domain 查询（query 未给时使用）",
                        },
                        "size": {"type": "integer", "description": "返回条数，默认 100"},
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
                    "子域名枚举。先用已配置的空间测绘引擎被动聚合，再用内置小字典做 DNS 解析爆破，"
                    "返回去重后的存活子域名列表。优先于 python_execute 自己写爆破。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "主域名，如 nju.edu.cn"},
                        "brute": {
                            "type": "boolean",
                            "description": "是否启用内置字典 DNS 爆破（默认 true）",
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
                    "JS 信息收集（参考 URLFinder）。抓取目标页面及其引用的全部 .js 文件，"
                    "提取 API 接口/路径、关联域名、绝对 URL，以及疑似硬编码密钥（AK/SK、token、JWT、私钥等）。"
                    "默认 auto_probe=true：自动对收集到的同源接口逐个做未授权访问探测（仅安全 GET，跳过破坏性接口）。"
                    "信息收集阶段优先调用，用真实提取的端点反哺后续测试，而非凭空猜接口。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "目标页面 URL"},
                        "max_js": {
                            "type": "integer",
                            "description": "最多抓取的 JS 文件数（默认 30）",
                        },
                        "auto_probe": {
                            "type": "boolean",
                            "description": "是否自动对收集到的接口做未授权探测（默认 true）",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "可选鉴权头做差分对比，如 'Authorization: Bearer xxx'，验证无 token 是否也能拿到数据",
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
                    "未授权访问探测。对一批接口（通常来自 js_recon 收集的端点）逐个无凭据请求，"
                    "按状态码/响应体/内容类型判定：⚠疑似未授权(返回数据) / ✓已鉴权拦截 / ↪跳转登录 / —不存在。"
                    "提供 auth_header 时做有/无 token 差分对比，无 token 也能拿到同样数据则判定 🔴未授权确认。"
                    "严守读写分离：仅发安全 GET，自动跳过 delete/update/sms 等破坏性接口，不批量遍历 ID。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base_url": {"type": "string", "description": "目标基础 URL（确定同源范围）"},
                        "endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "待测接口路径/URL 列表（来自 js_recon 的接口/路径）",
                        },
                        "auth_header": {
                            "type": "string",
                            "description": "可选鉴权头做差分，如 'Authorization: Bearer xxx' 或 'Cookie: session=...'",
                        },
                        "max_endpoints": {
                            "type": "integer",
                            "description": "最多探测的接口数（默认 60）",
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
                    "目录/文件枚举（参考 dirsearch）。并发字典爆破，自带 404 基线与全局伪装响应识别"
                    "（随机路径返回 200 即判定伪装并停止）、状态码与响应长度过滤。"
                    "仅做安全的 GET 探测，不碰 delete/update 等破坏性路径。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "目标基础 URL，如 https://x.com/"},
                        "extensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "扩展名展开，如 ['php','jsp','bak','zip']（可选）",
                        },
                        "wordlist": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "追加的自定义路径（基于命名规律的启发式字典，可选）",
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
