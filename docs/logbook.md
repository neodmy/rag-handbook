# Logbook

Continuity log for this repository. **If you are an agent picking this up in a new
session, read this file first, then `CLAUDE.md`.** It tells you what we are
building, the rules you must follow, the decisions already made (and why — so you
don't relitigate them), and exactly where we left off.

Keep this file current: append a dated entry to **Session log** at the end of every
working session, and update **Current state** + **Next step**.

---

## What we are building

A **handbook / course to understand, build, and evaluate production-grade RAG
systems**, for an engineer who starts with **no prior RAG or evaluation
knowledge**. Practice paired with solid, sourced theory. Used by a team to build
the expertise to ship and evaluate client RAG systems to the highest standards.

> **Scope note (decided 2026-06-06):** this started as "evals of RAG applications"
> and deliberately grew into a **complete RAG course (build + evaluate)**. That
> reframe is intentional — do not treat the build-side content as scope creep.
> Evaluation remains a major pillar, not the whole course.

## Non-negotiable rules (read `CLAUDE.md` "Evidence and honesty" in full)

- **Verify before asserting.** Never state non-trivial facts about libraries,
  APIs, papers, or "best practices" from memory. Check the primary source.
- **Library docs → Context7; everything else → web fetch/search of the primary
  source.** Blogs/Medium are never a sole source for prescriptive claims.
- **Every source must be verified** before it enters `docs/sources.md`
  (primary page, or DOI via Crossref/Semantic Scholar when paywalled — flag it).
- **No reflexive agreement; correct the user with evidence; be brutally critical
  of your own output.** Bias coverage audits toward *flagging* gaps, not
  rationalizing coverage (we learned this the hard way — see Session log).
- **Every committed artifact is in English.** Don't mix languages in one file.
- **Code is executed, not assumed.** Show real output. Pin versions/models.

## The method (full detail in `docs/handbook-method.md`)

Phased build:
- **Phase 0 — learning machinery** (DONE): lesson anatomy, linking convention,
  source registry, definition of done, authoring skill.
- **Phase 1 — research + concept map** (DONE): verified source registry +
  dependency-ordered concept map.
- **Phase 2 — derive the syllabus** (NEXT): topologically order the concept map
  into modules → lessons; tag each lesson type + prerequisites; no forward refs.
  **Approval gate** before building lessons.
- **Phase 3 — build lessons one at a time** via the authoring skill, each with
  deep per-lesson source research, run+verify code, self-review, user review.

## Key artifacts

| File | What it is | Status |
|------|-----------|--------|
| `CLAUDE.md` | Working principles (evidence rules, language, lesson conventions). Read first. | Reframed to build+evaluate; points to this logbook. |
| `docs/handbook-method.md` | The pedagogical method + lesson anatomy + registry rules. | Reframed to build+evaluate. |
| `docs/sources.md` | Verified source registry (§1–§13). Lessons cite only from here. | ~78 sources, all verified. "To verify" section empty. |
| `docs/concept-map.md` | Concept universe + module dependency graph (M0–M13), each concept tagged to a source. | Expanded; already framed as "understand, build, and evaluate". All 151 tag refs resolve. |
| `.claude/skills/authoring-lessons/` | Skill to author lessons (SKILL.md + lesson-template.md + tested `scripts/validate_lesson.py`). | Working; validator tested. |
| `lessons/` | One folder per lesson (built in Phase 3). | Only `README.md` (conventions) — no lessons yet. |
| `ragas_lab/` | Shared importable infra: `config.py` (pydantic-settings), `clients.py` (RAGAS judge LLM + embeddings via Ollama). | Working; `uv run pytest` green. |
| `tests/` | Smoke tests for the scaffolding. | 2 passing. |

## Key decisions & gotchas (don't relitigate)

- **Naming**: project folder and pyproject `name` are **`rag-handbook`** (renamed
  2026-06-06 from `ragas` / `ragas-evals-handbook` when the scope broadened). The
  shared import package is still **`ragas_lab/`** — apt, as it holds the
  RAGAS-integration helpers; rename only if desired (touches `clients.py`, tests, docs).
- **Stack**: uv (Python 3.12), ruff, taskipy, pre-commit. `pyproject.toml` is a uv
  **virtual project** (`[tool.uv] package = false`, no `[build-system]`).
- **RAGAS pinned `==0.4.3`**, and **langchain pinned to the 0.3.x line**
  (`langchain<1.0`, `langchain-community<0.4`, `langchain-core<1.0`). This is a
  **deliberate workaround** for an upstream bug: ragas 0.4.3 hard-imports
  `langchain_community.chat_models.vertexai`, removed in community 0.4.x — with
  langchain 1.x, `import ragas` crashes. Do **not** "upgrade" these pins until a
  patched ragas releases (upstream issues vibrantlabsai/ragas #2741/#2745/#2753).
- **Ollama integration**: RAGAS 0.4.x uses its own `llm_factory`/`embedding_factory`
  with an **OpenAI-compatible client** pointed at Ollama — **not** langchain-ollama.
  See `ragas_lab/clients.py`. A local `.env` may point Ollama at a non-localhost IP.
- **Layout**: lesson-specific code lives in `lessons/<NN-slug>/`; reusable infra in
  `ragas_lab/`. Run a lesson's code from repo root: `uv run python -m
  lessons.<NN-slug>.demo` (hyphenated dir names work with `-m`; verified).
- **Lesson conventions** (enforced by the validator): header `**Type:**`
  (theory | theory+practice | practice); `## Prerequisites` = markdown links =
  the ONLY dependency-graph edges; `## Sources` = links to registry entries only;
  prose links elsewhere are navigation, not edges.
- **Source registry tiers**: high (peer-reviewed / official docs / standard),
  medium (cited preprint / official model card / single-vendor), low. Paywalled
  primaries confirmed via Crossref/Semantic Scholar DOI and flagged as such.
- **Git**: repo is `git init`-ed but **nothing is committed yet** — the entire
  working state is untracked. Commit only when the user asks.

## Current state (as of 2026-06-06)

- Phases 0 and 1 complete. Concept map expanded after **two adversarial audits**
  (a 3-lens pass, then a deeper 5-lens pass) to a full build+evaluate scope:
  M0 primer, M1 foundations, M2 ingestion+retrieval, M3 generation/grounding,
  M4–M12 evaluation (foundations, retrieval eval, generation metrics, faithfulness,
  LLM-judge, metric suites, datasets/benchmarks, statistics, production/ops &
  governance), M13 advanced techniques.
- Source registry at ~78 verified entries across §1–§13; "To verify" is empty.
- Scope just reframed to a **complete RAG course** (user decision, 2026-06-06).

**Phase 2 — derive the syllabus** (`docs/syllabus.md`): order the concept map
into modules → lessons, each with type + `## Prerequisites`; verify no forward
references; present for the **approval gate** before any lesson is written.

(Scope alignment across `CLAUDE.md`, `README.md`, `handbook-method.md`, and the
authoring skill/template is **done** — all now framed as "build + evaluate".)

## Open threads / backlog

- Deferred nice-to-haves (add only if a lesson needs them, with a verified source
  first): late-interaction retrieval (ColBERT), GraphRAG, multimodal RAG, semantic
  caching, judge calibration, safety/toxicity eval, multi-turn/conversational eval.
- Consider recording in `handbook-method.md` the rule "coverage audits bias toward
  flagging" (lesson from this session).
- Commit the base state when the user approves.

---

## Session log

### 2026-06-05 / 06 — Setup + Phase 0 & 1
- Scaffolded the uv project (ruff, taskipy, pre-commit); hit and worked around the
  RAGAS↔langchain-1.x import bug (pinned langchain 0.3.x); wired Ollama via RAGAS
  `llm_factory` (OpenAI-compatible), not langchain-ollama.
- Restructured to `ragas_lab/` (shared) + `lessons/<slug>/` (co-located code);
  retired the initial `evals/`/`experiments/` flat layout.
- Wrote the method (`handbook-method.md`), the `authoring-lessons` skill +
  tested validator, the source registry (`sources.md`), and the concept map
  (`concept-map.md`).
- Built the registry research-first via verification subagents; **only verified
  sources admitted**; resolved paywalls via Crossref.
- Ran two coverage audits. First was too conservative (missed vector stores);
  second (5-lens, bias-to-flag) surfaced ingestion, foundations/primer,
  governance, and eval-methodology gaps — all added with newly verified sources.
- **Decision:** reframed the handbook from "evals of RAG" to a **complete RAG
  course (build + evaluate)**.
- Aligned all docs to the new scope (CLAUDE.md, README.md, handbook-method.md,
  authoring skill + template). Wrote this logbook.
- Renamed project `ragas` → `rag-handbook` (folder + pyproject `name`); rebuilt
  the venv at the new path; pytest + ruff green.
- **Left off at:** ready to start Phase 2 (syllabus). Nothing committed to git yet.

### 2026-06-06 — Concept-map module renumbering
- Renumbered the concept map: the old `M-1` primer is now `M0`, and every later
  module shifted +1 (old `M0`→`M1`, … old `M12`→`M13`). New range: **M0–M13**.
- Updated `concept-map.md` end to end (Mermaid graph node IDs + labels, all 14
  headers, every `(needs …)` cross-module note, the "Coverage check" callouts)
  and the two module-range references in this logbook. No other doc referenced
  module numbers (verified by grep). Source `[§N: …]` tags untouched.
