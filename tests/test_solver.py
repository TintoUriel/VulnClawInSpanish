from __future__ import annotations

import asyncio
from types import SimpleNamespace

from vulnclaw.agent import solver
from vulnclaw.agent.blackboard import Blackboard, IntentStatus


def _fake_agent(tool_outputs: list[str] | None = None):
    state = SimpleNamespace(board=Blackboard(), save=lambda: None)
    context = SimpleNamespace(
        state=state,
        add_user_message=lambda *a: None,
        add_assistant_message=lambda *a: None,
    )
    queue = list(tool_outputs or [])

    async def _execute(tool_name, tool_args):
        return queue.pop(0) if queue else "Status: 200"

    return SimpleNamespace(context=context, _execute_mcp_tool=_execute)


def test_flag_evidence_helpers():
    assert solver._extract_flags("got flag{abc} and ctfshow{xyz}") == ["flag{abc}", "ctfshow{xyz}"]
    # el flag declarado no está en la evidencia → se considera no verificado
    assert solver._unverified_flags("flag{fake}", "server said: error") == ["flag{fake}"]
    # está en la evidencia → se considera verificado
    assert solver._unverified_flags("flag{real}", "body: flag{real}") == []
    # objetivo de flag pero la evidencia no tiene flag → la finalización no es válida
    ok, _ = solver._completion_is_grounded("encontrar la flag", "only status 200")
    assert ok is False
    ok2, _ = solver._completion_is_grounded("encontrar la flag", "leaked flag{x}")
    assert ok2 is True
    # objetivo sin flag → no se fuerza la verificación
    ok3, _ = solver._completion_is_grounded("enumerar subdominios", "")
    assert ok3 is True


def test_extract_json_handles_fences_and_noise():
    assert solver._extract_json('```json\n{"complete": "ok"}\n```') == {"complete": "ok"}
    assert solver._extract_json('prefix {"intents": []} suffix') == {"intents": []}
    assert solver._extract_json("not json at all") is None


def test_reason_prompt_requires_frontier_recovery_without_open_intents():
    board = Blackboard(origin="http://t", goal="capture flag")
    seed = board.add_fact("login form")
    dead = board.add_intent("try generic login bypass", [seed.id])
    board.abandon_intent(dead.id, note="no useful response")

    prompt = solver._reason_prompt(board, max_intents=3)

    assert "Frontier recovery rule" in prompt
    assert 'Do not return {"complete": false} without new intents' in prompt


def test_reason_prompt_does_not_force_recovery_with_open_intents():
    board = Blackboard(origin="http://t", goal="capture flag")
    seed = board.add_fact("login form")
    board.add_intent("try generic login bypass", [seed.id])

    prompt = solver._reason_prompt(board, max_intents=3)

    assert "Frontier recovery rule" not in prompt


async def test_solve_completes_when_reason_signals_goal(monkeypatch):
    calls = {"reason": 0}

    async def fake_reason(agent, board, max_intents):
        calls["reason"] += 1
        if calls["reason"] == 1:
            return {"intents": [{"from": [], "description": "test sqli bypass"}]}
        return {"complete": "flag{captured} verificado"}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        # simula que la salida real de la herramienta contiene el flag (la compuerta de evidencia lo deja pasar)
        evidence_buffer.append("HTTP 200\n<html>... flag{captured} ...</html>")
        return True, "sqli confirmado, se extrajo flag{captured}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="http://t",
        goal="flag",
        max_steps=10,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is True
    assert "flag{captured}" in result.reason
    # origin fact + 1 concluded fact
    assert result.facts == 2
    assert "conclude" in events


async def test_solve_completes_immediately_on_verified_flag(monkeypatch):
    """En cuanto la exploración obtiene un flag con evidencia real, se completa de inmediato, sin rondas de verificación extra."""
    reason_calls = {"n": 0}

    async def fake_reason(agent, board, max_intents):
        reason_calls["n"] += 1
        return {"intents": [{"from": [], "description": "union inject"}]}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        evidence_buffer.append("Bienvenido, flag{real_one}")  # la salida real de la herramienta contiene el flag
        return True, "la inyección union refleja flag{real_one}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    result = await solver.solve(_fake_agent(), origin="t", goal="encontrar la flag", max_steps=10)

    assert result.completed is True
    assert "flag{real_one}" in result.board.complete_reason
    # al obtener el flag converge de inmediato: reason solo se llama una vez, no entra a otra ronda de verificación
    assert reason_calls["n"] == 1


