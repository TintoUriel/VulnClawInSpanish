"""VulnClaw Skill Dispatcher — match user intents to appropriate Skills."""

from __future__ import annotations

from typing import Any, Optional

from vulnclaw.skills.loader import list_core_skills, list_specialized_skills, load_skill_by_name

# ── Intent → Skill mapping ─────────────────────────────────────────

SKILL_INTENT_MAP: dict[str, list[str]] = {
    # Core skills
    "prueba de penetración|pentest|flujo completo|hazme una prueba": ["pentest-flow"],
    "recopilación de información|reconocimiento|recon|escaneo de puertos|escanear puertos|subdominios": ["recon"],
    "descubrimiento de vulnerabilidades|escaneo de vulnerabilidades|vulnerability|qué vulnerabilidades hay": ["vuln-discovery"],
    "explotación de vulnerabilidades|exploit|poc|explotar vulnerabilidad": ["exploitation"],
    "post-explotación|post-exploitation": ["post-exploitation"],
    "informe|report|generar informe": ["reporting"],
    "evadir waf|bypass de waf|waf bypass": ["waf-bypass"],
    # Specialized skills — original
    "pentest web|prueba web|prueba de sitio web": ["web-pentest"],
    "android|apk|prueba de app": ["android-pentest"],
    # Specialized skills — from Sec-Skill
    "ingeniería inversa|reverse|recuperación de firma|replay en burp|firma js|ingeniería inversa de cliente|cadena de peticiones|replay|firma": ["client-reverse"],
    "captura de paquetes|packet|frida|jadx|hook|ssl pinning|scrcpy": ["client-reverse"],
    "firma de navegador|antiscraping|antibot|generación de token|redirección de cookie": ["client-reverse"],
    "web avanzado|inyección|inyección sql|xss|ssrf|ssti|xxe|inyección de comandos|deserialización|rce|ejecución remota de código": [
        "web-security-advanced"
    ],
    "cors|graphql|websocket|oauth|contrabando de peticiones|jwt|csrf|contaminación de prototipos": ["web-security-advanced"],
    "vulnerabilidad de autenticación|vulnerabilidad de lógica de negocio|control de acceso indebido|idor|lógica de pago|carga de archivos|recorrido de rutas": ["web-security-advanced"],
    "seguridad de ia|seguridad mcp|inyección de prompt|abuso de herramientas|seguridad de agentes|seguridad del modelo": ["ai-mcp-security"],
    "pentest de ia|seguridad de grandes modelos|seguridad llm|prompt injection|tool abuse": ["ai-mcp-security"],
    "envenenamiento de mcp|cadena de suministro de skills|escape de rol|fuga de datos|filtración de prompt": ["ai-mcp-security"],
    "pentest de red interna|movimiento lateral|escalada de privilegios|persistencia|túnel|proxy|pentest de dominio|ataque a ad": ["intranet-pentest-advanced"],
    "adcs|exchange|sharepoint|mimikatz|kerberoasting|dcsync|pth": ["intranet-pentest-advanced"],
    "robo de credenciales|bloodhound|frp|chisel|ligolo|evasión de amsi": ["intranet-pentest-advanced"],
    "herramientas|comandos|codificación|decodificación|reverse shell|ataque de contraseñas|hashcat": ["pentest-tools"],
    "sqlmap|nmap|nuclei|ffuf|burp|impacket|crackmapexec": ["pentest-tools"],
    "consulta rápida|payload|recordatorio de bypass|verificación rápida|checklist|lista de verificación": ["rapid-checklist"],
    "colección de payloads|evasión|bypass|búsqueda rápida|tarjeta de referencia rápida|recordatorio rápido": ["rapid-checklist"],
    # SecKnowledge: practical CTF/SRC/Web+AI security testing knowledge base
    "src|caza de vulnerabilidades|pruebas colaborativas|butian|edusrc|cnvd": ["secknowledge-skill"],
    "wooyun|xianzhi|l1-l4|gaarm|owasp wstg|owasp llm|owasp asi": ["secknowledge-skill"],
    "pruebas de seguridad prácticas|base de conocimiento de pruebas de seguridad|web+ai|seguridad web ia|pruebas de seguridad de aplicaciones de ia": [
        "secknowledge-skill"
    ],
    "ctf src|caza de vulnerabilidades ctf|pentest integral ctf|ctf ai|ctf mcp|ctf agent": ["secknowledge-skill"],
    # Crypto toolkit
    "codificación|decodificación|base64|base32|hex|codificación url|cifrado|descifrado|hash": ["crypto-toolkit"],
    "md5|sha|aes|des|rsa|jwt|rot13|caesar|morse|cifrado de valla": ["crypto-toolkit"],
    "decodificar base64|codificar base64|decodificar hex|decodificar url|decodificar unicode|decodificar html": ["crypto-toolkit"],
    "criptografía|crypto|cipher|decrypt|encrypt|encode|decode": ["crypto-toolkit"],
    "código morse|cifrado césar|vigenère|cifrado de bacon|base58": ["crypto-toolkit"],
    # ── CTF specialized skills ──────────────────────────────────────
    # ctf-web: base de conocimiento de ataques CTF Web
    "ctf|capturar la bandera|flag|comparación débil|evasión con espacios|evasión de regex|rce|auditoría de código|bypass de eval|highlight_file": ["ctf-web"],
    "0e|bypass de md5|bypass de preg_match|bypass de tipos|type juggling|tipado débil": ["ctf-web"],
    "salida visible|sin salida|blind rce|bypass de ejecución de comandos|auditoría de código php|inyección ssti": ["ctf-web"],
    # ctf-crypto: base de conocimiento de ataques criptográficos CTF
    "ataque rsa|exponente pequeño|ataque de módulo común|wiener|coppersmith|padding oracle": ["ctf-crypto"],
    "ataque ecc|subgrupo pequeño|logaritmo discreto|ecdsa|ed25519|pohlig-hellman": ["ctf-crypto"],
    "lfsr|lcg|prng|mt19937|predicción de números aleatorios|cifrado de flujo": ["ctf-crypto"],
    "lwe|ataque de retículos|lll|cvp|svp|reducción de base de retículo": ["ctf-crypto"],
    "cifrado clásico|vigenère|césar|valla|cifrado de sustitución|análisis de frecuencia": ["ctf-crypto"],
    # ctf-misc: base de conocimiento de misceláneos CTF
    "pyjail|sandbox de python|escape de jail|sandbox_escape|python jail": ["ctf-misc"],
    "bashjail|sandbox de bash|restricted shell|escape de rbash": ["ctf-misc"],
    "cadena de codificación|codificación multicapa|misceláneo|misc|esteganografía|stego": ["ctf-misc"],
    "ctfd|plataforma de ctf|envío de flag|descarga de retos": ["ctf-misc"],
    # ── OSINT specialized skill — refined routing ───────────────────
    # osint-recon: Full-dimension recon (OSINT + social engineering)
    # Triggered only when user explicitly mentions social engineering / OSINT / author tracking
    "ingeniería social|social engineering|rastreo de autor|rastreo de personas|perfil del objetivo|perfil de persona": ["osint-recon"],
    "multiplataforma|búsqueda de nombre de usuario|correlación de identidad|rastreo en github|rastreo en bilibili": ["osint-recon"],
    # Full/deep recon — trigger osint-recon for comprehensive 4-dimension collection
    "reconocimiento integral|reconocimiento profundo|recopilación completa de información|recopilación integral de información|recopilación profunda|recopilar información básica": ["osint-recon"],
}


