"""Autonomous / persistent loop helpers for AgentCore."""

from __future__ import annotations

import re
from collections import Counter
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext


from vulnclaw.agent.constraint_policy import validate_phase_transition
from vulnclaw.agent.context import PentestPhase
from vulnclaw.agent.ctf_mode import update_ctf_state
from vulnclaw.agent.llm_client import call_llm_auto
from vulnclaw.agent.reasoning_state import (
    ConstraintCategory,
    ConstraintSeverity,
    PathStatus,
)
from vulnclaw.agent.reflexion import FailureCategory, classify_failure
from vulnclaw.agent.runtime_state import AgentResult, PersistentCycleResult

RECON_MIN_ROUNDS = 8


def _reasoning_enabled(agent: AgentContext) -> bool:
    return getattr(getattr(agent.config, "session", None), "reasoning_state_enabled", True)


def _sync_reasoning_path(agent: AgentContext, path_name: str, *, success: bool) -> None:
    """Registra la ruta de ataque identificada en el estado de razonamiento estructurado y actualiza las prioridades."""
    if not path_name or not _reasoning_enabled(agent):
        return
    reasoning = getattr(agent.context.state, "reasoning", None)
    if reasoning is None or not hasattr(reasoning, "add_path"):
        return
    existing = next((p for p in reasoning.paths if p.name == path_name), None)
    if existing is None:
        existing = reasoning.add_path(path_name, steps=[], priority=1)
    if success:
        existing.status = PathStatus.SUCCESS
        existing.result = "progreso logrado"
    elif existing.status != PathStatus.SUCCESS:
        existing.status = PathStatus.FAILED
    reasoning.auto_prioritize()


def _sync_reasoning_constraint(agent: AgentContext, path_name: str, category: FailureCategory) -> None:
    """Registra el obstáculo identificado (WAF/filtro, etc.) en el estado de razonamiento estructurado, manteniendo la descripción estable para facilitar la deduplicación."""
    if not _reasoning_enabled(agent):
        return
    reasoning = getattr(agent.context.state, "reasoning", None)
    if reasoning is None or not hasattr(reasoning, "add_constraint"):
        return
    mapping = {
        FailureCategory.ENV_CONSTRAINT: ConstraintCategory.WAF,
        FailureCategory.PARAM_ERROR: ConstraintCategory.FILTER,
    }
    category_value = mapping.get(category)
    if category_value is None:
        return
    reasoning.add_constraint(
        description=f"{path_name or 'ruta actual'} bloqueada por {category_value.value}",
        category=category_value,
        severity=ConstraintSeverity.HIGH,
        source="auto_pentest",
    )


def _configure_reflexion(agent: AgentContext) -> None:
    reflexion = getattr(agent.runtime, "reflexion", None)
    session = getattr(agent.config, "session", None)
    if not reflexion or not session:
        return

    for attr, config_attr in (
        ("max_same_vuln_fails", "reflexion_max_same_vuln_fails"),
        ("max_total_no_progress", "reflexion_max_total_no_progress"),
        ("escalation_max_level", "escalation_max_level"),
    ):
        if hasattr(reflexion, attr) and hasattr(session, config_attr):
            setattr(reflexion, attr, getattr(session, config_attr))


