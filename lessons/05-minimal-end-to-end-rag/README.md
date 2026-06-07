# Lesson 05 — A Minimal End-to-End RAG

**Type:** theory+practice

> After this lesson you can wire a complete, runnable naive RAG pipeline —
> load → chunk → embed → retrieve → augment → generate — with the LangChain
> orchestration framework, run it against a local model, and read what each stage
> produced. This is the baseline system the rest of the handbook measures and
> improves.

## Prerequisites

- [Lesson 04 — Architecture and Model Strategy](../04-architecture-and-model-strategy/README.md)

(Through L04 this also assumes [Lesson 02 — Embeddings and Search](../02-embeddings-and-search/README.md)
for vectors and similarity, and [Lesson 03 — Why RAG, and What It Is](../03-why-rag-and-what-it-is/README.md)
for the four-stage pipeline.)

## Why this matters

Lessons 01–04 were all black-box theory: what an LLM is, what embeddings are, what
RAG is and when to use it. Lesson 04 ended on a promise — *stop comparing, start
building.* This is where we cash it.

There is a reason the first four lessons had no code. RAG is not a single algorithm
you implement; it is a **pipeline of stages wired together** (Lesson 03), and in
practice you wire them with an **orchestration framework** that supplies the parts —
loaders, splitters, vector stores, retrievers, model clients, and a way to compose
them. You almost never build these from scratch. So the first runnable lesson is as
much about *meeting the framework* as it is about RAG itself.

We build the **naive** version on purpose: the simplest thing that runs end to end,
with every default left plain. It will have visible weaknesses — and that is the
point. You cannot improve, or even evaluate, a system you have not built. This
baseline is the fixed reference the rest of the handbook returns to: every later
technique (better chunking, hybrid retrieval, reranking, query rewriting) is a
*change to one stage of this pipeline*, and every evaluation metric is a way to
*measure whether that change helped*.

## The concept

We are building the pipeline Lesson 03 named — index → retrieve → augment →
generate — as the smallest amount of real code that runs. Two framing ideas first,
then the five stages.

### The orchestration-framework layer

A RAG system is glue between several moving parts: something that reads your files,
something that splits them, an embedding model, a place to store and search vectors,
a generator model, and the plumbing that passes data from one to the next. An
**orchestration framework** is the library that provides those parts behind uniform
interfaces and lets you compose them. We use **LangChain** [4]. The value it adds is
not intelligence — it is *uniformity*: a `Document` object every stage understands,
a `VectorStore` interface that looks the same whether it is in memory or a hosted
database, and a way to pipe components together. The official LangChain RAG tutorial
wires exactly the pipeline we build here [4].

> **Naming.** "Index" in Lesson 03's diagram is two code steps — **chunk** then
> **embed + store** — so the pipeline below has *five* stages, not four. The split
> is purely mechanical; conceptually it is still the same indexing step.

### The two phases (which code runs when)

Lesson 03 distinguished the **offline** phase (build the index, once) from the
**online** phase (answer a query, every time). In our script they run back to back
because the corpus is tiny and the index lives in memory, but keep the distinction:
stages 1–3 are offline (you would run them when documents change), and stages 4–5
are online (they run per question). In a real system the index is built once and
persisted; here we rebuild it on every run for simplicity.

### Stage 1 — Load

The framework reads each source file into a **`Document`**: an object with
`page_content` (the text) and `metadata` (here, the file path). Loading exists so
that everything downstream is uniform — a PDF, an HTML page, and a `.txt` file all
become the same `Document` shape, and the rest of the pipeline never has to know
where the text came from. We use `TextLoader` over a folder of plain-text help-desk
articles.

### Stage 2 — Chunk

Retrieval operates on **chunks**, not whole files. If you embed an entire article as
one vector, a query about one sentence has to match the average of the whole
document, and the passage you actually want is diluted. So we split each document
into smaller, slightly overlapping pieces with a `RecursiveCharacterTextSplitter`
(`chunk_size=500`, `chunk_overlap=50` characters) [4]. The overlap keeps a sentence
that straddles a boundary from being cut in half.