async def test_solve_rejects_hallucinated_flag(monkeypatch):
    """El flag declarado en la conclusión no está en la salida real de la herramienta → se detecta como alucinación, se rechaza y no se completa."""
    reason_calls = {"n": 0}

    async def fake_reason(agent, board, max_intents):
        reason_calls["n"] += 1
        if reason_calls["n"] == 1:
            return {"intents": [{"from": [], "description": "test sqli"}]}
        return {}  # después ya no propone nada → frontera agotada

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        # no escribe el flag en evidence_buffer —— simula que el modelo lo inventó
        return True, "se obtuvo con éxito flag{HALLUCINATED}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="t",
        goal="encontrar la flag",
        max_steps=10,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is False
    assert "hallucination" in events
    # el flag rechazado genera un hecho [No verificado]
    assert any("[No verificado]" in f.description for f in result.board.facts)


async def test_solve_rejects_ungrounded_completion(monkeypatch):
    """El objetivo exige un flag, pero jamás apareció en la salida real de las herramientas → se rechaza la declaración de finalización de Reason."""
    reason_calls = {"n": 0}

    async def fake_reason(agent, board, max_intents):
        reason_calls["n"] += 1
        if reason_calls["n"] == 1:
            return {"complete": "creo que ya obtuve la flag"}  # sin ninguna evidencia que lo respalde
        return {}  # después ya no propone nada → frontera agotada

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return True, "x"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="t",
        goal="encontrar la flag",
        max_steps=10,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is False
    assert "complete_rejected" in events


async def test_solve_rejects_negated_completion_claim(monkeypatch):
    """El modelo escribe una conclusión negativa («no se alcanzó») dentro del campo complete → jamás debe interpretarse como éxito (reproduce el falso positivo i004)."""
    reason_calls = {"n": 0}

    async def fake_reason(agent, board, max_intents):
        reason_calls["n"] += 1
        if reason_calls["n"] == 1:
            # complete=true pero reason es una conclusión negativa (debe ser bloqueada por la compuerta de negación)
            return {
                "complete": True,
                "reason": "f001 solo confirmó el puerto y la huella, no se alcanzó el estándar de finalización que exige el goal",
                "evidence": ["f001"],
            }
        return {"complete": False}  # después ya no propone nada → frontera agotada

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return True, "x"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="t",
        goal="analizar el sitio mediante pentest",  # objetivo sin flag; con la lógica antigua ninguna compuerta habría bloqueado el falso positivo
        max_steps=10,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is False
    assert "complete_rejected" in events
    assert "completed" not in events


async def test_solve_rejects_completion_without_explicit_bool(monkeypatch):
    """El formato antiguo {"complete": "<texto>"} (sin un true explícito) siempre se trata como no alcanzado."""

    async def fake_reason(agent, board, max_intents):
        return {"complete": "creo que ya terminé el análisis"}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return True, "x"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="t",
        goal="analizar el sitio mediante pentest",
        max_steps=10,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is False
    assert "complete_rejected" in events


async def test_solve_completes_nonflag_goal_with_evidence(monkeypatch):
    """Objetivo sin flag: complete=true + sin motivo negativo + referencia a un fact real → se alcanza normalmente."""

    async def fake_reason(agent, board, max_intents):
        return {
            "complete": True,
            "reason": "f001 ya confirmó la existencia de una interfaz sin autorización, objetivo alcanzado",
            "evidence": ["f001"],
        }

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return True, "x"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="t",
        goal="detectar acceso sin autorización",
        max_steps=10,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is True
    assert "completed" in events
    assert "sin autorización" in result.board.complete_reason


async def test_solve_stops_when_frontier_exhausted(monkeypatch):
    async def fake_reason_noop(agent, board, max_intents):
        return {}  # never proposes intents

    async def fake_recovery_noop(agent, board, max_intents, streak):
        return {}  # recovery also cannot find a path

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return True, "unused"

    monkeypatch.setattr(solver, "reason_step", fake_reason_noop)
    monkeypatch.setattr(solver, "frontier_recovery_step", fake_recovery_noop)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    result = await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=10)

    assert result.completed is False
    assert result.reason == "探索前沿耗尽"
    # only the seeded origin fact
    assert result.facts == 1


