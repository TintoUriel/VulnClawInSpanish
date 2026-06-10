"""/help command — list all slash commands or show detailed help.

Usage::

    /help                  List all commands with usage patterns
    /help <command>        Show detailed help for a specific command
    /command /?            Shorthand for ``/help <command>``
"""

from __future__ import annotations

from rich.markup import escape

from vulnclaw.cli.textui.commands.registry import CommandRegistry
from vulnclaw.i18n import _


class HelpCommand:
    """Display usage information for slash commands."""

    def __init__(self, registry: CommandRegistry) -> None:
        self._registry = registry

    async def run(self, args: str, **context) -> None:
        """Show /help output."""
        chat_pane = context.get("chat_pane")
        if chat_pane is None:
            return

        target = args.strip()

        if target:
            self._show_detail(target, chat_pane)
        else:
            self._show_all(chat_pane)

    # ── List all commands ───────────────────────────────────────

    def _show_all(self, chat_pane) -> None:
        """Show all registered commands with usage."""
        commands = self._registry.list_commands()

        lines = [
            _("tui.command.help.title"),
            "",
        ]
        for cmd in commands:
            name = cmd["name"]
            desc = cmd["description"]
            usage = cmd.get("usage", "")
            if usage:
                lines.append(f"  [cyan]{name}[/]  {desc}")
                lines.append(f"       [dim]{escape(usage)}[/]")
            else:
                lines.append(f"  [cyan]{name}[/]  {desc}")
        lines.append("")
        lines.append(_("tui.command.help.hint_all"))

        chat_pane.add_system_message("\n".join(lines))

    # ── Show detail for one command ─────────────────────────────

    def _show_detail(self, target: str, chat_pane) -> None:
        """Show detailed help for a specific command."""
        cmd = self._registry.get_command(target)

        if cmd is None:
            chat_pane.add_system_message(
                _("tui.command.help.unknown_command", target=escape(target))
            )
            return

        lines = [
            f"[bold cyan]{cmd['name']}[/] — {cmd['description']}",
            "",
        ]

        if cmd.get("usage"):
            lines.append(_("tui.command.help.usage_title"))
            for line in cmd["usage"].split("\n"):
                lines.append(f"  [dim]{escape(line)}[/]")
            lines.append("")

        if cmd.get("detail"):
            lines.append(_("tui.command.help.detail_title"))
            for line in cmd["detail"].split("\n"):
                lines.append(f"  {escape(line)}")
            lines.append("")

        if not cmd.get("usage") and not cmd.get("detail"):
            lines.append(_("tui.command.help.no_detail"))
            lines.append("")

        lines.append(
            _("tui.command.help.tab_hint", name=escape(cmd['name'].lstrip('/')))
        )

        chat_pane.add_system_message("\n".join(lines))
