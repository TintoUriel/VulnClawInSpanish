"""VulnClaw Finding Similarity — lightweight semantic deduplication.

Deduplicación semántica de hallazgos de vulnerabilidades implementada en Python
puro, sin depender de ninguna biblioteca externa de NLP.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: Corrección V2 — se trasladó desde
         agent/finding_similarity.py a la capa de infraestructura config/,
         eliminando la dependencia de report/filter.py sobre agent/.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional
from urllib.parse import parse_qs, urlsplit

if TYPE_CHECKING:
    from vulnclaw.config.domain_models import VulnerabilityFinding


# ── Mapeo de normalización de tipos de vulnerabilidad ──────────────────────

# Alias -> tipo canónico. Las claves se normalizan a minúsculas y sin espacios.
_VULN_TYPE_ALIASES: dict[str, str] = {
    # Inyección SQL
    "sqli": "sql_injection",
    "sql注入": "sql_injection",
    "sql injection": "sql_injection",
    "blind sqli": "sql_injection",
    "盲注": "sql_injection",
    "注入漏洞": "sql_injection",
    "sql_injection": "sql_injection",
    # XSS
    "xss": "cross_site_scripting",
    "跨站脚本": "cross_site_scripting",
    "反射型xss": "cross_site_scripting",
    "存储型xss": "cross_site_scripting",
    "xss跨站脚本": "cross_site_scripting",
    "cross site scripting": "cross_site_scripting",
    "cross_site_scripting": "cross_site_scripting",
    # SSRF
    "ssrf": "server_side_request_forgery",
    "服务端请求伪造": "server_side_request_forgery",
    "server side request forgery": "server_side_request_forgery",
    "server_side_request_forgery": "server_side_request_forgery",
    # RCE
    "rce": "remote_code_execution",
    "命令执行": "remote_code_execution",
    "远程代码执行": "remote_code_execution",
    "命令注入": "remote_code_execution",
    "remote code execution": "remote_code_execution",
    "remote_code_execution": "remote_code_execution",
    # LFI / inclusión de archivos
    "lfi": "local_file_inclusion",
    "文件包含": "local_file_inclusion",
    "rfi": "local_file_inclusion",
    "路径遍历": "local_file_inclusion",
    "文件包含/遍历": "local_file_inclusion",
    "local file inclusion": "local_file_inclusion",
    "local_file_inclusion": "local_file_inclusion",
    # IDOR / control de acceso indebido
    "idor": "insecure_direct_object_reference",
    "越权": "insecure_direct_object_reference",
    "横向越权": "insecure_direct_object_reference",
    "纵向越权": "insecure_direct_object_reference",
    "insecure direct object reference": "insecure_direct_object_reference",
    "insecure_direct_object_reference": "insecure_direct_object_reference",
    # CSRF
    "csrf": "cross_site_request_forgery",
    "跨站请求伪造": "cross_site_request_forgery",
    "cross site request forgery": "cross_site_request_forgery",
    # Bypass de autenticación
    "认证绕过": "auth_bypass",
    "未授权": "auth_bypass",
    "未授权访问": "auth_bypass",
    "未认证": "auth_bypass",
    "无需认证": "auth_bypass",
    # Fuga de información
    "信息泄露": "info_disclosure",
    "数据泄露": "info_disclosure",
    "敏感信息泄露": "info_disclosure",
    "info disclosure": "info_disclosure",
}


def normalize_vuln_type(vuln_type: str) -> str:
    """Normaliza el tipo de vulnerabilidad, mapeando alias comunes al nombre canónico.

    Args:
        vuln_type: Cadena de tipo de vulnerabilidad original (cualquier
            combinación de mayúsculas/minúsculas, chino/inglés, con espacios).

    Returns:
        El tipo normalizado; si no hay ningún alias coincidente, devuelve el
        valor original en minúsculas y sin espacios.
    """
    if not vuln_type:
        return ""
    key = re.sub(r"\s+", " ", vuln_type.strip().lower())
    if key in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[key]
    # Intentar coincidencia intercambiando guion bajo/espacio
    underscore = key.replace(" ", "_")
    if underscore in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[underscore]
    spaced = key.replace("_", " ")
    if spaced in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[spaced]
    return underscore


# ── Normalización de texto y similitud ──────────────────────────────────

_URL_RE = re.compile(r'https?://[^\s<>"\')\]]+', re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z0-9一-鿿]+", re.IGNORECASE)
# Las marcas delimitadoras (como [自动], [已确认]) deben eliminarse antes de
# tokenizar, para no contaminar el conjunto de palabras
_NOISE_TAGS = ("[自动]", "[已确认]", "[未验证]")


def _normalize_url_path(url: str) -> str:
    """Normaliza la URL: elimina el scheme, la barra final, conserva host+path."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.lower()
    host = (parts.hostname or "").lower()
    path = parts.path or ""
    if len(path) > 1:
        path = path.rstrip("/")
    return f"{host}{path}"


