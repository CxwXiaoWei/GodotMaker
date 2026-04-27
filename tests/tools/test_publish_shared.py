"""Tests for publish_shared_refs() and the _shared/ exclusion in publish_skills()."""
import json
import os
import re
import sys
import pytest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tools",
))

from publish import publish_skills, publish_shared_refs
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_repo(tmp_path: Path,
               shared_files: dict[str, list[str]] | None = None,
               skills: list[str] | None = None) -> Path:
    """Build a minimal fake repo with skills/core/* and an optional _shared/."""
    repo = tmp_path / "repo"
    skills = skills or ["gm-build", "gm-fixgap", "gm-asset"]
    for name in skills:
        skill_dir = repo / "skills" / "core" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")

    if shared_files is not None:
        shared_dir = repo / "skills" / "core" / "_shared"
        shared_dir.mkdir(parents=True)
        for filename in shared_files:
            (shared_dir / filename).write_text(f"shared: {filename}\n",
                                               encoding="utf-8")
        (shared_dir / "manifest.json").write_text(
            json.dumps({"files": shared_files}), encoding="utf-8")

    # _read_config.sh helper (publish_skills copies it)
    shell_dir = repo / "shell"
    shell_dir.mkdir(parents=True)
    (shell_dir / "_read_config.sh").write_text("#!/bin/bash\n",
                                               encoding="utf-8")
    return repo


class TestSharedExcludedFromPublishSkills:
    """publish_skills() must skip directories starting with `_`."""

    def test_underscore_dir_not_deployed(self, tmp_path):
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build"])
        target = tmp_path / "target"
        target.mkdir()
        count = publish_skills(repo, target)
        assert count == 1, "only gm-build counted as a skill"
        assert not (target / "_shared").exists(), \
            "_shared/ must NOT appear in deployed skills/"

    def test_real_skill_still_deployed(self, tmp_path):
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build", "gm-fixgap"])
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        assert (target / "gm-build" / "SKILL.md").exists()
        assert (target / "gm-fixgap" / "SKILL.md").exists()


class TestPublishSharedRefs:
    """publish_shared_refs() distributes _shared/<file> to consumer skills."""

    def test_distributes_to_each_consumer(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            shared_files={
                "worker-dispatch.md": ["gm-build", "gm-fixgap"],
                "analyst-dispatch.md": ["gm-asset", "gm-build", "gm-fixgap"],
            },
            skills=["gm-build", "gm-fixgap", "gm-asset"],
        )
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        count = publish_shared_refs(repo, target)
        # 2 + 3 = 5 distributions
        assert count == 5
        for skill in ["gm-build", "gm-fixgap"]:
            assert (target / skill / "references" / "worker-dispatch.md").exists()
        for skill in ["gm-asset", "gm-build", "gm-fixgap"]:
            assert (target / skill / "references" / "analyst-dispatch.md").exists()

    def test_deployed_copy_carries_auto_generated_header(self, tmp_path):
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build"])
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        publish_shared_refs(repo, target)
        deployed = (target / "gm-build" / "references" /
                    "worker-dispatch.md").read_text(encoding="utf-8")
        assert deployed.startswith("<!-- AUTO-GENERATED")
        assert "worker-dispatch.md" in deployed.split("\n")[0]
        # original source body still present below the header
        assert "shared: worker-dispatch.md" in deployed

    def test_invalid_manifest_json_raises_with_path(self, tmp_path):
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build"])
        # Corrupt the manifest
        (repo / "skills" / "core" / "_shared" /
         "manifest.json").write_text("{ not valid json", encoding="utf-8")
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        with pytest.raises(ValueError, match="Invalid JSON in.*manifest.json"):
            publish_shared_refs(repo, target)

    def test_creates_references_dir_if_missing(self, tmp_path):
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build"])
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        # gm-build doesn't have references/ in the fake repo
        assert not (target / "gm-build" / "references").exists()
        publish_shared_refs(repo, target)
        assert (target / "gm-build" / "references" / "worker-dispatch.md").exists()

    def test_no_manifest_returns_zero(self, tmp_path):
        repo = _make_repo(tmp_path, shared_files=None, skills=["gm-build"])
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        assert publish_shared_refs(repo, target) == 0

    def test_missing_source_file_raises(self, tmp_path):
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build"])
        # Delete the source file but leave the manifest claiming it exists
        (repo / "skills" / "core" / "_shared" / "worker-dispatch.md").unlink()
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        with pytest.raises(FileNotFoundError, match="worker-dispatch.md"):
            publish_shared_refs(repo, target)

    def test_missing_target_skill_raises(self, tmp_path):
        repo = _make_repo(
            tmp_path,
            shared_files={"worker-dispatch.md": ["gm-nonexistent"]},
            skills=["gm-build"],
        )
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        with pytest.raises(FileNotFoundError, match="gm-nonexistent"):
            publish_shared_refs(repo, target)

    def test_idempotent(self, tmp_path):
        """Re-publishing must overwrite cleanly, not accumulate or fail."""
        repo = _make_repo(tmp_path,
                          shared_files={"worker-dispatch.md": ["gm-build"]},
                          skills=["gm-build"])
        target = tmp_path / "target"
        target.mkdir()
        publish_skills(repo, target)
        publish_shared_refs(repo, target)
        # Modify source then re-publish
        src = repo / "skills" / "core" / "_shared" / "worker-dispatch.md"
        src.write_text("updated\n", encoding="utf-8")
        publish_shared_refs(repo, target)
        deployed = (target / "gm-build" / "references" /
                    "worker-dispatch.md").read_text(encoding="utf-8")
        # Header is regenerated, source body is the new content
        assert deployed.startswith("<!-- AUTO-GENERATED")
        assert deployed.endswith("updated\n")