async def test_solve_recovers_empty_frontier_with_new_intent(monkeypatch):
    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {
                "intents": [
                    {"from": [], "description": "inspect login page"},
                    {"from": [], "description": "try generic sqli bypass"},
                    {"from": [], "description": "enumerate common files"},
                ]
            }
        return {"complete": False}

    async def fake_recovery(agent, board, max_intents, streak):
        return {
            "complete": False,
            "intents": [
                {
                    "from": ["f002"],
                    "description": "try header and cookie based auth bypass",
                }
            ],
        }

    async def fake_explore(
        agent,
        board,
        intent,
        *,
        max_tool_rounds,
        evidence_buffer,
        stream_sink=None,
        skip_context_write=False,
    ):
        if "header and cookie" in intent.description:
            evidence_buffer.append("HTTP 200\nflag{recovered}")
            return True, "header/cookie bypass returned flag{recovered}"
        if "login page" in intent.description:
            return True, "login form and CORS headers confirmed"
        return False, "no useful result"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "frontier_recovery_step", fake_recovery)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(),
        origin="http://t",
        goal="capture flag",
        max_steps=10,
        max_parallel=3,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert result.completed is True
    assert "frontier_recovery" in events
    assert any("header and cookie" in intent.description for intent in result.board.intents)
    assert "flag{recovered}" in result.board.complete_reason


async def test_solve_adds_fallback_intents_when_recovery_is_empty(monkeypatch):
    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {"intents": [{"from": [], "description": "dead login path"}]}
        return {"complete": False}

    async def fake_recovery_noop(agent, board, max_intents, streak):
        return {"complete": False}

    async def fake_explore(
        agent,
        board,
        intent,
        *,
        max_tool_rounds,
        evidence_buffer,
        stream_sink=None,
        skip_context_write=False,
    ):
        if "header/cookie auth bypass" in intent.description:
            evidence_buffer.append("HTTP 200\nflag{fallback}")
            return True, "header/cookie auth bypass returned flag{fallback}"
        return False, "no useful result"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "frontier_recovery_step", fake_recovery_noop)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[tuple[str, dict]] = []
    result = await solver.solve(
        _fake_agent(),
        origin="http://t",
        goal="capture flag",
        max_steps=10,
        max_parallel=3,
        on_event=lambda kind, payload: events.append((kind, payload)),
    )

    assert result.completed is True
    assert any(
        kind == "frontier_recovery" and payload.get("reason") == "fallback_intents"
        for kind, payload in events
    )
    assert any("header/cookie auth bypass" in intent.description for intent in result.board.intents)
    assert "flag{fallback}" in result.board.complete_reason


async def test_solve_abandons_unproductive_intent(monkeypatch):
    state = {"reason": 0}

    async def fake_reason(agent, board, max_intents):
        state["reason"] += 1
        if state["reason"] == 1:
            return {"intents": [{"from": [], "description": "dead path"}]}
        return {}  # afterward propose nothing -> frontier exhausts

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return False, "该方向走不通"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    result = await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=10)

    assert result.completed is False
    board = result.board
    assert board.intents[0].status == IntentStatus.ABANDONED
    assert board.intents[0].note == "该方向走不通"


async def test_solve_respects_safety_step_budget(monkeypatch):
    counter = {"n": 0}

    async def fake_reason(agent, board, max_intents):
        counter["n"] += 1
        # each intent has a unique description to avoid dedup filtering
        return {"intents": [{"from": [], "description": f"unique direction {counter['n']}"}]}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None):
        return True, "step fact"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    result = await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=3)

    assert result.completed is False
    assert result.reason == "触达安全预算上限"
    assert result.steps == 3


# ── Parallel exploration tests ──────────────────────────────────────


async def test_solve_parallel_explores_multiple_intents(monkeypatch):
    """3 intents proposed → all 3 explored concurrently → each produces a fact."""
    reason_calls = {"n": 0}

    async def fake_reason(agent, board, max_intents):
        reason_calls["n"] += 1
        if reason_calls["n"] == 1:
            return {"intents": [
                {"from": [], "description": "sqli probe"},
                {"from": [], "description": "xss probe"},
                {"from": [], "description": "ssrf probe"},
            ]}
        return {"complete": True, "reason": "all probed", "evidence": ["f001"]}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None, skip_context_write=False):
        await asyncio.sleep(0)
        return True, f"found via {intent.description}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(), origin="t", goal="test", max_steps=10, max_parallel=3,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert events.count("explore_start") == 3
    concluded = [i for i in result.board.intents if i.status == IntentStatus.CONCLUDED]
    assert len(concluded) == 3


