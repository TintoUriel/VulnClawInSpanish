"""Status bar widget showing target, mode, and model status."""

from __future__ import annotations

from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from vulnclaw.i18n import _


class StatusBar(Static):
    """Status bar displaying target, mode, and model status in a row."""

    DEFAULT_CSS = """
    StatusBar {
        height: 2;
        margin: 0 1;
        background: $panel;
    }
    """

    def __init__(
        self,
        target: str = "",
        mode: str = "standard",
        model: str = "",
        provider: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._target = target
        self._mode = mode
        self._model = model
        self._provider = provider

    def update_target(self, target: str) -> None:
        self._target = target
        self._refresh()

    def update_mode(self, mode: str) -> None:
        self._mode = mode
        self._refresh()

    def update_model(self, model: str, provider: str = "") -> None:
        self._model = model
        if provider:
            self._provider = provider
        self._refresh()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        table = Table.grid(padding=(0, 2), expand=True)

        target_text = Text(self._target or "未设置", style="bold" if self._target else "dim")
        mode_styles = {
            "quick": "bold yellow",
            "standard": "bold green",
            "deep": "bold",
            "continuous": "bold",
        }
        mode_style = mode_styles.get(self._mode, "white")
        mode_text = Text(self._mode.upper(), style=mode_style)

        model_label = self._model or _("tui.widget.status_bar.unknown_model")
        provider_label = f"[{self._provider}] " if self._provider else ""
        model_text = Text(f"{provider_label}{model_label}", style="bold" if self._model else "dim")

        table.add_column("Target", ratio=3)
        table.add_column("Mode", ratio=2)
        table.add_column("Model", ratio=3)

        table.add_row(target_text, mode_text, model_text)
        self.update(table)
