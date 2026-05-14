# Project config

`.godotmaker/config.yaml` is per-project: things like which AI model handles code generation, which model checks screenshots, and other behaviour you might want to vary between projects. It lives inside the project folder, so different games can have different settings.

## How it gets created

The first time you run `python tools/publish.py <project>`, the publish script copies GodotMaker's defaults into `.godotmaker/config.yaml`. On every subsequent publish the file is left untouched — your edits are never overwritten.

## Common fields

These are the fields you are most likely to want to change:

**`worker_model`** — which Claude model writes your game code. Workers do the heavy lifting: implementing systems, writing tests, fixing gaps. Defaults to `opus` because complex code generation benefits from the stronger model. Switch to `sonnet` if you want faster (but potentially less thorough) builds.

**`verifier_model`** — which model runs verification checks (did the build compile, did tests pass). Defaults to `sonnet`. Fine to leave it here unless you are seeing spurious failures.

**`reviewer_model`** — which model reviews code for Godot-specific gotchas (physics, animation, UI pitfalls). Defaults to `sonnet`.

**`analyst_model`** — which model inspects user-provided image files during `/gm-asset`. Defaults to `sonnet`.

**`vqa_model`** — which Gemini model performs visual quality checks during `/gm-evaluate` (comparing screenshots against reference images). Defaults to `gemini-2.5-flash`. You can use a newer Gemini model name if you want higher-quality visual analysis at higher cost.

**`asset_image_provider`** — which image backend `tools/asset_gen.py image` uses when `--model` is omitted. Defaults to `gemini`, because `GOOGLE_API_KEY` is required by GodotMaker; set it to `grok` only when `XAI_API_KEY` is configured.

**`gemini_image_model`** — the Gemini image-generation model used when `asset_gen.py image --model gemini` runs. Defaults to `gemini-3.1-flash-image-preview` (Nano Banana 2), which supports the framework's `512`, `1K`, `2K`, and `4K` size presets.

**`grok_image_model`** — the xAI image model used when `asset_gen.py image --model grok` runs. Defaults to `grok-imagine-image`.

**`grok_video_model`** — the xAI video model used by `asset_gen.py video`. Defaults to `grok-imagine-video`.

The file with defaults looks like this:

```yaml
# GodotMaker project configuration
# Edit these values to customize behavior

# VQA model for visual quality checks (any Gemini model name)
# Default: gemini-2.5-flash
# Examples: gemini-2.5-flash, gemini-2.0-flash, gemini-flash-latest
vqa_model: gemini-2.5-flash

# Asset generation defaults
# Gemini is the default because GOOGLE_API_KEY is required by GodotMaker.
# Grok remains available when XAI_API_KEY is configured.
asset_image_provider: gemini

# Image/video generation models
# gemini_image_model is the Nano Banana 2 image model used by --model gemini.
gemini_image_model: gemini-3.1-flash-image-preview
grok_image_model: grok-imagine-image
grok_video_model: grok-imagine-video

# Agent model configuration
# Workers use opus for complex implementation tasks
# Verifiers, reviewers, and analysts use sonnet for lighter validation work
worker_model: opus
verifier_model: sonnet
reviewer_model: sonnet
analyst_model: sonnet
```

## How to change a setting

Open `.godotmaker/config.yaml` in any text editor and change the value after the colon. For example, to use `sonnet` for workers instead of `opus`:

```yaml
worker_model: sonnet
```

Save the file and you are done. No restart required.

## When changes take effect

The next `/gm-*` command you run picks up whatever is in the file at that moment. If you change a setting while a session is already running, the change does not apply until you start a new session.

## About `.claude/settings.json`

There is another config file at `.claude/settings.json` that registers which hook scripts Claude Code runs on events like file writes, session start, and agent stops. This is a framework-managed file — it wires up GodotMaker's safety rules and you generally do not need to touch it. If your hooks stop firing after an upgrade, running `python tools/publish.py --force <project>` republishes it with the current version.
