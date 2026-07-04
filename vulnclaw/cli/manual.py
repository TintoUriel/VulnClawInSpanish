"""Full CLI manual rendering for VulnClaw."""

from __future__ import annotations

from dataclasses import dataclass

from vulnclaw import __version__
from vulnclaw.config.schema import PROVIDER_PRESETS


@dataclass(frozen=True)
class ManualTopic:
    """A CLI manual topic or command."""

    name: str
    summary: str
    usage: str
    flags: tuple[tuple[str, str], ...] = ()
    notes: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


ROOT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("--help", "Show Typer's short help for the root command or selected subcommand."),
    ("--version", "Print the installed VulnClaw version and exit."),
    ("--man, --manual", "Print this full CLI manual and exit."),
)

COMMON_TASK_FLAGS: tuple[tuple[str, str], ...] = (
    (
        "--prompt TEXT",
        "Replace the built-in task prompt entirely. Use this when the default command intent is "
        "close but you need exact wording, credentials context, a lab note, or a custom workflow.",
    ),
    (
        "--only-port PORT",
        "Add a hard scope hint that only this TCP/UDP port is in scope. Valid ports are 1-65535.",
    ),
    (
        "--only-host HOST",
        "Restrict testing to one host even when a URL, CIDR, recon data, or target history points "
        "at related hosts.",
    ),
    (
        "--only-path PATH",
        "Restrict web testing to one path such as /admin. Available on URL-oriented task commands.",
    ),
    (
        "--blocked-host HOST",
        "Mark a host as explicitly out of scope. Tool calls to that host are blocked where VulnClaw "
        "can infer the destination.",
    ),
    (
        "--blocked-path PATH",
        "Mark a path as explicitly out of scope. Available on URL-oriented task commands.",
    ),
    (
        "--allow-actions CSV",
        "Comma-separated action allowlist. Common values are recon, scan, exploit, "
        "post_exploitation, report, run, and persistent. If set, commands outside the allowlist "
        "are blocked before the task starts, and tool/phase checks continue during the run.",
    ),
    (
        "--block-actions CSV",
        "Comma-separated action denylist using the same action names as --allow-actions.",
    ),
    (
        "--resume / --no-resume",
        "Resume saved target history by default. Use --no-resume for a clean run that ignores "
        "stored target state.",
    ),
    (
        "--snapshot ID",
        "Resume from a specific target-state snapshot instead of the latest one.",
    ),
)

ACTION_NAMES = (
    "recon",
    "scan",
    "exploit",
    "post_exploitation",
    "report",
    "run",
    "persistent",
)

