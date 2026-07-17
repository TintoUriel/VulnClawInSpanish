"""VulnClaw CLI main entry point with REPL and sub-commands."""

# ruff: noqa: E402

from __future__ import annotations

import asyncio
import os
import sys
import time
from typing import Any, Optional


def _configure_windows_console() -> None:
    """Force UTF-8 console I/O on Windows for reliable Unicode output."""
    if sys.platform != "win32":
        return

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass


_configure_windows_console()

import typer
from rich.panel import Panel

from vulnclaw import __version__, headless
from vulnclaw.agent.constraint_policy import validate_action_constraints
from vulnclaw.agent.input_analysis import extract_task_constraints

# === Stream Output Renderer ===
# Modificado por: Nyaecho
# Fecha de modificación: 2026-07-08
# Motivo de la modificación: corrección S2 — las funciones auxiliares
#   compartidas se movieron a cli/_helpers.py.
from vulnclaw.cli._helpers import (
    TerminalStreamSink,
    _append_action_constraints,
    _append_cli_constraints_compat,
    _generate_report_for_target,
    _make_solve_event_printer,
    _print_agent_output,
    _print_banner,
    _run_cli_orchestrated_task,
    console,
    err_console,
)
from vulnclaw.cli.manual import available_topics, render_manual
from vulnclaw.config.settings import (
    RUNS_DIR,
    apply_provider_preset,
    list_providers,
    load_config,
    save_config,
    set_config_value,
)
from vulnclaw.config.token_provider import has_llm_credentials
from vulnclaw.i18n import _
from vulnclaw.repl_runner import run_repl_call
from vulnclaw.target_state.store import (
    apply_target_state_to_agent,
    clear_target_state,
    diff_target_state_snapshots,
    get_target_state_preview,
    list_target_snapshots,
    load_target_state,
    rollback_target_state,
)

# ── REPL ────────────────────────────────────────────────────────────


def _prepare_repl_target(
    agent, requested_target: str, current_target: Optional[str], current_phase: str
) -> tuple[str, str, bool]:
    """Prepare REPL state for a target switch and optionally restore history."""
    target = requested_target.strip()
    if not target:
        return current_target or "", current_phase, False

    if current_target and current_target != target:
        console.print(
            f"[dim][*] Cambio de objetivo: {current_target} -> {target}, reiniciando contexto de sesión[/]"
        )
        agent.reset_context()
        current_phase = agent.session_state.phase.value

    restore_result = apply_target_state_to_agent(agent, target)
    current_phase = restore_result.phase or agent.session_state.phase.value
    return target, current_phase, restore_result.restored


async def _run_repl_agent_call(agent, *, call, after_result) -> None:
    """Run a REPL agent call and hand each result back to a caller hook."""
    await run_repl_call(call=call, after_result=after_result)


_PHASE_LABEL_KEYS = {
    "listo": "phase.idle",
    "ready": "phase.idle",
    "reconocimiento": "phase.recon",
    "recon": "phase.recon",
    "descubrimiento de vulnerabilidades": "phase.vuln_discovery",
    "vulnerability discovery": "phase.vuln_discovery",
    "explotación": "phase.exploitation",
    "exploitation": "phase.exploitation",
    "post-explotación": "phase.post_exploitation",
    "post-exploitation": "phase.post_exploitation",
    "post exploitation": "phase.post_exploitation",
    "generación de informe": "phase.reporting",
    "reporting": "phase.reporting",
}


def _localized_phase_label(phase: Any) -> str:
    """Return a display-only phase label for the active UI language."""
    raw = getattr(phase, "value", phase)
    text = str(raw or "").strip()
    key = _PHASE_LABEL_KEYS.get(text) or _PHASE_LABEL_KEYS.get(text.lower())
    return _(key) if key else text


def _make_repl_prompt_session() -> Any:
    """Build a prompt_toolkit session with the skill palette, or None if unavailable.

    Returns None when stdin is not a TTY (pipes, CI, ``--once`` smoke tests) or
    prompt_toolkit cannot attach, so the REPL falls back to plain input.
    """
    debug = bool(os.environ.get("VULNCLAW_DEBUG_INPUT"))
    try:
        if not sys.stdin.isatty():
            if debug:
                console.print("[dim](paleta de comandos desactivada: stdin no es una TTY)[/]")
            return None
        from prompt_toolkit import PromptSession

        from vulnclaw.cli.tui import build_repl_slash_completer, build_repl_slash_style

        session = PromptSession(
            completer=build_repl_slash_completer(),
            complete_while_typing=True,
            style=build_repl_slash_style(),
        )

        # `complete_while_typing` reopens the menu on insertion but not on
        # deletion, so backspacing to a bare '/' leaves it closed. Re-trigger
        # completion on any change while the line still starts with '/'.
        def _reopen_palette_on_edit(buff: Any) -> None:
            if buff.complete_state is None and buff.text.startswith("/"):
                buff.start_completion(select_first=False)

        session.default_buffer.on_text_changed += _reopen_palette_on_edit

        if debug:
            console.print("[dim](paleta de comandos activada)[/]")
        return session
    except Exception as exc:
        # Surface the reason instead of silently dropping to plain input.
        from rich.markup import escape as _esc

        console.print(f"[yellow](paleta de comandos no disponible: {_esc(str(exc))})[/]")
        return None


def _read_repl_line(
    pt_session: Any,
    target: Optional[str],
    phase: str,
    auto_mode: bool,
) -> str:
    """Read one REPL line, using the slash palette when a session is available."""
    phase_label = _localized_phase_label(phase)
    if pt_session is None:
        prompt_parts = []
        if target:
            prompt_parts.append(f"[bold cyan]{target}[/]")
        prompt_parts.append(f"[dim]{phase_label}[/]")
        if auto_mode:
            prompt_parts.append("[bold yellow]AUTO[/]")
        prompt_str = " | ".join(prompt_parts) if prompt_parts else "vulnclaw"
        return console.input(f"vulnclaw {prompt_str}> ")

    import html as _html

    from prompt_toolkit.formatted_text import HTML

    parts = []
    if target:
        parts.append(f"<ansicyan><b>{_html.escape(target)}</b></ansicyan>")
    parts.append(f"<ansibrightblack>{_html.escape(phase_label)}</ansibrightblack>")
    if auto_mode:
        parts.append("<ansiyellow><b>AUTO</b></ansiyellow>")
    body = " | ".join(parts) if parts else "vulnclaw"
    return pt_session.prompt(HTML(f"vulnclaw {body}<b>&gt; </b>"))


def _run_repl_command(name: str, args: str, agent: Any, config: Any) -> Any:
    """Execute a built-in classic-REPL slash command.

    Returns the (possibly reloaded) config so the caller can keep using it.
    """
    if name == "config":
        from vulnclaw.cli.tui import run_config_tui

        run_config_tui()
        # The editor writes to disk; reload and rebind the running agent so
        # provider/model/key changes take effect without restarting.
        new_config = load_config()
        agent.apply_config(new_config)
        console.print(
            f"[green]✓[/] Configuración recargada: "
            f"{new_config.llm.provider}/{new_config.llm.model}"
        )
        return new_config

    if name == "language":
        return _repl_switch_language(args, agent, config)

    return config


def _repl_switch_language(args: str, agent: Any, config: Any) -> Any:
    """Switch the interface language from the classic REPL."""
    from vulnclaw.cli.tui import _SUPPORTED_LANGUAGES, rebuild_translations
    from vulnclaw.i18n import init_i18n

    lang = args.strip().lower()
    if lang not in _SUPPORTED_LANGUAGES:
        console.print(
            "[yellow]Uso:[/] /language <"
            + " | ".join(_SUPPORTED_LANGUAGES)
            + f">  (actual: {config.session.language})"
        )
        return config

    config.session.language = lang
    save_config(config)
    init_i18n(lang=lang if lang != "auto" else None, config=config)
    rebuild_translations()
    agent.apply_config(config)
    console.print(f"[green]✓[/] Idioma configurado a [bold]{lang}[/].")
    return config


