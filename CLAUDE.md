# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What VulnClaw is

VulnClaw is an AI-powered penetration-testing CLI. A natural-language command
(e.g. "run a pentest on http://target") drives an autonomous LLM agent loop
through **Recon → Vulnerability Discovery → Exploitation → Reporting**, using
tool calling (nmap, `python_execute`, crypto/encode helpers, MCP servers) plus
a library of markdown "skills". It ships a Typer CLI, a Textual TUI, and an
optional FastAPI + React Web UI. The backend is Python 3.10+; the frontend is
React 18 + Vite + TypeScript.

Any LLM with an OpenAI-compatible API works — the config layer ships presets
for 13+ providers (OpenAI, Anthropic, DeepSeek, MiniMax, Zhipu, Moonshot, Qwen,
etc.). This is an authorized-use security tool; keep capability descriptions in
docs honest (see the MCP / sandbox caveats below).

## Commands

Development is driven through the `Makefile` (targets wrap Python/npm):

```bash
make install          # pip install -e ".[dev,web,pdf]" + npm install in frontend/
make test             # python -m pytest  (backend suite)
make lint             # python -m ruff check .
make build            # build Python wheel/sdist + frontend production bundle
make dev-web          # start the frontend Vite dev server
make release-preflight # run scripts/release_preflight.py
```

Common direct invocations:

```bash
pytest                                    # full backend suite (asyncio_mode=auto)
pytest tests/test_agent.py                # one file
pytest tests/test_agent.py::TestX::test_y # one test
pytest -q                                 # quiet (matches CI)
ruff check vulnclaw tests                 # lint (matches CI)

# Frontend (run inside frontend/)
npm run dev        # Vite dev server
npm run build      # tsc -b && vite build
npx tsc -b         # typecheck only (matches CI)
```

**CI** (`.github/workflows/ci.yml`) runs on Ubuntu + Windows across Python
3.10–3.13: `ruff check vulnclaw tests`, `npx tsc -b`, and `pytest -q`. Match
these locally before pushing.

**Before a release-affecting change**, run the preflight — it verifies
`pyproject.toml`/`vulnclaw.__version__` version agreement, backend pytest,
frontend `tsc -b`, and (with `--build`) dist artifacts:

```bash
python scripts/release_preflight.py
python scripts/release_preflight.py --build
```

### Tests run in a project-local sandbox

`conftest.py` redirects config and temp dirs into `tests/.test-tmp/` (it sets
`VULNCLAW_CONFIG_DIR`, `TMPDIR`, and overrides the `tmp_path` fixture) so tests
never touch `~/.vulnclaw` or the system temp. Don't hard-code absolute temp
paths in tests — use the provided `tmp_path` fixture.

## Architecture

The core insight: `AgentCore` (`vulnclaw/agent/core.py`) is deliberately a **thin
coordination shell**. Real behavior lives in sibling modules under
`vulnclaw/agent/`. When changing agent behavior, edit the relevant helper module
rather than growing `core.py` — the same applies to shared task flow and Web
logic (see "Where things go" below).

### The agent loop (`vulnclaw/agent/`)

`AgentCore` wires together many single-responsibility modules:

- `loop_controller.py` — the `auto_pentest` / `persistent_pentest` main loops
  (persistent = up to 100 rounds/cycle × 10 cycles, auto-reporting each cycle).
- `llm_client.py` — LLM calls, retry/failover across a key pool, streaming,
  tool-result summarization.
- `tool_call_manager.py` — tool-call dedup, execution, result packaging.
- `builtin_tools.py` — the built-in tools the LLM can call: `python_execute`,
  `nmap_scan`, MCP bridging, plus scan-target validation and
  `BLOCKED_PATTERNS` / `RESERVED_IP_RANGES` safety gates.
- `context.py` — `SessionState`, findings, steps, `PentestPhase`,
  `TaskConstraints` (the session/lifecycle state model).
- `system_prompt.py` / `prompt_context.py` / `prompts.py` — dynamic system
  prompt assembly and per-round context.
- `input_analysis.py` — extract target, phase, and vuln hints from NL input.
- `anti_loop.py` — anti-infinite-loop, failed-target tracking, attack-path
  detection. `reflexion.py` / `reasoning_state.py` add self-correction.
- `finding_parser.py` — finding extraction, evidence grading, lifecycle bucketing.
- `skill_context.py` / `kb_context.py` — inject skill and knowledge-base context.
- `ctf_mode.py`, `parallel_agents.py`, `team.py`, `recon_tracker.py` — CTF flag
  handling, parallel sub-agents, multi-role teams, recon-dimension coverage.

### Shared task orchestration

`vulnclaw/orchestrator.py` (`run_agent_task`) is the **restore → run → save →
summarize** flow shared by CLI and Web. `vulnclaw/repl_runner.py` is the REPL's
single-shot helper. If a behavior needs to appear in both CLI and Web, converge
it here instead of duplicating it in `cli/main.py` and `web/services/`.

