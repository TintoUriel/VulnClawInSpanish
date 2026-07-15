from pathlib import Path
from types import SimpleNamespace

from vulnclaw.agent.context import SessionState
from vulnclaw.agent.prompt_context import build_round_context
from vulnclaw.agent.reasoning_state import PathStep
from vulnclaw.agent.reflexion import FailureCategory, ReflexionEngine


def _fake_agent(tmp_path: Path, state: SessionState, reflexion=None):
    runtime = SimpleNamespace(
        user_vuln_hint="",
        user_vuln_hint_rounds=0,
        same_path_fail_count=0,
        python_timeout_rounds=0,
        rounds_without_progress=0,
        blocked_targets=set(),
        claimed_flag=None,
        flag_verified=False,
        is_ctf_mode=False,
        is_recon_phase=False,
        reflexion=reflexion,
    )
    session = SimpleNamespace(
        output_dir=tmp_path,
        stale_rounds_threshold=5,
        reasoning_state_enabled=True,
        reflexion_enabled=True,
    )
    return SimpleNamespace(
        context=SimpleNamespace(state=state),
        runtime=runtime,
        config=SimpleNamespace(session=session),
    )


def test_session_state_persists_reasoning(tmp_path):
    state = SessionState(target="example.com")
    state.reasoning.add_fact("framework", "thinkphp", source="fingerprint", confidence=0.8)
    state.reasoning.add_constraint("union keyword blocked", category="waf", severity="blocking")
    state.reasoning.add_path(
        "login sql injection",
        [PathStep(action="test username with quote", target="/login", vuln_type="sqli")],
        priority=5,
    )

    save_path = tmp_path / "session.json"
    state.save(save_path)

    loaded = SessionState.load(save_path)

    assert loaded.reasoning.facts[0].key == "framework"
    assert loaded.reasoning.facts[0].value == "thinkphp"
    assert loaded.reasoning.constraints[0].description == "union keyword blocked"
    assert loaded.reasoning.paths[0].name == "login sql injection"
    assert loaded.reasoning.paths[0].steps[0].action == "test username with quote"


def test_build_round_context_injects_reasoning_and_reflexion(tmp_path):
    state = SessionState(target="example.com")
    state.reasoning.add_fact("candidate", "admin search looks injectable", confidence=0.7)
    state.reasoning.add_path(
        "admin search sqli",
        [PathStep(action="verify with a boolean probe", target="/admin/search", vuln_type="sqli")],
        priority=5,
    )
    state.reasoning.set_active_path("admin search sqli")

    reflexion = ReflexionEngine()
    reflexion.record_attempt(
        path="/admin/search?q='",
        success=False,
        category=FailureCategory.PARAM_ERROR,
        details="syntax did not change the response",
        vuln_type="sqli",
    )

    context = build_round_context(_fake_agent(tmp_path, state, reflexion), 2, 5)

    assert "🧭 Estado de razonamiento actual" in context
    assert "admin search looks injectable" in context
    assert "admin search sqli" in context
    assert "🔁 Estado de reflexión:" in context
    assert "/admin/search?q='" in context
    assert "Nivel de escalado actual" in context
