---
name: authoring-lessons
description: Author, organize, and structure a handbook lesson using grounded pedagogy (gradual release of responsibility + comprehension checks) plus this repo's evidence rules and lesson format. Use when writing a new lesson, restructuring an existing one, or turning a researched concept into teachable theory and practice under lessons/.
when_to_use: Trigger when the task is to write or restructure a lesson in lessons/, draft teaching material for a RAG concept (building or evaluating), or convert a researched topic into a lesson. Not for the research/verification sweep itself (delegate that to a research subagent) or for non-teaching prose.
argument-hint: "[lesson-topic-or-slug]"
arguments: topic
---

# Authoring a handbook lesson

Write lessons that teach a production-RAG concept — building or evaluating — to an
engineer with **no prior RAG or evals knowledge**, building up gradually, theory
before practice. This
skill applies an established pedagogy — it does not invent one — and enforces the
repo's evidence discipline and lesson format.

Read first (from the repo root): `docs/handbook-method.md` (the method) and the
**Evidence and honesty** section of `CLAUDE.md` (non-negotiable). This skill
operationalizes both for a single lesson.

## When NOT to use this

- The broad source sweep and source verification → delegate to a research
  subagent; it returns verified material you then teach from. Writing stays here.
- Editing `ragas_lab/` or non-lesson docs.

## The authoring workflow

1. **Place the lesson.** Confirm its number/slug and its prerequisites (which
   earlier lessons it depends on). Never use a concept a prior lesson has not
   introduced — check the dependency order in the syllabus / concept map.
2. **Decide the type:** `theory` | `theory+practice` | `practice`.
3. **Gather verified sources** for *this* lesson (or take them from the research
   subagent's output). Every non-trivial claim must map to an entry that is —
   or will be added to — `docs/sources.md`. Do not write claims you cannot source.
4. **Outline against the structure below**, then write.
5. **If the lesson has practice:** write the code in the lesson folder, **run it**
   with `uv run python -m lessons.<slug>.demo`, and paste the **real** output.
   Never show output you did not produce.
6. **Self-review** against the Definition of Done. Run the validator
   (`scripts/validate_lesson.py`).
7. **Update the index.** Add a row for the new lesson to the "Index (built so
   far)" table in `lessons/README.md` (number, linked title, type, one-line
   coverage). This table lists only built lessons; the full plan stays in
   `docs/syllabus.md`.
8. **Hand to the user** for review before moving on. One lesson at a time.

## Lesson structure (gradual release, adapted to written self-study)

The backbone is the **gradual release of responsibility** ("I do → we do → you
do"): exposition where you carry the reasoning, then a worked example you walk
through, then a task the reader does alone. Adapt sections to the lesson type —
a `theory` lesson stops after the concept and a check; a `practice` lesson is
mostly the guided + independent parts.

```
# Lesson NN — Title

**Type:** theory+practice

> One sentence: what the reader will be able to do / understand after this.

## Prerequisites
- [Earlier lesson](../NN-slug/README.md)        # markdown links = the ONLY graph edges

## Why this matters
Motivate the concept before defining it. Where it sits in the RAG picture.

## The concept   (the "I do": explain WITH the reasoning, not just facts)
Introduce one concept at a time, concrete before abstract. Define terms on first
use. Show the *why* behind each claim, each claim backed by a source.

## Worked example   (the "we do": walk through it together)
Step through a concrete case, narrating each decision. For practice lessons this
references the runnable code and its real output.

## Your turn   (the "you do": the reader acts)
A small exercise or task. For practice lessons: the script to run and what to
observe / change.

## Common pitfalls / misconceptions
What learners get wrong here, and the correction.

## Check your understanding
2-4 genuine questions (not "did you read this?"). Prefer questions that surface
misconceptions. (Socratic style: questions that develop thinking, never leading.)

## Summary & next
What was established; the link forward to what builds on it.

## Sources
- [Title](https://primary-source) — what it backs (entry in docs/sources.md)
```

## Comprehension checks

Use genuine questions that make the reader reconstruct the idea, not recall
trivia. Favor ones that expose the typical misconception for the topic. Never
phrase a leading question that funnels to a predetermined answer.

## Evidence & format requirements (hard)

- Every non-trivial claim cites a `## Sources` entry; sources live in
  `docs/sources.md` (verified, reputation-rated). No blog/Medium as a sole
  source for prescriptive guidance.
- Flag uncertainty in plain terms ("not verified", "needs confirmation").
- Pin library/model versions used (RAGAS version, judge/embedding models).
- Code is executed; show real output.
- `## Prerequisites` is the single source of truth for the dependency graph;
  free prose links elsewhere are navigation only.

## Definition of Done (run `scripts/validate_lesson.py <lesson-dir>`)

- [ ] Header declares a valid **Type**.
- [ ] `## Prerequisites` present; every linked path exists.
- [ ] `## Sources` present and non-empty; claims trace to it.
- [ ] Uncertainties flagged; versions/models pinned.
- [ ] If practice: code ran, real output shown.
- [ ] No forward reference to a concept not yet introduced.

## Pedagogical grounding

The method here rests on established education research, not invention:

- **Gradual release of responsibility** (Pearson & Gallagher) and **explicit
  instruction** (Rosenshine; Archer & Hughes) — the I-do / we-do / you-do spine.
- **Self-explanation / elicit-then-explain** (Chi) — the comprehension checks.
- **Socratic questioning taxonomy** (Paul & Elder) — question quality, no leading.

Adapted from these public education skills (Agent Skills format), reframed from
live-classroom delivery to written self-study and fused with our evidence rules:
GarethManning/education-agent-skills (`explicit-instruction-sequence-builder`,
`socratic-questioning-sequence-generator`, `explain-first-interrogator`).

Honesty note: the author names above are the recognized basis for these methods,
stated from general knowledge. **Before citing any of them in learner-facing
prose, verify the reference and add it to `docs/sources.md`** — the same rule
every other claim follows.