async def test_solve_parallel_evidence_isolation(monkeypatch):
    """Each parallel worker gets its own evidence buffer, no cross-contamination."""
    collected_evidence: dict[str, list[str]] = {}

    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {"intents": [
                {"from": [], "description": "path A"},
                {"from": [], "description": "path B"},
            ]}
        return {}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None, skip_context_write=False):
        marker = f"evidence_for_{intent.id}"
        evidence_buffer.append(marker)
        collected_evidence[intent.id] = list(evidence_buffer)
        await asyncio.sleep(0)
        return True, f"result {intent.id}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=10, max_parallel=2)

    if "i001" in collected_evidence and "i002" in collected_evidence:
        assert "evidence_for_i002" not in collected_evidence["i001"]
        assert "evidence_for_i001" not in collected_evidence["i002"]


async def test_solve_parallel_one_failure_others_continue(monkeypatch):
    """One intent raises an exception, others complete normally."""
    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {"intents": [
                {"from": [], "description": "will fail"},
                {"from": [], "description": "will succeed"},
            ]}
        return {}

    call_count = {"n": 0}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None, skip_context_write=False):
        call_count["n"] += 1
        if "fail" in intent.description:
            raise RuntimeError("simulated crash")
        return True, "success result"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    events: list[str] = []
    result = await solver.solve(
        _fake_agent(), origin="t", goal="g", max_steps=10, max_parallel=2,
        on_event=lambda kind, payload: events.append(kind),
    )

    assert "error" in events
    concluded = [i for i in result.board.intents if i.status == IntentStatus.CONCLUDED]
    abandoned = [i for i in result.board.intents if i.status == IntentStatus.ABANDONED]
    assert len(concluded) == 1
    assert len(abandoned) >= 1


async def test_solve_parallel_board_fact_ids_sequential(monkeypatch):
    """Concurrent conclude operations produce unique, sequential fact IDs."""
    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {"intents": [
                {"from": [], "description": f"dir {i}"} for i in range(3)
            ]}
        return {}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None, skip_context_write=False):
        await asyncio.sleep(0)
        return True, f"fact from {intent.id}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    result = await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=10, max_parallel=3)

    fact_ids = [f.id for f in result.board.facts]
    assert len(fact_ids) == len(set(fact_ids)), f"duplicate fact IDs: {fact_ids}"


async def test_solve_serial_fallback(monkeypatch):
    """With only 1 open intent, solve takes the serial path (no gather overhead)."""
    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {"intents": [{"from": [], "description": "single path"}]}
        return {}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None, skip_context_write=False):
        return True, "serial result"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    result = await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=10, max_parallel=3)

    concluded = [i for i in result.board.intents if i.status == IntentStatus.CONCLUDED]
    assert len(concluded) == 1


async def test_solve_parallel_max_caps_batch(monkeypatch):
    """max_parallel=2 caps the batch even when 3 intents are open."""
    explored_intents: list[str] = []

    async def fake_reason(agent, board, max_intents):
        if not board.intents:
            return {"intents": [
                {"from": [], "description": f"path {i}"} for i in range(3)
            ]}
        return {}

    async def fake_explore(agent, board, intent, *, max_tool_rounds, evidence_buffer, stream_sink=None, skip_context_write=False):
        explored_intents.append(intent.id)
        return True, f"done {intent.id}"

    monkeypatch.setattr(solver, "reason_step", fake_reason)
    monkeypatch.setattr(solver, "explore_step", fake_explore)

    await solver.solve(_fake_agent(), origin="t", goal="g", max_steps=10, max_parallel=2)

    assert len(explored_intents) == 3


# ── Blackboard seq restore test ─────────────────────────────────────


def test_blackboard_seq_restores_from_existing_facts():
    """After deserialisation, fact/intent seq counters recover from existing items."""
    board = Blackboard()
    board.add_fact("first", source="test")
    board.add_fact("second", source="test")
    board.add_intent("intent one")

    data = board.model_dump()
    restored = Blackboard.model_validate(data)

    new_fact = restored.add_fact("third", source="test")
    assert new_fact.id == "f003"
    new_intent = restored.add_intent("intent two")
    assert new_intent.id == "i002"
