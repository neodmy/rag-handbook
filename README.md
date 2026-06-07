# rag-handbook

Learn to **understand, build, and evaluate production-grade RAG applications**
(retrieval-augmented generation) from practice, with a solid theoretical
foundation — **RAGAS** and the wider evaluation toolkit are a major pillar. Every
lesson pairs runnable code with the *why*: how each part works, how to build it,
and how to tell whether it works.

See [`CLAUDE.md`](./CLAUDE.md) for the working principles — especially the
**Evidence and honesty** rules that govern what gets committed here — and
[`docs/logbook.md`](./docs/logbook.md) for current status and continuity.

## Lessons

The handbook is the lessons. **Start here → [`lessons/`](./lessons/README.md)**
for the index of lessons built so far; the full plan is in
[`docs/syllabus.md`](./docs/syllabus.md) (39 lessons, built one at a time in
dependency order).

Some lessons carry a reference appendix alongside them — e.g.
[`lessons/07-…/appendix-parsing-tools.md`](./lessons/07-document-loading-and-parsing/appendix-parsing-tools.md),
a verified catalogue of PDF / OCR / HTML parsing tools.

## Stack

- **uv** — environment + dependency management (`.python-version` pins 3.12)
- **ruff** — lint + format
- **taskipy** — task runner (tasks defined in `pyproject.toml`)
- **pre-commit** — ruff + conventional-commit message checks on commit
- **RAGAS** — pinned to `0.4.3` (pre-1.0; the API can break between minors)
- **Ollama** — local judge LLM + embeddings via its OpenAI-compatible API

## Setup

```bash
uv run task setup          # uv sync + install git hooks
cp .env.sample .env        # then adjust models/endpoint if needed
```

Practice lessons need Ollama running with the models pulled:

```bash
ollama serve
ollama pull mistral            # judge LLM (OLLAMA_JUDGE_MODEL)
ollama pull nomic-embed-text   # embeddings  (OLLAMA_EMBED_MODEL)
```

## Common commands

```bash
uv run task test           # pytest (smoke tests need no network)
uv run task lint           # ruff check .
uv run task format         # ruff format .
uv run task hooks-run      # pre-commit on all files
```

## Layout

```
.
├── ragas_lab/         # shared, importable infra: config, clients, dataset loaders
├── lessons/           # one folder per lesson (README.md theory + lesson code)
├── datasets/          # evaluation datasets with ground truth, reused across lessons
├── docs/              # handbook method, source registry, concept map, syllabus
└── tests/             # smoke tests for the scaffolding and ragas_lab
```

Shared modules live in `ragas_lab/`; lesson-specific code lives with each lesson.
`pythonpath = ["."]` (in `pyproject.toml`) puts the repo root on the import path
so tests and lesson scripts can `import ragas_lab.*` without an installable
package. See [`docs/handbook-method.md`](./docs/handbook-method.md) for how
lessons are structured.
