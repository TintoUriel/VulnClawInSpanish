import pytest

from vulnclaw.agent.context import PentestPhase
from vulnclaw.agent.core import AgentCore
from vulnclaw.agent.reflexion import FailureCategory
from vulnclaw.config.schema import VulnClawConfig


def _make_agent(tmp_path, reflexion_enabled=True):
    config = VulnClawConfig()
    config.session.output_dir = tmp_path
    config.session.reflexion_enabled = reflexion_enabled
    config.session.reflexion_max_same_vuln_fails = 2
    config.session.reflexion_max_total_no_progress = 5
    return AgentCore(config)


@pytest.mark.asyncio
async def test_consecutive_same_failures_generate_reflexion_prompt(tmp_path, monkeypatch):
    agent = _make_agent(tmp_path, reflexion_enabled=True)
    captured_contexts = []

    from vulnclaw.agent import loop_controller

    async def _fake_call_llm_auto(agent_obj, system_prompt, round_context, **kwargs):
        captured_contexts.append(round_context)
        return "Intenté un payload de sqli, la solicitud falló con ConnectionError."

    monkeypatch.setattr(loop_controller, "call_llm_auto", _fake_call_llm_auto)

    await agent.auto_pentest("escanea la vulnerabilidad de inyección SQL en example.com", max_rounds=4)

    assert "🔴 Toma de control por reflexión" in captured_contexts[3]
    assert "Deja de cambiar payloads repetidamente en la ruta de ataque actual." in captured_contexts[3]
    assert "Instrucción obligatoria de cambio de ruta" not in captured_contexts[3]
    assert agent.runtime.same_path_fail_count >= 2


def test_reflexion_disabled_keeps_legacy_same_path_warning(tmp_path):
    agent = _make_agent(tmp_path, reflexion_enabled=False)
    agent.context.state.advance_phase(PentestPhase.VULN_DISCOVERY)
    agent.runtime.same_path_fail_count = 3

    context = agent._build_round_context(5, 5)

    assert "Instrucción obligatoria de cambio de ruta" in context
    assert "🔴 Toma de control por reflexión" not in context
    assert agent.runtime.same_path_fail_count == 0
    assert agent.runtime.path_switch_forced is True


def test_reflexion_memory_persists_across_cycles(tmp_path):
    """P2-7: el modo persistente conserva la memoria de fallos entre ciclos, pero reinicia el contador de estancamiento del ciclo actual."""
    agent = _make_agent(tmp_path, reflexion_enabled=True)

    # Ciclo 1: acumula fallos del mismo tipo
    rx = agent.runtime.reflexion
    for _ in range(2):
        rx.record_attempt(
            path="sqli",
            success=False,
            category=FailureCategory.ENV_CONSTRAINT,
            details="Bloqueado por WAF",
            vuln_type="sqli",
        )
    assert rx.state.consecutive_failures == 2
    assert rx.state.vuln_type_fail_count == 2

    # Fin del ciclo 1: se escribe el snapshot
    agent._save_reflexion_snapshot()
    assert agent.context.state.reflexion_snapshot

    # Frontera del ciclo 2: se reconstruye runtime y se restaura la memoria
    agent._reset_runtime_state(user_input="[Ciclo persistente 2] continuar el pentest")
    rx2 = agent.runtime.reflexion

    # La memoria se conserva: la ruta fallida es visible
    assert "sqli" in rx2.get_failed_paths()
    # El contador de estancamiento del ciclo actual se reinicia, la detección de bloqueo empieza de nuevo
    assert rx2.state.consecutive_failures == 0
    assert rx2.state.vuln_type_fail_count == 0


def test_reflexion_snapshot_skipped_when_disabled(tmp_path):
    """Cuando reflexion_enabled=False no se escribe ni se restaura el snapshot."""
    agent = _make_agent(tmp_path, reflexion_enabled=False)
    agent.runtime.reflexion.record_attempt(path="sqli", success=False, vuln_type="sqli")
    agent._save_reflexion_snapshot()
    assert agent.context.state.reflexion_snapshot == {}
