# Document Index: {Name}

<!-- Master index of all project documents. Updated by each /gm-* role on completion. -->

## Design Documents
- `GDD.md` — Game Design Document (produced by `/gm-gdd`)
- `SCENES.md` — UI/scene layout descriptions with element positions and sizes (produced by `/gm-gdd`)

## Planning Documents
- `PLAN.md` — Task breakdown with status tracking (produced by `/gm-gdd`)
- `STRUCTURE.md` — ECS architecture: components, systems, entity archetypes (produced by `/gm-gdd`)
- `ASSETS.md` — Art direction and asset requirements (produced by `/gm-gdd`, refined by `/gm-asset`)

## Pipeline Records
- `.godotmaker/stage.jsonl` — Append-only milestone log; one event per role completion
- `.godotmaker/evaluation.json` — Latest evaluator verdict (produced by `/gm-evaluate`)
- `.godotmaker/final_report.json` — Final acceptance record (produced by `/gm-finalize`)
- `GAP.md` — Gap-fix task list (present only during `/gm-fixgap`; archived to `.godotmaker/gaps/<n>/` afterwards)

## Reference
- `MEMORY.md` — Knowledge base index
- `references/` — Scene reference images (produced by `/gm-asset`)
- `assets/manifest.json` — Asset manifest (produced by `/gm-asset`, if user provides assets)
