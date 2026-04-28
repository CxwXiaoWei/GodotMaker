# Changelog

All notable changes to GodotMaker will be documented in this file.

Format: [Semantic Versioning](https://semver.org/) — MAJOR.MINOR.PATCH

## [0.2.2] — 2026-04-28

### Added

- `auditor_model` config key in `config/config.yaml.default` (default `sonnet`).
- Cross-layer consistency tests — `tests/test_config_consistency.py` (skill-referenced `*_model` defaults match config) and `tests/test_audit_workflow.py` (Round 6 + Round 7 dispatch contract).
- `docs/wiki/07-contributing/codebase-guide.md` (EN + zh) "Permission contract layers" subsection explaining the schema vs hook vs SKILL.md split.
- `docs/update/v0.2.0.md` "Upgrading from v0.1.x" section — declares clean redeploy via `--force` as the supported path; no `0.1_to_0.2` migration is shipped.
- Pre-push CI-mirror hook (`scripts/pre-push`, `scripts/install-hooks.sh`).

### Changed

- `check_file_permissions.py` narrowed evaluate/verify write scopes — evaluate may write `e2e/`, `.godotmaker/evaluation.json`, `.godotmaker/stage.jsonl`, `.godotmaker/current_role`; verify is read-only except `stage.jsonl` and `current_role`.
- `gm-evaluate`/`gm-verify`/`gm-fixgap` SKILL.md now have explicit Permission sections that mirror the hook allow-lists; `gm-fixgap` notes the `fixgap → verify → evaluate` loop position.
- `game-planner` `auditor_model` default switched from `opus` to `sonnet` to match `config.yaml.default`.
- The 9-roles wiki page (EN + zh) — `/gm-asset` section expanded to describe scene reference generation and how `/gm-evaluate` uses `references/scene_<name>.png` as the visual contract.
- FAQ (EN + zh) — per-scene visual reference target corrected to `references/scene_<name>.png`; runtime frame capture path documented separately.
- Active terminology converged on the role-based model — "Stage 1b/4" and "orchestrator" removed from hooks, skills, templates, agents, and tests. Historical references in changelog/glossary/FAQ explanations are kept on purpose.
- README first-run flow (EN + zh) — entry command is `/gm-scaffold`, with `/gm-gdd` as the per-milestone follow-up.
- `docs/update/release-checklist.md` — new step 5 covering five cross-layer consistency gates.
- `templates/TOC.md` — replaced legacy "Stage Execution Records" placeholders with real "Pipeline Records" artifacts.
- `tests/test_agents.py` drops the PyYAML runtime dependency.
- CI workflows bumped to `actions/checkout@v6` and `actions/setup-python@v6` (Node 24).

### Fixed

- Hook docstrings, comments, and user-visible block messages no longer say "orchestrator" — `check_file_permissions.py`, `session_start.py`, `stage_reminder.py`, `metrics/highlights.py`, `metrics/schema.py`.
- `_shared/manifest.json` sanity checks in `check_stage_prerequisites.py` and `stage_reminder.py` now raise `RuntimeError` instead of `assert` (survives `python -O`).
- All `.godotmaker/verify_result.json` references removed from skills and wiki — that file was documented but never produced.

### Removed

- `templates/TOC.md` "Stage Execution Records" rows (STAGE_3 through STAGE_8).

## [0.2.1] — 2026-04-28

### Added

- New `gdd-auditor` sub-agent — independent reviewer that audits a draft GDD against a 9-category checklist and returns 5-8 high-impact follow-up questions per pass. Read-only.
- `tests/test_agents.py` — frontmatter validation for `agents/*.md` (parses, required fields, name matches filename, valid model alias).

### Changed

- `game-planner` now runs two fixed audit rounds (Rounds 6-7) after synthesizing the GDD draft and before showing it to the user. Each round dispatches the new `gdd-auditor` with a fresh context; Round 7 explicitly populates the auditor's `Previously Asked` field to avoid repeats.
- Wiki (EN + zh) updated to document the new agent — `core-skills.md` and `codebase-guide.md` (new `agents/` section enumerating all 5 sub-agents).

## [0.2.0] — 2026-04-27

### Added

- Shared reference docs mechanism (`skills/core/_shared/`) deployed via `publish_shared_refs()` into each consumer skill's `references/` (auto-generated, single source of truth).
- Per-scene visual targets — `/gm-asset` generates `references/scene_*.png`; `/gm-evaluate` compares running screenshots against them via the `visual-qa` skill (Static / Dynamic templates, frame sequences under `e2e/screenshots/scene_{name}/frame_*.png`).

### Changed

- Pipeline split into 9 role-based skills (`gm-scaffold` → `gm-gdd` → `gm-asset` → `gm-build` → `gm-verify` → `gm-evaluate` → `gm-fixgap` → `gm-accept` → `gm-finalize`). `.godotmaker/current_role` file lock enforces per-role write scope at hook level. Stage transitions recorded in `.godotmaker/stage.jsonl` (was `stage.json`).
- Hooks rewritten for the role model — `check_stage_prerequisites.py` uses `PREREQ_ROLE`; `stage_reminder.py` validates per-role outputs from `config/stage_schemas.json`; `on_subagent_stop.py` serialises `log_subagent` + `check_worker_report` to avoid race on `metrics_current.jsonl`.
- Wiki rewritten end-user-facing — 28 pages across 8 sections (getting-started, concepts, skills, troubleshooting, tools, configuration, contributing, reference). `mkdocs.yml` nav and landing page synced.

### Fixed

- Cleared 24 ruff lint errors across `hooks/`, `tools/`, `tests/` and a real `NameError` in `tools/rembg_matting.py` (`bg_color` referenced before assignment in `--preview` branch).
- Aligned `pyproject.toml` version with `VERSION` file.

### Removed

- `harness/` code and docs migrated out into the separate `external automation host` repository.

## [0.1.0] — 2026-04-26

Initial public release.

- 8-stage orchestrator pipeline with hook-enforced gates (requirements → architecture → scaffold → assets → risk impl → main impl → integration → final)
- Worker / verifier / reviewer / analyst subagent dispatch with format-validated reports
- 13 core skills (orchestrator, godot-api, headless-build, gdunit-driver, gdtoolkit, gecs, game-planner, project-scaffold, visual-qa, screenshot, mcp-driver, godot-e2e, input-mapper) and 8 reviewer skills (physics, animation, ui, tilemap, navigation, shader, audio, particles)
- 8 hooks: file permission enforcement, stage prerequisite gating, completion checks, subagent report validation, session bookkeeping, anti-deadloop protection, worktree-aware file resolution
- `tools/publish.py` deploys the framework into a target Godot project, with version tracking and upgrade prompts
- Static checks: `check_project.py` for project completeness, `check_classname.py` for Godot built-in collisions
- Asset pipeline helpers (`asset_gen.py`, `rembg_matting.py`, `tripo3d.py`)
- Wiki documentation (30 pages across 8 sections)
- 193+ unit tests for hooks and tools