COMMANDS: tuple[ManualTopic, ...] = (
    ManualTopic(
        name="run",
        summary="Run the full authorized pentest workflow against one target.",
        usage="vulnclaw run TARGET [--scope full|web|api|mobile] [--output PATH] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required host, IP, URL, or other authorized target identifier."),
            (
                "--scope TEXT",
                "High-level test focus. Built-in wording recognizes full, web, api, and mobile, "
                "but the value is passed into the task prompt, so custom labels are possible.",
            ),
            (
                "--output PATH",
                "After the run, generate a report at PATH from the saved target state. A .html "
                "suffix writes HTML; otherwise the configured report format is used.",
            ),
        ),
        notes=(
            "Requires configured LLM credentials (llm.api_key or auth_mode) before the task starts.",
            "By default (session.engine=solve) this runs the goal-driven solve loop — no fixed round "
            "count, bounded by session.solve_max_steps/solve_max_intents/solve_max_tool_rounds — and "
            "stops when the exploration frontier is exhausted, same underlying engine as `vulnclaw "
            "solve`. Set session.engine=rounds to use the legacy fixed-round auto_pentest loop "
            "instead (bounded by session.max_rounds).",
            "Use --allow-actions recon,scan when you want broad coverage but no exploitation.",
        ),
        examples=(
            "vulnclaw run https://lab.example --scope web --allow-actions recon,scan",
            "vulnclaw run 10.10.10.5 --output reports/lab.md --no-resume",
        ),
    ),
    ManualTopic(
        name="solve",
        summary="Goal-driven solve loop with no fixed round count.",
        usage=(
            "vulnclaw solve TARGET [--goal TEXT] [--max-steps N] [--max-intents N] "
            "[--max-tool-rounds N] [--resume/--no-resume] [--snapshot ID]"
        ),
        flags=(
            ("TARGET", "Required host, IP, URL, or other authorized target identifier."),
            (
                "--goal TEXT",
                "Success condition, e.g. 'capture the flag' or 'get a shell'. Defaults to finding "
                "and verifying a flag/shell/high-value vulnerability.",
            ),
            ("--prompt TEXT", "Custom task description that overrides the auto-generated one."),
            (
                "--max-steps N",
                "Safety cap on explore steps (not a fixed workflow length; default 40).",
            ),
            ("--max-intents N", "Max new intents generated per reason step (default 3)."),
            (
                "--max-tool-rounds N",
                "Max tool-calling rounds per intent exploration (default 4).",
            ),
            ("--resume / --no-resume", "Resume saved target history by default."),
            ("--snapshot ID", "Resume from a specific target-state snapshot instead of the latest one."),
        ),
        notes=(
            "Unlike run/persistent, solve has no fixed round count: it searches a Fact/Intent graph "
            "from the target toward the goal and stops on success or when no path remains.",
            "This is the same engine `run` uses by default (session.engine=solve); `solve` exposes "
            "its tuning knobs directly on the command line instead of through config.",
        ),
        examples=(
            "vulnclaw solve https://lab.example --goal 'get a shell'",
            "vulnclaw solve 10.10.10.5 --max-steps 60 --max-intents 4",
        ),
    ),
    ManualTopic(
        name="persistent",
        summary="Run repeated pentest cycles and optionally write a report after each cycle.",
        usage="vulnclaw persistent TARGET [--rounds N] [--cycles N] [--no-report] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required authorized target."),
            (
                "--rounds N, -r N",
                "Rounds per cycle. 0 means use session.persistent_rounds_per_cycle from config.",
            ),
            (
                "--cycles N, -c N",
                "Maximum number of cycles. 0 means use session.persistent_max_cycles from config; "
                "if that config value is also 0, the run is unlimited until interrupted.",
            ),
            ("--no-report", "Disable the normal persistent-cycle report generation."),
        ),
        notes=(
            "Persistent mode is for long authorized lab or assessment runs where VulnClaw should "
            "keep cycling through recon, scan, verification, and reporting.",
            "Use Ctrl+C to interrupt. The command still prints a final summary.",
        ),
        examples=(
            "vulnclaw persistent https://lab.example --rounds 25 --cycles 4",
            "vulnclaw persistent 10.0.0.0/24 --allow-actions recon,scan --no-report",
        ),
    ),
    ManualTopic(
        name="recon",
        summary="Run reconnaissance only, without exploitation.",
        usage="vulnclaw recon TARGET [COMMON TASK FLAGS]",
        flags=(("TARGET", "Required host, IP, URL, CIDR, or domain to investigate."),),
        notes=(
            "The default prompt asks for authorized reconnaissance without exploitation.",
            "Good first command when you only want asset discovery, fingerprinting, and notes.",
        ),
        examples=("vulnclaw recon example.com --only-host example.com",),
    ),
    ManualTopic(
        name="scan",
        summary="Run vulnerability discovery without exploitation.",
        usage="vulnclaw scan TARGET [--ports PORTS] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required authorized target."),
            (
                "--ports PORTS",
                "Port list or range hint such as 80,443,8080. This is prompt guidance, not an "
                "nmap-only switch; use network-scan for direct nmap profile control.",
            ),
        ),
        notes=(
            "The default prompt asks VulnClaw to identify vulnerabilities without exploitation.",
            "Use --block-actions exploit for an explicit denylist in addition to the scan wording.",
        ),
        examples=("vulnclaw scan https://lab.example --ports 80,443 --block-actions exploit",),
    ),
    ManualTopic(
        name="network-scan",
        summary="Run nmap-based network discovery and optional safe follow-up probes.",
        usage=(
            "vulnclaw network-scan [TARGET] [--profile adaptive|fast|thorough|stealth] "
            "[--ports PORTS] [--parallel-agents N]"
        ),
        flags=(
            (
                "TARGET",
                "Optional host, IP, or CIDR. If omitted, VulnClaw tries to detect the connected "
                "Wi-Fi subnet and scan that CIDR.",
            ),
            (
                "--profile TEXT",
                "nmap scan profile. adaptive uses target history and defaults; fast favors speed; "
                "thorough expands coverage; stealth lowers scan intensity.",
            ),
            ("--ports PORTS", "Port list or range for nmap, for example 22,80,443 or 1-1000."),
            (
                "--max-rounds N",
                "Agent follow-up rounds after nmap. 0 means use session.max_rounds.",
            ),
            (
                "--parallel-agents N",
                "Number of child agents to fan out across discovered surfaces. 1 disables fan-out.",
            ),
            (
                "--parallel-depth N",
                "Number of child-agent discovery waves when --parallel-agents is greater than 1.",
            ),
            ("--worker-rounds N", "Agent rounds per child surface worker."),
            (
                "--surface-limit N",
                "Maximum discovered surfaces considered for child-agent fan-out.",
            ),
            (
                "--safe-probes / --no-safe-probes",
                "With safe probes on, VulnClaw defaults to --allow-actions recon,scan and performs "
                "only non-destructive verification probes after nmap. With --no-safe-probes, it "
                "summarizes weak links without follow-up probes.",
            ),
            ("--only-port PORT", "Restrict follow-up analysis to one port."),
            ("--only-host HOST", "Restrict follow-up analysis to one host."),
            ("--blocked-host HOST", "Exclude a host from follow-up analysis."),
            ("--allow-actions CSV", "Override the safe-probe action allowlist."),
            ("--block-actions CSV", "Add an action denylist."),
            ("--resume / --no-resume", "Use or ignore saved target history."),
            ("--snapshot ID", "Resume from a specific target-state snapshot."),
        ),
        notes=(
            "This is the command to use when you want nmap involved directly.",
            "The built-in profile validation accepts adaptive, fast, thorough, and stealth.",
        ),
        examples=(
            "vulnclaw network-scan --profile fast",
            "vulnclaw network-scan 192.168.56.0/24 --ports 22,80,443 --parallel-agents 3",
        ),
    ),
    ManualTopic(
        name="exploit",
        summary="Run an authorized exploitation-focused task.",
        usage="vulnclaw exploit TARGET [--cve CVE-ID] [--cmd CMD] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required authorized target."),
            ("--cve CVE-ID", "Tell VulnClaw to focus on a specific CVE."),
            (
                "--cmd CMD",
                "Verification command for command-execution style findings. Defaults to id.",
            ),
        ),
        notes=(
            "Use only against systems where exploitation is explicitly authorized.",
            "Scope flags still apply and are checked before the command starts.",
        ),
        examples=(
            "vulnclaw exploit https://lab.example --cve CVE-2024-1234 --only-path /vulnerable",
        ),
    ),
    ManualTopic(
        name="report",
        summary="Generate a report from a saved session file or from target history.",
        usage="vulnclaw report SESSION_JSON [--target] [--pdf] [--pdf-out PATH]",
        flags=(
            (
                "SESSION_JSON",
                "Path to a saved session JSON file. With --target, this argument is interpreted "
                "as a target name instead.",
            ),
            (
                "--target",
                "Generate from the current target-state history rather than a session JSON file.",
            ),
            (
                "--pdf",
                "Also export a PDF. Requires the pdf extra, for example pip install 'vulnclaw[pdf]'.",
            ),
            (
                "--pdf-out PATH",
                "PDF output path. Defaults to the generated report path with a .pdf suffix.",
            ),
        ),
        notes=(
            "Reports include verified findings, false-positive/review status, attack path summary, "
            "and recorded scope governance where available.",
        ),
        examples=(
            "vulnclaw report ~/.vulnclaw/sessions/session_001.json",
            "vulnclaw report https://lab.example --target --pdf",
        ),
    ),
    ManualTopic(
        name="config",
        summary="Manage config values and provider presets.",
        usage=(
            "vulnclaw config list\n"
            "vulnclaw config get KEY\n"
            "vulnclaw config set KEY VALUE\n"
            "vulnclaw config provider [NAME|--list]"
        ),
        flags=(
            ("set KEY VALUE", "Set a dot-notated config key such as llm.model or session.max_rounds."),
            ("get KEY", "Print one config value. Secret-looking keys are masked."),
            ("list", "Print the full effective config as YAML."),
            ("provider NAME", "Switch provider preset and fill base_url/model defaults."),
            ("provider --list, -l", "List provider presets and show the current provider."),
        ),
        notes=(
            "A config subcommand is required; running vulnclaw config alone prints usage and exits.",
            "Useful LLM keys: llm.provider, llm.api_key, llm.api_keys, llm.auth_mode, "
            "llm.chatgpt_auto_proxy, llm.base_url, llm.model, llm.max_tokens, "
            "llm.max_context_tokens, llm.temperature, llm.reasoning_effort. Use `vulnclaw login` "
            "instead of llm.api_key for OAuth-based ChatGPT-subscription auth.",
            "Useful session keys: session.output_dir, session.report_format, session.max_rounds, "
            "session.engine (solve|rounds), session.solve_max_steps, session.solve_max_intents, "
            "session.solve_max_tool_rounds, session.solve_max_parallel, session.show_thinking, "
            "session.persistent_rounds_per_cycle, session.persistent_max_cycles, "
            "session.persistent_auto_report, session.language, session.reasoning_state_enabled, "
            "session.reflexion_enabled, session.plugin_runtime_enabled. The repl_parallel_* keys "
            "(repl_parallel_enabled/agents/depth/worker_rounds/surface_limit) only apply to the "
            "legacy 'rounds' engine's network-scan --parallel-agents fan-out, not to 'solve'.",
            "Useful safety keys: safety.enable_python_execute, safety.python_execute_mode, "
            "safety.python_execute_max_lines, safety.tool_parallel, safety.tool_max_concurrent.",
        ),
        examples=(
            "vulnclaw config provider --list",
            "vulnclaw config provider deepseek",
            "vulnclaw config set llm.api_keys 'key-one,key-two,key-three'",
            "vulnclaw config set session.max_rounds 25",
            "vulnclaw config set session.engine rounds",
        ),
    ),
    ManualTopic(
        name="kb",
        summary="Manage the local security knowledge base.",
        usage="vulnclaw kb update\nvulnclaw kb status",
        flags=(
            ("update", "Seed or refresh bundled knowledge-base entries."),
            ("status", "Show whether semantic retrieval is active, keyword fallback is active, or no data is available."),
        ),
        notes=(
            "Semantic retrieval requires the kb extra. Without it, VulnClaw falls back to keyword retrieval when data exists.",
        ),
        examples=("vulnclaw kb update", "vulnclaw kb status"),
    ),
    ManualTopic(
        name="target-state",
        summary="Inspect, compare, restore, or clear persisted target history.",
        usage=(
            "vulnclaw target-state list TARGET\n"
            "vulnclaw target-state preview TARGET [--snapshot ID]\n"
            "vulnclaw target-state diff TARGET FROM_ID [--to TO_ID]\n"
            "vulnclaw target-state rollback TARGET SNAPSHOT_ID\n"
            "vulnclaw target-state clear TARGET"
        ),
        flags=(
            ("list TARGET", "List up to 20 recent snapshots for a target."),
            ("preview TARGET", "Show phase, resume strategy, finding counts, priority assets, and next actions."),
            ("preview --snapshot ID", "Preview a specific snapshot."),
            ("diff TARGET FROM_ID --to TO_ID", "Compare two snapshots, or compare FROM_ID to current state when --to is omitted."),
            ("rollback TARGET SNAPSHOT_ID", "Restore target history to a snapshot."),
            ("clear TARGET", "Delete persisted target history for a target."),
        ),
        notes=(
            "Task commands use target state when --resume is enabled, which is the default.",
            "Use --no-resume on run/recon/scan/exploit/persistent/network-scan to ignore this history.",
        ),
        examples=(
            "vulnclaw target-state list https://lab.example",
            "vulnclaw target-state preview https://lab.example",
            "vulnclaw target-state diff https://lab.example snap-a --to snap-b",
        ),
        aliases=("target", "state", "history"),
    ),
    ManualTopic(
        name="plugins",
        summary="Inspect and run vulnerability detection plugins.",
        usage=(
            "vulnclaw plugins list [--stage STAGE] [--tag TAG]\n"
            "vulnclaw plugins info PLUGIN_ID\n"
            "vulnclaw plugins run PLUGIN_ID --target TARGET [--stage STAGE] [--option KEY=VALUE] "
            "[--input FILE]"
        ),
        flags=(
            ("list --stage STAGE", "Filter the plugin list by stage, e.g. discovery."),
            ("list --tag TAG", "Filter the plugin list by tag."),
            ("info PLUGIN_ID", "Print full JSON metadata for one plugin."),
            ("run PLUGIN_ID", "Required plugin id to run."),
            ("run --target TARGET", "Target host/IP/URL for the plugin run."),
            ("run --stage STAGE", "Plugin stage to run under (default: discovery)."),
            (
                "run --option KEY=VALUE, -o KEY=VALUE",
                "Plugin option, repeatable. The value is parsed as JSON when possible.",
            ),
            ("run --input FILE", "JSON file whose contents are merged into the plugin options."),
        ),
        notes=(
            "Plugins are the structured, non-LLM detection checks (headers, JS endpoints, JWT, "
            "etc.) that back session.plugin_runtime_enabled during autonomous runs.",
            "session.plugin_default_timeout and session.plugin_max_requests_per_target bound "
            "plugin execution during autonomous runs; the CLI run command has no such cap.",
        ),
        examples=(
            "vulnclaw plugins list",
            "vulnclaw plugins info builtin.web.headers",
            "vulnclaw plugins run builtin.web.headers --target https://lab.example",
        ),
    ),
    ManualTopic(
        name="tui",
        summary="Open the terminal workbench for guided task setup.",
        usage="vulnclaw tui [--target TARGET] [--mode quick|standard|deep|continuous] [SCOPE FLAGS]",
        flags=(
            ("--target TARGET, -t TARGET", "Pre-fill the authorized target."),
            (
                "--mode MODE, -m MODE",
                "Pre-fill workbench mode. quick maps to recon, standard maps to run, deep maps to "
                "scan, and continuous maps to persistent.",
            ),
            ("--only-port PORT", "Pre-fill a single allowed port."),
            ("--only-host HOST", "Pre-fill a single allowed host."),
            ("--only-path PATH", "Pre-fill a single allowed path."),
            ("--blocked-host HOST", "Pre-fill an excluded host."),
            ("--blocked-path PATH", "Pre-fill an excluded path."),
            ("--allow-actions CSV", "Pre-fill allowed actions."),
            ("--block-actions CSV", "Pre-fill blocked actions."),
            ("--resume / --no-resume", "Pre-fill target history resume behavior."),
            ("--dry-run", "Render the launch summary and exit without starting a task."),
            ("--once", "Render the dashboard once and exit, useful for smoke tests."),
        ),
        notes=(
            "The TUI exposes the same scope and action controls as the CLI task commands.",
        ),
        examples=(
            "vulnclaw tui",
            "vulnclaw tui --target https://lab.example --mode quick --only-port 443",
            "vulnclaw tui --dry-run --target https://lab.example --mode deep",
        ),
    ),
    ManualTopic(
        name="web",
        summary="Start the local FastAPI/React web UI.",
        usage="vulnclaw web [--host HOST] [--port PORT] [--dry-run] [--allow-remote]",
        flags=(
            ("--host HOST", "Bind address. Defaults to 127.0.0.1."),
            ("--port PORT", "Bind port. Defaults to 7788."),
            ("--dry-run", "Validate imports and print launch information without starting uvicorn."),
            (
                "--allow-remote",
                "Required when --host is not 127.0.0.1. This prevents accidentally exposing the Web UI.",
            ),
        ),
        notes=(
            "Install the web extra if FastAPI/uvicorn are missing: pip install 'vulnclaw[web]'.",
            "Keep the Web UI on localhost unless you intentionally need remote access.",
        ),
        examples=("vulnclaw web", "vulnclaw web --port 8080 --dry-run"),
    ),
    ManualTopic(
        name="repl",
        summary="Start the classic natural-language REPL.",
        usage="vulnclaw repl\nvulnclaw",
        flags=(
            ("no arguments", "Running vulnclaw with no subcommand opens this REPL by default."),
        ),
        notes=(
            "REPL commands include help, status, target TARGET, tools, report [TARGET], persistent [TARGET], think [on|off], clear, and exit.",
            "Natural-language inputs that include an auto-mode keyword and a target enter autonomous pentest mode.",
            "Bounded parallel child-agent fan-out is available from the network-scan command's --parallel-agents flag, not from the REPL directly.",
        ),
        examples=("vulnclaw", "vulnclaw repl"),
    ),
    ManualTopic(
        name="init",
        summary="Create the VulnClaw config directories and initial config file.",
        usage="vulnclaw init",
        notes=(
            "Creates ~/.vulnclaw by default, unless VULNCLAW_CONFIG_DIR points somewhere else.",
        ),
        examples=("vulnclaw init",),
    ),
    ManualTopic(
        name="doctor",
        summary="Check runtime readiness and configured integrations.",
        usage="vulnclaw doctor",
        notes=(
            "Checks Python, node, npx, uvx, nmap, LLM config, MCP service registration, and exposed tool count.",
            "Use this before a real run when provider, MCP, or frontend tooling feels unclear.",
        ),
        examples=("vulnclaw doctor",),
    ),
    ManualTopic(
        name="login",
        summary="Sign in with a ChatGPT subscription (Codex \"Sign in with ChatGPT\").",
        usage="vulnclaw login [--proxy-url URL] [--no-browser] [--set-default/--no-set-default]",
        flags=(
            (
                "--proxy-url URL",
                "Use an external OpenAI-compatible proxy base_url instead of the built-in bridge.",
            ),
            ("--no-browser", "Print the sign-in URL instead of opening a browser."),
            (
                "--set-default / --no-set-default",
                "Set llm.auth_mode=oauth on success (default: set it).",
            ),
        ),
        notes=(
            "Opens the ChatGPT consent page, stores a refreshable token, and (with "
            "llm.chatgpt_auto_proxy) starts a built-in local proxy that bridges chat.completions "
            "to the ChatGPT backend.",
            "This reuses OpenAI's first-party Codex OAuth client. Using a ChatGPT subscription "
            "through a non-official client may violate OpenAI's Terms of Service and can get your "
            "account restricted; proceed at your own risk.",
            "Use `vulnclaw logout` to remove stored tokens, or `vulnclaw config set llm.auth_mode "
            "static` plus llm.api_key to switch back to a static API key.",
        ),
        examples=("vulnclaw login", "vulnclaw login --no-browser"),
    ),
    ManualTopic(
        name="logout",
        summary="Remove stored OAuth tokens from the ChatGPT sign-in flow.",
        usage="vulnclaw logout",
        notes=("Does not change llm.auth_mode; switch it back to static separately if needed.",),
        examples=("vulnclaw logout",),
    ),
    ManualTopic(
        name="manual",
        summary="Print this full manual.",
        usage="vulnclaw manual [TOPIC] [--format text|markdown|man]\nvulnclaw man [TOPIC] [--format text|markdown|man]\nvulnclaw --man",
        flags=(
            ("TOPIC", "Optional command/topic name such as scan, network-scan, config, or target-state."),
            ("--format text, -f text", "Human terminal format. This is the default."),
            ("--format markdown, -f markdown", "Markdown suitable for docs or README snippets."),
            ("--format man, -f man", "roff man-page format suitable for saving as vulnclaw.1."),
        ),
        notes=(
            "The manual command is packaged with VulnClaw, so it works from installed wheels and source checkouts.",
        ),
        examples=(
            "vulnclaw manual",
            "vulnclaw manual network-scan",
            "vulnclaw manual --format man",
        ),
        aliases=("man", "help-man"),
    ),
)

