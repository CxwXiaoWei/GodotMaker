"""Migrate existing projects to the tag-based pipeline layout.

Before: a project has a single root-level GDD.md + PLAN.md + STRUCTURE.md
+ SCENES.md + ASSETS.md + MEMORY.md describing the entire game in one
shot. /gm-build runs end-to-end against that single PLAN.

After: ROADMAP.md splits the game into SemVer-tagged release tags; root
docs are scoped to one tag at a time; finished tags are archived to
docs/tags/<tag>/.

This migration retroactively treats whatever was already there as
v0.1.0's working docs:
  - writes a stub ROADMAP.md with a single v0.1.0 entry the user can edit
  - copies the current root docs into docs/tags/v0.1.0/ as v0.1.0's
    archive (GDD.md is copied as GDD-snapshot.md to match the new naming)
  - leaves root files untouched — /gm-gdd subsequent-mode picks them up
    as the in-progress v0.1.0 working set on the next run

Does NOT run `git tag v0.1.0` — the migration cannot know whether the
working tree is in a state worth tagging. The user decides when to tag.
"""
import os
import re
import shutil
from pathlib import Path

ROOT_DOCS = ("PLAN.md", "STRUCTURE.md", "SCENES.md", "MEMORY.md")
INITIAL_TAG = "v0.1.0"
ROADMAP_FILENAME = "ROADMAP.md"
TAGS_DIR_REL = Path("docs") / "tags"

_TAG_HEADER_RE = re.compile(r"^\*\*Tag:\*\*\s*v\d+\.\d+\.\d+\s*$", re.MULTILINE)


def migrate(target: Path) -> None:
    """target is the absolute path to the game project root."""
    gdd = target / "GDD.md"
    plan = target / "PLAN.md"
    roadmap = target / ROADMAP_FILENAME
    tags_dir = target / TAGS_DIR_REL
    archive_dir = tags_dir / INITIAL_TAG

    if not gdd.is_file() or not plan.is_file():
        print(f"  [skip] no existing GDD.md+PLAN.md at {target} — nothing to migrate")
        return

    if roadmap.is_file() and (archive_dir / "GDD-snapshot.md").is_file():
        print(f"  [skip] target already migrated (ROADMAP.md + docs/tags/{INITIAL_TAG}/GDD-snapshot.md both present)")
        return

    # Validate PLAN.md is UTF-8 before any mutation. Strict read here so a
    # CP-1252/GBK file aborts cleanly instead of getting silently corrupted
    # by `errors="replace"` + write-back inside `_inject_tag_header`.
    try:
        plan.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(
            f"  [error] PLAN.md is not UTF-8 (decode failed at byte "
            f"{exc.start}). Re-save as UTF-8 without BOM and re-run the "
            f"migration. No files have been modified."
        )
        return

    project_name = _extract_project_name(gdd, plan)
    feature_bullets = _extract_feature_bullets(plan)

    if _inject_tag_header(plan, INITIAL_TAG):
        print(f"  [done] inject `**Tag:** {INITIAL_TAG}` header into PLAN.md")

    archive_dir.mkdir(parents=True, exist_ok=True)
    print(f"  [done] mkdir docs/tags/{INITIAL_TAG}/")

    shutil.copy2(gdd, archive_dir / "GDD-snapshot.md")
    print(f"  [done] copy GDD.md → docs/tags/{INITIAL_TAG}/GDD-snapshot.md")

    for name in ROOT_DOCS:
        src = target / name
        if src.is_file():
            shutil.copy2(src, archive_dir / name)
            print(f"  [done] copy {name} → docs/tags/{INITIAL_TAG}/{name}")
        else:
            print(f"  [skip] {name} not at root — nothing to archive")

    _atomic_write_text(roadmap, _render_roadmap(project_name, feature_bullets))
    print(f"  [done] write {ROADMAP_FILENAME}")

    print(
        f"  [info] {INITIAL_TAG} archived but NOT git-tagged. Inspect "
        f"docs/tags/{INITIAL_TAG}/ and the new {ROADMAP_FILENAME}, then "
        f"run `git tag {INITIAL_TAG}` yourself when the working tree is "
        f"in a state worth marking."
    )


