"""VulnClaw Report Generator — generate structured penetration test reports."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from jinja2 import Template

# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: Eliminación de la infracción V2 — los tipos hoja se movieron a
#          config/domain_models.py.
from vulnclaw.agent.context import SessionState
from vulnclaw.config.domain_models import VulnerabilityFinding

# ── Report Template ─────────────────────────────────────────────────

REPORT_TEMPLATE = """\
# Informe de Pruebas de Penetración

## 1. Resumen del Proyecto

| Elemento | Detalle |
|------|------|
| **Objetivo de la prueba** | {{ target }} |
| **Fecha de la prueba** | {{ started_at }} |
| **Generación del informe** | {{ generated_at }} |
| **Herramienta de prueba** | VulnClaw v{{ version }} |
| **Restricciones de la tarea** | {{ task_constraints_summary }} |

## 2. Resumen Ejecutivo

{% if verified_count > 0 %}
- **Vulnerabilidades verificadas**: {{ verified_count }} (de las cuales {{ critical_count }} son Critical y {{ high_count }} son High)
{% else %}
- **Vulnerabilidades verificadas**: 0
{% endif %}
- **Falsos positivos descartados**: {{ rejected_count }}
- **Pendientes de verificación**: {{ pending_count }} (no se muestran en el informe)
- **Candidatas**: {{ candidate_count }}
- **Pendientes de verificación (detalle)**: {{ pending_verification_count }}
- **Requieren revisión manual**: {{ manual_review_count }}
- **Superficie de ataque**: {{ attack_surface_summary }}
{% if constraint_violation_events or constraint_violations %}
- **Infracciones de restricciones bloqueadas**: {{ constraint_violations|length }}
{% endif %}

{% if rejected_count > 0 %}
### Falsos positivos descartados

Las siguientes hipótesis de vulnerabilidad no pasaron la verificación con PoC y fueron descartadas, por lo que no se incluyen en el informe:

{% for f in rejected_findings %}
- {{ f.title }} — {{ f.verification_note }}
{% endfor %}
{% endif %}

### Distribución por Nivel de Riesgo

| Nivel | Cantidad |
|------|------|
| Critical | {{ critical_count }} |
| High | {{ high_count }} |
| Medium | {{ medium_count }} |
| Low/Info | {{ low_count }} |

{% if verified_findings %}
### Recomendaciones Clave

{% for rec in key_recommendations %}
{{ loop.index }}. {{ rec }}
{% endfor %}
{% else %}
### Hallazgos de Vulnerabilidades

**No se encontraron vulnerabilidades válidas en esta prueba.**

Posibles causas:
- La configuración de seguridad del sistema objetivo es sólida
- Profundidad de la prueba insuficiente (pocas rondas de reconocimiento)
- No se cumplieron las condiciones para la explotación

Recomendaciones:
- Aumentar el número de rondas de la prueba de penetración
- Probar más tipos de vulnerabilidades
- Verificar si se requiere autenticación o permisos de acceso especiales
{% endif %}

## 3. Hallazgos Detallados

{% for finding in findings %}
### 3.{{ loop.index }} {{ finding.title }} — [{{ finding.severity }}]
{% if finding.verification_status == "pending" %}
> ⚠️ **Pendiente de verificación** — Esta vulnerabilidad fue detectada automáticamente y aún no ha pasado la verificación con PoC. Revísela manualmente.
{% elif finding.verification_status == "rejected" %}
> ❌ **Descartada (falso positivo)** — {{ finding.verification_note or "Verificada como falso positivo" }}
{% elif finding.lifecycle_status == "needs_manual_review" %}
> 🔎 **Requiere revisión manual** — Actualmente existe evidencia indirecta, pero se requiere revisión manual antes de confirmarla como vulnerabilidad formal.
{% endif %}

- **Tipo de vulnerabilidad**: {{ finding.vuln_type or "Sin clasificar" }}
- **Ciclo de vida**: {{ finding.lifecycle_status or "pending_verification" }}
- **Nivel de evidencia**: {{ finding.evidence_level or "L1" }}
- **CVE**: {{ finding.cve or "N/A" }}
- **Alcance del impacto**: {{ finding.description or "Ninguno" }}
{% if finding.evidence %}
- **Evidencia de verificación**: {{ finding.evidence }}
{% endif %}
{% if finding.poc_script %}
- **Script PoC**: ver adjunto `{{ finding.poc_script }}`
{% endif %}
- **Recomendación de corrección**: {{ finding.remediation or "Aplique las medidas de corrección adecuadas según el tipo de vulnerabilidad" }}
{% if finding.verified and finding.verified_at %}
- **Fecha de verificación**: {{ finding.verified_at }}
{% endif %}

