# Handbook Method

How we build this handbook — the pedagogical method, not the course content.
This is a living document; keep it in sync as the method evolves.

See [`CLAUDE.md`](../CLAUDE.md) for the working principles this method enforces,
especially the **Evidence and honesty** section.

## Audience and premise

The reader is an engineer who can program but is assumed to know nothing about
RAG or evaluation. Lessons are self-contained and build gradually: we introduce
what a RAG system is, then how to build and evaluate one.

## Principles

- **Theory before practice.** Concepts are introduced in dependency order; no
  lesson uses a concept a prior lesson has not introduced.
- **Evidence-first.** Every non-trivial claim is backed by a reputable source;
  code is executed and verified (not assumed); model and library versions are
  pinned. A lesson that asserts without a source is not done.
- **A lesson is one readable unit.** Its prose and its code live together, so it
  can be read and reviewed top to bottom.

## The phased method

- **Phase 0 — Learning machinery (one-time).** Define the lesson anatomy, the
  linking convention, the per-lesson definition of done, and the **source
  registry** ([`docs/sources.md`](./sources.md)) — the vetted list of sources we
  are allowed to cite. This operationalizes the evidence rules for the course.
- **Phase 1 — Research and concept map.** A wide-but-shallow sweep of the
  sources in the registry produces a *concept map*: the universe of concepts and
  their dependency edges, every node tagged with the registry entries that back
  it. The dependency graph is what makes the sequencing principled rather than
  arbitrary.
- **Phase 2 — Derive the syllabus from the map.** Topologically order the
  concept graph into modules and lessons; tag each lesson with its type and
  prerequisites; verify there are no forward references. **Approval gate.**
- **Phase 3 — Build lessons one at a time**, each through a mini-loop:
  research the lesson's specific sources → write the theory with citations → if
  practical, write **and run and verify** the code → self-review against the
  evidence rules → user review. Lessons ship sequentially so learning compounds
  and an error does not propagate.

## Research breadth

Wide-but-shallow upfront (Phase 1) — just enough for a sound map and index.
Deep, per-lesson research happens in Phase 3, when the lesson is written.

## Source registry

The registry ([`docs/sources.md`](./sources.md)) is the single allowed-list of
sources for the whole handbook. A source enters the registry only after it has
been **verified to exist** (fetched or searched against the primary source —
never added from memory). Each entry records:

- **Title** and **authors/organization**.
- **Venue and date** (conference/journal/year, or "official docs" + version).
- **URL** to the primary source.
- **Reputation tier** — `high` (peer-reviewed paper, official docs, standard) /
  `medium` (vendor engineering blog, maintained framework guide) / `low`
  (community write-up — supporting evidence only, never a sole citation).
- **One-line note** on what it is authoritative for.

Lessons cite only registry entries. A `## Sources` link in a lesson that is not
in the registry is a defect. The registry starts empty and is built in Phase 0 /
early Phase 1 by verifying candidate sources one by one.

## Repository structure

```
ragas_lab/            # shared, importable infra: config, clients, dataset loaders
lessons/
  NN-slug/            # one folder per lesson
    README.md         # the lesson (theory)
    demo.py           # lesson-specific code (only when the lesson has practice)
    data/             # tiny, lesson-specific sample data
datasets/             # corpora reused across lessons
tests/                # smoke tests for the scaffolding and ragas_lab
docs/                 # this method doc, the source registry, concept map, syllabus
```

Rule: **cross-cutting infrastructure goes in `ragas_lab/`; lesson-specific code
lives with the lesson.** A dataset reused by several lessons lives in
`datasets/`; a three-line example lives in `lessons/NN-slug/data/`.

## Lesson anatomy

Each lesson is a `README.md` whose header states its **type**, one of:

- `theory` — prose only.
- `theory+practice` — prose plus linked, runnable code.
- `practice` — a guided, runnable script with minimal framing.

A lesson README uses two structured sections plus free prose:

- **`## Prerequisites`** — markdown links (relative paths) to the lessons that
  must be understood first. This section is the **single source of truth for
  the dependency graph**: nothing else is treated as a prerequisite edge.

  ```markdown
  ## Prerequisites
  - [What is RAG](../01-what-is-rag/README.md)
  - [The RAG pipeline](../02-rag-pipeline/README.md)
  ```

- **`## Sources`** — external links (URLs) backing the lesson's claims, each
  with a reputation note. This enforces the evidence rule at the document level.

- **Free prose links.** Anywhere else, markdown links are navigation only —
  forward references ("we will see this in [lesson 8](...)"), "see also", the
  glossary. They are NOT dependency edges and are ignored when building the DAG.

Practice lessons link to their code and state how to run it.

## Dependency-tree reconstruction

To rebuild the graph: parse the `## Prerequisites` section of every
`lessons/**/README.md`, treat each linked path as an edge, and assemble the DAG.
This is deterministic — no heuristic guessing about which prose link is a
dependency. Use it to validate ordering (no lesson depends on a later one).

## Definition of done (per lesson)

A lesson is done only when:

- [ ] Every non-trivial claim cites a source in `## Sources`.
- [ ] Uncertainties are flagged in plain terms ("not verified", "needs confirmation").
- [ ] Model and library versions used are pinned/stated.
- [ ] If it has code, the code was executed and its real output is shown.
- [ ] `## Prerequisites` lists every concept the lesson relies on.
- [ ] Sources are rated for reputation; no blog/Medium post is the sole source
      for prescriptive guidance.
