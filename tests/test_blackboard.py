from __future__ import annotations

from vulnclaw.agent.blackboard import Blackboard, IntentStatus


def test_fact_and_intent_ids_are_sequential():
    board = Blackboard(origin="t", goal="flag")
    f1 = board.add_fact("login form", "origin")
    f2 = board.add_fact("php 7.3", "fetch")
    assert (f1.id, f2.id) == ("f001", "f002")
    i1 = board.add_intent("test sqli", [f1.id])
    assert i1.id == "i001"
    assert i1.from_facts == ["f001"]


def test_add_intent_drops_unknown_from_facts():
    board = Blackboard()
    board.add_fact("x")
    intent = board.add_intent("explore", ["f001", "f999"])
    assert intent.from_facts == ["f001"]


def test_conclude_intent_creates_linked_fact():
    board = Blackboard()
    f = board.add_fact("seed")
    intent = board.add_intent("probe", [f.id])
    board.claim_intent(intent.id)
    assert board.get_intent(intent.id).status == IntentStatus.EXPLORING

    new_fact = board.conclude_intent(intent.id, "sqli confirmed")
    assert new_fact.id == "f002"
    assert board.get_intent(intent.id).status == IntentStatus.CONCLUDED
    assert board.get_intent(intent.id).result_fact == "f002"
    assert not board.open_intents()


def test_abandon_and_active_intents():
    board = Blackboard()
    board.add_fact("seed")
    a = board.add_intent("dead end")
    b = board.add_intent("live path")
    board.abandon_intent(a.id, note="sin salida")
    assert board.get_intent(a.id).status == IntentStatus.ABANDONED
    assert board.get_intent(a.id).note == "sin salida"
    # active = open + exploring (abandoned/concluded excluded)
    active_ids = {i.id for i in board.active_intents()}
    assert active_ids == {b.id}


def test_mark_complete_and_summary():
    board = Blackboard(goal="flag")
    board.add_fact("seed")
    board.mark_complete("flag{found} 已验证")
    summary = board.get_summary()
    assert summary["completed"] is True
    assert summary["complete_reason"].startswith("flag{found}")
    assert summary["facts"] == 1


def test_to_prompt_graph_renders_goal_facts_intents():
    board = Blackboard(origin="http://t", goal="capture flag")
    f = board.add_fact("login form", "origin")
    board.add_intent("sqli bypass", [f.id])
    text = board.to_prompt_graph()
    assert "goal: capture flag" in text
    assert "f001: login form" in text
    assert "i001 [open]" in text


def test_board_roundtrips_through_pydantic():
    board = Blackboard(goal="g")
    f = board.add_fact("a")
    board.add_intent("b", [f.id])
    dumped = board.model_dump()
    restored = Blackboard.model_validate(dumped)
    assert restored.goal == "g"
    assert restored.fact_ids() == ["f001"]
    assert restored.open_intents()[0].description == "b"