def normalize_text(text: str) -> str:
    """Normaliza el texto: minúsculas, unifica espacios, estandariza rutas de URL incrustadas.

    Args:
        text: Cualquier texto libre (descripción/evidencia/título).

    Returns:
        El texto normalizado.
    """
    if not text:
        return ""
    result = text
    for tag in _NOISE_TAGS:
        result = result.replace(tag, " ")
    # Sustituir las URL incrustadas por su forma normalizada host+path
    result = _URL_RE.sub(lambda m: _normalize_url_path(m.group(0)), result)
    result = result.lower()
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _tokenize(text: str) -> set[str]:
    """Divide el texto normalizado en un conjunto de palabras."""
    return set(_TOKEN_RE.findall(text))


def text_similarity(a: str, b: str) -> float:
    """Similitud de Jaccard basada en conjuntos de palabras.

    Args:
        a: Texto A.
        b: Texto B.

    Returns:
        Similitud entre [0.0, 1.0]. Si ambos están vacíos devuelve 1.0;
        si solo uno está vacío devuelve 0.0.
    """
    na, nb = normalize_text(a), normalize_text(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    ta, tb = _tokenize(na), _tokenize(nb)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def url_similarity(a: str, b: str) -> float:
    """Compara la similitud de host / path / parámetros de query entre dos URL.

    Pesos: host 0.3 + path 0.4 + conjunto de nombres de parámetros de query 0.3.
    Para cadenas que no son URL, recurre a la similitud de Jaccard sobre el texto original.

    Args:
        a: URL o cadena de ubicación A.
        b: URL o cadena de ubicación B.

    Returns:
        Similitud entre [0.0, 1.0].
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    pa, pb = urlsplit(a.strip()), urlsplit(b.strip())
    # Si ninguna de las dos parece una URL (sin scheme, sin netloc ni separador de path), comparar como texto
    if not (pa.scheme or pa.netloc) and not (pb.scheme or pb.netloc):
        return text_similarity(a, b)

    # Comparación de host
    ha, hb = (pa.hostname or "").lower(), (pb.hostname or "").lower()
    if not ha and not hb:
        host_sim = 1.0
    elif not ha or not hb:
        host_sim = 0.0
    else:
        host_sim = 1.0 if ha == hb else 0.0

    # Comparación de path: Jaccard por segmentos separados por "/"
    seg_a = {s for s in pa.path.split("/") if s}
    seg_b = {s for s in pb.path.split("/") if s}
    if not seg_a and not seg_b:
        path_sim = 1.0
    elif not seg_a or not seg_b:
        path_sim = 0.0
    else:
        path_sim = len(seg_a & seg_b) / len(seg_a | seg_b)

    # Comparación del conjunto de nombres de parámetros de query (se ignora el
    # valor concreto; distintas paginaciones/ID se consideran el mismo endpoint)
    qa = set(parse_qs(pa.query).keys())
    qb = set(parse_qs(pb.query).keys())
    if not qa and not qb:
        query_sim = 1.0
    elif not qa or not qb:
        query_sim = 0.0
    else:
        query_sim = len(qa & qb) / len(qa | qb)

    return host_sim * 0.3 + path_sim * 0.4 + query_sim * 0.3


# ── Similitud combinada de findings ─────────────────────────────────────

_LOCATION_RE = re.compile(r'(?:https?://[^\s<>"\')\]]+)|(?:/[\w%&=?\-./]+)')


def _extract_location(finding: "VulnerabilityFinding") -> str:
    """Extrae la primera URL o ruta de evidence/description del finding como ubicación."""
    for field in (finding.evidence or "", finding.description or ""):
        if not field:
            continue
        m = _LOCATION_RE.search(field)
        if m:
            return m.group(0)
    return ""


def _vuln_type_similarity(a: str, b: str) -> float:
    """Similitud de tipo de vulnerabilidad: coincidencia exacta 1.0, coincidencia normalizada 0.8, en otro caso 0.0."""
    ra, rb = (a or "").strip().lower(), (b or "").strip().lower()
    if ra and rb and ra == rb:
        return 1.0
    na, nb = normalize_vuln_type(a), normalize_vuln_type(b)
    if na and nb and na == nb:
        return 0.8
    return 0.0


def finding_similarity(a: "VulnerabilityFinding", b: "VulnerabilityFinding") -> float:
    """Compara de forma combinada la similitud entre dos hallazgos de vulnerabilidad.

    Pesos por dimensión:
        - vuln_type:    0.3 (coincidencia exacta 1.0 / coincidencia normalizada 0.8)
        - location/URL: 0.4 (extraído de evidence/description y comparado con url_similarity)
        - description:  0.3 (Jaccard textual de título + descripción)

    Args:
        a: Hallazgo de vulnerabilidad A.
        b: Hallazgo de vulnerabilidad B.

    Returns:
        Similitud combinada entre [0.0, 1.0].
    """
    type_sim = _vuln_type_similarity(a.vuln_type, b.vuln_type)

    loc_a, loc_b = _extract_location(a), _extract_location(b)
    if not loc_a and not loc_b:
        # Ninguno de los dos tiene una ubicación clara — esta dimensión no es
        # comparable, se considera neutral (no suma ni resta)
        loc_sim = 0.5
    else:
        loc_sim = url_similarity(loc_a, loc_b)

    desc_a = f"{a.title} {a.description}".strip()
    desc_b = f"{b.title} {b.description}".strip()
    desc_sim = text_similarity(desc_a, desc_b)

    return type_sim * 0.3 + loc_sim * 0.4 + desc_sim * 0.3


# ── Comparación de solidez de evidencia y deduplicación ─────────────────

_EVIDENCE_LEVEL_RANK = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}
_LIFECYCLE_RANK = {
    "rejected": 0,
    "candidate": 1,
    "pending_verification": 2,
    "needs_manual_review": 3,
    "verified": 4,
}


def _evidence_strength(finding: "VulnerabilityFinding") -> tuple:
    """Calcula la solidez de la evidencia del finding, para decidir cuál conservar en caso de duplicado.

    Clave de ordenación (a mayor valor, más sólido):
        1. Prioridad a los ya verificados (verified=True)
        2. Nivel del ciclo de vida
        3. Nivel de evidencia L1-L4
        4. Longitud del texto de evidence (evidencia más detallada)
    """
    return (
        1 if finding.verified else 0,
        _LIFECYCLE_RANK.get(finding.lifecycle_status, 1),
        _EVIDENCE_LEVEL_RANK.get(finding.evidence_level, 1),
        len(finding.evidence or ""),
    )


def deduplicate_findings(
    findings: list["VulnerabilityFinding"], threshold: float = 0.75
) -> list["VulnerabilityFinding"]:
    """Deduplica semánticamente la lista de hallazgos, conservando el de evidencia más sólida.

    Recorre findings comparando cada nuevo finding con los ya conservados;
    si la similitud supera el umbral se considera duplicado y se conserva
    el que tenga la evidencia más sólida.

    Args:
        findings: Lista original de hallazgos de vulnerabilidad.
        threshold: Umbral de similitud, por defecto 0.75.

    Returns:
        La lista deduplicada, manteniendo el orden relativo de la primera aparición.
    """
    kept: list["VulnerabilityFinding"] = []
    for cand in findings:
        dup_index: Optional[int] = None
        for idx, existing in enumerate(kept):
            if finding_similarity(cand, existing) >= threshold:
                dup_index = idx
                break
        if dup_index is None:
            kept.append(cand)
            continue
        # Duplicado detectado: conservar el de evidencia más sólida
        if _evidence_strength(cand) > _evidence_strength(kept[dup_index]):
            kept[dup_index] = cand
    return kept
