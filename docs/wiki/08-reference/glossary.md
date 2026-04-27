# Glossary

Definitions for terms you'll see across the GodotMaker docs and slash-command output.

---

**Accept** / **Acceptance** — The eighth role in the pipeline, triggered by `/gm-accept`. The AI presents the current build to you and asks whether you want to accept it, send it back for another round of fixes, or stop. Your decision is recorded as an `accept` event in `.godotmaker/stage.jsonl`. See also: *Milestone*, *Role*.

**Analyst** — A sub-agent spawned by `/gm-asset` to inspect image files you provide. The main agent is blocked from reading images directly (to avoid burning context on raw pixel data), so it delegates image analysis to an analyst. The analyst reports back with an art-style summary and a list of usable assets. See also: *Sub-agent*.

**Asset** / **ASSETS.md** — "Asset" refers to art or audio files used by the game (sprites, backgrounds, sound effects). `ASSETS.md` is the planning document that lists every asset the game needs, who will generate it, and whether it has been produced. `/gm-asset` generates missing art and updates this file.

**Component** (ECS) — A small, plain data container attached to an entity. For example, a `Health` component might hold a single number (`hp: 5`). Components have no logic of their own. See also: *ECS*, *Entity*, *System*.

**Current role** / `.godotmaker/current_role` — A plain-text file written by each `/gm-*` skill as its very first action. It records which role is active right now (e.g., `build`). Hook scripts read this file to decide which file-write operations are allowed and which are blocked. When no `/gm-*` skill is running the file is absent (or stale from a previous session, which `session_start.py` clears). See also: *Hook*, *Role*.

