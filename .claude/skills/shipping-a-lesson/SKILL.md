---
name: shipping-a-lesson
description: Use when a handbook lesson has just been reviewed and approved by the user and needs to be closed out — recording it in the logbook and committing/pushing the change. Trigger on "close it out", "ship it", "approved, commit it", or any post-review wrap-up of a lessons/ change.
when_to_use: Trigger only AFTER the user has reviewed and approved a lesson (or a lesson edit). Not for writing the lesson (use authoring-lessons) and not before user review.
argument-hint: "[lesson-number-or-slug]"
arguments: lesson
---

# Shipping a lesson

Close out an **already-approved** lesson: record it in the logbook, commit, push.
This is the repeatable wrap-up that runs *after* `authoring-lessons` + user review.

## Precondition (do not skip)

**The user must have reviewed and approved the lesson first.** This skill is the
*post-approval* step. If approval hasn't happened, stop and ask — do not ship an
unreviewed lesson.

**Invoking this skill IS the user's authorization to commit AND push.** CLAUDE.md
says "commit or push only when the user asks"; running this skill is that ask. Both
commit and push are in scope — do not defer the push.

## The workflow

Do these in order. Stop and report if any verification gate fails.

### 1. Verification gate (before touching git)

```bash
uv run python .claude/skills/authoring-lessons/scripts/validate_lesson.py lessons/<NN-slug>
uv run task lint
```

If the lesson is `theory+practice` / `practice`, also run its code and confirm the
pasted output is real:

```bash
uv run python -m lessons.<NN-slug>.demo
```

A failing gate blocks the commit. Fix or report; do not ship red.

### 2. Update `lessons/README.md` index

Confirm the lesson has a row in the **"Index (built so far)"** table (number,
linked title, type, one-line coverage). `authoring-lessons` step 7 usually adds it
during authoring — if it's missing, add it now.

### 3. Update `docs/logbook.md` — all three edits

This is the part that needs judgment; the rest is mechanical. Do **all three**:

- **Session log**: append a dated entry — what was built, what was verified *at the
  primary*, registry impact (changed? why?), any in-lesson uncertainty flags, and a
  **"Left off at / Next"** line.
- **Current state**: mark the lesson DONE.
- **Next step / "Next session"** block: point it at the next lesson in syllabus
  order (number, slug, type, prereqs, and any per-lesson reminders — e.g. practice
  lessons must run with real output, verify framework APIs via Context7).
- Also update the **Key artifacts table** row (`lessons/` status; and the
  `sources.md` row if the registry changed).

### 4. Update `docs/sources.md` — only if the registry changed

Touch this **only** if the lesson added or corrected a registry entry — and only
with content **verified at its primary source** (CLAUDE.md evidence rule). If the
lesson cited only already-verified sources, leave it untouched.

### 5. Commit on `main` — do NOT branch

This repo commits Phase-3 lessons **directly on `main`** (see git history). This
overrides the default "branch first" behavior. Stage only the lesson plus the docs
you actually touched:

```bash
git add lessons/<NN-slug>/ lessons/README.md docs/logbook.md docs/sources.md
git status   # confirm ONLY the intended paths are staged (drop sources.md if untouched)
```

### 6. Commit message (fixed template)

```
docs: Phase 3 — build lesson NN (short title)

<one paragraph: what the lesson teaches>

<one paragraph: verification/registry impact — "No registry change" or what
changed and why; "Validator green"; "index + logbook updated">

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```

The `Co-Authored-By` trailer is mandatory and must be exactly this line.

### 7. Push

```bash
git push origin main
```

Report the resulting commit hash and the pushed ref range.

## Common mistakes

| Mistake | Fix |
|---|---|
| Deferring the push ("only if you ask") | Invoking this skill *is* the ask — push is in scope |
| Creating a feature branch | Commit directly on `main` — repo convention |
| Updating only the Session log | All three logbook edits: Session log + Current state + Next step |
| Editing `sources.md` with unverified content | Only verified-at-primary entries ever enter the registry |
| Committing before the validator/lint pass | Run the gate first; never ship red |
| Generic commit message / missing trailer | Use the fixed template + exact `Co-Authored-By` line |
| Shipping before user review | This skill runs *after* approval — never before |

## Not this skill

Writing or restructuring the lesson is `authoring-lessons`. This skill assumes the
lesson is written and approved; it only records and ships it.