*How* to chunk well — by size, by sentence, by structure, with what overlap — is a
real engineering topic with measurable consequences, and it gets its own lessons in
the ingestion part of the course. Here we take a small, sane default and move on;
treat the numbers as illustrative, not optimal.

### Stage 3 — Embed + index

Each chunk is turned into a vector with the **embedding model** (Lesson 02), and the
vectors are put in a **vector store** we can search by similarity. We use
`OllamaEmbeddings` pointed at a **local embedding model** [5] (the model name comes
from `.env`, so you can swap in your own — each model has its own fixed vector size;
the run below used one that produces 2560-dimensional vectors, printed at runtime)
and an `InMemoryVectorStore` [4], which keeps the vectors in a plain Python
structure with no database to set up. That is all a baseline needs; production
vector stores (persistence, scale, filtering) come later.

### Stage 4 — Retrieve

For a question, the store embeds it **with the same model** and returns the
**top-k** nearest chunks by vector similarity (Lesson 02's cosine idea). We ask for
`k = 3`. This is the single most consequential stage for quality: the LLM in stage 5
sees *only these chunks*. If the right passage is not retrieved, no amount of
generation skill can recover it — retrieval quality is a ceiling on answer quality.
(That ceiling is exactly what the retrieval-evaluation lessons later learn to
measure.)

### Stage 5 — Augment + generate

We build the prompt by **inserting the retrieved chunks as context**, then ask the
generator (`ChatOllama` pointed at a **local chat model** [5], also set in `.env`)
to answer **only from that context** and to **say it doesn't know** rather than
guess. Two of these are the grounding craft
from Lesson 04: *use the supplied context* and *give the model permission to
abstain* [6]. This is what makes the answer traceable to the corpus (Lesson 03's
third gap) instead of to the model's frozen weights. We compose the prompt, model,
and an output parser with LangChain's pipe syntax — `prompt | llm | parser` [4].

## Worked example

The runnable code is [`demo.py`](./demo.py). Run it from the repo root:

```bash
uv run python -m lessons.05-minimal-end-to-end-rag.demo
```

It loads a tiny **fictional** help-desk corpus for "Acme Cloud" (the `data/` folder —
invented sample content, not a real product and not an evaluation dataset), then
runs the five stages for the question *"How do I cancel my subscription, and will I
get a refund?"* — the running example from Lessons 02–03. Here is the **real output**
of one run; the models for this run came from `.env` (generator `qwen3:14b`,
embeddings `qwen3-embedding:4b`, both served by Ollama; LangChain 0.3.x;
`langchain-ollama` 0.3.10) — yours will differ if your `.env` points elsewhere:

```
======================================================================
1. LOAD
======================================================================
Loaded 5 documents from data/:
  - account-password.txt  (570 chars)
  - billing-cancellation.txt  (730 chars)
  - billing-refunds.txt  (609 chars)
  - data-export.txt  (576 chars)
  - plans-and-tiers.txt  (630 chars)

======================================================================
2. CHUNK
======================================================================
Split 5 documents into 10 chunks (chunk_size=500, chunk_overlap=50).

======================================================================
3. EMBED + INDEX
======================================================================
Embedded 10 chunks with 'qwen3-embedding:4b' (2560-dim vectors) and indexed them in memory.

======================================================================
4. RETRIEVE
======================================================================
Question: How do I cancel my subscription, and will I get a refund?

Top 3 retrieved chunks:
  [1] billing-cancellation.txt: Cancelling your Acme Cloud subscription You can cancel your Acme Cloud plan at any time fr...
  [2] billing-cancellation.txt: When you cancel an annual plan, you remain on the paid tier until the annual term ends; we...
  [3] billing-refunds.txt: Refund policy Acme Cloud offers a refund only within 14 days of the original purchase or o...

======================================================================
5. AUGMENT + GENERATE
======================================================================
Answer:
To cancel your Acme Cloud subscription, go to **Settings > Billing > Cancel plan**. Cancellation takes effect at the end of your current billing period, and you’ll retain access to paid features until that date.

**Refunds**:
- You’re eligible for a refund **only within 14 days** of your original purchase or renewal. Contact **support@acme.example** during this window for a refund to your original payment method.
- After 14 days, refunds are not issued for the current period. Cancellation does not result in a refund for the period already paid.
```

Read the run as the pipeline itself. **Load** turned 5 files into 5 `Document`s.
**Chunk** split them into 10 pieces — roughly two per article, because each article
is longer than 500 characters. **Embed + index** produced one 2560-dim vector per
chunk. **Retrieve** scored all 10 chunks against the question and returned the 3
nearest: two from the cancellation article and one from the refunds article —
notice it pulled from *two different documents*, which is exactly why we chunk and
retrieve instead of picking one file. **Generate** then composed an answer that
fuses both: the cancellation procedure (from chunks 1–2) and the refund window (from
chunk 3). Every claim in the answer traces back to a retrieved chunk; the model was
not asked to know anything about Acme Cloud on its own.

Two honest notes. First, generation is **not bit-for-bit deterministic** even at
`temperature=0`, so your answer wording may differ slightly from the above — the
*retrieved chunks* should be stable, the prose around them less so. Second, this run
*looks* good, but "looks good on one question" is not evaluation — we have no measure
of whether retrieval found the *best* chunks, or whether the answer is faithful to
them. Building that measure is the whole next part of the course.

## Your turn

Run the demo, then change one thing at a time in `demo.py` and re-run, observing the
effect on the printed stages:

1. **Force an abstention.** Change `QUESTION` to something the corpus does not cover,
   e.g. `"What is Acme Cloud's phone number?"`. Retrieval will still return 3 chunks
   (it always returns its nearest *k*, relevant or not) — watch whether the generator
   correctly says it doesn't know instead of inventing a number. This is the
   abstention instruction [6] doing its job, and it previews a real failure mode:
   the retriever cannot say "nothing matches."

2. **Shrink the context.** Set `TOP_K = 1`. Re-ask the original question. With only
   the top chunk retrieved, does the answer lose the refund half? This shows directly
   how retrieval bounds the answer — stage 4 decides what stage 5 can possibly say.

3. **Break the grounding.** Temporarily delete the "answer ONLY from the context …
   say you don't know" sentence from the system prompt and ask the abstention
   question from (1). Compare: an ungrounded model will happily fabricate. Put the
   instruction back. This is why grounding is craft, not decoration.

You do not need to fix anything. The goal is to *feel* where the naive baseline is
fragile — those fragile spots are the syllabus for everything that follows.

## Common pitfalls / misconceptions

- **"The framework is doing the RAG."** No — the framework supplies uniform parts and
  plumbing [4]; *you* chose the chunk size, the *k*, the embedding model, and the
  prompt. Every quality lever is a decision the framework leaves to you.

- **"It answered correctly, so the pipeline is good."** One correct answer is an
  anecdote, not a measurement. We have not checked whether retrieval surfaced the
  *right* chunks, whether the answer is *faithful* to them, or how it does across
  *many* questions. That is evaluation, and it starts in Lesson 06.

- **"Retrieval returns relevant chunks."** Retrieval returns the *k nearest* chunks,
  relevant or not. On an out-of-corpus question it still returns 3 — the nearest of a
  bad lot. Naive retrieval has no notion of "nothing matches"; the generator's
  abstention is the only guard, and it is imperfect.

- **"Bigger k is better."** More chunks means more context, more cost, and more room
  for the model to be distracted or to bury the answer in the middle of a long prompt
  (Lesson 04's *lost-in-the-middle* [3]). *k* is a trade-off to tune and measure, not
  a dial to max out.

- **"In-memory vector store = toy, useless."** For a baseline it is exactly right:
  zero setup, fully visible. Production stores add persistence, scale, and metadata
  filtering — but the *interface* is the same one you just used, so swapping it later
  changes one line, not the pipeline [4].

## Check your understanding

1. The pipeline has five code stages but Lesson 03 named four. Which conceptual stage
   splits into two code steps, and why is the split mechanical rather than conceptual?

2. In the worked example, retrieval returned chunks from *two different documents* and
   the answer used both. Explain why chunking-then-retrieving makes that possible in a
   way that "find the single most relevant file" would not.

3. You ask the demo a question the corpus has no answer to. Describe exactly what each
   of stages 4 and 5 does, and identify which single instruction in the prompt is the
   only thing standing between the user and a fabricated answer [6].

4. A colleague says "let's just set `k` to 20 so we never miss the right chunk." Give
   two distinct reasons from this lesson (and Lesson 04) why that can *hurt* answer
   quality, not just cost [3].

5. We claim retrieval quality is a *ceiling* on answer quality. Construct a short
   scenario with this pipeline where the generator is perfect but the final answer is
   still wrong, and say which stage is at fault.

## Summary & next

We built the handbook's first runnable system: a naive RAG pipeline wired with
LangChain [4] — **load** files into `Document`s, **chunk** them with a character
splitter, **embed** the chunks with a local model and **index** them in an in-memory
vector store, **retrieve** the top-k by similarity, and **augment + generate** a
grounded, abstaining answer with a local LLM [5][6]. We ran it end to end and read
each stage's real output, and we named where it is fragile: retrieval returns its
nearest *k* whether or not anything is relevant, *k* is an untuned trade-off, and "it
looked right once" is not a measurement.

That last gap is the pivot of the whole course. We now have a baseline that *runs* but
that we cannot yet *judge*. Lesson 06 (*Why evaluation is hard*) takes that head on:
what would it even mean to say this pipeline is "good," why measuring it is harder
than it looks, and what has to be true of a test before its numbers mean anything.
From there the loop is always the same — **build a stage, measure it, improve it** —
and this lesson is the thing every measurement and every improvement is applied to.

## Sources

- [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)
  — Gao, Xiong, et al., arXiv:2312.10997 (v5). **[1]** The four-stage
  index→retrieve→(augment)→generate framing this pipeline implements; the "Naive RAG"
  baseline. *Heavily-cited preprint, self-labeled "Ongoing Work"; not peer-reviewed.*
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
  — Lewis, Perez, Piktus, Petroni, et al., NeurIPS 2020. **[2]** The RAG architecture:
  a parametric generator conditioned on text from a non-parametric retriever — what
  stages 3–5 wire together.
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
  — Liu, Lin, Hewitt, Paranjape, et al., TACL 2023. **[3]** Positional bias: a model
  uses information buried in the middle of a long context poorly — why larger *k* is a
  trade-off, not a free win.
- [LangChain — Build a Retrieval Augmented Generation (RAG) App](https://python.langchain.com/docs/tutorials/rag/)
  — LangChain, official framework docs. **[4]** The orchestration-framework layer and
  the wiring used here: `RecursiveCharacterTextSplitter`, `InMemoryVectorStore`,
  top-k retrieval via `as_retriever`, and LCEL composition (`prompt | llm | parser`).
  *API behavior verified by running it against langchain 0.3.x this session.*
- [LangChain — ChatOllama](https://python.langchain.com/docs/integrations/chat/ollama/)
  and [OllamaEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/ollama/)
  — LangChain, official integration docs. **[5]** Using a local Ollama-served chat
  model and embedding model as the generator and indexer. *Verified by execution this
  session (`qwen3:14b`, `qwen3-embedding:4b`).*
- [Anthropic — Reduce hallucinations](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
  — Anthropic, official docs. **[6]** The grounding/abstention craft in the prompt:
  answer from the supplied context and give the model permission to say "I don't know."
  *Single-vendor prescriptive guidance.*

