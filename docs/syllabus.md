# Syllabus

The ordered lesson plan for the handbook, derived from
[`concept-map.md`](./concept-map.md) by topologically ordering its concepts into
lessons (Phase 2 — see [`handbook-method.md`](./handbook-method.md)). This is the
**teaching sequence**; the concept map is the concept graph it comes from.

> **Status: APPROVED (2026-06-06).** No lessons are written yet. Phase 3 builds
> them one at a time, starting next session with lesson 01 (deep per-lesson
> research → write → run+verify code → self-review → user review).

## Design principle: baseline early, then eval-driven and progressive

The arc is deliberately **not** "build everything, then learn to measure." After
the foundations we stand up a **minimal, runnable end-to-end RAG** (lesson 05) so
there is a working system to reason about, and we introduce **why evaluation is
hard** immediately after (lesson 06). From there each stage follows
**build → measure → improve**: build retrieval → evaluate retrieval → improve it
(query understanding); build generation → evaluate generation; then whole-pipeline
suites, methodology, production, and advanced patterns.

**Methodology is taught progressively too.** The moment the learner first makes an
"X improved Y" claim (the first improvement step, query transformation) they get a
short **"is the delta real?"** primer (held-out discipline + significance/power,
lesson 22); the deeper measurement-validity methodology (agreement, human
instruments, correlation, the formal eval-driven loop) lands as a capstone (35).

## How to read this

- Lessons are in **global teaching order** (`01 … 38`); the number is the folder
  prefix (`lessons/NN-slug/`). The order is a topological sort — **every
  prerequisite has a lower number than the lesson that needs it** (no forward
  references; verified at the end).
- Each lesson is tagged with its **source module** (M0–M14), its **type**
  (`theory` / `theory+practice` / `practice`), the **concepts** it covers, and its
  **prereqs** (by lesson number — these become the `## Prerequisites` links in
  Phase 3).
- **Parts** are a reading aid (the teaching arc), not a dependency unit.

---

## Part I — Foundations & a working baseline (M0, M1, M5)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 01 | `llms-tokens-and-prompting` | theory | M0 | What an LLM is & autoregressive generation; tokens & context window; prompting & in-context learning; sampling (temperature/top-p) | — |
| 02 | `embeddings-and-search` | theory | M0 | Embeddings & vector similarity; semantic vs keyword search; parametric vs non-parametric knowledge | 01 |
| 03 | `why-rag-and-what-it-is` | theory | M1 | Why RAG exists; what RAG is; the index→retrieve→augment→generate pipeline; naive/advanced/modular paradigms | 01, 02 |
| 04 | `architecture-and-model-strategy` | theory | M1 | RAG vs long-context; **what fine-tuning is** + RAG vs fine-tuning; RAFT; CAG; when NOT to use RAG; choosing the generator | 03 |
| 05 | `minimal-end-to-end-rag` | theory+practice | M1 (integrative) | Wire a **runnable naive RAG** end-to-end (load→chunk→embed→retrieve→generate) with a framework; introduces the orchestration-framework layer; the baseline we improve | 04 |
| 06 | `why-evaluation-is-hard` | theory | M5 | Eval targets (retrieval vs generation); ref-based vs ref-free; offline vs online; error attribution & recall ceiling; eval design/ablation; abstention & robustness as targets | 05 |

## Part II — Ingestion (M2)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 07 | `document-loading-and-parsing` | theory+practice | M2 | Loading/parsing PDF/HTML/scanned files; layout-aware extraction; tables | 05 |
| 08 | `cleaning-and-deduplication` | theory+practice | M2 | Cleaning, normalization; near-duplicate removal | 07 |
| 09 | `chunking-strategies` | theory+practice | M2 | Fixed-size vs structural/semantic chunking; chunk size & retrieval granularity | 07 |
| 10 | `metadata-and-chunk-enrichment` | theory+practice | M2 | Metadata extraction; contextual retrieval (chunk-specific enrichment before indexing) | 09 |

