"""Add configurable asset-generation model defaults."""
from pathlib import Path


DEFAULTS = {
    "vqa_model": "gemini-2.5-flash",
    "asset_image_provider": "gemini",
    "gemini_image_model": "gemini-3.1-flash-image-preview",
    "grok_image_model": "grok-imagine-image",
    "grok_video_model": "grok-imagine-video",
}


def _parse_scalar_keys(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        if raw_line.startswith((" ", "\t")):
            continue
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            values[key] = value
    return values


def migrate(target: Path) -> None:
    config_path = target / ".godotmaker" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    values = _parse_scalar_keys(text)

    changed = False
    lines = text.splitlines()
    if values.get("vqa_model") == "gemini-3-flash":
        lines = [
            "vqa_model: gemini-2.5-flash"
            if line.strip().startswith("vqa_model:")
            else line
            for line in lines
        ]
        changed = True

    missing = [key for key in DEFAULTS if key not in values]
    if missing:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([
            "# Asset generation defaults",
            "# Gemini is the default because GOOGLE_API_KEY is required by GodotMaker.",
            "# Grok remains available when XAI_API_KEY is configured.",
        ])
        for key in missing:
            lines.append(f"{key}: {DEFAULTS[key]}")
        changed = True

    if changed:
        config_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        print("  Updated .godotmaker/config.yaml asset model defaults")
    else:
        print("  .godotmaker/config.yaml asset model defaults already present")