def _run_repl() -> None:
    """Run the interactive REPL loop."""
    from vulnclaw.agent.core import AgentCore
    from vulnclaw.mcp.lifecycle import MCPLifecycleManager

    _print_banner()

    config = load_config()
    if not has_llm_credentials(config.llm):
        console.print(_("cli.no_api_key"))
        console.print(_("cli.choose_provider"))
        console.print(_("cli.set_env_var"))
        console.print()
        console.print(_("cli.offline_mode"))

    # Initialize MCP lifecycle manager
    mcp_manager = MCPLifecycleManager(config)
    started = mcp_manager.start_enabled_servers()
    console.print(_("cli.mcp_registered", count=started))
    # Report any servers that failed to attach so the user knows immediately
    for srv_name, srv_state in mcp_manager.registry.get_all_servers().items():
        if srv_state.health_status in ("degraded", "unavailable") and srv_state.execution_mode in ("placeholder",):
            err_msg = getattr(srv_state, "error", "") or ""
            if err_msg:
                console.print(f"[yellow]  ⚠ {srv_name}: {err_msg[:120]}[/yellow]")

    # Initialize agent
    agent = AgentCore(config, mcp_manager)

    console.print(_("cli.welcome"))
    console.print()

    # Track current target
    current_target: Optional[str] = None
    current_phase: str = "Ready"
    exit_requested = False
    auto_mode_active = False
    _last_ctrlc_time = 0.0
    last_auto_input: str = ""

    # Interactive slash palette: skills under '/', flag skills under '/.'.
    # Falls back to plain input when there is no TTY (pipes, CI smoke tests).
    _pt_session = _make_repl_prompt_session()

    while True:
        try:
            # Read input (slash palette when interactive, plain prompt otherwise)
            user_input = _read_repl_line(
                _pt_session, current_target, current_phase, auto_mode_active
            ).strip()

            if not user_input:
                if last_auto_input:
                    user_input = last_auto_input
                    console.print(f"[dim]↻ Reanudando pentest automático: {last_auto_input[:60]}...[/]")
                else:
                    continue

            # Handle slash commands: '/' selects a skill, '/.' a flag skill.
            if user_input.startswith("/"):
                from vulnclaw.cli.tui import dispatch_repl_slash

                result = dispatch_repl_slash(user_input)
                if result.kind == "message":
                    console.print(result.text)
                    continue
                if result.kind == "target":
                    current_target, current_phase, restored_loaded = _prepare_repl_target(
                        agent, result.value, current_target, current_phase
                    )
                    if restored_loaded:
                        console.print(_("cli.target_restored", target=current_target))
                    console.print(_("cli.target_set", target=current_target))
                    continue
                if result.kind == "command":
                    config = _run_repl_command(result.value, result.text, agent, config)
                    continue
                # result.kind == "run": fall through with the rewritten prompt.
                user_input = result.text

            # Handle built-in commands
            cmd_lower = user_input.lower()

            if cmd_lower in ("exit", "quit", "q"):
                console.print(_("cli.bye"))
                break

            elif cmd_lower == "help":
                _print_help()
                continue

            elif cmd_lower == "status":
                _print_status(agent, mcp_manager, current_target, current_phase, config)
                continue

            elif cmd_lower.startswith("target "):
                current_target, current_phase, restored_loaded = _prepare_repl_target(
                    agent,
                    user_input[7:].strip(),
                    current_target,
                    current_phase,
                )
                if restored_loaded:
                    console.print(_("cli.target_restored", target=current_target))
                console.print(_("cli.target_set", target=current_target))
                continue

            elif cmd_lower == "clear":
                current_target = None
                current_phase = "Ready"
                auto_mode_active = False
                last_auto_input = ""
                agent.reset_context()
                console.print(_("cli.conversation_cleared"))
                continue

            elif cmd_lower == "tools":
                tools = mcp_manager.list_available_tools()
                if tools:
                    console.print(_("cli.available_tools"))
                    for tool in tools:
                        console.print(f"  - {tool}")
                else:
                    console.print(_("cli.no_tools"))
                continue

            elif cmd_lower.startswith("report"):
                report_target = user_input[len("report") :].strip() or current_target
                if not report_target:
                    console.print(_("cli.no_target_for_report"))
                    continue

                report_path = _generate_report_for_target(
                    report_target,
                    current_session=agent.session_state
                    if agent.session_state.target == report_target
                    else None,
                    report_format=config.session.report_format,
                )
                console.print(_("cli.report_generated", path=report_path))
                continue

            elif cmd_lower.startswith("persistent"):
                explicit_target = user_input[len("persistent") :].strip()
                persistent_target = explicit_target or current_target
                if not persistent_target:
                    console.print(
                        "[!] Primero define un objetivo con [bold]target <host>[/] o ejecuta [bold]persistent <host>[/]."
                    )
                    continue

                current_target, current_phase, restored_loaded = _prepare_repl_target(
                    agent,
                    persistent_target,
                    current_target,
                    current_phase,
                )
                persistent_target = current_target
                if restored_loaded:
                    console.print(_("cli.target_restored", target=persistent_target))

                from vulnclaw.agent.core import PersistentCycleResult

                rounds_per_cycle = config.session.persistent_rounds_per_cycle
                max_cycles = config.session.persistent_max_cycles
                auto_report = config.session.persistent_auto_report

                console.print(
                    Panel(
                        f"Objetivo: [bold]{persistent_target}[/]\n"
                        f"Rondas por ciclo: [bold]{rounds_per_cycle}[/]\n"
                        f"Ciclos máximos: [bold]{max_cycles}[/]\n"
                        f"Informe automático: {'[green]activado[/]' if auto_report else '[yellow]desactivado[/]'}",
                        title="Pentest persistente",
                        border_style="cyan",
                    )
                )

                persistent_prompt = (
                    f"Realizar una prueba de penetración persistente autorizada contra {persistent_target}. "
                    "Este objetivo está dentro del alcance y explícitamente autorizado."
                )

                all_cycle_results: list[PersistentCycleResult] = []

                def _on_persistent_step(round_num: int, cycle_num: int, result) -> None:
                    console.print(f"[dim]-- Ciclo {cycle_num} | Ronda {round_num} --[/]")
                    # TerminalStreamSink ya se muestra en streaming en tiempo real; el callback no vuelve a imprimir
                    console.print()
                    nonlocal current_target, current_phase
                    if result.target:
                        current_target = result.target
                    if result.phase:
                        current_phase = result.phase

                def _on_persistent_cycle(
                    cycle_num: int, cycle_result: PersistentCycleResult
                ) -> None:
                    all_cycle_results.append(cycle_result)
                    console.print(
                        Panel(
                            f"Ciclo {cycle_num} completado\n"
                            f"   Hallazgos totales: {cycle_result.total_findings}\n"
                            f"   Hallazgos nuevos: {cycle_result.new_findings}\n"
                            f"   Informe: {cycle_result.report_path or 'no generado'}",
                            title=f"Ciclo {cycle_num}",
                            border_style="green" if cycle_result.new_findings == 0 else "red",
                        )
                    )
                    console.print()

                try:

                    async def _run_persistent():
                        await mcp_manager._preinit_chrome_devtools()
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        return await agent.persistent_pentest(
                            user_input=persistent_prompt,
                            target=persistent_target,
                            rounds_per_cycle=rounds_per_cycle,
                            max_cycles=max_cycles,
                            auto_report=auto_report,
                            on_cycle_step=_on_persistent_step,
                            on_cycle_complete=_on_persistent_cycle,
                            stream_sink=sink,
                        )

                    asyncio.run(_run_persistent())
                    if auto_report and not all_cycle_results:
                        partial_report = _generate_report_for_target(
                            persistent_target,
                            current_session=agent.session_state,
                            report_format=config.session.report_format,
                        )
                        console.print(_("cli.partial_report", path=partial_report))
                except KeyboardInterrupt:
                    console.print(f"\n{_('persistent.interrupted_message')}")
                    if agent.session_state.findings:
                        try:
                            final_report = _generate_report_for_target(
                                persistent_target,
                                current_session=agent.session_state,
                                report_format=config.session.report_format,
                            )
                            console.print(_("persistent.final_report", path=final_report))
                        except Exception as exc:
                            console.print(_("persistent.failed_final_report", exc=exc))

                # Summary
                tf = len(agent.session_state.findings)
                console.print(
                    _("persistent.finished_summary", cycles=len(all_cycle_results), findings=tf)
                )
                continue

            elif cmd_lower == "think":
                # Toggle think tag display
                config.session.show_thinking = not config.session.show_thinking
                state_str = (
                    "[green]visible[/]" if config.session.show_thinking else "[yellow]oculto[/]"
                )
                console.print(f"[*] Visibilidad del razonamiento: {state_str}")
                console.print(_("cli.thinking_toggle_hint"))
                continue

            elif cmd_lower == "think on":
                config.session.show_thinking = True
                console.print(_("cli.thinking_shown"))
                continue

            elif cmd_lower == "think off":
                config.session.show_thinking = False
                console.print(_("cli.thinking_hidden"))
                continue

            # Handle auto mode persistence: exit auto mode on explicit commands
            if auto_mode_active and user_input.lower().strip() in (
                "chat", "manual", "exit auto", "un turno", "manual",
            ):
                auto_mode_active = False
                last_auto_input = ""
                console.print(_("cli.auto_mode_exited"))
                is_auto_mode = False
            elif auto_mode_active:
                is_auto_mode = True
            else:
                # Route to agent and detect whether this should be an autonomous loop
                is_auto_mode = _should_auto_pentest(user_input, current_target)

            # Detect target switch and reset context if the user mentions a new target
            new_target = _extract_target_from_input(user_input)
            if new_target and current_target and new_target != current_target:
                console.print(_("cli.target_switch", from_target=current_target, to_target=new_target))
                current_target = new_target
                current_phase = "Recon"
                agent.reset_context()
                # Reset auto mode on target switch
                auto_mode_active = False
                last_auto_input = ""

            # Save last auto input for resume on empty Enter
            if is_auto_mode:
                last_auto_input = user_input

            try:
                if is_auto_mode:
                    # Autonomous pentest loop
                    console.print(_("cli.enter_auto_mode"))
                    console.print()

                    # Por defecto se usa el motor solve dirigido por objetivos;
                    # con engine=rounds se recurre al antiguo bucle de rondas fijas
                    if getattr(config.session, "engine", "solve") == "solve":
                        async def _run_auto():
                            await mcp_manager._preinit_chrome_devtools()
                            sink = TerminalStreamSink(console, config.session.show_thinking)

                            async def call():
                                return await agent.solve(
                                    user_input,
                                    target=current_target,
                                    max_steps=config.session.solve_max_steps,
                                    max_intents=config.session.solve_max_intents,
                                    max_tool_rounds=config.session.solve_max_tool_rounds,
                                    stream_sink=sink,
                                    on_event=_make_solve_event_printer(console),
                                )

                            async def after_result(result):
                                board = agent.context.state.board.get_summary()
                                done = board.get("completed")
                                console.print()
                                console.print(
                                    Panel(
                                        f"{'✅ Objetivo alcanzado' if done else '⊘ No alcanzado'} — "
                                        f"facts={board.get('facts', 0)} intents={board.get('intents', 0)}\n"
                                        f"Motivo: {board.get('complete_reason') or 'exploración finalizada'}",
                                        title="Solve",
                                        border_style="green" if done else "yellow",
                                    )
                                )

                            await _run_repl_agent_call(agent, call=call, after_result=after_result)

                        asyncio.run(_run_auto())
                        auto_mode_active = True
                        console.print(_("cli.auto_mode_hint"))
                        continue

                    async def _run_auto():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        async def call():
                            def on_step(round_num, result):
                                nonlocal current_target, current_phase
                                console.print(f"[dim]-- Ronda {round_num} --[/]")
                                console.print()
                                if result.target:
                                    current_target = result.target
                                if result.phase:
                                    current_phase = result.phase

                            return await agent.auto_pentest(
                                user_input,
                                target=current_target,
                                max_rounds=config.session.max_rounds,
                                on_step=on_step,
                                stream_sink=sink,
                            )

                        async def after_result(results):
                            if results:
                                total_findings = len(agent.session_state.findings)
                                total_steps = len(agent.session_state.executed_steps)
                                console.print()
                                console.print(
                                    Panel(
                                        f"{_('auto_pentest.finished')}\n"
                                        f"{_('auto_pentest.rounds', rounds=len(results))}\n"
                                        f"{_('auto_pentest.steps', steps=total_steps)}\n"
                                        f"{_('auto_pentest.findings', findings=total_findings)}",
                                        title=_("auto_pentest.title"),
                                        border_style="green" if total_findings == 0 else "red",
                                    )
                                )

                                if any(
                                    token in user_input.lower()
                                    for token in (
                                        "salida",
                                        "guardar",
                                        "escribir",
                                        "exportar",
                                        "save",
                                        "write",
                                        "export",
                                    )
                                ):
                                    _auto_save_recon_report(agent, user_input, config)

                        await _run_repl_agent_call(agent, call=call, after_result=after_result)

                    asyncio.run(_run_auto())
                    auto_mode_active = True
                    console.print(_("cli.auto_mode_hint"))

                else:
                    # Single-turn chat
                    async def _run_agent():
                        await mcp_manager._preinit_chrome_devtools()
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        async def call():
                            return await agent.chat(user_input, target=current_target, stream_sink=sink)

                        async def after_result(result):
                            nonlocal current_target, current_phase
                            if result:
                                if result.target:
                                    current_target = result.target
                                if result.phase:
                                    current_phase = result.phase
                                # Comentado: la salida en streaming ya se muestra en tiempo real vía TerminalStreamSink, no hace falta reimprimir
                                # if result.output:
                                #     _print_agent_output(result.output, config)

                        await _run_repl_agent_call(agent, call=call, after_result=after_result)

                    asyncio.run(_run_agent())

            except KeyboardInterrupt:
                if is_auto_mode:
                    auto_mode_active = False
                    console.print()
                    console.print(_("cli.interrupted"))
                    console.print(_("cli.auto_resume_hint"))
                else:
                    console.print(f"\n{_('cli.interrupted')}")
            except Exception as e:
                # Escape Rich markup chars in exception message to prevent MarkupError
                from rich.markup import escape as rich_escape

                console.print(_("cli.error", msg=rich_escape(str(e))))

        except KeyboardInterrupt:
            now = time.monotonic()
            if exit_requested and (now - _last_ctrlc_time) < 3.0:
                console.print(_("cli.bye"))
                break
            exit_requested = True
            _last_ctrlc_time = now
            console.print(f"\n{_('cli.press_again')}")
        except EOFError:
            break

    # Cleanup — suppress SIGINT to prevent re-trigger during threading shutdown
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    mcp_manager.stop_all()
    console.print("[dim]Servicios MCP detenidos.[/]")


def _print_help() -> None:
    """Print REPL help."""
    help_text = f"""
 [bold]{_("help.commands")}[/]:
  {_("help.target")}
  {_("help.status")}
  {_("help.tools")}
  {_("help.report")}
  {_("help.think")}
  {_("help.think_on_off")}
  {_("help.persistent")}
  {_("help.persistent_host")}
  {_("help.clear")}
  {_("help.chat")}
  {_("help.help")}
  {_("help.exit")}

 [bold]{_("help.auto_mode")}[/]:
  {_("help.auto_mode_desc")}
  {_("help.auto_mode_example")}
  {_("help.auto_mode_stays")}

 [bold]{_("help.persistent_mode")}[/]:
  {_("help.persistent_mode_desc")}
  {_("help.persistent_cli")}
  {_("help.persistent_repl")}

 [bold]{_("help.examples")}[/]:
  {_("help.example_pentest")}
  {_("help.example_scan")}
  {_("help.example_vuln")}
  {_("help.example_exploit")}
  {_("help.example_report")}
"""
    console.print(Panel(help_text, title=_("help.title"), border_style="cyan"))


def _print_status(agent, mcp_manager, target, phase, config) -> None:
    """Print current session status."""
    think_state = "[green]visible[/]" if config.session.show_thinking else "[yellow]oculto[/]"
    phase_label = _localized_phase_label(phase)
    console.print(
        Panel(
            f"{_('status.target', target=target or 'Not set')}\n"
            f"{_('status.phase', phase=phase_label)}\n"
            f"{_('status.mcp_services', count=mcp_manager.running_count())}\n"
            f"{_('status.tools', count=len(mcp_manager.list_available_tools()))}\n"
            f"{_('status.thinking', state=think_state)}",
            title=_("status.title"),
            border_style="green",
        )
    )


def _validate_headless_choices(
    scan_mode: str, fail_on: str, scope_mode: str
) -> Optional[str]:
    """Return an error message for a bad headless choice, else ``None``."""
    if scan_mode not in headless.SCAN_MODES:
        return f"--scan-mode debe ser uno de: {', '.join(headless.SCAN_MODES)}"
    if fail_on not in headless.FAIL_ON_MODES:
        return f"--fail-on debe ser uno de: {', '.join(headless.FAIL_ON_MODES)}"
    if scope_mode not in headless.SCOPE_MODES:
        return f"--scope-mode debe ser uno de: {', '.join(headless.SCOPE_MODES)}"
    return None


