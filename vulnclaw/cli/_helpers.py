"""CLI shared helper functions — extracted from cli/main.py.

修改者: Nyaecho
修改时间: 2026-07-08
修改原因: S2 修复 — 从 cli/main.py（2932 行）提取共享辅助函数到独立模块，
         为后续命令拆分做准备。
"""

from __future__ import annotations

from typing import Any, Optional

from rich.console import Console
from rich.text import Text

from vulnclaw import __version__
from vulnclaw.config.text_utils import format_think_tags, strip_think_tags

console = Console()
err_console = Console(stderr=True)


class TerminalStreamSink:
    """CLI terminal stream renderer.

    Implements StreamSink protocol for real-time terminal output.
    """

    def __init__(self, console: Console, show_thinking: bool = False) -> None:
        self._console = console
        self._show_thinking = show_thinking
        self._status_printed = False
        self._in_thinking = False

    def on_status(self, message: str) -> None:
        """Display status message like 'Thinking...'."""
        self._console.print(f"[dim]{message}[/dim] ", end="", soft_wrap=True)
        self._status_printed = True

    def on_thinking_token(self, token: str) -> None:
        """Receive thinking token."""
        if self._show_thinking:
            self._console.print(f"[dim i]{token}[/]", end="", soft_wrap=True)

    def on_content_token(self, token: str) -> None:
        """Receive content token."""
        if self._status_printed and not self._in_thinking:
            self._console.print()
            self._status_printed = False
        self._console.print(token, end="", soft_wrap=True)

    def on_tool_call(self, tool_name: str, args: str) -> None:
        """Display tool call notification."""
        self._console.print()
        self._console.print(f"[bold cyan]→ 调用工具: {tool_name}[/] {args[:100]}")
        self._status_printed = False

    def on_tool_result(self, result_summary: str) -> None:
        """Display tool result summary."""
        self._console.print()
        if len(result_summary) > 200:
            result_summary = result_summary[:200] + "..."
        self._console.print(f"[dim]→ 工具结果: {result_summary}[/]")

    def on_stream_end(self) -> None:
        """Handle stream end."""
        if self._status_printed:
            self._status_printed = False
        self._console.print()


ASCII_LOGO = (
    " _    __      __      ________\n"
    "| |  / /_  __/ /___  / ____/ /___ __      __\n"
    "| | / / / / / / __ \\/ /   / / __ `/ | /| / /\n"
    "| |/ / /_/ / / / / / /___/ / /_/ /| |/ |/ /\n"
    "|___/\\__,_/_/_/ /_/\\____/_/\\__,_/ |__/|__/\n"
)

BANNER_SUBTITLE = f"VulnClaw v{__version__} - AI-powered penetration testing CLI"


def _print_banner() -> None:
    """Print the VulnClaw ASCII banner."""
    logo = Text(ASCII_LOGO, style="bold red")
    subtitle = Text(BANNER_SUBTITLE)
    console.print(logo)
    console.print(subtitle)
    console.print()


def _print_agent_output(output: str, config: Any) -> None:
    """Print agent output with think-tag filtering based on config."""
    from rich.markup import escape as rich_escape

    formatted = format_think_tags(output, show=config.session.show_thinking)
    if formatted:
        console.print(rich_escape(formatted))
    elif not config.session.show_thinking:
        stripped = strip_think_tags(output)
        had_thinking = (stripped != output) and not stripped
        if had_thinking:
            console.print("[dim](LLM returned only hidden reasoning and no visible answer.)[/dim]")


def _make_solve_event_printer(target_console: Console) -> Any:
    """Return an on_event callback that prints solve-engine progress live."""

    def on_event(kind: str, payload: dict) -> None:
        if kind == "reason":
            decision = payload.get("decision") or {}
            complete_flag = decision.get("complete")
            if complete_flag is not None and complete_flag is not False:
                pass
            elif decision.get("intents"):
                target_console.print(
                    f"[cyan]◆ Reason:[/cyan] 提出 {len(decision['intents'])} 个新探索方向"
                )
            else:
                target_console.print("[dim]◆ Reason: 暂不新增方向[/dim]")
        elif kind == "frontier_recovery":
            if payload.get("reason") == "fallback_intents":
                target_console.print(
                    f"[yellow]Frontier recovery:[/yellow] "
                    f"added {payload.get('added', 0)} fallback intents"
                )
            else:
                target_console.print(
                    f"[yellow]Frontier recovery:[/yellow] "
                    f"no open intents, retry {payload.get('streak', '?')}"
                )
        elif kind == "completed":
            target_console.print("[green]✓ Reason: 目标达成[/green]")
        elif kind == "explore_start":
            target_console.print(
                f"[yellow]▶ Explore {payload['intent_id']}:[/yellow] {payload['description'][:90]}"
            )
        elif kind == "conclude":
            target_console.print(
                f"[green]＋ Fact {payload.get('fact', '')}:[/green] {payload.get('desc', '')[:90]}"
            )
        elif kind == "hallucination":
            target_console.print(
                f"[red]⚠ 幻觉拦截 {payload['intent_id']}:[/red] 声称的 flag 无真实证据，已拒绝"
            )
        elif kind == "complete_rejected":
            target_console.print(f"[red]⚠ 拒绝完成:[/red] {payload.get('reason', '')[:90]}")
        elif kind == "abandon":
            target_console.print(f"[red]✗ 放弃 {payload['intent_id']}[/red]")

    return on_event


