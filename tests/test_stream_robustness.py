"""Pruebas de robustez del ensamblaje de tool_calls en streaming.

Cobertura:
- Ensamblaje de tool_calls fragmentados en varios chunks (alineación por index, concatenación de arguments)
- function name / arguments llegando en chunks distintos
- Primer fragmento que solo contiene id (campo function en None) —— diferencias entre providers
- Casos límite: delta vacío / tc_delta en None / index ausente
- tool_call incompleto (JSON truncado / id ausente / name ausente) se descarta
- Conservación del content ya recibido cuando se produce una desconexión a mitad de stream
- reasoning_content no se mezcla con content
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vulnclaw.agent.llm_client import (
    _assemble_tool_calls,
    _collect_tool_call_deltas,
    _validate_tool_call,
    call_llm_auto_stream,
    call_llm_stream,
)

# === Tipos mock de apoyo para las pruebas (simulan la estructura de delta en streaming de OpenAI) ===


class _Func:
    def __init__(self, name=None, arguments=None):
        self.name = name
        self.arguments = arguments


class _TCDelta:
    """Un único fragmento de tool_call (delta.tool_calls[i])."""

    def __init__(self, index=0, id=None, name=None, arguments=None, function="set"):
        self.index = index
        self.id = id
        # function="none" simula el primer fragmento que solo trae id (en algunos providers)
        if function == "none":
            self.function = None
        else:
            self.function = _Func(name=name, arguments=arguments)


class _Delta:
    def __init__(self, content=None, reasoning=None, tool_calls=None):
        self.content = content
        self.reasoning_content = reasoning
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, delta):
        self.delta = delta


class _Chunk:
    def __init__(self, content=None, reasoning=None, tool_calls=None, choices=None):
        if choices is not None:
            self.choices = choices
        else:
            self.choices = [_Choice(_Delta(content=content, reasoning=reasoning, tool_calls=tool_calls))]


class _SyncStream:
    def __init__(self, chunks):
        self._chunks = chunks

    def __iter__(self):
        return iter(self._chunks)


class _BreakingStream:
    """Produce algunos chunks y luego lanza una excepción simulando una desconexión a mitad de stream."""

    def __init__(self, chunks, exc):
        self._chunks = list(chunks)
        self._exc = exc

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._chunks:
            return self._chunks.pop(0)
        raise self._exc


class SpySink:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def on_status(self, message):
        self.calls.append(("status", message))

    def on_thinking_token(self, token):
        self.calls.append(("thinking", token))

    def on_content_token(self, token):
        self.calls.append(("content", token))

    def on_tool_call(self, tool_name, args):
        self.calls.append(("tool_call", f"{tool_name}:{args}"))

    def on_tool_result(self, result_summary):
        self.calls.append(("tool_result", result_summary))

    def on_stream_end(self):
        self.calls.append(("end", ""))


def _make_agent():
    agent = MagicMock()
    mock_client = MagicMock()
    agent._get_client.return_value = mock_client
    agent.config.llm.provider = "openai"
    agent.config.llm.model = "gpt-4"
    agent.config.llm.max_tokens = None
    agent.config.llm.temperature = None
    agent.config.llm.max_context_tokens = None
    agent.context.get_messages.return_value = []
    agent._build_openai_tools.return_value = []
    return agent, mock_client


# === Pruebas unitarias de _collect_tool_call_deltas ===


class TestCollectToolCallDeltas:
    def test_none_delta_tool_calls(self):
        """No se agrega nada cuando delta.tool_calls es None."""
        chunks: list[dict] = []
        _collect_tool_call_deltas(_Delta(tool_calls=None), chunks)
        assert chunks == []

    def test_none_entry_in_tool_calls_skipped(self):
        """Los elementos None dentro de la lista tool_calls se omiten."""
        chunks: list[dict] = []
        _collect_tool_call_deltas(_Delta(tool_calls=[None]), chunks)
        assert chunks == []

    def test_id_only_chunk_function_none(self):
        """El primer fragmento que solo contiene id (function=None) no debe hacer fallar el código."""
        chunks: list[dict] = []
        delta = _Delta(tool_calls=[_TCDelta(index=0, id="call_abc", function="none")])
        _collect_tool_call_deltas(delta, chunks)
        assert chunks == [
            {"index": 0, "id": "call_abc", "function": {"name": "", "arguments": ""}}
        ]

    def test_missing_index_defaults_zero(self):
        """Cuando index es None, se usa 0 como valor por defecto."""
        chunks: list[dict] = []
        delta = _Delta(tool_calls=[_TCDelta(index=None, name="t", arguments="{}")])
        _collect_tool_call_deltas(delta, chunks)
        assert chunks[0]["index"] == 0

    def test_name_and_args_separate_chunks(self):
        """name y arguments llegan en fragmentos distintos."""
        chunks: list[dict] = []
        _collect_tool_call_deltas(
            _Delta(tool_calls=[_TCDelta(index=0, id="c1", name="scan", arguments="")]), chunks
        )
        _collect_tool_call_deltas(
            _Delta(tool_calls=[_TCDelta(index=0, name="", arguments='{"t":1}')]), chunks
        )
        assert len(chunks) == 2
        assert chunks[0]["function"]["name"] == "scan"
        assert chunks[1]["function"]["arguments"] == '{"t":1}'


# === Pruebas unitarias de _validate_tool_call ===


class TestValidateToolCall:
    def _tc(self, id="c1", name="scan", arguments="{}"):
        return MagicMock(id=id, function=MagicMock(name=name, arguments=arguments))

    def test_valid_json_args(self):
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = '{"target": "x"}'
        assert _validate_tool_call(tc) is True

    def test_empty_args_allowed(self):
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = ""
        assert _validate_tool_call(tc) is True

    def test_missing_id_rejected(self):
        tc = MagicMock(id="")
        tc.function.name = "scan"
        tc.function.arguments = "{}"
        assert _validate_tool_call(tc) is False

    def test_missing_name_rejected(self):
        tc = MagicMock(id="c1")
        tc.function.name = ""
        tc.function.arguments = "{}"
        assert _validate_tool_call(tc) is False

    def test_truncated_json_rejected(self):
        """El JSON incompleto producido por una interrupción del streaming se considera inválido."""
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = '{"target": "exam'
        assert _validate_tool_call(tc) is False

    def test_none_function_rejected(self):
        tc = MagicMock(id="c1", function=None)
        assert _validate_tool_call(tc) is False


# === Pruebas unitarias de _assemble_tool_calls ===


class TestAssembleToolCalls:
    def test_empty(self):
        assert _assemble_tool_calls([]) == []

    def test_cross_chunk_assembly(self):
        """El id/name/arguments repartidos en varios fragmentos se ensamblan por index en una llamada completa."""
        chunks = [
            {"index": 0, "id": "call_", "function": {"name": "nmap", "arguments": ""}},
            {"index": 0, "id": "123", "function": {"name": "", "arguments": '{"target":'}},
            {"index": 0, "id": "", "function": {"name": "", "arguments": '"x"}'}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 1
        assert result[0].id == "call_123"
        assert result[0].function.name == "nmap"
        assert result[0].function.arguments == '{"target":"x"}'

    def test_multiple_indices(self):
        """Los tool_call paralelos con distinto index se agregan por separado."""
        chunks = [
            {"index": 0, "id": "a", "function": {"name": "t0", "arguments": "{}"}},
            {"index": 1, "id": "b", "function": {"name": "t1", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 2
        names = {tc.function.name for tc in result}
        assert names == {"t0", "t1"}

    def test_incomplete_json_discarded(self):
        """La llamada con arguments cuyo JSON está incompleto se descarta."""
        chunks = [
            {"index": 0, "id": "ok", "function": {"name": "good", "arguments": "{}"}},
            {"index": 1, "id": "bad", "function": {"name": "broken", "arguments": '{"t":'}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 1
        assert result[0].function.name == "good"

    def test_missing_id_discarded(self):
        """La llamada que, tras el ensamblaje, sigue sin id se descarta."""
        chunks = [
            {"index": 0, "id": "", "function": {"name": "noid", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert result == []

    def test_missing_name_discarded(self):
        """La llamada que, tras el ensamblaje, carece de name se descarta."""
        chunks = [
            {"index": 0, "id": "c1", "function": {"name": "", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert result == []


# === Pruebas de streaming de extremo a extremo ===


class TestStreamEndToEnd:
    @pytest.mark.asyncio
    async def test_tool_call_id_only_in_first_chunk(self):
        """El provider solo da tool_call.id en el primer chunk; los fragmentos siguientes solo traen arguments.

        Cubre las diferencias de formato de delta entre providers requeridas por la tarea.
        """
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            # Primer fragmento: id + name, function presente pero arguments vacío
            _Chunk(tool_calls=[_TCDelta(index=0, id="call_xyz", name="recon", arguments="")]),
            # Fragmentos siguientes: sin id, solo incrementos de arguments
            _Chunk(tool_calls=[_TCDelta(index=0, id=None, name=None, arguments='{"host":')]),
            _Chunk(tool_calls=[_TCDelta(index=0, id=None, name=None, arguments='"a.com"}')]),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        captured = {}

        async def fake_handle(agent_obj, message):
            captured["tool_calls"] = list(message.tool_calls)
            return "tool done"

        import vulnclaw.agent.llm_client as mod

        orig = mod.handle_tool_calls
        mod.handle_tool_calls = fake_handle
        try:
            await call_llm_stream(agent, "sys", stream_sink=spy)
        finally:
            mod.handle_tool_calls = orig

        assert "tool_calls" in captured
        tcs = captured["tool_calls"]
        assert len(tcs) == 1
        assert tcs[0].id == "call_xyz"
        assert tcs[0].function.name == "recon"
        assert tcs[0].function.arguments == '{"host":"a.com"}'

    @pytest.mark.asyncio
    async def test_incomplete_tool_call_dropped_end_to_end(self):
        """El streaming solo entrega arguments a medias → tras el ensamblaje el JSON queda incompleto → no se ejecuta la herramienta."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            _Chunk(tool_calls=[_TCDelta(index=0, id="c1", name="scan", arguments='{"t":')]),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        called = {"handle": False}

        async def fake_handle(agent_obj, message):
            called["handle"] = True
            return "x"

        import vulnclaw.agent.llm_client as mod

        orig = mod.handle_tool_calls
        mod.handle_tool_calls = fake_handle
        try:
            result = await call_llm_stream(agent, "sys", stream_sink=spy)
        finally:
            mod.handle_tool_calls = orig

        # La llamada incompleta se descarta, no se ejecuta la herramienta y se devuelve full_text vacío
        assert called["handle"] is False
        assert result == ""

    @pytest.mark.asyncio
    async def test_partial_content_preserved_on_disconnect(self):
        """Si se lanza ConnectionError a mitad del streaming, debería degradarse a la ruta no-streaming (fallback).

        La desconexión no es una excepción de tipo streaming-marker, así que según la lógica
        actual debe volver a lanzarse —— se verifica que el content ya recibido no provoque
        una salida duplicada adicional en el sink.
        """
        agent, mock_client = _make_agent()
        spy = SpySink()

        breaking = _BreakingStream(
            [_Chunk(content="partial ")], RuntimeError("connection reset")
        )

        # Primera llamada (streaming) devuelve el stream que se desconecta; la llamada de fallback devuelve una respuesta no-streaming
        non_stream_msg = MagicMock()
        non_stream_msg.content = "recovered"
        non_stream_msg.tool_calls = None
        non_stream_resp = MagicMock(choices=[MagicMock(message=non_stream_msg)])
        mock_client.chat.completions.create.side_effect = [breaking, non_stream_resp, non_stream_resp]

        with pytest.raises(RuntimeError):
            await call_llm_stream(agent, "sys", stream_sink=spy)

        # El content token recibido antes de la desconexión ya se emitió una vez
        content_calls = [c for c in spy.calls if c[0] == "content"]
        assert content_calls == [("content", "partial ")]

    @pytest.mark.asyncio
    async def test_content_emitted_exactly_once(self):
        """Los tokens del cuerpo del mensaje se emiten una sola vez mediante on_content_token, sin duplicados."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [_Chunk(content="A"), _Chunk(content="B"), _Chunk(content="C")]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        result = await call_llm_stream(agent, "sys", stream_sink=spy)

        content_calls = [c for c in spy.calls if c[0] == "content"]
        assert content_calls == [("content", "A"), ("content", "B"), ("content", "C")]
        assert result == "ABC"

    @pytest.mark.asyncio
    async def test_reasoning_not_mixed_into_content(self):
        """reasoning_content pasa por el canal thinking y no se mezcla con los tokens del cuerpo."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            _Chunk(reasoning="let me think"),
            _Chunk(content="final answer"),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        result = await call_llm_stream(agent, "sys", stream_sink=spy)

        thinking = [c for c in spy.calls if c[0] == "thinking"]
        content = [c for c in spy.calls if c[0] == "content"]
        assert thinking == [("thinking", "let me think")]
        assert content == [("content", "final answer")]
        # Los tokens del cuerpo no contienen el texto de reasoning
        assert "let me think" not in "".join(c[1] for c in content)
        # full_text contiene el bloque <thinking> + el cuerpo del mensaje
        assert "<thinking>" in result and "final answer" in result


