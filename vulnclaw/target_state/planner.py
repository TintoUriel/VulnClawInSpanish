from __future__ import annotations

from datetime import datetime
from typing import Any

# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de modificación: Eliminación de infracción V3 — los tipos hoja se movieron a config/domain_models.py.
from vulnclaw.config.domain_models import PentestPhase


def build_resume_plan(raw: dict[str, Any]) -> dict[str, Any]:
    """Build a structured resume plan from target state."""
    findings = raw.get("findings", [])
    finding_meta = raw.get("finding_meta", {})
    recon_dims = raw.get("recon_dimensions_completed", {}) or {}
    recon_meta = raw.get("recon_meta", {}) or {}
    runtime_meta = raw.get("runtime_meta", {}) or {}
    violation_events = raw.get("constraint_violation_events", []) or []

    blocked_targets = sorted(runtime_meta.get("blocked_targets", []))
    failed_targets = runtime_meta.get("failed_targets", {}) or {}
    failed_steps = runtime_meta.get("failed_steps", []) or []
    low_value_rounds = int(runtime_meta.get("rounds_without_progress", 0) or 0)
    current_attack_path = runtime_meta.get("current_attack_path")

    pending = [f for f in findings if f.get("verification_status", "pending") == "pending"]
    verified = [f for f in findings if f.get("verification_status") == "verified"]

    pending_sorted = sorted(
        pending,
        key=lambda finding: -_lookup_confidence(finding, finding_meta),
    )
    verified_sorted = sorted(
        verified,
        key=lambda finding: -_lookup_confidence(finding, finding_meta),
    )
    recon_priority_assets = _top_recon_assets(recon_meta)

    if pending_sorted:
        next_actions = [
            "Priorizar el reanálisis de vulnerabilidades pendientes con alta confianza",
            "Evitar volver a ejecutar la enumeración de directorios a nivel de página principal",
        ]
        if violation_events:
            next_actions.append("Evitar acciones y rutas de herramientas bloqueadas recientemente por la política de restricciones")
        if blocked_targets:
            next_actions.append("Omitir objetivos confirmados como inaccesibles y concentrarse en verificar los puntos de entrada aún accesibles")
        if low_value_rounds >= 3:
            next_actions.append("Hay muchas rondas consecutivas de bajo valor; priorizar el cambio de superficie de parámetros o nuevos puntos de entrada")
        if recon_priority_assets:
            next_actions.append(f"Priorizar el regreso al activo de reconocimiento de alto valor: {recon_priority_assets[0]}")
        return {
            "strategy": "verify_pending_findings",
            "reason": _build_reason(
                f"Existen {len(pending_sorted)} candidatos a vulnerabilidad pendientes de verificación; se debe priorizar cerrar el ciclo de verificación",
                blocked_targets=blocked_targets,
                low_value_rounds=low_value_rounds,
            ),
            "recommended_phase": PentestPhase.VULN_DISCOVERY.value,
            "priority_findings": [_brief_finding(f, finding_meta) for f in pending_sorted[:5]],
            "priority_targets": _infer_priority_targets(pending_sorted)
            or recon_priority_assets[:5],
            "priority_recon_assets": recon_priority_assets[:5],
            "blocked_targets": blocked_targets[:5],
            "failed_targets": _top_failed_targets(failed_targets),
            "recent_failed_steps": failed_steps[:5],
            "low_value_rounds": low_value_rounds,
            "next_actions": next_actions,
        }

    if verified_sorted:
        next_actions = [
            "Priorizar la expansión de la cadena de explotación en torno a las vulnerabilidades ya verificadas",
            "Evitar retroceder a un reconocimiento básico de bajo valor",
        ]
        if violation_events:
            next_actions.append("Antes de ampliar la explotación, confirmar que no se activará la política de restricciones existente")
        if current_attack_path:
            next_actions.append(f"No seguir estancado en la ruta anterior {current_attack_path}; priorizar la expansión hacia nueva explotación posterior")
        if recon_priority_assets:
            next_actions.append(f"Ampliar la explotación combinándola con el activo de reconocimiento de alto valor: {recon_priority_assets[0]}")
        return {
            "strategy": "exploit_expand",
            "reason": _build_reason(
                f"Ya existen {len(verified_sorted)} vulnerabilidades verificadas; priorizar continuar su explotación y expansión",
                blocked_targets=blocked_targets,
                low_value_rounds=low_value_rounds,
            ),
            "recommended_phase": PentestPhase.EXPLOITATION.value,
            "priority_findings": [_brief_finding(f, finding_meta) for f in verified_sorted[:5]],
            "priority_targets": _infer_priority_targets(verified_sorted)
            or recon_priority_assets[:5],
            "priority_recon_assets": recon_priority_assets[:5],
            "blocked_targets": blocked_targets[:5],
            "failed_targets": _top_failed_targets(failed_targets),
            "recent_failed_steps": failed_steps[:5],
            "low_value_rounds": low_value_rounds,
            "next_actions": next_actions,
        }

    active_dims = [key for key in ("server", "website", "domain", "personnel") if key in recon_dims]
    incomplete = [key for key in active_dims if not recon_dims.get(key, False)]
    if incomplete:
        next_actions = ["Completar las brechas de reconocimiento antes de pasar a la verificación de vulnerabilidades"]
        if violation_events:
            next_actions.append("Priorizar acciones de recopilación de información que no estén bloqueadas por restricciones")
        if blocked_targets:
            next_actions.append("Ignorar los subobjetivos inaccesibles y priorizar completar las dimensiones de reconocimiento de los activos aún accesibles")
        if recon_priority_assets:
            next_actions.append(f"Priorizar continuar con estos activos de reconocimiento de alto valor: {recon_priority_assets[0]}")
        return {
            "strategy": "continue_recon",
            "reason": _build_reason(
                f"Dimensiones de reconocimiento incompletas: {', '.join(incomplete)}",
                blocked_targets=blocked_targets,
                low_value_rounds=low_value_rounds,
            ),
            "recommended_phase": PentestPhase.RECON.value,
            "priority_findings": [],
            "priority_targets": recon_priority_assets[:5],
            "priority_recon_assets": recon_priority_assets[:5],
            "blocked_targets": blocked_targets[:5],
            "failed_targets": _top_failed_targets(failed_targets),
            "recent_failed_steps": failed_steps[:5],
            "low_value_rounds": low_value_rounds,
            "next_actions": next_actions,
        }

    next_actions = ["Continuar realizando verificación de candidatos en torno a los puntos de entrada conocidos"]
    if violation_events:
        next_actions.append("Evitar acciones de alto riesgo bloqueadas recientemente por restricciones")
    if low_value_rounds >= 3:
        next_actions.append("Evitar rutas de escaneo que fallaron recientemente; cambiar a un nuevo punto de entrada o a una superficie de parámetros diferente")
    if recon_priority_assets:
        next_actions.append(f"Priorizar la prueba de estos activos de reconocimiento de alto valor: {recon_priority_assets[0]}")
    return {
        "strategy": "continue_scan",
        "reason": _build_reason(
            "Aún no hay vulnerabilidades verificadas; continuar avanzando el escaneo desde la superficie de ataque candidata",
            blocked_targets=blocked_targets,
            low_value_rounds=low_value_rounds,
        ),
        "recommended_phase": PentestPhase.VULN_DISCOVERY.value,
        "priority_findings": [],
        "priority_targets": recon_priority_assets[:5],
        "priority_recon_assets": recon_priority_assets[:5],
        "blocked_targets": blocked_targets[:5],
        "failed_targets": _top_failed_targets(failed_targets),
        "recent_failed_steps": failed_steps[:5],
        "low_value_rounds": low_value_rounds,
        "next_actions": next_actions,
    }


