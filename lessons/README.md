# lessons

One folder per lesson, in dependency order. See
[`docs/handbook-method.md`](../docs/handbook-method.md) for the lesson anatomy
and conventions.

## Index (built so far)

The full plan is [`docs/syllabus.md`](../docs/syllabus.md) (39 lessons); lessons
are built one at a time in syllabus order. Built so far:

| # | Lesson | Type | What it covers |
|---|--------|------|----------------|
| 01 | [LLMs, Tokens, and Prompting](./01-llms-tokens-and-prompting/README.md) | theory | What an LLM is & autoregressive generation; tokens & context window; prompting & in-context learning; sampling (temperature/top-p) |
| 02 | [Embeddings and Search](./02-embeddings-and-search/README.md) | theory | Embeddings & vector similarity (cosine); semantic vs keyword search; parametric vs non-parametric knowledge |
| 03 | [Why RAG, and What It Is](./03-why-rag-and-what-it-is/README.md) | theory | Why RAG exists; what RAG is; the index→retrieve→augment→generate pipeline; Naive/Advanced/Modular paradigms |
| 04 | [Architecture and Model Strategy](./04-architecture-and-model-strategy/README.md) | theory | RAG vs long-context; what fine-tuning is + RAG vs fine-tuning; RAFT; CAG; when *not* to use RAG; choosing the generator |

Each lesson:

- lives in its own folder (e.g. `01-what-is-rag/`);
- has a `README.md` whose header states its **type** (`theory` /
  `theory+practice` / `practice`);
- declares its dependencies in a `## Prerequisites` section (markdown links to
  other lessons) — the single source of truth for the dependency graph;
- cites its sources in a `## Sources` section (entries from
  [`docs/sources.md`](../docs/sources.md));
- keeps any lesson-specific code (e.g. `demo.py`) and tiny sample data
  (`data/`) alongside the `README.md`. Reusable infrastructure goes in
  [`ragas_lab/`](../ragas_lab/), not here.

## Running a lesson's code

From the repo root:

```bash
uv run python -m lessons.<NN-slug>.demo      # e.g. lessons.05-minimal-end-to-end-rag.demo
```

`uv run` uses the project venv; `python -m` puts the repo root on the import
path so the script resolves both its own package and `ragas_lab` (no
`__init__.py` or `PYTHONPATH` needed — these are namespace packages). Hyphenated
folder names work with `-m`. Equivalent fallback:
`PYTHONPATH=. uv run python lessons/<NN-slug>/demo.py`.