## Part III — Retrieval: build (M3 core)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 11 | `embeddings-and-model-selection` | theory+practice | M3 | Dense embeddings in practice; embedding-model selection & adaptation (briefly introduces MTEB — formal treatment in 21) | 02, 09 |
| 12 | `sparse-retrieval-bm25` | theory+practice | M3 | TF-IDF, Okapi BM25 | 02, 09 |
| 13 | `dense-retrieval-dpr` | theory+practice | M3 | Dual-encoder / DPR retrieval | 11 |
| 14 | `vector-indexes-and-ann` | theory+practice | M3 | HNSW, FAISS; recall vs throughput | 13 |
| 15 | `vector-store-selection` | theory | M3 | Store taxonomy (native VDBMS / pgvector / search engines) and how to choose | 14 |
| 16 | `hybrid-retrieval-and-reranking` | theory+practice | M3 | Lexical+semantic hybrid; cross-encoder / seq2seq reranking | 12, 13, 14 |
| 17 | `parent-doc-and-metadata-filtering` | theory+practice | M3 | Parent-document / small-to-big; metadata filtering & index lifecycle | 14, 10 |
| 18 | `vector-layer-engineering` | theory+practice | M3 | Quantization (PQ/int8/binary); Matryoshka/truncatable dims; ANN tuning & capacity planning | 14 |
| 19 | `structured-data-and-text-to-sql` | theory+practice | M3 | Retrieval over relational/tabular data; text-to-SQL; schema linking | 14 |

## Part IV — Retrieval: evaluate & improve (M6, M12 primer, M3 query understanding)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 20 | `retrieval-metrics` | theory+practice | M6 | Relevance & qrels (Cranfield/TREC); precision@k/recall@k; MRR/MAP; DCG/nDCG | 14, 06 |
| 21 | `retrieval-benchmarks` | theory | M6 | BEIR, MTEB | 20 |
| 22 | `interpreting-results` | theory+practice | M12 (primer) | Held-out discipline / don't tune on test; "is the delta real?" — significance (bootstrap/randomization) & statistical power / sample size, at working depth | 20 |
| 23 | `query-transformation` | theory+practice | M3 | Query rewriting; HyDE; query expansion / relevance feedback | 16, 20, 22 |
| 24 | `query-decomposition-routing-fusion` | theory+practice | M3 | Query decomposition (Self-Ask); routing / "retrieve or not"; fusion (RAG-Fusion + RRF); conversational contextualization | 23 |

## Part V — Generation: build (M4)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 25 | `grounded-generation-and-prompt-design` | theory+practice | M4 | Generation conditioned on context; augmentation-prompt design (delimiters/XML, source tags, system prompt, quote-first) | 04, 14 |
| 26 | `synthesis-curation-and-position` | theory+practice | M4 | Multi-chunk synthesis (stuff/refine/tree-summarize/accumulate); context curation; "lost in the middle" / ordering | 25 |
| 27 | `faithfulness-abstention-and-citations` | theory+practice | M4 | Faithfulness/groundedness; hallucination types; generation-time abstention; citation/attribution generation | 25 |
| 28 | `structured-output-and-streaming` | theory+practice | M4 | Structured/constrained output (JSON-schema vs JSON mode vs tool calling); response streaming | 25 |
| 29 | `rag-security-prompt-injection` | theory | M4 | Indirect prompt injection (retrieved content is attacker-controlled); threat model & mitigations; OWASP LLM01 — cross-links production guardrails/ACL (37) | 25 |

## Part VI — Generation: evaluate (M7, M8, M9)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 30 | `classical-generation-metrics` | theory+practice | M7 | BLEU/ROUGE/METEOR; BERTScore; why overlap metrics fail; answer correctness vs ground truth | 25, 06, 22 |
| 31 | `faithfulness-measurement` | theory+practice | M8 | NLI (FactCC/SummaC); FActScore; SelfCheckGPT; HHEM; TruthfulQA/RAGTruth; citation-quality eval | 27, 06 |
| 32 | `llm-as-a-judge` | theory+practice | M9 | LLM-judge idea & validity; G-Eval recipe; judge biases; robustness (LLMBar); reproducibility | 30, 31 |