class TestAutoStreamRobustness:
    @pytest.mark.asyncio
    async def test_reasoning_buffer_reset_between_rounds(self):
        """El reasoning residual de la primera ronda no debe filtrarse al stream de resumen de la segunda ronda (evita salida duplicada)."""
        agent, mock_client = _make_agent()
        spy = SpySink()

        # Primera ronda: reasoning residual (sin content posterior que dispare el flush) + tool_call
        first_round = _SyncStream([
            _Chunk(reasoning="round1 reasoning"),
            _Chunk(tool_calls=[_TCDelta(index=0, id="c1", name="t", arguments="{}")]),
        ])
        # Resumen de la segunda ronda: trae su propio reasoning nuevo + content
        second_round = _SyncStream([
            _Chunk(reasoning="round2 reasoning"),
            _Chunk(content="summary"),
        ])
        mock_client.chat.completions.create.side_effect = [first_round, second_round]

        async def fake_handle(agent_obj, message):
            return [{"tool_call_id": "c1", "content": "result"}], []

        import vulnclaw.agent.llm_client as mod

        orig = mod.handle_tool_calls_with_results
        mod.handle_tool_calls_with_results = fake_handle
        try:
            result = await call_llm_auto_stream(agent, "sys", "ctx", stream_sink=spy)
        finally:
            mod.handle_tool_calls_with_results = orig

        # El reasoning de round1 no debe repetirse en el texto final
        assert result.count("round1 reasoning") <= 1
        # El texto final debe provenir del resumen de la segunda ronda
        assert "summary" in result
        # El reasoning de round2 aparece una sola vez
        assert result.count("round2 reasoning") == 1
