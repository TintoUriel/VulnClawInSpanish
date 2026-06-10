"""/config command — view and modify configuration.

Usage::

    /config                        Show all configuration
    /config llm                    Show LLM provider settings
    /config llm set provider <name>  Set LLM provider
    /config llm set api_key <key>    Set API key
    /config llm set base_url <url>   Set base URL
    /config llm set model <name>     Set model name
    /config render                 Show current render mode
    /config render markdown        Enable Markdown rendering
    /config render plain           Disable Markdown rendering
    /config popup-mode             Show current popup mode
    /config popup-mode embed       In-terminal panel (default)
    /config popup-mode separate    New terminal window
"""

from __future__ import annotations

from rich.markup import escape

from vulnclaw.config.schema import PROVIDER_PRESETS, LLMProvider
from vulnclaw.config.settings import (
    CONFIG_FILE,
    load_config,
    save_config,
    apply_provider_preset,
)
from vulnclaw.i18n import _


class ConfigCommand:
    """View and modify application configuration."""

    async def run(self, args: str, **context) -> None:
        chat_pane = context.get("chat_pane")
        if chat_pane is None:
            return

        args = args.strip()

        # ── No args: show full config ────────────────────────────
        if not args:
            await self._show_all(chat_pane)
            return

        # ── Subcommand: llm ──────────────────────────────────────
        if args.startswith("llm"):
            await self._handle_llm(args[3:].strip(), chat_pane)
            return

        # ── Subcommand: render ───────────────────────────────────
        if args.startswith("render"):
            await self._handle_render(args[6:].strip(), chat_pane)
            return

        # ── Subcommand: popup-mode ──────────────────────────────
        if args.startswith("popup-mode") or args == "popup":
            await self._handle_popup_mode(args.split(maxsplit=1)[-1], chat_pane)
            return

        # ── Unknown subcommand ───────────────────────────────────
        chat_pane.add_system_message(
            _(
                "tui.command.config.unknown_subcommand",
                args=escape(args),
            )
        )

    # ──────────────────────────────────────────────────────────────
    #  显示
    # ──────────────────────────────────────────────────────────────

    async def _show_all(self, chat_pane) -> None:
        """Show full configuration summary."""
        cfg = load_config()
        llm = cfg.llm

        provider_label = PROVIDER_PRESETS.get(
            LLMProvider(llm.provider), {}
        ).get("label", llm.provider) if llm.provider in (
            p.value for p in LLMProvider
        ) else llm.provider

        api_key_masked = (
            f"{llm.api_key[:8]}...{llm.api_key[-4:]}"
            if len(llm.api_key) > 12
            else "***"
        ) if llm.api_key else _("tui.command.config.unset")

        lines = [
            "[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]",
            _("tui.command.config.title"),
            "[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]",
            "",
            _("tui.command.config.llm_section"),
            f"  [cyan]Provider:[/]     {provider_label}",
            f"  [cyan]API Key:[/]      {api_key_masked}",
            _(
                "tui.command.config.base_url_line",
                base_url=llm.base_url or _("tui.command.config.unset"),
            ),
            _(
                "tui.command.config.model_line",
                model=llm.model or _("tui.command.config.unset"),
            ),
            f"  [cyan]Max Tokens:[/]   {llm.max_tokens}",
            f"  [cyan]Temperature:[/]  {llm.temperature}",
            "",
            _("tui.command.config.session_section"),
            _("tui.command.config.render_mode_line", mode=cfg.session.render_mode),
            _(
                "tui.command.config.popup_mode_line",
                mode=cfg.session.popup_mode,
            ),
            _("tui.command.config.show_thinking_line", status="✓" if cfg.session.show_thinking else "✗"),
            _("tui.command.config.auto_save_line", status="✓" if cfg.session.auto_save else "✗"),
            _("tui.command.config.max_rounds_line", rounds=cfg.session.max_rounds),
            _("tui.command.config.language_line", lang=cfg.session.language),
            _("tui.command.config.output_dir_line", dir=cfg.session.output_dir),
            "",
            _("tui.command.config.safety_section"),
            _("tui.command.config.python_execute_line", status="✓" if cfg.safety.enable_python_execute else "✗"),
            _("tui.command.config.restricted_mode_line", status="✓" if cfg.safety.python_execute_restricted else "✗"),
            "",
            _("tui.command.config.file_section"),
            f"  [dim]{CONFIG_FILE}[/]",
            "",
            _("tui.command.config.edit_hint_llm"),
            _("tui.command.config.edit_hint_render"),
        ]
        chat_pane.add_system_message("\n".join(lines))

    # ──────────────────────────────────────────────────────────────
    #  LLM 子命令
    # ──────────────────────────────────────────────────────────────

    async def _handle_llm(self, args: str, chat_pane) -> None:
        """Handle ``/config llm [...]``."""
        if not args:
            await self._show_llm(chat_pane)
            return

        if args.startswith("set"):
            await self._handle_llm_set(args[3:].strip(), chat_pane)
            return

        chat_pane.add_system_message(
            _("tui.command.config.unknown_llm_sub", args=escape(args))
        )

    async def _show_llm(self, chat_pane) -> None:
        """Show LLM configuration details."""
        cfg = load_config()
        llm = cfg.llm

        provider_label = PROVIDER_PRESETS.get(
            LLMProvider(llm.provider), {}
        ).get("label", llm.provider) if llm.provider in (
            p.value for p in LLMProvider
        ) else llm.provider

        api_key_masked = (
            f"{llm.api_key[:8]}...{llm.api_key[-4:]}"
            if len(llm.api_key) > 12
            else "***"
        ) if llm.api_key else _("tui.command.config.unset")

        # Build provider list
        provider_lines = []
        for prov in LLMProvider:
            if prov == LLMProvider.CUSTOM:
                continue
            preset = PROVIDER_PRESETS.get(prov, {})
            marker = " →" if prov.value == llm.provider else "  "
            provider_lines.append(
                f"  {marker} [cyan]{prov.value:<14}[/] {preset.get('label', ''):<16}"
                f" [dim]{preset.get('default_model', '')}[/]"
            )
        provider_lines.append(
            _(
                "tui.command.config.custom_provider_line",
                marker=" →" if llm.provider == "custom" else "  ",
            )
        )

        lines = [
            "[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━[/]",
            _("tui.command.config.llm_title"),
            "[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━[/]",
            "",
            _("tui.command.config.current_provider_line", label=provider_label),
            _("tui.command.config.api_key_line", key=api_key_masked),
            _("tui.command.config.base_url_line_detailed", url=llm.base_url),
            _("tui.command.config.model_line_detailed", model=llm.model),
            f"[cyan]Max Tokens:[/]    {llm.max_tokens}",
            f"[cyan]Temperature:[/]   {llm.temperature}",
            "",
            _("tui.command.config.available_providers_title"),
            *provider_lines,
            "",
            _("tui.command.config.switch_provider_hint"),
            _("tui.command.config.set_api_key_hint"),
            _("tui.command.config.set_base_url_hint"),
            _("tui.command.config.set_model_hint"),
        ]
        chat_pane.add_system_message("\n".join(lines))

    async def _handle_llm_set(self, args: str, chat_pane) -> None:
        """Handle ``/config llm set <key> <value>``."""
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            chat_pane.add_system_message(
                _("tui.command.config.set_usage")
            )
            return

        key, value = parts[0].lower(), parts[1]

        cfg = load_config()
        valid_keys = {"provider", "api_key", "base_url", "model"}

        if key not in valid_keys:
            chat_pane.add_system_message(
                _(
                    "tui.command.config.unknown_key",
                    key=escape(key),
                    keys=", ".join(sorted(valid_keys)),
                )
            )
            return

        # ── Handle provider ──────────────────────────────────────
        if key == "provider":
            try:
                provider = LLMProvider(value.lower())
            except ValueError:
                available = ", ".join(p.value for p in LLMProvider if p != LLMProvider.CUSTOM)
                chat_pane.add_system_message(
                    _(
                        "tui.command.config.unknown_provider",
                        value=escape(value),
                        available=available,
                    )
                )
                return
            apply_provider_preset(cfg, provider.value)
            save_config(cfg)
            provider_label = PROVIDER_PRESETS.get(provider, {}).get("label", provider.value)
            chat_pane.add_system_message(
                _(
                    "tui.command.config.provider_switched",
                    label=provider_label,
                    base_url=cfg.llm.base_url,
                    model=cfg.llm.model,
                )
            )
            return

        # ── Handle other keys ────────────────────────────────────
        if key == "api_key":
            cfg.llm.api_key = value
            save_config(cfg)
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            chat_pane.add_system_message(
                _("tui.command.config.api_key_updated", masked=masked)
            )
            return

        if key == "base_url":
            cfg.llm.base_url = value
            save_config(cfg)
            chat_pane.add_system_message(
                _("tui.command.config.base_url_updated", value=value)
            )
            return

        if key == "model":
            cfg.llm.model = value
            save_config(cfg)
            chat_pane.add_system_message(
                _("tui.command.config.model_updated", value=value)
            )
            return

    # ──────────────────────────────────────────────────────────────
    #  Render 子命令
    # ──────────────────────────────────────────────────────────────

    async def _handle_render(self, args: str, chat_pane) -> None:
        """Handle ``/config render [...]``."""

        cfg = load_config()

        if not args:
            mode = cfg.session.render_mode
            chat_pane.add_system_message(
                _("tui.command.config.render_status", mode=mode)
            )
            return

        args = args.lower()

        if args not in ("markdown", "plain"):
            chat_pane.add_system_message(
                _("tui.command.config.unknown_render_mode", mode=escape(args))
            )
            return

        # Save config
        cfg.session.render_mode = args
        save_config(cfg)

        # Update all existing AssistantText widgets
        if chat_pane and hasattr(chat_pane, "_messages"):
            updated = 0
            for msg in chat_pane._messages:
                if hasattr(msg, "set_render_mode"):
                    msg.set_render_mode(args)
                    updated += 1
            if updated > 0:
                chat_pane.add_system_message(
                    _(
                        "tui.command.config.render_switched_with_count",
                        mode=args,
                        count=updated,
                    )
                )
            else:
                chat_pane.add_system_message(
                    _("tui.command.config.render_switched", mode=args)
                )
        else:
            chat_pane.add_system_message(
                _("tui.command.config.render_switched", mode=args)
            )

    # ──────────────────────────────────────────────────────────────
    #  Popup mode 子命令
    # ──────────────────────────────────────────────────────────────

    async def _handle_popup_mode(self, args: str, chat_pane) -> None:
        """Handle ``/config popup-mode embed|separate``."""

        cfg = load_config()

        if not args:
            chat_pane.add_system_message(
                _("tui.command.config.popup_status", mode=cfg.session.popup_mode)
            )
            return

        args = args.lower()

        if args == "embed":
            cfg.session.popup_mode = "embed"
            save_config(cfg)
            chat_pane.add_system_message(_("tui.command.config.popup_switched_embed"))
        elif args == "separate":
            cfg.session.popup_mode = "separate"
            save_config(cfg)
            chat_pane.add_system_message(_("tui.command.config.popup_switched_separate"))
        else:
            chat_pane.add_system_message(
                _("tui.command.config.invalid_popup_mode", mode=escape(args))
            )
