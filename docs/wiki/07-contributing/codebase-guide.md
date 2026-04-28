# Codebase Guide

This page gives a folder-by-folder tour of the GodotMaker repository, with enough depth to orient you before you start editing. For a shorter overview, see [Development setup](development-setup.md). For how all the pieces wire together at runtime, keep reading.

## Repository layout

```
GodotMaker/
├── hooks/                   8 hook scripts + hooks/metrics/ subsystem
├── agents/                  5 sub-agent definitions (worker, verifier, reviewer, analyst, gdd-auditor)
├── skills/
│   ├── core/                Role skills + supporting skills + _shared/
│   └── reviewer/            8 reviewer skills (gotchas.md + checklist.md each)
├── tools/                   publish.py, check_env.py, check_project.py, asset_gen.py, migrate.py
├── config/                  settings.json, stage_schemas.json, addon_versions.json
├── templates/               Document templates (GDD, PLAN, STRUCTURE, SCENES, ASSETS, GAP, MEMORY, TOC)
├── tests/                   ~320 unit tests for hooks and tools
├── docs/                    versioning.md, hooks.md, wiki/, update/, contributing/, reference/
├── shell/                   publish.sh / publish.ps1, report.sh / report.bat
├── migrations/              Per-version-jump migration scripts
├── VERSION                  Semantic version source of truth
└── CHANGELOG.md             Per-release notes
```

---

## hooks/

Eight Python scripts enforcing pipeline rules. Each script reads a JSON payload from `sys.stdin`, decides whether to allow or block the action, and writes a JSON response to stdout (or exits 0 silently for a quiet allow).

Scripts and the events they handle:

| Script | Event | Blocks? |
|--------|-------|---------|
| `session_start.py` | SessionStart | No |
| `check_file_permissions.py` | PreToolUse (Write\|Edit) | Yes |
| `stage_reminder.py` | PreToolUse (Write\|Edit) | Yes |
| `check_stage_prerequisites.py` | PreToolUse (Agent) | Yes |
| `check_asset_access.py` | PreToolUse (Read) | Yes |
| `log_subagent.py` | SubagentStart | No |
| `on_subagent_stop.py` | SubagentStop | Delegates |
| `check_worker_report.py` | Called by on_subagent_stop.py | Yes |
| `check_completion.py` | Stop | Yes |

Hook registration (which script fires on which event) lives in `config/settings.json` and is deployed into the target project as `.claude/settings.json`.

### hooks/metrics/

A small subsystem for recording what happened during a session. Hooks call `record_event()` to append a JSON line to `.godotmaker/metrics_current.jsonl` (current session) and `.godotmaker/metrics_total.jsonl` (lifetime). The `state.py` module manages mutable per-session counters (block counts, etc.) in `.godotmaker/state.json`. `session_start.py` resets both on every new session.

For details on writing hooks and using the metrics API, see [Writing a hook](writing-a-hook.md).

---

## agents/

Sub-agent definitions, one Markdown file per agent. Each file has YAML front-matter (`name`, `description`, `model`) and a system-prompt body. `publish.py` deploys them to `<target>/.claude/agents/`, where Claude Code picks them up by `subagent_type`.

| Agent | Role | Dispatched by |
|-------|------|---------------|
| `worker.md` | Implements one task end-to-end (code + unit tests) | `/gm-build`, `/gm-fixgap` |
| `verifier.md` | Mechanically checks a worker's output (build, tests, file presence) | `/gm-build`, `/gm-fixgap` |
| `reviewer.md` | Reads code against `skills/reviewer/<domain>` checklists and reports issues | `/gm-build`, `/gm-fixgap` |
| `analyst.md` | Analyses user-provided assets and produces a manifest | `/gm-asset` |
| `gdd-auditor.md` | Independently audits a draft GDD against a 9-category checklist and returns 5–8 follow-up questions per pass | `game-planner` (Rounds 6 + 7) |

The dispatch protocols (call format and brief templates) live in `skills/core/_shared/{worker,verifier,reviewer,analyst}-dispatch.md`. `gdd-auditor` is invoked inline from `skills/core/game-planner/SKILL.md`.

---

## skills/core/

Role skills and supporting skills, one directory per skill. Each directory contains at minimum a `SKILL.md` with YAML front-matter and the prompt body.

**Role skills (9):** `gm-scaffold`, `gm-gdd`, `gm-asset`, `gm-build`, `gm-verify`, `gm-evaluate`, `gm-fixgap`, `gm-accept`, `gm-finalize`. These map 1:1 to the `/gm-*` slash commands. Each role skill writes its role name to `.godotmaker/current_role` as its first action, which is what `check_file_permissions.py` reads to enforce write rules.

**Supporting skills (12):** `game-planner`, `project-scaffold`, `godot-api`, `gecs`, `input-mapper`, `headless-build`, `gdunit-driver`, `godot-e2e`, `gdtoolkit`, `visual-qa`, `screenshot`, `mcp-driver`. These are reference documents loaded by role skills — users do not invoke them directly.

### skills/core/_shared/

Any reference document consumed by more than one skill lives here as the single source of truth. Examples: `worker-dispatch.md`, `verifier-dispatch.md`, `reviewer-dispatch.md`, `analyst-dispatch.md`.

At publish time, `publish_shared_refs()` reads `_shared/manifest.json` and writes each source file into every listed consumer skill's `references/` folder. Deployed copies carry an `<!-- AUTO-GENERATED -->` header and are overwritten on every publish.