def _generate_report_for_target(
    target: str,
    *,
    current_session: Any = None,
    report_format: str = "markdown",
    output_path: Optional[str] = None,
) -> str:
    """Generate a report for a target using the best available source data."""
    from vulnclaw.agent.context import SessionState
    from vulnclaw.report.generator import generate_report, generate_report_from_target_state
    from vulnclaw.target_state.store import load_target_state

    if current_session is not None and (
        current_session.findings or current_session.executed_steps or current_session.notes
    ):
        path = generate_report(current_session, output_path, report_format=report_format)
        return str(path)

    state = load_target_state(target)
    if state:
        path = generate_report_from_target_state(state, output_path=output_path)
        return str(path)

    session = SessionState(target=target)
    path = generate_report(session, output_path, report_format=report_format)
    return str(path)


def _append_cli_constraints(
    prompt: str,
    only_port: Optional[int],
    only_host: Optional[str],
    only_path: Optional[str],
    blocked_host: Optional[str] = None,
    blocked_path: Optional[str] = None,
) -> str:
    """Append scope constraints to the task prompt."""
    constraints = []
    if only_port is not None:
        constraints.append(f"Only test port {only_port}")
    if only_host:
        constraints.append(f"Only test host {only_host}")
    if only_path:
        constraints.append(f"Only test path {only_path}")
    if blocked_host:
        constraints.append(f"Blocked host {blocked_host}")
    if blocked_path:
        constraints.append(f"Blocked path {blocked_path}")
    if not constraints:
        return prompt
    return f"{prompt} {' '.join(constraints)}."


def _append_cli_constraints_compat(
    prompt: str,
    only_port: Optional[int],
    only_host: Optional[str],
    only_path: Optional[str],
    blocked_host: Optional[str],
    blocked_path: Optional[str],
) -> str:
    """Append scope constraints while preserving older monkeypatch call shapes."""
    try:
        return _append_cli_constraints(
            prompt, only_port, only_host, only_path, blocked_host, blocked_path
        )
    except TypeError as exc:
        if "positional" not in str(exc) and "argument" not in str(exc):
            raise
        return _append_cli_constraints(prompt, only_port, only_host, only_path)


def _append_action_constraints(
    prompt: str, allow_actions: Optional[str], block_actions: Optional[str]
) -> str:
    """Append action constraints to the task prompt."""
    constraints = []
    if allow_actions:
        constraints.append(f"Only allowed actions: {allow_actions}")
    if block_actions:
        constraints.append(f"Blocked actions: {block_actions}")
    if not constraints:
        return prompt
    return f"{prompt} {' '.join(constraints)}."


async def _run_cli_orchestrated_task(
    *,
    command: str,
    target: str,
    resume: bool,
    snapshot: Optional[str],
    runner: Any,
) -> Any:
    """Run a CLI task through the shared orchestrator helpers."""
    from vulnclaw.agent.core import AgentCore
    from vulnclaw.config.settings import load_config
    from vulnclaw.mcp.lifecycle import MCPLifecycleManager
    from vulnclaw.orchestrator import run_agent_task

    config = load_config()
    mcp_manager = MCPLifecycleManager(config)
    mcp_manager.start_enabled_servers()
    agent = AgentCore(config, mcp_manager)

    try:
        def on_restored(restore_result: Any) -> None:
            console.print(
                f"[*] Restored saved target state: [bold]{restore_result.target or target}[/]"
            )

        return await run_agent_task(
            agent=agent,
            command=command,
            target=target,
            resume=resume,
            snapshot_id=snapshot,
            on_restored=on_restored,
            runner=lambda shared_agent: runner(shared_agent, config),
        )
    finally:
        import signal

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        mcp_manager.stop_all()
