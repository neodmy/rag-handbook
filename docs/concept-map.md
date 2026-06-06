# Concept map

The universe of concepts a practitioner must master to **understand, build, and
evaluate** a production RAG system — and the dependency order between them. This
is the Phase-1 artifact (see [`handbook-method.md`](./handbook-method.md)); the
syllabus (Phase 2) is derived from it by topologically ordering these concepts
into lessons.

**Every concept is anchored to a verified source** in
[`sources.md`](./sources.md); the `[§N: short-name]` tags point there. A concept
with no backing source does not belong here.

## How to read this

- **Modules** (M0–M14) are thematic clusters. The arrows below are the
  module-level dependency graph — what must be understood before what.
- Inside each module, concepts are listed in learning order; inline `(needs …)`
  notes mark cross-module prerequisites.
- This is the *concept* graph, not the lesson list. Lesson granularity and the
  per-lesson `## Prerequisites` edges are decided in Phase 2 from this map.

```mermaid
graph TD
  M0[M0 Primer] --> M1[M1 Foundations]
  M1 --> M2[M2 Ingestion]
  M2 --> M3[M3 Retrieval & query]
  M1 --> M4[M4 Generation & grounding]
  M1 --> M5[M5 Why eval is hard]
  M3 --> M6[M6 Retrieval evaluation]
  M5 --> M6
  M4 --> M7[M7 Generation metrics]
  M5 --> M7
  M4 --> M8[M8 Faithfulness detection]
  M5 --> M8
  M7 --> M9[M9 LLM-as-a-judge]
  M8 --> M9
  M8 --> M10[M10 RAG metric suites]
  M9 --> M10
  M6 --> M10
  M6 --> M11[M11 Datasets & benchmarks]
  M10 --> M11
  M9 --> M12[M12 Statistical rigor]
  M6 --> M12
  M10 --> M13[M13 Production eval & ops]
  M3 --> M14[M14 Iterative & agentic RAG]
  M4 --> M14
  M10 --> M14
```

---

## M0 — Primer (foundations assumed by everything below)

For readers with no LLM background. Black-box depth: enough to build and evaluate, not to train.

- **What an LLM is & autoregressive generation**: predicts text token by token from a prompt. `[§12: Vaswani]` `[§12: Brown]`
- **Tokens & the context window**: text is split into tokens; the model sees a bounded window — the reason chunking and per-token cost exist. `[§12: Sennrich BPE]`
- **Prompting & in-context learning**: instruction + context + question assembled into one prompt; few-shot examples steer behavior. `[§12: Brown]`
- **Sampling: temperature & top-p**: generation is stochastic (same prompt → different outputs), which is why LLM-judges must be pinned. `[§12: Holtzman]`
- **Embeddings & vector similarity**: text → vectors; nearby ≈ similar meaning; cosine vs dot product. `[§12: word2vec]` `[§4: Intro to IR]`
- **Semantic vs keyword search**: matching meaning vs matching words — the split behind dense vs sparse retrieval. `[§4: Intro to IR]`
- **Parametric vs non-parametric knowledge**: knowledge baked into weights vs fetched at inference — the core idea RAG rests on. `[§1: Lewis RAG paper]`

## M1 — Foundations & motivation

- **Why RAG exists**: LLM knowledge cutoff, hallucination, no grounding/provenance. `[§6: Hallucination survey]` `[§1: RAG survey]`
- **What RAG is**: retriever + generator over an external knowledge source. `[§1: Lewis RAG paper]`
- **The RAG pipeline**: index → retrieve → augment prompt → generate. `[§1: RAG survey]`
- **RAG paradigms**: naive vs advanced vs modular. `[§1: RAG survey]`

*Architecture & model strategy — the build decisions that precede the pipeline:*