**Edit rules:**
- Edit only the source under `_shared/<file>.md`. Never edit the deployed copies.
- Inside a consumer `SKILL.md`, reference the doc as `references/<file>.md` (the deployed path). Do not write `_shared/<file>` — that path does not exist in a published project.
- After adding or changing a shared doc, run `python -m pytest tests/tools/test_publish_shared.py -q` to confirm the manifest and all consumer references are consistent.

The manifest schema, add/remove flows, and debugging tips are in `docs/contributing/shared-refs.md`.

---

## skills/reviewer/

Eight reviewer skills, one per domain: `physics`, `animation`, `ui`, `tilemap`, `navigation`, `shader`, `audio`, `particles`.

Each reviewer skill directory contains exactly three files:
- `SKILL.md` — the reviewer prompt
- `gotchas.md` — a catalogue of domain-specific pitfalls that LLMs reliably get wrong
- `checklist.md` — systematic checks that map back to gotcha IDs

The reviewer sub-agent (dispatched by `gm-build` and `gm-fixgap`) reads these dynamically based on which Godot classes and APIs appear in the worker's output. For details on the reviewer structure, see [Writing a skill](writing-a-skill.md).

---

## tools/

Python CLI scripts that contributors and users run directly.

| Tool | Purpose |
|------|---------|
| `publish.py` | Deploy GodotMaker into a target Godot project |
| `check_env.py` | Verify Godot, Python, API keys are set up correctly |
| `check_project.py` | Validate a generated project for missing files and broken paths |
| `asset_gen.py` | Generate art via Gemini / xAI (called by `/gm-asset`, can run standalone) |
| `migrate.py` | Run version migration scripts when upgrading across MINOR releases |

### How publish.py wires everything together

When you run `python tools/publish.py <target>`:

1. Read `VERSION` from the repo root and compare against `<target>/.godotmaker/version`. Prompt or block on MINOR / MAJOR upgrades.
2. Copy skills (flat): all directories under `skills/core/` and `skills/reviewer/` → `<target>/.claude/skills/`. Directories whose name starts with `_` (i.e., `_shared/`) are skipped by `publish_skills()`; shared docs are deployed into consumer `references/` folders instead by `publish_shared_refs()`.
3. Copy hooks → `<target>/.godotmaker/hooks/`.
4. Copy tools → `<target>/tools/`.
5. Copy templates → `<target>/.claude/templates/`.
6. Copy `config/stage_schemas.json` → `<target>/.godotmaker/stage_schemas.json`.
7. On fresh install (or `--force`): write `.claude/settings.json`, initialize `CLAUDE.md`, prompt for `godotmaker.yaml`.
8. Stamp `<target>/.godotmaker/version` with the current version.

---

## config/

| File | What it controls |
|------|-----------------|
| `settings.json` | Hook registration: which scripts fire on which Claude Code events |
| `stage_schemas.json` | Per-role required outputs and programmatic checks (keys are role names) |
| `addon_versions.json` | Pinned Godot addon versions per engine version |

`stage_schemas.json` is the schema that `stage_reminder.py` and `check_stage_prerequisites.py` both read. Its keys are role names (`scaffold`, `gdd`, `build`, etc.); each value has an optional `files` array (paths that must exist) and an optional `checks` array (programmatic validator names). See [Writing a skill](writing-a-skill.md) for the full schema description.

---

## templates/

Markdown document templates that `publish.py` deploys into new game projects under `.claude/templates/`. The role skills fill these in during their work. Templates include: `GDD.md`, `PLAN.md`, `STRUCTURE.md`, `SCENES.md`, `ASSETS.md`, `GAP.md`, `MEMORY.md`, `TOC.md`, `game-claude.md`.

---

## tests/

The test suite, organized by what it covers.

```
tests/
├── hooks/
│   ├── helpers.py                       Shared utilities: run_hook, is_blocked, write_completed_roles, ...
│   ├── test_check_completion.py
│   ├── test_check_file_permissions.py
│   ├── test_check_stage_prerequisites.py
│   ├── test_check_worker_report.py
│   ├── test_metrics.py
│   ├── test_session_start.py
│   └── test_stage_reminder.py
├── tools/
│   ├── conftest.py
│   ├── test_addon_versions.py
│   ├── test_check_classname.py
│   ├── test_check_env.py
│   ├── test_check_project.py
│   ├── test_migrate.py
│   ├── test_publish.py
│   └── test_publish_shared.py
└── test_pipeline_e2e.py                 End-to-end pipeline smoke test
```

`pyproject.toml` adds `hooks/` to `pythonpath` so that `from metrics import ...` resolves in hook tests without installing anything. For writing new tests, see [Testing](testing.md).

---

## docs/

Human-readable documentation that lives in the repo alongside the code.

| Path | What it contains |
|------|-----------------|
| `docs/hooks.md` | Accurate per-hook reference (post-rewrite) |
| `docs/versioning.md` | Version scheme and upgrade behaviour |
| `docs/wiki/` | The user-facing and contributor wiki |
| `docs/contributing/` | Shared-refs schema, release checklist |
| `docs/update/` | `next.md` (pending changes) and archived `vX.Y.Z.md` files |
| `docs/reference/` | API and config reference stubs |

---

## shell/

Thin wrappers for the two operations that contributors run from a terminal:

- `publish.sh` / `publish.ps1` — delegates to `python tools/publish.py`
- `report.sh` / `report.bat` — runs `python -m hooks.metrics.reporter` to generate an HTML report from a JSONL metrics file

---

## migrations/

Migration scripts run by `tools/migrate.py` when upgrading a target project across MINOR releases. Scripts are stored under `migrations/{old}_to_{new}/` and run in sorted order. MAJOR upgrades clear all migration scripts (they are not carried forward). See [Release process](release-process.md) for the full upgrade flow.
