#!/usr/bin/env python3
"""SessionStart hook: initialize metrics for new session.

Clears current session metrics log, resets runtime state, and removes any
stale .godotmaker/current_role left from a previous session. Each gm-* skill
will write its own role on first action.

Displays deployed GodotMaker version.
Never blocks.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import start_session, state


def clear_stale_role() -> None:
    """Remove .godotmaker/current_role so the next skill writes a fresh value."""
    try:
        os.remove(os.path.join(".godotmaker", "current_role"))
    except OSError:
        pass


def read_deployed_version() -> str | None:
    """Read the deployed GodotMaker version from .godotmaker/version."""
    try:
        with open(os.path.join(".godotmaker", "version"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def main():
    start_session()
    state.reset()
    clear_stale_role()

    version = read_deployed_version()
    if version:
        # Inject version info as additional context for the active role
        result = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"[GodotMaker v{version}]",
            }
        }
        print(json.dumps(result))

    sys.exit(0)

if __name__ == "__main__":
    main()