def _run_non_interactive(
    *,
    target: str,
    output: Optional[str],
    profile: "headless.ScanProfile",
    scan_mode: str,
    scope_mode: str,
    fail_on: str,
    run_coro_factory,
    classification_holder: dict,
) -> None:
    """Drive a headless run: no prompts, structured output, exit-code contract.

    Any crash during the scan exits :data:`headless.EXIT_ERROR` (1) — a broken
    scan never exits 0. On completion the finding set is mapped to an exit code
    under ``--fail-on`` and a ``summary.json`` is written into the run directory.
    """
    from datetime import datetime

    try:
        asyncio.run(run_coro_factory())
    except typer.Exit:
        raise
    except BaseException as exc:  # noqa: BLE001 - CI must see a nonzero exit, not a traceback
        err_console.print(f"[!] El escaneo no se completó: {type(exc).__name__}: {exc}")
        raise typer.Exit(headless.EXIT_ERROR) from exc

    classification = classification_holder.get("classification") or headless.FindingClassification(
        verified=0, candidates=0
    )
    exit_code = headless.determine_exit_code(classification, fail_on)

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = headless.run_directory(RUNS_DIR, target, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    # Co-locate the report inside the run directory unless the caller pinned a
    # path with --output, so all structured output for a run lives in one place.
    report_output = output or str(run_dir / "report.md")
    report_path = _generate_report_for_target(target, output_path=report_output)

    summary = headless.build_run_summary(
        target=target,
        scan_mode=scan_mode,
        scope_mode=scope_mode,
        fail_on=fail_on,
        profile=profile,
        classification=classification,
        exit_code=exit_code,
        report_path=str(report_path),
    )
    summary_path = headless.write_run_artifacts(run_dir, summary)

    console.print(
        f"[*] hallazgos: verificados={classification.verified} "
        f"candidatos={classification.candidates} | "
        f"salida={exit_code} ({headless.exit_code_meaning(exit_code)})"
    )
    console.print(f"[*] artefactos de la ejecución: {summary_path}")
    console.print(_("cli.report_generated", path=report_path))
    raise typer.Exit(exit_code)


def _run_context_kwargs(
    *,
    run_name: Optional[str] = None,
    resume_run_name: Optional[str] = None,
    runs_dir: Optional[str] = None,
    additional_targets: Optional[list[str]] = None,
    target_type: Optional[str] = None,
    mount: bool = False,
    repair: bool = False,
    force_fresh: bool = False,
    no_import: bool = False,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if run_name:
        kwargs["run_name"] = run_name
    if resume_run_name:
        kwargs["resume_run_name"] = resume_run_name
    if runs_dir:
        kwargs["runs_dir"] = runs_dir
    if additional_targets:
        kwargs["additional_targets"] = additional_targets
    if target_type:
        kwargs["target_type"] = target_type
    if mount:
        kwargs["mount"] = mount
    if repair:
        kwargs["repair"] = repair
    if force_fresh:
        kwargs["force_fresh"] = force_fresh
    if no_import:
        kwargs["no_import"] = no_import
    return kwargs


def _print_run_completion_summary(summary: dict[str, Any]) -> None:
    run_name = summary.get("run_name")
    run_dir = summary.get("run_dir")
    if not run_name or not run_dir:
        return
    artifacts = summary.get("artifact_locations", {})
    console.print(
        Panel(
            f"Ejecución: [bold]{run_name}[/]\n"
            f"Directorio: [bold]{run_dir}[/]\n"
            f"Hallazgos: [bold]{summary.get('verified_count', 0)} verificados / "
            f"{summary.get('pending_count', 0)} pendientes / "
            f"{summary.get('candidate_count', 0)} candidatos[/]\n"
            f"Artefactos: hallazgos={artifacts.get('findings', '')} "
            f"informes={artifacts.get('reports', '')} evidencia={artifacts.get('evidence', '')}\n"
            f"Reanudar: [bold]{summary.get('resume_command', '')}[/]\n"
            f"Salida: [bold]{summary.get('exit_code', 0)}[/] "
            f"({summary.get('exit_meaning', 'completado')})",
            title="Resumen de la ejecución",
            border_style="green" if summary.get("exit_code", 0) == 0 else "yellow",
        )
    )


# ── Sub-commands ────────────────────────────────────────────────────


app = typer.Typer(
    name="vulnclaw",
    help="VulnClaw - CLI de pentesting con IA (ejecuta 'vulnclaw tui' para el entorno TUI)",
    no_args_is_help=False,
    add_completion=False,
)


@app.command()
def run(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    scope: str = typer.Option("full", help="Alcance de la prueba: full, web, api, mobile"),
    output: Optional[str] = typer.Option(None, help="Ruta del archivo de informe de salida"),
    # [Añadido] 2026-06-10 Nyaecho - TUI impulsado por lenguaje natural: permite
    #   pasar un prompt personalizado vía --prompt que sobrescribe el prompt generado automáticamente
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Prompt personalizado en lenguaje natural (sobrescribe el prompt generado automáticamente)"
    ),
    engine: Optional[str] = typer.Option(
        None,
        "--engine",
        help="Motor autónomo para esta ejecución: solve, team o rounds",
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restringe las pruebas a un único puerto"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restringe las pruebas a un único host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restringe las pruebas a una única ruta"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Host explícitamente bloqueado"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Ruta explícitamente bloqueada"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Acciones permitidas, separadas por comas"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Acciones bloqueadas, separadas por comas"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Reanuda desde un id de snapshot específico del objetivo"
    ),
    # ── Headless / CI knobs ────────────────────────────────────────────
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Modo headless: sin preguntas, salida estructurada en el directorio de la "
        "ejecución y un código de salida distintivo (ver --fail-on). Pensado para CI.",
    ),
    scan_mode: str = typer.Option(
        headless.DEFAULT_SCAN_MODE,
        "--scan-mode",
        help="Preajuste de profundidad sobre los parámetros de esfuerzo: quick | standard | deep. "
        "Las flags --max-* explícitas sobrescriben el preajuste.",
    ),
    fail_on: str = typer.Option(
        headless.DEFAULT_FAIL_ON,
        "--fail-on",
        help="Qué clase de hallazgo dispara una salida distinta de cero: verified | any | never.",
    ),
    scope_mode: str = typer.Option(
        headless.DEFAULT_SCOPE_MODE,
        "--scope-mode",
        help="Selección de alcance registrada para la ejecución: full (superficie completa, "
        "comportamiento actual) | auto (alcance por diferencias sobre el código modificado — "
        "consumido por el modelo de diff-scope del Target, #35; usa full como respaldo hasta "
        "que eso se implemente).",
    ),
    max_steps: Optional[int] = typer.Option(
        None, "--max-steps", help="Sobrescribe el límite de pasos de exploración del scan-mode"
    ),
    max_intents: Optional[int] = typer.Option(
        None, "--max-intents", help="Sobrescribe el máximo de intents por paso del scan-mode"
    ),
    max_tool_rounds: Optional[int] = typer.Option(
        None, "--max-tool-rounds", help="Sobrescribe las rondas de herramientas por intent del scan-mode"
    ),
    max_parallel: Optional[int] = typer.Option(
        None, "--max-parallel", help="Sobrescribe el límite de paralelismo del scan-mode (1 = un solo agente)"
    ),
    max_rounds: Optional[int] = typer.Option(
        None, "--max-rounds", help="Sobrescribe el límite de rondas del motor legacy del scan-mode"
    ),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por su nombre"
    ),
    runs_dir: Optional[str] = typer.Option(
        None, "--runs-dir", help="Raíz del directorio de ejecuciones (sobrescribe VULNCLAW_RUNS_DIR)"
    ),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(
        None, "--target-type", help="Sobrescribe el tipo de objetivo: local_repo, repo_url, web_url, domain, ip"
    ),
    mount: bool = typer.Option(
        False, "--mount", help="Usa el modo de ingreso por montaje para objetivos de repositorio local"
    ),
    repair: bool = typer.Option(
        False, "--repair", help="Repara una ejecución corrupta revirtiendo al último snapshot válido"
    ),
    force_fresh: bool = typer.Option(
        False, "--force-fresh", help="Inicia una ejecución nueva sin sobrescribir una corrupta"
    ),
    no_import: bool = typer.Option(
        False, "--no-import", help="Lee el estado legacy del objetivo sin importarlo a una ejecución"
    ),
) -> None:
    """Ejecuta un flujo completo de pentest autorizado.

    Interactivo por defecto. Pasa ``--non-interactive`` para una ejecución
    headless en CI: sin preguntas, un ``summary.json`` legible por máquina en
    el directorio de la ejecución, y un código de salida que permite a un
    pipeline distinguir un escaneo limpio (0) de uno roto (1), de uno que
    confirmó un hallazgo verificado (2) o solo candidatos (3).
    """
    config = load_config()

    # A bad target / scan-mode / fail-on / scope-mode is a misconfiguration:
    # exit 1 (never a silent green run).
    if not target or not target.strip():
        err_console.print("[!] Se requiere un objetivo no vacío.")
        raise typer.Exit(headless.EXIT_ERROR)
    bad_choice = _validate_headless_choices(scan_mode, fail_on, scope_mode)
    if bad_choice is not None:
        err_console.print(f"[!] {bad_choice}")
        raise typer.Exit(headless.EXIT_ERROR)
    if not has_llm_credentials(config.llm):
        err_console.print("[!] Configura primero las credenciales del LLM (api_key o auth_mode).")
        raise typer.Exit(headless.EXIT_ERROR)
    if engine is not None and engine not in {"solve", "team", "rounds"}:
        err_console.print("[!] --engine debe ser uno de: solve, team, rounds")
        raise typer.Exit(headless.EXIT_ERROR)

    profile = headless.resolve_scan_profile(
        config,
        scan_mode,
        max_steps=max_steps,
        max_intents=max_intents,
        max_tool_rounds=max_tool_rounds,
        max_parallel=max_parallel,
        max_rounds=max_rounds,
    )

    console.print(
        f"[*] Objetivo: [bold]{target}[/] | Alcance: [bold]{scope}[/] | "
        f"Modo: [bold]{profile.scan_mode}[/]"
        + (" | [bold]no interactivo[/]" if non_interactive else "")
    )

    task_prompt = prompt if prompt else (
        f"Realizar una prueba de penetración autorizada de tipo {scope} contra {target}. "
        "Este objetivo está dentro del alcance y explícitamente autorizado."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("run", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(headless.EXIT_ERROR)

    board_holder: dict = {}
    classification_holder: dict = {}

    async def _run():
        async def runner(agent, shared_config):
            # Apply the resolved fan-out / round caps so solve/team/auto_pentest
            # (which read them off config.session) honour the scan-mode preset.
            shared_config.session.solve_max_parallel = profile.max_parallel
            shared_config.session.max_rounds = profile.max_rounds
            # In headless mode suppress streaming thinking so nothing blocks on a TTY.
            sink = (
                None
                if non_interactive
                else TerminalStreamSink(console, shared_config.session.show_thinking)
            )
            on_event = None if non_interactive else _make_solve_event_printer(console)
            selected_engine = engine or getattr(shared_config.session, "engine", "solve")
            # Por defecto se usa el motor solve dirigido por objetivos; engine=team
            # habilita el equipo de roles; engine=rounds recurre al antiguo bucle
            if selected_engine == "solve":
                result = await agent.solve(
                    task_prompt,
                    target=target,
                    max_steps=profile.max_steps,
                    max_intents=profile.max_intents,
                    max_tool_rounds=profile.max_tool_rounds,
                    stream_sink=sink,
                    on_event=on_event,
                )
            elif selected_engine == "team":
                from vulnclaw.agent.team import run_team_pentest

                def agent_factory():
                    return agent.__class__(shared_config, getattr(agent, "mcp_manager", None))

                result = await run_team_pentest(
                    agent,
                    user_input=task_prompt,
                    target=target,
                    agent_factory=agent_factory,
                    max_steps=profile.max_steps,
                    max_intents=profile.max_intents,
                    max_tool_rounds=profile.max_tool_rounds,
                    # team fan-out reads its own cap (not config), so pass the
                    # resolved scan-mode profile explicitly or quick/--max-parallel
                    # would be ignored and it would fan out to every ready step.
                    max_parallel=profile.max_parallel,
                    stream_sink=sink,
                    on_event=on_event,
                )
            else:
                result = await agent.auto_pentest(
                    task_prompt,
                    target=target,
                    max_rounds=profile.max_rounds,
                    on_step=lambda r, res: (
                        _print_agent_output(
                            f"[dim]Ronda {r}[/]: {res.output[:200]}...", shared_config
                        )
                        if res.output and not non_interactive
                        else None
                    ),
                    stream_sink=sink,
                )
            board = getattr(getattr(getattr(agent, "context", None), "state", None), "board", None)
            if board is not None:
                board_holder["board"] = board.get_summary()
            classification_holder["classification"] = headless.classify_findings(
                getattr(agent, "session_state", None)
            )
            return result

        result = await _run_cli_orchestrated_task(
            command="run",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )
        return result

    if non_interactive:
        _run_non_interactive(
            target=target,
            output=output,
            profile=profile,
            scan_mode=scan_mode,
            scope_mode=scope_mode,
            fail_on=fail_on,
            run_coro_factory=_run,
            classification_holder=classification_holder,
        )
        return

    orchestrated = asyncio.run(_run())
    if board_holder.get("board"):
        board = board_holder["board"]
        status = "✅ Objetivo alcanzado" if board.get("completed") else "⊘ No alcanzado"
        console.print(
            f"\n[bold]{status}[/bold] — facts={board.get('facts', 0)} "
            f"intents={board.get('intents', 0)} Motivo: {board.get('complete_reason') or 'exploración finalizada'}"
        )
    else:
        total_findings = orchestrated.summary["findings_count"]
        console.print(_("cli.pentest_finished", findings=total_findings))

    report_path = _generate_report_for_target(target, output_path=output)
    console.print(_("cli.report_generated", path=report_path))


@app.command()
def solve(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    goal: Optional[str] = typer.Option(
        None, "--goal", help="Condición de éxito, ej. 'capturar la flag' / 'obtener una shell'"
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Descripción de tarea personalizada (sobrescribe la generada automáticamente)"
    ),
    max_steps: int = typer.Option(
        40, "--max-steps", help="Límite de seguridad en pasos de exploración (NO es una longitud fija de flujo)"
    ),
    max_intents: int = typer.Option(3, "--max-intents", help="Máximo de nuevos intents por paso de razonamiento"),
    max_tool_rounds: int = typer.Option(
        4, "--max-tool-rounds", help="Máximo de rondas de uso de herramientas por exploración de intent"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(None, "--snapshot", help="Reanuda desde un id de snapshot"),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por su nombre"
    ),
    runs_dir: Optional[str] = typer.Option(None, "--runs-dir", help="Raíz del directorio de ejecuciones"),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(None, "--target-type", help="Sobrescribe el tipo de objetivo"),
    mount: bool = typer.Option(False, "--mount", help="Usa el modo de ingreso por montaje"),
    repair: bool = typer.Option(False, "--repair", help="Repara una ejecución corrupta"),
    force_fresh: bool = typer.Option(False, "--force-fresh", help="Inicia una ejecución nueva"),
    no_import: bool = typer.Option(False, "--no-import", help="No importa el estado legacy"),
) -> None:
    """Bucle solve dirigido por objetivo — se ejecuta hasta cumplir la meta o agotar la frontera de exploración.

    A diferencia de `run`, no tiene un número fijo de rondas. Busca en un grafo
    de Facts/Intents desde el objetivo hacia la meta y se detiene al lograrlo
    o cuando no queda ningún camino.
    """
    config = load_config()
    if not has_llm_credentials(config.llm):
        err_console.print("[!] Configura primero las credenciales del LLM (api_key o auth_mode).")
        raise typer.Exit(1)

    resolved_goal = goal or "encontrar flag / obtener shell / confirmar y verificar vulnerabilidades de alto valor"
    task_prompt = prompt or (
        f"Realizar una prueba de penetración autorizada contra {target}. Este es un objetivo "
        f"explícitamente autorizado y dentro del alcance. Objetivo (goal): {resolved_goal}."
    )
    console.print(f"[*] Objetivo: [bold]{target}[/] | Meta: [bold]{resolved_goal}[/]")

    on_event = _make_solve_event_printer(console)
    holder: dict = {}

    async def _run():
        async def runner(agent, shared_config):
            sink = TerminalStreamSink(console, shared_config.session.show_thinking)
            result = await agent.solve(
                task_prompt,
                target=target,
                goal=resolved_goal,
                max_steps=max_steps,
                max_intents=max_intents,
                max_tool_rounds=max_tool_rounds,
                stream_sink=sink,
                on_event=on_event,
            )
            holder["board"] = agent.context.state.board.get_summary()
            return result

        return await _run_cli_orchestrated_task(
            command="solve",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )

    asyncio.run(_run())
    board = holder.get("board") or {}
    status = "✅ Objetivo alcanzado" if board.get("completed") else "⊘ No alcanzado"
    console.print(
        f"\n[bold]{status}[/bold] — facts={board.get('facts', 0)} "
        f"intents={board.get('intents', 0)} Motivo: {board.get('complete_reason') or 'exploración finalizada'}"
    )


@app.command()
def persistent(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    rounds: int = typer.Option(
        0, "--rounds", "-r", help="Rondas por ciclo (0=usar config, por defecto 100)"
    ),
    cycles: int = typer.Option(0, "--cycles", "-c", help="Ciclos máximos (0=usar config, por defecto 10)"),
    no_report: bool = typer.Option(
        False, "--no-report", help="Desactiva el informe automático después de cada ciclo"
    ),
    # [Añadido] 2026-06-10 Nyaecho - TUI impulsado por lenguaje natural: permite
    #   pasar un prompt personalizado vía --prompt que sobrescribe el prompt generado automáticamente
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Prompt personalizado en lenguaje natural (sobrescribe el prompt generado automáticamente)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restringe las pruebas a un único puerto"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restringe las pruebas a un único host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restringe las pruebas a una única ruta"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Host explícitamente bloqueado"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Ruta explícitamente bloqueada"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Acciones permitidas, separadas por comas"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Acciones bloqueadas, separadas por comas"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Reanuda desde un id de snapshot específico del objetivo"
    ),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por su nombre"
    ),
    runs_dir: Optional[str] = typer.Option(None, "--runs-dir", help="Raíz del directorio de ejecuciones"),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(None, "--target-type", help="Sobrescribe el tipo de objetivo"),
    mount: bool = typer.Option(False, "--mount", help="Usa el modo de ingreso por montaje"),
    repair: bool = typer.Option(False, "--repair", help="Repara una ejecución corrupta"),
    force_fresh: bool = typer.Option(False, "--force-fresh", help="Inicia una ejecución nueva"),
    no_import: bool = typer.Option(False, "--no-import", help="No importa el estado legacy"),
) -> None:
    """Ejecuta un pentest persistente autorizado a través de múltiples ciclos."""
    from vulnclaw.agent.core import PersistentCycleResult

    config = load_config()
    if not has_llm_credentials(config.llm):
        err_console.print("[!] Configura primero las credenciales del LLM (api_key o auth_mode).")
        raise typer.Exit(1)

    # Resolve parameters (CLI override -> config defaults)
    rounds_per_cycle = rounds if rounds > 0 else config.session.persistent_rounds_per_cycle
    max_cycles = cycles if cycles > 0 else config.session.persistent_max_cycles
    auto_report = config.session.persistent_auto_report and not no_report

    console.print(
        Panel(
            f"Objetivo: [bold]{target}[/]\n"
            f"Rondas por ciclo: [bold]{rounds_per_cycle}[/]\n"
            f"Ciclos máximos: [bold]{max_cycles}[/] {'(sin límite)' if max_cycles == 0 else ''}\n"
            f"Informe automático: {'[green]activado[/]' if auto_report else '[yellow]desactivado[/]'}\n"
            f"Rondas totales máximas: [bold]{rounds_per_cycle * max_cycles if max_cycles > 0 else 'sin límite'}[/]",
            title="Pentest persistente",
            border_style="cyan",
        )
    )

    task_prompt = prompt if prompt else (
        f"Realizar una prueba de penetración persistente autorizada contra {target}. "
        "Este objetivo está dentro del alcance y explícitamente autorizado."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("persistent", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    # Track stats
    all_cycle_results: list[PersistentCycleResult] = []
    interrupted = False

    def _on_cycle_step(round_num: int, cycle_num: int, result) -> None:
        """Real-time output for each step within a cycle."""
        console.print(f"[dim]-- Ciclo {cycle_num} | Ronda {round_num} --[/]")
        # TerminalStreamSink ya se muestra en streaming en tiempo real; el callback no vuelve a imprimir
        console.print()

    def _on_cycle_complete(cycle_num: int, cycle_result: PersistentCycleResult) -> None:
        """Callback after each cycle completes."""
        all_cycle_results.append(cycle_result)
        console.print(
            Panel(
                f"Ciclo {cycle_num} completado\n"
                f"   Pasos ejecutados: {cycle_result.total_steps}\n"
                f"   Hallazgos totales: {cycle_result.total_findings}\n"
                f"   Hallazgos nuevos: {cycle_result.new_findings}\n"
                f"   Informe: {cycle_result.report_path or 'no generado'}",
                title=f"Resultado del ciclo {cycle_num}",
                border_style="green" if cycle_result.new_findings == 0 else "red",
            )
        )
        console.print()

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            return await agent.persistent_pentest(
                user_input=task_prompt,
                target=target,
                rounds_per_cycle=rounds_per_cycle,
                max_cycles=max_cycles,
                auto_report=auto_report,
                on_cycle_step=_on_cycle_step,
                on_cycle_complete=_on_cycle_complete,
                stream_sink=sink,
            )

        return await _run_cli_orchestrated_task(
            command="persistent",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )

    try:
        orchestrated = asyncio.run(_run())
    except KeyboardInterrupt:
        interrupted = True
        console.print("\n[!] El usuario interrumpió el pentest persistente")
        orchestrated = None

    summary = (
        orchestrated.summary
        if orchestrated
        else {
            "findings_count": 0,
            "executed_steps": 0,
        }
    )
    total_findings = summary["findings_count"]
    total_steps = summary["executed_steps"]
    completed_cycles = len(all_cycle_results)

    console.print()
    console.print(
        Panel(
            f"{'Interrumpido por el usuario' if interrupted else 'Prueba completada'}\n\n"
            f"  Ciclos completados: [bold]{completed_cycles}[/]\n"
            f"  Pasos ejecutados: [bold]{total_steps}[/]\n"
            f"  Hallazgos: [bold]{total_findings}[/]",
            title="Resumen del pentest persistente",
            border_style="red" if total_findings > 0 else "green",
        )
    )

    if auto_report and all_cycle_results:
        console.print("\n[bold]Informes por ciclo[/]:")
        for cr in all_cycle_results:
            if cr.report_path and "failed" not in str(cr.report_path).lower():
                console.print(f"  Ciclo {cr.cycle_num}: {cr.report_path}")


@app.command()
def recon(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    # [Añadido] 2026-06-10 Nyaecho - TUI impulsado por lenguaje natural: permite
    #   pasar un prompt personalizado vía --prompt que sobrescribe el prompt generado automáticamente
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Prompt personalizado en lenguaje natural (sobrescribe el prompt generado automáticamente)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restringe las pruebas a un único puerto"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restringe las pruebas a un único host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restringe las pruebas a una única ruta"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Host explícitamente bloqueado"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Ruta explícitamente bloqueada"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Acciones permitidas, separadas por comas"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Acciones bloqueadas, separadas por comas"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Reanuda desde un id de snapshot específico del objetivo"
    ),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por su nombre"
    ),
    runs_dir: Optional[str] = typer.Option(None, "--runs-dir", help="Raíz del directorio de ejecuciones"),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(None, "--target-type", help="Sobrescribe el tipo de objetivo"),
    mount: bool = typer.Option(False, "--mount", help="Usa el modo de ingreso por montaje"),
    repair: bool = typer.Option(False, "--repair", help="Repara una ejecución corrupta"),
    force_fresh: bool = typer.Option(False, "--force-fresh", help="Inicia una ejecución nueva"),
    no_import: bool = typer.Option(False, "--no-import", help="No importa el estado legacy"),
) -> None:
    """Ejecuta solo la fase de reconocimiento."""
    task_prompt = prompt if prompt else f"Realizar un reconocimiento autorizado contra {target} sin explotación."
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("recon", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            # TerminalStreamSink ya se muestra en streaming en tiempo real; no se repite console.print
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="recon",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )

    asyncio.run(_run())


