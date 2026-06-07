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
| `docs/sources.md` | Verified source registry (§1–§14). Lessons cite only from here. | ~93 sources, all verified. "To verify" section empty. §14 (build engineering) added 2026-06-06. §12 gained Mikolov et al. NAACL 2013 (*Linguistic Regularities*) for L02; word2vec entry re-scoped (it does not originate the king/queen analogy). L04 used existing §1 entries (no new sources); fixed RAG-vs-LC affiliation Google → **Google DeepMind**. L05 added two §14 framework-doc entries (LangChain RAG tutorial; LangChain ChatOllama/OllamaEmbeddings integration pages) — pages live (HTTP 200) + API verified by execution. |
| `docs/concept-map.md` | Concept universe + module dependency graph (M0–M14), each concept tagged to a source. | Expanded; build+evaluate scope. Build-side audit (2026-06-06) added architecture/generation-craft/vector-layer/text-to-SQL/reliability; M13 distributed to stages; ingestion+retrieval split into M2/M3. All tag refs resolve to the registry. |
| `docs/syllabus.md` | Phase-2 artifact: the ordered lesson plan derived from the concept map. | **APPROVED — 39 lessons (re-approved 2026-06-06).** Was 38; inserted L17 `learned-sparse-retrieval` (SPLADE/COIL) after hybrid (L16); renumbered former 17–38 → 18–39; prereqs remapped; no-forward-ref re-checked (executed, passes). Phase 3 builds from here (L01–L02 done). |
| `.claude/skills/authoring-lessons/` | Skill to author lessons (SKILL.md + lesson-template.md + tested `scripts/validate_lesson.py`). | Working; validator tested. |
| `lessons/` | One folder per lesson (built in Phase 3). | **L01–L05 DONE** (`01-llms-tokens-and-prompting`, `02-embeddings-and-search`, `03-why-rag-and-what-it-is`, `04-architecture-and-model-strategy` — all theory; **`05-minimal-end-to-end-rag` — first `theory+practice`, runnable `demo.py`**; validator green; user-reviewed). Plus `README.md` conventions + built-lessons index. |
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
- **Git**: remote `origin` = `git@github.com:neodmy/rag-handbook` (branch `main`).
  History (milestones): `0dc6450` (initial scaffold + Phase 0/1), `54c1a06`
  (build-side audit + concept-map restructure M0–M14), `aa014c4` (approved Phase 2
  syllabus), then Phase 3 lessons L01→L03 and the navigation/workflow commits
  (lessons index, README link, authoring-skill step 7); latest on `main` is the L03
  set. Commit only when the user asks.

## Current state (as of 2026-06-07)

- Phases 0 and 1 complete. Concept map expanded after **two adversarial audits**
  (a 3-lens pass, then a deeper 5-lens pass) to a full build+evaluate scope:
  M0 primer, M1 foundations, M2 ingestion, M3 retrieval & query understanding,
  M4 generation/grounding, M5–M13 evaluation (why-eval, retrieval eval, generation
  metrics, faithfulness, LLM-judge, metric suites, datasets/benchmarks, statistics,
  production/ops & governance), M14 iterative & agentic RAG.
- Source registry at ~92 verified entries across §1–§14; "To verify" is empty.
- Scope reframed to a **complete RAG course** (user decision, 2026-06-06).
- A **build-side concept-map audit** (2026-06-06, 5 parallel lenses) added
  architecture/model-strategy (M1), generation craft (now M4), vector-layer
  engineering + text-to-SQL (now M3), and request-path reliability (now M13) —
  all sources verified at the primary. Multimodal RAG and GraphRAG were considered
  but **kept deferred** by user decision. (Module numbers reflect the later
  M2/M3 split + renumber; the audit happened before it.)

**Phase 2 — derive the syllabus** (`docs/syllabus.md`): **DRAFT DONE (revised
twice after an adversarial audit), at the approval gate.** **38 lessons** in
global teaching order, **eval-driven progressive** arc: runnable baseline early
(L05), "why eval is hard" right after (L06), then build→measure→improve per stage.
Methodology is also progressive: an `interpreting-results` primer (L22 — held-out
+ "is the delta real?") sits right before the first improvement; deep
measurement-validity methodology is the capstone (L35). RAG security (indirect
prompt injection) split into its own build-time lesson (L29). No-forward-reference
check passes (script).

