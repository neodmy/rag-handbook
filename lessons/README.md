# lessons

One folder per lesson, in dependency order. See
[`docs/handbook-method.md`](../docs/handbook-method.md) for the lesson anatomy
and conventions.

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
uv run python -m lessons.<NN-slug>.demo      # e.g. lessons.03-faithfulness.demo
```

`uv run` uses the project venv; `python -m` puts the repo root on the import
path so the script resolves both its own package and `ragas_lab` (no
`__init__.py` or `PYTHONPATH` needed — these are namespace packages). Hyphenated
folder names work with `-m`. Equivalent fallback:
`PYTHONPATH=. uv run python lessons/<NN-slug>/demo.py`.