@app.command()
def scan(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    ports: Optional[str] = typer.Option(None, help="Rango de puertos, ej. 80,443,8080"),
    # [Añadido] 2026-06-10 Nyaecho - TUI impulsado por lenguaje natural: permite
    #   pasar un prompt personalizado vía --prompt que sobrescribe el prompt generado automáticamente
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Prompt personalizado en lenguaje natural (sobrescribe el prompt generado automáticamente)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restringe las pruebas a un único puerto"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restringe las pruebas a un único host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restringe las pruebas a una única ruta"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Host explícitamente bloqueado"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Ruta explícitamente bloqueada"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Acciones permitidas, separadas por comas"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Acciones bloqueadas, separadas por comas"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Reanuda desde un id de snapshot específico del objetivo"
    ),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por su nombre"
    ),
    runs_dir: Optional[str] = typer.Option(None, "--runs-dir", help="Raíz del directorio de ejecuciones"),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(None, "--target-type", help="Sobrescribe el tipo de objetivo"),
    mount: bool = typer.Option(False, "--mount", help="Usa el modo de ingreso por montaje"),
    repair: bool = typer.Option(False, "--repair", help="Repara una ejecución corrupta"),
    force_fresh: bool = typer.Option(False, "--force-fresh", help="Inicia una ejecución nueva"),
    no_import: bool = typer.Option(False, "--no-import", help="No importa el estado legacy"),
) -> None:
    """Ejecuta solo el escaneo de vulnerabilidades."""
    port_hint = f", enfocado en los puertos {ports}" if ports else ""
    task_prompt = prompt if prompt else f"Realizar un escaneo de vulnerabilidades autorizado contra {target}{port_hint} sin explotación."
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("scan", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            # TerminalStreamSink ya se muestra en streaming en tiempo real; no se repite console.print
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="scan",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )

    asyncio.run(_run())