TASK_COMMAND_NAMES = {"run", "persistent", "recon", "scan", "network-scan", "exploit"}


def render_manual(output_format: str = "text", topic: str | None = None) -> str:
    """Render the VulnClaw manual in text, markdown, or roff man-page format."""

    fmt = output_format.strip().lower()
    if fmt not in {"text", "markdown", "man"}:
        raise ValueError("manual format must be one of: text, markdown, man")

    topics = _select_topics(topic)
    normalized_topic = _normalize_topic(topic)
    if fmt == "markdown":
        return _render_markdown(topics, normalized_topic)
    if fmt == "man":
        return _render_man(topics, normalized_topic)
    return _render_text(topics, normalized_topic)


def available_topics() -> list[str]:
    """Return the user-facing topic names accepted by the manual command."""

    return [topic.name for topic in COMMANDS]


def _select_topics(topic: str | None) -> tuple[ManualTopic, ...]:
    normalized = _normalize_topic(topic)
    if not normalized:
        return COMMANDS

    by_name = {item.name: item for item in COMMANDS}
    for item in COMMANDS:
        by_name.update({alias: item for alias in item.aliases})

    selected = by_name.get(normalized)
    if not selected:
        raise ValueError(
            f"unknown manual topic '{topic}'. Available topics: {', '.join(available_topics())}"
        )
    return (selected,)