async def auto_pentest(
    agent: AgentContext,
    user_input: str,
    target: str | None = None,
    max_rounds: int = 15,
    on_step: Callable[[int, AgentResult], None] | None = None,
    *,
    stream_sink: Any = None,
) -> list[AgentResult]:
    results: list[AgentResult] = []

    detected_target = target or agent._detect_target(user_input)
    detected_phase = agent._detect_phase(user_input) or PentestPhase.RECON

    if detected_target:
        agent.context.state.target = detected_target
    if detected_phase:
        agent.context.state.advance_phase(detected_phase)

    agent.context.add_user_message(user_input)
    agent._reset_runtime_state(user_input=user_input, detected_phase=detected_phase)
    _configure_reflexion(agent)

    for round_num in range(1, max_rounds + 1):
        result = AgentResult()
        result.target = agent.context.state.target
        result.phase = agent.context.state.phase.value

        system_prompt = agent._build_system_prompt(
            agent.context.state.target,
            auto_mode=True,
            user_input=agent.runtime.auto_skill_input or user_input,
        )
        round_context = agent._build_round_context(round_num, max_rounds)

        try:
            response_text = await call_llm_auto(agent, system_prompt, round_context, stream_sink=stream_sink)
            result.output = response_text
            agent.context.add_assistant_message(f"[Análisis de la ronda {round_num}] {response_text}")
            agent._finding_parser.parse(response_text)

            if agent.runtime.is_recon_phase:
                agent._update_recon_dimension_completion(response_text)

            new_phase = agent._detect_phase_from_output(response_text)
            phase_violation = None
            if new_phase and new_phase != agent.context.state.phase:
                phase_violation = validate_phase_transition(
                    new_phase, agent.context.state.task_constraints
                )
                if phase_violation:
                    agent.context.state.add_constraint_violation_event(
                        source="phase",
                        action="exploit"
                        if hasattr(new_phase, "value") and new_phase.value == "Explotación"
                        else "",
                        code="phase_transition_blocked",
                        severity="high",
                        summary=phase_violation,
                        detail=response_text[:500],
                    )
                    result.output = f"{response_text}\n[!] {phase_violation}"
                    result.should_continue = False
                else:
                    agent.context.state.advance_phase(new_phase)
                    result.phase = new_phase.value

            if phase_violation is None:
                result.should_continue = not agent._is_completion_signal(response_text)

            result.should_continue = update_ctf_state(agent, response_text, result.should_continue)

            if (
                agent.runtime.is_recon_phase
                and not result.should_continue
                and phase_violation is None
            ):
                if (
                    agent.runtime.is_ctf_mode
                    and agent.runtime.flag_verified
                    and agent.runtime.claimed_flag
                ):
                    pass
                elif round_num < RECON_MIN_ROUNDS:
                    result.should_continue = True
                elif not agent.context.state.is_recon_complete():
                    result.should_continue = True

            step_raw = f"Round {round_num}: {response_text[:100]}..."
            sig = re.sub(r"Round\s*\d+:", "", step_raw).strip()[:60].lower()
            sig = re.sub(r"\s+", "_", sig)
            sig = re.sub(r"[^\w]", "", sig)

            if sig not in agent.runtime.seen_step_signatures:
                agent.runtime.seen_step_signatures.add(sig)
                agent.context.state.add_step(step_raw)

            agent._track_failed_target(response_text)

            current_findings = len(agent.context.state.findings)
            current_notes = len(agent.context.state.notes)
            current_steps = len(agent.context.state.executed_steps)

            is_spinning = False
            recent_notes = agent.context.state.notes[-5:]
            if recent_notes:
                all_words: list[str] = []
                for note in recent_notes:
                    all_words.extend(re.findall(r"[\u4e00-\u9fff]+", note))
                if all_words:
                    word_counts = Counter(all_words)
                    if word_counts.most_common(1)[0][1] >= 3:
                        is_spinning = True

            last_step = (
                agent.context.state.executed_steps[-1] if agent.context.state.executed_steps else ""
            )
            is_meaningful = agent._is_meaningful_step(last_step)

            has_new_progress = (
                current_findings > agent.runtime.last_findings_count
                or (current_notes > agent.runtime.last_notes_count and not is_spinning)
                or (current_steps > agent.runtime.last_steps_count + 1 and is_meaningful)
            )

            if has_new_progress:
                agent.runtime.rounds_without_progress = 0
                agent.runtime.python_timeout_rounds = 0
            else:
                agent.runtime.rounds_without_progress += 1

            agent.runtime.last_findings_count = current_findings
            agent.runtime.last_notes_count = current_notes
            agent.runtime.last_steps_count = current_steps

            detected_path = agent._detect_attack_path(response_text)
            reflexion = getattr(agent.runtime, "reflexion", None)
            reflexion_on = getattr(agent.config.session, "reflexion_enabled", True) and hasattr(
                reflexion, "record_attempt"
            )
            failure_category = None if has_new_progress else classify_failure(response_text)
            if reflexion_on:
                reflexion.record_attempt(
                    path=detected_path or agent.runtime.current_attack_path or "unknown",
                    success=has_new_progress,
                    category=failure_category,
                    details=response_text[:200],
                    vuln_type=detected_path or "",
                )

            # Sincroniza la ruta de ataque y los obstáculos con el estado de razonamiento estructurado
            _sync_reasoning_path(agent, detected_path, success=has_new_progress)
            if failure_category is not None:
                _sync_reasoning_constraint(agent, detected_path, failure_category)

            if not has_new_progress and not agent.runtime.path_switch_forced:
                if detected_path:
                    if detected_path == agent.runtime.current_attack_path:
                        agent.runtime.same_path_fail_count += 1
                    else:
                        # Cambiar de ruta de ataque tras quedar atascado = un evento de reflexión, se registra para cerrar el ciclo de escalamiento
                        if (
                            reflexion_on
                            and agent.runtime.current_attack_path
                            and reflexion.should_reflect()
                        ):
                            reflexion.record_reflection(
                                old_path=agent.runtime.current_attack_path,
                                new_path=detected_path,
                                reasoning=response_text[:200],
                            )
                        agent.runtime.current_attack_path = detected_path
                        agent.runtime.same_path_fail_count = 0
                        agent.runtime.path_switch_forced = False
            elif has_new_progress:
                agent.runtime.same_path_fail_count = 0
                agent.runtime.path_switch_forced = False

            agent.context.state.save()

        except Exception as e:
            result.output = f"[!] Error en la ronda {round_num}: {e}"
            agent.runtime.consecutive_errors += 1
            if agent.runtime.consecutive_errors >= 3:
                result.should_continue = False
            else:
                result.should_continue = True
                agent.context.trim_messages(max_messages=20)
        else:
            agent.runtime.consecutive_errors = 0

        results.append(result)
        if on_step:
            on_step(round_num, result)
        if not result.should_continue:
            break

    # Guarda la memoria de reflexión de este ciclo en la instantánea de SessionState, para reutilizarla al reanudar el próximo ciclo/mismo objetivo
    if hasattr(agent, "_save_reflexion_snapshot"):
        agent._save_reflexion_snapshot()
        agent.context.state.save()

    return results