@app.command("network-scan")
def network_scan(
    target: Optional[str] = typer.Argument(
        None, help="Host/IP/CIDR objetivo; por defecto usa la subred Wi-Fi conectada actualmente"
    ),
    profile: str = typer.Option(
        "adaptive",
        "--profile",
        help="Perfil de escaneo de red: adaptive, fast, thorough, stealth",
    ),
    ports: Optional[str] = typer.Option(None, "--ports", help="Rango de puertos, p. ej. 80,443,1-1000"),
    max_rounds: int = typer.Option(
        0, "--max-rounds", help="Rondas de seguimiento del Agent (0=usar el valor por defecto de la configuración)"
    ),
    parallel_agents: int = typer.Option(
        1,
        "--parallel-agents",
        min=1,
        help="Cantidad de sub-Agents derivados en paralelo sobre la superficie de ataque descubierta (1 = sin paralelismo)",
    ),
    parallel_depth: int = typer.Option(
        1,
        "--parallel-depth",
        min=1,
        help="Número de oleadas acotadas de descubrimiento de superficie de ataque de los sub-Agents",
    ),
    worker_rounds: int = typer.Option(
        3,
        "--worker-rounds",
        min=1,
        help="Rondas de ejecución de cada sub-Agent worker",
    ),
    surface_limit: int = typer.Option(
        20,
        "--surface-limit",
        min=1,
        help="Cantidad máxima de superficies de ataque usadas para derivar sub-Agents en paralelo",
    ),
    safe_probes: bool = typer.Option(
        True,
        "--safe-probes/--no-safe-probes",
        help="Tras el escaneo nmap, por defecto solo se ejecutan sondeos de verificación no destructivos",
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Prompt personalizado en lenguaje natural (sobrescribe el prompt generado automáticamente)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restringe las pruebas a un solo puerto"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restringe las pruebas a un solo host"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Host explícitamente bloqueado"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Acciones permitidas separadas por comas"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Acciones bloqueadas separadas por comas"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Reanuda desde un id de snapshot de objetivo específico"
    ),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por nombre de ejecución"
    ),
    runs_dir: Optional[str] = typer.Option(None, "--runs-dir", help="Raíz del directorio de ejecuciones"),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(None, "--target-type", help="Sobrescribe el tipo de objetivo"),
    mount: bool = typer.Option(False, "--mount", help="Usa el modo de ingreso mount"),
    repair: bool = typer.Option(False, "--repair", help="Repara una ejecución corrupta"),
    force_fresh: bool = typer.Option(False, "--force-fresh", help="Inicia una ejecución nueva"),
    no_import: bool = typer.Option(False, "--no-import", help="No importa el estado heredado"),
) -> None:
    """Ejecuta un escaneo de red basado en nmap y hace seguimiento de los puntos débiles."""
    normalized_profile = profile.strip().lower()
    if normalized_profile not in {"adaptive", "fast", "thorough", "stealth"}:
        err_console.print("[!] profile debe ser uno de los siguientes: adaptive, fast, thorough, stealth")
        raise typer.Exit(1)

    detected_wifi = None
    scan_target = target.strip() if target else ""
    if not scan_target:
        from vulnclaw.agent.network_scan import detect_connected_wifi_target

        try:
            detected_wifi = detect_connected_wifi_target()
            scan_target = detected_wifi.cidr
        except RuntimeError as exc:
            err_console.print(f"[!] {exc}")
            raise typer.Exit(1)

    port_hint = f" limited to ports {ports}" if ports else ""
    follow_up = (
        "Then prioritize weak links and perform safe, non-destructive verification probes only."
        if safe_probes
        else "Then summarize weak links without running follow-up probes."
    )
    task_prompt = prompt if prompt else (
        f"Perform an authorized {normalized_profile} network scan against {scan_target}{port_hint}. "
        f"Use the nmap_scan tool with profile={normalized_profile}"
        f"{f' and ports={ports}' if ports else ''}. "
        f"{follow_up} Record open services and candidate weak-link findings in target state. "
        "Do not brute force credentials, run destructive payloads, or perform post-exploitation."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt,
        only_port,
        only_host,
        None,
        blocked_host,
        None,
    )

    effective_allow_actions = allow_actions
    effective_block_actions = block_actions
    if safe_probes and not allow_actions and not block_actions:
        effective_allow_actions = "recon,scan"
    task_prompt = _append_action_constraints(
        task_prompt, effective_allow_actions, effective_block_actions
    )

    violation = validate_action_constraints("scan", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Objetivo: [bold]{scan_target}[/]\n"
            + (
                f"Interfaz Wi-Fi: [bold]{detected_wifi.interface}[/] ({detected_wifi.address})\n"
                if detected_wifi
                else ""
            )
            +
            f"Perfil: [bold]{normalized_profile}[/]\n"
            f"Puertos: [bold]{ports or 'valor por defecto del perfil'}[/]\n"
            f"Estrategia de seguimiento: [bold]{'sondeo seguro' if safe_probes else 'solo resumen'}[/]\n"
            f"Número de Agents en paralelo: [bold]{parallel_agents}[/]"
            + (
                f" (profundidad {parallel_depth}, {worker_rounds} rondas por worker)"
                if parallel_agents > 1
                else ""
            ),
            title="Escaneo de red",
            border_style="cyan",
        )
    )

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            rounds = max_rounds if max_rounds > 0 else _config.session.max_rounds
            if parallel_agents > 1:
                from vulnclaw.agent.parallel_agents import run_parallel_pentest

                def agent_factory():
                    return agent.__class__(_config, getattr(agent, "mcp_manager", None))

                return await run_parallel_pentest(
                    agent,
                    agent_factory=agent_factory,
                    user_input=task_prompt,
                    target=scan_target,
                    discovery_rounds=rounds,
                    worker_rounds=worker_rounds,
                    max_agents=parallel_agents,
                    max_depth=parallel_depth,
                    surface_limit=surface_limit,
                    stream_sink=sink,
                )
            return await agent.auto_pentest(
                task_prompt,
                target=scan_target,
                max_rounds=rounds,
                stream_sink=sink,
            )

        await _run_cli_orchestrated_task(
            command="network-scan",
            target=scan_target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )

    asyncio.run(_run())


@app.command()
def exploit(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    cve: Optional[str] = typer.Option(None, help="CVE específico a explotar"),
    cmd: str = typer.Option("id", help="Comando a ejecutar para verificación"),
    # [Añadido] 2026-06-10 Nyaecho - TUI impulsado por lenguaje natural: permite
    #   pasar un prompt personalizado vía --prompt que sobrescribe el prompt generado automáticamente
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Prompt personalizado en lenguaje natural (sobrescribe el prompt generado automáticamente)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restringe las pruebas a un solo puerto"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restringe las pruebas a un solo host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restringe las pruebas a una sola ruta"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Host explícitamente bloqueado"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Ruta explícitamente bloqueada"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Acciones permitidas separadas por comas"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Acciones bloqueadas separadas por comas"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el estado previo del objetivo"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Reanuda desde un id de snapshot de objetivo específico"
    ),
    run_name: Optional[str] = typer.Option(
        None, "--run-name", help="Nombre explícito para un nuevo directorio de ejecución"
    ),
    resume_run: Optional[str] = typer.Option(
        None, "--resume-run", help="Reanuda una ejecución exacta por nombre de ejecución"
    ),
    runs_dir: Optional[str] = typer.Option(None, "--runs-dir", help="Raíz del directorio de ejecuciones"),
    additional_targets: Optional[list[str]] = typer.Option(
        None, "--target", help="Objetivo adicional para incluir en esta ejecución"
    ),
    target_type: Optional[str] = typer.Option(None, "--target-type", help="Sobrescribe el tipo de objetivo"),
    mount: bool = typer.Option(False, "--mount", help="Usa el modo de ingreso mount"),
    repair: bool = typer.Option(False, "--repair", help="Repara una ejecución corrupta"),
    force_fresh: bool = typer.Option(False, "--force-fresh", help="Inicia una ejecución nueva"),
    no_import: bool = typer.Option(False, "--no-import", help="No importa el estado heredado"),
) -> None:
    """Ejecuta solo la explotación."""
    cve_hint = f" using {cve}" if cve else ""
    task_prompt = prompt if prompt else (
        f"Attempt authorized exploitation against {target}{cve_hint} and verify with command: {cmd}"
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("exploit", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            # TerminalStreamSink ya se muestra en streaming en tiempo real; no se repite console.print
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="exploit",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
            **_run_context_kwargs(
                run_name=run_name,
                resume_run_name=resume_run,
                runs_dir=runs_dir,
                additional_targets=additional_targets,
                target_type=target_type,
                mount=mount,
                repair=repair,
                force_fresh=force_fresh,
                no_import=no_import,
            ),
        )

    asyncio.run(_run())


@app.command()
def report(
    session: str = typer.Argument(
        ..., help="Ruta al archivo JSON de la sesión, o el objetivo si se usa con --target"
    ),
    target_mode: bool = typer.Option(
        False, "--target", help="Interpreta el argumento como objetivo y genera el informe desde el estado del objetivo"
    ),
    pdf: bool = typer.Option(
        False, "--pdf", help="También exporta el informe a PDF (requiere el extra vulnclaw[pdf])"
    ),
    pdf_out: str = typer.Option(
        "", "--pdf-out", help="Ruta de salida del PDF (por defecto: la ruta del informe con sufijo .pdf)"
    ),
) -> None:
    """Genera un informe a partir de un archivo de sesión o del estado del objetivo."""
    if target_mode:
        from vulnclaw.report.generator import generate_report_from_target_state

        state = load_target_state(session)
        if not state:
            err_console.print(f"[!] Estado del objetivo no encontrado: {session}")
            raise typer.Exit(1)
        report_path = generate_report_from_target_state(state)
    else:
        from vulnclaw.report.generator import generate_report_from_file

        report_path = generate_report_from_file(session)
    console.print(f"[+] Informe generado: {report_path}")

    if pdf:
        from pathlib import Path

        from vulnclaw.report.pdf_exporter import export_pdf

        out = Path(pdf_out) if pdf_out else Path(report_path).with_suffix(".pdf")
        try:
            markdown = Path(report_path).read_text(encoding="utf-8")
            export_pdf(markdown, out, title="Informe VulnClaw")
        except RuntimeError as exc:
            err_console.print(f"[!] {exc}")
            raise typer.Exit(1) from exc
        console.print(f"[+] PDF exportado: {out}")


def _print_cli_manual(topic: Optional[str], output_format: str) -> None:
    """Imprime el manual de la CLI incluido, normalizando los errores de cara al usuario."""
    try:
        console.out(render_manual(output_format, topic), end="")
    except ValueError as exc:
        err_console.print(f"[!] {exc}")
        err_console.print(f"    Temas disponibles: {', '.join(available_topics())}")
        raise typer.Exit(1) from exc


@app.command("manual")
def manual_command(
    topic: Optional[str] = typer.Argument(
        None, help="Tema opcional del manual, p. ej. run, solve, network-scan, config"
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Formato de salida: text, markdown, man",
    ),
) -> None:
    """Imprime el manual completo de la CLI de VulnClaw."""
    _print_cli_manual(topic, output_format)


@app.command("man")
def man_command(
    topic: Optional[str] = typer.Argument(
        None, help="Tema opcional del manual, p. ej. run, solve, network-scan, config"
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Formato de salida: text, markdown, man",
    ),
) -> None:
    """Alias de 'vulnclaw manual'."""
    _print_cli_manual(topic, output_format)


# ── Config sub-command group ───────────────────────────────────────

config_app = typer.Typer(help="Gestionar la configuración")
app.add_typer(config_app, name="config")


@config_app.callback(invoke_without_command=True)
def config_root(ctx: typer.Context) -> None:
    """Abre el editor de configuración interactivo cuando no se indica un subcomando."""
    if ctx.resilient_parsing or ctx.invoked_subcommand is not None:
        return
    from vulnclaw.cli.tui import run_config_tui

    run_config_tui()


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Clave de configuración en notación de puntos, p. ej. llm.api_key"),
    value: str = typer.Argument(..., help="Valor de configuración"),
) -> None:
    """Establece un valor de configuración."""
    set_config_value(key, value)
    console.print(
        f"[+] Set {key} = {'***' if 'key' in key.lower() or 'pass' in key.lower() else value}"
    )


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Clave de configuración en notación de puntos"),
) -> None:
    """Obtiene un valor de configuración."""
    config = load_config()
    parts = key.split(".")
    obj = config
    for part in parts:
        obj = getattr(obj, part)
    value = obj if not hasattr(obj, "model_dump") else obj.model_dump()
    if isinstance(value, str) and ("key" in key.lower() or "pass" in key.lower()):
        value = value[:8] + "..." if len(value) > 8 else "***"
    console.print(f"{key} = {value}")


