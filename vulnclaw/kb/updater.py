"""VulnClaw Knowledge Updater — update and seed the knowledge base."""

from __future__ import annotations

from vulnclaw.kb.store import KnowledgeStore


def seed_knowledge_base(store: KnowledgeStore) -> None:
    """Seed the knowledge base with initial data.

    This populates the KB with essential security knowledge for MVP.
    """
    # ── CVE Entries ──────────────────────────────────────────────

    cves = [
        {
            "id": "CVE-2026-21858",
            "title": "n8n Arbitrary File Read via Public Form",
            "description": "n8n versions >= 1.65.0 and < 1.121.0 allow unauthenticated "
            "arbitrary file read through public form submission endpoints when "
            "a workflow contains a Form Ending node returning a binary file.",
            "severity": "Critical",
            "affected": "n8n >= 1.65.0, < 1.121.0",
            "tags": ["n8n", "file-read", "rce", "critical"],
            "exploitation_steps": [
                "Identify a public form path on the n8n instance",
                "Send POST request with forged files object containing filepath",
                "Read server files including /etc/passwd, config, database",
                "Extract encryption key from config",
                "Use extracted credentials to login",
                "Create malicious workflow with expression injection for RCE",
            ],
            "remediation": "Upgrade to n8n >= 1.121.0",
        },
        {
            "id": "CVE-2025-68613",
            "title": "n8n Authenticated Expression Injection RCE",
            "description": "Authenticated expression injection in n8n allows RCE via "
            "malicious workflow expressions.",
            "severity": "Critical",
            "affected": "n8n >= 0.211.0, < 1.120.4",
            "tags": ["n8n", "rce", "expression-injection", "critical"],
            "exploitation_steps": [
                "Login with valid credentials",
                "Create a workflow with manualTrigger + set node",
                "Insert expression payload: ={{ (function(){...execSync(cmd)...})() }}",
                "Run the workflow",
                "Read execution result for command output",
            ],
            "remediation": "Upgrade to n8n >= 1.120.4 or 1.121.1",
        },
    ]

    for cve in cves:
        existing = store.get_entry("cve", cve["id"])
        if not existing:
            store.add_entry("cve", cve["id"], cve)

    # ── Technique Entries ────────────────────────────────────────

    techniques = [
        {
            "id": "sqli-bypass",
            "title": "Técnicas de evasión para inyección SQL",
            "description": "Métodos de construcción de payloads de inyección SQL para evadir WAF",
            "tags": ["sqli", "waf-bypass", "web"],
            "bypass_methods": [
                "Mezcla de mayúsculas y minúsculas: SeLeCt",
                "Comentario en línea: S/*!ELECT*/",
                "Doble codificación: %2565",
                "Funciones equivalentes: GROUP_CONCAT en lugar de concat_ws",
            ],
        },
        {
            "id": "rce-bypass-php",
            "title": "Técnicas de evasión para ejecución de comandos en PHP",
            "description": "Construcción de payloads de ejecución de comandos para evadir WAF en PHP",
            "tags": ["rce", "waf-bypass", "php", "web"],
            "bypass_methods": [
                "Nombre de función codificado en Base64: $f=base64_decode('c3lzdGVt');$f('id');",
                "Concatenación de cadenas: $f='sys'.'tem';$f('id');",
                "División de rutas: '/va'.'r/ww'.'w/ht'.'ml'",
                "Cadena invertida: $f=strrev('metsys');$f('id');",
            ],
        },
        {
            "id": "xss-bypass",
            "title": "Técnicas de evasión para XSS",
            "description": "Construcción de payloads para evadir filtros WAF/XSS",
            "tags": ["xss", "waf-bypass", "web"],
            "bypass_methods": [
                "Manejador de eventos: <img src=x onerror=alert(1)>",
                "Etiqueta SVG: <svg onload=alert(1)>",
                "Codificación de entidades HTML",
                "Codificación Unicode",
            ],
        },
        {
            "id": "cmd-injection-bypass",
            "title": "Técnicas de evasión para inyección de comandos",
            "description": "Métodos para evadir filtros de inyección de comandos",
            "tags": ["command-injection", "waf-bypass", "web"],
            "bypass_methods": [
                "Salto de línea: id\\nwhoami",
                "Tubería (pipe): id|whoami",
                "Concatenación de variables: a=i;b=d;$a$b",
                "Comodines: /bin/ca? /etc/pas?d",
            ],
        },
    ]

    for tech in techniques:
        existing = store.get_entry("techniques", tech["id"])
        if not existing:
            store.add_entry("techniques", tech["id"], tech)

    # ── Tool Guides ──────────────────────────────────────────────

    tools = [
        {
            "id": "nmap",
            "title": "Referencia rápida de escaneo de puertos con Nmap",
            "description": "Comandos y parámetros de escaneo más usados de Nmap",
            "tags": ["nmap", "recon", "scanning"],
            "commands": [
                "nmap -sV -sC -p- TARGET    # Escaneo de todos los puertos + detección de versión",
                "nmap -sS -TOP_PORTS 1000 TARGET   # Escaneo SYN de los 1000 puertos principales",
                "nmap --script vuln TARGET   # Script de escaneo de vulnerabilidades",
                "nmap -sU -TOP_PORTS 100 TARGET     # Escaneo UDP",
            ],
        },
        {
            "id": "burp",
            "title": "Flujo de trabajo de Burp Suite",
            "description": "Flujo de trabajo de pentesting con Burp Suite",
            "tags": ["burp", "proxy", "web"],
            "workflow": [
                "Configurar el proxy del navegador → Burp",
                "Navegar por el sitio objetivo y recopilar solicitudes",
                "Analizar los parámetros y endpoints de las solicitudes",
                "Usar Intruder para pruebas de fuzzing",
                "Usar Repeater para verificar manualmente las vulnerabilidades",
            ],
        },
    ]

    for tool in tools:
        existing = store.get_entry("tools", tool["id"])
        if not existing:
            store.add_entry("tools", tool["id"], tool)
