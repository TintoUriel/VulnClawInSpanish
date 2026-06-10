"""Cross-platform terminal launcher.

Opens a new terminal window running a given command string.
Supports Windows (cmd.exe) and Linux (common terminal emulators).
"""

from __future__ import annotations

import shlex
import subprocess
import sys


def open_terminal(command: str) -> None:
    """Open a new terminal window executing *command*.

    Parameters
    ----------
    command:
        Shell command to run in the new window, e.g.
        ``"python -m vulnclaw.cli.textui.popup --session-dir /tmp/x"``.
    """
    if sys.platform == "win32":
        _open_windows(command)
    else:
        _open_linux(command)


def _open_windows(command: str) -> None:
    """Windows: use ``start`` with a new console."""
    subprocess.Popen(
        f'start "VulnClaw Popup" {command}',
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def _open_linux(command: str) -> None:
    """Linux: try common terminal emulators in order."""
    terminals = [
        ("x-terminal-emulator", ("-e", command)),
        ("gnome-terminal", ("--", "sh", "-c", command)),
        ("xterm", ("-e", command)),
        ("konsole", ("--hold", "-e", "sh", "-c", command)),
        ("lxterminal", ("-e", command)),
        ("xfce4-terminal", ("-e", command)),
        ("mate-terminal", ("-e", command)),
    ]

    for term, args in terminals:
        try:
            subprocess.Popen([term, *args])
            return
        except FileNotFoundError:
            continue

    print(
        "Warning: could not open a new terminal window. "
        "Install x-terminal-emulator, gnome-terminal, or xterm.",
        file=sys.stderr,
    )