class SkillDispatcher:
    """Dispatches user input to the most appropriate Skill.

    Kept as a thin compatibility layer over the deterministic
    :class:`~vulnclaw.skills.resolver.SkillResolver`: ``dispatch`` returns the
    resolver's primary skill for older callers, while :meth:`resolve` exposes
    the full :class:`~vulnclaw.skills.resolver.SkillSelection` bundle.
    """

    def resolve(self, user_input: str, **kwargs: Any) -> Any:
        """Resolve user input into a full :class:`SkillSelection` bundle."""
        from vulnclaw.skills.resolver import SkillQuery, SkillResolver

        query = SkillQuery.from_input(user_input, **kwargs)
        return SkillResolver().resolve(query)

    def dispatch(self, user_input: str) -> Optional[dict[str, Any]]:
        """Match user input to a Skill and load its primary.

        Args:
            user_input: Natural language input from the user.

        Returns:
            Loaded primary skill dict, or None if no skill matched (unrelated,
            non-security input no longer auto-injects ``pentest-flow``).
        """
        selection = self.resolve(user_input)
        if selection.primary:
            return load_skill_by_name(selection.primary)
        return None

    def list_all_skills(self) -> list[dict[str, str]]:
        """List all available skills with name and description."""
        skills = []
        for name in list_core_skills():
            skill = load_skill_by_name(name)
            if skill:
                skills.append(
                    {
                        "name": skill["name"],
                        "description": skill.get("description", ""),
                        "type": "core",
                        "format": skill.get("format", "flat"),
                        "references": str(len(skill.get("references", []))),
                    }
                )
        for name in list_specialized_skills():
            skill = load_skill_by_name(name)
            if skill:
                skills.append(
                    {
                        "name": skill["name"],
                        "description": skill.get("description", ""),
                        "type": "specialized",
                        "format": skill.get("format", "flat"),
                        "references": str(len(skill.get("references", []))),
                    }
                )
        return skills
