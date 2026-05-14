"""Tests for migrations/20260514160000_asset_model_config.py.

Migration adds project-level asset generation defaults and corrects only the
known-bad legacy VQA default. User-provided model values must be preserved.
"""
import importlib.util
from pathlib import Path

import pytest


MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "20260514160000_asset_model_config.py"
)


@pytest.fixture
def migration_module():
    spec = importlib.util.spec_from_file_location("asset_model_config", MIGRATION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_adds_missing_asset_model_defaults(migration_module, tmp_path):
    config = tmp_path / ".godotmaker" / "config.yaml"
    config.parent.mkdir()
    config.write_text("worker_model: opus\n", encoding="utf-8")

    migration_module.migrate(tmp_path)

    text = config.read_text(encoding="utf-8")
    assert "asset_image_provider: gemini" in text
    assert "gemini_image_model: gemini-3.1-flash-image-preview" in text
    assert "grok_image_model: grok-imagine-image" in text
    assert "grok_video_model: grok-imagine-video" in text
    assert "vqa_model: gemini-2.5-flash" in text


def test_replaces_only_old_invalid_vqa_default(migration_module, tmp_path):
    config = tmp_path / ".godotmaker" / "config.yaml"
    config.parent.mkdir()
    config.write_text(
        "vqa_model: gemini-3-flash\n"
        "gemini_image_model: custom-gemini-image\n",
        encoding="utf-8",
    )

    migration_module.migrate(tmp_path)

    text = config.read_text(encoding="utf-8")
    assert "vqa_model: gemini-2.5-flash" in text
    assert "gemini_image_model: custom-gemini-image" in text


def test_is_idempotent(migration_module, tmp_path):
    config = tmp_path / ".godotmaker" / "config.yaml"
    config.parent.mkdir()
    config.write_text("worker_model: opus\n", encoding="utf-8")

    migration_module.migrate(tmp_path)
    once = config.read_text(encoding="utf-8")
    migration_module.migrate(tmp_path)

    assert config.read_text(encoding="utf-8") == once
