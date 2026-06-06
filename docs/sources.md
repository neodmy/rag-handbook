# Source registry

The allowed-list of sources for the handbook. Lessons cite **only** entries from
this file (a `## Sources` link in a lesson must appear here). See
[`handbook-method.md`](./handbook-method.md) for the registry rules.

Every entry was **verified against its primary source** (fetched/searched, not
recalled). Where the primary page was paywalled, the entry is confirmed via an
authoritative secondary (DOI metadata / ACL Anthology / DBLP) and **flagged**.
Sources we could not confirm live under [To verify](#to-verify-before-citing) —
do not cite them until promoted.

Reputation tiers: `high` (peer-reviewed paper / official docs / standard textbook) ·
`medium` (maintained but not peer-reviewed — cited preprint or official model card) ·
`low` (weak provenance — supporting only, never a sole citation).

Organized by the RAG pipeline and its evaluation, end to end. Selection is driven
by coverage of the concepts a practitioner must understand to **build and evaluate**
production RAG — not by convenience. **Last verified:** 2026-06-06 (build-side audit
added §14 + entries to §1/§3; all fetched at the primary this session).

> Naming collision to watch: **"CRAG"** refers to two different things below —
> *Corrective RAG* (a technique, §2) and the *Comprehensive RAG Benchmark* (a
> dataset, §9). They are unrelated.

## 1. RAG foundations & architecture

- **[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)**
  — Lewis, Perez, Piktus, Petroni, et al. NeurIPS 2020. **high**.
  Backs: the original RAG architecture (parametric generator + non-parametric dense retriever); origin of the term.
- **[Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)**
  — Gao, Xiong, et al. arXiv:2312.10997, 2023–24. **medium** (heavily-cited preprint, "Ongoing Work", not peer-reviewed).
  Backs: Naive / Advanced / Modular RAG taxonomy; retrieval–generation–augmentation framing.
- **[Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)**
  — Liu, Lin, Hewitt, Paranjape, et al. TACL 2023. **high**.
  Backs: positional bias in long contexts (the U-shaped curve) — how a generator uses retrieved context, and why chunk ordering matters.
- **[Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach](https://arxiv.org/abs/2407.16833)**
  — Li, et al. (Google). EMNLP 2024 (industry track). **high**.
  Backs: the RAG-vs-long-context architecture decision — long-context wins on quality when resourced, RAG wins on cost; the Self-Route query router. *Verified at arXiv abstract 2026-06-06.*
- **[Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs](https://arxiv.org/abs/2312.05934)**
  — Ovadia, Brief, Mishaeli, Elisha (Microsoft). arXiv:2312.05934, 2023–24. **medium** (widely-cited preprint; venue not confirmed at primary).
  Backs: RAG vs (unsupervised) fine-tuning for knowledge injection — RAG consistently outperforms FT for both previously-seen and entirely new knowledge. *Verified at arXiv abstract 2026-06-06.*
- **[RAFT: Adapting Language Model to Domain Specific RAG](https://arxiv.org/abs/2403.10131)**
  — Zhang, Patil, Jain, Shen, …, Zaharia, Stoica, Gonzalez (UC Berkeley). arXiv:2403.10131, 2024. **medium** (cited preprint).
  Backs: retrieval-augmented fine-tuning — train the generator to use retrieved docs and ignore distractors ("combine RAG + fine-tuning"). *Verified at arXiv abstract 2026-06-06.*
- **[Don't Do RAG: When Cache-Augmented Generation is All You Need for Knowledge Tasks (CAG)](https://arxiv.org/abs/2412.15605)**
  — Chan, Chen, Cheng, Huang. arXiv:2412.15605, 2024–25. **medium** (cited preprint).
  Backs: cache-augmented generation — preload a bounded corpus into the context window + persist the KV cache to bypass real-time retrieval. **Distinct from *semantic* caching** (query→answer caching). *Verified at arXiv abstract 2026-06-06.*

## 2. Advanced RAG techniques

- **[Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)](https://arxiv.org/abs/2212.10496)**
  — Gao, Ma, Lin, Callan. ACL 2023. **high**. Backs: HyDE query transformation.
- **[Query Rewriting for Retrieval-Augmented Large Language Models](https://arxiv.org/abs/2305.14283)**
  — Ma, Gong, He, Zhao, et al. EMNLP 2023. **high**. Backs: Rewrite-Retrieve-Read query rewriting (and, by extension, conversational query contextualization — rewriting a follow-up into a standalone question).
- **[Measuring and Narrowing the Compositionality Gap in Language Models (Self-Ask)](https://arxiv.org/abs/2210.03350)**
  — Press, Zhang, Min, Schmidt, Smith, Lewis. Findings of EMNLP 2023. **high**.
  Backs: query decomposition — break a complex query into follow-up sub-questions and answer each (optionally via a search engine), then compose. *Verified at arXiv abstract 2026-06-06.*
- **[Interleaving Retrieval with Chain-of-Thought Reasoning (IRCoT)](https://arxiv.org/abs/2212.10509)**
  — Trivedi, Balasubramanian, Khot, Sabharwal. ACL 2023. **high**. Backs: multi-hop / iterative retrieval.
- **[Active Retrieval Augmented Generation (FLARE)](https://arxiv.org/abs/2305.06983)**
  — Jiang, Xu, Gao, Sun, et al. EMNLP 2023. **high**. Backs: forward-looking active retrieval.
- **[Iterative Retrieval-Generation Synergy (Iter-RetGen)](https://arxiv.org/abs/2305.15294)**
  — Shao, Gong, Shen, Huang, et al. Findings of EMNLP 2023. **high**. Backs: iterative retrieve/generate loops.
- **[Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511)**
  — Asai, Wu, Wang, Sil, Hajishirzi. ICLR 2024. **high**. Backs: on-demand retrieval + reflection/self-critique.
- **[Corrective Retrieval Augmented Generation (CRAG, technique)](https://arxiv.org/abs/2401.15884)**
  — Yan, Gu, Zhu, Ling. arXiv:2401.15884, 2024. **medium** (cited preprint). Backs: retrieval evaluator + correct/ambiguous/incorrect actions.
- **[Agentic Retrieval-Augmented Generation: A Survey](https://arxiv.org/abs/2501.09136)**
  — Singh, Ehtesham, Kumar, Khoei. arXiv:2501.09136, 2025. **medium** (preprint survey). Backs: agentic RAG patterns (routing, planning).
- **[RAG-Fusion: a New Take on Retrieval-Augmented Generation](https://arxiv.org/abs/2402.03367)**
  — Rackauckas. arXiv:2402.03367, 2024. **low** (single-author preprint — pair with the RRF source below). Backs: multi-query + reciprocal rank fusion.
- **[Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://doi.org/10.1145/1571941.1572114)**
  — Cormack, Clarke, Büttcher. SIGIR 2009. **high**. Backs: the RRF algorithm underlying RAG-Fusion.
  *Confirmed via Crossref DOI metadata — ACM DL primary page paywalled.*
- **[LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression](https://arxiv.org/abs/2310.06839)**
  — Jiang, Wu, et al. (Microsoft). ACL 2024. **high**. Backs: question-aware context/prompt compression — cut tokens and mitigate position bias before generation.
- **[Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)**
  — Anthropic, 2024. Official engineering blog. **medium** (single-vendor). Backs: prepending chunk-specific context before embedding + BM25 to cut retrieval failures.

## 3. Retrieval building blocks

- **[The Probabilistic Relevance Framework: BM25 and Beyond](https://doi.org/10.1561/1500000019)**
  — Robertson, Zaragoza. Foundations and Trends in IR, 2009. **high**. Backs: Okapi BM25, the standard sparse/lexical ranking function (primary source; the IIR textbook in §4 gives the textbook treatment).
  *Confirmed via Crossref DOI metadata — publisher primary page paywalled.*
- **[Dense Passage Retrieval for Open-Domain Question Answering (DPR)](https://aclanthology.org/2020.emnlp-main.550/)**
  — Karpukhin, Oguz, Min, Lewis, et al. EMNLP 2020. **high**. Backs: dual-encoder dense retrieval (the retrieval half of RAG).
- **[Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://aclanthology.org/D19-1410/)**
  — Reimers, Gurevych. EMNLP-IJCNLP 2019. **high**. Backs: semantically meaningful sentence/text embeddings.
- **[Large Dual Encoders Are Generalizable Retrievers (GTR)](https://arxiv.org/abs/2112.07899)**
  — Ni, Qu, Lu, Dai, et al. (Google). EMNLP 2022. **high**. Backs: embedding-model **selection** — larger dual encoders generalize better out-of-domain.
- **[Passage Re-ranking with BERT (monoBERT)](https://arxiv.org/abs/1901.04085)**
  — Nogueira, Cho. arXiv:1901.04085, 2019. **medium** (canonical preprint). Backs: cross-encoder reranking.
- **[Document Ranking with a Pretrained Seq2Seq Model (monoT5)](https://aclanthology.org/2020.findings-emnlp.63/)**
  — Nogueira, Jiang, Pradeep, Lin. Findings of EMNLP 2020. **high**. Backs: generative (T5) reranking.
- **[Efficient and robust ANN search using HNSW graphs](https://arxiv.org/abs/1603.09320)**
  — Malkov, Yashunin. arXiv:1603.09320; IEEE TPAMI 2020. **high**. Backs: HNSW vector index.
- **[Billion-scale similarity search with GPUs (FAISS)](https://arxiv.org/abs/1702.08734)**
  — Johnson, Douze, Jégou. arXiv:1702.08734; IEEE Trans. Big Data. **high**. Backs: FAISS vector index.
- **[Leveraging Semantic and Lexical Matching to Improve Recall — A Hybrid Approach](https://arxiv.org/abs/2010.01195)**
  — Kuzi, et al. arXiv:2010.01195, 2020. **medium** (preprint). Backs: hybrid (sparse+dense) retrieval.
- **[COIL: Revisit Exact Lexical Match in IR with Contextualized Inverted List](https://arxiv.org/abs/2104.07186)**
  — Gao, Dai, Callan. NAACL 2021. **high**. Backs: contextualized lexical + dense bridge — "contextualized exact match retrieval … brings semantic lexical matching", storing token representations in inverted lists. Supporting context for the learned-sparse family (not term-expansion).
- **[SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking](https://arxiv.org/abs/2107.05720)**
  — Formal, Piwowarski, Clinchant. SIGIR 2021. **high**. Backs: **learned sparse retrieval** — learned sparse term-weight representations over the vocabulary that "inherit … the exact matching of terms and the efficiency of inverted indexes," via explicit sparsity regularization + a log-saturation effect on term weights; "competitive results with respect to state-of-the-art dense and sparse methods." *Verified at arXiv abstract 2026-06-06; the WordPiece-vocabulary, FLOPS-regularization, and explicit vocabulary-mismatch framing are in the paper body, not the abstract — cite body sections for those.*
- **[SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval](https://arxiv.org/abs/2109.10086)**
  — Formal, Lassance, Piwowarski, Clinchant. arXiv:2109.10086, 2021. **medium** (preprint follow-up to the SIGIR paper). Backs: improved pooling + document expansion + distillation; headline result ">9% NDCG@10 gains on TREC DL 2019, leading to state-of-the-art results on the BEIR benchmark." *Verified at arXiv abstract 2026-06-06.*
- **[Dense X Retrieval: What Retrieval Granularity Should We Use?](https://arxiv.org/abs/2312.06648)**
  — Chen, Wang, Chen, Yu, et al. EMNLP 2024. **high**. Backs: chunking / retrieval-unit granularity (incl. propositions).
- **Parent-document / small-to-big retrieval** (engineering pattern — retrieve small chunks, return their larger parent/merged context). Official framework docs:
  [LangChain `ParentDocumentRetriever`](https://python.langchain.com/api_reference/langchain/retrievers/langchain.retrievers.parent_document_retriever.ParentDocumentRetriever.html)
  and [LlamaIndex Auto-Merging / Recursive Retriever](https://docs.llamaindex.ai/en/stable/examples/retrievers/auto_vs_recursive_retriever/). **high** (official docs of widely-used frameworks).
  Backs: small-to-big / auto-merging / recursive retrieval. No canonical paper — cite as an engineering pattern, not a peer-reviewed concept.
- **[pgvector](https://github.com/pgvector/pgvector)** — open-source vector extension for Postgres. Official repo/docs. **high** (official docs of a widely-used tool).
  Backs: metadata filtering of vector search (SQL `WHERE`) and index lifecycle — incremental insert/update/delete (freshness). Engineering reference; Pinecone/Weaviate docs are equivalents.
- **[Survey of Vector Database Management Systems](https://doi.org/10.1007/s00778-024-00864-x)**
  — Pan, Wang, Li. The VLDB Journal, 2024 ([arXiv:2310.14021](https://arxiv.org/abs/2310.14021)). **high** (peer-reviewed).
  Backs: the vector-store **taxonomy and selection** — *native* VDBMSs (e.g. Milvus, Vearch), *extended* systems (SQL + vector, e.g. pgvector / AnalyticDB-V), and *search engines & libraries* (e.g. Elasticsearch/Lucene, FAISS) — plus hybrid attribute+vector queries. Per-store capability details → each store's own official docs.
- **[ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms](https://doi.org/10.1016/j.is.2019.02.006)**
  — Aumüller, Bernhardsson, Faithfull. Information Systems, 2019 ([arXiv:1807.05614](https://arxiv.org/abs/1807.05614)). **high** (peer-reviewed).
  Backs: empirical comparison of ANN algorithms/implementations (recall vs throughput trade-offs).
- **[Faiss — Guidelines to choose an index](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)**
  — Facebook AI Research. Official wiki. **high** (official docs of a widely-used library).
  Backs: build-time index choice and ANN parameter tuning (HNSW `M`/`efSearch`, IVF `nlist`/`nprobe`), the all-in-RAM constraint, per-vector memory footprint, and quantization (SQ/PQ) options. *Verified 2026-06-06.*
- **[Binary and Scalar Embedding Quantization for Significantly Faster & Cheaper Retrieval](https://huggingface.co/blog/embedding-quantization)**
  — Hugging Face / Sentence-Transformers, 2024. Engineering blog with reproducible MTEB benchmarks. **medium** (single-vendor; supporting — pair with the Faiss guidelines above).
  Backs: int8 / binary embedding quantization and the recall-vs-memory-vs-speed trade-off. *Verified 2026-06-06.*
- **[Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147)**
  — Kusupati, et al. NeurIPS 2022. **high**.
  Backs: nested / truncatable embedding dimensions — cut dimensionality post-hoc to shrink index cost with bounded quality loss (the basis of `dimensions`-style embedding APIs). *Verified at arXiv abstract 2026-06-06.*
- **[TableRAG: A Retrieval Augmented Generation Framework for Heterogeneous Document Reasoning](https://arxiv.org/abs/2506.10380)**
  — Yu, Jian, Chen. arXiv:2506.10380, 2025. **medium** (recent preprint).
  Backs: structured / tabular retrieval via SQL — why flattening + chunking tables disrupts tabular structure and breaks multi-hop / global queries. *Verified at arXiv abstract 2026-06-06.*
- **[Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL](https://arxiv.org/abs/1809.08887)**
  — Yu, Zhang, Yang, Yasunaga, …, Radev (Yale). EMNLP 2018. **high**.
  Backs: the canonical text-to-SQL task and its cross-domain evaluation — retrieval over relational data. *Verified at arXiv abstract 2026-06-06.*

## 4. Retrieval evaluation (IR metrics & benchmarks)

- **[Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/)**
  — Manning, Raghavan, Schütze. Cambridge University Press, 2008. **high** (standard textbook).
  Backs: classical IR — precision@k, recall@k, MAP, MRR (metric foundations) **and** TF-IDF / Okapi BM25 (sparse retrieval, Ch. 6 & 11) **and** query expansion / relevance feedback (Ch. 9).
- **[TREC — Text REtrieval Conference](https://trec.nist.gov/)**
  — NIST. Since 1992. **high** (standard evaluation body). Backs: IR test collections and standardized relevance-based evaluation.
- **[Cumulated gain-based evaluation of IR techniques (nDCG)](https://doi.org/10.1145/582415.582418)**
  — Järvelin, Kekäläinen. ACM TOIS, 2002. **high**. Backs: nDCG (the originating paper).
  *Confirmed via Semantic Scholar DOI metadata — ACM DL page is paywalled (403).*
- **[BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of IR Models](https://arxiv.org/abs/2104.08663)**
  — Thakur, Reimers, Rücklé, Srivastava, Gurevych. NeurIPS 2021 (D&B). **high**. Backs: zero-shot retrieval benchmark (18 datasets).
- **[MTEB: Massive Text Embedding Benchmark](https://aclanthology.org/2023.eacl-main.148/)**
  — Muennighoff, Tazi, Magne, Reimers. EACL 2023. **high**. Backs: embedding/retrieval model benchmark.

## 5. Classical generation metrics & their limits

- **[BLEU: a Method for Automatic Evaluation of Machine Translation](https://aclanthology.org/P02-1040/)**
  — Papineni, Roukos, Ward, Zhu. ACL 2002. **high**. Backs: n-gram precision metric (and why it under-serves single-answer eval).
- **[ROUGE: A Package for Automatic Evaluation of Summaries](https://aclanthology.org/W04-1013/)**
  — Lin. ACL workshop, 2004. **high**. Backs: recall-oriented n-gram/LCS overlap metric.
- **[METEOR: An Automatic Metric for MT Evaluation with Improved Correlation](https://aclanthology.org/W05-0909/)**
  — Banerjee, Lavie. ACL workshop, 2005. **high**. Backs: stem/synonym-aware overlap; documents BLEU's weak human correlation.
- **[BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675)**
  — Zhang, Kishore, Wu, Weinberger, Artzi. ICLR 2020. **high**. Backs: embedding-based semantic similarity over surface overlap.
- **[How NOT To Evaluate Your Dialogue System](https://aclanthology.org/D16-1230/)**
  — Liu, Lowe, Serban, Noseworthy, Charlin, Pineau. EMNLP 2016. **high**. Backs: empirical evidence that n-gram metrics correlate weakly with human judgment.

## 6. Hallucination & faithfulness detection

- **[Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629)**
  — Ji, et al. ACM Computing Surveys; arXiv:2202.03629. **high**. Backs: hallucination taxonomy (intrinsic vs extrinsic), eval/mitigation map.
- **[SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection](https://arxiv.org/abs/2303.08896)**
  — Manakul, Liusie, Gales. EMNLP 2023. **high**. Backs: sampling-consistency hallucination detection.
- **[FActScore: Fine-grained Atomic Evaluation of Factual Precision](https://arxiv.org/abs/2305.14251)**
  — Min, Krishna, Lyu, Lewis, Yih, Koh, Iyyer, Zettlemoyer, Hajishirzi. EMNLP 2023. **high**. Backs: atomic-fact decomposition for groundedness.
- **[TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958)**
  — Lin, Hilton, Evans. ACL 2022. **high**. Backs: truthfulness benchmark.
- **[SummaC: Re-Visiting NLI-based Models for Inconsistency Detection](https://arxiv.org/abs/2111.09525)**
  — Laban, et al. TACL 2022. **high**. Backs: NLI/entailment-based factual consistency.
- **[Evaluating the Factual Consistency of Abstractive Summarization (FactCC)](https://arxiv.org/abs/1910.12840)**
  — Kryściński, et al. EMNLP 2020. **high**. Backs: weakly-supervised entailment-style consistency classifier.
- **[HHEM-2.1-Open (Vectara Hughes Hallucination Evaluation Model)](https://huggingface.co/vectara/hallucination_evaluation_model)**
  — Vectara. Official model card. **medium** (not peer-reviewed). Backs: cross-encoder factual-consistency scorer for RAG.
- **[RAGTruth: A Hallucination Corpus for Trustworthy RAG](https://arxiv.org/abs/2401.00396)**
  — Niu, Wu, Zhu, Xu, et al. ACL 2024. **high**. Backs: RAG-specific, span-level hallucination corpus.
- **[Enabling Large Language Models to Generate Text with Citations (ALCE)](https://arxiv.org/abs/2305.14627)**
  — Gao, et al. EMNLP 2023. **high**. Backs: generating answers with inline citations, **and** evaluating citation quality (citation precision/recall).

## 7. LLM-as-a-judge methodology & statistics

- **[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)**
  — Zheng, et al. NeurIPS 2023 (D&B). **high**. Backs: judge validity & human agreement; names position/verbosity/self-enhancement biases.
- **[G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)**
  — Liu, et al. EMNLP 2023. **high**. Backs: CoT + form-filling LLM-judge recipe.
- **[Large Language Models are not Fair Evaluators](https://arxiv.org/abs/2305.17926)**
  — Wang, et al. ACL 2024. **high**. Backs: position bias in pairwise judging + calibration mitigations.
- **[Evaluating LLMs at Evaluating Instruction Following (LLMBar)](https://arxiv.org/abs/2310.07641)**
  — Zeng, Yu, et al. ICLR 2024. **high**. Backs: meta-evaluation of judge robustness vs superficial quality.
- **[A Survey on LLM-as-a-Judge](https://arxiv.org/abs/2411.15594)**
  — Gu, Jiang, Shi, Tan, et al. arXiv:2411.15594, 2024. **medium** (preprint). Backs: systematization of the field.
- **[Assessing Agreement on Classification Tasks: The Kappa Statistic](https://aclanthology.org/J96-2004/)**
  — Carletta. Computational Linguistics, 1996. **high**. Backs: inter-annotator agreement (kappa) in NLP.
- **[On Some Pitfalls in Automatic Evaluation and Significance Testing for MT](https://aclanthology.org/W05-0908/)**
  — Riezler, Maxwell. ACL workshop, 2005. **high**. Backs: significance testing (bootstrap / randomization) for comparing systems.
- **[A Coefficient of Agreement for Nominal Scales](https://doi.org/10.1177/001316446002000104)**
  — Cohen. Educational and Psychological Measurement, 1960. **high**. Backs: Cohen's kappa (the original inter-rater agreement coefficient).
  *Confirmed via Crossref DOI metadata — publisher primary page paywalled.*
- **[Answering the Call for a Standard Reliability Measure for Coding Data](https://doi.org/10.1080/19312450709336664)**
  — Hayes, Krippendorff. Communication Methods and Measures, 2007. **high**. Backs: Krippendorff's alpha (agreement across any number of raters/scales).
  *Confirmed via Crossref DOI metadata — publisher primary page paywalled.*
- **[With Little Power Comes Great Responsibility](https://aclanthology.org/2020.emnlp-main.745/)**
  — Card, Henderson, Khandelwal, Jia, Mahowald, Jurafsky. EMNLP 2020. **high**. Backs: statistical **power / sample size** for evaluation — many experiments are underpowered.
- **[Best-Worst Scaling More Reliable than Rating Scales](https://aclanthology.org/P17-2074/)**
  — Kiritchenko, Mohammad. ACL 2017. **high**. Backs: human-rating **instruments** — best-worst scaling beats Likert at equal budget.
- **[The reusable holdout: Preserving validity in adaptive data analysis](https://doi.org/10.1126/science.aaa9375)**
  — Dwork, Feldman, Hardt, Pitassi, Reingold, Roth. Science, 2015. **high**. Backs: avoiding **eval-set overfitting** under repeated/adaptive reuse (held-out discipline). *Confirmed via Crossref DOI metadata — primary paywalled.*

## 8. RAG evaluation frameworks (metric suites)

- **[RAGAS — Concepts › Metrics](https://docs.ragas.io/en/stable/concepts/metrics/)**
  — Vibrant Labs. Official docs (`stable`, aligns with `ragas` 0.4.3). **high**. Backs: faithfulness, context precision/recall, response relevancy, noise sensitivity.
- **[vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas)** — Vibrant Labs. Canonical repo (old `explodinggradients/ragas` 301-redirects). **high**. Backs: reference implementation of RAGAS metrics.
- **[RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/)**
  — Es, James, Espinosa-Anke, Schockaert. EACL 2024 (Demos) ([arXiv](https://arxiv.org/abs/2309.15217)). **high**. Backs: reference-free RAG metric definitions.
- **[ARES: An Automated Evaluation Framework for RAG Systems](https://aclanthology.org/2024.naacl-long.20/)**
  — Saad-Falcon, Khattab, Potts, Zaharia. NAACL 2024 ([arXiv](https://arxiv.org/abs/2311.09476)). **high**. Backs: fine-tuned LM judges + prediction-powered inference.
- **[TruLens — The RAG Triad](https://www.trulens.org/getting_started/core_concepts/rag_triad/)**
  — TruEra. Official docs. **high**. Backs: context relevance, groundedness, answer relevance.
- **[DeepEval — Introduction to LLM Metrics](https://deepeval.com/docs/metrics-introduction)**
  ([repo](https://github.com/confident-ai/deepeval)) — Confident AI. Official docs. **high**. Backs: a second framework's RAG metric definitions (cross-check).

## 9. RAG benchmarks & datasets

- **[Benchmarking Large Language Models in RAG (RGB)](https://arxiv.org/abs/2309.01431)**
  — Chen, Lin, Han, Sun. AAAI 2024. **high**. Backs: noise robustness, negative rejection, information integration, counterfactual robustness.
- **[CRUD-RAG: A Comprehensive Chinese Benchmark for RAG](https://arxiv.org/abs/2401.17043)**
  — Lyu, Li, Niu, et al. ACM TOIS; arXiv:2401.17043. **high**. Backs: RAG eval by Create/Read/Update/Delete operation types.
- **[CRAG — Comprehensive RAG Benchmark (dataset)](https://arxiv.org/abs/2406.04744)**
  — Yang, Sun, et al. (Meta). NeurIPS 2024 (D&B). **high**. Backs: factual-QA benchmark, 5 domains + mock retrieval/KG APIs. *(Not the Corrective-RAG technique in §2.)*
- **[MultiHop-RAG: Benchmarking RAG for Multi-Hop Queries](https://arxiv.org/abs/2401.15391)**
  — Tang, Yang. arXiv:2401.15391, 2024. **medium** (preprint). Backs: multi-hop benchmark + LLM-assisted synthetic query/answer generation.
- **[Evaluation of Retrieval-Augmented Generation: A Survey](https://arxiv.org/abs/2405.07437)**
  — Yu, Gan, Zhang, et al. arXiv:2405.07437, 2024. **medium** (preprint). Backs: dedicated RAG-evaluation taxonomy (targets, datasets, metrics).
- **[Searching for Best Practices in RAG](https://arxiv.org/abs/2407.01219)**
  — Wang, Wang, et al. (Fudan). EMNLP 2024. **high**. Backs: empirical best-practice study of the full RAG workflow + evaluation.
- **[Natural Questions: A Benchmark for QA Research](https://aclanthology.org/Q19-1026/)**
  — Kwiatkowski, et al. (Google). TACL 2019. **high**. Backs: open-domain QA ground truth.
- **[HotpotQA: Diverse, Explainable Multi-hop QA](https://arxiv.org/abs/1809.09600)**
  — Yang, Qi, Zhang, Bengio, Cohen, Salakhutdinov, Manning. EMNLP 2018. **high**. Backs: multi-hop QA with supporting-fact annotations.
- **[TriviaQA: Large Scale Distantly Supervised Reading Comprehension](https://aclanthology.org/P17-1147/)**
  — Joshi, Choi, Weld, Zettlemoyer. ACL 2017. **high**. Backs: open-domain QA with evidence documents.
- **[MS MARCO: A Human Generated MAchine Reading COmprehension Dataset](https://arxiv.org/abs/1611.09268)**
  — Bajaj, Campos, Craswell, Nguyen, et al. (Microsoft). arXiv:1611.09268, 2016. **high** (canonical). Backs: real-query retrieval + answer ground truth.
- **[KILT: a Benchmark for Knowledge Intensive Language Tasks](https://aclanthology.org/2021.naacl-main.200/)**
  — Petroni, Piktus, Fan, Lewis, et al. (FAIR). NAACL 2021. **high**. Backs: unified knowledge-intensive benchmark with provenance.
- **[Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/abs/2406.04244)**
  — Xu, et al. arXiv:2406.04244, 2024. **medium** (preprint survey). Backs: benchmark contamination / test-set leakage and contamination-resistant evaluation.

## 10. Production evaluation & observability (LLMOps)

- **[LangSmith — Evaluation concepts](https://docs.smith.langchain.com/evaluation)** & **[Observability](https://docs.smith.langchain.com/observability)**
  — LangChain. Official docs. **high**. Backs: offline/online eval, datasets/experiments, LLM-judge evaluators, production tracing & monitoring.
- **[Arize Phoenix — Overview](https://arize.com/docs/phoenix)** & **[Tracing](https://arize.com/docs/phoenix/tracing/llm-traces)**
  — Arize AI. Official docs. **high**. Backs: OpenTelemetry-based LLM tracing and observability-driven evaluation.
- **[Langfuse — Evaluation](https://langfuse.com/docs/evaluation/overview)** & **[Observability](https://langfuse.com/docs/observability/overview)**
  — Langfuse. Official docs. **high**. Backs: human-in-the-loop eval, LLM-judge, dataset eval, open-source tracing.
- **[OpenTelemetry — Semantic conventions for generative AI systems](https://opentelemetry.io/docs/specs/semconv/gen-ai/)**
  — OpenTelemetry / CNCF. Official spec. **high**. Backs: vendor-neutral GenAI tracing spans/attributes underlying production observability.
- **[Online Evaluation for Information Retrieval](https://doi.org/10.1561/9781680831627)**
  — Hofmann, Li, Radlinski. Foundations and Trends in IR, 2016. **high**. Backs: online evaluation — A/B testing and interleaving for live IR/RAG systems.
  *Confirmed via Crossref DOI metadata — publisher primary page paywalled.*

## 11. Security, governance & operational hygiene

- **[OWASP Top 10 for Large Language Model Applications (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)**
  — OWASP. Official project. **high**. Backs: the LLM security checklist — LLM01 Prompt Injection, sensitive-information disclosure, and mitigations relevant to RAG.
- **[Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173)**
  — Greshake, et al. arXiv:2302.12173, 2023. **medium** (widely-cited preprint). Backs: indirect prompt injection — malicious instructions hidden in retrieved/external content the model ingests.
- **[Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations](https://arxiv.org/abs/2312.06674)**
  — Inan, et al. (Meta). arXiv:2312.06674, 2023. **medium** (cited preprint, Meta-official). Backs: input/output safety classification — guardrails.
- **[NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails](https://arxiv.org/abs/2310.10501)**
  — Rebedea, et al. (NVIDIA). arXiv:2310.10501, 2023 ([docs](https://docs.nvidia.com/nemo/guardrails/)). **medium**. Backs: programmable input/output/dialog rails.
- **[GDPR Art. 17 — Right to erasure ("right to be forgotten")](https://eur-lex.europa.eu/eli/reg/2016/679/oj)**
  — EU, Regulation 2016/679 ([readable text](https://gdpr-info.eu/art-17-gdpr/)). Legal standard. **high**. Backs: right-to-erasure applied to an embedding index (delete embeddings, derived chunks, caches, logs).
- **[NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework)**
  — NIST, 2023. Official standard. **high**. Backs: AI governance framing (Govern / Map / Measure / Manage).
- **[Microsoft Presidio — Data Protection and De-identification SDK](https://microsoft.github.io/presidio/)**
  — Microsoft. Official docs. **high**. Backs: PII detection and redaction/anonymization before indexing.

## 12. Foundations (primer for from-zero readers)

- **[Attention Is All You Need](https://arxiv.org/abs/1706.03762)**
  — Vaswani, et al. NeurIPS 2017. **high**. Backs: the Transformer — how modern LLMs are built (black-box depth is enough for this handbook).
- **[Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)**
  — Brown, et al. NeurIPS 2020. **high**. Backs: prompting & in-context / few-shot learning.
- **[The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)**
  — Holtzman, Buys, Forbes, Choi. ICLR 2020. **high**. Backs: decoding/sampling — nucleus (top-p), temperature, why generation is stochastic (basis for judge reproducibility).
- **[Neural Machine Translation of Rare Words with Subword Units (BPE)](https://aclanthology.org/P16-1162/)**
  — Sennrich, Haddow, Birch. ACL 2016. **high**. Backs: subword tokenization — what tokens are (underpins context windows & cost).
- **[Efficient Estimation of Word Representations in Vector Space (word2vec)](https://arxiv.org/abs/1301.3781)**
  — Mikolov, Chen, Corrado, Dean. ICLR 2013 (workshop). **medium** (foundational workshop track). Backs: embedding intuition — text as vectors, "similar words tend to be close to each other" (§1.1); the word-offset analogy *method* (its own examples, e.g. `biggest − big + small`). **Does not originate the king/queen analogy** — it restates that result citing its ref [20] (the NAACL paper below); attribute the analogy there.
- **[Linguistic Regularities in Continuous Space Word Representations](https://aclanthology.org/N13-1090/)**
  — Mikolov, Yih, Zweig. NAACL-HLT 2013. **high** (primary, ACL Anthology). Backs: the canonical `vector("King") − vector("Man") + vector("Woman") ≈ vector("Queen")` analogy and the relation-specific **vector-offset** method (semantic vs syntactic regularities). *Verified at the ACL Anthology primary 2026-06-06.*

## 13. Ingestion & data pipeline

- **[Unstructured — Partitioning](https://docs.unstructured.io/open-source/core-functionality/partitioning)**
  — Unstructured. Official docs. **high**. Backs: loading/parsing raw documents (PDF/HTML/…) into structured elements for ingestion.
- **[LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking](https://arxiv.org/abs/2204.08387)**
  — Huang, Lv, Cui, Lu, Wei (Microsoft). ACM MM 2022. **high**. Backs: layout-aware extraction (reading order, structure) for complex documents.
- **[PubTables-1M: Towards Comprehensive Table Extraction from Unstructured Documents](https://arxiv.org/abs/2110.00061)**
  — Smock, Pesala, Abraham (Microsoft). CVPR 2022. **high**. Backs: table detection & structure recognition in ingestion.
- **[Deduplicating Training Data Makes Language Models Better](https://arxiv.org/abs/2107.06499)**
  — Lee, Ippolito, et al. (Google/UPenn). ACL 2022. **high**. Backs: corpus deduplication (exact + near-dup) as ingestion hygiene.

## 14. Build engineering: generation craft, serving & reliability

Official framework/API docs backing build-side *engineering patterns* (not peer-reviewed
concepts). Treated like the §3 framework references (`ParentDocumentRetriever`, pgvector):
authoritative for the tool's own behavior; pair vendor prescriptive guidance with a concept source.

- **[Anthropic — Reduce hallucinations](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)**
  — Anthropic. Official docs. **medium** (single-vendor prescriptive guidance).
  Backs: generation-time grounding craft — give the model permission to say "I don't know" (abstention) and ask for word-for-word supporting quotes first (augmentation-prompt grounding). *Verified 2026-06-06.*
- **[OpenAI — Structured model outputs](https://platform.openai.com/docs/guides/structured-outputs)**
  — OpenAI. Official API docs. **high** (authoritative for the API behavior).
  Backs: schema-constrained generation — `json_schema` (strict) guarantees schema adherence where JSON mode does not; the reliable substrate for emitting structured citations. *Verified 2026-06-06.*
- **[LlamaIndex — Response Synthesizers](https://docs.llamaindex.ai/en/stable/module_guides/querying/response_synthesizers/)**
  — LlamaIndex. Official framework docs. **high**.
  Backs: multi-chunk answer-synthesis strategies — `refine`, `compact`, `tree_summarize`, `accumulate` and their cost/latency/quality trade-offs. *Verified 2026-06-06.*
- **[LangChain — How to add fallbacks to a runnable](https://python.langchain.com/docs/how_to/fallbacks/)**
  — LangChain. Official framework docs. **high**.
  Backs: request-path reliability — `with_fallbacks`, retries, and fallback models/routes for graceful degradation. *Verified 2026-06-06.*
- **[Anthropic — Streaming Messages](https://docs.anthropic.com/en/api/messages-streaming)**
  — Anthropic. Official API docs. **high** (authoritative for the protocol).
  Backs: response streaming to the user (the SSE event sequence) — a serving/build primitive that drives time-to-first-token. *Verified 2026-06-06.*

## To verify before citing

Not yet confirmed at a primary source — **do not cite until promoted into a section above.**

- _(none outstanding)_ — all candidate sources have been verified and promoted above.