def compute_finding_confidence(meta: dict[str, Any]) -> float:
    """Compute effective confidence from stored finding metadata with time decay."""
    status = meta.get("verification_status", "pending")
    observation_count = int(meta.get("observation_count", 1))
    last_seen_at = meta.get("last_seen_at")
    last_verified_at = meta.get("last_verified_at")

    if status == "verified":
        base = 0.88
    elif status == "rejected":
        base = 0.08
    else:
        base = 0.55

    confidence = base + min(max(observation_count - 1, 0), 4) * 0.04

    age_days = _age_days(
        last_verified_at if status == "verified" and last_verified_at else last_seen_at
    )
    if status == "pending":
        confidence -= age_days * 0.02
    elif status == "verified":
        confidence -= age_days * 0.01

    return round(max(0.05, min(confidence, 0.99)), 3)


def compute_recon_asset_confidence(meta: dict[str, Any]) -> float:
    """Compute effective confidence for recon assets such as subdomains or paths."""
    category = str(meta.get("category", "asset"))
    value = str(meta.get("value", ""))
    observation_count = int(meta.get("observation_count", 1))
    last_seen_at = meta.get("last_seen_at")

    base = {
        "subdomains": 0.62,
        "paths": 0.68,
        "params": 0.58,
    }.get(category, 0.55)

    confidence = base + min(max(observation_count - 1, 0), 4) * 0.05
    value_lower = value.lower()

    if category == "subdomains" and any(
        token in value_lower for token in ("api", "admin", "vpn", "oa", "mail", "jw", "jwc", "zsw")
    ):
        confidence += 0.04
    elif category == "paths" and any(
        token in value_lower
        for token in ("admin", "api", "login", "upload", "download", "search", "news", "jwc", "vpn")
    ):
        confidence += 0.05
    elif category == "params" and any(
        token in value_lower
        for token in ("id", "file", "path", "q", "search", "wd", "keyword", "page", "cid")
    ):
        confidence += 0.04

    age_days = _age_days(last_seen_at)
    confidence -= age_days * 0.015

    return round(max(0.05, min(confidence, 0.99)), 3)