**Syllabus APPROVED (2026-06-06) and committed.**

**Phase 3 — IN PROGRESS.** **L01 `llms-tokens-and-prompting` is DONE** (theory, no
prereqs): a from-zero black-box primer on LLMs & autoregressive generation, tokens &
the context window, prompting & in-context learning, and sampling
(temperature/top-k/top-p). All claims verified at the primary this session (Holtzman
full text via ar5iv for the precise top-p/top-k/temperature definitions; Brown
abstract for the "without any gradient updates" in-context-learning quote); the §12
registry entries already covered it, so **no registry change**. The sampling section
went through three rounds of user-driven restructuring (numeric examples added, then
moved out of the concept into a single integrative worked example, then collapsed
into one two-step narrative where peaked↔flat falls out of the loop). Validator green.

**L02 `embeddings-and-search` is DONE** (theory, prereq L01): a from-zero primer on
embeddings & vector similarity (cosine; an intuition for vector dimensionality),
semantic vs keyword/sparse search (synonymy / vocabulary-mismatch vs exact-token
failure modes), and parametric vs non-parametric knowledge (the framing RAG is built
on). Every non-trivial claim verified at the primary this session (delegated to a
verification subagent: word2vec §1.1, Sentence-BERT abstract, IIR Ch. 6 cosine + Ch. 9
synonymy, DPR abstract 9–19%, Lewis parametric/non-parametric wording). The registry
gained one source — Mikolov et al. NAACL 2013 *Linguistic Regularities* (the real
origin of the king/queen analogy) — and the word2vec entry was re-scoped accordingly.
Cosine arithmetic in the worked example checked by hand. Validator green; user-reviewed
(added a dimensionality-intuition paragraph on user feedback).

**L03 `why-rag-and-what-it-is` is DONE** (theory, prereqs L01/L02): names the whole
machine — why RAG exists (the three structural limits of a bare LLM: hallucination /
outdated knowledge / untraceable reasoning, mapped to L02's parametric knowledge),
what RAG is (one-sentence def anchored in Lewis's parametric + non-parametric pairing;
two boundaries — *not* fine-tuning, *not* just search), the **index → retrieve →
augment → generate** pipeline (offline/online ASCII diagram + an honest name-reconciliation
note: the survey says "indexing, retrieval, generation" with augmentation as one of three
technique areas; we just draw *augment* as its own box), and the **Naive / Advanced /
Modular** maturity spectrum (Retrieve-Read + its drawbacks → pre/post-retrieval → modular,
framed as the build→measure→improve arc). Worked example traces L02's "cancel my plan"
query through all four stages, showing what each fix buys and where it can still fail
(retrieval vs generation — seeding the metric split). **No registry change** — the three
sources were already verified; Gao survey citation pinned to **v5 (27 Mar 2024)**, "Ongoing
Work" flagged as arXiv metadata not prose. Used Lost in the Middle [3] black-box to motivate
post-retrieval reordering. Verified Gao's exact wording at the primary (v5 full text via a
research subagent) before teaching it. Validator green; user-reviewed.