**ECS** (Entity-Component-System) — The architecture that all generated game code follows. Instead of putting data and logic together in one big script, ECS splits them: entities are just IDs, components are data bags attached to entities, and systems are functions that run every frame over matching entities. This keeps AI-generated code modular and easier to extend. GodotMaker uses the [gecs](https://github.com/csprance/gecs) addon for ECS in Godot. See also: *Entity*, *Component*, *System*, *gecs*.

**Entity** (ECS) — A unique numeric ID that represents a "thing" in the game world (a player, an enemy, a bullet). An entity has no data or behaviour of its own; it only gains meaning through the components attached to it. See also: *ECS*, *Component*.

**Evaluation** / **Evaluator** — The sixth role in the pipeline, triggered by `/gm-evaluate`. An independent agent runs the game headlessly, captures screenshots, and scores the result against the GDD. It writes its findings to `.godotmaker/evaluation.json` and stores screenshots in `e2e/screenshots/`. The results feed directly into the next role, `/gm-fixgap`. See also: *Role*, *Visual QA*.

**Fixgap** / **GAP.md** — The seventh role, triggered by `/gm-fixgap`. It reads the evaluation report, creates a `GAP.md` file listing every gap between what the GDD describes and what the game currently does, and dispatches workers to address each issue. After the fixes are done, `GAP.md` is archived to `.godotmaker/gaps/<n>/`. See also: *Role*, *Worker*.

**GDD** (Game Design Document) — A structured document (`GDD.md`) that describes everything about the game: what it is, how it plays, what the player does, what the win/lose conditions are. The GDD is the single source of truth that all later roles refer back to. Produced by `/gm-gdd`.

**gecs** — An open-source Godot addon that provides the Entity, Component, and System base classes GodotMaker builds on. Source: [github.com/csprance/gecs](https://github.com/csprance/gecs). GodotMaker pins specific addon versions in `config/addon_versions.json`. See also: *ECS*.

**Hook** — A small Python script that Claude Code runs automatically on specific events (session start, before a file write, after a sub-agent finishes, etc.). Hooks enforce pipeline rules — for example, blocking the main agent from writing game code during the evaluate role, or refusing to let `/gm-build` end if it dispatched workers but never ran a verifier. Hooks live in `.godotmaker/hooks/` inside the generated project. See `docs/hooks.md` for the full list.

**Milestone** — One complete pass through the pipeline from `/gm-gdd` to `/gm-finalize`. After a milestone is done you can start the next one with a fresh `/gm-gdd` to add features or change direction. `/gm-scaffold` is a once-per-project step and does not repeat between milestones.

**PLAN.md** — The task list produced by `/gm-gdd`. It breaks the GDD down into discrete implementation tasks, each with a status field (`pending` / `in_progress` / `completed` / `verified`). `/gm-build` works through this list by dispatching a worker per task. The hook `stage_reminder.py` refuses to let `/gm-build` finish until every task is marked `verified`.

**Reviewer** — A sub-agent and a set of 8 specialist skills (`physics`, `animation`, `ui`, `tilemap`, `navigation`, `shader`, `audio`, `particles`). After a worker implements a task and a verifier tests it, a reviewer checks the code for Godot-specific pitfalls documented in each skill's `gotchas.md` and `checklist.md`. Any new issues discovered are fed back into `PLAN.md` as new tasks. See also: *Sub-agent*, *Worker*, *Verifier*.

**Role** — One of the nine focused steps in the GodotMaker pipeline. Each role maps to a `/gm-*` slash command and has a defined scope of what it may read and write. Roles replaced the older concept of "stages" (see *Stage vs Role* below). The nine roles in order: `scaffold`, `gdd`, `asset`, `build`, `verify`, `evaluate`, `fixgap`, `accept`, `finalize`.

**SCENES.md** — A planning document produced by `/gm-gdd` that lists every Godot scene the game needs, what it contains, and how scenes relate to each other. The build role uses this when implementing the scene tree layout.

**Skill** (Claude Code skill) — A markdown file (`SKILL.md`) that gives Claude Code a set of instructions for a specific job. GodotMaker ships 9 role skills (the `/gm-*` commands), 12 supporting skills (reference docs and helpers), and 8 reviewer skills. Skills are deployed into `.claude/skills/` inside the generated project. Users invoke role skills by typing the slash command; supporting and reviewer skills are called internally by the role skills.

**Stage vs Role** — "Stage" was the original GodotMaker term for a pipeline step, and references to an "8-stage pipeline" described the first architecture. The pipeline has been redesigned as 9 role-based commands with no central orchestrator. The word "stage" may still appear in some file names (e.g., `stage_schemas.json`, `stage.jsonl`) and older docs, but the canonical term going forward is "role." See also: *Role*.

**stage.jsonl** — An append-only log file at `.godotmaker/stage.jsonl`. Every time a `/gm-*` role finishes successfully, it appends one JSON line: `{"role": "<name>", "ts": "<iso-timestamp>"}`. The `check_stage_prerequisites.py` hook reads this file to confirm that required earlier roles have completed before allowing a new role to start. "jsonl" means each line is a separate valid JSON object.

**STRUCTURE.md** — A planning document produced by `/gm-gdd` that describes the folder layout of the generated project: which directories exist, what kinds of files go in each, and how the source tree is organised.

**Sub-agent** — An AI agent that the main role agent spawns to do a specific piece of work in parallel. Sub-agents operate in isolated git worktrees so they don't conflict with each other. The four sub-agent types are: *Worker*, *Verifier*, *Reviewer*, and *Analyst*.

**System** (ECS) — A function (or GDScript class) that runs every frame over all entities that have a specific combination of components. For example, a `MovementSystem` might run over every entity that has both a `Velocity` component and a `Position` component, updating the position each frame. Systems contain all the game logic. See also: *ECS*, *Entity*, *Component*.

**TOC.md** — A table of contents document produced by `/gm-gdd` that lists all planning documents and their locations. It gives a quick overview of what exists in the project at the start of each milestone.

**Verifier** — A sub-agent that runs the headless Godot build and the unit tests written by a worker, then reports whether they pass. The verifier also runs "adversarial probes" — targeted tests for edge cases and error handling. If verification fails, the issue goes back to the worker. See also: *Sub-agent*, *Worker*, *Reviewer*.

**Visual QA** / **VQA** — The process of comparing a screenshot of the running game against a reference image or a set of written criteria. `/gm-evaluate` uses the `visual-qa` skill (backed by Gemini) to score each scene against the GDD description and any per-scene reference images generated by `/gm-asset`. See also: *Evaluation*.

**Worker** — A sub-agent that implements one game task: writes the GDScript code, the unit tests, and an end-to-end test, then reports back with a structured report. Workers operate in isolated git worktrees. After a worker finishes, a verifier and then a reviewer must both complete before the next task begins. See also: *Sub-agent*, *Verifier*, *Reviewer*, *Worktree*.

**Worktree** — A git feature that lets multiple working directories share the same repository. GodotMaker uses worktrees so parallel sub-agents each get their own folder to write files into without stepping on each other's changes. A worktree requires at least one commit in the repository, which is why `/gm-scaffold` always creates an initial commit. See also: *Sub-agent*.
