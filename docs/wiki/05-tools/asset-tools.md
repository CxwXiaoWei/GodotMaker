# Asset tools

GodotMaker generates art via small Python helper scripts. `/gm-asset` calls them automatically — but you can also run them by hand if you need to regenerate a specific file or experiment with different settings.

## asset_gen.py

`asset_gen.py` is the main API-backed image and 3D model generator. It supports Gemini, OpenAI, xAI Grok, and Tripo3D. Runtime-native `native` / `codex` image generation is selected by `/gm-asset`, not this script.

**Image providers:**

| Provider | Cost per image | Best for |
|----------|---------------|---------|
| xAI Grok | 2 cents (1K or 2K only) | Fast, good for most sprites and UI elements |
| Google Gemini | 5–15 cents (512 to 4K) | More precise prompt following, better for detailed or edited images |
| OpenAI | 5–7 cents in the local budget model | OpenAI Images API generation/editing |

Provider-prefixed selectors require the matching key: `GOOGLE_API_KEY` / `GEMINI_API_KEY` for Gemini, `OPENAI_API_KEY` for OpenAI, and `XAI_API_KEY` for Grok. To choose which provider `/gm-asset` uses, set `asset_image_model` in [`../06-configuration/project-config.md`](../06-configuration/project-config.md).

### Generating an image

```bash
python tools/asset_gen.py image \
  --prompt "top-down pixel art player character, blue outfit, 64x64, transparent background" \
  -o assets/sprites/player.png
```

To use Grok instead:

```bash
python tools/asset_gen.py image \
  --prompt "top-down pixel art player character, blue outfit, 64x64, transparent background" \
  --model grok \
  --size 1K \
  -o assets/sprites/player.png
```

To edit an existing image (image-to-image):

```bash
python tools/asset_gen.py image \
  --prompt "add a glowing aura around the character" \
  --image assets/sprites/player.png \
  -o assets/sprites/player_glow.png
```

**Common options:**

| Option | Default | Notes |
|--------|---------|-------|
| `--prompt` | (required) | Describe what you want |
| `--model` | project config | `gemini[:model]`, `openai[:model]`, or `grok[:model]`; overrides `asset_image_model` |
| `--size` | `1K` | OpenAI: `1K`. Grok: `1K`, `2K`. Gemini: `512`, `1K`, `2K`, `4K` |
| `--aspect-ratio` | `1:1` | Many options — run `--help` to see all |
| `--image` | none | Provide a reference image to edit |
| `-o` | (required) | Output file path |

### Setting a budget

You can cap total spending to avoid surprises:

```bash
python tools/asset_gen.py set_budget 500
```

This sets a 500-cent ($5.00) limit, tracked in `assets/budget.json`. Any generation command that would exceed the remaining budget exits with an error before making an API call.

### Generating 3D models

The `glb` subcommand converts a PNG image into a 3D model (`.glb` file) using Tripo3D. This requires `TRIPO3D_API_KEY` and is only relevant for 3D games.

```bash
python tools/asset_gen.py glb \
  --image assets/sprites/tree.png \
  -o assets/models/tree.glb
```

Cost is roughly 40–50 cents per model depending on the `--quality` preset (`default` or `high`).

## rembg_matting.py

`rembg_matting.py` removes solid-color backgrounds from images, producing PNG files with transparent backgrounds. Use this when you have a sprite rendered on a plain background and need it cut out for use in a scene.

```bash
# Single image, auto-detect the best approach
python tools/rembg_matting.py assets/sprites/enemy_raw.png -o assets/sprites/enemy.png

# Batch: process all PNGs in a folder
python tools/rembg_matting.py --batch raw_frames/ -o clean_frames/

# Generate a preview so you can check the result before using it
python tools/rembg_matting.py assets/sprites/enemy_raw.png --preview
```

The tool uses a neural network (BiRefNet) to identify the subject and color matting to clean up the edges. It auto-selects the right approach for most images; you can force a mode with `-m trust`, `-m adapt`, or `-m color` if the automatic result is not clean enough.

GPU acceleration is used automatically if an NVIDIA GPU with CUDA is available. On CPU it is slower but still works.

## tripo3d.py

`tripo3d.py` is the Tripo3D API client used by `asset_gen.py glb` internally. You do not normally call it directly — use the `glb` subcommand of `asset_gen.py` instead. It requires `TRIPO3D_API_KEY`.

## Calling these by hand

You usually do not need to run these scripts directly. `/gm-asset` orchestrates them based on your `ASSETS.md` and calls them with the right prompts and output paths automatically.

The main reasons to call them manually:

- You want to regenerate one specific asset with a tweaked prompt.
- You are experimenting with different sizes, providers, or aspect ratios before committing to a full `/gm-asset` run.
- You received art from an external source and want to remove its background with `rembg_matting.py`.

If you want to update the visual targets that `/gm-evaluate` checks against, re-run `/gm-asset` rather than editing the generated images directly. Editing them by hand will be overwritten the next time `/gm-asset` runs.