async def persistent_pentest(
    agent: AgentContext,
    user_input: str,
    target: str | None = None,
    rounds_per_cycle: int = 100,
    max_cycles: int = 10,
    auto_report: bool = True,
    on_cycle_step: Callable[[int, int, AgentResult], None] | None = None,
    on_cycle_complete: Callable[[int, PersistentCycleResult], None] | None = None,
    *,
    # stream_sink se pasa desde core.py y se reenvía a agent.auto_pentest() para implementar la salida en streaming
    stream_sink: Any = None,
) -> list[PersistentCycleResult]:
    cycle_results: list[PersistentCycleResult] = []

    detected_target = target or agent._detect_target(user_input)
    if detected_target:
        agent.context.state.target = detected_target

    agent.context.add_user_message(user_input)
    agent._reset_runtime_state(user_input=user_input)

    findings_at_cycle_start = len(agent.context.state.findings)
    cycle_num = 0
    should_stop = False

    while not should_stop:
        cycle_num += 1
        if max_cycles > 0 and cycle_num > max_cycles:
            should_stop = True
            break

        cycle_results_list: list[AgentResult] = []

        # Snapshot which findings were already verified before this cycle runs, so
        # the cycle report can label only genuinely-new verified findings.
        prev_verified_ids = {
            f.finding_id for f in agent.context.state.get_verified_findings()
        }

        def _make_step_callback(cycle: int):
            def _on_step(round_num: int, result: AgentResult) -> None:
                cycle_results_list.append(result)
                if on_cycle_step:
                    on_cycle_step(round_num, cycle, result)

            return _on_step

        try:
            constraints_block = ""
            if getattr(agent.context.state, "task_constraints", None):
                rendered = agent.context.state.task_constraints.to_prompt_block()
                if rendered:
                    constraints_block = f"\n\n{rendered}"
            results = await agent.auto_pentest(
                user_input=(
                    f"[Ciclo persistente {cycle_num}] Continuar la prueba de penetración sobre el objetivo {agent.context.state.target or 'desconocido'}."
                    f"Este es el ciclo número {cycle_num}; mantén todos los hallazgos previos y profundiza a partir de ellos."
                    f"{constraints_block}"
                    if cycle_num > 1
                    else user_input
                ),
                target=agent.context.state.target,
                max_rounds=rounds_per_cycle,
                on_step=_make_step_callback(cycle_num),
                # Reenvía stream_sink para que el modo persistente también soporte salida en streaming
                stream_sink=stream_sink,
            )
            cycle_results_list = results if results else cycle_results_list
        except KeyboardInterrupt:
            should_stop = True
            cycle_results_list = cycle_results_list or []

        total_findings = len(agent.context.state.findings)
        total_steps = len(agent.context.state.executed_steps)
        new_findings = total_findings - findings_at_cycle_start
        findings_at_cycle_start = total_findings

        llm_summary = ""
        try:
            llm_summary = await agent._generate_attack_summary()
        except Exception:
            pass

        report_path = None
        if auto_report:
            try:
                from vulnclaw.report.generator import generate_persistent_cycle_report

                report_path = generate_persistent_cycle_report(
                    session=agent.context.state,
                    cycle_num=cycle_num,
                    total_findings=total_findings,
                    new_findings=new_findings,
                    total_steps=total_steps,
                    rounds_per_cycle=rounds_per_cycle,
                    llm_attack_summary=llm_summary,
                    prev_verified_ids=prev_verified_ids,
                )
            except Exception as e:
                report_path = f"Error al generar el informe: {e}"

        cycle_result = PersistentCycleResult(
            cycle_num=cycle_num,
            results=cycle_results_list,
            report_path=str(report_path) if report_path else None,
            total_findings=total_findings,
            total_steps=total_steps,
            stopped_early=should_stop,
        )
        cycle_results.append(cycle_result)

        if on_cycle_complete:
            on_cycle_complete(cycle_num, cycle_result)

        if cycle_results_list and not should_stop:
            last_result = cycle_results_list[-1]
            if not last_result.should_continue:
                if new_findings == 0 and total_findings > 0:
                    should_stop = True

    return cycle_results