## Part VII — Whole-pipeline evaluation & methodology (M10, M11, M12)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 33 | `rag-metric-suites` | theory+practice | M10 | RAGAS (faithfulness, context precision/recall, answer relevancy, noise sensitivity); the RAG triad; ARES; DeepEval | 20, 25, 32 |
| 34 | `datasets-and-synthetic-generation` | theory+practice | M11 | QA datasets; RAG benchmarks; synthetic test-set generation; **eval-methodology surveys / best practices**; golden-set building; contamination & held-out discipline | 20, 33 |
| 35 | `measurement-validity-and-methodology` | theory+practice | M12 | Inter-annotator agreement (kappa/alpha); human-eval instruments (Likert/pairwise/BWS); metric↔human correlation; significance/power in depth; the formal eval-driven-development loop | 22, 32 |

## Part VIII — Production (M13)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 36 | `online-eval-and-observability` | theory+practice | M13 | Online vs offline; A/B & interleaving; observability/tracing (OTel/LangSmith/Phoenix/Langfuse); CI eval & drift; HITL; cost/latency | 33 |
| 37 | `governance-and-safe-operation` | theory | M13 | Request-path reliability (timeouts/retries/fallbacks); security/ACL; guardrails; PII/governance/right-to-erasure; versioning & safe rollout; feedback loops; business vs technical metrics | 36 |

## Part IX — Advanced RAG (M14)

| # | Lesson | Type | Module | Covers | Prereq |
|---|--------|------|--------|--------|--------|
| 38 | `iterative-and-agentic-rag` | theory+practice | M14 | Multi-hop / iterative retrieval (IRCoT/FLARE/Iter-RetGen); self-correcting RAG (Self-RAG/CRAG); agentic RAG | 16, 25, 33 |

---

## Sequencing notes & judgment calls

1. **Eval-driven & progressive arc.** "Why evaluation is hard" at 06 (after a
   runnable baseline at 05); retrieval eval (20–21) follows retrieval build
   (11–19); generation eval (30–32) follows generation build (25–29); whole-pipeline
   suites at 33.
2. **Methodology taught when first needed.** The `interpreting-results` primer (22)
   — held-out discipline + "is the delta real?" — sits right before the first
   improvement (23), so every "X improved Y" claim from then on is made with the
   right hygiene. The deep measurement-validity methodology is the capstone (35),
   which builds on 22.
3. **Quickstart (05).** Runnable naive RAG via a framework — "see it work, then
   dissect." Integrative (realizes the M1 pipeline across M2–M4 at toy depth); also
   where the orchestration-framework layer is named.
4. **Query understanding (23–24) after retrieval eval (20–22).** Honors the
   concept-map note (tuned/evaluated with retrieval metrics). Module M3 is therefore
   non-contiguous (11–19 build, 23–24 improve) — by design.
5. **Security split (29).** Indirect prompt injection is OWASP LLM01 and uniquely
   acute in RAG (retrieved content is untrusted input), so it is its own build-time
   lesson rather than a tail on output mechanics; it cross-links the production
   guardrails/ACL lesson (37).
6. **Cheap audit fixes applied:** MTEB introduced in 11 (formal treatment 21);
   "what fine-tuning is" framed in 04; eval-methodology surveys named in 34; RAGAS
   (33) lists generation (25) as a prereq.
7. **Production (36/37).** Kept to two lessons; request-path **reliability** moved
   from observability (36) into safe-operation (37), where it belongs.

## No-forward-reference check

Every lesson's prerequisites have strictly lower numbers than the lesson itself
(verified by script). The sequence is a valid topological order of the per-lesson
dependency graph, and respects the concept-map module edges: ingestion (M2) →
retrieval (M3) → retrieval eval (M6) → query understanding (M3); generation (M4) →
generation/faithfulness eval (M7/M8) → judge (M9) → suites (M10) →
datasets/methodology (M11/M12) → production (M13); advanced (M14) last. The M12
"interpreting-results" primer (22) is a deliberate early slice of statistical
methodology placed at the first system comparison.

## Coverage check

Every concept-map module M0–M14 is represented by ≥1 lesson:
M0→01–02 · M1→03–05 · M2→07–10 · M3→11–19, 23–24 · M4→25–29 · M5→06 · M6→20–21 ·
M7→30 · M8→31 · M9→32 · M10→33 · M11→34 · M12→22, 35 · M13→36–37 · M14→38.
Lesson 05 is an extra integrative baseline (no new concept; realizes the pipeline).
