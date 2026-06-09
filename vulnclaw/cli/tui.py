"""Rich-powered TUI helpers for the VulnClaw CLI."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Callable, Literal

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from vulnclaw.config.settings import apply_provider_preset, list_providers, load_config, save_config
from vulnclaw.i18n import _, init_i18n
from vulnclaw.target_state.store import get_target_state_preview, list_target_snapshots

# Initialize i18n with config
_config_holder = [None]


def _init_tui_i18n() -> None:
    """Initialize i18n for TUI with config language setting."""
    config = load_config()
    _config_holder[0] = config
    session_lang = getattr(config.session, "language", "auto") if config else "auto"
    init_i18n(lang=session_lang if session_lang != "auto" else None, config=config)


_init_tui_i18n()

CheckMode = Literal["quick", "standard", "deep", "continuous"]
TaskCommand = Literal["recon", "run", "scan", "persistent"]


@dataclass(frozen=True)
class TuiMode:
    key: CheckMode
    label: str
    command: TaskCommand
    description: str
    allow_actions: tuple[str, ...]
    block_actions: tuple[str, ...] = ()
    needs_extra_confirm: bool = False


@dataclass
class TuiState:
    target: str = ""
    mode: CheckMode = "standard"
    only_host: str = ""
    only_port: str = ""
    only_path: str = ""
    blocked_host: str = ""
    blocked_path: str = ""
    allow_actions: list[str] = field(default_factory=list)
    block_actions: list[str] = field(default_factory=list)
    resume: bool = True


@dataclass(frozen=True)
class TuiTargetOverview:
    """Small, safe-to-render summary of the selected target history."""

    target: str
    has_history: bool
    snapshot_count: int = 0
    phase: str = "unknown"
    findings_count: int = 0
    verified_count: int = 0
    pending_count: int = 0
    constraints_summary: str = "Not recorded"
    violations_count: int = 0
    last_command: str = ""
    error: str = ""


@dataclass(frozen=True)
class TuiRuntimeDiagnostic:
    """Runtime readiness summary shown inside the TUI."""

    python_version: str
    node_version: str = "missing"
    npx_status: str = "missing"
    uvx_status: str = "missing"
    nmap_status: str = "optional/missing"
    provider: str = "unknown"
    model: str = "unknown"
    api_key_configured: bool = False
    mcp_total_services: int = 0
    mcp_running_services: int = 0
    mcp_local_services: int = 0
    mcp_placeholder_services: int = 0
    mcp_tool_count: int = 0
    mcp_error: str = ""


@dataclass(frozen=True)
class TuiTaskDraft:
    command: TaskCommand
    target: str
    only_host: str | None = None
    only_port: int | None = None
    only_path: str | None = None
    blocked_host: str | None = None
    blocked_path: str | None = None
    allow_actions: tuple[str, ...] = ()
    block_actions: tuple[str, ...] = ()
    resume: bool = True

    @property
    def command_line(self) -> str:
        """Return a copyable command line for the current draft."""
        return " ".join(build_command_preview_args(self))


TaskLauncher = Callable[[TuiTaskDraft], None]


def _build_modes() -> dict[CheckMode, TuiMode]:
    """Build MODES dict with translated labels and descriptions."""
    return {
        "quick": TuiMode(
            key="quick",
            label=_("tui.mode_quick"),
            command="recon",
            description=_("tui.mode_quick_desc"),
            allow_actions=("recon",),
            block_actions=("exploit", "persistent", "post_exploitation"),
        ),
        "standard": TuiMode(
            key="standard",
            label=_("tui.mode_standard"),
            command="run",
            description=_("tui.mode_standard_desc"),
            allow_actions=("recon", "scan"),
            block_actions=("post_exploitation",),
        ),
        "deep": TuiMode(
            key="deep",
            label=_("tui.mode_deep"),
            command="scan",
            description=_("tui.mode_deep_desc"),
            allow_actions=("recon", "scan", "exploit"),
            needs_extra_confirm=True,
        ),
        "continuous": TuiMode(
            key="continuous",
            label=_("tui.mode_continuous"),
            command="persistent",
            description=_("tui.mode_continuous_desc"),
            allow_actions=("recon", "scan"),
            block_actions=("post_exploitation",),
            needs_extra_confirm=True,
        ),
    }


def _build_menu_items() -> dict[str, str]:
    """Build MENU_ITEMS dict with translated labels."""
    return {
        "1": _("tui.menu_set_target"),
        "2": _("tui.menu_select_mode"),
        "3": _("tui.menu_set_scope"),
        "4": _("tui.menu_start"),
        "5": _("tui.menu_history"),
        "6": _("tui.menu_report"),
        "7": _("tui.menu_diagnostic"),
        "8": _("tui.menu_config"),
        "q": _("tui.menu_exit"),
    }


MODES: dict[CheckMode, TuiMode] = _build_modes()
MENU_ITEMS: dict[str, str] = _build_menu_items()


def render_tui_home(state: TuiState | None = None, *, width: int = 110) -> str:
    """Render the TUI home surface into plain text for tests and dry-runs."""
    console = Console(
        file=io.StringIO(),
        record=True,
        width=width,
        force_terminal=False,
        color_system=None,
    )
    config = load_config()
    console.print(build_dashboard(config, state or TuiState()))
    return console.export_text()


def build_state_from_options(
    *,
    target: str = "",
    mode: CheckMode = "standard",
    only_host: str = "",
    only_port: str | int | None = "",
    only_path: str = "",
    blocked_host: str = "",
    blocked_path: str = "",
    allow_actions: str | tuple[str, ...] | list[str] | None = None,
    block_actions: str | tuple[str, ...] | list[str] | None = None,
    resume: bool = True,
) -> TuiState:
    """Build a TUI state object from CLI flags or tests."""
    return TuiState(
        target=target.strip(),
        mode=mode,
        only_host=only_host.strip(),
        only_port=str(only_port or "").strip(),
        only_path=only_path.strip(),
        blocked_host=blocked_host.strip(),
        blocked_path=blocked_path.strip(),
        allow_actions=_parse_action_csv(allow_actions),
        block_actions=_parse_action_csv(block_actions),
        resume=resume,
    )


def build_dashboard(config, state: TuiState) -> Group:
    """Build the first-screen VulnClaw TUI dashboard."""
    mode = MODES[state.mode]
    provider = getattr(config.llm, "provider", "unknown")
    model = getattr(config.llm, "model", "unknown")
    api_ready = bool(getattr(config.llm, "api_key", ""))
    overview = build_target_overview(state.target)

    title = Text(_("tui.title"), style="bold cyan")
    subtitle = Text(_("tui.desc"), style="dim")
    header = Panel(
        Align.left(Group(title, subtitle)),
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    status = Table.grid(expand=True)
    status.add_column(ratio=1)
    status.add_column(ratio=1)
    status.add_column(ratio=1)
    status.add_row(
        _metric_panel(_("tui.authorized_target"), state.target or _("tui.target_not_set"), "yellow" if not state.target else "green"),
        _metric_panel(_("tui.check_mode"), f"{mode.label} / {mode.command}", "cyan"),
        _metric_panel(_("tui.ai_model"), f"{provider} · {model}", "green" if api_ready else "yellow"),
    )

    scope_table = Table(box=box.SIMPLE_HEAVY, expand=True, show_header=True)
    scope_table.add_column(_("tui.test_scope"), style="bold")
    scope_table.add_column(_("tui.current_value"))
    scope_table.add_row(_("tui.only_host"), state.only_host or _("tui.only_host_default"))
    scope_table.add_row(_("tui.only_port"), state.only_port or _("tui.only_port_default"))
    scope_table.add_row(_("tui.only_path"), state.only_path or _("tui.only_path_default"))
    scope_table.add_row(_("tui.blocked_host"), state.blocked_host or _("tui.blocked_host_default"))
    scope_table.add_row(_("tui.blocked_path"), state.blocked_path or _("tui.blocked_path_default"))
    scope_table.add_row(_("tui.allowed_actions"), ", ".join(_effective_allow_actions(state)) or _("tui.not_set"))
    scope_table.add_row(_("tui.blocked_actions"), ", ".join(_effective_block_actions(state)) or _("tui.not_set"))

    overview_table = Table(box=box.SIMPLE_HEAVY, expand=True, show_header=True)
    overview_table.add_column(_("tui.workbench_overview"), style="bold")
    overview_table.add_column(_("tui.current_status"))
    overview_table.add_row(_("tui.model_key"), _("tui.model_key_configured") if api_ready else _("tui.model_key_not_configured"))
    overview_table.add_row(_("tui.history_resume"), _("tui.history_resume_on") if state.resume else _("tui.history_resume_off"))
    overview_table.add_row(_("tui.target_history"), _format_target_history_line(overview))
    overview_table.add_row(_("tui.risk_overview"), _format_findings_line(overview))
    overview_table.add_row(_("tui.persistent_constraints"), overview.constraints_summary)
    overview_table.add_row(_("tui.constraints_violations"), f"{overview.violations_count} {_('tui.times')}")
    if overview.last_command:
        overview_table.add_row(_("tui.last_command"), overview.last_command)
    if overview.error:
        overview_table.add_row(_("tui.history_error"), overview.error)

    menu = Table(box=box.MINIMAL_HEAVY_HEAD, expand=True, show_header=False)
    menu.add_column("Key", style="bold cyan", width=6)
    menu.add_column("Action")
    for key, label in MENU_ITEMS.items():
        menu.add_row(key, label)

    command_preview = _draft_from_state(state).command_line
    footer = Panel(
        f"[bold]{_('tui.command_preview')}\n{command_preview}\n\n"
        f"[dim]{_('tui.cli_note')}[/]",
        title=_("tui.confirm_title"),
        border_style="green" if state.target else "yellow",
        box=box.ROUNDED,
    )

    return Group(
        header,
        status,
        Panel(overview_table, title=_("tui.overview_title"), border_style="blue", box=box.ROUNDED),
        Panel(scope_table, title=_("tui.boundary_title"), border_style="green", box=box.ROUNDED),
        Panel(menu, title=_("tui.menu_title"), border_style="cyan", box=box.ROUNDED),
        footer,
    )


def run_tui(
    *,
    launcher: TaskLauncher | None = None,
    once: bool = False,
    initial_state: TuiState | None = None,
) -> None:
    """Run the interactive terminal UI loop."""
    state = initial_state or TuiState()
    config = load_config()
    active_launcher = launcher or _default_launcher
    screen = Console()

    exit_requested = False
    _last_ctrlc_time = 0.0

    while True:
        screen.clear()
        screen.print(build_dashboard(config, state))

        if once:
            return

        try:
            choice = Prompt.ask(
                _("tui.select_action"),
                choices=list(MENU_ITEMS.keys()),
                default="1" if not state.target else "4",
            )
        except KeyboardInterrupt:
            now = time.monotonic()
            if exit_requested and (now - _last_ctrlc_time) < 3.0:
                screen.print(_("tui.exited"))
                return
            exit_requested = True
            _last_ctrlc_time = now
            screen.print(f"\n{_('tui.press_again')}")
            Prompt.ask(_("tui.press_enter"), default="")
            continue

        # Reset double-ctrl-c guard on any normal input
        exit_requested = False

        try:
            if choice == "q":
                screen.print(_("tui.exited"))
                return
            if choice == "1":
                _prompt_target(state)
            elif choice == "2":
                _prompt_mode(state)
            elif choice == "3":
                _prompt_scope(state)
            elif choice == "4":
                _confirm_and_launch(state, active_launcher)
            elif choice == "5":
                _show_target_history(screen, state)
            elif choice == "6":
                _generate_target_report(screen, state)
            elif choice == "7":
                screen.print(build_runtime_diagnostic_panel(config))
                Prompt.ask(_("tui.press_enter"), default="")
            elif choice == "8":
                config = _prompt_llm_config(screen, config)
        except KeyboardInterrupt:
            # Interrupted inside a sub-prompt — return to main loop
            continue


def render_task_summary(draft: TuiTaskDraft, *, width: int = 100) -> str:
    """Render a launch summary for dry-run output and tests."""
    console = Console(
        file=io.StringIO(),
        record=True,
        width=width,
        force_terminal=False,
        color_system=None,
    )
    console.print(_build_task_summary_panel(draft))
    return console.export_text()


def build_task_draft(state: TuiState) -> TuiTaskDraft:
    """Public wrapper for converting TUI state into an executable task draft."""
    return _draft_from_state(state)


def build_target_overview(target: str) -> TuiTargetOverview:
    """Build a safe target-history overview for the TUI dashboard."""
    normalized = target.strip()
    if not normalized:
        return TuiTargetOverview(target="", has_history=False)

    try:
        preview = get_target_state_preview(normalized)
        snapshots = list_target_snapshots(normalized)
    except Exception as exc:
        return TuiTargetOverview(
            target=normalized,
            has_history=False,
            error=f"读取失败: {exc}",
        )

    if preview is None:
        return TuiTargetOverview(target=normalized, has_history=False)

    violations = preview.get("constraint_violations", [])
    if not isinstance(violations, list):
        violations = []

    return TuiTargetOverview(
        target=str(preview.get("target") or normalized),
        has_history=True,
        snapshot_count=len(snapshots),
        phase=str(preview.get("phase") or "unknown"),
        findings_count=_safe_int(preview.get("findings_count")),
        verified_count=_safe_int(preview.get("verified_count")),
        pending_count=_safe_int(preview.get("pending_count")),
        constraints_summary=_format_constraints_summary(preview.get("constraints")),
        violations_count=len(violations),
        last_command=str(preview.get("last_command") or ""),
    )


def build_runtime_diagnostic(config) -> TuiRuntimeDiagnostic:
    """Collect runtime readiness without leaving the TUI."""
    provider = str(getattr(config.llm, "provider", "unknown"))
    model = str(getattr(config.llm, "model", "unknown"))
    api_key_configured = bool(getattr(config.llm, "api_key", ""))

    node_version = _command_version("node", "--version") or "missing"
    npx_status = "installed" if shutil.which("npx") else "missing"
    uvx_status = "installed" if shutil.which("uvx") else "missing"
    nmap_status = "installed" if shutil.which("nmap") else "optional/missing"

    try:
        from vulnclaw.web.services.mcp_service import get_mcp_diagnostics

        mcp_diag = get_mcp_diagnostics()
        return TuiRuntimeDiagnostic(
            python_version=sys.version.split()[0],
            node_version=node_version,
            npx_status=npx_status,
            uvx_status=uvx_status,
            nmap_status=nmap_status,
            provider=provider,
            model=model,
            api_key_configured=api_key_configured,
            mcp_total_services=mcp_diag.total_services,
            mcp_running_services=mcp_diag.running_services,
            mcp_local_services=mcp_diag.local_services,
            mcp_placeholder_services=mcp_diag.placeholder_services,
            mcp_tool_count=mcp_diag.tool_count,
        )
    except Exception as exc:
        return TuiRuntimeDiagnostic(
            python_version=sys.version.split()[0],
            node_version=node_version,
            npx_status=npx_status,
            uvx_status=uvx_status,
            nmap_status=nmap_status,
            provider=provider,
            model=model,
            api_key_configured=api_key_configured,
            mcp_error=f"MCP 诊断失败: {exc}",
        )


def build_runtime_diagnostic_panel(config) -> Panel:
    """Render the runtime diagnostic panel used by menu item 7."""
    diagnostic = build_runtime_diagnostic(config)
    table = Table(box=box.SIMPLE_HEAVY, expand=True, show_header=True)
    table.add_column(_("tui.diagnostic_item"), style="bold")
    table.add_column(_("tui.diagnostic_status"))
    table.add_row("Python", diagnostic.python_version)
    table.add_row("Node.js", diagnostic.node_version)
    table.add_row("npx", diagnostic.npx_status)
    table.add_row("uvx", diagnostic.uvx_status)
    table.add_row("nmap", diagnostic.nmap_status)
    table.add_row("LLM Provider", diagnostic.provider)
    table.add_row("LLM Model", diagnostic.model)
    table.add_row("API Key", _("tui.model_key_configured") if diagnostic.api_key_configured else _("tui.model_key_not_configured"))
    table.add_row(
        "MCP Services",
        (
            f"{diagnostic.mcp_total_services} registered / "
            f"{diagnostic.mcp_running_services} running / "
            f"{diagnostic.mcp_local_services} local / "
            f"{diagnostic.mcp_placeholder_services} placeholder"
        ),
    )
    table.add_row("MCP Tools", str(diagnostic.mcp_tool_count))
    if diagnostic.mcp_error:
        table.add_row("MCP Error", diagnostic.mcp_error)

    footer = _("tui.diagnostic_footer")
    return Panel(Group(table, Text.from_markup(footer)), title=_("tui.diagnostic_title"), border_style="cyan")


def _command_version(command: str, *args: str) -> str:
    path = shutil.which(command)
    if not path:
        return ""
    try:
        result = subprocess.run(
            [path, *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return "check failed"
    return (result.stdout or result.stderr).strip() or "installed"


def _metric_panel(label: str, value: str, style: str) -> Panel:
    return Panel(
        f"[dim]{label}[/]\n[bold {style}]{value}[/]",
        box=box.ROUNDED,
        border_style=style,
    )


def _safe_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _format_target_history_line(overview: TuiTargetOverview) -> str:
    if not overview.target:
        return _("tui.no_target")
    if overview.error:
        return _("tui.read_error_short")
    if not overview.has_history:
        return _("tui.no_history")
    return f"{overview.snapshot_count} {_('tui.snapshots')} / {_('tui.phase')} {overview.phase}"


def _format_findings_line(overview: TuiTargetOverview) -> str:
    if not overview.has_history:
        return _("tui.no_findings")
    return (
        f"{overview.findings_count} {_('tui.risks')}"
        f"({_('tui.verified')} {overview.verified_count} / {_('tui.pending')} {overview.pending_count})"
    )


def _format_constraints_summary(raw: object) -> str:
    if not isinstance(raw, dict) or not raw:
        return _("tui.constraints_not_recorded")

    parts: list[str] = []
    mapping = [
        ("allowed_hosts", _("tui.allowed_hosts")),
        ("allowed_ports", _("tui.allowed_ports")),
        ("allowed_paths", _("tui.allowed_paths")),
        ("blocked_hosts", _("tui.blocked_hosts")),
        ("blocked_paths", _("tui.blocked_paths")),
        ("allowed_actions", _("tui.allowed_actions")),
        ("blocked_actions", _("tui.blocked_actions")),
    ]
    for key, label in mapping:
        value = raw.get(key)
        if isinstance(value, list) and value:
            parts.append(f"{label}: {', '.join(str(item) for item in value)}")
        elif value:
            parts.append(f"{label}: {value}")

    if raw.get("strict_mode"):
        parts.append(_("tui.strict_mode"))

    return "；".join(parts) if parts else _("tui.constraints_not_recorded")


def _effective_allow_actions(state: TuiState) -> tuple[str, ...]:
    return tuple(state.allow_actions) or MODES[state.mode].allow_actions


def _effective_block_actions(state: TuiState) -> tuple[str, ...]:
    return tuple(state.block_actions) or MODES[state.mode].block_actions


def _parse_action_csv(value: str | tuple[str, ...] | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def _parse_optional_port(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError("端口必须是 1-65535 之间的数字") from exc
    if port < 1 or port > 65535:
        raise ValueError("端口必须是 1-65535 之间的数字")
    return port


def _draft_from_state(state: TuiState) -> TuiTaskDraft:
    mode = MODES[state.mode]
    return TuiTaskDraft(
        command=mode.command,
        target=state.target.strip() or "<target>",
        only_host=state.only_host.strip() or None,
        only_port=_parse_optional_port(state.only_port),
        only_path=state.only_path.strip() or None,
        blocked_host=state.blocked_host.strip() or None,
        blocked_path=state.blocked_path.strip() or None,
        allow_actions=_effective_allow_actions(state),
        block_actions=_effective_block_actions(state),
        resume=state.resume,
    )


def _build_command_preview_args(draft: TuiTaskDraft) -> list[str]:
    return build_command_preview_args(draft)


def build_command_preview_args(draft: TuiTaskDraft) -> list[str]:
    """Build a copyable CLI command from a TUI task draft."""
    args = ["vulnclaw", draft.command, draft.target]
    if not draft.resume:
        args.append("--no-resume")
    if draft.only_port is not None:
        args.extend(["--only-port", str(draft.only_port)])
    if draft.only_host:
        args.extend(["--only-host", draft.only_host])
    if draft.only_path:
        args.extend(["--only-path", draft.only_path])
    if draft.blocked_host:
        args.extend(["--blocked-host", draft.blocked_host])
    if draft.blocked_path:
        args.extend(["--blocked-path", draft.blocked_path])
    if draft.allow_actions:
        args.extend(["--allow-actions", ",".join(draft.allow_actions)])
    if draft.block_actions:
        args.extend(["--block-actions", ",".join(draft.block_actions)])
    return args


def _prompt_target(state: TuiState) -> None:
    state.target = Prompt.ask(_("tui.enter_target"), default=state.target).strip()


def _prompt_mode(state: TuiState) -> None:
    choices = list(MODES.keys())
    table = Table(title=_("tui.check_mode"), box=box.SIMPLE)
    table.add_column("Key", style="bold cyan")
    table.add_column(_("tui.name"))
    table.add_column(_("tui.description"))
    for key in choices:
        mode = MODES[key]
        table.add_row(key, mode.label, mode.description)
    Console().print(table)
    state.mode = Prompt.ask(_("tui.select_mode"), choices=choices, default=state.mode)  # type: ignore[assignment]


def _prompt_llm_config(screen: Console, config):
    provider_table = Table(title=_("tui.available_providers"), box=box.SIMPLE)
    provider_table.add_column("Provider", style="bold cyan")
    provider_table.add_column("Default Model")
    provider_table.add_column("Base URL")
    for item in list_providers():
        marker = " *" if item["provider"] == config.llm.provider else ""
        provider_table.add_row(
            f"{item['provider']}{marker}",
            item.get("default_model", ""),
            item.get("base_url", ""),
        )
    screen.print(provider_table)

    provider = Prompt.ask(
        _("tui.select_provider"),
        default=config.llm.provider,
    ).strip()
    if provider and provider != config.llm.provider:
        config = apply_provider_preset(config, provider)

    base_url = Prompt.ask("Base URL", default=config.llm.base_url).strip()
    model = Prompt.ask("Model", default=config.llm.model).strip()
    current_key = _("tui.api_key_configured") if config.llm.api_key else _("tui.api_key_not_configured")
    api_key = Prompt.ask(_("tui.enter_api_key"), default="").strip()

    if base_url:
        config.llm.base_url = base_url
    if model:
        config.llm.model = model
    if api_key:
        config.llm.api_key = api_key
    save_config(config)

    screen.print(
        Panel(
            f"Provider: [bold]{config.llm.provider}[/]\n"
            f"Base URL: [dim]{config.llm.base_url}[/]\n"
            f"Model: [dim]{config.llm.model}[/]\n"
            f"API Key: {_('tui.updated') if api_key else current_key}",
            title=_("tui.config_saved"),
            border_style="green",
        )
    )
    Prompt.ask(_("tui.press_enter"), default="")
    return config


def _prompt_scope(state: TuiState) -> None:
    state.only_host = Prompt.ask(_("tui.enter_only_host"), default=state.only_host).strip()
    while True:
        state.only_port = Prompt.ask(_("tui.enter_only_port"), default=state.only_port).strip()
        try:
            _parse_optional_port(state.only_port)
            break
        except ValueError as exc:
            Console().print(f"[red]{exc}[/]")
    state.only_path = Prompt.ask(_("tui.enter_only_path"), default=state.only_path).strip()
    state.blocked_host = Prompt.ask(_("tui.enter_blocked_host"), default=state.blocked_host).strip()
    state.blocked_path = Prompt.ask(_("tui.enter_blocked_path"), default=state.blocked_path).strip()
    state.allow_actions = _parse_action_csv(
        Prompt.ask(
            _("tui.enter_allowed_actions"),
            default=",".join(state.allow_actions),
        )
    )
    state.block_actions = _parse_action_csv(
        Prompt.ask(
            _("tui.enter_blocked_actions"),
            default=",".join(state.block_actions),
        )
    )
    state.resume = Confirm.ask(_("tui.resume_history"), default=state.resume)


def _confirm_and_launch(state: TuiState, launcher: TaskLauncher) -> None:
    if not state.target.strip():
        Console().print(_("tui.please_set_target"))
        Prompt.ask(_("tui.press_enter"), default="")
        return

    mode = MODES[state.mode]
    if mode.needs_extra_confirm:
        ok = Confirm.ask(
            _("tui.confirm_deep_mode", mode=mode.label),
            default=False,
        )
        if not ok:
            return

    draft = _draft_from_state(state)
    Console().print(_build_task_summary_panel(draft, title=_("tui.launch_summary")))
    if Confirm.ask(_("tui.start_check"), default=False):
        Console().print(_("tui.enter_task_mode"))
        launcher(draft)
        Prompt.ask(_("tui.task_returned"), default="")


def _build_task_summary_panel(draft: TuiTaskDraft, *, title: str = "启动摘要") -> Panel:
    lines = [
        f"{_('tui.target')}: [bold]{draft.target}[/]",
        f"{_('tui.command')}: [bold]{draft.command}[/]",
        f"{_('tui.resume_history')}: {_('tui.yes') if draft.resume else _('tui.no')}",
        f"{_('tui.only_host')}: {draft.only_host or _('tui.unrestricted')}",
        f"{_('tui.only_port')}: {draft.only_port if draft.only_port is not None else _('tui.unrestricted')}",
        f"{_('tui.only_path')}: {draft.only_path or _('tui.unrestricted')}",
        f"{_('tui.blocked_host')}: {draft.blocked_host or _('tui.not_set')}",
        f"{_('tui.blocked_path')}: {draft.blocked_path or _('tui.not_set')}",
        f"{_('tui.allowed_actions')}: {', '.join(draft.allow_actions) or _('tui.not_set')}",
        f"{_('tui.blocked_actions')}: {', '.join(draft.block_actions) or _('tui.not_set')}",
        "",
        f"[bold]{_('tui.copyable_command')}[/]",
        draft.command_line,
    ]
    return Panel("\n".join(lines), title=title, border_style="yellow", box=box.ROUNDED)


def _show_target_history(screen: Console, state: TuiState) -> None:
    if not state.target.strip():
        screen.print(_("tui.please_set_target"))
        Prompt.ask(_("tui.press_enter"), default="")
        return

    preview = get_target_state_preview(state.target)
    snapshots = list_target_snapshots(state.target)
    if preview is None:
        screen.print(Panel(_("tui.no_history_for_target"), title=_("tui.history_status"), border_style="yellow"))
    else:
        screen.print(
            Panel(
                f"{_('tui.target')}: [bold]{preview.get('target', state.target)}[/]\n"
                f"{_('tui.phase')}: [bold]{preview.get('phase', 'unknown')}[/]\n"
                f"{_('tui.findings_count')}: [bold]{preview.get('findings_count', 0)}[/]\n"
                f"{_('tui.snapshot_count')}: [bold]{len(snapshots)}[/]",
                title=_("tui.history_status"),
                border_style="cyan",
            )
        )
    Prompt.ask(_("tui.press_enter"), default="")


def _generate_target_report(screen: Console, state: TuiState) -> None:
    if not state.target.strip():
        screen.print(_("tui.please_set_target"))
        Prompt.ask(_("tui.press_enter"), default="")
        return

    from vulnclaw.cli.main import _generate_report_for_target

    report_path = _generate_report_for_target(state.target)
    screen.print(Panel(report_path, title=_("tui.report_generated"), border_style="green"))
    Prompt.ask(_("tui.press_enter"), default="")


def _default_launcher(draft: TuiTaskDraft) -> None:
    from vulnclaw.cli import main as cli_main

    allow_actions = ",".join(draft.allow_actions) if draft.allow_actions else None
    block_actions = ",".join(draft.block_actions) if draft.block_actions else None

    common = {
        "target": draft.target,
        "only_port": draft.only_port,
        "only_host": draft.only_host,
        "only_path": draft.only_path,
        "blocked_host": draft.blocked_host,
        "blocked_path": draft.blocked_path,
        "allow_actions": allow_actions,
        "block_actions": block_actions,
        "resume": draft.resume,
        "snapshot": None,
    }

    if draft.command == "recon":
        cli_main.recon(**common)
    elif draft.command == "scan":
        cli_main.scan(ports=None, **common)
    elif draft.command == "persistent":
        cli_main.persistent(rounds=0, cycles=0, no_report=False, **common)
    else:
        cli_main.run(scope="full", output=None, **common)
