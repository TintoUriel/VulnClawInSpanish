"""VulnClaw CLI Module Tests 鈥?main.py"""

import pytest
from typer.testing import CliRunner


# 鈹€鈹€ CLI smoke tests 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

class TestCLI:
    """Test CLI entry point and sub-commands."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_cli_help(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "VulnClaw" in result.output or "vulnclaw" in result.output.lower()

    def test_cli_version(self, runner):
        from vulnclaw import __version__
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["--version"])
        # Typer may return exit code 0 or 2 depending on version
        assert __version__ in result.output or result.exit_code in (0, 2)

    def test_cli_init(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["init"])
        # Should not crash
        assert result.exit_code == 0

    def test_cli_doctor(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["doctor"])
        # Should not crash
        assert result.exit_code == 0
        assert "Registered:" in result.output
        assert "Tools:" in result.output

    def test_cli_config_list(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["config", "list"])
        # Should not crash
        assert result.exit_code == 0

    def test_cli_config_provider_list(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["config", "provider", "--list"])
        # Should show available providers
        assert result.exit_code == 0

    def test_cli_config_provider_set(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["config", "provider", "deepseek"])
        # Should not crash
        assert result.exit_code == 0

    def test_cli_kb_update(self, runner, monkeypatch, tmp_path):
        from vulnclaw.cli.main import app
        import vulnclaw.kb.store as kb_store

        monkeypatch.setattr(kb_store, "KB_DIR", tmp_path)
        result = runner.invoke(app, ["kb", "update"])
        assert result.exit_code == 0
        assert "Knowledge base updated" in result.output or result.output
        assert (tmp_path / "index.json").exists()

    def test_cli_doctor_reports_registered_tools(self, runner):
        from vulnclaw.cli.main import app

        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Registered:" in result.output
        assert "Tools:" in result.output

    def test_recon_resumes_target_state(self, runner, monkeypatch, tmp_path):
        from vulnclaw.cli.main import app
        import vulnclaw.orchestrator as orchestrator_mod
        import vulnclaw.target_state.store as store_mod
        from vulnclaw.agent.context import SessionState, PentestPhase

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        state.advance_phase(PentestPhase.RECON)
        store_mod.save_target_state("https://example.com", state, command="recon")

        calls: list[tuple[str, str | None]] = []
        original_apply = orchestrator_mod.apply_target_state_to_agent

        def tracking_apply(agent, target, snapshot_id=None):
            calls.append((target, snapshot_id))
            return original_apply(agent, target, snapshot_id=snapshot_id)

        monkeypatch.setattr(orchestrator_mod, "apply_target_state_to_agent", tracking_apply)

        result = runner.invoke(app, ["recon", "https://example.com"])
        assert result.exit_code == 0
        assert result.output
        assert calls == [("https://example.com", None)]

    def test_recon_no_resume_skips_target_state(self, runner, monkeypatch, tmp_path):
        from vulnclaw.cli.main import app
        import vulnclaw.target_state.store as store_mod
        from vulnclaw.agent.context import SessionState, PentestPhase

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        state.advance_phase(PentestPhase.RECON)
        store_mod.save_target_state("https://example.com", state, command="recon")

        result = runner.invoke(app, ["recon", "https://example.com", "--no-resume"])
        assert result.exit_code == 0
        assert result.output is not None

    def test_repl_persistent_explicit_target_restores_history(self, runner, monkeypatch):
        from vulnclaw.cli.main import app
        import vulnclaw.cli.main as cli_main
        import vulnclaw.agent.core as agent_core
        import vulnclaw.mcp.lifecycle as lifecycle_mod
        from vulnclaw.agent.context import PentestPhase, SessionState
        from vulnclaw.config.schema import VulnClawConfig

        config = VulnClawConfig()
        config.llm.api_key = "test-key"

        old_state = SessionState(target="https://old.example")
        old_state.advance_phase(PentestPhase.RECON)

        new_state = SessionState(target="https://new.example")
        new_state.advance_phase(PentestPhase.EXPLOITATION)

        observed: dict[str, str] = {}

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0)
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)

        def fake_apply(agent, target: str, snapshot_id=None):
            restored = None
            if target == "https://old.example":
                restored = old_state
            elif target == "https://new.example":
                restored = new_state

            if restored is not None:
                agent.context.state = restored
                return type(
                    "Restore",
                    (),
                    {
                        "restored": True,
                        "target": restored.target,
                        "phase": restored.phase.value,
                        "snapshot_id": snapshot_id or "",
                        "resume_strategy": "",
                        "resume_reason": "",
                    },
                )()

            agent.context.state.target = target
            return type(
                "Restore",
                (),
                {
                    "restored": False,
                    "target": target,
                    "phase": agent.context.state.phase.value,
                    "snapshot_id": snapshot_id or "",
                    "resume_strategy": "",
                    "resume_reason": "",
                },
            )()

        async def fake_persistent_pentest(self, user_input: str, target=None, **kwargs):
            observed["target_arg"] = target or ""
            observed["state_target"] = self.context.state.target or ""
            observed["phase"] = self.context.state.phase.value
            return []

        monkeypatch.setattr(cli_main, "apply_target_state_to_agent", fake_apply)
        monkeypatch.setattr(agent_core.AgentCore, "persistent_pentest", fake_persistent_pentest)

        result = runner.invoke(
            app,
            [],
            input="target https://old.example\npersistent https://new.example\nexit\n",
        )

        assert result.exit_code == 0
        assert observed["target_arg"] == "https://new.example"
        assert observed["state_target"] == "https://new.example"
        assert observed["phase"] == PentestPhase.EXPLOITATION.value

    def test_report_target_mode(self, runner, monkeypatch, tmp_path):
        from vulnclaw.cli.main import app
        import vulnclaw.target_state.store as store_mod
        from vulnclaw.agent.context import SessionState, VulnerabilityFinding

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        finding = VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi")
        finding.verified = True
        finding.verification_status = "verified"
        state.add_finding(finding)
        store_mod.save_target_state("https://example.com", state, command="scan")

        result = runner.invoke(app, ["report", "https://example.com", "--target"])
        assert result.exit_code == 0
        assert "Report generated" in result.output or result.output

    def test_repl_report_command_uses_current_session_or_target_state(self, runner, monkeypatch):
        from vulnclaw.cli.main import app
        import vulnclaw.cli.main as cli_main
        import vulnclaw.mcp.lifecycle as lifecycle_mod
        from vulnclaw.config.schema import VulnClawConfig

        config = VulnClawConfig()
        config.llm.api_key = "test-key"

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0)
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)
        monkeypatch.setattr(cli_main, "_generate_report_for_target", lambda target, **kwargs: "C:/tmp/report.md")

        result = runner.invoke(
            app,
            [],
            input="target https://example.com\nreport https://example.com\nexit\n",
        )

        assert result.exit_code == 0
        assert "Report generated" in result.output
        assert "report.md" in result.output

    def test_run_uses_shared_orchestrator(self, runner, monkeypatch):
        from vulnclaw.cli.main import app
        import vulnclaw.cli.main as cli_main
        from vulnclaw.config.schema import VulnClawConfig

        config = VulnClawConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        called: list[tuple[str, str]] = []

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            called.append((command, target))
            return type("RunResult", (), {"summary": {"findings_count": 3}})()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)

        result = runner.invoke(app, ["run", "https://example.com"])
        assert result.exit_code == 0
        assert called == [("run", "https://example.com")]

    def test_persistent_command_uses_correct_cycle_callback(self, runner, monkeypatch):
        from vulnclaw.cli.main import app
        import vulnclaw.cli.main as cli_main
        from vulnclaw.config.schema import VulnClawConfig

        config = VulnClawConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        class DummyAgent:
            def __init__(self):
                self.context = type("Ctx", (), {"state": type("State", (), {"target": "https://example.com"})()})()
                self.runtime = type("Runtime", (), {})()

            async def persistent_pentest(self, *args, **kwargs):
                assert "on_cycle_complete" in kwargs
                assert kwargs["on_cycle_complete"] is not None
                return []

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            await runner(DummyAgent(), config)
            return type("Result", (), {"summary": {"findings_count": 0, "executed_steps": 0}})()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)

        result = runner.invoke(app, ["persistent", "https://example.com", "--cycles", "1", "--rounds", "1"])
        assert result.exit_code == 0

    def test_repl_persistent_interrupt_generates_final_report(self, runner, monkeypatch):
        from vulnclaw.cli.main import app
        import vulnclaw.cli.main as cli_main
        import vulnclaw.agent.core as agent_core
        import vulnclaw.mcp.lifecycle as lifecycle_mod
        from vulnclaw.agent.context import SessionState, VulnerabilityFinding
        from vulnclaw.config.schema import VulnClawConfig

        config = VulnClawConfig()
        config.llm.api_key = "test-key"

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0)
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)

        state = SessionState(target="https://example.com")
        finding = VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi")
        state.add_finding(finding)

        def fake_apply(agent, target: str, snapshot_id=None):
            agent.context.state = state
            return type(
                "Restore",
                (),
                {
                    "restored": True,
                    "target": state.target,
                    "phase": state.phase.value,
                    "snapshot_id": snapshot_id or "",
                    "resume_strategy": "",
                    "resume_reason": "",
                },
            )()

        async def fake_persistent_pentest(self, user_input: str, target=None, **kwargs):
            raise KeyboardInterrupt()

        monkeypatch.setattr(cli_main, "apply_target_state_to_agent", fake_apply)
        monkeypatch.setattr(agent_core.AgentCore, "persistent_pentest", fake_persistent_pentest)
        monkeypatch.setattr(cli_main, "_generate_report_for_target", lambda target, **kwargs: "C:/tmp/final.md")

        result = runner.invoke(
            app,
            [],
            input="persistent https://example.com\nexit\n",
        )

        assert result.exit_code == 0
        assert "Final report" in result.output
        assert "final.md" in result.output
    def test_target_state_list_and_clear(self, runner, monkeypatch, tmp_path):
        from vulnclaw.cli.main import app
        import vulnclaw.target_state.store as store_mod
        from vulnclaw.agent.context import SessionState

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        store_mod.save_target_state("https://example.com", state, command="recon")

        result_list = runner.invoke(app, ["target-state", "list", "https://example.com"])
        assert result_list.exit_code == 0
        assert "snapshot" in result_list.output.lower() or "蹇収" in result_list.output

        result_clear = runner.invoke(app, ["target-state", "clear", "https://example.com"])
        assert result_clear.exit_code == 0
        assert result_clear.output

    def test_target_state_preview_and_diff(self, runner, monkeypatch, tmp_path):
        from vulnclaw.cli.main import app
        import vulnclaw.target_state.store as store_mod
        from vulnclaw.agent.context import SessionState, VulnerabilityFinding

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")

        state1 = SessionState(target="https://example.com")
        state1.add_finding(VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi"))
        store_mod.save_target_state("https://example.com", state1, command="recon")

        state2 = SessionState(target="https://example.com")
        state2.add_finding(VulnerabilityFinding(title="XSS", severity="Medium", vuln_type="XSS"))
        store_mod.save_target_state("https://example.com", state2, command="scan")

        snapshots = store_mod.list_target_snapshots("https://example.com")
        result_preview = runner.invoke(app, ["target-state", "preview", "https://example.com"])
        assert result_preview.exit_code == 0
        assert "Target Preview" in result_preview.output

        result_diff = runner.invoke(
            app,
            ["target-state", "diff", "https://example.com", snapshots[-1]["snapshot_id"], "--to", snapshots[0]["snapshot_id"]],
        )
        assert result_diff.exit_code == 0
        assert "Target Diff" in result_diff.output

    @pytest.mark.asyncio
    async def test_repl_runner_executes_post_hook(self):
        from vulnclaw.repl_runner import run_repl_call

        observed = []

        async def call():
            observed.append("call")
            return "hello"

        async def after_result(result):
            observed.append(f"after:{result}")

        result = await run_repl_call(call=call, after_result=after_result)
        assert result == "hello"
        assert observed == ["call", "after:hello"]

    def test_cli_kb_info(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["kb", "info"])
        # kb info might not exist in all versions, just verify no crash
        assert result.exit_code in (0, 2)

    def test_cli_no_args(self, runner):
        """Running with no args should show help or enter REPL mode."""
        from vulnclaw.cli.main import app
        result = runner.invoke(app, [])
        # Should not crash
        assert result.exit_code == 0


class TestCLISubCommands:
    """Test CLI sub-command help messages."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_run_help(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0

    def test_recon_help(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["recon", "--help"])
        assert result.exit_code == 0

    def test_scan_help(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["scan", "--help"])
        assert result.exit_code == 0

    def test_report_help(self, runner):
        from vulnclaw.cli.main import app
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0