def _atomic_write_text(path: Path, content: str) -> None:
    """Write content to path via tempfile + os.replace. Crash-safe: a
    SIGTERM mid-write either leaves the original file intact (if rename
    didn't run) or fully replaced (if it did). LF line endings on every
    platform so the output diffs cleanly against the rest of the repo.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def _inject_tag_header(plan: Path, tag: str) -> bool:
    """Add `**Tag:** {tag}` to PLAN.md if missing. Returns True if modified.

    Inserts two lines below the first H1; if no H1, prepends to top.
    Idempotent: any pre-existing `**Tag:** vX.Y.Z` (regardless of value)
    is left alone so a re-run never duplicates the header.

    Caller MUST have validated PLAN.md is UTF-8 (see migrate()).
    """
    text = plan.read_text(encoding="utf-8")
    if _TAG_HEADER_RE.search(text):
        return False

    header_line = f"**Tag:** {tag}"
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("# "):
            ending = "\n" if line.endswith("\n") else ""
            lines.insert(i + 1, f"\n{header_line}{ending}")
            _atomic_write_text(plan, "".join(lines))
            return True
    _atomic_write_text(plan, f"{header_line}\n\n{text}")
    return True


def _extract_project_name(gdd: Path, plan: Path) -> str:
    """Read the first H1 from GDD.md or PLAN.md, strip leading prose."""
    for path in (gdd, plan):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        title = line[2:].strip()
                        for prefix in ("Game Design Document:", "Game Plan:"):
                            if title.startswith(prefix):
                                title = title[len(prefix):].strip()
                        if title:
                            return title
        except OSError:
            continue
    return "Untitled"


def _extract_feature_bullets(plan: Path) -> list[str]:
    """Pull a few bullets to seed the v0.1.0 ROADMAP entry. Best-effort.

    Looks for the first table whose header includes 'System' or 'Task'
    and grabs up to 5 row labels. If nothing matches, returns a single
    placeholder line.
    """
    try:
        with open(plan, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return ["initial implementation (see docs/tags/v0.1.0/PLAN.md for details)"]

    bullets: list[str] = []
    in_table = False
    header_seen = False
    for raw in lines:
        line = raw.strip()
        if line.startswith("|") and not in_table:
            lower = line.lower()
            if "system" in lower or "task" in lower or "mechanic" in lower:
                in_table = True
                continue
        elif in_table:
            if not line.startswith("|"):
                if header_seen:
                    break
                continue
            if set(line.replace("|", "").strip()) <= set("-: "):
                header_seen = True
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells and cells[0]:
                bullets.append(cells[0])
                if len(bullets) >= 5:
                    break

    if not bullets:
        bullets = ["initial implementation (see docs/tags/v0.1.0/PLAN.md for details)"]
    return bullets


def _render_roadmap(project_name: str, bullets: list[str]) -> str:
    bullet_lines = "\n".join(f"- {b}" for b in bullets)
    return f"""# Roadmap: {project_name}

<!-- Auto-generated by the tag-based-pipeline migration. The features
     listed under v0.1.0 below were extracted from the pre-migration
     PLAN.md as a starting point — edit them to match what was actually
     built (or what you want v0.1.0 to claim it built). Add later tags
     (v0.2.0, v0.3.0, ...) describing what comes next. -->

## SemVer convention

- **MAJOR** (vX.0.0): core gameplay loop changes
- **MINOR** (v0.X.0): new full system or playable module
- **PATCH** (v0.X.Y): in-tag fixes / small tweaks

## v0.1.0 — Initial implementation

<!-- Working docs at the moment of migration were archived to
     docs/tags/v0.1.0/ as a snapshot. The root GDD/PLAN/STRUCTURE/
     SCENES/ASSETS/MEMORY remain in place; /gm-gdd subsequent-mode
     picks them up as the in-progress v0.1.0 working set. -->

{bullet_lines}

## v0.2.0 — {{next theme}}

- {{feature 1}}
- {{feature 2}}
"""