def _normalize_topic(topic: str | None) -> str:
    return (topic or "").strip().lower().replace("_", "-")


def _provider_names() -> str:
    return ", ".join(provider.value for provider in PROVIDER_PRESETS)


def _render_text(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines: list[str] = [
        "VULNCLAW(1) - VulnClaw CLI Manual",
        f"Version: {__version__}",
        "",
        "SYNOPSIS",
        "  vulnclaw [--help] [--version] [--man] [COMMAND] [ARGS]...",
        "  vulnclaw manual [TOPIC] [--format text|markdown|man]",
        "",
        "DESCRIPTION",
        "  VulnClaw is an AI-assisted CLI for authorized security testing. It combines",
        "  natural-language tasking, scoped autonomous loops, target history, reports,",
        "  MCP/built-in tools, a terminal workbench, and an optional local Web UI.",
        "",
        "ROOT OPTIONS",
    ]
    lines.extend(_render_text_pairs(ROOT_OPTIONS, indent_spaces=2))
    lines.extend(
        [
            "",
            "FAST START",
            "  vulnclaw init",
            "  vulnclaw config provider deepseek",
            "  vulnclaw config set llm.api_key <key>",
            "  vulnclaw doctor",
            "  vulnclaw run https://authorized-target.example --allow-actions recon,scan",
            "",
            "COMMAND MAP",
        ]
    )
    for item in COMMANDS:
        lines.append(f"  {item.name:<13} {item.summary}")

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend(_common_sections_text())

    lines.extend(["", "COMMAND DETAILS"])
    for item in topics:
        lines.extend(_topic_text(item))

    lines.extend(
        [
            "",
            "CONFIG AND ENVIRONMENT",
            f"  Provider presets: {_provider_names()}",
            "  Config directory: ~/.vulnclaw by default, or VULNCLAW_CONFIG_DIR when set.",
            "  High-value env vars: VULNCLAW_LLM_API_KEY, VULNCLAW_LLM_API_KEYS,",
            "  VULNCLAW_LLM_PROVIDER, VULNCLAW_LLM_BASE_URL, VULNCLAW_LLM_MODEL,",
            "  VULNCLAW_SESSION_OUTPUT_DIR, VULNCLAW_SESSION_MAX_ROUNDS,",
            "  VULNCLAW_SESSION_SHOW_THINKING, VULNCLAW_SAFETY_PYTHON_EXECUTE_ENABLED.",
            "",
            "SAFETY",
            "  VulnClaw is for authorized testing only. Scope flags and action constraints",
            "  are there to make allowed boundaries explicit and enforceable, but they do",
            "  not replace written authorization or a clear rules-of-engagement document.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _common_sections_text() -> list[str]:
    lines = [
        "",
        "COMMON TASK FLAGS",
    ]
    lines.extend(_render_text_pairs(COMMON_TASK_FLAGS, indent_spaces=2))
    lines.extend(
        [
            "",
            "ACTION CONSTRAINTS",
            f"  Recognized action names: {', '.join(ACTION_NAMES)}.",
            "  Example: --allow-actions recon,scan blocks direct exploit/report commands",
            "  and also constrains tool and phase transitions during agent execution.",
        ]
    )
    return lines


def _topic_text(topic: ManualTopic) -> list[str]:
    lines = [
        "",
        topic.name.upper(),
        f"  {topic.summary}",
        "",
        "  Usage:",
    ]
    for usage_line in topic.usage.splitlines():
        lines.append(f"    {usage_line}")

    if topic.flags:
        lines.extend(["", "  Arguments and flags:"])
        lines.extend(_render_text_pairs(topic.flags, indent_spaces=4))
    if topic.notes:
        lines.extend(["", "  Notes:"])
        lines.extend(f"    - {note}" for note in topic.notes)
    if topic.examples:
        lines.extend(["", "  Examples:"])
        lines.extend(f"    {example}" for example in topic.examples)
    return lines


def _render_text_pairs(pairs: tuple[tuple[str, str], ...], indent_spaces: int) -> list[str]:
    pad = " " * indent_spaces
    lines: list[str] = []
    for name, description in pairs:
        lines.append(f"{pad}{name}")
        lines.append(f"{pad}  {description}")
    return lines


def _render_markdown(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines: list[str] = [
        "# VulnClaw CLI Manual",
        "",
        f"Version: `{__version__}`",
        "",
        "## Synopsis",
        "",
        "```bash",
        "vulnclaw [--help] [--version] [--man] [COMMAND] [ARGS]...",
        "vulnclaw manual [TOPIC] [--format text|markdown|man]",
        "```",
        "",
        "## Description",
        "",
        "VulnClaw is an AI-assisted CLI for authorized security testing. It combines natural-language tasking, scoped autonomous loops, target history, reports, MCP/built-in tools, a terminal workbench, and an optional local Web UI.",
        "",
        "## Root Options",
        "",
    ]
    lines.extend(_markdown_table(["Option", "Meaning"], ROOT_OPTIONS))
    lines.extend(
        [
            "",
            "## Fast Start",
            "",
            "```bash",
            "vulnclaw init",
            "vulnclaw config provider deepseek",
            "vulnclaw config set llm.api_key <key>",
            "vulnclaw doctor",
            "vulnclaw run https://authorized-target.example --allow-actions recon,scan",
            "```",
            "",
            "## Command Map",
            "",
        ]
    )
    lines.extend(_markdown_table(["Command", "Summary"], tuple((c.name, c.summary) for c in COMMANDS)))

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend(
            [
                "",
                "## Common Task Flags",
                "",
            ]
        )
        lines.extend(_markdown_table(["Flag", "Meaning"], COMMON_TASK_FLAGS))
        lines.extend(
            [
                "",
                "## Action Constraints",
                "",
                f"Recognized action names: `{', '.join(ACTION_NAMES)}`.",
                "",
                "Example: `--allow-actions recon,scan` blocks direct exploit/report commands and also constrains tool and phase transitions during agent execution.",
            ]
        )

    lines.extend(["", "## Command Details", ""])
    for item in topics:
        lines.extend(_topic_markdown(item))

    lines.extend(
        [
            "",
            "## Config And Environment",
            "",
            f"Provider presets: `{_provider_names()}`.",
            "",
            "Config directory: `~/.vulnclaw` by default, or `VULNCLAW_CONFIG_DIR` when set.",
            "",
            "High-value env vars: `VULNCLAW_LLM_API_KEY`, `VULNCLAW_LLM_API_KEYS`, `VULNCLAW_LLM_PROVIDER`, `VULNCLAW_LLM_BASE_URL`, `VULNCLAW_LLM_MODEL`, `VULNCLAW_SESSION_OUTPUT_DIR`, `VULNCLAW_SESSION_MAX_ROUNDS`, `VULNCLAW_SESSION_SHOW_THINKING`, `VULNCLAW_SAFETY_PYTHON_EXECUTE_ENABLED`.",
            "",
            "## Safety",
            "",
            "VulnClaw is for authorized testing only. Scope flags and action constraints make allowed boundaries explicit and enforceable, but they do not replace written authorization or a clear rules-of-engagement document.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _topic_markdown(topic: ManualTopic) -> list[str]:
    lines = [
        f"### `{topic.name}`",
        "",
        topic.summary,
        "",
        "```bash",
        *topic.usage.splitlines(),
        "```",
    ]
    if topic.flags:
        lines.extend(["", "Arguments and flags:", ""])
        lines.extend(_markdown_table(["Name", "Meaning"], topic.flags))
    if topic.notes:
        lines.extend(["", "Notes:", ""])
        lines.extend(f"- {note}" for note in topic.notes)
    if topic.examples:
        lines.extend(["", "Examples:", "", "```bash", *topic.examples, "```"])
    lines.append("")
    return lines


def _markdown_table(headers: list[str], rows: tuple[tuple[str, str], ...]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for left, right in rows:
        lines.append(f"| `{left}` | {right} |")
    return lines


def _render_man(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines = [
        f'.TH VULNCLAW 1 "" "VulnClaw {__version__}" "VulnClaw Manual"',
        ".SH NAME",
        "vulnclaw \\- AI-assisted authorized security-testing CLI",
        ".SH SYNOPSIS",
        ".B vulnclaw",
        "[--help] [--version] [--man] [COMMAND] [ARGS]...",
        ".br",
        ".B vulnclaw manual",
        "[TOPIC] [--format text|markdown|man]",
        ".SH DESCRIPTION",
        "VulnClaw combines natural-language tasking, scoped autonomous loops, target history, reports, MCP and built-in tools, a terminal workbench, and an optional local Web UI.",
        ".SH ROOT OPTIONS",
    ]
    lines.extend(_roff_pairs(ROOT_OPTIONS))
    lines.extend(
        [
            ".SH COMMAND MAP",
        ]
    )
    lines.extend(_roff_pairs(tuple((item.name, item.summary) for item in COMMANDS)))

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend([".SH COMMON TASK FLAGS"])
        lines.extend(_roff_pairs(COMMON_TASK_FLAGS))
        lines.extend(
            [
                ".SH ACTION CONSTRAINTS",
                f"Recognized action names: {', '.join(ACTION_NAMES)}.",
            ]
        )

    lines.append(".SH COMMAND DETAILS")
    for item in topics:
        lines.extend(_topic_roff(item))

    lines.extend(
        [
            ".SH CONFIG AND ENVIRONMENT",
            f"Provider presets: {_provider_names()}.",
            ".PP",
            "Config directory: ~/.vulnclaw by default, or VULNCLAW_CONFIG_DIR when set.",
            ".PP",
            "High-value env vars: VULNCLAW_LLM_API_KEY, VULNCLAW_LLM_API_KEYS, VULNCLAW_LLM_PROVIDER, VULNCLAW_LLM_BASE_URL, VULNCLAW_LLM_MODEL, VULNCLAW_SESSION_OUTPUT_DIR, VULNCLAW_SESSION_MAX_ROUNDS, VULNCLAW_SESSION_SHOW_THINKING, VULNCLAW_SAFETY_PYTHON_EXECUTE_ENABLED.",
            ".SH SAFETY",
            "VulnClaw is for authorized testing only. Scope flags and action constraints make allowed boundaries explicit and enforceable, but they do not replace written authorization or a clear rules-of-engagement document.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _topic_roff(topic: ManualTopic) -> list[str]:
    lines = [
        ".SS " + _roff_escape(topic.name),
        _roff_escape(topic.summary),
        ".PP",
        ".B Usage:",
    ]
    for usage_line in topic.usage.splitlines():
        lines.extend([".br", _roff_escape(usage_line)])
    if topic.flags:
        lines.extend([".PP", ".B Arguments and flags:"])
        lines.extend(_roff_pairs(topic.flags))
    if topic.notes:
        lines.extend([".PP", ".B Notes:"])
        for note in topic.notes:
            lines.extend([".IP \\[bu] 2", _roff_escape(note)])
    if topic.examples:
        lines.extend([".PP", ".B Examples:"])
        for example in topic.examples:
            lines.extend([".br", _roff_escape(example)])
    return lines


def _roff_pairs(pairs: tuple[tuple[str, str], ...]) -> list[str]:
    lines: list[str] = []
    for name, description in pairs:
        lines.extend(
            [
                f".TP\n.B {_roff_escape(name)}",
                _roff_escape(description),
            ]
        )
    return lines


def _roff_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("-", "\\-")