@config_app.command("list")
def config_list() -> None:
    """Lista todos los valores de configuración."""
    import yaml as _yaml

    config = load_config()
    raw = config.model_dump(mode="json")
    console.print(_yaml.dump(raw, default_flow_style=False, allow_unicode=True))


@config_app.command("provider")
def config_provider(
    name: Optional[str] = typer.Argument(
        None, help="Nombre del proveedor al que cambiar (p. ej. minimax, deepseek)"
    ),
    list_all: bool = typer.Option(False, "--list", "-l", help="Lista todos los proveedores disponibles"),
) -> None:
    """Muestra o cambia el proveedor LLM configurado."""
    if list_all or name is None:
        providers = list_providers()
        current_config = load_config()
        current_provider = current_config.llm.provider

        console.print("[bold]Proveedores LLM disponibles[/]")
        console.print()
        for p in providers:
            is_current = p["provider"] == current_provider
            marker = " [green](current)[/]" if is_current else ""
            console.print(f"  [bold cyan]{p['provider']}[/]{marker}")
            console.print(f"    Etiqueta: {p['label']}")
            console.print(f"    URL:  [dim]{p['base_url']}[/]")
            console.print(f"    Modelo: [dim]{p['default_model']}[/]")
            console.print()
        console.print("[dim]Usa vulnclaw config provider <nombre> para cambiar de proveedor.[/]")
        return

    # Switch provider
    from vulnclaw.config.schema import PROVIDER_PRESETS, LLMProvider

    # Validate provider name
    try:
        provider_enum = LLMProvider(name.lower())
    except ValueError:
        console.print(f"[!] Proveedor desconocido: [bold]{name}[/]")
        console.print(f"    Disponibles: {', '.join(p.value for p in LLMProvider)}")
        console.print("    Consejo: usa [bold]custom[/] para un base_url y modelo manuales.")
        raise typer.Exit(1)

    config = load_config()
    config = apply_provider_preset(config, name.lower())
    save_config(config)

    preset = PROVIDER_PRESETS.get(provider_enum, {})
    label = preset.get("label", name)
    console.print(f"[+] Proveedor LLM cambiado a [bold cyan]{label}[/]")
    console.print(f"    URL base: [dim]{config.llm.base_url}[/]")
    console.print(f"    Modelo:   [dim]{config.llm.model}[/]")

    if not has_llm_credentials(config.llm):
        console.print()
        console.print(
            "[yellow]Configura primero las credenciales: [bold]vulnclaw config set llm.api_key <tu-clave>[/] "
            "o configura autenticación sin clave (llm.auth_mode = env/file/command/wif)[/]"
        )


# ── Init command ────────────────────────────────────────────────────


@app.command()
def init() -> None:
    """Inicializa la configuración de VulnClaw."""
    from vulnclaw.config.settings import ensure_dirs

    ensure_dirs()

    config = load_config()
    save_config(config)
    console.print(_("cli.init.config_created"))
    console.print(_("cli.init.dirs_initialized"))
    console.print(_("cli.init.dir_sessions"))
    console.print(_("cli.init.dir_kb"))
    console.print(_("cli.init.dir_skills"))
    console.print()
    console.print(_("cli.init.next_steps"))
    console.print(_("cli.init.step_provider"))
    console.print(_("cli.init.step_api_key"))
    console.print(_("cli.init.step_cli"))
    console.print(_("cli.init.step_tui"))


# ── Login / Logout commands ─────────────────────────────────


@app.command()
def login(
    proxy_url: Optional[str] = typer.Option(
        None,
        "--proxy-url",
        help="base_url de un proxy externo compatible con OpenAI (desactiva el integrado)",
    ),
    no_browser: bool = typer.Option(
        False, "--no-browser", help="Imprime la URL en lugar de abrir un navegador"
    ),
    set_default: bool = typer.Option(
        True, "--set-default/--no-set-default", help="Establece llm.auth_mode=oauth si tiene éxito"
    ),
) -> None:
    """Inicia sesión con tu suscripción de ChatGPT (Codex "Sign in with ChatGPT").

    Abre la página de consentimiento de ChatGPT en tu navegador, almacena el
    token renovable resultante y habilita el proxy integrado que conecta
    chat.completions con el backend de ChatGPT — así VulnClaw simplemente funciona después.

    ⚠️ Esto reutiliza el cliente OAuth de Codex de OpenAI (first-party). Usar una
    suscripción de ChatGPT a través de un cliente no oficial puede violar los
    Términos de Servicio de OpenAI y tu cuenta podría ser restringida.
    Procedes bajo tu propio riesgo.
    """
    from vulnclaw.config.token_provider import (
        CHATGPT_CLIENT_ID,
        CHATGPT_TOKEN_URL,
        OAuthError,
        perform_chatgpt_login,
    )

    llm = load_config().llm

    err_console.print(
        "[yellow][!] Iniciar sesión con ChatGPT reutiliza el cliente OAuth de Codex "
        "de OpenAI (first-party). Usar una suscripción de ChatGPT a través de un "
        "cliente no oficial puede violar los Términos de Servicio de OpenAI y tu "
        "cuenta podría ser restringida. Procedes bajo tu propio riesgo.[/]"
    )
    try:
        bundle = perform_chatgpt_login(open_browser=not no_browser)
    except OAuthError as exc:
        err_console.print(f"[!] Error al iniciar sesión con ChatGPT: {exc}")
        raise typer.Exit(1)

    # Wire config so resolve/refresh works against the Codex token endpoint.
    set_config_value("llm.oauth_token_url", CHATGPT_TOKEN_URL)
    set_config_value("llm.oauth_client_id", CHATGPT_CLIENT_ID)
    if set_default:
        set_config_value("llm.auth_mode", "oauth")
    # The ChatGPT backend serves its own model family — gpt-4o won't work.
    if (llm.model or "").lower() in ("", "gpt-4o", "gpt-5", "gpt-5-codex"):
        set_config_value("llm.model", "gpt-5.5")

    if proxy_url:
        # User supplied an external proxy: use it, disable the built-in one.
        set_config_value("llm.base_url", proxy_url.rstrip("/"))
        set_config_value("llm.chatgpt_auto_proxy", "false")
    else:
        # Default: built-in proxy auto-starts on demand — zero setup.
        set_config_value("llm.chatgpt_auto_proxy", "true")

    tok = bundle.get("access_token", "")
    masked = (tok[:6] + "…" + tok[-4:]) if len(tok) > 12 else "(recibido)"
    console.print("[green]Sesión iniciada con ChatGPT.[/]")
    console.print(f"  Token de acceso: [dim]{masked}[/]  (se renueva automáticamente)")
    if bundle.get("account_id"):
        console.print(f"  ID de cuenta: [dim]{bundle['account_id']}[/]")
    console.print()
    if proxy_url:
        console.print(f"  base_url configurado al proxy externo: [dim]{proxy_url.rstrip('/')}[/]")
    else:
        console.print(
            "  [green]Proxy integrado de ChatGPT habilitado — se inicia automáticamente.[/]\n"
            "  [dim]No se necesita un proxy externo. El puente hacia el backend de ChatGPT "
            "de OpenAI es experimental; si una llamada falla, el error muestra la respuesta "
            "del backend para que puedas ajustar llm.model o las variables de entorno VULNCLAW_CHATGPT_*.[/]"
        )
    console.print("  Ejecuta [bold]vulnclaw[/] para comenzar.")


@app.command()
def logout() -> None:
    """Elimina los tokens OAuth almacenados (inicio de sesión por navegador)."""
    from vulnclaw.config.token_provider import logout_oauth

    if logout_oauth():
        console.print("[green]Sesión cerrada — se eliminaron los tokens OAuth almacenados.[/]")
    else:
        console.print("[yellow]No hay tokens OAuth almacenados para eliminar.[/]")


# ── Doctor command ──────────────────────────────────────────────────


@app.command()
def doctor() -> None:
    """Inspecciona el entorno de ejecución de VulnClaw."""
    import shutil

    # Modificado por: Nyaecho
    # Fecha de modificación: 2026-07-08
    # Motivo de la modificación: corrección V6 — se importa desde mcp/diagnostics,
    #   eliminando la dependencia CLI→Web.
    from vulnclaw.mcp.diagnostics import get_mcp_diagnostics

    console.print("[bold]Verificación del entorno de VulnClaw[/]")
    console.print()

    # Check Python
    console.print(f"  Python: [green]{sys.version.split()[0]}[/]")

    # Check Node.js
    node_path = shutil.which("node")
    if node_path:
        import subprocess

        try:
            result = subprocess.run(
                [node_path, "--version"], capture_output=True, text=True, timeout=5
            )
            console.print(f"  Node.js: [green]{result.stdout.strip()}[/]")
        except Exception:
            console.print("  Node.js: [yellow]verificación fallida[/]")
    else:
        console.print("  Node.js: [red]no instalado[/] (requerido para algunos servicios MCP)")

    # Check npx
    npx_path = shutil.which("npx")
    console.print(
        f"  npx: [{'green' if npx_path else 'red'}]{'instalado' if npx_path else 'faltante'}[/]"
    )

    # Check uvx
    uvx_path = shutil.which("uvx")
    console.print(
        f"  uvx: [{'green' if uvx_path else 'yellow'}]{'instalado' if uvx_path else 'faltante'}[/]"
    )

    # Check nmap
    nmap_path = shutil.which("nmap")
    console.print(
        f"  nmap: [{'green' if nmap_path else 'yellow'}]{'instalado' if nmap_path else 'opcional/faltante'}[/]"
    )

    # Check config
    config = load_config()
    console.print()
    console.print("[bold]Configuración LLM[/]:")
    has_key = has_llm_credentials(config.llm)
    auth_mode = (config.llm.auth_mode or "static").lower()
    console.print(f"  Proveedor: [bold cyan]{config.llm.provider}[/]")
    console.print(f"  Modo de autenticación: [bold]{auth_mode}[/]")
    cred_label = "configurado" if has_key else "no configurado"
    console.print(
        f"  Credenciales: [{'green' if has_key else 'red'}]{cred_label}[/]"
    )
    console.print(f"  URL base: [dim]{config.llm.base_url}[/]")
    console.print(f"  Modelo: [dim]{config.llm.model}[/]")

    # Check MCP servers
    console.print()
    console.print("[bold]Servicios MCP[/]:")
    mcp_diag = get_mcp_diagnostics()
    console.print(f"  Registrados: [bold]{mcp_diag.total_services}[/] servicios")
    console.print(f"  Herramientas: [bold]{mcp_diag.tool_count}[/] expuestas")

    for item in mcp_diag.services:
        status = "[green]habilitado[/]" if item.enabled else "[dim]deshabilitado[/]"
        priority_label = {0: "P0", 1: "P1", 2: "P2"}.get(item.priority, "??")
        running = "[green]en ejecución[/]" if item.running else "[yellow]registrado[/]"
        capability = "[green]exec[/]" if item.can_execute else "[yellow]solo esquema[/]"
        console.print(
            f"  {item.name}: {status} [{priority_label}] {running} mode={item.execution_mode} {capability} tools={item.tool_count}"
        )
        if item.error:
            label = item.last_error_type or "error"
            console.print(f"    [red]{label}[/]: {item.error}")

    console.print(
        "[dim]doctor muestra el estado de registro de MCP y las herramientas expuestas. fetch/memory se ejecutan en modo local; la mayoría de los demás servicios siguen siendo marcadores de posición.[/]"
    )
    console.print(
        "[yellow]python_execute es una capacidad experimental de alto riesgo. No es un sandbox robusto; úsala solo en entornos autorizados o controlados.[/]"
    )
    console.print(
        "[dim]El flujo de actualización de la base de conocimiento está activo; las mejoras de recuperación pueden continuar de forma independiente.[/]"
    )

    console.print()
    if has_key:
        console.print("[green]Entorno listo. Ejecuta [bold]vulnclaw[/] para comenzar.[/]")
    else:
        console.print(
            "[yellow]Configura primero las credenciales: [bold]vulnclaw config set llm.api_key <clave>[/] "
            "o autenticación sin clave (llm.auth_mode = env/file/command/wif)[/]"
        )


# ── KB command ──────────────────────────────────────────────────────