{% endfor %}

{% if llm_attack_summary %}
## 4. Resumen de la Ruta de Ataque

{{ llm_attack_summary }}

{% elif step_summary and step_summary.total_steps > 0 %}
## 4. Resumen de la Ruta de Ataque

{% for phase_name, phase_data in step_summary.phases.items() %}
### {{ phase_name }} (total {{ phase_data.count }} pasos)

| Estado | Cantidad |
|------|------|
| ✅ Éxito | {{ phase_data.success_count }} |
| ❌ Fallo | {{ phase_data.failure_count }} |

**Acciones clave**: {{ phase_data.actions[:5]|join(', ') }}

{% if phase_data.key_results %}
**Hallazgos principales**:
{% for result in phase_data.key_results %}
- {{ result }}
{% endfor %}
{% endif %}

---
{% endfor %}

**Total**: {{ step_summary.total_steps }} pasos

{% if step_summary.key_findings %}
### Cronología de Hallazgos Clave

{% for finding in step_summary.key_findings %}
- {{ finding }}
{% endfor %}
{% endif %}

{% elif findings %}
## 4. Ruta de Ataque

{% for step in executed_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
{% endif %}

{% if constraint_violation_events or constraint_violations %}
## 5. Auditoría de Infracciones de Restricciones

{% if constraint_violation_events %}
{% for item in constraint_violation_events %}
- [{{ item.source or "unknown" }}] {{ item.summary }}
{% endfor %}
{% else %}
{% for item in constraint_violations %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}

## 6. Anexos

- Scripts PoC: ver el directorio `pocs/`
- Capturas de tráfico: ver el directorio `evidence/traffic/` (índice requests.jsonl + solicitud/respuesta cruda por cada petición)
- Evidencia de capturas de pantalla: ver el directorio `screenshots/`

---

> 🦞 Informe generado automáticamente por VulnClaw | {{ generated_at }}
> **Principio**: vulnerabilidad no verificada = falso positivo = no se incluye en el informe
"""


def generate_report(
    session: SessionState,
    output_path: Optional[str] = None,
    llm_attack_summary: str = "",
    report_format: str = "markdown",
    target_state_context: Optional[dict[str, Any]] = None,
) -> Path:
    """Generate a penetration test report from session state.

    Only verified findings are rendered into the main detailed findings section.
    Pending, candidate, and rejected findings remain in summary/governance views.
    """
    from vulnclaw import __version__
    from vulnclaw.report.filter import deduplicate_report_findings

    all_findings = session.findings
    verified_findings = deduplicate_report_findings(session.get_verified_findings())
    pending_findings = session.get_pending_findings()
    rejected_findings = session.get_rejected_findings()
    candidate_findings = (
        session.get_candidate_findings() if hasattr(session, "get_candidate_findings") else []
    )
    pending_verification_findings = (
        session.get_pending_verification_findings()
        if hasattr(session, "get_pending_verification_findings")
        else []
    )
    manual_review_findings = (
        session.get_manual_review_findings()
        if hasattr(session, "get_manual_review_findings")
        else []
    )

    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
    for finding in verified_findings:
        sev = finding.severity
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["Medium"] += 1

    seen_vuln_types = set()
    recommendations = []
    for finding in verified_findings:
        if finding.severity in ("Critical", "High"):
            vt = finding.vuln_type or "Sin clasificar"
            if vt in seen_vuln_types:
                continue
            seen_vuln_types.add(vt)
            rec = finding.remediation or f"Corrija con prioridad el riesgo de {vt}: {finding.title}"
            recommendations.append(rec)

    if not recommendations:
        recommendations.append("Revise con prioridad la superficie de ataque y complete la cadena de verificación, confirmando que se hayan corregido los puntos de entrada de alto riesgo.")

    if output_path is None:
        from vulnclaw.config.settings import SESSIONS_DIR

        safe_target = (session.target or "unknown").replace("/", "_").replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(SESSIONS_DIR / f"report_{timestamp}_{safe_target}.md")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    from vulnclaw.report.poc_builder import generate_pocs

    pocs_dir = output.parent / "pocs"
    generate_pocs(session, pocs_dir)

    from vulnclaw.report.filter import ReportContentFilter

    if not llm_attack_summary:
        llm_attack_summary = _generate_attack_summary_from_session(session)
        if llm_attack_summary:
            print("[*] LLM attack summary generated for report section 4")
    filtered_summary = ReportContentFilter.filter(llm_attack_summary) if llm_attack_summary else ""

    context = {
        "target": session.target or "unknown",
        "started_at": session.started_at,
        "generated_at": datetime.now().isoformat(),
        "version": __version__,
        "critical_count": severity_counts["Critical"],
        "high_count": severity_counts["High"],
        "medium_count": severity_counts["Medium"],
        "low_count": severity_counts["Low"] + severity_counts["Info"],
        "task_constraints_summary": _format_task_constraints_summary(session),
        "attack_surface_summary": _summarize_attack_surface(session),
        "constraint_violations": list(getattr(session, "constraint_violations", [])),
        "constraint_violation_events": [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in getattr(session, "constraint_violation_events", [])
        ],
        "key_recommendations": recommendations,
        "verified_findings": [_build_report_finding(finding) for finding in verified_findings],
        "findings": [_build_report_finding(finding) for finding in verified_findings],
        "executed_steps": session.executed_steps,
        "total_findings_submitted": len(all_findings),
        "verified_count": len(verified_findings),
        "rejected_count": len(rejected_findings),
        "pending_count": len(pending_findings),
        "candidate_count": len(candidate_findings),
        "pending_verification_count": len(pending_verification_findings),
        "manual_review_count": len(manual_review_findings),
        "rejected_findings": rejected_findings,
        "step_summary": session.get_step_summary(),
        "llm_attack_summary": filtered_summary,
    }

    template = Template(REPORT_TEMPLATE)
    report_content = template.render(**context)
    if verified_findings:
        report_content += "\n\n" + _render_verified_finding_details_clean(
            verified_findings,
            heading="## 6. Ubicación y Reproducción de Vulnerabilidades Verificadas",
            traffic_store=_resolve_traffic_store(output.parent),
        )
    if target_state_context:
        report_content += "\n\n" + _render_target_state_context(target_state_context)

    if report_format.lower() == "html":
        html_content = Template(
            """<!doctype html><html><head><meta charset="utf-8"><title>VulnClaw Report</title></head><body><pre>{{ content }}</pre></body></html>"""
        ).render(content=report_content)
        output = output.with_suffix(".html") if output.suffix.lower() != ".html" else output
        output.write_text(html_content, encoding="utf-8")
    else:
        output.write_text(report_content, encoding="utf-8")

    # ★ Emit machine-consumable findings artifacts next to the report: findings.json
    # (all findings + lifecycle) and findings.sarif (verified findings only). These
    # draw from the same verified feed as the report — no divergent finding lists.
    from vulnclaw.report.findings_output import write_findings_artifacts

    write_findings_artifacts(session, output.parent / "findings")

    return output


def generate_report_from_file(session_path: str) -> Path:
    """Generate a report from a saved session JSON file."""
    session = SessionState.load(Path(session_path))
    return generate_report(session)


def generate_report_from_target_state(
    target_state: dict[str, Any],
    report_format: str = "markdown",
    output_path: str | None = None,
) -> Path:
    """Generate a report from a target-state snapshot."""
    raw = dict(target_state)
    target_state_context = {
        "resume_meta": raw.pop("resume_meta", None),
        "resume_summary": raw.pop("resume_summary", None),
        "recon_meta": raw.pop("recon_meta", None),
        "runtime_meta": raw.pop("runtime_meta", None),
        "finding_meta": raw.pop("finding_meta", None),
    }
    session = SessionState(**raw)
    return generate_report(
        session,
        output_path=output_path,
        report_format=report_format,
        target_state_context=target_state_context,
    )


def _summarize_attack_surface(session: SessionState) -> str:
    """Summarize the attack surface from recon data, including subdomains."""
    parts = []
    recon = session.recon_data

    if "subdomains" in recon and recon["subdomains"]:
        parts.append(f"Subdominios: {', '.join(recon['subdomains'][:10])}")
    if "ports" in recon:
        parts.append(f"Puertos abiertos: {recon['ports']}")
    if "services" in recon:
        parts.append(f"Servicios: {recon['services']}")
    if "technologies" in recon:
        parts.append(f"Pila tecnológica: {recon['technologies']}")
    if "waf" in recon:
        parts.append(f"WAF: {recon['waf']}")
    if "domains" in recon:
        parts.append(f"Dominios relacionados: {', '.join(recon['domains'][:5])}")

    return "; ".join(parts) if parts else "No recopilado"


# ── Persistent Pentest Cycle Report ──────────────────────────────────

CYCLE_REPORT_TEMPLATE = """\
# Pruebas de Penetración Continuas — Informe de Ciclo

## Información del Ciclo

| Elemento | Detalle |
|------|------|
| **Objetivo de la prueba** | {{ target }} |
| **Ciclo actual** | Ciclo {{ cycle_num }} |
| **Rondas por ciclo** | {{ rounds_per_cycle }} |
| **Vulnerabilidades verificadas nuevas en este ciclo** | {{ new_findings }} |
| **Total acumulado de vulnerabilidades verificadas** | {{ total_findings }} |
| **Total acumulado de pasos ejecutados** | {{ total_steps }} |
| **Fecha de generación del informe** | {{ generated_at }} |

{% if cycle_findings %}
## Hallazgos de Vulnerabilidades de Este Ciclo

{% for finding in cycle_findings %}
### {{ loop.index }}. {{ finding.title }} — [{{ finding.severity }}]
{% if finding.verification_status == "pending" %}
> ⚠️ **Pendiente de verificación** — Esta vulnerabilidad fue detectada automáticamente y aún no ha pasado la verificación con PoC.
{% elif finding.lifecycle_status == "needs_manual_review" %}
> 🔎 **Requiere revisión manual** — Actualmente existe evidencia indirecta, pero se requiere revisión manual antes de confirmarla como vulnerabilidad formal.
{% endif %}
- **Tipo de vulnerabilidad**: {{ finding.vuln_type or "Sin clasificar" }}
- **Ciclo de vida**: {{ finding.lifecycle_status or "pending_verification" }}
- **Nivel de evidencia**: {{ finding.evidence_level or "L1" }}
- **CVE**: {{ finding.cve or "N/A" }}
- **Alcance del impacto**: {{ finding.description or "Ninguno" }}
{% if finding.evidence %}
- **Evidencia de verificación**: {{ finding.evidence }}
{% endif %}
- **Recomendación de corrección**: {{ finding.remediation or "Aplique las medidas de corrección adecuadas según el tipo de vulnerabilidad" }}
{% if finding.verified_at %}
- **Fecha de verificación**: {{ finding.verified_at }}
{% endif %}

{% endfor %}
{% else %}
## Hallazgos de Vulnerabilidades de Este Ciclo

No se encontraron vulnerabilidades nuevas en este ciclo.
{% endif %}

## Resumen Acumulado de Vulnerabilidades

| # | Título de la vulnerabilidad | Nivel | Tipo | Evidencia/URL | Estado |
|---|---------|------|------|---------|------|
{% for finding in all_findings %}
{% set ev = (finding.evidence or finding.description or "")[:80] %}
| {{ loop.index }} | {{ finding.title }} | {{ finding.severity }} | {{ finding.vuln_type or "—" }} | {{ ev if ev else "—" }} | {% if finding.verification_status == "verified" %}✅ Verificada{% elif finding.lifecycle_status == "needs_manual_review" %}🔎 Requiere revisión manual{% elif finding.verification_status == "pending" %}⚠️ Pendiente de verificación{% else %}❌ Descartada{% endif %} |
{% endfor %}

{% if not all_findings %}
Aún no se han encontrado vulnerabilidades
{% endif %}

## Distribución por Nivel de Riesgo

| Nivel | Cantidad |
|------|------|
| Critical | {{ critical_count }} |
| High | {{ high_count }} |
| Medium | {{ medium_count }} |
| Low/Info | {{ low_count }} |

{% if llm_attack_summary %}
## Resumen de la Ruta de Ataque

{{ llm_attack_summary }}

{% elif step_summary and step_summary.total_steps > 0 %}
## Resumen de la Ruta de Ataque

{% for phase_name, phase_data in step_summary.phases.items() %}
### {{ phase_name }} (total {{ phase_data.count }} pasos)

| Estado | Cantidad |
|------|------|
| ✅ Éxito | {{ phase_data.success_count }} |
| ❌ Fallo | {{ phase_data.failure_count }} |

**Acciones clave**: {{ phase_data.actions[:5]|join(', ') }}

{% if phase_data.key_results %}
**Hallazgos principales**:
{% for result in phase_data.key_results %}
- {{ result }}
{% endfor %}
{% endif %}

---
{% endfor %}

**Total**: {{ step_summary.total_steps }} pasos

{% if step_summary.key_findings %}
### Cronología de Hallazgos Clave

{% for finding in step_summary.key_findings %}
- {{ finding }}
{% endfor %}
{% endif %}

{% elif recent_steps %}
## Resumen de la Ruta de Ataque

{% for step in recent_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
{% endif %}

## Recomendaciones Clave

{% for rec in recommendations %}
{{ loop.index }}. {{ rec }}
{% endfor %}

---

> 🦞 Informe de Ciclo de Pruebas de Penetración Continuas | VulnClaw | {{ generated_at }}
> **Principio**: vulnerabilidad no verificada = falso positivo = no se incluye en el informe
"""


def _generate_attack_summary_from_session(session: SessionState) -> str:
    """Generate a readable attack-path summary using VulnClaw's configured LLM."""
    try:
        from vulnclaw.config.settings import load_config, make_openai_client
        from vulnclaw.config.text_utils import strip_think_tags
        from vulnclaw.config.token_provider import (
            TokenResolutionError,
            has_llm_credentials,
            resolve_llm_token,
        )

        config = load_config()
        if not has_llm_credentials(config.llm):
            return ""

        try:
            token = resolve_llm_token(config.llm)
        except TokenResolutionError:
            return ""

        client = make_openai_client(
            api_key=token,
            base_url=config.llm.base_url,
        )

        steps = session.executed_steps[-40:] if session.executed_steps else []
        notes = session.notes[-25:] if session.notes else []
        findings = session.findings[-20:] if session.findings else []

        steps_text = (
            "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(steps))
            if steps
            else "No step records"
        )
        notes_text = "\n".join(f"- {note}" for note in notes) if notes else "No key observations"
        findings_text = (
            "\n".join(
                f"- [{finding.severity}] {finding.title} | Evidence: {(finding.evidence or '')[:200]}"
                for finding in findings
            )
            if findings
            else "No findings"
        )

        prompt = (
            f"Target: {session.target or 'unknown'}\n"
            f"Phase: {getattr(session.phase, 'value', str(session.phase))}\n\n"
            f"=== Executed Steps ===\n{steps_text}\n\n"
            f"=== Key Observations ===\n{notes_text}\n\n"
            f"=== Findings ===\n{findings_text}\n\n"
            "Please write a readable Spanish attack-path summary. Requirements:\n"
            "1. Clearly explain how the testing progressed, not generic filler.\n"
            "2. Mention URLs, paths, parameters, stack, and verification actions when available.\n"
            "3. Explicitly call out false positives or findings that failed to reproduce.\n"
            "4. Output 2-5 short natural-language paragraphs only. No markdown headings. No thinking tags.\n"
            "5. Do not invent steps that were never executed.\n"
        )

        response = client.chat.completions.create(
            **_build_report_summary_llm_kwargs(
                config,
                [{"role": "user", "content": prompt}],
            )
        )
        if response and response.choices:
            raw = response.choices[0].message.content or ""
            return strip_think_tags(raw).strip()
    except Exception as exc:
        print(f"[!] LLM attack summary generation failed: {exc}")
        return ""
    return ""


def _build_report_summary_llm_kwargs(config: Any, messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build Chat Completions kwargs for report summary generation."""
    # Modificado por: Nyaecho
    # Fecha de modificación: 2026-07-08
    # Motivo de la modificación: Corrección V2 — se usa directamente config/llm_utils,
    #          eliminando el shim de AgentContext.
    from vulnclaw.config.llm_utils import build_chat_completion_kwargs

    return build_chat_completion_kwargs(
        config.llm,
        messages,
        max_tokens=min(config.llm.max_tokens, 1200),
        temperature=0.2,
    )


def generate_persistent_cycle_report(
    session: SessionState,
    cycle_num: int,
    total_findings: int,
    new_findings: int,
    total_steps: int,
    rounds_per_cycle: int,
    output_path: Optional[str] = None,
    llm_attack_summary: str = "",  # ★ Resumen de la ruta de ataque generado por el LLM
    prev_verified_ids: Optional[set] = None,
) -> Path:
    """Generate a cycle report for persistent pentest.

    Solo incluye vulnerabilidades verificadas (verified=True).

    Args:
        session: Current session state with findings.
        cycle_num: Current cycle number (1-based).
        total_findings: Total findings so far (cumulative).
        new_findings: New findings in this cycle (all findings delta; used only
            as a fallback when prev_verified_ids is not supplied).
        total_steps: Total executed steps so far (cumulative).
        rounds_per_cycle: Rounds per cycle.
        output_path: Output file path. If None, auto-generate.
        prev_verified_ids: finding_id set of findings already verified before this
            cycle. When provided, "new this cycle" is computed by identity against
            this set instead of slicing by an all-findings count — the count-based
            slice mislabels prior verified findings as new when a cycle adds
            unverified findings.

    Returns:
        Path to the generated report file.
    """
    from vulnclaw import __version__
    from vulnclaw.report.filter import deduplicate_report_findings

    # ★ Incluye todos los findings (incluyendo pending y confirmed, no solo verified)
    all_findings = session.findings
    verified_findings = deduplicate_report_findings(session.get_verified_findings())
    manual_review_findings = (
        session.get_manual_review_findings()
        if hasattr(session, "get_manual_review_findings")
        else []
    )

    # Count verified findings by severity only (pending doesn't count as real result)
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
    for finding in verified_findings:
        sev = finding.severity
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["Medium"] += 1

    # ★ Findings verificados nuevos en este ciclo (solo se cuentan los verified)
    if prev_verified_ids is not None:
        # Determina las vulnerabilidades verificadas nuevas en este ciclo por identidad
        # de finding_id, evitando que al recortar el "subconjunto verificado" mediante
        # el "incremento de todos los findings" se etiqueten erróneamente vulnerabilidades
        # anteriores como nuevas de este ciclo.
        cycle_findings = [
            f for f in verified_findings if f.finding_id not in prev_verified_ids
        ]
    else:
        cycle_findings = verified_findings[-new_findings:] if new_findings > 0 else []

    # Generate recommendations from verified high/critical findings only
    # Deduplicate by vuln_type: only one recommendation per vulnerability type
    seen_vuln_types = set()
    recommendations = []
    for finding in verified_findings:
        if finding.severity in ("Critical", "High"):
            vt = finding.vuln_type or "Sin clasificar"
            if vt in seen_vuln_types:
                continue
            seen_vuln_types.add(vt)
            rec = finding.remediation or f"Corregir vulnerabilidad de {vt}: {finding.title}"
            recommendations.append(rec)
    if not recommendations:
        recommendations.append("Aún no hay hallazgos de alto riesgo; continuar profundizando en la prueba")

    if output_path is None:
        from vulnclaw.config.settings import SESSIONS_DIR

        safe_target = (session.target or "unknown").replace("/", "_").replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(
            SESSIONS_DIR / f"persistent_cycle{cycle_num:03d}_{timestamp}_{safe_target}.md"
        )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    from vulnclaw.report.poc_builder import generate_pocs

    pocs_dir = output.parent / "pocs"
    generate_pocs(session, pocs_dir)

    # Recent steps (last 20 to avoid bloat)
    recent_steps = session.executed_steps[-20:]

    # ★ Resumen de la ruta de ataque (filtra las etiquetas think / marcadores de
    # depuración de la salida cruda del LLM)
    step_summary = session.get_step_summary()
    from vulnclaw.report.filter import ReportContentFilter

    if not llm_attack_summary:
        llm_attack_summary = _generate_attack_summary_from_session(session)
    filtered_summary = ReportContentFilter.filter(llm_attack_summary) if llm_attack_summary else ""

    context = {
        "target": session.target or "No especificado",
        "cycle_num": cycle_num,
        "rounds_per_cycle": rounds_per_cycle,
        "new_findings": len(cycle_findings),
        "total_findings": len(all_findings),
        "total_steps": total_steps,
        "generated_at": datetime.now().isoformat(),
        "version": __version__,
        "cycle_findings": cycle_findings,
        "all_findings": all_findings,  # ★ Incluye todos los findings (incluyendo pending)
        "critical_count": severity_counts["Critical"],
        "high_count": severity_counts["High"],
        "medium_count": severity_counts["Medium"],
        "low_count": severity_counts["Low"] + severity_counts["Info"],
        "recent_steps": recent_steps,
        "recommendations": recommendations,
        "manual_review_count": len(manual_review_findings),
        "step_summary": step_summary,
        "llm_attack_summary": filtered_summary,
    }

    # Render report
    template = Template(CYCLE_REPORT_TEMPLATE)
    report_content = template.render(**context)
    if verified_findings:
        report_content += "\n\n" + _render_verified_finding_details_clean(
            verified_findings,
            heading="## Ubicación y Reproducción de Vulnerabilidades Verificadas",
            traffic_store=_resolve_traffic_store(output.parent),
        )
    output.write_text(report_content, encoding="utf-8")

    # ★ Emit the same machine-consumable findings artifacts as generate_report, so a
    # persistent run's per-cycle reports also produce findings/findings.json and
    # findings/findings.sarif.
    from vulnclaw.report.findings_output import write_findings_artifacts

    write_findings_artifacts(session, output.parent / "findings")

    return output


def _render_target_state_context(target_state_context: dict[str, Any]) -> str:
    """Render extra governance context for target-state based reports."""
    resume_meta = target_state_context.get("resume_meta") or {}
    recon_meta = target_state_context.get("recon_meta") or {}
    runtime_meta = target_state_context.get("runtime_meta") or {}
    resume_summary = target_state_context.get("resume_summary") or ""

    lines = ["## 6. Contexto Histórico de Gobernanza del Objetivo"]

    if resume_meta:
        lines.extend(
            [
                "",
                f"- Estrategia de reanudación: {resume_meta.get('resume_strategy', 'unknown')}",
                f"- Motivo de la estrategia: {resume_meta.get('resume_strategy_reason', 'N/A')}",
            ]
        )
        if resume_meta.get("priority_targets"):
            lines.append(f"- Objetivos prioritarios de reanudación: {', '.join(resume_meta['priority_targets'][:5])}")
        if resume_meta.get("priority_recon_assets"):
            lines.append(
                f"- Activos de reconocimiento prioritarios de reanudación: {', '.join(resume_meta['priority_recon_assets'][:5])}"
            )
        if resume_meta.get("blocked_targets"):
            lines.append(f"- Objetivos bloqueados: {', '.join(resume_meta['blocked_targets'][:5])}")
        if resume_meta.get("failed_targets"):
            lines.append(f"- Objetivos con fallos históricos: {', '.join(resume_meta['failed_targets'][:5])}")
        if resume_meta.get("recent_failed_steps"):
            lines.append("- Rutas/pasos fallidos recientes:")
            for item in resume_meta["recent_failed_steps"][:5]:
                lines.append(f"  - {item}")

    top_assets = _top_recon_assets_for_report(recon_meta)
    if top_assets:
        lines.extend(["", "### Activos de Reconocimiento de Alto Valor"])
        for item in top_assets[:8]:
            lines.append(f"- {item}")

    if runtime_meta.get("current_attack_path"):
        lines.extend(["", f"- Ruta de ataque más reciente: {runtime_meta['current_attack_path']}"])

    if resume_summary:
        lines.extend(["", "### Resumen de Reanudación", "```text", resume_summary.strip(), "```"])

    return "\n".join(lines)


def _top_recon_assets_for_report(recon_meta: dict[str, Any]) -> list[str]:
    ranked: list[tuple[float, str]] = []
    for category, items in recon_meta.items():
        if not isinstance(items, dict):
            continue
        for value, meta in items.items():
            confidence = float(meta.get("confidence", 0))
            ranked.append((confidence, f"{category}:{value} (conf={confidence:.2f})"))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [label for _, label in ranked]


def _extract_location_summary_clean(finding: VulnerabilityFinding) -> str:
    text = " ".join(part for part in [finding.evidence or "", finding.description or ""] if part)
    urls = re.findall(r'https?://[^\s<>"\')\]]+', text)
    paths = re.findall(r"(?:/[\w%&=?\-]+)+", text)

    items: list[str] = []
    seen: set[str] = set()
    for value in urls + paths:
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= 4:
            break
    return " | ".join(items)


def _build_repro_summary_clean(finding: VulnerabilityFinding) -> str:
    parts: list[str] = []
    if finding.poc_script:
        parts.append(f"Ejecutar script PoC: {finding.poc_script}")
    if finding.verification_note:
        parts.append(f"Nota de verificación: {finding.verification_note}")
    elif finding.evidence:
        parts.append(f"Reproducir según la evidencia verificada: {finding.evidence[:160]}")
    if finding.verified_at:
        parts.append(f"Fecha de verificación: {finding.verified_at}")
    return "；".join(parts) if parts else "Aún no hay instrucciones de reproducción disponibles"


def _resolve_traffic_store(output_dir: Path) -> Any | None:
    """Return the run's TrafficStore (report dir preferred, config default as
    fallback so captures the agent wrote are found), or None if none exist."""
    try:
        from vulnclaw.traffic.paths import resolve_report_traffic_store
    except Exception:
        return None
    store = resolve_report_traffic_store(output_dir)
    return store if store.index_path.exists() else None


def _render_http_captures(finding: VulnerabilityFinding, traffic_store: Any) -> list[str]:
    """Inline the raw request/response for each http_capture evidence ref.

    Mirrors the way poc_builder inlines PoC scripts: each verified finding's
    ``evidence_refs`` with ``kind="http_capture"`` is resolved back to its
    JSONL record + blob files and rendered as fenced code blocks.
    """
    refs = getattr(finding, "evidence_refs", None) or []
    if not refs or traffic_store is None:
        return []

    lines: list[str] = []
    for ref in refs:
        if getattr(ref, "kind", "") != "http_capture":
            continue
        request_id = getattr(ref, "request_id", "")
        view = traffic_store.view(request_id) if request_id else None
        if not view:
            continue
        header = f"  - Evidencia de captura `{request_id}` — {view.get('method')} {view.get('url')} → {view.get('status')}"
        lines.append(header)
        request_text = (view.get("request_text") or "").strip()
        response_text = (view.get("response_text") or "").strip()
        if request_text:
            lines.append("    - Solicitud cruda:")
            lines.append("")
            lines.append("```http")
            lines.append(request_text)
            lines.append("```")
        if response_text:
            lines.append("    - Respuesta cruda:")
            lines.append("")
            lines.append("```http")
            lines.append(response_text)
            lines.append("```")
    return lines


def _render_verified_finding_details_clean(
    findings: list[VulnerabilityFinding], heading: str, traffic_store: Any | None = None
) -> str:
    lines = [heading, ""]
    for idx, finding in enumerate(findings, 1):
        location = _extract_location_summary_clean(finding) or "No ubicado / no se extrajo ninguna URL"
        lines.append(f"### {idx}. {finding.title} [{finding.severity}]")
        lines.append(f"- Tipo de vulnerabilidad: {finding.vuln_type or 'Sin clasificar'}")
        lines.append(f"- Ciclo de vida: {finding.lifecycle_status or 'verified'}")
        lines.append(f"- Nivel de evidencia: {finding.evidence_level or 'L4'}")
        lines.append(f"- Ubicación / URL: {location}")
        if finding.evidence:
            lines.append(f"- Evidencia de verificación: {finding.evidence}")
        lines.append(f"- Reproducción / PoC: {_build_repro_summary_clean(finding)}")
        capture_lines = _render_http_captures(finding, traffic_store)
        if capture_lines:
            lines.append("- Evidencia de reproducción capturada:")
            lines.extend(capture_lines)
        lines.append("")
    return "\n".join(lines).rstrip()


def _extract_location_summary(finding: VulnerabilityFinding) -> str:
    text = " ".join(part for part in [finding.evidence or "", finding.description or ""] if part)
    urls = re.findall(r'https?://[^\s<>"\')\]]+', text)
    paths = re.findall(r"(?:/[\w%&=?\-]+)+", text)

    items: list[str] = []
    seen: set[str] = set()
    for value in urls + paths:
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= 4:
            break
    return " | ".join(items)


def _build_repro_summary(finding: VulnerabilityFinding) -> str:
    parts: list[str] = []
    if finding.poc_script:
        parts.append(f"Ejecutar script PoC: {finding.poc_script}")
    if finding.verification_note:
        parts.append(f"Nota de verificación: {finding.verification_note}")
    elif finding.evidence:
        parts.append(f"Reproducir según la evidencia verificada: {finding.evidence[:160]}")
    if finding.verified_at:
        parts.append(f"Fecha de verificación: {finding.verified_at}")
    return "；".join(parts) if parts else "Aún no hay instrucciones de reproducción disponibles"


def _format_task_constraints_summary(session: SessionState) -> str:
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return "No especificado"

    parts: list[str] = []
    if constraints.allowed_ports:
        parts.append(f"Solo puertos {','.join(str(p) for p in constraints.allowed_ports)}")
    if constraints.blocked_ports:
        parts.append(f"Puertos prohibidos {','.join(str(p) for p in constraints.blocked_ports)}")
    if constraints.allowed_hosts:
        parts.append(f"Solo hosts {','.join(constraints.allowed_hosts)}")
    if constraints.allowed_paths:
        parts.append(f"Solo rutas {','.join(constraints.allowed_paths)}")
    if constraints.allowed_actions:
        parts.append(f"Solo acciones {','.join(constraints.allowed_actions)}")
    if constraints.blocked_actions:
        parts.append(f"Acciones prohibidas {','.join(constraints.blocked_actions)}")
    return "；".join(parts) if parts else "Restricciones habilitadas"


def _build_report_finding(finding: VulnerabilityFinding) -> dict[str, Any]:
    return {
        "title": finding.title,
        "severity": finding.severity,
        "vuln_type": finding.vuln_type,
        "description": finding.description,
        "evidence": finding.evidence,
        "cve": finding.cve,
        "remediation": finding.remediation,
        "poc_script": finding.poc_script,
        "verified": finding.verified,
        "verified_at": finding.verified_at,
        "verification_status": finding.verification_status,
        "verification_note": finding.verification_note,
        "lifecycle_status": finding.lifecycle_status,
        "evidence_level": finding.evidence_level,
        "location_summary": _extract_location_summary(finding),
        "repro_summary": _build_repro_summary(finding),
    }


def _render_verified_finding_details(findings: list[VulnerabilityFinding], heading: str) -> str:
    lines = [heading, ""]
    for idx, finding in enumerate(findings, 1):
        location = _extract_location_summary(finding) or "No ubicado / no se extrajo ninguna URL"
        lines.append(f"### {idx}. {finding.title} [{finding.severity}]")
        lines.append(f"- Tipo de vulnerabilidad: {finding.vuln_type or 'Sin clasificar'}")
        lines.append(f"- Ubicación / URL: {location}")
        if finding.evidence:
            lines.append(f"- Evidencia de verificación: {finding.evidence}")
        lines.append(f"- Reproducción / PoC: {_build_repro_summary(finding)}")
        lines.append("")
    return "\n".join(lines).rstrip()