**L04 `architecture-and-model-strategy` is DONE** (theory, prereq L03): takes up what L03
deferred — the architecture decision. Two levers for giving an LLM new knowledge: *change
the prompt* (RAG / long-context / CAG — in-context, weights untouched [Lewis]) vs *change
the weights* (**fine-tuning**, defined here against Brown's "no gradient updates"). Then the
comparisons: RAG vs fine-tuning (Ovadia — RAG "consistently outperforms" *unsupervised* FT
for knowledge injection; FT is for behavior, not facts); RAG vs long-context (Li et al.,
Google DeepMind — LC wins quality when resourced, RAG wins cost; Self-Route routes per query
by answerability); the hybrids RAFT (FT + RAG, ignore distractors) and CAG (preload a bounded
corpus + cache state, no retrieval — only when the corpus fits); a *when-not-to-use-RAG*
decision table; and generator-selection criteria (context window, grounding/abstention,
cost/latency — no model prescribed). Worked example: L03's help-desk in three corpus profiles.
**No registry change** — all 4 §1 sources (RAG-vs-LC, FT-vs-Retrieval, RAFT, CAG) plus
Lewis/Gao/Brown/Lost-in-the-Middle/Anthropic-§14 were already verified; a verification subagent
re-fetched the exact quotable wording at each primary before citing. Flagged in-lesson: preprint
statuses; Ovadia scoped to *unsupervised* FT; CAG's KV-cache detail is body-not-abstract (not
quoted verbatim); "FT for behavior" marked as engineering consensus, not a measured claim. Fixed
the RAG-vs-LC affiliation in the registry (Google → Google DeepMind). Validator green; user-reviewed.

**L05 `minimal-end-to-end-rag` is DONE** (type `theory+practice`, prereq L04 — the first lesson with
runnable code; see the Session log entry below for full detail). It wires a naive RAG end-to-end with
**LangChain + a local Ollama model**, runs, and pastes real output; it is the baseline the rest of the
handbook measures/improves.

**Next session: build L06 `why-evaluation-is-hard`** (type **`theory`**, prereq L05) via the
`authoring-lessons` skill. It is the pivot into the evaluation arc: eval targets (retrieval vs
generation), reference-based vs reference-free, offline vs online, error attribution & the recall
ceiling, eval design/ablation, abstention & robustness as targets. This is also where the **first real
evaluation dataset** (with ground truth, in `datasets/`) should be built — see the backlog note. Build
lessons strictly in syllabus order; each lesson's `## Prerequisites` are the lower-numbered lessons in
its syllabus row; per skill step 7, add L06's row to the `lessons/README.md` index.

(Scope alignment across `CLAUDE.md`, `README.md`, `handbook-method.md`, and the
authoring skill/template is **done** — all now framed as "build + evaluate".)

## Open threads / backlog

- Deferred nice-to-haves (add only if a lesson needs them, with a verified source
  first): late-interaction retrieval (ColBERT), GraphRAG, multimodal RAG, semantic
  caching, judge calibration, safety/toxicity eval, multi-turn/conversational eval.
- Consider recording in `handbook-method.md` the rule "coverage audits bias toward
  flagging" (lesson from this session).
- **Build a serious evaluation dataset for L06+** (user decision, 2026-06-07). L05's
  `data/` is a throwaway toy corpus *for L05 only*; from L06 on we need a real dataset
  with ground truth, living in `datasets/` under the RAGAS field contract
  (`user_input` / `response` / `retrieved_contexts` / `reference`).
- **Latent: RAGAS judge model default is `mistral`, not present on the Ollama host**
  (`ragas_lab/config.py` `ollama_judge_model`). Irrelevant to L05 (no eval yet), but
  must be pinned to a real host model before the L06+ evaluation lessons run RAGAS.
- Syllabus approved & committed; **Phase 3 (build lessons) starts next session at
  L01**. Lesson code/data live in `lessons/NN-slug/`; reusable infra in `ragas_lab/`.

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

### 2026-06-06 — Phase 2: draft syllabus + adversarial audit + revision
- Derived `docs/syllabus.md` from the concept map (first cut: 35 lessons,
  build-first then eval).
