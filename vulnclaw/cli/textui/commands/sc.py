"""/sc command — scan configuration (floating modal or quick args).

Usage::

    /sc                        Open scan configuration modal
    /sc show                   Display current config in chat
    /sc run                    Execute scan with current config
    /sc --key value ...        Quick-set config values
"""

from __future__ import annotations

import asyncio
import shlex

from vulnclaw.i18n import _


class ScanConfigCommand:
    """Manage scan configuration via modal, display, or quick args."""

    async def run(self, args: str, **context) -> None:
        """Route the command: modal vs subcommand vs quick args."""
        chat_pane = context.get("chat_pane")
        if chat_pane is None:
            return

        if not args.strip():
            # No args → open modal
            await self._open_modal(chat_pane)
            return

        # Parse subcommand or quick args
        try:
            parts = shlex.split(args)
        except ValueError:
            chat_pane.add_system_message(_("tui.command.sc.parse_error", args=args))
            return

        first = parts[0]

        if first == "show":
            self._show_config(chat_pane)
        elif first == "run":
            await self._run_task(chat_pane)
        elif first.startswith("--"):
            self._handle_quick_args(args, chat_pane)
        else:
            chat_pane.add_system_message(
                _("tui.command.sc.unknown_subcommand", first=first)
            )

    # ── Open config (embed or separate) ────────────────────────

    async def _open_modal(self, chat_pane) -> None:
        """Open scan configuration — embed (in-terminal) or separate window."""
        popup_mode = chat_pane._state.config.session.popup_mode

        if popup_mode == "separate":
            await self._open_separate(chat_pane)
        else:
            await self._open_embed(chat_pane)

    async def _open_embed(self, chat_pane) -> None:
        """Push the ScanConfigScreen modal in-terminal."""
        from vulnclaw.cli.textui.components.scan_config_screen import ScanConfigScreen

        screen = ScanConfigScreen(chat_pane._state.to_dict())
        chat_pane.add_system_message(_("tui.command.sc.opening_panel"))
        result = await chat_pane.app.push_screen_wait(screen)

        if result:
            await self._apply_and_maybe_execute(chat_pane, result)

        chat_pane._focus_input()

    async def _open_separate(self, chat_pane) -> None:
        """Open scan configuration in a new terminal window (file IPC)."""
        import json
        import tempfile
        import uuid
        from pathlib import Path

        session_id = uuid.uuid4().hex[:12]
        session_dir = Path(tempfile.gettempdir()) / "vulnclaw_popup" / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Write initial config for the child process
        main_file = session_dir / "main_to_child.json"
        main_file.write_text(
            json.dumps({
                "version": 1,
                "data": chat_pane._state.to_dict(),
                "action": None,
            }),
            encoding="utf-8",
        )

        from vulnclaw.cli.textui.popup.launcher import open_terminal

        python = "python"
        open_terminal(
            f'{python} -m vulnclaw.cli.textui.popup --session-dir "{session_dir}"',
        )

        chat_pane.add_system_message(
            _("tui.command.sc.opened_separate", session_id=session_id)
        )

        # Poll for result from child process
        child_file = session_dir / "child_to_main.json"
        last_version = 0
        max_attempts = 600  # 10 minutes timeout
        for _ in range(max_attempts):
            await asyncio.sleep(1)
            try:
                raw = child_file.read_text(encoding="utf-8")
                data = json.loads(raw)
                if data.get("version", 0) > last_version:
                    last_version = data["version"]
                    if data.get("action") in ("save", "execute"):
                        result = data.get("data", {})
                        await self._apply_and_maybe_execute(
                            chat_pane, result,
                            execute=data["action"] == "execute",
                        )
                        break
                    elif data.get("action") == "close":
                        break
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        else:
            chat_pane.add_system_message(_("tui.command.sc.timeout_close"))

        # Cleanup
        import shutil
        try:
            shutil.rmtree(session_dir)
        except Exception:
            pass

        chat_pane._focus_input()

    @staticmethod
    async def _apply_and_maybe_execute(
        chat_pane, result: dict, *, execute: bool = False,
    ) -> None:
        """Apply config and optionally start the scan task."""
        chat_pane._apply_sc_config(result)
        if execute or result.get("_execute"):
            target = result.get("target", "")
            msg = (
                _("tui.command.sc.start_pentest", target=target)
                if target
                else _("tui.command.sc.start_scan")
            )
            chat_pane.add_user_message(msg)
            await chat_pane._handle_chat(msg)
        else:
            chat_pane.add_system_message(_("tui.command.sc.config_saved"))

    # ── show ────────────────────────────────────────────────────

    @staticmethod
    def _show_config(chat_pane) -> None:
        """Display current scan config in the chat area."""
        state = chat_pane._state

        allow_str = (
            ", ".join(state.allow_actions)
            if state.allow_actions
            else _("tui.command.sc.unrestricted")
        )
        block_str = (
            ", ".join(state.block_actions)
            if state.block_actions
            else _("tui.command.sc.unrestricted")
        )

        lines = [
            "[bold]━━━━━━━━━━━━━━━━━━━━━━[/]",
            _("tui.command.sc.config_title"),
            "[bold]━━━━━━━━━━━━━━━━━━━━━━[/]",
            "",
            _("tui.command.sc.target_line", target=state.target or _("tui.command.sc.target_unset")),
            _("tui.command.sc.mode_line", mode=state.mode),
            "",
            _("tui.command.sc.boundary_section"),
            _("tui.command.sc.only_host_line", host=state.only_host or "—"),
            _("tui.command.sc.only_port_line", port=state.only_port or "—"),
            _("tui.command.sc.only_path_line", path=state.only_path or "—"),
            _("tui.command.sc.blocked_host_line", host=state.blocked_host or "—"),
            _("tui.command.sc.blocked_path_line", path=state.blocked_path or "—"),
            "",
            _("tui.command.sc.action_limits_section"),
            _("tui.command.sc.allow_actions_line", actions=allow_str),
            _("tui.command.sc.block_actions_line", actions=block_str),
            "",
            _("tui.command.sc.edit_hint"),
            _("tui.command.sc.run_hint"),
        ]
        chat_pane.add_system_message("\n".join(lines))

    # ── run ─────────────────────────────────────────────────────

    @staticmethod
    async def _run_task(chat_pane) -> None:
        """Execute scan task with current configuration."""
        target = chat_pane._state.target
        if not target:
            chat_pane.add_system_message(
                _("tui.command.sc.no_target")
            )
            return
        msg = _("tui.command.sc.running_pentest", target=target)
        chat_pane.add_user_message(msg)
        await chat_pane._handle_chat(msg)

    # ── Quick args ──────────────────────────────────────────────

    @staticmethod
    def _handle_quick_args(args: str, chat_pane) -> None:
        """Parse --key value pairs and apply directly."""
        try:
            tokens = shlex.split(args)
        except ValueError:
            chat_pane.add_system_message(_("tui.command.sc.parse_error", args=args))
            return

        config: dict[str, str] = {}
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.startswith("--"):
                key = token[2:].replace("-", "_")
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                    config[key] = tokens[i + 1]
                    i += 2
                else:
                    config[key] = ""
                    i += 1
            else:
                i += 1

        if not config:
            chat_pane.add_system_message(_("tui.command.sc.invalid_args", args=args))
            chat_pane.add_system_message(
                _("tui.command.sc.quick_usage")
            )
            return

        chat_pane._state.update_from_dict(config)
        chat_pane.add_system_message(_("tui.command.sc.config_updated"))
