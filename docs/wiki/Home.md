# GodotMaker Wiki

GodotMaker takes a plain-English description of the game you want and turns it into a complete, playable Godot 4 project — code, art, tests, and quality checks already in place. You drive the process with nine slash commands; the framework keeps everything honest in between.

## New here? Start with these three pages

1. [Installation](01-getting-started/installation.md) — what you need on your machine and how to set it up
2. [Your first game](01-getting-started/first-game.md) — a walk-through that runs all nine commands end-to-end
3. [How it works](02-concepts/how-it-works.md) — what the framework actually does behind those commands

## Wiki sections

| Section | When to read it |
|---------|-----------------|
| [Getting Started](01-getting-started/installation.md) | First time setting up GodotMaker, or making a fresh project |
| [Concepts](02-concepts/how-it-works.md) | You want to understand the 9-role pipeline, ECS, and the design choices |
| [Skills](03-skills/skill-system.md) | What the role / supporting / reviewer skills are and which one does what |
| [Troubleshooting](04-troubleshooting/common-problems.md) | A command stopped, blocked, or behaved oddly — find a fix here |
| [Tools](05-tools/publish.md) | Reference for `publish.py`, `check_env.py`, `check_project.py`, asset helpers |
| [Configuration](06-configuration/project-config.md) | Per-project preferences, host paths, addon version pinning |
| [Contributing](07-contributing/development-setup.md) | You want to add a skill, hook, or tool, or cut a release |
| [Reference](08-reference/glossary.md) | Glossary, FAQ, and pointer to the changelog |

## What you can do with GodotMaker

| Capability | What it means for you |
|------------|----------------------|
| **Describe, don't configure** | Write a plain-language game brief; the framework plans, scaffolds, and codes it for you |
| **Get tested code by default** | Unit tests (gdUnit4) and end-to-end tests are written alongside game code, not bolted on later |
| **Catch Godot-specific bugs early** | Eight domain reviewers (physics, animation, UI, tilemap, navigation, shader, audio, particles) flag common Godot pitfalls before you see the build |
| **Visual quality checks included** | Automated screenshots and AI-based visual assessment confirm the game looks right, not just compiles |
| **Consistent ECS structure** | All generated game logic follows Entity-Component-System via `gecs` — no spaghetti node scripts |
| **Stay in control** | Each step is one slash command; you decide when to start the next, can stop anytime, and resume cleanly |

## Project status

- Current release: see [`VERSION`](https://github.com/RandallLiuXin/GodotMaker/blob/main/VERSION) and [`CHANGELOG.md`](https://github.com/RandallLiuXin/GodotMaker/blob/main/CHANGELOG.md)
- What's coming next: [`docs/update/next.md`](../update/next.md)
- Roadmap: [`ROADMAP.md`](https://github.com/RandallLiuXin/GodotMaker/blob/main/ROADMAP.md)

## Quick links

- [GodotMaker repository](https://github.com/RandallLiuXin/GodotMaker)
- [gecs — ECS framework](https://github.com/csprance/gecs)
- [gdUnit4 — testing framework](https://github.com/MikeSchulze/gdUnit4)
- [godot-mcp — runtime debugging](https://github.com/Coding-Solo/godot-mcp)
