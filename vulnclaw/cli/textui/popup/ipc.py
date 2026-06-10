"""File-based IPC for popup child process communication.

Uses two separate JSON files to avoid write conflicts:
  - main_to_child.json   — 主 → 子 (initial config + updates)
  - child_to_main.json   — 子 → 主 (saved config + actions)

Both sides poll every ~1 s and detect changes via an incrementing
``version`` field.
"""

from __future__ import annotations

from vulnclaw.i18n import _

import json
import time
from pathlib import Path


class PopupIPC:
    """Bidirectional IPC between main and child processes.

    Parameters
    ----------
    session_dir:
        Directory containing the two IPC JSON files.
    side:
        ``"main"`` (reads child_to_main, writes main_to_child) or
        ``"child"`` (reads main_to_child, writes child_to_main).
    """

    def __init__(self, session_dir: str | Path, side: str) -> None:
        self._dir = Path(session_dir)
        self._side = side

        if side == "main":
            self._write_file = self._dir / "main_to_child.json"
            self._read_file = self._dir / "child_to_main.json"
        else:
            self._write_file = self._dir / "child_to_main.json"
            self._read_file = self._dir / "main_to_child.json"

        self._last_read_version = 0
        self._write_version = 1

    # ── Write ──────────────────────────────────────────────────

    def write(self, data: dict, action: str | None = None) -> None:
        """Write data to the other process.

        Parameters
        ----------
        data:
            Payload dict.
        action:
            Optional action hint: ``"save"``, ``"execute"``, ``"close"``,
            or ``None`` for a passive sync.
        """
        payload = {
            "version": self._write_version,
            "timestamp": time.time(),
            "writer": self._side,
            "data": data,
            "action": action,
        }
        self._write_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._write_version += 1

    # ── Read (returns only if version changed) ─────────────────

    def read(self) -> dict | None:
        """Read data written by the other process.

        Returns
        -------
        The full payload dict (``version``, ``data``, ``action``, …)
        if the file exists and ``version`` has advanced, or ``None``
        if nothing new is available.
        """
        try:
            raw = self._read_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None

        ver = payload.get("version", 0)
        if ver <= self._last_read_version:
            return None

        self._last_read_version = ver
        return payload
