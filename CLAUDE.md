# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Returning in a later session, or picking this up fresh? Read [`docs/logbook.md`](./docs/logbook.md) first — it has the current status, decisions made, and where we left off.

## Repository purpose

Learning repository / handbook for **understanding, building, and evaluating production-grade RAG applications** (retrieval-augmented generation) — with **RAGAS** and the wider evaluation toolkit as a major pillar. Stated goal: learn from practice, but with a solid theoretical foundation. Every piece of code should come with the rationale for *why* something is measured and *what* the metric means — not just the how.

This repository is a learning artifact: the team uses it to build the expertise needed to build and evaluate production-grade RAG systems to the highest standards. What gets committed here becomes the shared reference the team studies and builds on later, so correctness compounds — and so does any error left unchecked.

> Current state: scaffolded — uv project (Python 3.12), ruff, taskipy, pre-commit, and RAGAS pinned to `0.4.3` are in place; git is initialized. See the Commands and Architecture sections below. Keep them in sync as the project grows; do not invent structure that does not exist.

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

_(TBD: add build/test/run once the environment manager is chosen — e.g. `uv`, `poetry`, or `pip` + venv. RAGAS is a Python library.)_

## Architecture

_(TBD: document the structure once code exists — typically: ingestion/indexing, RAG pipeline, evaluation datasets with ground truth, and the RAGAS eval scripts.)_
