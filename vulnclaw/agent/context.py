"""VulnClaw session context management — track pentest state across turns."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field, PrivateAttr

from vulnclaw.agent.blackboard import Blackboard
from vulnclaw.agent.reasoning_state import ReasoningState

# ──────────────────────────────────────────────────────────────
# Los tipos hoja se extrajeron a config/domain_models.py; aquí se reexportan por compatibilidad.
# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: elimina las violaciones V2/V3/V4 — la capa de infraestructura no debe depender inversamente de la capa de dominio.
# ──────────────────────────────────────────────────────────────
from vulnclaw.config.domain_models import (  # noqa: F401 — re-export
    PHASE_TO_ACTION,
    ConstraintViolationEvent,
    EvidenceKind,
    EvidenceRef,
    PentestPhase,
    StepRecord,
    StepStatus,
    TaskConstraints,
    VulnerabilityFinding,
    normalize_action_name,
    validate_action_constraints,
)

# ==============================================================================
# [Refactor P17] Definición de clases de sub-estado
# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: SessionState tenía demasiados campos (20+), violando el principio de responsabilidad única
#          se dividió en 6 clases de sub-estado, cada una a cargo de un ámbito de responsabilidad claro
# Nota auxiliar: estas clases de sub-estado son mantenidas por SessionState mediante composición,
#          el código externo accede a través de @property como proxy, manteniendo compatibilidad hacia atrás
# ==============================================================================

class SessionConfig(BaseModel):
    """Configuración básica de la sesión — gestiona el ciclo de vida de la sesión y la información del objetivo.

    Ámbito de responsabilidad:
    - Objetivo de la sesión (target)
    - Fase actual (phase)
    - Marca de tiempo (started_at)
    - Información de reanudación (resume_summary, resume_meta)
    - Restricciones de la tarea (task_constraints)
    """

    target: Optional[str] = None
    phase: PentestPhase = PentestPhase.IDLE
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resume_summary: str = Field(default="", description="Resumen de logros históricos inyectado al reanudar")
    resume_meta: dict[str, Any] = Field(default_factory=dict, description="Metainformación de reanudación")
    task_constraints: TaskConstraints = Field(default_factory=TaskConstraints)


class VulnerabilityStore(BaseModel):
    """Gestión del almacén de vulnerabilidades — encargada de añadir, eliminar, modificar, consultar y deduplicar vulnerabilidades.

    Ámbito de responsabilidad:
    - Lista de vulnerabilidades (findings)
    - Caché de IDs para deduplicación exacta (_finding_ids_cache)
    - Umbral de deduplicación semántica (semantic_dedup_threshold)

    Estrategia de deduplicación:
    1. Coincidencia exacta de hash por finding_id (rápida)
    2. Coincidencia por similitud semántica (captura distintas formulaciones de la misma vulnerabilidad); en caso de coincidencia, se conserva la de evidencia más sólida
    """

    target: Optional[str] = None
    findings: list[VulnerabilityFinding] = Field(default_factory=list)
    semantic_dedup_threshold: float = Field(
        default=0.75, description="Umbral de similitud para la deduplicación semántica (0-1)"
    )
    # PrivateAttr no está sujeto a las restricciones de nombres de campo de Pydantic; se usa para el seguimiento interno de deduplicación
    _finding_ids_cache: set[str] = PrivateAttr(default_factory=set)

    def set_checkpoint_callback(
        self, callback: Callable[["SessionState", str], None] | None
    ) -> None:
        """Install a persistence callback fired at durable state boundaries."""
        self._checkpoint_callback = callback

    def _notify_checkpoint(self, reason: str) -> None:
        if self._checkpoint_callback is None:
            return
        self._checkpoint_callback(self, reason)

    def add_finding(self, finding: VulnerabilityFinding) -> bool:
        """Añade un hallazgo de vulnerabilidad, con deduplicación automática.

        Returns:
            True if finding was added, False if duplicate (skipped).
        """
        # Genera finding_id (si aún no existe)
        if hasattr(finding, "_sync_status_fields"):
            finding._sync_status_fields()
        if not finding.finding_id:
            finding.finding_id = finding._generate_finding_id()

        # Tie the finding to the owning target when the caller didn't set one.
        if not finding.target and self.target:
            finding.target = self.target

        # Primera capa: deduplicación exacta por finding_id
        if finding.finding_id in self._finding_ids_cache:
            print(f"[DEDUP] Vulnerabilidad duplicada omitida: {finding.title} (ID: {finding.finding_id})")
            return False

        # Segunda capa: deduplicación por similitud semántica
        from vulnclaw.agent.finding_similarity import (
            _evidence_strength,
            finding_similarity,
        )

        for idx, existing in enumerate(self.findings):
            if finding_similarity(finding, existing) >= self.semantic_dedup_threshold:
                # Coincidencia semántica: se conserva la de evidencia más sólida
                if _evidence_strength(finding) > _evidence_strength(existing):
                    print(
                        f"[DEDUP-SEM] Duplicado semántico, se reemplaza por la vulnerabilidad con evidencia más sólida: "
                        f"{finding.title} reemplaza a {existing.title}"
                    )
                    self._finding_ids_cache.discard(existing.finding_id)
                    self._finding_ids_cache.add(finding.finding_id)
                    self.findings[idx] = finding
                    self._notify_checkpoint("finding_updated")
                else:
                    print(f"[DEDUP-SEM] Vulnerabilidad semánticamente duplicada omitida: {finding.title}")
                return False

        # Adjunta la procedencia del skill (si no se proporcionó explícitamente y hay una selección activa).
        # Se hace una copia profunda para que la lista references_loaded no se comparta con
        # active_skill_selection — de lo contrario, record_loaded_reference() modificaría
        # retroactivamente la procedencia de vulnerabilidades ya registradas.
        if finding.skill_provenance is None and self.active_skill_selection is not None:
            finding.skill_provenance = copy.deepcopy(self.active_skill_selection)

        # Se agrega al conjunto de seguimiento y a la lista
        self._finding_ids_cache.add(finding.finding_id)
        self.findings.append(finding)
        self._notify_checkpoint("finding_added")
        return True

    def set_active_skill_selection(self, provenance: Optional[dict[str, Any]]) -> bool:
        """Record the active skill selection; emit a run event when it changes.

        Args:
            provenance: A ``SkillSelection.to_provenance()`` dict (or None).

        Returns:
            True if the selection changed from the previous turn.
        """
        prev = self.active_skill_selection
        changed = (prev or {}).get("primary") != (provenance or {}).get("primary") or (
            (prev or {}).get("supporting") != (provenance or {}).get("supporting")
        )
        # Same bundle as last turn: carry over references already loaded under it
        # so provenance keeps a complete record across turns.
        if not changed and prev is not None and provenance is not None:
            loaded = prev.get("references_loaded")
            if loaded and not provenance.get("references_loaded"):
                provenance = {**provenance, "references_loaded": list(loaded)}
        self.active_skill_selection = provenance
        if changed:
            event = {
                "kind": "skill_selection_changed" if provenance is not None else "skill_selection_cleared",
                "timestamp": datetime.now().isoformat(),
                "primary": (provenance or {}).get("primary"),
                "supporting": (provenance or {}).get("supporting", []),
                "reason": (provenance or {}).get("reason", ""),
                "confidence": (provenance or {}).get("confidence", 0.0),
            }
            self.skill_selection_events.append(event)
            self.skill_selection_events = self.skill_selection_events[-50:]
        return changed

    def record_loaded_reference(self, skill_name: str, ref_name: str) -> None:
        """Record a reference loaded via ``load_skill_reference`` onto provenance.

        Findings created after this call inherit the reference in their
        ``skill_provenance['references_loaded']``.
        """
        if self.active_skill_selection is None:
            return
        entry = f"{skill_name}/{ref_name}" if skill_name else ref_name
        loaded = self.active_skill_selection.setdefault("references_loaded", [])
        if entry and entry not in loaded:
            loaded.append(entry)

    def get_verified_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades verificadas."""
        return [f for f in self.findings if f.verified]

    def get_rejected_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades rechazadas (falsos positivos)."""
        return [f for f in self.findings if f.verification_status == "rejected"]

    def get_pending_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades pendientes de verificación."""
        return [f for f in self.findings if f.verification_status == "pending"]

    def get_candidate_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene las vulnerabilidades candidatas de baja confianza."""
        return [f for f in self.findings if f.lifecycle_status == "candidate"]

    def get_pending_verification_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene las vulnerabilidades con evidencia pendiente de verificación."""
        return [f for f in self.findings if f.lifecycle_status == "pending_verification"]

    def get_manual_review_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene las vulnerabilidades que requieren revisión manual."""
        return [
            f
            for f in self.findings
            if (
                f.lifecycle_status == "needs_manual_review"
                or (
                    not f.verified
                    and f.verification_status != "rejected"
                    and f.severity in {"Critical", "High"}
                    and f.lifecycle_status in {"candidate", "pending_verification"}
                )
            )
        ]


class ReconState(BaseModel):
    """Gestión del estado de reconocimiento — hace seguimiento del avance de la recolección de información.

    Ámbito de responsabilidad:
    - Datos de reconocimiento (recon_data)
    - Grado de avance del modelo de cuatro dimensiones (recon_dimensions_completed)
    - Estado de activación de la dimensión cuatro (recon_dimension4_active)

    Modelo de cuatro dimensiones:
    - Dimensión uno: información del servidor (puerto/IP real/SO/middleware/base de datos)
    - Dimensión dos: información del sitio web (arquitectura/huella/WAF/directorios sensibles/filtración de código fuente/sitios asociados/segmento C)
    - Dimensión tres: información del dominio (WHOIS/registro ICP/subdominios/DNS/transparencia de certificados)
    - Dimensión cuatro: información de personas (activación condicional — solo se activa cuando hay una necesidad explícita de ingeniería social)
    """

    recon_data: dict[str, Any] = Field(default_factory=dict)
    recon_dimensions_completed: dict[str, bool] = Field(
        default_factory=lambda: {
            "server": False,
            "website": False,
            "domain": False,
            "personnel": False,
        },
        description="Seguimiento del avance del modelo de cuatro dimensiones de recolección de información",
    )
    recon_dimension4_active: bool = Field(
        default=False, description="Si la dimensión cuatro (información de personas) está activada"
    )

    def add_recon_subdomain(self, subdomain: str) -> None:
        """Registra los subdominios descubiertos en recon_data['subdomains']."""
        if "subdomains" not in self.recon_data:
            self.recon_data["subdomains"] = []
        if subdomain and subdomain not in self.recon_data["subdomains"]:
            self.recon_data["subdomains"].append(subdomain)

    def mark_recon_dimension(self, dimension: str) -> None:
        """Marca una dimensión de reconocimiento como completada.

        Args:
            dimension: uno de 'server', 'website', 'domain', 'personnel'
        """
        if dimension in self.recon_dimensions_completed:
            self.recon_dimensions_completed[dimension] = True

    def is_recon_complete(self) -> bool:
        """Comprueba si todas las dimensiones de reconocimiento activas se completaron al menos una vez.

        La dimensión cuatro (información de personas) solo se verifica cuando está activada.
        """
        for dim, completed in self.recon_dimensions_completed.items():
            if dim == "personnel" and not self.recon_dimension4_active:
                continue
            if not completed:
                return False
        return True

    def get_recon_status_text(self) -> str:
        """Obtiene el estado de avance de las dimensiones de reconocimiento en formato legible para humanos."""
        parts = []
        dim_names = {
            "server": "Dimensión uno (servidor)",
            "website": "Dimensión dos (sitio web)",
            "domain": "Dimensión tres (dominio)",
            "personnel": "Dimensión cuatro (personas)",
        }
        for dim, completed in self.recon_dimensions_completed.items():
            if dim == "personnel" and not self.recon_dimension4_active:
                continue
            name = dim_names.get(dim, dim)
            parts.append(f"{'✅' if completed else '❌'} {name}")
        incomplete = [
            dim
            for dim, done in self.recon_dimensions_completed.items()
            if (dim != "personnel" or self.recon_dimension4_active) and not done
        ]
        status = " | ".join(parts)
        if incomplete:
            status += f"\n→ Aún quedan {len(incomplete)} dimensiones sin revisar, continúa recolectando, no marques [DONE]"
        return status


class ReasoningSnapshot(BaseModel):
    """Instantánea del estado de razonamiento — almacena los datos centrales del motor de razonamiento.

    Ámbito de responsabilidad:
    - Estado de razonamiento (reasoning)
    - Grafo de pizarra (board)
    - Instantánea de reflexión (reflexion_snapshot)
    - Hechos confirmados (confirmed_facts)
    - Hipótesis no verificadas (unverified_assumptions)
    """

    reasoning: ReasoningState = Field(default_factory=ReasoningState)
    board: Blackboard = Field(default_factory=Blackboard)
    reflexion_snapshot: dict[str, Any] = Field(default_factory=dict)
    confirmed_facts: list[str] = Field(
        default_factory=list, description="Hechos confirmados y verificados mediante herramientas"
    )
    unverified_assumptions: list[str] = Field(
        default_factory=list, description="Hipótesis en las que se basó el razonamiento pero que no fueron verificadas"
    )

    def add_confirmed_fact(self, fact: str) -> None:
        """Añade un hecho confirmado (verificado mediante la salida de una herramienta)."""
        if fact and fact not in self.confirmed_facts:
            self.confirmed_facts.append(fact)
        if fact:
            self.reasoning.add_fact(
                key=self._fact_key_from_text(fact),
                value=fact,
                source="confirmed_fact",
                confidence=0.9,
            )

    def _fact_key_from_text(self, fact: str) -> str:
        """Infiere la clave de tipo de hecho a partir del texto del hecho."""
        text = fact.lower()
        if "cve-" in text:
            return "cve"
        if "http://" in text or "https://" in text:
            return "url"
        if "port" in text or "puerto" in fact:
            return "port"
        if "server" in text or "x-powered-by" in text:
            return "service"
        if "waf" in text:
            return "waf"
        return "confirmed_fact"

    def add_assumption(self, assumption: str) -> None:
        """Añade una hipótesis no verificada."""
        if assumption and assumption not in self.unverified_assumptions:
            self.unverified_assumptions.append(assumption)


class ConstraintManager(BaseModel):
    """Gestión de restricciones — hace seguimiento de los eventos de violación de restricciones.

    Ámbito de responsabilidad:
    - Lista de mensajes de violación de restricciones (constraint_violations)
    - Eventos estructurados de violación de restricciones (constraint_violation_events)
    """

    constraint_violations: list[str] = Field(default_factory=list)
    constraint_violation_events: list[ConstraintViolationEvent] = Field(
        default_factory=list
    )

    def add_constraint_violation(self, message: str) -> None:
        """Registra un evento de auditoría de violación de restricciones."""
        if not message:
            return
        if message not in self.constraint_violations:
            self.constraint_violations.append(message)
        elif self.constraint_violations and self.constraint_violations[-1] != message:
            self.constraint_violations.append(message)
        # Conserva los últimos 20 registros
        self.constraint_violations = self.constraint_violations[-20:]

    def add_constraint_violation_event(
        self,
        *,
        source: str,
        action: str = "",
        tool_name: str = "",
        code: str = "",
        severity: str = "medium",
        summary: str,
        detail: str = "",
        phase: str = "",
    ) -> None:
        """Registra un evento estructurado de auditoría de violación de restricciones."""
        event = ConstraintViolationEvent(
            source=source,
            action=action,
            tool_name=tool_name,
            code=code,
            severity=severity,
            phase=phase,
            summary=summary,
            detail=detail or summary,
        )
        self.constraint_violation_events.append(event)
        self.constraint_violation_events = self.constraint_violation_events[-20:]
        self.add_constraint_violation(summary)


class ExecutionHistory(BaseModel):
    """Historial de ejecución — registra los pasos de ejecución y las notas del pentest.

    [Refactor P18] Se adopta step_records como formato principal de registro:
    - step_records: registros de pasos estructurados (fuente de datos principal)
    - executed_steps: capa de compatibilidad @property, derivada de step_records
    - notes: notas de la sesión

    Modificado por: Nyaecho
    Fecha de modificación: 2026-07-08
    Motivo de la modificación: unifica tres sistemas paralelos de seguimiento de estado, elimina redundancia de datos
    Nota auxiliar: executed_steps ahora es una propiedad de solo lectura; toda escritura debe hacerse mediante add_step()
    """

    # [Modificación P18] Se elimina el campo executed_steps, se convierte en @property
    step_records: list[StepRecord] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @property
    def executed_steps(self) -> list[str]:
        """[Capa de compatibilidad P18] Genera la lista de strings original a partir de step_records.

        Compatible hacia atrás con todos los consumidores (construcción de prompts, generación de informes, persistencia, etc.).
        Se genera dinámicamente en cada acceso, garantizando la consistencia de los datos.
        """
        return [r.to_legacy_string() for r in self.step_records]

    def add_step(
        self,
        step: str,
        action: str = "",
        target: str = "",
        result: str = "",
        status: StepStatus = StepStatus.INFO,
        detail: str = "",
        phase: PentestPhase = PentestPhase.IDLE,
    ) -> None:
        """Registra un paso de ejecución.

        [Modificación P18] Solo escribe en step_records, ya no escribe en executed_steps.
        executed_steps se genera dinámicamente desde step_records mediante @property.

        Args:
            step: cadena de paso original (compatibilidad hacia atrás)
            action: descripción breve de la acción
            target: objetivo de la acción
            result: resumen del resultado
            status: estado de ejecución
            detail: información detallada
            phase: fase actual
        """
        # Conserva el paso original (compatibilidad hacia atrás); deduplicación consecutiva para evitar saturar el título
        if not self.executed_steps or self.executed_steps[-1] != step:
            self.executed_steps.append(step)

        # Crea el registro estructurado
        if action:
            record = StepRecord(
                phase=phase,
                round=len(self.executed_steps),
                action=action,
                target=target,
                result=result or step[:60],
                status=status,
                detail=detail,
            )
            self.step_records.append(record)
        self._notify_checkpoint("step_complete")

    def add_note(self, note: str) -> None:
        """Añade una nota de sesión, filtrando ruido de código/símbolos."""
        # Rechaza notas que son principalmente código/símbolos — contaminarían la extracción de evidencia
        chinese = re.findall(r"[\u4e00-\u9fff]", note)
        code_symbols = re.findall(
            r"[{}()=+*/<>\-\\[\\]|;|import |def |return |print\(|requests\.|socket\.|re\.|sys\.]",
            note,
        )
        if len(note) > 20 and len(code_symbols) > len(chinese) * 0.5:
            return
        # Rechaza notas muy cortas
        if len(note) < 5 or note in ("---", "**", ">>>", "..."):
            return
        self.notes.append(note)

    def get_step_summary(self) -> dict[str, Any]:
        """Genera el resumen de la ruta de ataque.

        [Modificación P18] Se elimina la lógica de respaldo, solo se usa step_records.
        executed_steps ahora es una @property, derivada de step_records.
        """
        if self.step_records:
            return self._build_step_summary_from_records()
        return {"total_steps": 0, "phases": {}, "key_findings": []}

    def _build_step_summary_from_records(self) -> dict[str, Any]:
        """Construye el resumen a partir de los step_records estructurados."""
        phases: dict[str, list[StepRecord]] = {}
        for record in self.step_records:
            phase_name = record.phase.value
            if phase_name not in phases:
                phases[phase_name] = []
            phases[phase_name].append(record)

        phase_summaries = {}
        for phase_name, records in phases.items():
            phase_summaries[phase_name] = {
                "count": len(records),
                "actions": list(set(r.action for r in records)),
                "success_count": len([r for r in records if r.status == StepStatus.SUCCESS]),
                "failure_count": len([r for r in records if r.status == StepStatus.FAILURE]),
                "key_results": [r.to_brief() for r in records if r.status == StepStatus.SUCCESS][
                    :5
                ],
            }

        key_findings = [
            r.to_brief() for r in self.step_records if r.status == StepStatus.SUCCESS and r.result
        ][:10]

        return {
            "total_steps": len(self.step_records),
            "phases": phase_summaries,
            "key_findings": key_findings,
        }




# ==============================================================================
# [Fin del refactor P17] Definición de clases de sub-estado
# ==============================================================================


# ==============================================================================
# [Refactor P17] SessionState refactorizado con patrón de composición
# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: SessionState tenía originalmente 22 campos, violando el principio de responsabilidad única
#          se adopta el patrón de composición, delegando la responsabilidad a 6 clases de sub-estado
# Nota auxiliar: se mantiene el proxy @property de todos los campos originales, garantizando compatibilidad hacia atrás
#          las instancias de sub-estado son PrivateAttr, no afectan la serialización
#          los métodos save()/load() permanecen sin cambios, formato JSON compatible
# ==============================================================================

class SessionState(BaseModel):
    """Full session state for a pentest engagement.

    [Refactor P17] Se adopta el patrón de composición, usando internamente 6 clases de sub-estado:
    - SessionConfig: configuración de la sesión
    - VulnerabilityStore: gestión de vulnerabilidades
    - ReconState: estado de reconocimiento
    - ReasoningSnapshot: estado de razonamiento
    - ConstraintManager: gestión de restricciones
    - ExecutionHistory: historial de ejecución

    Todos los campos originales mantienen compatibilidad hacia atrás mediante proxy @property.
    """

    # ★ Instancias de sub-estado (PrivateAttr, no afectan la serialización)
    _config: SessionConfig = PrivateAttr(default_factory=SessionConfig)
    _vulnerabilities: VulnerabilityStore = PrivateAttr(default_factory=VulnerabilityStore)
    _recon: ReconState = PrivateAttr(default_factory=ReconState)
    _reasoning_snapshot: ReasoningSnapshot = PrivateAttr(default_factory=ReasoningSnapshot)
    _constraints: ConstraintManager = PrivateAttr(default_factory=ConstraintManager)
    _history: ExecutionHistory = PrivateAttr(default_factory=ExecutionHistory)

    # ★ Los campos originales se conservan por compatibilidad de serialización; el valor real se almacena en el sub-estado
    # Nota: estos campos se serializan en model_dump(), pero la lectura/escritura real pasa por el proxy @property

    def model_post_init(self, __context: Any) -> None:
        """Sincroniza los valores de los campos con el sub-estado tras la inicialización."""
        # Restaura el sub-estado a partir de los datos serializados
        self._config = SessionConfig(
            target=self.target,
            phase=self.phase,
            started_at=self.started_at,
            resume_summary=self.resume_summary,
            resume_meta=self.resume_meta,
            task_constraints=self.task_constraints,
        )
        self._vulnerabilities = VulnerabilityStore(
            target=self.target,
            findings=self.findings,
            semantic_dedup_threshold=self.semantic_dedup_threshold,
        )
        self._recon = ReconState(
            recon_data=self.recon_data,
            recon_dimensions_completed=self.recon_dimensions_completed,
            recon_dimension4_active=self.recon_dimension4_active,
        )
        self._reasoning_snapshot = ReasoningSnapshot(
            reasoning=self.reasoning,
            board=self.board,
            reflexion_snapshot=self.reflexion_snapshot,
            confirmed_facts=self.confirmed_facts,
            unverified_assumptions=self.unverified_assumptions,
        )
        self._constraints = ConstraintManager(
            constraint_violations=self.constraint_violations,
            constraint_violation_events=self.constraint_violation_events,
        )
        self._history = ExecutionHistory(
            step_records=self.step_records,
            notes=self.notes,
        )

    # ==========================================================================
    # Definición de campos (por compatibilidad de serialización)
    # ==========================================================================

    target: Optional[str] = None
    phase: PentestPhase = PentestPhase.IDLE
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resume_summary: str = Field(default="", description="Resumen de logros históricos inyectado al reanudar")
    resume_meta: dict[str, Any] = Field(default_factory=dict, description="Metainformación de reanudación")
    task_constraints: TaskConstraints = Field(default_factory=TaskConstraints)
    constraint_violations: list[str] = Field(default_factory=list)
    constraint_violation_events: list[ConstraintViolationEvent] = Field(default_factory=list)
    reasoning: ReasoningState = Field(default_factory=ReasoningState)
    board: Blackboard = Field(default_factory=Blackboard)
    reflexion_snapshot: dict[str, Any] = Field(default_factory=dict)
    findings: list[VulnerabilityFinding] = Field(default_factory=list)
    recon_data: dict[str, Any] = Field(default_factory=dict)
    # [Modificación P18] executed_steps se convierte en @property, derivada de step_records
    # Ya no se define como campo, sino que se genera dinámicamente mediante @property
    step_records: list[StepRecord] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    confirmed_facts: list[str] = Field(default_factory=list, description="Hechos confirmados y verificados mediante herramientas")
    unverified_assumptions: list[str] = Field(
        default_factory=list, description="Hipótesis en las que se basó el razonamiento pero que no fueron verificadas"
    )
    recon_dimensions_completed: dict[str, bool] = Field(
        default_factory=lambda: {
            "server": False,
            "website": False,
            "domain": False,
            "personnel": False,
        },
        description="Seguimiento del avance del modelo de cuatro dimensiones de recolección de información",
    )
    recon_dimension4_active: bool = Field(default=False, description="Si la dimensión cuatro (información de personas) está activada")
    # ★ Active skill selection for this turn/child task — structured provenance
    # source. Stored as a plain dict to avoid importing the resolver here.
    active_skill_selection: Optional[dict[str, Any]] = Field(
        default=None, description="Active SkillSelection.to_provenance() for the current turn"
    )
    # ★ Run events emitted whenever the active skill selection changes.
    skill_selection_events: list[dict[str, Any]] = Field(
        default_factory=list, description="Audit log of skill-selection changes"
    )
    semantic_dedup_threshold: float = Field(
        default=0.75, description="Umbral de similitud para la deduplicación semántica (0-1)"
    )

    # ★ Seguimiento de deduplicación de vulnerabilidades (PrivateAttr)
    _finding_ids_cache: set[str] = PrivateAttr(default_factory=set)
    _checkpoint_callback: Callable[["SessionState", str], None] | None = PrivateAttr(
        default=None
    )

    def set_checkpoint_callback(
        self, callback: Callable[["SessionState", str], None] | None
    ) -> None:
        """Install a persistence callback fired at durable state boundaries."""
        self._checkpoint_callback = callback

    def _notify_checkpoint(self, reason: str) -> None:
        if self._checkpoint_callback is None:
            return
        self._checkpoint_callback(self, reason)

    # ==========================================================================
    # Proxy @property (mantiene compatibilidad hacia atrás)
    # ==========================================================================

    @property
    def executed_steps(self) -> list[str]:
        """[Capa de compatibilidad P18] Genera la lista de strings original a partir de step_records.

        Compatible hacia atrás con todos los consumidores (construcción de prompts, generación de informes, persistencia, etc.).
        Se genera dinámicamente en cada acceso, garantizando la consistencia de los datos.
        """
        return [r.to_legacy_string() for r in self.step_records]

    @executed_steps.setter
    def executed_steps(self, value: list[str]) -> None:
        """[Capa de compatibilidad P18] Permite asignar executed_steps (compatibilidad hacia atrás).

        Convierte la lista de strings del formato antiguo a step_records.
        """
        self.step_records = [
            StepRecord.from_legacy_string(s, self.phase) for s in value
        ]
        # Sincroniza con el sub-estado
        self._history.step_records = self.step_records

    # Nota: los demás campos ya son de acceso directo
    # Los métodos de las clases de sub-estado se invocan mediante métodos delegados

    # ==========================================================================
    # Métodos delegados (delegan a las clases de sub-estado)
    # ==========================================================================

    def add_finding(self, finding: VulnerabilityFinding) -> bool:
        """Añade un hallazgo de vulnerabilidad.

        [Refactor P17] Actualiza simultáneamente self.findings y self._finding_ids_cache,
        manteniendo la compatibilidad hacia atrás. La lógica de deduplicación se delega a VulnerabilityStore.
        """
        # Genera finding_id (si aún no existe)
        if hasattr(finding, "_sync_status_fields"):
            finding._sync_status_fields()
        if not finding.finding_id:
            finding.finding_id = finding._generate_finding_id()

        # Tie the finding to the owning target when the caller didn't set one.
        if not finding.target and self.target:
            finding.target = self.target

        # Primera capa: deduplicación exacta por finding_id
        if finding.finding_id in self._finding_ids_cache:
            print(f"[DEDUP] Vulnerabilidad duplicada omitida: {finding.title} (ID: {finding.finding_id})")
            return False

        # Segunda capa: deduplicación por similitud semántica
        from vulnclaw.agent.finding_similarity import (
            _evidence_strength,
            finding_similarity,
        )

        for idx, existing in enumerate(self.findings):
            if finding_similarity(finding, existing) >= self.semantic_dedup_threshold:
                # Coincidencia semántica: se conserva la de evidencia más sólida
                if _evidence_strength(finding) > _evidence_strength(existing):
                    print(
                        f"[DEDUP-SEM] Duplicado semántico, se reemplaza por la vulnerabilidad con evidencia más sólida: "
                        f"{finding.title} reemplaza a {existing.title}"
                    )
                    self._finding_ids_cache.discard(existing.finding_id)
                    self._finding_ids_cache.add(finding.finding_id)
                    self.findings[idx] = finding
                else:
                    print(f"[DEDUP-SEM] Vulnerabilidad semánticamente duplicada omitida: {finding.title}")
                return False

        # Adjunta la procedencia del skill (si no se proporcionó explícitamente y hay una selección activa).
        # Se hace una copia profunda para que la lista references_loaded no se comparta con
        # active_skill_selection — de lo contrario, record_loaded_reference() modificaría
        # retroactivamente la procedencia de vulnerabilidades ya registradas.
        if finding.skill_provenance is None and self.active_skill_selection is not None:
            finding.skill_provenance = copy.deepcopy(self.active_skill_selection)

        # Se agrega al conjunto de seguimiento y a la lista
        self._finding_ids_cache.add(finding.finding_id)
        self.findings.append(finding)

        # Sincroniza con el sub-estado
        self._vulnerabilities.findings = self.findings
        self._vulnerabilities._finding_ids_cache = self._finding_ids_cache

        return True

    def get_verified_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades verificadas, delegando a VulnerabilityStore."""
        return self._vulnerabilities.get_verified_findings()

    def get_rejected_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades rechazadas, delegando a VulnerabilityStore."""
        return self._vulnerabilities.get_rejected_findings()

    def get_pending_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene la lista de vulnerabilidades pendientes de verificación, delegando a VulnerabilityStore."""
        return self._vulnerabilities.get_pending_findings()

    def get_candidate_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene las vulnerabilidades candidatas, delegando a VulnerabilityStore."""
        return self._vulnerabilities.get_candidate_findings()

    def get_pending_verification_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene las vulnerabilidades con evidencia pendiente de verificación, delegando a VulnerabilityStore."""
        return self._vulnerabilities.get_pending_verification_findings()

    def get_manual_review_findings(self) -> list[VulnerabilityFinding]:
        """Obtiene las vulnerabilidades que requieren revisión manual, delegando a VulnerabilityStore."""
        return self._vulnerabilities.get_manual_review_findings()

    def add_recon_subdomain(self, subdomain: str) -> None:
        """Registra los subdominios descubiertos.

        [Refactor P17] Actualiza simultáneamente self.recon_data, manteniendo la compatibilidad hacia atrás.
        """
        if "subdomains" not in self.recon_data:
            self.recon_data["subdomains"] = []
        if subdomain and subdomain not in self.recon_data["subdomains"]:
            self.recon_data["subdomains"].append(subdomain)
        # Sincroniza con el sub-estado
        self._recon.recon_data = self.recon_data

    def mark_recon_dimension(self, dimension: str) -> None:
        """Marca una dimensión de reconocimiento como completada.

        [Refactor P17] Actualiza simultáneamente self.recon_dimensions_completed, manteniendo la compatibilidad hacia atrás.
        """
        if dimension in self.recon_dimensions_completed:
            self.recon_dimensions_completed[dimension] = True
            # Sincroniza con el sub-estado
            self._recon.recon_dimensions_completed = self.recon_dimensions_completed

    def is_recon_complete(self) -> bool:
        """Comprueba si el reconocimiento está completo, delegando a ReconState."""
        return self._recon.is_recon_complete()

    def get_recon_status_text(self) -> str:
        """Obtiene el texto de estado del reconocimiento, delegando a ReconState."""
        return self._recon.get_recon_status_text()

    def add_constraint_violation(self, message: str) -> None:
        """Registra una violación de restricción.

        [Refactor P17] Actualiza simultáneamente self.constraint_violations, manteniendo la compatibilidad hacia atrás.
        """
        if not message:
            return
        if message not in self.constraint_violations:
            self.constraint_violations.append(message)
        elif self.constraint_violations and self.constraint_violations[-1] != message:
            self.constraint_violations.append(message)
        # Conserva los últimos 20 registros
        self.constraint_violations = self.constraint_violations[-20:]
        # Sincroniza con el sub-estado
        self._constraints.constraint_violations = self.constraint_violations

    def add_constraint_violation_event(
        self,
        *,
        source: str,
        action: str = "",
        tool_name: str = "",
        code: str = "",
        severity: str = "medium",
        summary: str,
        detail: str = "",
    ) -> None:
        """Registra un evento estructurado de violación de restricción.

        [Refactor P17] Actualiza simultáneamente self.constraint_violation_events, manteniendo la compatibilidad hacia atrás.
        """
        phase_str = self.phase.value if hasattr(self.phase, "value") else str(self.phase)
        event = ConstraintViolationEvent(
            source=source,
            action=action,
            tool_name=tool_name,
            code=code,
            severity=severity,
            phase=phase_str,
            summary=summary,
            detail=detail or summary,
        )
        self.constraint_violation_events.append(event)
        self.constraint_violation_events = self.constraint_violation_events[-20:]
        self.add_constraint_violation(summary)
        # Sincroniza con el sub-estado
        self._constraints.constraint_violation_events = self.constraint_violation_events

    def add_step(
        self,
        step: str,
        action: str = "",
        target: str = "",
        result: str = "",
        status: StepStatus = StepStatus.INFO,
        detail: str = "",
    ) -> None:
        """Registra un paso de ejecución.

        [Modificación P18] Solo escribe en step_records, ya no escribe en executed_steps.
        executed_steps ahora es una @property, generada dinámicamente desde step_records.
        """
        # [Modificación P18] Siempre crea el registro estructurado, usando step como valor por defecto de action
        record = StepRecord(
            phase=self.phase,
            round=len(self.step_records) + 1,
            action=action or step[:60],
            target=target,
            result=result or step[:60],
            status=status,
            detail=detail,
        )
        self.step_records.append(record)
        # Sincroniza con el sub-estado
        self._history.step_records = self.step_records

    def get_step_summary(self) -> dict[str, Any]:
        """Genera el resumen de la ruta de ataque, delegando a ExecutionHistory."""
        return self._history.get_step_summary()

    def add_note(self, note: str) -> None:
        """Añade una nota de sesión.

        [Refactor P17] Actualiza simultáneamente self.notes, manteniendo la compatibilidad hacia atrás.
        """
        # Rechaza notas que son principalmente código/símbolos
        chinese = re.findall(r"[\u4e00-\u9fff]", note)
        code_symbols = re.findall(
            r"[{}()=+*/<>\-\\[\\]|;|import |def |return |print\(|requests\.|socket\.|re\.|sys\.]",
            note,
        )
        if len(note) > 20 and len(code_symbols) > len(chinese) * 0.5:
            return
        # Rechaza notas muy cortas
        if len(note) < 5 or note in ("---", "**", ">>>", "..."):
            return
        self.notes.append(note)
        # Sincroniza con el sub-estado
        self._history.notes = self.notes

    def set_active_skill_selection(self, provenance: Optional[dict[str, Any]]) -> bool:
        """Record the active skill selection; emit a run event when it changes.

        Args:
            provenance: A ``SkillSelection.to_provenance()`` dict (or None).

        Returns:
            True if the selection changed from the previous turn.
        """
        prev = self.active_skill_selection
        changed = (prev or {}).get("primary") != (provenance or {}).get("primary") or (
            (prev or {}).get("supporting") != (provenance or {}).get("supporting")
        )
        # Same bundle as last turn: carry over references already loaded under it
        # so provenance keeps a complete record across turns.
        if not changed and prev is not None and provenance is not None:
            loaded = prev.get("references_loaded")
            if loaded and not provenance.get("references_loaded"):
                provenance = {**provenance, "references_loaded": list(loaded)}
        self.active_skill_selection = provenance
        if changed:
            event = {
                "kind": "skill_selection_changed" if provenance is not None else "skill_selection_cleared",
                "timestamp": datetime.now().isoformat(),
                "primary": (provenance or {}).get("primary"),
                "supporting": (provenance or {}).get("supporting", []),
                "reason": (provenance or {}).get("reason", ""),
                "confidence": (provenance or {}).get("confidence", 0.0),
            }
            self.skill_selection_events.append(event)
            self.skill_selection_events = self.skill_selection_events[-50:]
        self._notify_checkpoint("skill_selection_changed")
        return changed

    def record_loaded_reference(self, skill_name: str, ref_name: str) -> None:
        """Track a reference loaded under the current skill selection."""
        if self.active_skill_selection is None:
            return
        entry = f"{skill_name}/{ref_name}" if skill_name else ref_name
        loaded = self.active_skill_selection.setdefault("references_loaded", [])
        if entry and entry not in loaded:
            loaded.append(entry)

    def add_confirmed_fact(self, fact: str) -> None:
        """Añade un hecho confirmado.

        [Refactor P17] Actualiza simultáneamente self.confirmed_facts y self.reasoning,
        manteniendo la compatibilidad hacia atrás.
        """
        if fact and fact not in self.confirmed_facts:
            self.confirmed_facts.append(fact)
        if fact:
            self.reasoning.add_fact(
                key=self._fact_key_from_text(fact),
                value=fact,
                source="confirmed_fact",
                confidence=0.9,
            )
        # Sincroniza con el sub-estado
        self._reasoning_snapshot.confirmed_facts = self.confirmed_facts
        self._reasoning_snapshot.reasoning = self.reasoning

    def _fact_key_from_text(self, fact: str) -> str:
        """Infiere la clave de tipo de hecho a partir del texto del hecho."""
        text = fact.lower()
        if "cve-" in text:
            return "cve"
        if "http://" in text or "https://" in text:
            return "url"
        if "port" in text or "puerto" in fact:
            return "port"
        if "server" in text or "x-powered-by" in text:
            return "service"
        if "waf" in text:
            return "waf"
        return "confirmed_fact"

    def add_assumption(self, assumption: str) -> None:
        """Añade una hipótesis no verificada."""
        if assumption and assumption not in self.unverified_assumptions:
            self.unverified_assumptions.append(assumption)
        # Sincroniza con el sub-estado
        self._reasoning_snapshot.unverified_assumptions = self.unverified_assumptions

    def get_constraints_prompt_block(self) -> str:
        """Obtiene el bloque de restricciones para el prompt, delegando a TaskConstraints."""
        return self.task_constraints.to_prompt_block()

    def advance_phase(self, phase: PentestPhase) -> None:
        """Cambia a una nueva fase."""
        old_phase = self.phase
        self.phase = phase
        # Registra el cambio de fase
        self.add_step(
            step=f"cambio de fase → {phase.value}",
            action="cambio de fase",
            target=f"{old_phase.value} → {phase.value}",
            result=f"entrando en la fase {phase.value}",
            status=StepStatus.INFO,
        )
        self._notify_checkpoint("phase_transition")

    def save(self, path: Optional[Path] = None) -> Path:
        """Guarda el estado de la sesión en un archivo JSON.

        [Modificación P18] Garantiza que executed_steps se serialice en el JSON,
        manteniendo la compatibilidad hacia atrás.
        """
        if path is None:
            from vulnclaw.config.settings import SESSIONS_DIR

            safe_target = (self.target or "unknown").replace("/", "_").replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = SESSIONS_DIR / f"{timestamp}_{safe_target}.json"

        path.parent.mkdir(parents=True, exist_ok=True)
        # [Compatibilidad P18] Obtiene los datos serializados y añade executed_steps
        data = self.model_dump(mode="json")
        data["executed_steps"] = self.executed_steps
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, path: Path) -> "SessionState":
        """Carga el estado de la sesión desde un archivo JSON.

        [Modificación P18] Procesa el JSON de formato antiguo (que contiene el campo executed_steps),
        convirtiéndolo al formato step_records.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # [Compatibilidad P18] Si solo hay executed_steps, se convierte a step_records
        if "executed_steps" in data and "step_records" not in data:
            data["step_records"] = [
                StepRecord.from_legacy_string(s) for s in data["executed_steps"]
            ]

        # [Compatibilidad P18] Elimina el campo executed_steps para evitar errores de validación de Pydantic
        data.pop("executed_steps", None)

        return cls(**data)

# ==============================================================================
# [Fin del refactor P17] SessionState refactorizado con patrón de composición
# ==============================================================================


class ContextManager:
    """Manages conversation context and session state."""

    def __init__(self, max_history: int = 200) -> None:
        self.max_history = max_history
        self.messages: list[dict[str, str]] = []
        self.state = SessionState()

    def add_user_message(self, content: str) -> None:
        """Add a user message to context."""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to context."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_system_message(self, content: str) -> None:
        """Add a system message (inserted at beginning)."""
        # System messages are handled separately in the API call
        pass

    def get_messages(self) -> list[dict[str, str]]:
        """Get conversation messages for API call."""
        return self.messages.copy()

    def reset(self) -> None:
        """Reset context and session state."""
        self.messages = []
        self.state = SessionState()

    def _trim(self) -> None:
        """Trim old messages to stay within limit.

        Instead of blindly dropping old messages, we compress them
        into a summary to preserve key discoveries for multi-round loops.
        """
        if len(self.messages) <= self.max_history:
            return

        # Keep the most recent 70% of messages intact
        keep_count = int(self.max_history * 0.7)
        recent = self.messages[-keep_count:]
        old = self.messages[:-keep_count]

        # Compress old messages into a summary instead of discarding
        summary = self._compress_messages(old)

        self.messages = []
        if summary:
            self.messages.append(
                {
                    "role": "system",
                    "content": f"[Resumen de la sesión anterior]\n{summary}",
                }
            )
        self.messages.extend(recent)

    @staticmethod
    def _compress_messages(messages: list[dict[str, str]]) -> str:
        """Compress a list of messages into a concise summary.

        Extracts key findings, tool results, and discoveries from the
        conversation history so the LLM doesn't completely lose context.
        """
        key_parts = []

        for msg in messages:
            content = msg.get("content", "")
            # Extract tool call/result information — these contain actual findings
            if "Llamada a herramienta:" in content or "Resultado de herramienta:" in content:
                key_parts.append(content[:300])

            # Extract lines that look like findings/discoveries
            for line in content.split("\n"):
                stripped = line.strip()
                if any(
                    marker in stripped
                    for marker in [
                        "[+]",
                        "[!]",
                        "[-]",
                        "hallazgo",
                        "vulnerabilidad",
                        "flag",
                        "CVE",
                        "puerto",
                        "abierto",
                        "servicio",
                        "ruta",
                        "filtración",
                        "inyección",
                        "Status:",
                        "Headers:",
                        "Body",
                        # ★ Negative/failure markers — critical for CTF to avoid repeating
                        "falló",
                        "inválido",
                        "no hay",
                        "misma respuesta",
                        "bloqueado",
                        "sin éxito",
                        "no existe",
                        "error",
                        "404",
                        "timeout",
                        # ★ Confirmed fact markers — verified by actual tool output
                        "confirmado",
                        "confirmación",
                        "verificación exitosa",
                        "verified",
                        "confirmed",
                        # ★ Assumption markers — things the LLM assumed but didn't verify
                        "hipótesis",
                        "debería",
                        "posiblemente",
                        "se presume",
                        "conjetura",
                        "se estima",
                    ]
                ):
                    key_parts.append(stripped[:200])

        if not key_parts:
            return ""

        # Limit total summary size to avoid context bloat
        summary = "\n".join(key_parts)
        if len(summary) > 3000:
            summary = summary[:3000] + "\n...(más historial omitido)"

        return summary

    def trim_messages(self, max_messages: int = 20) -> None:
        """Forcefully trim conversation history to a specific size.

        Used when context overflow causes repeated LLM errors.
        """
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