- **RAG vs long-context**: when a long context window can hold the corpus directly — long-context wins on quality when resourced, RAG wins on cost; route per query (Self-Route). `[§1: RAG vs Long-Context]`
- **Knowledge injection: RAG vs fine-tuning (vs both)**: retrieve at inference vs bake into weights; RAG generally wins for factual/new knowledge, fine-tuning for style/format. `[§1: FT vs Retrieval]`
- **Retrieval-augmented fine-tuning (RAFT)**: train the generator to read retrieved context and ignore distractors — the "combine RAG + fine-tuning" option (advanced; relates to M14). `[§1: RAFT]`
- **Cache-Augmented Generation (CAG)**: preload a bounded corpus into the context + persist the KV cache to skip retrieval entirely — **distinct from *semantic* caching**. `[§1: CAG]`
- **When NOT to use RAG; choosing the generator**: corpus size, freshness, and budget drive the go/no-go; the generator's knowledge cutoff, context limit, and cost are themselves build choices (symmetric to embedding-model & vector-store selection in M3). `[§1: RAG vs Long-Context]` `[§1: FT vs Retrieval]`

## M2 — Ingestion  (needs M0, M1)

*From raw documents to clean, enriched, chunked text ready to index. Production RAG lives or dies here — garbage in, garbage retrieved.*

- **Document loading & parsing**: raw PDF/HTML/scanned files → text; layout-aware extraction (reading order, structure) and tables. `[§13: Unstructured]` `[§13: LayoutLMv3]` `[§13: PubTables-1M]`
- **Cleaning, normalization & deduplication**: strip boilerplate; remove near-duplicates so the top-k isn't crowded. `[§13: Deduplication]`
- **Documents & chunking**: fixed-size vs structural/semantic chunking; chunk size and retrieval granularity. `[§3: Dense X Retrieval]` `[§9: Searching for Best Practices]`
- **Metadata extraction**: derive titles/dates/sections — the supply side for metadata filtering (in M3). `[§13: Unstructured]`
- **Contextual retrieval (chunk enrichment)**: prepend chunk-specific context to each chunk before embedding/indexing to cut retrieval failures. `[§2: Anthropic Contextual Retrieval]`

## M3 — Retrieval & query understanding  (needs M0, M1, M2)

*Turn the ingested corpus into searchable structure, then retrieve and rank context for a query. Vector/search engineering + the query side.*