kb_app = typer.Typer(help="Comandos de la base de conocimiento de seguridad")
app.add_typer(kb_app, name="kb")

target_state_app = typer.Typer(help="Gestiona el historial de estado del objetivo")
app.add_typer(target_state_app, name="target-state")

plugins_app = typer.Typer(help="Inspecciona y ejecuta plugins de detección de vulnerabilidades")
app.add_typer(plugins_app, name="plugins")


def _parse_kv_options(pairs: Optional[list[str]]) -> dict[str, object]:
    """Convierte --option key=value (repetible) en un dict; el value se intenta parsear como JSON primero."""
    import json as _json

    options: dict[str, object] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise typer.BadParameter(f"Se esperaba key=value, se obtuvo: {pair}")
        key, _, raw = pair.partition("=")
        key = key.strip()
        raw = raw.strip()
        try:
            options[key] = _json.loads(raw)
        except (ValueError, TypeError):
            options[key] = raw
    return options


@plugins_app.command("list")
def plugins_list(
    stage: Optional[str] = typer.Option(None, "--stage", help="Filtra por etapa"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filtra por etiqueta"),
) -> None:
    """Lista los plugins de detección registrados."""
    from rich.table import Table

    from vulnclaw.plugins import registry

    plugin_classes = registry.list()
    if stage:
        try:
            plugin_classes = registry.by_stage(stage)
        except ValueError:
            err_console.print(f"[!] Etapa desconocida: {stage}")
            raise typer.Exit(1) from None
    if tag:
        tag_set = {p.plugin_id for p in registry.by_tag(tag)}
        plugin_classes = [p for p in plugin_classes if p.plugin_id in tag_set]

    if not plugin_classes:
        console.print("[yellow]Ningún plugin coincide con el filtro.[/yellow]")
        return

    table = Table(title="Plugins de VulnClaw", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Nombre")
    table.add_column("Etapas")
    table.add_column("Riesgo")
    table.add_column("Destructivo", justify="center")
    for plugin_cls in sorted(plugin_classes, key=lambda p: p.plugin_id):
        meta = plugin_cls.metadata()
        table.add_row(
            meta["plugin_id"],
            meta["name"],
            ", ".join(meta["stages"]),
            meta["default_risk"],
            "⚠️" if meta["destructive"] else "-",
        )
    console.print(table)


@plugins_app.command("info")
def plugins_info(plugin_id: str = typer.Argument(..., help="Id del plugin")) -> None:
    """Muestra los metadatos completos de un plugin."""
    import json as _json

    from vulnclaw.plugins import registry

    plugin_cls = registry.get(plugin_id)
    if plugin_cls is None:
        err_console.print(f"[!] Plugin no encontrado: {plugin_id}")
        raise typer.Exit(1)
    console.print_json(_json.dumps(plugin_cls.metadata(), ensure_ascii=False))


@plugins_app.command("run")
def plugins_run(
    plugin_id: str = typer.Argument(..., help="Id del plugin a ejecutar"),
    target: str = typer.Option("", "--target", help="Host/IP/URL objetivo"),
    stage: str = typer.Option("discovery", "--stage", help="Etapa del plugin"),
    option: Optional[list[str]] = typer.Option(
        None, "--option", "-o", help="Opción del plugin key=value (repetible; el valor se interpreta como JSON)"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", help="Archivo JSON combinado con las opciones del plugin"
    ),
    allow_destructive: bool = typer.Option(
        False, "--allow-destructive", help="Permite plugins destructivos"
    ),
    session_file: Optional[str] = typer.Option(
        None, "--session", help="Combina los hallazgos en este JSON de SessionState y lo guarda"
    ),
    as_json: bool = typer.Option(False, "--json", help="Imprime el PluginResult sin procesar como JSON"),
) -> None:
    """Ejecuta un plugin sobre los datos proporcionados (los plugins integrados solo analizan la entrada dada)."""
    import json as _json
    from pathlib import Path

    from rich.table import Table

    from vulnclaw.plugins import PluginContext, PluginStage, create_builtin_runtime
    from vulnclaw.plugins.integration import merge_plugin_results_into_session

    try:
        stage_value = PluginStage(stage)
    except ValueError:
        err_console.print(f"[!] Etapa desconocida: {stage}")
        raise typer.Exit(1) from None

    options = _parse_kv_options(option)
    if input_file:
        path = Path(input_file)
        if not path.exists():
            err_console.print(f"[!] Archivo de entrada no encontrado: {input_file}")
            raise typer.Exit(1)
        try:
            payload = _json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            err_console.print(f"[!] Error al leer el archivo de entrada: {exc}")
            raise typer.Exit(1) from None
        if isinstance(payload, dict):
            options.update(payload)
        else:
            options["input"] = payload

    config = load_config()
    runtime = create_builtin_runtime(config)
    context = PluginContext(
        target=target,
        stage=stage_value,
        options=options,
        allow_destructive=allow_destructive,
    )

    result = asyncio.run(runtime.execute(plugin_id, context))

    if as_json:
        console.print_json(result.model_dump_json())
    else:
        if result.skipped:
            console.print(f"[yellow]⊘ Omitido[/yellow] ({result.error_type}): {result.error}")
        elif result.error:
            console.print(f"[red]✗ Error[/red] ({result.error_type}): {result.error}")
        for message in result.messages:
            console.print(f"  [dim]{message}[/dim]")
        if result.findings:
            table = Table(title=f"Hallazgos de {plugin_id}", show_lines=True)
            table.add_column("Riesgo", style="magenta", no_wrap=True)
            table.add_column("Título")
            table.add_column("Tipo")
            table.add_column("Confianza", justify="right")
            for finding in result.findings:
                table.add_row(
                    finding.risk.value,
                    finding.title,
                    finding.vuln_type or "-",
                    f"{finding.confidence:.2f}",
                )
            console.print(table)
        elif not result.error:
            console.print("[green]✓[/green] El plugin se ejecutó; sin hallazgos.")

    if session_file:
        session_path = Path(session_file)
        from vulnclaw.agent.context import SessionState

        session = SessionState.load(session_path) if session_path.exists() else SessionState()
        added = merge_plugin_results_into_session(session, result)
        session.save(session_path)
        console.print(f"[+] Se combinaron {added} hallazgo(s) en {session_file}")


@kb_app.command("update")
def kb_update() -> None:
    """Actualiza la base de conocimiento."""
    console.print("[*] Actualizando la base de conocimiento...")
    from vulnclaw.kb.store import KnowledgeStore
    from vulnclaw.kb.updater import seed_knowledge_base

    store = KnowledgeStore()
    before_stats = store.get_stats()
    seed_knowledge_base(store)
    after_stats = store.get_stats()

    before_total = sum(before_stats.values())
    after_total = sum(after_stats.values())
    delta = after_total - before_total
    category_summary = ", ".join(f"{cat}={count}" for cat, count in sorted(after_stats.items()))

    console.print(f"[+] Base de conocimiento actualizada: +{delta} entradas")
    console.print(f"    Categorías: {category_summary or 'vacío'}")


@kb_app.command("status")
def kb_status() -> None:
    """Muestra el estado del backend de recuperación de la base de conocimiento."""
    from vulnclaw.kb.retriever import KnowledgeRetriever, RetrieverStatus
    from vulnclaw.kb.store import KnowledgeStore

    store = KnowledgeStore()
    retriever = KnowledgeRetriever(store=store)
    status = retriever.get_status()
    detail = retriever.get_status_detail()
    stats = store.get_stats()
    total = sum(stats.values())
    category_summary = ", ".join(f"{cat}={count}" for cat, count in sorted(stats.items()))

    if status == RetrieverStatus.CHROMADB_ACTIVE:
        line = "[green]✓ Base de conocimiento habilitada (búsqueda semántica ChromaDB)[/green]"
    elif status == RetrieverStatus.KEYWORD_FALLBACK:
        line = "[yellow]⚠ Base de conocimiento degradada a modo por palabras clave (chromadb no instalado)[/yellow]"
    else:
        line = "[red]✗ Base de conocimiento deshabilitada (sin datos disponibles)[/red]"

    console.print(
        Panel(
            f"{line}\n"
            f"Backend: [bold]{status.value}[/]\n"
            f"Detalle: {detail or 'n/d'}\n"
            f"Entradas: [bold]{total}[/] ({category_summary or 'vacío'})\n"
            f"Búsqueda semántica: ejecuta [bold]pip install vulnclaw\\[kb][/] para habilitar ChromaDB",
            title="Estado de la KB",
            border_style="cyan",
        )
    )


@target_state_app.command("list")
def target_state_list(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
) -> None:
    """Lista los snapshots del objetivo."""
    snapshots = list_target_snapshots(target)
    if not snapshots:
        console.print(f"[-] No se encontraron snapshots para: {target}")
        raise typer.Exit(1)

    console.print(f"[bold]Snapshots del objetivo[/]: {target}")
    for item in snapshots[:20]:
        console.print(
            f"  {item['snapshot_id']} | v{item.get('schema_version', 1)} | {item['last_command']} | "
            f"steps={item['executed_steps']} verified={item['verified_findings']} pending={item['pending_findings']}"
        )


@target_state_app.command("preview")
def target_state_preview_cmd(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    snapshot_id: Optional[str] = typer.Option(
        None, "--snapshot", help="Vista previa de un snapshot específico"
    ),
) -> None:
    """Muestra una vista previa de reanudación del estado del objetivo."""
    preview = get_target_state_preview(target, snapshot_id=snapshot_id)
    if not preview:
        console.print(f"[-] No se encontró estado del objetivo: {target}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Objetivo: [bold]{preview['target']}[/]\n"
            f"Esquema: [bold]v{preview['schema_version']}[/]\n"
            f"Fase: [bold]{preview['phase'] or 'desconocida'}[/]\n"
            f"Estrategia de reanudación: [bold]{preview['resume_strategy'] or 'ninguna'}[/]\n"
            f"Motivo: {preview['resume_reason'] or 'n/d'}\n"
            f"Hallazgos: {preview['verified_count']} verificados / {preview['pending_count']} pendientes / {preview['findings_count']} total",
            title="Vista previa del objetivo",
            border_style="cyan",
        )
    )

    if preview.get("priority_targets"):
        console.print("[bold]Objetivos prioritarios[/]:")
        for item in preview["priority_targets"][:5]:
            console.print(f"  - {item}")
    if preview.get("priority_recon_assets"):
        console.print("[bold]Activos de reconocimiento prioritarios[/]:")
        for item in preview["priority_recon_assets"][:5]:
            console.print(f"  - {item}")
    if preview.get("next_actions"):
        console.print("[bold]Próximas acciones[/]:")
        for item in preview["next_actions"][:5]:
            console.print(f"  - {item}")


@target_state_app.command("diff")
def target_state_diff_cmd(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    from_snapshot_id: str = typer.Argument(..., help="Id del snapshot base"),
    to_snapshot_id: Optional[str] = typer.Option(
        None, "--to", help="Compara con otro snapshot o con el estado actual"
    ),
) -> None:
    """Muestra las diferencias entre dos snapshots del estado del objetivo."""
    diff = diff_target_state_snapshots(target, from_snapshot_id, to_snapshot_id=to_snapshot_id)
    if not diff:
        console.print(f"[-] No se pudo comparar el estado del objetivo: {target}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Objetivo: [bold]{diff['target']}[/]\n"
            f"Desde: [bold]{diff['from_snapshot_id']}[/] -> Hasta: [bold]{diff['to_snapshot_id']}[/]\n"
            f"Esquema: v{diff['schema_version_from']} -> v{diff['schema_version_to']}\n"
            f"Estrategia de reanudación: {diff['resume_strategy_from'] or 'ninguna'} -> {diff['resume_strategy_to'] or 'ninguna'}",
            title="Diferencias del objetivo",
            border_style="magenta",
        )
    )

    for title, items in (
        ("Hallazgos agregados", diff.get("added_findings", [])),
        ("Hallazgos eliminados", diff.get("removed_findings", [])),
        ("Hallazgos actualizados", diff.get("updated_findings", [])),
        ("Activos de reconocimiento agregados", diff.get("added_recon_assets", [])),
        ("Activos de reconocimiento eliminados", diff.get("removed_recon_assets", [])),
        ("Pasos agregados", diff.get("added_steps", [])),
        ("Pasos eliminados", diff.get("removed_steps", [])),
        ("Notas agregadas", diff.get("added_notes", [])),
        ("Notas eliminadas", diff.get("removed_notes", [])),
    ):
        if items:
            console.print(f"[bold]{title}[/]:")
            for item in items[:10]:
                console.print(f"  - {item}")


@target_state_app.command("rollback")
def target_state_rollback_cmd(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
    snapshot_id: str = typer.Argument(..., help="Id del snapshot a restaurar"),
) -> None:
    """Revierte el estado del objetivo a un snapshot."""
    path = rollback_target_state(target, snapshot_id)
    if not path:
        console.print(f"[-] Snapshot no encontrado: {snapshot_id}")
        raise typer.Exit(1)
    console.print(f"[+] Estado del objetivo revertido: {target}")
    console.print(f"    Snapshot: {snapshot_id}")


