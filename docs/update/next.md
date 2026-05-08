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

- `skills/core/_shared/reviewer-finding-triage.md` — New shared reference doc defining the **ACCEPT / REJECT / SKIP** triage rules for every reviewer finding regardless of severity. Defaults: critical/major → ACCEPT; minor → SKIP. Citation is mandatory for critical/major REJECT/SKIP and optional for minor. Forbidden reject reasons listed explicitly. Deployed to `gm-build` and `gm-fixgap` via the manifest.
- `skills/core/gm-accept/SKILL.md` — "Reviewer Triage Decisions for This Tag" table added to the user-facing tag summary (with a Decision column for REJECT vs SKIP); user is the final gate on whether the agent's triage was justified.
- `templates/MEMORY.md` — New "Reviewer Triage Log" section between Workarounds and Component Design Decisions. Records every REJECT and SKIP with finding/severity/decision/reason/citation. Cross-tag accumulating audit trail.
- `tests/test_reviewer_finding_triage.py` — Structural regression gate that locks in the three-option model, severity-conditional citation requirement, and the forbidden-reasons list against silent weakening.

## Changed

- `skills/core/gm-build/SKILL.md` — Mid-cycle "every ≥5 worker" verify+review trigger removed. New Step 2 "Verify + Review Pass" runs once per cycle iteration after `PLAN.md` is clean and loops back to dispatch if the reviewer added ACCEPTED tasks. Hard Rule 5/6 reworded; reviewer subsection now uses the three-option triage. Retry limit raised from 3 to 5.
- `skills/core/gm-fixgap/SKILL.md` — Step 4 reviewer subsection now uses the three-option triage (ACCEPT / REJECT / SKIP per `references/reviewer-finding-triage.md`). Hard Rule 6 reworded. Retry limit raised from 3 to 5.
- `skills/core/_shared/reviewer-dispatch.md` — Outdated "every completed worker task" wording fixed; new "Handling the Reviewer's Report" section describes the three-option triage and points to the triage doc.
- Wiki (EN + zh) — `02-concepts/the-9-roles.md`, `02-concepts/how-it-works.md`, `03-skills/reviewer-skills.md`, `07-contributing/writing-a-skill.md`, `08-reference/faq.md`, `08-reference/glossary.md` updated to describe the new "PLAN clean → one verify+review pass → ACCEPT/REJECT/SKIP triage" model.

## Fixed

## Removed
