# Next Release

> **Contributors:** Every pull request MUST include an entry in this file describing the change.
> When a new version is released, this file will be archived as `vX.Y.Z.md` and a fresh copy will take its place.

## How to add an entry

Append your change under the appropriate category below. Use this format:

```
- Brief description of the change (#PR_NUMBER) — @author
```

If no category fits, add a new one following [Keep a Changelog](https://keepachangelog.com/) conventions.

---

## Added

## Changed

- **`publish.py --force` upgrade path now has integration coverage.** New `tests/tools/test_publish.py::TestPublishMainForceRmtree` drives `publish.main(--force)` end-to-end against a target seeded with the exact failing shape — a read-only `pack-*.idx` under `.claude/skills/godot-api/doc_source/.git/objects/pack/`. Mutation-verified: reverting the rmtree fix makes the test fail with the real `PermissionError [WinError 5]`. Before this, the `--force` cleanup branch (`elif args.force and skills_target.exists()` in `publish.py`) had zero coverage — `tests/tools/test_publish.py` was unit-only, and the only main()-driving test (`tests/tools/test_migrate.py::TestPublishMainMigrationRouting`) seeded an empty target so the rmtree branch was never entered.

## Fixed

- **Windows `--force` upgrade crashed on read-only files (`PermissionError [WinError 5]`).** When upgrading from a baseline that had cloned `godot-docs` into `.claude/skills/godot-api/doc_source/`, git wrote `.git/objects/pack/pack-*.idx` as `r--r--r--`. `publish.py` cleared `.claude/skills/` via plain `shutil.rmtree`, which on Windows refuses to unlink read-only files (Linux/macOS ignore the read-only bit, hence the cross-platform blind spot). All three `shutil.rmtree` call sites in `publish.py` now go through a new `rmtree_force()` helper that clears the read-only bit in the rmtree `onerror`/`onexc` hook and retries (handler signature compatible with both Python 3.10–3.11 and 3.12+). The crash aborted `main()` before `.godotmaker/version` was stamped, so any caller that re-invokes `publish.py` on `installed_version != target_version` would keep re-triggering the same crash on every retry — looking like an "infinite republish" symptom from the caller's side.

## Removed
