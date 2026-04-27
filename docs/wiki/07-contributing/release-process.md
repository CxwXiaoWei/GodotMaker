# Release Process

GodotMaker uses semantic versioning. Each release follows a short checklist; this page summarises it. The canonical checklist is in `docs/contributing/release-checklist.md`.

For version scheme details and how `publish.py` handles upgrades in target projects, see [../../versioning.md](../../versioning.md).

---

## When to bump what

| Level | When | Example |
|-------|------|---------|
| PATCH | Bug fixes with no behaviour change | `0.4.0 → 0.4.1` |
| MINOR | New features or behaviour changes (backward-compatible) | `0.4.0 → 0.5.0` |
| MAJOR | Breaking changes; incremental migration not possible | `0.x → 1.0.0` |

`publish.py` auto-proceeds on PATCH, prompts for confirmation on MINOR, and requires `--force` on MAJOR.

---

## The next.md workflow

Contributors never edit `CHANGELOG.md` directly. Instead, every pull request adds at least one bullet to `docs/update/next.md` under the appropriate category:

```markdown
## Added
- Brief description of the new thing (#123) — @author

## Changed
- What changed and why (#124) — @author

## Fixed
- What was broken (#125) — @author

## Removed
- What was deleted (#126) — @author
```

Use [Keep a Changelog](https://keepachangelog.com/) conventions for category names. If none of the four standard categories fits, add a new one.

At release time, `next.md` is archived and a fresh copy is created. Contributors working on the next batch of changes immediately start adding to the new `next.md`. This means `CHANGELOG.md` is touched only once per release, by whoever cuts the release.

---

## Cutting a release

High-level checklist. Follow the canonical steps in `docs/contributing/release-checklist.md`:

1. **Merge all pending PRs** that should be in this release. Confirm `next.md` has entries for all of them.

2. **Archive next.md.** Rename `docs/update/next.md` to `docs/update/vX.Y.Z.md`. Create a fresh `docs/update/next.md` from the template at the top of that file.

3. **Update CHANGELOG.md.** Prepend a new section:

   ```markdown
   ## [X.Y.Z] — YYYY-MM-DD

   ### Added
   - (items from next.md)

   ### Changed / Fixed / Removed
   - ...
   ```

4. **Bump VERSION.** Write the new version number to the `VERSION` file at the repo root. This is the single source of truth.

5. **Add migration scripts** (MINOR only). If any change requires updating an existing game project's files, add a migration script under `migrations/{old}_to_{new}/`. Scripts are numbered and run in sorted order by `tools/migrate.py`. See `migrations/README.md` for the script format.

6. **Commit and tag.**

   ```bash
   git add VERSION CHANGELOG.md docs/update/ migrations/
   git commit -m "release: vX.Y.Z"
   git tag vX.Y.Z
   ```

7. **Publish to test projects** to confirm nothing broke:

   ```bash
   python tools/publish.py /path/to/test-game
   ```

---

## Migrations

Each MINOR release may ship migration scripts that automatically fix compatibility issues in existing game projects. Scripts live under `migrations/{old}_to_{new}/`, for example:

```
migrations/0.3_to_0.4/001_track_hooks.py
migrations/0.3_to_0.4/002_track_stage_schemas.py
```

`tools/migrate.py` runs them in sorted order when `publish.py` detects a MINOR upgrade. If a script fails, the chain aborts and publish exits with an error. The target project may be partially migrated at that point — fix the issue and re-run publish to continue, or use `--force` for a clean install.

At MAJOR release time, all migration scripts from the previous MAJOR version are deleted. They are not carried forward — MAJOR upgrades use `--force` for a clean re-initialization instead.
