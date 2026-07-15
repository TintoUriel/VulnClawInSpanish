"""Capa puente entre los resultados de plugins y SessionState.findings.

Convierte el PluginFinding emitido por un plugin en un VulnerabilityFinding
usado por el Agent, y lo fusiona en SessionState con deduplicación por
finding_id, para que los resultados de los plugins entren en la cadena de
generación de informes.
"""

from __future__ import annotations

import json
from typing import Any

# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: elimina la violación V4 — los tipos hoja se movieron a config/domain_models.py.
from vulnclaw.agent.context import SessionState
from vulnclaw.config.domain_models import VulnerabilityFinding
from vulnclaw.plugins.result import PluginFinding, PluginResult, RiskLevel

# Nivel de riesgo del plugin → severidad de vulnerabilidad (alineado con los valores de VulnerabilityFinding.severity)
RISK_TO_SEVERITY: dict[RiskLevel, str] = {
    RiskLevel.INFO: "Info",
    RiskLevel.LOW: "Low",
    RiskLevel.MEDIUM: "Medium",
    RiskLevel.HIGH: "High",
    RiskLevel.CRITICAL: "Critical",
}


def _evidence_level_for(confidence: float) -> str:
    """Mapea aproximadamente el nivel de evidencia según la confianza (el plugin no verifica activamente en red, el máximo es L2)."""
    if confidence >= 0.8:
        return "L2"
    return "L1"


def plugin_finding_to_vuln_finding(
    finding: PluginFinding,
    *,
    plugin_id: str = "",
) -> VulnerabilityFinding:
    """Convierte un PluginFinding individual en un VulnerabilityFinding."""
    evidence_obj = finding.evidence or {}
    try:
        evidence_text = (
            json.dumps(evidence_obj, ensure_ascii=False)
            if isinstance(evidence_obj, (dict, list))
            else str(evidence_obj)
        )
    except (TypeError, ValueError):
        evidence_text = str(evidence_obj)

    source = plugin_id or finding.metadata.get("plugin_id", "")
    description = finding.description
    if source:
        prefix = f"[Plugin:{source}] "
        description = f"{prefix}{description}" if description else prefix.strip()

    return VulnerabilityFinding(
        title=finding.title,
        severity=RISK_TO_SEVERITY.get(finding.risk, "Info"),
        vuln_type=finding.vuln_type,
        description=description,
        evidence=evidence_text[:500],
        remediation=finding.remediation,
        evidence_level=_evidence_level_for(finding.confidence),
        lifecycle_status="pending_verification",
    )


def merge_plugin_results_into_session(
    session: SessionState,
    results: PluginResult | list[PluginResult],
) -> int:
    """Fusiona los findings de un lote de resultados de plugins en la sesión, devolviendo la cantidad añadida (tras deduplicar)."""
    if isinstance(results, PluginResult):
        results = [results]

    added = 0
    for result in results:
        for finding in result.findings:
            vuln = plugin_finding_to_vuln_finding(finding, plugin_id=result.plugin_id)
            if session.add_finding(vuln):
                added += 1
    return added


def summarize_plugin_results(results: list[PluginResult]) -> dict[str, Any]:
    """Resume un lote de resultados de plugins para mostrarlos en el CLI o en el informe."""
    findings = sum(len(result.findings) for result in results)
    errors = [result for result in results if result.error and not result.skipped]
    skipped = [result for result in results if result.skipped]
    return {
        "plugins": len(results),
        "findings": findings,
        "errors": len(errors),
        "skipped": len(skipped),
    }
