"""/load command — load chat history for a target."""

from __future__ import annotations

from vulnclaw.i18n import _


class LoadCommand:
    """Load chat history for a specific target."""

    async def run(self, args: str, **context) -> None:
        chat_pane = context.get("chat_pane")
        if chat_pane is None:
            return

        target = args.strip()
        if not target:
            # Show available targets
            from vulnclaw.cli.textui.services.history import get_history_store
            store = get_history_store()
            targets = store.list_targets()

            if not targets:
                chat_pane.add_system_message(_("tui.command.load.no_history"))
                return

            lines = [
                _("tui.command.load.available"),
                "",
            ]
            for t, ts in targets:
                lines.append(f"  [cyan]{t}[/]  — {ts}")
            lines.append("")
            lines.append(_("tui.command.load.hint"))
            chat_pane.add_system_message("\n".join(lines))
        else:
            chat_pane._load_history(target)