def _lookup_confidence(finding: dict[str, Any], finding_meta: dict[str, Any]) -> float:
    key = _finding_key(finding)
    meta = finding_meta.get(key, {})
    if not meta:
        return 0.5
    return float(meta.get("confidence", compute_finding_confidence(meta)))


def _finding_key(finding: dict[str, Any]) -> str:
    return (
        finding.get("finding_id") or f"{finding.get('title', '')}::{finding.get('vuln_type', '')}"
    )


def _brief_finding(finding: dict[str, Any], finding_meta: dict[str, Any]) -> str:
    confidence = _lookup_confidence(finding, finding_meta)
    title = finding.get("title", "unknown")
    status = finding.get("verification_status", "pending")
    return f"{title} ({status}, conf={confidence:.2f})"


def _age_days(timestamp: str | None) -> float:
    if not timestamp:
        return 0.0
    try:
        delta = datetime.now() - datetime.fromisoformat(timestamp)
        return max(delta.total_seconds() / 86400.0, 0.0)
    except Exception:
        return 0.0


def _infer_priority_targets(findings: list[dict[str, Any]]) -> list[str]:
    import re

    targets: list[str] = []
    for finding in findings:
        text = " ".join(
            str(part or "")
            for part in (
                finding.get("title"),
                finding.get("description"),
                finding.get("evidence"),
            )
        )
        url_match = re.search(r"https?://[^\s'\"<>()]+", text)
        path_match = re.search(r"/[A-Za-z0-9._/\-?=&%]+", text) if not url_match else None
        candidate = url_match.group(0) if url_match else path_match.group(0) if path_match else None
        if candidate and candidate not in targets:
            targets.append(candidate)
    return targets[:5]


def _top_recon_assets(recon_meta: dict[str, Any]) -> list[str]:
    assets: list[tuple[float, int, str]] = []
    for category, items in recon_meta.items():
        if not isinstance(items, dict):
            continue
        for value, meta in items.items():
            confidence = float(meta.get("confidence", compute_recon_asset_confidence(meta)))
            obs = int(meta.get("observation_count", 1))
            label = f"{category}:{value}"
            assets.append((confidence, obs, label))
    assets.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return [label for _, _, label in assets[:5]]


def _top_failed_targets(failed_targets: dict[str, Any]) -> list[str]:
    items = sorted(
        ((str(host), int(count)) for host, count in failed_targets.items()),
        key=lambda item: (-item[1], item[0]),
    )
    return [f"{host} ({count})" for host, count in items[:5]]


def _build_reason(base: str, *, blocked_targets: list[str], low_value_rounds: int) -> str:
    suffix: list[str] = []
    if blocked_targets:
        suffix.append(f"Ya existen {len(blocked_targets)} objetivos inaccesibles")
    if low_value_rounds >= 3:
        suffix.append(f"{low_value_rounds} rondas consecutivas de avance de bajo valor")
    if not suffix:
        return base
    return f"{base}; {'; '.join(suffix)}"
