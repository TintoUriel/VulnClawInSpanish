"""Recon dimension tracking helpers for AgentCore."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext


RECON_MIN_ROUNDS = 8  # Número mínimo de rondas en la fase de reconocimiento; por debajo de este número, [DONE] se ignora

# ★ Include BOTH tool-result signatures AND natural-language descriptions from notes/confirmed_facts
RECON_DIM_KEYWORDS: dict[str, list[str]] = {
    "server": [
        "puerto",
        "port",
        "nmap",
        "abierto",
        "open",
        "versión del servicio",
        "service",
        "ip real",
        "real ip",
        "cdn",
        "servidor origen",
        "sistema operativo",
        "detección de so",
        "ttl",
        "middleware",
        "middleware",
        "base de datos",
        "database",
        "mysql",
        "redis",
        "escaneo",
        "escaneo de puertos",
        "dirección ip",
        "detección de ip",
        "host activo",
        "apache",
        "nginx",
        "tomcat",
        "iis",
        "jetty",
        "sistema operativo",
        "linux",
        "windows",
        "ubuntu",
        "centos",
    ],
    "website": [
        "waf",
        "cortafuegos de aplicaciones web",
        "directorio sensible",
        "escaneo de directorios",
        "dirsearch",
        "gobuster",
        "filtración de código fuente",
        ".git",
        ".svn",
        ".ds_store",
        ".env",
        "archivo de respaldo",
        ".bak",
        "sitio vecino",
        "misma ip",
        "segmento c",
        "mismo segmento de red",
        "huella",
        "cms",
        "framework",
        "framework",
        "arquitectura",
        "pila tecnológica",
        "huella web",
        "sitio web",
        "web",
        "javascript",
        "archivo js",
        "endpoint api",
        "extremo de api",
        "cms",
        "wordpress",
        "dedecms",
        "phpcms",
        "discuz",
        "inicio de sesión",
        "panel de administración",
        "administración",
        "admin",
        "login",
        "página",
        "url",
        "directorio",
        "archivo",
    ],
    "domain": [
        "whois",
        "titular del registro",
        "registrador",
        "icp",
        "registro icp",
        "subdominio",
        "subdomain",
        "registro dns",
        "cname",
        "registro mx",
        "registro txt",
        "transparencia de certificados",
        "crt.sh",
        "información del certificado",
        "certificado ssl",
        "dominio",
        "dns",
        " registr",
        "información de registro",
        "registro icp",
        "subdominio",
        "subsitio",
        "crt.sh",
        "certificado",
    ],
    "personnel": [
        "github_id",
        "followers",
        "following",
        "public_repos",
        "unclecheng",
        "twitter",
        "ingeniería social",
        "ingeniería social",
        "información de personal",
        "seguimiento del autor",
        "perfil de persona",
    ],
}


def update_recon_dimension_completion(agent: AgentContext, response: str) -> None:
    """Auto-detect which recon dimensions have been explored.

    Uses signal-weighted sources instead of blindly scanning all round text.
    El parámetro response se conserva para mantener la compatibilidad con la
    firma de llamada existente, pero en la lógica no se utiliza el texto de
    razonamiento original.
    """
    note_text = " ".join(agent.context.state.notes[-15:]).lower()
    fact_text = " ".join(getattr(agent.context.state, "confirmed_facts", [])[-15:]).lower()
    step_text = " ".join(agent.context.state.executed_steps[-15:]).lower()

    for dim, keywords in RECON_DIM_KEYWORDS.items():
        if dim == "personnel":
            if not agent.context.state.recon_dimension4_active:
                continue
            source_text = fact_text
        else:
            source_text = f"{fact_text} {note_text} {step_text}"

        if not source_text.strip():
            continue

        if not agent.context.state.recon_dimensions_completed.get(dim, False):
            if any(kw.lower() in source_text for kw in keywords):
                agent.context.state.mark_recon_dimension(dim)
