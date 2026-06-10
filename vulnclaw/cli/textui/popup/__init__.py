"""Popup child process — runs ``python -m vulnclaw.cli.textui.popup``.

Launched by the main TUI when ``popup_mode == "separate"`` to display
scan configuration in an independent terminal window, communicating
via file IPC.
"""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="VulnClaw popup child process")
    parser.add_argument(
        "--session-dir", required=True,
        help="IPC session directory path",
    )
    parser.add_argument(
        "--type", default="sc",
        choices=["sc"],
        help="Type of popup (currently only 'sc')",
    )
    args, _ = parser.parse_known_args()

    if args.type == "sc":
        from vulnclaw.cli.textui.popup.sc_screen import PopupSCApp

        app = PopupSCApp(args.session_dir)
        app.run()
    else:
        print(f"Unknown popup type: {args.type}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
