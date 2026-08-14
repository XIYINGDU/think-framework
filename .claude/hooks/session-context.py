#!/usr/bin/env python3
"""SessionStart hook: inject the project focus snapshot as orientation only."""
import json
import sys
from pathlib import Path

PREFIX = (
    "Project focus snapshot (orientation only). "
    "Do not start unfinished items unless the user asks to continue, "
    "asks for status, or the request matches a listed item.\n\n"
)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    cwd = Path(data.get("cwd") or ".")
    focus = cwd / ".claude" / "state" / "current-focus.md"
    try:
        body = (
            focus.read_text(errors="ignore")[:4000]
            if focus.exists()
            else "No current-focus.md yet. Create `.claude/state/current-focus.md` at the next handoff."
        )
    except OSError as exc:
        body = f"(session-context: could not read {focus}: {exc})"
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": PREFIX + body,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