- **Adversarial audit** (completeness + ordering): extracted all 117 map concepts
  and matched each to a lesson — coverage near-complete (only "eval-methodology
  surveys" unnamed). Flagged: no end-to-end baseline lesson; eval fully
  back-loaded vs the repo's eval-driven ethos; MTEB used (L09) before taught;
  L04 assumed fine-tuning the primer excludes; stats taught late.
- **User decisions:** add an **early runnable baseline** (quickstart) and make the
  course **eval-driven & progressive**.
- **Revised to 36 lessons** with a build→measure→improve arc per stage: baseline
  L05, "why eval is hard" L06, retrieval build → retrieval eval → query
  understanding, generation build → generation eval, suites/methodology/production/
  advanced. Cheap audit fixes applied (MTEB intro in L11, fine-tuning framing in
  L04, eval-methodology named in L32, RAGAS prereq). No-forward-ref check re-run:
  clean (36 lessons).
- **Second revision (same day):** applied three pedagogical refinements — (1)
  pulled a statistics **primer** forward to L22 (`interpreting-results`: held-out
  + significance/power) so the first "X improved Y" claim is made with hygiene,
  keeping deep methodology as the L35 capstone; (2) **split RAG security** (indirect
  prompt injection) out of the output-mechanics lesson into its own build-time
  lesson (L29); (3) re-cut production — moved request-path reliability into the
  safe-operation lesson (L37). Now **38 lessons**; no-forward-ref check clean.
- **Syllabus APPROVED by the user (2026-06-06)**; committed & pushed alongside
  these logbook updates.
- **Left off at:** Phase 2 complete. **Next session: begin Phase 3 — build
  lesson 01 (`llms-tokens-and-prompting`) via the `authoring-lessons` skill**,
  then proceed in syllabus order. Phases 0–2 done; registry frozen at ~92 sources
  (extend only via verified per-lesson research).

### 2026-06-06 — Build-side concept-map audit (Tier 1 incorporated)
- Ran a 3rd adversarial audit, this time biased to the **build** side (5 parallel
  research lenses: generation craft, vector-layer engineering, architecture/model
  strategy, data sources/representations, build engineering & reliability). Every
  candidate gap required a primary source verified live.
- Headline finding: M3 was *failure-modes only* (no generation craft), M2 was a
  *catalogue* (no cost/scale knobs), and there was **no architecture-decision node
  at all**. User chose to incorporate **all Tier 1**; **kept Tier 2 deferred**
  (multimodal RAG, GraphRAG stay out despite the audit's argument to promote).
- Verified 7 arXiv papers + 7 vendor/framework docs at the primary myself
  (re-confirmed, not trusting subagent summaries): RAG-vs-LongContext (EMNLP'24),
  FT-vs-Retrieval, RAFT, CAG, TableRAG, Spider, Matryoshka; FAISS guidelines, HF
  quantization, LlamaIndex synthesizers, LangChain fallbacks, OpenAI structured
  outputs, Anthropic grounding + streaming. (OpenAI embeddings blog 403'd — used
  the Matryoshka paper as the primary anchor instead.)
- Edits: `sources.md` — new **§14** (build engineering) + entries in §1 (RAG-vs-LC,
  FT-vs-Retrieval, RAFT, CAG) and §3 (FAISS guidelines, quantization, Matryoshka,
  TableRAG, Spider). `concept-map.md` — M1 architecture cluster, M3 generation
  craft, M2 vector-layer + text-to-SQL, M12 reliability, M13 conversational
  contextualization; Coverage check updated (§1–§14, 3rd audit, deferral notes
  clarifying CAG≠semantic-caching and multi-turn build vs eval). No module
  renumbering and no Mermaid edges changed.
- **Follow-up reorg (same day):** distributed the old M13 "advanced techniques"
  to their stage modules (user chose "distribute to stage" over "capstone"):
  query-understanding family (rewriting, HyDE, **query expansion**, **query
  decomposition**, routing, conversational contextualization, fusion) → **M2**;
  context curation → **M3**; contextual-retrieval enrichment → **M2** (ingestion).
  M13 slimmed to iterative & agentic control-flow (multi-hop, self-correcting,
  agentic) and retitled; added `M3 → M13` edge. Two gaps closed: query expansion
  (`§4: Intro to IR` Ch. 9 — note extended) and query decomposition (added
  `§2: Self-Ask`, Findings of EMNLP 2023, verified at primary). Note for Phase 2:
  M2 is now large and will spawn several lessons; the query-understanding
  sub-cluster is *understood* after M2 but *tuned/evaluated* with M5 metrics, so
  sequence it after M5.
- **Module split (same day):** the oversized M2 (it was doing four jobs) was
  split into **M2 Ingestion** (text engineering: loading/cleaning/chunking/
  metadata/contextual-enrichment) and **M3 Retrieval & query understanding**
  (embeddings/index/sparse/dense/hybrid/rerank/vector-layer-engineering/
  text-to-SQL/query-family). Downstream modules renumbered +1 → final range
  **M0–M14** (generation = M4, … iterative/agentic = M14). New split edge
  `M2 → M3`; all `(needs …)` notes recomputed and verified acyclic; `[§N:…]`
  source tags untouched. Module ≠ lesson: M3 will still spawn several lessons in
  Phase 2.
- **Left off at:** map + registry updated and self-consistent (M0–M14); awaiting
  user review of the changes. Phase 2 (syllabus) still the next milestone.

### 2026-06-06 — Concept-map module renumbering
- Renumbered the concept map: the old `M-1` primer is now `M0`, and every later
  module shifted +1 (old `M0`→`M1`, … old `M12`→`M13`). New range: **M0–M13**.
- Updated `concept-map.md` end to end (Mermaid graph node IDs + labels, all 14
  headers, every `(needs …)` cross-module note, the "Coverage check" callouts)
  and the two module-range references in this logbook. No other doc referenced
  module numbers (verified by grep). Source `[§N: …]` tags untouched.

### 2026-06-06 — Phase 3 begins: L01 built
- Started Phase 3. Built **L01 `lessons/01-llms-tokens-and-prompting/README.md`**
  (type `theory`, no prereqs) via the `authoring-lessons` skill: a from-zero
  black-box primer covering (1) LLM & autoregressive generation, (2) tokens &
  context window, (3) prompting & in-context learning, (4) sampling
  (temperature/top-k/top-p).
- **Verified every non-trivial claim at the primary** (not from memory): fetched
  Holtzman full text via ar5iv for the exact definitions — nucleus/top-p ("smallest
  set… whose cumulative probability mass exceeds `p`", dynamic nucleus), top-k
  (fixed count; "differ only in… where to truncate"), temperature ("`t`∈[0,1) skews
  the distribution towards high probability events"); Brown abstract for the
  in-context-learning quote ("without any gradient updates or fine-tuning… purely
  via text"). §12 registry entries already covered all of it → **no registry edit**.
  WebFetch was blocked by a hook; used context-mode `ctx_fetch_and_index` instead.
- **Sampling section restructured three times on user feedback** (each round
  improved it): first added accurate numeric examples (softmax computed with real
  arithmetic, illustrative logits); then pulled all tables out of "The concept"
  (now definitions + mental model only: temperature *reshapes*, top-k/top-p
  *truncate*) into a single integrative **worked example**; finally collapsed that
  into **one two-step narrative** so the peaked↔flat contrast (top-p adapts, fixed
  `k` over-/under-includes) falls naturally out of two consecutive loop steps rather
  than a contrived "Distribution A/B". Also fixed a left-vs-right table-reading
  inconsistency the user caught.
- Type stays `theory` (no `demo.py`); all numbers flagged illustrative, the one
  idealization (Step 2 being "flat" after `Paris`) flagged in-text. Validator green.
- **Left off at:** L01 done & user-approved. **Next: L02 `embeddings-and-search`**
  (`theory`, prereq L01). Registry frozen at ~92 (extend only via verified
  per-lesson research). This session committed & pushed.

### 2026-06-06 — Phase 3: L02 built
- Built **L02 `lessons/02-embeddings-and-search/README.md`** (type `theory`, prereq
  L01) via the `authoring-lessons` skill: a from-zero primer on (1) embeddings &
  vector similarity (cosine = direction not magnitude; an intuition for what a
  *dimension* is and why models use hundreds–thousands), (2) semantic vs
  keyword/**sparse** search (lexical matches words & misses synonyms; dense matches
  meaning & can miss exact tokens — opposite failure modes, neither universally
  better), and (3) **parametric vs non-parametric** knowledge (weights vs a queried
  vector index — the framing RAG is built on).
- **Verified every non-trivial claim at the primary** via a verification subagent:
  word2vec §1.1 ("similar words tend to be close"); the king/queen analogy is from
  the **companion** NAACL paper, not the word2vec paper (attribution trap caught);
  Sentence-BERT abstract (BERT pairwise ≈ 65h / SBERT ≈ 5s, cosine-comparable);
  IIR Ch. 6 (vector space model + cosine) and Ch. 9 (synonymy — note "vocabulary
  mismatch" is community phrasing, IIR says *synonymy*); DPR abstract (dense beats
  BM25 9–19% top-20); Lewis et al. verbatim "parametric memory … non-parametric
  memory … dense vector index of Wikipedia."
- **Registry change:** added **§12** *Linguistic Regularities* (Mikolov, Yih, Zweig,
  NAACL-HLT 2013, `N13-1090`, **high**, verified at ACL Anthology) for the analogy;
  **re-scoped** the word2vec (`1301.3781`) entry to state it does *not* originate the
  analogy (it restates it citing its ref [20]). Net registry ≈ 93.
- Worked example uses illustrative 3-D toy vectors (flagged); the cosine arithmetic
  (Q·A=1.44→cos≈0.990, Q·B=0.34→cos≈0.304) was checked by hand. Includes the honest
  counter-case (exact-token query where keyword wins). Type `theory`, no `demo.py`.
- **User feedback applied:** added a dimensionality-intuition paragraph to §1 (each
  number = a coordinate/axis; 3-D visualizable, 1,536-D not, arithmetic identical)
  and turned the worked-example "3-dimensional" mention into a callback. Validator
  green after each change.
- Discussed (no code): dimensions are *not* individually human-interpretable
  (meaning is distributed; relationships are directions/offsets); embedding
  dimensionality is a pre-set hyperparameter (Matryoshka only truncates a pre-set
  max); keyword search ≈ sparse retrieval (sparse names the representation, DPR
  abstract backs the sparse-vs-dense contrast).
- **Left off at:** L02 done & user-approved; committed & pushed. **Next: L03
  `why-rag-and-what-it-is`** (`theory`, prereqs L01, L02).

### 2026-06-06 — Syllabus revision: add learned sparse retrieval (L17)
- After the L02 push, took up the parked question of whether to add **learned sparse
  retrieval** (SPLADE/COIL). **User chose** "new dedicated lesson right after L16
  hybrid" (over "after L13" or "fold into L16").
- **Verified SPLADE at the primary** (subagent, arXiv abstracts): v1 (Formal,
  Piwowarski, Clinchant; **SIGIR 2021**, high) — sparse lexical term-weight vectors
  that "inherit … the exact matching of terms and the efficiency of inverted
  indexes," sparsity via regularization + log-saturation, "competitive … with
  state-of-the-art dense and sparse methods"; v2 (arXiv, medium) — ">9% NDCG@10 on
  TREC DL 2019, SOTA on BEIR." COIL already in §3 (NAACL 2021) as supporting context.
  Caveat: WordPiece-vocab / FLOPS-reg / explicit vocabulary-mismatch framing are in
  the paper body, not the abstract — cite body sections when building the lesson.
- **Edits:** `sources.md` §3 — added SPLADE v1 (high) + v2 (medium), extended the
  COIL note. `concept-map.md` M3 — added a **Learned sparse retrieval** node
  (`[§3: SPLADE]` `[§3: COIL]`) in the matching-methods cluster after hybrid.
  `syllabus.md` — inserted **L17 `learned-sparse-retrieval`** (theory+practice, M3,
  prereqs 12/13/16); renumbered 17–38 → 18–39; remapped every downstream prereq;
  updated sequencing notes (new note 8 explains the placement), the no-forward-ref
  note, and the coverage check (M3→11–20, 24–25). Now **39 lessons**.
- **Re-checked no forward references with an executed script** (parse tables → assert
  prereq < lesson, contiguous 1–39, no dupes, no dangling): **passes**.
- **Re-approved by the user (2026-06-06)**; committed & pushed.
- **Left off at:** syllabus at 39 lessons, approved & committed. Build order
  unchanged — **next build is still L03** `why-rag-and-what-it-is`.

### 2026-06-07 — Phase 3: L03 built
- Built **L03 `lessons/03-why-rag-and-what-it-is/README.md`** (type `theory`, prereqs
  L01/L02) via the `authoring-lessons` skill: (1) **why RAG exists** — the three
  structural limits of a bare LLM (hallucination / outdated knowledge / untraceable
  reasoning), each mapped back to L02's parametric knowledge, with a "limitation → what
  RAG does" table; (2) **what RAG is** — one-sentence definition anchored in Lewis's
  parametric + non-parametric pairing, plus two boundaries (*not* fine-tuning, *not* just
  search); (3) the **index → retrieve → augment → generate** pipeline with an offline/online
  ASCII diagram and an honest name-reconciliation note; (4) the **Naive / Advanced /
  Modular** maturity spectrum framed as the build→measure→improve arc. Worked example
  traces L02's "cancel my plan" query through all four stages (what each fix buys;
  retrieval-vs-generation failure split — seeds the later metric split).
- **Verified Gao et al. survey wording at the primary** (research subagent fetched v5 full
  text via arxiv.org/html): motivations, the retrieval/generation/augmentation framing,
  Naive ("Retrieve-Read") + its drawbacks, Advanced (pre-/post-retrieval), Modular — all
  quoted verbatim. **No registry change** (all three sources — Lewis, Gao survey, Lost in
  the Middle — were already verified). Pinned the Gao citation to **v5 (27 Mar 2024)** and
  flagged "Ongoing Work" as arXiv metadata, not paper prose.
- Type `theory`, no `demo.py`. Deferred RAG-vs-FT/long-context/RAFT/CAG explicitly to L04
  (no forward refs). Used Lost in the Middle [3] black-box to motivate post-retrieval
  reordering. Validator green; user-reviewed.
- **Navigation + workflow upkeep (same session):** added an "Index (built so far)"
  table to `lessons/README.md` (built lessons only; full plan stays in the syllabus);
  added a **step 7 to the `authoring-lessons` workflow** — "update that index when a
  lesson ships" — so it stays current; and added a **Lessons section to the root
  `README.md`** linking to the index + syllabus. All committed & pushed.
- **Left off at:** L03 done & user-approved; committed & pushed. **Next: L04
  `architecture-and-model-strategy`** (`theory`, prereq L03). Reminder for the next
  build: per the new skill step 7, add L04's row to the `lessons/README.md` index.

### 2026-06-07 — Phase 3: L04 built
- Built **L04 `lessons/04-architecture-and-model-strategy/README.md`** (type `theory`,
  prereq L03) via the `authoring-lessons` skill — the architecture-decision lesson L03
  deferred. Frame: two levers for new knowledge — *change the prompt* (RAG / long-context /
  CAG, in-context, weights untouched) vs *change the weights* (**fine-tuning**, defined here
  against Brown's "no gradient updates"). Then: RAG vs FT (Ovadia — RAG "consistently
  outperforms" *unsupervised* FT for knowledge injection; FT for behavior); RAG vs long-context
  (Li et al., Google DeepMind — LC wins quality when resourced, RAG wins cost; **Self-Route**);
  hybrids **RAFT** (FT+RAG, ignore distractors) and **CAG** (preload bounded corpus + cache,
  skip retrieval); a *when-NOT-to-use-RAG* decision table; generator-selection criteria
  (context window / grounding+abstention / cost+latency — no model prescribed). Worked example:
  L03's help-desk across three corpus profiles (static→CAG/LC; large+volatile→RAG; JSON+distraction→RAG+RAFT/FT).
- **Verification subagent** re-fetched exact quotable wording at each primary before citing
  (2407.16833, 2312.05934, 2403.10131, 2412.15605, plus Gao 2312.10997). **No registry change** —
  all sources already verified. Flagged in-lesson: preprint statuses; Ovadia scoped to *unsupervised*
  FT (not all FT); CAG's KV-cache detail is body-not-abstract (used the verbatim "caching its runtime
  parameters" instead); "FT for behavior" marked engineering consensus, not a measured claim; no
  specific generator model prescribed (versions change fast).
- **Registry fix:** corrected the RAG-vs-LC (2407.16833) affiliation **Google → Google DeepMind**
  (caught during verification). Validator green; index row added to `lessons/README.md`; user-reviewed.
- **Left off at:** L04 done & user-approved; committed & pushed. **Next: L05 `minimal-end-to-end-rag`**
  (`theory+practice` — first lesson with runnable code; prereq L04). Per skill step 5, the practice
  arm must run (`uv run python -m lessons.05-minimal-end-to-end-rag.demo`) with real output pasted;
  verify framework APIs via Context7 first. Per step 7, add L05's row to the index.

### 2026-06-07 — Phase 3: L05 built (first runnable lesson)
- Built **L05 `lessons/05-minimal-end-to-end-rag/`** (type `theory+practice`, prereq L04) via the
  `authoring-lessons` skill — the handbook's **first runnable lesson**. Teaches the orchestration-framework
  layer and wires a naive RAG end-to-end with **LangChain**: load (`TextLoader`) → chunk
  (`RecursiveCharacterTextSplitter`, 500/50) → embed+index (`OllamaEmbeddings` + `InMemoryVectorStore`) →
  retrieve (top-k=3 via `as_retriever`) → augment+generate (`ChatOllama`, grounded+abstaining prompt, LCEL
  `prompt | llm | parser`). `README.md` + `demo.py` + a **throwaway toy** help-desk corpus in `data/`
  (5 fictional "Acme Cloud" articles — flagged in-lesson as not a real product and **not** an eval dataset).
- **Ran it for real** (`uv run python -m lessons.05-minimal-end-to-end-rag.demo`) against the remote Ollama
  host from `.env`; pasted the real output (5 docs → 10 chunks → 2560-dim vectors → top-3 chunks from 2 docs →
  grounded answer fusing cancellation + refund). Flagged: LLM generation not bit-for-bit deterministic even
  at temp 0; retrieved chunks stable, prose varies. Validator green; ruff clean; pytest 2/2.
- **Decisions (verified, not from memory):** generator `qwen3:14b`, embeddings `qwen3-embedding:4b` (both on
  the user's remote host, confirmed via `/api/tags`); vector store `InMemoryVectorStore` (in-RAM dict, no
  persistence — recomputed each run; verified by inspecting the installed class). **Integration = `langchain-ollama`**
  (added `>=0.3,<0.4` → resolved `0.3.10`): corrected the user's assumption with **PyPI metadata** — the RAGAS
  bug only caps langchain/core/community to 0.3.x; `langchain-ollama` 0.3.x requires `langchain-core<1.0`, so it
  is compatible. The "no langchain-ollama" note in CLAUDE.md was scoped to the RAGAS *judge* path only. Whole
  stack stays 0.3.x (`langchain-core 0.3.86`, `ragas 0.4.3` intact).
- **Config refactor (`ragas_lab/config.py`):** added `ollama_chat_model` (reads `OLLAMA_CHAT_MODEL`, or the
  legacy `OLLAMA_MODEL` via `AliasChoices`); `demo.py` now sources **all three** knobs (endpoint, chat, embed)
  from `settings`/`.env` — no hardcoded model names. Verified base_url/chat/embed resolve from `.env` by running.
- **Registry change:** `docs/sources.md` §14 gained two **verified** framework-doc entries — LangChain RAG
  tutorial and the LangChain ChatOllama/OllamaEmbeddings integration pages (pages live HTTP 200 2026-06-07; API
  behavior additionally verified by execution). Conceptual claims reuse already-verified §1 (Gao, Lewis,
  Lost-in-the-Middle) and §14 (Anthropic grounding/abstention). Framework patterns cross-checked via Context7
  before writing.
- **Lesson prose** kept model-agnostic on user feedback (stages 3/5 say "a local embedding/chat model … set in
  `.env`"); concrete model names remain only where they document the actual shown run + in Sources `[5]`.
- **Backlog opened:** build a serious eval dataset (ground truth, `datasets/`) for L06+; pin the RAGAS judge
  model (default `mistral` absent on host) before L06+ eval runs.
- **Left off at:** L05 done & user-approved; committing & pushing this session. **Next: L06
  `why-evaluation-is-hard`** (`theory`, prereq L05) — the pivot into evaluation; build the first real dataset there.
