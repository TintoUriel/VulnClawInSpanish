"""Scan configuration modal screen — launched by /sc.

Provides a floating modal panel for configuring scan targets,
boundary constraints, mode, and action filters.

Supports responsive sizing and optional dark overlay background.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet, Static

from vulnclaw.i18n import _
from vulnclaw.cli.tui import MODES


class ScanConfigScreen(ModalScreen[dict[str, Any] | None]):
    """Floating modal for scan configuration.

    Returns a dict of config values when the user clicks
    "执行任务" or "保存配置", or ``None`` when cancelled.

    Parameters
    ----------
    initial:
        Initial form values keyed by field name.
    """

    BINDINGS = [
        ("escape", "dismiss_modal", _("tui.component.scan_config.close_button")),
    ]

    DEFAULT_CSS = """
    ScanConfigScreen {
        align: center middle;
    }

    #sc-panel {
        min-width: 40;
        width: 80%;
        max-width: 80;
        height: auto;
        max-height: 90%;
        border: thick $secondary;
        background: $surface;
        padding: 1 2;
    }

    #sc-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }

    #sc-body {
        height: auto;
        max-height: 60vh;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 0 1;
        scrollbar-gutter: stable;
    }

    .sc-section {
        height: auto;
        margin: 1 0;
    }

    .sc-section-title {
        text-style: bold;
        color: $text;
        margin: 0 0 1 0;
    }

    .sc-section > Input {
        margin: 0 0 1 0;
        width: 1fr;
    }

    #sc-mode {
        height: auto;
        margin: 0 0 1 0;
    }

    #sc-actions {
        height: auto;
        margin-top: 1;
        align: center middle;
        padding: 0 1;
    }

    #sc-actions > Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._initial = initial or {}

    def action_dismiss_modal(self) -> None:
        """Close the config modal (ESC)."""
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        with Vertical(id="sc-panel"):
            yield Static(_("tui.component.scan_config.title"), id="sc-title")

            with Vertical(id="sc-body"):
                # ── Target ──
                with Vertical(classes="sc-section"):
                    yield Static(_("tui.component.scan_config.target_section"), classes="sc-section-title")
                    yield Input(
                        value=self._initial.get("target", ""),
                        placeholder=_("tui.component.scan_config.target_placeholder"),
                        id="sc-target",
                    )

                # ── Boundary constraints ──
                with Vertical(classes="sc-section"):
                    yield Static(_("tui.component.scan_config.boundary_section"), classes="sc-section-title")
                    yield Input(
                        value=self._initial.get("only_host", ""),
                        placeholder=_("tui.component.scan_config.only_host_placeholder"),
                        id="sc-only-host",
                    )
                    yield Input(
                        value=self._initial.get("only_port", ""),
                        placeholder=_("tui.component.scan_config.only_port_placeholder"),
                        id="sc-only-port",
                    )
                    yield Input(
                        value=self._initial.get("only_path", ""),
                        placeholder=_("tui.component.scan_config.only_path_placeholder"),
                        id="sc-only-path",
                    )
                    yield Input(
                        value=self._initial.get("blocked_host", ""),
                        placeholder=_("tui.component.scan_config.blocked_host_placeholder"),
                        id="sc-blocked-host",
                    )
                    yield Input(
                        value=self._initial.get("blocked_path", ""),
                        placeholder=_("tui.component.scan_config.blocked_path_placeholder"),
                        id="sc-blocked-path",
                    )

                # ── Actions ──
                with Vertical(classes="sc-section"):
                    yield Static(_("tui.component.scan_config.actions_section"), classes="sc-section-title")
                    yield Input(
                        value=self._initial.get("allow_actions", ""),
                        placeholder=_("tui.component.scan_config.allow_actions_placeholder"),
                        id="sc-allow-actions",
                    )
                    yield Input(
                        value=self._initial.get("block_actions", ""),
                        placeholder=_("tui.component.scan_config.block_actions_placeholder"),
                        id="sc-block-actions",
                    )

                # ── Mode ──
                with Vertical(classes="sc-section"):
                    yield Static(_("tui.component.scan_config.mode_section"), classes="sc-section-title")
                    current_mode = self._initial.get("mode", "standard")
                    yield RadioSet(
                        *[
                            RadioButton(
                                f"{m.label} - {m.description}",
                                value=k == current_mode,
                            )
                            for k, m in MODES.items()
                        ],
                        id="sc-mode",
                    )

            # ── Buttons ──
            with Horizontal(id="sc-actions"):
                yield Button(_("tui.component.scan_config.execute_button"), id="sc-execute", variant="primary")
                yield Button(_("tui.component.scan_config.save_button"), id="sc-save")
                yield Button(_("tui.component.scan_config.close_button"), id="sc-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        btn_id = event.button.id

        if btn_id == "sc-close":
            self.dismiss(None)
            return

        try:
            config = self._collect_config()
        except Exception:
            self.dismiss(None)
            return

        if btn_id == "sc-execute":
            config["_execute"] = True
            self.dismiss(config)
        elif btn_id == "sc-save":
            self.dismiss(config)

    def _collect_config(self) -> dict[str, Any]:
        """Read all form values into a dict."""
        return {
            "target": self._get_input("sc-target"),
            "only_host": self._get_input("sc-only-host"),
            "only_port": self._get_input("sc-only-port"),
            "only_path": self._get_input("sc-only-path"),
            "blocked_host": self._get_input("sc-blocked-host"),
            "blocked_path": self._get_input("sc-blocked-path"),
            "allow_actions": self._get_input("sc-allow-actions"),
            "block_actions": self._get_input("sc-block-actions"),
            "mode": self._get_mode(),
        }

    def _get_input(self, input_id: str) -> str:
        try:
            return self.query_one(f"#{input_id}", Input).value.strip()
        except Exception:
            return ""

    def _get_mode(self) -> str:
        try:
            mode_set = self.query_one("#sc-mode", RadioSet)
            pressed = mode_set.pressed_index
            for i, btn in enumerate(mode_set.children):
                if isinstance(btn, RadioButton) and i == pressed:
                    label = str(btn.label).split(" - ")[0]
                    for key, m in MODES.items():
                        if m.label == label:
                            return key
        except Exception:
            pass
        return self._initial.get("mode", "standard")