- **Embeddings**: dense vector representations of text. `[§3: Sentence-BERT]`
- **Embedding model selection & adaptation**: choosing / fine-tuning the embedder for your domain and cost. `[§3: GTR]` `[§4: MTEB]`
- **Sparse retrieval**: TF-IDF, Okapi BM25. `[§4: Intro to IR]` `[§3: BM25]`
- **Dense retrieval**: dual-encoder / DPR. `[§3: DPR]`
- **Vector indexes / ANN**: HNSW, FAISS; comparing implementations (recall vs throughput). `[§3: HNSW]` `[§3: FAISS]` `[§3: ANN-Benchmarks]`
- **Vector store landscape & selection**: the store taxonomy — *native* vector DBs (Milvus, Qdrant, Weaviate, Chroma), *extended* SQL systems (pgvector on Postgres), and *search engines & libraries* (Elasticsearch/OpenSearch, Lucene, FAISS) — and how to choose (hybrid queries, scale, ops, embedded vs server). `[§3: Vector DBMS survey]` (per-store capabilities → each store's official docs)
- **Hybrid retrieval**: combining lexical + semantic. `[§3: Hybrid]` `[§3: COIL]`
- **Reranking**: cross-encoder / seq2seq rerankers. `[§3: monoBERT]` `[§3: monoT5]`
- **Parent-document / small-to-big**: retrieve small, return larger context. `[§3: Parent-document]`
- **Metadata filtering & index lifecycle**: filter ANN by metadata (tenant, recency, doc-type); incremental upsert/delete/re-embed (freshness). `[§3: pgvector]`

*Vector-layer engineering at scale — making the index fast, cheap, and accurate (build-time knobs, not just an eval metric):*

- **Embedding compression & quantization**: product / scalar (int8) / binary quantization and the recall-vs-memory-vs-speed trade-off (ANN indexes live in RAM). `[§3: Faiss guidelines]` `[§3: Embedding quantization]`
- **Truncatable dimensions (Matryoshka) & dimensionality choice**: cut embedding dimensions post-hoc to shrink index cost with bounded quality loss. `[§3: Matryoshka]`
- **Index tuning & capacity planning**: set HNSW (`M`/`efSearch`) and IVF (`nlist`/`nprobe`) from corpus size and RAM budget; size the memory footprint at build time. `[§3: Faiss guidelines]` `[§3: ANN-Benchmarks]`
- **Structured / tabular data & text-to-SQL retrieval**: retrieve over relational data (schema linking, SQL) — distinct from *parsing* tables out of documents; flattening + chunking tables breaks numeric/multi-hop queries. `[§3: TableRAG]` `[§3: Spider]`

*Query understanding & transformation (pre-retrieval — shape the query before searching). These are **tuned and evaluated** with the retrieval metrics in M6, so the syllabus sequences them after M6:*

- **Query rewriting**: reformulate the raw query for better retrieval (Rewrite-Retrieve-Read). `[§2: Query Rewriting]`
- **Conversational contextualization / anaphora resolution**: rewrite a follow-up into a standalone question using chat history (the multi-turn *build* primitive; multi-turn *eval* stays deferred). `[§2: Query Rewriting]`
- **Hypothetical Document Embeddings (HyDE)**: generate a hypothetical answer, embed it, and retrieve against it. `[§2: HyDE]`
- **Query expansion / relevance feedback**: enrich the query with related terms — classical PRF/synonyms, or LLM-generated. `[§4: Intro to IR]`
- **Query decomposition**: split a complex query into sub-questions, retrieve each, then compose — distinct from the *sequential* multi-hop loop in M14. `[§2: Self-Ask]`
- **Query routing / "retrieve or not"**: classify whether (and where) to retrieve before retrieving. `[§9: Searching for Best Practices]`
- **Fusion**: multiple query variants + Reciprocal Rank Fusion to merge the result lists (RAG-Fusion). `[§2: RAG-Fusion]` `[§2: RRF]`

## M4 — Generation & grounding  (needs M1)

- **Generation conditioned on context**: prompting the LLM with retrieved passages. `[§1: Lewis RAG paper]`
- **Augmentation prompt design**: how retrieved context is assembled into the prompt — delimiters/XML, per-chunk source tags, system-prompt instructions, quote-first grounding (also dampens "lost in the middle"). `[§14: Anthropic grounding]`
- **Multi-chunk answer synthesis**: stuff/compact vs refine vs tree-summarize vs accumulate — cost/latency/faithfulness trade-offs when retrieved context overflows the prompt. `[§14: LlamaIndex synthesizers]`
- **Generation-time abstention**: instruct the model to answer only from context and say "I don't know" when it's insufficient — the build-side counterpart to abstention *measurement* (M5). `[§14: Anthropic grounding]`
- **Structured / constrained output**: schema-constrained decoding (strict JSON-schema) vs JSON mode vs tool/function calling — the reliable substrate for structured citations. `[§14: OpenAI Structured Outputs]`
- **Response streaming (delivery)**: stream tokens to the user; time-to-first-token dominates perceived latency and shapes how citations/guardrails attach. `[§14: Anthropic streaming]`
- **Context-position effects**: "lost in the middle", chunk ordering. `[§1: Lost in the Middle]`
- **Context curation**: post-retrieval compression/summarization and repacking/ordering of passages before generation — trims tokens and mitigates the position effects above. `[§2: LongLLMLingua]` `[§1: Lost in the Middle]`
- **Faithfulness / groundedness**: answer supported by context vs fabricated. `[§6: Hallucination survey]`
- **Hallucination types**: intrinsic vs extrinsic. `[§6: Hallucination survey]`
- **Citation / attribution generation**: make the generator emit inline citations to the sources it used. `[§6: ALCE]`
- **Security — indirect prompt injection**: malicious instructions hidden in retrieved/external content. `[§11: Greshake]` `[§11: OWASP]`

## M5 — Why evaluation is hard (eval foundations)  (needs M1)

- **Eval targets**: retrieval quality vs generation quality (separable failure modes). `[§8: RAGAS paper]` `[§9: Eval-of-RAG survey]`
- **Reference-based vs reference-free** evaluation. `[§8: RAGAS paper]`
- **Offline vs online** evaluation. `[§10: Online Eval for IR]`
- **Pipeline error attribution & the retrieval recall ceiling**: generation quality is capped by what retrieval surfaced; attribute end-to-end failures to the right stage. `[§9: Eval-of-RAG survey]`
- **Eval design**: choose which metrics fit the use case; baselines & ablation (change one component, attribute the delta). `[§9: Eval-of-RAG survey]` `[§9: Searching for Best Practices]`
- **Eval targets beyond retrieval/generation**: negative rejection / abstention ("I don't know"), noise & counterfactual robustness. `[§9: Eval-of-RAG survey]` `[§9: RGB]`

## M6 — Retrieval evaluation  (needs M3, M5)

- **Relevance & test collections**: qrels, the Cranfield/TREC paradigm. `[§4: TREC]` `[§4: Intro to IR]`
- **Set metrics**: precision@k, recall@k. `[§4: Intro to IR]`
- **Rank-aware metrics**: MRR, MAP. `[§4: Intro to IR]`
- **Graded relevance**: DCG / nDCG. `[§4: nDCG]`
- **Retrieval & embedding benchmarks**: BEIR, MTEB. `[§4: BEIR]` `[§4: MTEB]`

## M7 — Generation evaluation: classical metrics & their limits  (needs M4, M5)

- **Lexical-overlap metrics**: BLEU, ROUGE, METEOR. `[§5: BLEU]` `[§5: ROUGE]` `[§5: METEOR]`
- **Embedding-based metrics**: BERTScore. `[§5: BERTScore]`
- **Why overlap metrics fail for RAG answers**: weak correlation with human judgment. `[§5: How NOT To Evaluate]`
- **Answer correctness vs ground truth**: semantic/factual match to a gold answer — distinct from faithfulness (grounded in context) and answer-relevancy (addresses the question). `[§8: RAGAS docs]`

## M8 — Faithfulness / hallucination measurement  (needs M4, M5)

- **NLI / entailment-based consistency**: FactCC, SummaC. `[§6: FactCC]` `[§6: SummaC]`
- **Atomic-fact precision**: FActScore. `[§6: FActScore]`
- **Sampling-consistency detection**: SelfCheckGPT. `[§6: SelfCheckGPT]`
- **Production scorers**: Vectara HHEM. `[§6: HHEM]`
- **Hallucination benchmarks**: TruthfulQA, RAGTruth. `[§6: TruthfulQA]` `[§6: RAGTruth]`
- **Citation / attribution-quality evaluation**: do the cited sources actually support the claim? (citation precision/recall). `[§6: ALCE]`

## M9 — LLM-as-a-judge  (needs M7, M8)

- **The LLM-as-judge idea & its validity** vs human preference. `[§7: MT-Bench]`
- **A concrete recipe**: G-Eval (CoT + form-filling). `[§7: G-Eval]`
- **Judge biases**: position, verbosity, self-enhancement. `[§7: MT-Bench]` `[§7: Fair Evaluators]`
- **Judge robustness / meta-evaluation**: LLMBar. `[§7: LLMBar]`
- **Field overview**: LLM-as-a-judge survey. `[§7: Judge survey]`
- **Reproducibility of judged scores**: pin temperature/seed/judge-model version; report score variance across runs. `[§7: Judge survey]` `[§7: G-Eval]`

## M10 — RAG-specific metric suites (frameworks)  (needs M6, M8, M9)

- **RAGAS metrics**: faithfulness, context precision, context recall, answer relevancy, noise sensitivity. `[§8: RAGAS paper]` `[§8: RAGAS docs]`
- **The RAG triad**: context relevance, groundedness, answer relevance. `[§8: TruLens]`
- **ARES methodology**: fine-tuned judges + prediction-powered inference. `[§8: ARES]`
- **Cross-framework view**: DeepEval RAG metrics. `[§8: DeepEval]`

## M11 — Datasets, benchmarks & synthetic test generation  (needs M6, M10)

- **QA datasets as ground truth**: Natural Questions, HotpotQA, TriviaQA, MS MARCO, KILT. `[§9: Natural Questions]` `[§9: HotpotQA]` `[§9: TriviaQA]` `[§9: MS MARCO]` `[§9: KILT]`
- **RAG-specific benchmarks**: RGB, CRUD-RAG, CRAG-benchmark, MultiHop-RAG. `[§9: RGB]` `[§9: CRUD-RAG]` `[§9: CRAG benchmark]` `[§9: MultiHop-RAG]`
- **Synthetic test-set generation** for RAG. `[§9: MultiHop-RAG]` `[§8: RAGAS docs]`
- **Eval methodology surveys / best practices**. `[§9: Eval-of-RAG survey]` `[§9: Searching for Best Practices]`
- **Benchmark data contamination / test-set leakage**: test items leaking into pretraining inflate scores and invalidate benchmarks. `[§9: Data contamination survey]`
- **Building a golden eval set**: query sampling, annotation guidelines, annotator training & agreement. `[§4: TREC]` `[§7: Kiritchenko]` `[§7: Carletta]`
- **Held-out discipline / eval-set overfitting**: don't tune against your test set; keep a rarely-touched holdout (distinct from pretraining contamination). `[§7: Dwork]`

## M12 — Statistical rigor & methodology  (needs M6, M9; cross-cuts M7/M8/M10/M11)

- **Inter-annotator agreement**: Cohen's kappa, Krippendorff's alpha. `[§7: Carletta]` `[§7: Cohen]` `[§7: Krippendorff]`
- **Significance testing**: bootstrap / randomization for system comparison. `[§7: Riezler & Maxwell]`
- **Correlating automated metrics with human judgment** (the meta-question behind every metric). `[§5: How NOT To Evaluate]` `[§7: MT-Bench]`
- **Statistical power / sample size**: is the eval set big enough to trust the delta? `[§7: Card]`
- **Human-eval instruments**: Likert vs pairwise vs best-worst scaling; humans vs automated. `[§7: Kiritchenko]` `[§7: MT-Bench]`
- **Eval-driven development**: failure analysis → fix → re-eval loop, guarded by a held-out set. `[§9: Searching for Best Practices]` `[§7: Dwork]`

## M13 — Production evaluation & operations (LLMOps)  (needs M10)

- **Online vs offline eval; A/B testing & interleaving**. `[§10: Online Eval for IR]`
- **Observability & tracing**: spans, the GenAI OTel standard. `[§10: OpenTelemetry GenAI]` `[§10: LangSmith]` `[§10: Phoenix]` `[§10: Langfuse]`
- **Continuous / CI evaluation, monitoring & drift**. `[§10: LangSmith]` `[§10: Langfuse]` `[§8: RAGAS paper]`
- **Human-in-the-loop evaluation**. `[§10: Langfuse]`
- **Cost / latency / efficiency as first-class metrics**: trade answer quality against \$/query and p95 latency. `[§10: OpenTelemetry GenAI]` `[§9: Searching for Best Practices]`
- **Request-path reliability**: timeouts, retries/backoff, fallback model or route, and graceful degradation when retrieval returns nothing or a component fails (distinct from deploy-time rollout). `[§14: LangChain fallbacks]`
- **Security & access control in production**: ACL-aware retrieval, data-leakage prevention, the OWASP LLM risk checklist. `[§11: OWASP]`
- **Guardrails / output validation**: input-output safety filtering, schema/format validation, refusal. `[§11: Llama Guard]` `[§11: NeMo Guardrails]`
- **PII, governance & right-to-erasure**: PII redaction before indexing; deleting a subject's data across embeddings, chunks, caches & logs (GDPR Art. 17). `[§11: GDPR Art.17]` `[§11: Presidio]` `[§11: NIST AI RMF]`
- **Feedback loops / data flywheel**: mine production signals (explicit & implicit) back into the eval set and improvements. `[§10: Online Eval for IR]`
- **System versioning & safe rollout**: version prompts/indexes/models; canary & shadow deploys with auto-rollback (distinct from A/B). `[§10: LangSmith]` `[§10: Langfuse]`
- **Business vs technical metrics**: deflection, task success, CSAT — and the gap between offline wins and outcomes. `[§10: Online Eval for IR]`

## M14 — Advanced RAG: iterative & agentic control flow  (needs M3, M4, M10)

*Patterns that interleave retrieval, reasoning, and generation in a loop — learned last, because you need the pipeline (M2–M4) and the means to evaluate whether the loop actually helps (M10). The per-stage advanced techniques (query transformation, fusion, context curation, contextual retrieval) now live in their stage modules: M2, M3, M4.*

- **Multi-hop / iterative retrieval**: IRCoT, FLARE, Iter-RetGen. `[§2: IRCoT]` `[§2: FLARE]` `[§2: Iter-RetGen]`
- **Self-correcting RAG**: Self-RAG, Corrective RAG (CRAG technique). `[§2: Self-RAG]` `[§2: CRAG technique]`
- **Agentic RAG**. `[§2: Agentic RAG survey]`

---

## Coverage check

Every module is backed by ≥1 verified registry source, and every registry
section (§1–§14) is exercised by ≥1 module. Two adversarial audits were run on
2026-06-05: a first 3-lens pass (build/eval/consistency) and a deeper 5-lens pass
(ingestion, foundations, ops/governance, eval-methodology, vs-authoritative-curricula).
The second pass added the **primer**, the **ingestion** front-half, **eval-methodology**
concepts, and the **governance/lifecycle** cluster — all with newly verified sources
(§12 primer, §13 ingestion, plus additions to §2/§3/§7/§11). One source-misattribution
(ARES on human-in-the-loop) was fixed.

A third, **build-side** audit ran on 2026-06-06 (5 parallel lenses) after the scope
reframed to build + evaluate. It surfaced four blind spots, all now added with
sources verified at the primary: **architecture & model strategy** (M1 — RAG vs
long-context / fine-tuning / CAG, "when not to RAG"), **generation craft** (M4 —
augmentation-prompt design, multi-chunk synthesis, generation-time abstention,
structured output, streaming), **vector-layer engineering at scale** (M3 —
quantization, Matryoshka, index tuning & capacity planning), **structured/tabular
text-to-SQL retrieval** (M3), and **request-path reliability** (M13). New registry
section §14 + entries in §1/§3 back these.

Two follow-up restructurings (2026-06-06): (1) the old "advanced techniques"
module was **distributed to stage modules** — the query-understanding family
(rewriting, HyDE, expansion, decomposition, routing, conversational
contextualization, fusion) now lives in **M3**; context curation in **M4**;
contextual-retrieval enrichment in **M2**; only the iterative & agentic
control-flow patterns (multi-hop, self-correcting, agentic) remain, as **M14**.
**Query expansion** (`§4: Intro to IR`, Ch. 9) and **query decomposition**
(`§2: Self-Ask`) were added to close two gaps. (2) The oversized ingestion+retrieval
module was **split into M2 (ingestion — text engineering)** and **M3 (retrieval,
indexing & query understanding — vector/search engineering)**, renumbering the
downstream modules by +1 (generation is now M4, … iterative/agentic is M14). The
`[§N: …]` source tags are unaffected (they point at registry sections, not modules).

Remaining items to revisit during Phase 3 (deep per-lesson research may add sources):

- **Synthetic test generation** (M11): currently leans on MultiHop-RAG + RAGAS
  docs; a dedicated method paper may be worth verifying in Phase 3.
- **M3 is large** (retrieval + vector-layer engineering + query understanding):
  expect it to spawn several lessons in Phase 2; sequence the query-understanding
  sub-cluster after M6 (it is evaluated with retrieval metrics).
- **Deliberately deferred as nice-to-have / out of core scope** (revisit only if
  a lesson needs them): late-interaction retrieval (ColBERT), GraphRAG,
  multimodal RAG, **semantic caching** (note: *cache-augmented generation* is a
  different thing and is now in M1), judge calibration, safety/toxicity eval, and
  **multi-turn/conversational *evaluation*** (the multi-turn *build* primitive —
  conversational query contextualization — is now in M3). The 2026-06-06 audit
  argued for promoting multimodal RAG and GraphRAG, but they remain deferred by
  decision. Each would need a verified source first.
