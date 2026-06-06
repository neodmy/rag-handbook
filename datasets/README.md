# datasets

Evaluation datasets with ground truth. Each RAGAS metric needs specific
fields, so record which columns a dataset provides:

- `user_input` — the question
- `response` — the system's generated answer
- `retrieved_contexts` — the chunks the retriever returned
- `reference` — the ground-truth answer (needed by metrics like context recall
  and answer correctness)

Keep raw data versioned here so experiments are reproducible. Note the source
and how ground truth was produced — a dataset is only as trustworthy as its
labels.
