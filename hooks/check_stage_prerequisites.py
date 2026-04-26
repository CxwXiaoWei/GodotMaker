#!/usr/bin/env python3
"""PreToolUse hook (Agent tool): verify role prerequisites before worker dispatch.

Only enforces for roles that dispatch workers:
  - build → requires setup completed + its files present
  - fixgap → requires evaluate completed + evaluation.json present

Other roles (setup, verify, evaluate, accept, finalize) don't dispatch workers
and skip this check.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import (
    record_event, EventType,
    get_current_role, get_completed_roles,
    load_stage_schemas, WORKER_DISPATCH_ROLES,
)


PREREQ_ROLE = {
    "build": "setup",
    "fixgap": "evaluate",
}

# Sanity check: PREREQ_ROLE must cover exactly the worker-dispatching roles.
assert frozenset(PREREQ_ROLE) == WORKER_DISPATCH_ROLES, (
    f"PREREQ_ROLE keys {sorted(PREREQ_ROLE)} must equal "
    f"WORKER_DISPATCH_ROLES {sorted(WORKER_DISPATCH_ROLES)}"
)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if data.get("tool_name") != "Agent":
        sys.exit(0)

    # Only check main agent (the gm-* skill orchestrating dispatch)
    if data.get("agent_id", ""):
        sys.exit(0)

    role = get_current_role()
    prereq = PREREQ_ROLE.get(role)
    if not prereq:
        sys.exit(0)  # No worker-dispatch role active, nothing to enforce

    completed = get_completed_roles()
    issues = []

    if prereq not in completed:
        issues.append(f"Role '{prereq}' has not completed yet — run /gm-{prereq} first")

    schemas = load_stage_schemas()
    if schemas:
        prereq_schema = schemas.get(prereq, {})
        # Inline existence check here (not validate_schema_files) to keep the
        # role-aware "{prereq} output missing: X" message style.
        for filepath in prereq_schema.get("files", []):
            if not os.path.exists(filepath):
                issues.append(f"{prereq} output missing: {filepath}")

    if issues:
        reason = (
            f"Cannot dispatch worker — '{role}' role prerequisites missing:\n"
            + "\n".join(f"  - {m}" for m in issues)
        )
        record_event(EventType.HOOK_BLOCK, hook="check_stage_prerequisites",
                     role=role, missing=issues)
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
        sys.exit(0)

    record_event(EventType.HOOK_ALLOW, hook="check_stage_prerequisites", role=role)


if __name__ == "__main__":
    main()
