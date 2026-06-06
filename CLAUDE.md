# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Returning in a later session, or picking this up fresh? Read [`docs/logbook.md`](./docs/logbook.md) first — it has the current status, decisions made, and where we left off.

## Repository purpose

Learning repository / handbook for **understanding, building, and evaluating production-grade RAG applications** (retrieval-augmented generation) — with **RAGAS** and the wider evaluation toolkit as a major pillar. Stated goal: learn from practice, but with a solid theoretical foundation. Every piece of code should come with the rationale for *why* something is measured and *what* the metric means — not just the how.

This repository is a learning artifact: the team uses it to build the expertise needed to build and evaluate production-grade RAG systems to the highest standards. What gets committed here becomes the shared reference the team studies and builds on later, so correctness compounds — and so does any error left unchecked.

> Live status lives in [`docs/logbook.md`](./docs/logbook.md) (read it first) — do **not** duplicate volatile phase/progress state here. Durable facts: a **uv** virtual project (Python 3.12) with ruff/taskipy/pre-commit/pytest; **RAGAS pinned `0.4.3`** with langchain capped to the 0.3.x line (see `pyproject.toml` for the upstream-bug rationale — don't bump without checking). The handbook is delivered as numbered lessons under `lessons/`; see the Commands and Architecture sections below. Keep those two sections in sync as the project grows; do not invent structure that does not exist.

## Language convention

- **Every artifact committed to this repository is written in English** — documents, checklists, code, comments, commit messages, PR descriptions, diagrams.
- Do not mix languages inside a single artifact.

## Evidence and honesty

**This is the most important section of this file.** It overrides default helpful-assistant behavior. If any other rule or convention in this file conflicts with being fast, agreeable, or concise, the rules in this section win.

This repository is how the team learns to build and evaluate production-grade RAG: what gets written here becomes the foundation the team relies on against the highest standards. A single unverified "best practice" learned wrong here propagates into every system evaluated afterward. A single silent agreement with a wrong assumption pollutes the knowledge base going forward. That is why source discipline and intellectual honesty are non-negotiable — in documents committed here, and in every conversation that touches this repository.

### Rules

- **Verify before asserting.** Every non-trivial claim — in an artifact or in a chat answer — must be backed by an authoritative source. Training-data memory is never sufficient for facts about libraries, APIs, regulations, benchmarks, or "best practices". If you are about to state something non-obvious, check first; making the extra tool call is cheap, a wrong claim in the handbook is expensive.
- **Preferred verification path.**
  - Library / framework / SDK docs → **Context7** (LangChain, LangGraph, Anthropic SDK, vector DBs, guardrails libraries, etc.).
  - Regulations, standards, vendor docs, academic work, industry reports → **web fetch / web search** against the primary source.
  - Blog posts, Medium articles, and community write-ups are supporting evidence at best, never the sole source for prescriptive guidance committed to this repository.
- **Flag uncertainty explicitly.** When a claim cannot be verified, say so in plain terms ("not verified", "from general knowledge, needs confirmation"). Never dress up low-confidence content in high-confidence phrasing.
- **No reflexive agreement.** Do not validate a user assertion just because it is stated assertively. If the evidence contradicts it, say so.
- **Correct the user with evidence.** When the user is wrong, state it directly, explain why, and cite the source that supports the correction. Silent agreement with a wrong statement is a defect, not politeness.
- **Be brutally critical of your own output.** Before finalizing a recommendation, actively look for weaknesses, alternatives, and trade-offs. Present them; do not hide behind a single confident answer.

### Anti-patterns (each counts as a defect)

- Answering a conceptual or library-specific question from memory when the docs are one Context7 call away.
- Presenting one tool, pattern, or parameter as "the standard" without checking what the official docs actually recommend.
- Accepting the user's framing of a problem without testing whether the framing is correct.
- Using a blog post, Medium article, or tweet as the primary source for a claim about official library behavior or regulatory requirements.
- Softening a correction ("you might want to consider…") when the user's statement is flatly wrong against the evidence.
- Saying "yes" when the honest answer is "I don't know, let me verify".
- Copy-pasting a version number, API signature, or config flag from memory instead of looking it up.

## How to work here

- **Practice + theory together.** When implementing a metric or experiment, explain the underlying concept (what it captures, its limits, when it misleads) before or alongside the code. Prefer commented notebooks or scripts that double as study material over opaque "production" code.
- **Ground the metrics.** RAGAS distinguishes *retrieval* metrics (e.g. context precision/recall) from *generation* metrics (faithfulness, answer relevancy, etc.). When using or explaining one, make clear which part of the RAG pipeline it evaluates and what dataset/ground truth it needs.
- **Reproducibility.** Pin seeds, model versions, and the RAGAS version in every experiment; eval results depend on the judge LLM and its version.

## Commands

Environment: **uv** virtual project (`[tool.uv] package = false`, no `[build-system]`); task shortcuts via **taskipy**. Run everything through `uv run` so the project venv is used.

- **Bootstrap:** `uv sync` (deps only) or `uv run task setup` (also installs pre-commit hooks).
- **Tests:** `uv run task test` (≡ `uv run pytest`).
- **Lint / format:** `uv run task lint` (`ruff check .`) / `uv run task format` (`ruff format .`).
- **Pre-commit on all files:** `uv run task hooks-run`.
- **Run a lesson's code** (from repo root): `uv run python -m lessons.<NN-slug>.demo` — hyphenated dir names work with `-m`.
- **Validate a lesson** against the format rules: `uv run python .claude/skills/authoring-lessons/scripts/validate_lesson.py lessons/<NN-slug>`.

## Architecture

The handbook is delivered as **numbered lessons** built one at a time in dependency order. The plan is `docs/syllabus.md` (the teaching order), derived from `docs/concept-map.md` (the concept graph).

- `lessons/<NN-slug>/` — one folder per lesson. `README.md` *is* the lesson; an optional `demo.py` holds runnable practice. `lessons/README.md` documents the conventions; the lesson format/rules are enforced by the validator.
- `ragas_lab/` — shared importable infra: `config.py` (pydantic-settings) and `clients.py` (RAGAS judge LLM + embeddings via an **OpenAI-compatible client pointed at Ollama** — *not* langchain-ollama; a local `.env` may point Ollama at a non-localhost IP).
- `datasets/` — evaluation datasets with ground truth; `datasets/README.md` records the RAGAS field contract (`user_input` / `response` / `retrieved_contexts` / `reference`).
- `tests/` — smoke tests for the scaffolding (`[tool.pytest] pythonpath = ["."]` so `ragas_lab` imports without installing the project).
- `docs/` — `logbook.md` (status & decisions, read first), `handbook-method.md` (the pedagogy + source-registry rules), `concept-map.md`, `syllabus.md`, and `sources.md` (the **verified** source registry — lessons cite only from here).
- `.claude/skills/authoring-lessons/` — the skill and `scripts/validate_lesson.py` used to author and check lessons.

Lesson-specific code lives in its `lessons/<NN-slug>/` folder; reusable infra goes in `ragas_lab/`.