@target_state_app.command("clear")
def target_state_clear_cmd(
    target: str = typer.Argument(..., help="Host/IP/URL objetivo"),
) -> None:
    """Borra el estado del objetivo."""
    ok = clear_target_state(target)
    if not ok:
        console.print(f"[-] No se encontró estado del objetivo: {target}")
        raise typer.Exit(1)
    console.print(f"[+] Estado del objetivo borrado: {target}")


# Default command (no sub-command -> REPL)

# ── Auto-pentest detection ──────────────────────────────────────────


def _should_auto_pentest(user_input: str, current_target: Optional[str]) -> bool:
    """Determine if user input should trigger autonomous pentest loop.

    Triggers when:
    - User explicitly asks for a full pentest with a target
    - User mentions a target plus action keywords like "prueba de penetración" or "atácalo"
    - User asks to solve a CTF / find a flag with a target
    - User asks for information gathering / recon / OSINT with a target
    - A target is present + multi-step intent indicators
    """
    input_lower = user_input.lower()

    # Explicit auto-mode triggers
    auto_keywords = [
        "prueba de penetración",
        "realizar penetración",
        "hacer pentest",
        "atácalo",
        "prueba completa",
        "pentest",
        "full test",
        "auto",
        "modo pentest autónomo",
        "modo autónomo",
        "encontrar flag",
        "buscar flag",
        "conseguir flag",
        "get flag",
        "find flag",
        "resolver reto",
        "resolver desafío",
        "reto",
        "challenge",
        "ctf",
        "contraseña débil",
        "fuerza bruta",
        "eludir",
        "bypass",
        "brute",
        "recopilar",
        "recolectar",
        "recopilación de información",
        "reconocimiento",
        "recon",
        "reconnaissance",
        "ingeniería social",
        "osint",
        "inteligencia",
        "intelligence",
        "analizar objetivo",
        "análisis de objetivo",
        "descubrimiento de activos",
        "escaneo de directorios",
        "sondeo",
        "explorar",
        "investigar",
        "investigate",
        "enumerate",
        "análisis completo",
        "análisis profundo",
        "análisis detallado",
        "escaneo completo",
        "subdominio",
        "subdomain",
    ]

    # Single-step queries should NOT trigger auto mode
    single_step_keywords = [
        "generar reporte",
        "report",
        "help",
        "ayuda",
    ]

    # If it's clearly a single-step query, don't auto-loop
    # But if it also has auto keywords, still go auto (e.g. "recopilar información y generar reporte")
    if any(kw in input_lower for kw in single_step_keywords) and not any(
        kw in input_lower for kw in auto_keywords
    ):
        return False

    # If it has auto-mode keywords, trigger auto loop
    if any(kw in input_lower for kw in auto_keywords):
        # Must have a target (either in input or already set)
        has_target = bool(current_target) or bool(_extract_target_from_input(user_input))
        return has_target

    # Fallback: has target + multi-step intent -> auto
    has_target = bool(current_target) or bool(_extract_target_from_input(user_input))
    if has_target:
        multi_step_indicators = [
            "y además",
            "luego",
            "salida",
            "guardar",
            "escribir a",
            "exportar",
            "todos",
            "todo",
            "completo",
            "detallado",
        ]
        if any(ind in input_lower for ind in multi_step_indicators):
            return True

    return False


def _extract_target_from_input(user_input: str) -> Optional[str]:
    """Extract target from user input string."""
    import re

    # Try to find URL (with optional port)
    url_match = re.search(r"(https?://[a-zA-Z0-9][-a-zA-Z0-9.:]*)", user_input)
    if url_match:
        return url_match.group(1).rstrip("/")
    # Try to find IP address
    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", user_input)
    if ip_match:
        return ip_match.group(1)
    # Try to find domain
    domain_match = re.search(r"([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)", user_input)
    if domain_match:
        return domain_match.group(1)
    return None


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Muestra la versión y termina.",
        is_eager=True,
    ),
    show_manual: bool = typer.Option(
        False,
        "--man",
        "--manual",
        help="Muestra el manual completo de la CLI y termina.",
        is_eager=True,
    ),
    resume_run_name: Optional[str] = typer.Option(
        None,
        "--resume",
        help="Reanuda una ejecución guardada exacta por nombre de ejecución.",
    ),
    runs_dir: Optional[str] = typer.Option(
        None,
        "--runs-dir",
        help="Raíz del directorio de ejecuciones para --resume.",
    ),
    repair: bool = typer.Option(
        False,
        "--repair",
        help="Repara una ejecución corrupta revirtiendo al último snapshot válido.",
    ),
) -> None:
    """Abre la CLI/REPL clásica por defecto."""
    if version:
        console.print(__version__)
        raise typer.Exit()
    if show_manual:
        _print_cli_manual(None, "text")
        raise typer.Exit()
    if ctx.invoked_subcommand is None and resume_run_name:
        _resume_saved_run(resume_run_name, runs_dir=runs_dir, repair=repair)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _run_repl()


def _resume_saved_run(
    run_name: str,
    *,
    runs_dir: Optional[str] = None,
    repair: bool = False,
) -> None:
    from vulnclaw.run_context import RunCorruptError, load_run_context

    config = load_config()
    try:
        run_context = load_run_context(
            run_name,
            runs_dir=runs_dir,
            config=config,
            repair=repair,
        )
    except RunCorruptError as exc:
        err_console.print(f"[!] {exc}")
        raise typer.Exit(1) from exc

    targets = run_context.manifest.get("targets", [])
    first_target = targets[0] if isinstance(targets, list) and targets else {}
    if not isinstance(first_target, dict) or not first_target.get("input"):
        err_console.print(f"[!] La ejecución {run_name} no tiene un objetivo reanudable en run.json")
        raise typer.Exit(1)

    target = str(first_target["input"])
    command = str(run_context.manifest.get("command") or "run")
    if not has_llm_credentials(config.llm):
        err_console.print("[!] Configura primero las credenciales del LLM (api_key o auth_mode).")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, shared_config):
            sink = TerminalStreamSink(console, shared_config.session.show_thinking)
            prompt = (
                f"Continue the saved VulnClaw run {run_name} for {target}. "
                "Resume from the loaded checkpoint and continue the authorized task."
            )
            return await agent.chat(prompt, target=target, stream_sink=sink)

        return await _run_cli_orchestrated_task(
            command=command,
            target=target,
            resume=True,
            snapshot=None,
            runner=runner,
            resume_run_name=run_name,
            runs_dir=runs_dir,
            repair=repair,
        )

    asyncio.run(_run())


def _auto_save_recon_report(agent, user_input: str, config) -> None:
    """Auto-save a recon report after auto_pentest completes when user requested file output."""
    import re
    from datetime import datetime

    try:
        state = agent.session_state
        target = state.target or "desconocido"

        # Determine output path
        # Check if user specified a path
        path_match = re.search(
            r"(?:guardar en|escribir a|salida a|exportar a|save to|write to|output to|export to)\s*([^\s,]+)",
            user_input,
            re.IGNORECASE,
        )
        if path_match:
            output_path = path_match.group(1)
        else:
            safe_name = re.sub(r"[^\w]", "_", target)[:30]
            date_str = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = str(config.session.output_dir / f"{safe_name}_recon_{date_str}.md")

        from vulnclaw.report.generator import generate_report

        generate_report(
            state,
            output_path,
            report_format=config.session.report_format,
        )

        console.print(f"\n[+] Informe de reconocimiento guardado: {output_path}")

    except Exception as e:
        console.print(f"\n[!] Error al guardar automáticamente el informe: {e}")


@app.command()
def repl() -> None:
    """Inicia la REPL clásica de lenguaje natural."""
    _run_repl()


@app.command()
def tui(
    target: Optional[str] = typer.Option(
        None,
        "--target",
        "-t",
        help="Precarga el objetivo autorizado para la TUI.",
    ),
    mode: str = typer.Option(
        "standard",
        "--mode",
        "-m",
        help="Precarga el modo de verificación: quick, standard, deep, continuous.",
    ),
    only_port: Optional[int] = typer.Option(
        None,
        "--only-port",
        help="Precarga un único puerto de prueba permitido.",
    ),
    only_host: Optional[str] = typer.Option(
        None,
        "--only-host",
        help="Precarga un único host permitido.",
    ),
    only_path: Optional[str] = typer.Option(
        None,
        "--only-path",
        help="Precarga una única ruta permitida.",
    ),
    blocked_host: Optional[str] = typer.Option(
        None,
        "--blocked-host",
        help="Precarga un host explícitamente bloqueado.",
    ),
    blocked_path: Optional[str] = typer.Option(
        None,
        "--blocked-path",
        help="Precarga una ruta explícitamente bloqueada.",
    ),
    allow_actions: Optional[str] = typer.Option(
        None,
        "--allow-actions",
        help="Precarga acciones permitidas separadas por comas.",
    ),
    block_actions: Optional[str] = typer.Option(
        None,
        "--block-actions",
        help="Precarga acciones bloqueadas separadas por comas.",
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reanuda el historial del objetivo."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Muestra el resumen de lanzamiento y termina sin iniciar una tarea.",
    ),
    once: bool = typer.Option(
        False,
        "--once",
        help="Muestra el panel de la TUI una vez y termina (útil para pruebas rápidas).",
    ),
) -> None:
    """Abre el banco de trabajo de la interfaz de terminal (TUI)."""
    from vulnclaw.cli.tui import (
        MODES,
        build_state_from_options,
        build_task_draft,
        render_task_summary,
        run_tui,
    )

    if mode not in MODES:
        err_console.print("[!] Modo de TUI desconocido. Usa uno de: quick, standard, deep, continuous")
        raise typer.Exit(1)

    state = build_state_from_options(
        target=target or "",
        mode=mode,  # type: ignore[arg-type]
        only_host=only_host or "",
        only_port=only_port,
        only_path=only_path or "",
        blocked_host=blocked_host or "",
        blocked_path=blocked_path or "",
        allow_actions=allow_actions,
        block_actions=block_actions,
        resume=resume,
    )

    if dry_run:
        console.out(render_task_summary(build_task_draft(state)), end="")
        return

    if once and target:
        from vulnclaw.cli.tui import render_tui_home

        console.out(render_tui_home(state), end="")
        return

    run_tui(once=once, initial_state=state)


@app.command()
def web(
    host: str = typer.Option(
        "127.0.0.1", "--host", help="Host del servidor web (por defecto: solo localhost)"
    ),
    port: int = typer.Option(7788, "--port", help="Puerto del servidor web"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Valida e imprime la información de lanzamiento sin iniciar el servidor"
    ),
    allow_remote: bool = typer.Option(
        False, "--allow-remote", help="Permite explícitamente enlazar la Web UI a una dirección no local"
    ),
) -> None:
    """Ejecuta la Web UI local."""
    if not _is_loopback_bind_host(host):
        if not allow_remote:
            err_console.print(
                "[!] Se rechaza enlazar la Web UI a una dirección no local sin --allow-remote."
            )
            raise typer.Exit(1)
        console.print(
            "[yellow]Advertencia: mantén la Web UI enlazada a 127.0.0.1 a menos que sepas lo que haces.[/]"
        )

    from vulnclaw.web.app import FASTAPI_AVAILABLE

    console.print(
        Panel(
            f"Host: [bold]{host}[/]\n"
            f"Puerto: [bold]{port}[/]\n"
            f"FastAPI: [{'green' if FASTAPI_AVAILABLE else 'yellow'}]{'instalado' if FASTAPI_AVAILABLE else 'faltante'}[/]\n"
            f"URL: [bold]http://{host}:{port}[/]",
            title="Interfaz Web de VulnClaw",
            border_style="cyan",
        )
    )

    if dry_run:
        console.print("[green]Ejecución de prueba (dry-run) de la Web UI completada.[/]")
        return

    if not FASTAPI_AVAILABLE:
        err_console.print(
            "[!] Falta FastAPI. Instálalo con [bold]pip install vulnclaw[web][/]."
        )
        raise typer.Exit(1)

    try:
        import uvicorn
    except ImportError:
        err_console.print(
            "[!] Falta uvicorn. Instálalo con [bold]pip install vulnclaw[web][/]."
        )
        raise typer.Exit(1)

    from vulnclaw.web.app import create_app

    uvicorn.run(create_app(), host=host, port=port, log_level="info")


def _is_loopback_bind_host(host: str) -> bool:
    """Return True when a requested bind host is loopback-only."""
    normalized = host.strip().strip("[]").lower()
    if normalized in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        import ipaddress

        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


if __name__ == "__main__":
    app()