class TestProductionManifest:
    """Sanity-check the real _shared/manifest.json against the live repo."""

    def test_all_source_files_exist(self):
        manifest_path = REPO_ROOT / "skills" / "core" / "_shared" / "manifest.json"
        assert manifest_path.exists(), "_shared/manifest.json missing"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename in manifest.get("files", {}):
            src = REPO_ROOT / "skills" / "core" / "_shared" / filename
            assert src.exists(), f"_shared/{filename} listed in manifest but missing"

    def test_all_target_skills_exist(self):
        manifest_path = REPO_ROOT / "skills" / "core" / "_shared" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename, target_skills in manifest.get("files", {}).items():
            for skill_name in target_skills:
                skill_dir = REPO_ROOT / "skills" / "core" / skill_name
                assert skill_dir.is_dir(), \
                    f"manifest maps {filename} -> {skill_name}, but {skill_dir} missing"

    def test_consumer_skills_reference_deployed_path(self):
        """Each consumer SKILL.md should reference `references/<file>`,
        not the legacy `.claude/skills/orchestrator/<file>` or `_shared/`."""
        manifest_path = REPO_ROOT / "skills" / "core" / "_shared" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename, target_skills in manifest.get("files", {}).items():
            for skill_name in target_skills:
                skill_md = REPO_ROOT / "skills" / "core" / skill_name / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                assert f"references/{filename}" in content, \
                    f"{skill_name}/SKILL.md should reference references/{filename}"
                assert f"orchestrator/{filename}" not in content, \
                    f"{skill_name}/SKILL.md still references legacy orchestrator/{filename}"
                assert f"_shared/{filename}" not in content, \
                    f"{skill_name}/SKILL.md should not reference _shared/ at runtime"

    def test_no_bare_shared_filename_references(self):
        """Every mention of a shared filename in a consumer SKILL.md must be
        prefixed with `references/`. Bare mentions (like `\\`worker-dispatch.md\\``
        in body prose) deploy to a path that doesn't exist at runtime."""
        manifest_path = REPO_ROOT / "skills" / "core" / "_shared" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename, target_skills in manifest.get("files", {}).items():
            # Match the filename only when it is NOT preceded by "references/".
            pattern = re.compile(
                r"(?<!references/)\b" + re.escape(filename) + r"\b"
            )
            for skill_name in target_skills:
                skill_md = REPO_ROOT / "skills" / "core" / skill_name / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                bare_hits = pattern.findall(content)
                assert not bare_hits, (
                    f"{skill_name}/SKILL.md has {len(bare_hits)} bare "
                    f"reference(s) to {filename} without the `references/` "
                    f"prefix — these will not resolve at runtime."
                )
