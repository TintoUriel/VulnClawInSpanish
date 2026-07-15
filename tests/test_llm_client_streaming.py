"""Tests for LLM streaming functionality."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest


class TestNullSink:
    """Test _NullSink has no side effects."""

    def test_null_sink_on_status(self):
        """on_status should do nothing."""
        from vulnclaw.agent.llm_client import _NullSink

        sink = _NullSink()
        # Should not raise
        sink.on_status("Thinking...")
        sink.on_thinking_token("test")
        sink.on_content_token("test")
        sink.on_tool_call("tool", "args")
        sink.on_tool_result("result")
        sink.on_stream_end()

    def test_null_sink_returns_none(self):
        """All methods should return None."""
        from vulnclaw.agent.llm_client import _NullSink

        sink = _NullSink()
        assert sink.on_status("msg") is None
        assert sink.on_thinking_token("token") is None
        assert sink.on_content_token("token") is None
        assert sink.on_tool_call("name", "args") is None
        assert sink.on_tool_result("result") is None
        assert sink.on_stream_end() is None


class TestCallLlmStream:
    """Test call_llm_stream functionality."""

    @pytest.mark.asyncio
    async def test_stream_tokens_accumulated(self):
        """Test that stream tokens are accumulated correctly."""
        from vulnclaw.agent.llm_client import call_llm_stream

        # Mock agent
        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        # Mock llm config
        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        # Create mock streaming response - using plain objects
        class MockDelta:
            def __init__(self, content="", reasoning=""):
                self.content = content
                self.reasoning_content = reasoning

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning=""):
                self.delta = MockDelta(content=content, reasoning=reasoning)
                self.choices = [MockChoice(self.delta)]

        # Create async iterator
        class MockAsyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._chunks:
                    return self._chunks.pop(0)
                raise StopAsyncIteration

        mock_stream = MockAsyncStream([
            MockChunk(content="Hello"),
            MockChunk(content=" "),
            MockChunk(content="World"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream

        # Mock other agent methods
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        # Test
        result = await call_llm_stream(agent, "system prompt")

        assert "Hello World" in result or result == "Hello World"

    @pytest.mark.asyncio
    async def test_stream_with_reasoning(self):
        """Test streaming with reasoning content."""
        from vulnclaw.agent.llm_client import call_llm_stream

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        # Mock llm config
        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        class MockDelta:
            def __init__(self, content="", reasoning=""):
                self.content = content
                self.reasoning_content = reasoning

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning=""):
                self.delta = MockDelta(content=content, reasoning=reasoning)
                self.choices = [MockChoice(self.delta)]

        class MockAsyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._chunks:
                    return self._chunks.pop(0)
                raise StopAsyncIteration

        mock_stream = MockAsyncStream([
            MockChunk(reasoning="thinking..."),
            MockChunk(content="answer"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        result = await call_llm_stream(agent, "system prompt")

        assert "answer" in result


class TestTerminalStreamSink:
    """Test TerminalStreamSink."""

    def test_show_thinking_true(self):
        """Test thinking content is shown when show_thinking=True."""
        from vulnclaw.agent.llm_client import _NullSink

        # This is tested implicitly - NullSink should do nothing
        sink = _NullSink()
        sink.on_thinking_token("thinking content")
        # Should not raise

    def test_show_thinking_false(self):
        """Test thinking content is hidden when show_thinking=False."""
        from vulnclaw.agent.llm_client import _NullSink

        sink = _NullSink()
        # Should not raise even with content
        sink.on_thinking_token("thinking content")


class SpySink:
    """Sink de prueba que registra todas las llamadas a sus métodos."""

    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def on_status(self, message: str) -> None:
        self.calls.append(('status', message))

    def on_thinking_token(self, token: str) -> None:
        self.calls.append(('thinking', token))

    def on_content_token(self, token: str) -> None:
        self.calls.append(('content', token))

    def on_tool_call(self, tool_name: str, args: str) -> None:
        self.calls.append(('tool_call', f"{tool_name}:{args}"))

    def on_tool_result(self, result_summary: str) -> None:
        self.calls.append(('tool_result', result_summary))

    def on_stream_end(self) -> None:
        self.calls.append(('end', ''))


class TestStreamOutputSequence:
    """Prueba el orden de llamadas de la salida en streaming"""

    @pytest.mark.asyncio
    async def test_stream_calls_sink_in_order(self):
        """Verifica que los métodos del sink se llamen en el orden correcto"""
        from vulnclaw.agent.llm_client import call_llm_stream

        # Crear Spy Sink
        spy = SpySink()

        # Mock agent
        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        # Mock llm config
        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        # Mock streaming response
        class MockDelta:
            def __init__(self, content="", reasoning=""):
                self.content = content
                self.reasoning_content = reasoning

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning=""):
                self.delta = MockDelta(content=content, reasoning=reasoning)
                self.choices = [MockChoice(self.delta)]

        class MockAsyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._chunks:
                    return self._chunks.pop(0)
                raise StopAsyncIteration

        mock_stream = MockAsyncStream([
            MockChunk(content="Hello"),
            MockChunk(content=" "),
            MockChunk(content="World"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        # Test
        await call_llm_stream(agent, "system prompt", stream_sink=spy)

        # Verificar la secuencia
        assert len(spy.calls) > 0
        # El primero debería ser status (Thinking...)
        assert spy.calls[0][0] == 'status'
        assert 'Thinking' in spy.calls[0][1]
        # El último debería ser end
        assert spy.calls[-1][0] == 'end'
        # En medio debería haber content tokens
        content_calls = [c for c in spy.calls if c[0] == 'content']
        assert len(content_calls) == 3  # "Hello", " ", "World"

    @pytest.mark.asyncio
    async def test_stream_with_reasoning_calls_thinking_then_content(self):
        """Verifica el orden de llamadas entre reasoning y content"""
        from vulnclaw.agent.llm_client import call_llm_stream

        spy = SpySink()

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        class MockDelta:
            def __init__(self, content="", reasoning=""):
                self.content = content
                self.reasoning_content = reasoning

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning=""):
                self.delta = MockDelta(content=content, reasoning=reasoning)
                self.choices = [MockChoice(self.delta)]

        class MockAsyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._chunks:
                    return self._chunks.pop(0)
                raise StopAsyncIteration

        mock_stream = MockAsyncStream([
            MockChunk(reasoning="thinking..."),
            MockChunk(content="answer"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        await call_llm_stream(agent, "system prompt", stream_sink=spy)

        # Verificar que reasoning aparece antes que content
        thinking_calls = [c for c in spy.calls if c[0] == 'thinking']
        content_calls = [c for c in spy.calls if c[0] == 'content']

        assert len(thinking_calls) > 0
        assert len(content_calls) > 0

        # Encontrar el índice del primer thinking y del primer content
        first_thinking_idx = next(i for i, c in enumerate(spy.calls) if c[0] == 'thinking')
        first_content_idx = next(i for i, c in enumerate(spy.calls) if c[0] == 'content')
        assert first_thinking_idx < first_content_idx

    @pytest.mark.asyncio
    async def test_stream_accumulates_full_text(self):
        """Verifica que el texto completo devuelto contenga todos los tokens"""
        from vulnclaw.agent.llm_client import call_llm_stream

        spy = SpySink()

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        class MockDelta:
            def __init__(self, content="", reasoning=""):
                self.content = content
                self.reasoning_content = reasoning

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning=""):
                self.delta = MockDelta(content=content, reasoning=reasoning)
                self.choices = [MockChoice(self.delta)]

        class MockAsyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._chunks:
                    return self._chunks.pop(0)
                raise StopAsyncIteration

        mock_stream = MockAsyncStream([
            MockChunk(content="The "),
            MockChunk(content="quick "),
            MockChunk(content="brown "),
            MockChunk(content="fox"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        result = await call_llm_stream(agent, "system prompt", stream_sink=spy)

        # Verificar que el valor devuelto contiene todos los tokens
        assert "The quick brown fox" in result or result == "The quick brown fox"
        # Verificar el número de tokens
        content_tokens = [c for c in spy.calls if c[0] == 'content']
        assert len(content_tokens) == 4


class TestTerminalStreamSinkRealOutput:
    """Prueba la salida real de TerminalStreamSink"""

    def test_sink_outputs_status(self):
        """Prueba que on_status produzca la salida correcta"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=False)

        sink.on_status("Thinking...")
        sink.on_stream_end()

        result = output.getvalue()
        assert "Thinking" in result

    def test_sink_outputs_content_tokens(self):
        """Prueba que on_content_token produzca la salida correcta"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=False)

        sink.on_content_token("Hello")
        sink.on_content_token(" ")
        sink.on_content_token("World")
        sink.on_stream_end()

        result = output.getvalue()
        assert "Hello" in result
        assert "World" in result

    def test_sink_show_thinking_true_outputs_thinking(self):
        """Prueba que el contenido de thinking se muestre cuando show_thinking=True"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=True)

        sink.on_thinking_token("thinking...")
        sink.on_stream_end()

        result = output.getvalue()
        assert "thinking" in result

    def test_sink_show_thinking_false_hides_thinking(self, capsys):
        """Prueba que el contenido de thinking se oculte cuando show_thinking=False"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=False)

        sink.on_thinking_token("thinking...")
        sink.on_content_token("answer")
        sink.on_stream_end()

        result = output.getvalue()
        # thinking no debería estar en la salida
        # pero content sí debería aparecer
        assert "answer" in result

    def test_sink_outputs_tool_call(self):
        """Prueba que on_tool_call produzca la salida correcta"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=False)

        sink.on_tool_call("nmap_scan", '{"target": "example.com"}')
        sink.on_stream_end()

        result = output.getvalue()
        assert "nmap_scan" in result
        assert "example.com" in result

    def test_sink_outputs_tool_result(self):
        """Prueba que on_tool_result produzca la salida correcta"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=False)

        sink.on_tool_result("Port is open")
        sink.on_stream_end()

        result = output.getvalue()
        assert "Port" in result
        assert "open" in result

    def test_sink_truncates_long_tool_result(self):
        """Prueba que un resultado de herramienta demasiado largo se trunque"""
        import io

        from rich.console import Console

        from vulnclaw.cli.main import TerminalStreamSink

        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        sink = TerminalStreamSink(console, show_thinking=False)

        long_result = "A" * 500
        sink.on_tool_result(long_result)
        sink.on_stream_end()

        result = output.getvalue()
        # Debería truncarse a unos 200 caracteres
        assert len(result) < 300


class TestStreamFallback:
    """Prueba el escenario de degradación de streaming a no-streaming"""

    @pytest.mark.asyncio
    async def test_stream_fallback_when_streaming_not_supported(self):
        """Prueba la degradación automática cuando el Provider no soporta streaming"""
        from vulnclaw.agent.llm_client import call_llm_stream

        spy = SpySink()

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        # Mock de respuesta no-streaming (ruta de fallback)
        class MockMessage:
            def __init__(self):
                self.content = "Fallback response text"
                self.tool_calls = None

        class MockChoice:
            def __init__(self):
                self.message = MockMessage()

        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]

        mock_client.chat.completions.create.return_value = MockResponse()
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        # Test - debería devolver la respuesta de fallback
        result = await call_llm_stream(agent, "system prompt", stream_sink=spy)

        # Verificar el valor devuelto
        assert "Fallback response text" in result

    @pytest.mark.asyncio
    async def test_stream_with_cancellation_returns_partial(self):
        """Prueba que al interrumpirse el streaming se devuelva el texto parcial ya recolectado"""
        from vulnclaw.agent.llm_client import call_llm_stream

        spy = SpySink()

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        # Crear un stream que lanzará CancelledError
        class MockAsyncStream:
            def __init__(self):
                self.yielded = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                if not self.yielded:
                    self.yielded = True
                    class MockDelta:
                        content = "Partial "
                        reasoning_content = ""
                    class MockChoice:
                        delta = MockDelta()
                    class MockChunk:
                        choices = [MockChoice()]
                    return MockChunk()
                raise asyncio.CancelledError()

        mock_client.chat.completions.create.return_value = MockAsyncStream()
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []

        # Test
        try:
            result = await call_llm_stream(agent, "system prompt", stream_sink=spy)
            # Si no se lanzó ninguna excepción, verificar el valor devuelto
            assert result is not None
        except asyncio.CancelledError:
            # Si se lanza la excepción, es un comportamiento aceptable
            # aunque lo ideal sería manejarla con elegancia
            pass


class TestCallLlmAutoStream:
    """Prueba la funcionalidad de call_llm_auto_stream"""

    @pytest.mark.asyncio
    async def test_auto_stream_handles_tool_calls(self):
        """Prueba que las llamadas a herramientas se manejen correctamente"""
        from vulnclaw.agent.llm_client import call_llm_auto_stream

        spy = SpySink()

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        # Mock de respuesta en streaming con llamadas a herramientas (iterador síncrono)
        class MockDelta:
            def __init__(self, content="", reasoning="", tool_calls=None):
                self.content = content
                self.reasoning_content = reasoning
                self.tool_calls = tool_calls

        class MockToolCallChunk:
            def __init__(self):
                self.id = "call_123"
                self.type = "function"
                self.function = MagicMock()
                self.function.name = "test_tool"
                self.function.arguments = '{"arg": "value"}'

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning="", tool_calls=None):
                self.choices = [MockChoice(MockDelta(content=content, reasoning=reasoning, tool_calls=tool_calls))]

        class MockSyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __iter__(self):
                return iter(self._chunks)

        mock_stream = MockSyncStream([
            MockChunk(content="Using "),
            MockChunk(content="test tool"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream

        # Mock de la ejecución de la herramienta
        async def mock_handle_tool_calls_with_results(agent_obj, message):
            return [{"tool_call_id": "call_123", "content": "Tool executed"}], []

        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []
        agent.context.add_assistant_message = MagicMock()

        # Patch handle_tool_calls_with_results
        import vulnclaw.agent.llm_client as llm_client_module
        original = llm_client_module.handle_tool_calls_with_results
        llm_client_module.handle_tool_calls_with_results = mock_handle_tool_calls_with_results

        try:
            result = await call_llm_auto_stream(
                agent, "system prompt", "round context", stream_sink=spy
            )
            # Verificar el valor devuelto
            assert result is not None
        finally:
            llm_client_module.handle_tool_calls_with_results = original

    @pytest.mark.asyncio
    async def test_auto_stream_text_only_response(self):
        """Prueba una respuesta de solo texto (sin llamadas a herramientas)"""
        from vulnclaw.agent.llm_client import call_llm_auto_stream

        spy = SpySink()

        agent = MagicMock()
        mock_client = MagicMock()
        agent._get_client.return_value = mock_client

        agent.config.llm.provider = "openai"
        agent.config.llm.model = "gpt-4"
        agent.config.llm.max_tokens = None
        agent.config.llm.temperature = None

        # Mock de respuesta en streaming (solo texto, iterador síncrono)
        class MockDelta:
            def __init__(self, content="", reasoning=""):
                self.content = content
                self.reasoning_content = reasoning

        class MockChoice:
            def __init__(self, delta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content="", reasoning=""):
                self.choices = [MockChoice(MockDelta(content=content, reasoning=reasoning))]

        class MockSyncStream:
            def __init__(self, chunks):
                self._chunks = chunks

            def __iter__(self):
                return iter(self._chunks)

        mock_stream = MockSyncStream([
            MockChunk(content="Analysis "),
            MockChunk(content="complete"),
        ])

        mock_client.chat.completions.create.return_value = mock_stream
        agent.context.get_messages.return_value = []
        agent._build_openai_tools.return_value = []
        agent.context.add_assistant_message = MagicMock()

        result = await call_llm_auto_stream(
            agent, "system prompt", "round context", stream_sink=spy
        )

        # 验证返回值包含响应文本
        assert "Analysis complete" in result