### CLI & TUI (`vulnclaw/cli/`)

`main.py` (~3k lines) holds all Typer commands: `run`, `persistent`, `recon`,
`scan`, `exploit`, `report`, `repl`, `config`, `init`, `doctor`, `tui`, `web`,
`network-scan`, plus `config`, `kb`, `target-state`, and `plugins` sub-apps. It
is the entry/argument/output layer — keep core pentest logic out of it.
`vulnclaw` with no args opens the classic REPL; `vulnclaw tui` opens the TUI.

The TUI is split: `tui.py` holds data classes, Rich dashboard rendering, color
constants, and the `SLASH_COMMANDS` registry; `tui_textual.py` is the Textual
app (dashboard screen, command palette, secondary popups, prompt state machine,
in-TUI subprocess execution). Slash-command handlers register via
`@_register_handler(...)` and return `"quit"` / `"launch"` / `None`.

### Other subsystems

- `config/` — `schema.py` (Pydantic models, `LLMProvider` enum + `PROVIDER_PRESETS`)
  and `settings.py` (load/save, env-var overrides, directory paths). Don't parse
  config ad hoc in business logic.
- `mcp/` — `registry.py` (service state/health/attach/tool registration),
  `lifecycle.py` (attach/probe/call/degrade), `router.py` (NL intent → tool
  suggestion). **Reality check:** `fetch`/`memory` run locally;
  `chrome-devtools`/`burp` have real stdio-attach skeletons; most other MCP
  services still degrade to structured placeholders. Keep docs matched to this.
- `skills/` — markdown-driven pentest playbooks in two formats: **flat**
  (`skills/core/*.md`, single file) and **directory** (`skills/specialized/
  <name>/SKILL.md` + optional `references/`). `dispatcher.py` routes NL intent
  to skills via `SKILL_INTENT_MAP`; `loader.py` loads both formats and serves
  `load_skill_reference`. New/changed skills should update `tests/test_skills.py`.
- `intel/` — attack/CVE/OSINT/topology/compliance/remediation/findings analysis
  modules (mirrored by `tests/intel/`).
- `report/` — `generator.py` is the main entry (feeds both target-state and
  persistent-cycle reports); also filtering, PoC building, verification,
  optional PDF export (needs the `pdf` extra).
- `target_state/` — cross-command persistence for a target: snapshots, preview,
  diff, rollback, resume plans. This is how "same target across commands shares
  progress" works; don't reimplement it in `core.py` or the Web layer.
- `plugins/` — vulnerability-detection plugin runtime (`base.py`, `registry.py`,
  `runtime.py`, `web/` built-in plugins).
- `kb/` — knowledge-base store/retriever/updater (optional `kb` extra pulls in
  chromadb; degrades gracefully when unavailable).
- `web/` — FastAPI backend: `app.py` (routes + serves the built frontend),
  `schemas.py` (request/response models — the frontend contract), `task_manager.py`,
  `stream.py` (SSE), `services/` (config/report/target/task/MCP service layer).
  Put logic in `services/`, not route bodies; reuse the agent/target_state/report
  trunk; never hand secrets to the frontend.
- `frontend/` — React 18 + Vite + TanStack Query. Pages under `src/pages/`,
  API bindings in `src/api/`, query hooks in `src/hooks/`, shared types in
  `src/types/`. Keep types in sync with `vulnclaw/web/schemas.py`.

## Conventions

- **Ruff** is the linter/formatter: line-length 100, `target-version = py310`,
  rules `E/F/I/W`, `E501` ignored. Run `ruff check .`.
- **Version source of truth** is `pyproject.toml`; `vulnclaw/__init__.py` is the
  fallback. Keep them in sync (preflight enforces this).
- **Runtime state** lives under `VULNCLAW_CONFIG_DIR` (default `~/.vulnclaw`):
  `config.yaml`, `sessions/`, `targets/`, `kb/`, `skills/`, `web_tasks.json`,
  `python_execute_audit.jsonl`.
- **Config precedence**: env vars prefixed `VULNCLAW_` (e.g.
  `VULNCLAW_LLM_API_KEY`, `VULNCLAW_LLM_BASE_URL`, `VULNCLAW_LLM_MODEL`) override
  the config file. Note: setting `VULNCLAW_LLM_PROVIDER` alone is only a label
  and does **not** auto-fill base_url/model (unlike the interactive
  `vulnclaw config provider` command) — set base_url and model explicitly.
- **`python_execute` is experimental, not a hardened sandbox.** Treat it as a
  high-risk capability; the built-in tools enforce target validation,
  `BLOCKED_PATTERNS`, and reserved-IP blocking as guardrails.
- When adding behavior, keep documentation (README, README_EN) honest about
  what's actually implemented — MCP status, sandbox limits, and safety
  boundaries are the areas most prone to overstating capability.

Full module-location guidance lives in `CONTRIBUTING.md` (in Chinese); it maps
"I want to change X" to the right module and is worth consulting for anything
non-trivial.
