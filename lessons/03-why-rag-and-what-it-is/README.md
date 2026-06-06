# Lesson 03 — Why RAG, and What It Is

**Type:** theory

> After this lesson you can explain *why* retrieval-augmented generation exists
> (which concrete limitations of a bare LLM it fixes), state *what* RAG is in one
> sentence, trace the **index → retrieve → augment → generate** pipeline end to
> end, and place a system on the **Naive / Advanced / Modular** maturity spectrum.

## Prerequisites

- [Lesson 01 — LLMs, Tokens, and Prompting](../01-llms-tokens-and-prompting/README.md)
- [Lesson 02 — Embeddings and Search](../02-embeddings-and-search/README.md)

## Why this matters

The last two lessons gave us the two halves of RAG without naming the whole.
Lesson 01 left us with an LLM as a **black-box next-token predictor** whose only
input is the text in its prompt, and whose built-in knowledge is **parametric** —
frozen into its weights at training time. Lesson 02 gave us **embeddings** and
**semantic search**: a way to turn text into vectors and *find* the passages whose
meaning matches a query, plus the name for knowledge kept *outside* the model and
fetched on demand — **non-parametric**.

RAG is simply the act of wiring those two halves together: search a knowledge
store for relevant text, then put that text in the prompt so the LLM answers from
it. This lesson names the whole machine, says precisely why you would build it, and
gives you the vocabulary — the four pipeline stages and the three maturity
paradigms — that the rest of the handbook uses as its skeleton. Everything we build
or evaluate later is one stage of this pipeline, done well.

This is still black-box, build-and-evaluate depth: we care about *what each stage
does and why*, not the internals of the retriever or the generator.

## The concept

We build up four ideas: (1) why a bare LLM is not enough, (2) what RAG is, (3) the
four-stage pipeline, and (4) the Naive / Advanced / Modular maturity spectrum.

### 1. Why RAG exists — the gap in a bare LLM

A large language model on its own is impressive but has limitations that are
*structural*, not bugs to be patched. The RAG survey by Gao et al. (2023–24) opens
by naming them: LLMs "encounter challenges like **hallucination, outdated
knowledge, and non-transparent, untraceable reasoning processes**" [2]. Take them
one at a time, because each maps to something we already established:

- **Hallucination.** Asked something outside or at the edge of its training, the
  model still produces a fluent, confident answer — which may be **factually
  wrong**. We met this in Lesson 02 as a hazard of purely *parametric* knowledge.
- **Outdated knowledge.** Parametric knowledge is **frozen at the training cutoff**
  (Lesson 01). The model cannot know anything that happened after it was trained,
  and you cannot teach it a new fact without retraining or fine-tuning its weights.
- **Non-transparent, untraceable reasoning.** When the answer lives only in the
  weights, there is **no source to cite or audit** — you cannot ask the model
  *where* a fact came from.

RAG attacks all three at once by changing *where the knowledge lives*. Gao et al.
describe it directly: RAG "enhances LLMs by retrieving relevant document chunks
from external knowledge base through semantic similarity calculation. By
referencing external knowledge, RAG effectively reduces the problem of generating
factually incorrect content," and "allows for continuous knowledge updates and
integration of domain-specific information" [2]. Map those back:

| Bare-LLM limitation | What RAG does about it |
|---|---|
| Hallucination | Grounds the answer in retrieved text the model is told to use |
| Outdated knowledge | Update the *store*, not the weights — no retraining |
| No provenance | The retrieved passages *are* the citation — you know what was used |

> This is the *motivation* for RAG, not a claim that RAG is always the right tool.
> When to prefer RAG over alternatives like long-context prompting or fine-tuning —
> and when *not* to use RAG at all — is a real engineering decision we take up in
> the next lesson (L04). Here we only establish what gap RAG was built to fill.

### 2. What RAG is

We can now state it precisely. RAG was named by Lewis et al. (2020), who built
models that combine "a **parametric memory**" — a pre-trained sequence-to-sequence
model — with "a **non-parametric memory**" that is "a dense vector index of
Wikipedia, accessed with a pre-trained neural retriever" [1]. That is exactly the
Lesson 02 pairing: the *parametric* generator (good at language and reasoning) plus
a *non-parametric* store (current, updatable, auditable knowledge).

So, in one sentence:

> **RAG is the technique of retrieving relevant text from an external knowledge
> store at query time and placing it in the LLM's prompt, so the model generates
> its answer grounded in that retrieved text rather than from its weights alone.**

The survey's operational description matches: RAG "enhances LLMs by retrieving
relevant document chunks from external knowledge base through semantic similarity
calculation" [2] — note "semantic similarity calculation," which is precisely the
embeddings-plus-cosine machinery of Lesson 02 doing the *retrieve* step.

Two things RAG is *not*, to fix the boundary early:

- It is **not retraining or fine-tuning.** The model's weights never change. RAG
  works through *in-context learning* (Lesson 01): whatever you put in the prompt
  steers the output, with no gradient updates [1].
- It is **not just "search."** Search returns documents *to a person*; RAG feeds
  the retrieved text *to a model* that then composes an answer over it. Retrieval
  is one stage, not the whole system.

### 3. The pipeline: index → retrieve → augment → generate

A RAG system runs in two phases. One happens **offline, ahead of time**; three
happen **online, per query**.

**Indexing (offline).** Before any question is asked, we prepare the knowledge
store. Documents are loaded, split into **chunks** (Lesson 01 told us why: a corpus
is far larger than any context window), each chunk is turned into an **embedding**
(Lesson 02), and the vectors are stored in an index that supports fast similarity
search. This is build-it-once-and-reuse work; the survey calls indexing the first
step of the pipeline [2].

Then, for each user query, three stages run in order:

1. **Retrieve.** Embed the query and use semantic similarity to pull the top-k most
   relevant chunks from the index (Lesson 02's "find the nearest vectors").
2. **Augment.** Assemble the prompt: combine an instruction (e.g. "Answer using only
   the context below"), the retrieved chunks, and the user's question into one input
   for the model. This integration step is what the survey isolates as
   **"Augmentation"** — one of the three core areas of RAG technique, alongside
   retrieval and generation [2].
3. **Generate.** The LLM runs its autoregressive loop (Lesson 01) over that
   assembled prompt and produces the answer, ideally grounded in the supplied
   context.

```
        OFFLINE (once)                         ONLINE (per query)
   ┌───────────────────────┐
   │ documents             │            query ─┐
   │   → load → chunk      │                   ▼
   │   → embed → store ────┼──► index ──►  [1] RETRIEVE  (top-k chunks)
   └───────────────────────┘                   │
                                                ▼
                                           [2] AUGMENT   (instruction + chunks + query
                                                          → one prompt)
                                                │
                                                ▼
                                           [3] GENERATE  (LLM answers over the prompt)
                                                │
                                                ▼
                                             answer
```

A naming note, so the sources line up. Lewis et al. and the survey both center on
three technique areas — **retrieval, generation, and augmentation** [1][2] — and
the survey describes the simplest pipeline as "indexing, retrieval, and generation"
[2]. The four-stage "index → retrieve → augment → generate" framing this handbook
uses simply makes the *augment* step (building the prompt) explicit as its own box,
because in practice that is where a lot of design effort goes. The steps are the
same; we have just drawn the prompt-assembly step on its own.

### 4. The maturity spectrum: Naive → Advanced → Modular

Not all RAG systems are equally sophisticated. The survey organizes "over 100 RAG
studies" into "**three main research paradigms**" [2] — a useful maturity ladder.

**Naive RAG** is "the earliest methodology … a traditional process that includes
indexing, retrieval, and generation, which is also characterized as a
**'Retrieve-Read' framework**" [2]. It is exactly the pipeline of §3 with nothing
extra: embed, retrieve top-k, stuff into the prompt, generate. It is the right
*starting* point — and the survey is candid about where it breaks down. Among its
drawbacks [2]:

- **Retrieval** "often struggles with precision and recall, leading to the
  selection of misaligned or irrelevant chunks, and the missing of crucial
  information."
- **Generation** can still "face the issue of hallucination, where it produces
  content not supported by the retrieved context."
- **Augmentation** can produce "disjointed or incoherent outputs," "redundancy
  when similar information is retrieved from multiple sources," and the model can
  "overly rely on augmented information … simply echo[ing] retrieved content."

Notice these are exactly the things we will later learn to *measure* — retrieval
precision/recall and generation faithfulness are core evaluation targets precisely
because Naive RAG fails at them.

**Advanced RAG** "introduces specific improvements to overcome the limitations of
Naive RAG," focused on "enhancing retrieval quality" via "**pre-retrieval and
post-retrieval strategies**" [2]:

- **Pre-retrieval** optimizes the index and the query before searching — e.g.
  "query rewriting … query expansion" to make the question "clearer and more
  suitable for the retrieval task" [2].
- **Post-retrieval** processes the results before generating — e.g. **re-ranking**
  the retrieved chunks and reordering them. (One concrete reason ordering matters:
  Liu et al. (2023) found LLMs use information better when it sits near the start or
  end of a long context than buried in the middle — a "U-shaped" positional bias
  [3]. So *where* a retrieved chunk lands in the prompt affects whether the model
  uses it.)

**Modular RAG** "advances beyond the former two … offering enhanced adaptability
and versatility," adding new components (e.g. a search module, routing across data
sources) and "restructured RAG modules and rearranged RAG pipelines" [2]. Crucially
it is not a clean break: "Modular RAG builds upon the foundational principles of
Advanced and Naive RAG, illustrating a progression and refinement within the RAG
family" [2]. This is where the iterative and agentic systems we study at the end of
the handbook live.

The takeaway is not to memorize three labels but to internalize the *arc*: **start
naive, measure where it fails, add targeted optimizations.** That build → measure →
improve loop is the spine of this entire handbook.

## Worked example

Let's trace **one question through the whole pipeline**, reusing the Lesson 02
scenario. Suppose a help-desk assistant sits on top of a product's support docs, and
a user asks:

```
How do I cancel my plan?
```

**Offline, already done — Indexing.** The support corpus was chunked and embedded.
One chunk is the passage titled *"Steps to terminate your subscription"*; its
embedding sits at some point in vector space. (This happened once, at build time;
it is reused for every query.)

**[1] Retrieve.** We embed the query `"How do I cancel my plan?"` and rank chunks by
cosine similarity. Even though the query and the passage share *no content words*
("cancel/plan" vs "terminate/subscription"), they are close in meaning-space, so the
*terminate your subscription* chunk scores highly and is pulled into the top-k —
this is exactly the synonymy win we computed by hand in Lesson 02. A pure
keyword system would have missed it.

**[2] Augment.** We build the prompt by slotting the retrieved chunk into a
template:

```
You are a support assistant. Answer the user's question using ONLY the context below.
If the context does not contain the answer, say you don't know.

Context:
"To terminate your subscription, open Settings → Billing, click 'Cancel plan',
and confirm. Your access continues until the end of the current billing period."

Question: How do I cancel my plan?
```

**[3] Generate.** The LLM runs its autoregressive loop over that prompt and produces:

```
Go to Settings → Billing, click "Cancel plan", and confirm. You'll keep access
until the end of your current billing period.
```

Now see what each RAG limitation-fix bought us in this single trace:

- **No hallucination of steps** — the model paraphrased the supplied passage instead
  of inventing a plausible-sounding cancellation flow.
- **Updatable** — if the cancellation flow changes, we edit *the document* and
  re-index. The model's weights never change; nothing is retrained.
- **Auditable** — we know the answer came from the *"terminate your subscription"*
  chunk, so we could show or cite it.

And see where it could still go wrong — i.e. why Naive isn't the end:

- If **retrieval** had missed the right chunk (precision/recall failure), the model
  would answer from its weights or refuse — a *retrieval* problem, fixed with
  Advanced-RAG techniques and measured with retrieval metrics.
- If the model **ignored the context** and added a made-up step (e.g. "call
  support"), that is a *generation/faithfulness* problem — measured separately.

That split — retrieval failures vs generation failures — is the reason the handbook
evaluates the two halves with different metrics. We are already seeing the shape of
it.

## Your turn

No code yet — this is a reasoning exercise.

1. **Locate each fix.** A bare LLM, asked "what's our current refund window?", says
   "30 days" — confidently, but the company changed it to 14 days last month. Name
   which of the three bare-LLM limitations this is, and describe concretely what the
   *retrieve* and *augment* stages would change about the answer.

2. **Place the system.** A team ships RAG v1: embed the query, grab the top-5
   chunks, paste them in, generate. Users complain it sometimes retrieves the wrong
   chunks for vague questions. Which paradigm is v1, and name *one* pre-retrieval and
   *one* post-retrieval Advanced-RAG move (from the lesson) that could help — and say
   which stage each one acts on.

3. **Defend the boundary.** A colleague says "RAG is just fine-tuning the model on
   our docs." Using Lesson 01's in-context learning and the parametric/
   non-parametric distinction, explain in two sentences why that statement is wrong.

## Common pitfalls / misconceptions

- **"RAG changes / trains the model."** No. The weights are untouched; RAG works
  entirely through *in-context learning* — putting text in the prompt at query time
  [1]. Updating knowledge means editing the store and re-indexing, not retraining.

- **"RAG is just search with extra steps."** Search hands documents to a *person*;
  RAG feeds retrieved text to a *model* that composes an answer over it. Retrieval
  is one of four stages, not the whole system.

- **"More retrieved chunks = better answers."** Naive "stuff everything in" runs
  into the context window and per-token cost (Lesson 01), and into positional bias —
  models use the middle of a long context less well than its ends [3]. *Which* and
  *how many* chunks, and *where* you place them, are real decisions (the Augment and
  post-retrieval stages), not afterthoughts.

- **"Advanced/Modular replaces Naive."** They *build on* it: Modular RAG "builds
  upon the foundational principles of Advanced and Naive RAG" [2]. The right path is
  to start naive, measure, and add complexity where the measurements say you need it.

- **"RAG eliminates hallucination."** It *reduces* it by grounding answers in
  retrieved text [2], but the generator can still ignore or contradict the context —
  which is exactly why we will later measure *faithfulness* as its own metric.

## Check your understanding

1. State, in one sentence each, what the **retrieve**, **augment**, and **generate**
   stages do — and say which one relies on the embeddings/cosine machinery from
   Lesson 02 and which relies on the autoregressive loop from Lesson 01.

2. RAG is said to make knowledge "updatable" and "auditable" in a way a bare LLM is
   not. Explain *mechanically* why — what physical thing do you change to update a
   fact, and what physical thing lets you audit where an answer came from?

3. A system retrieves perfectly relevant context but the model's answer still
   contradicts it. Which *stage* failed, is this a retrieval problem or a generation
   problem, and which paradigm's drawbacks (Naive's) does this match?

4. Why is "start with Naive RAG" good advice even though the survey lists so many
   ways Naive RAG fails? (Tie your answer to the build → measure → improve arc.)

## Summary & next

We named the whole machine. **RAG exists** to fix three structural limits of a bare
LLM — hallucination, outdated knowledge, and untraceable reasoning [2] — by moving
knowledge from the model's frozen weights into an external, searchable store. **RAG
is** the pairing of a *parametric* generator with a *non-parametric* retrieved store
[1], run as a four-stage pipeline: **index** (offline) then **retrieve → augment →
generate** (per query). And RAG systems sit on a maturity spectrum — **Naive**
(Retrieve-Read), **Advanced** (pre-/post-retrieval optimization), **Modular**
(restructured pipelines) [2] — which is really the build → measure → improve arc of
this handbook in miniature.

Next (lesson 04, *Architecture and model strategy*) we make the decision this lesson
deliberately deferred: **when to actually reach for RAG** versus alternatives —
long-context prompting, fine-tuning, RAFT, cache-augmented generation — when *not*
to use RAG at all, and how to choose the generator. We move from "what RAG is" to
"is RAG the right tool here, and which pieces."

## Sources

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
  — Lewis, Perez, Piktus, Petroni, et al., NeurIPS 2020. **[1]** The paper that named
  RAG: parametric memory (a seq2seq generator) + non-parametric memory (a dense
  vector index), combined via in-context use without changing the weights.
- [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)
  — Gao, Xiong, et al., arXiv:2312.10997 **v5 (27 Mar 2024)**. **[2]** Motivations
  for RAG (hallucination / outdated knowledge / untraceable reasoning); the
  retrieval–generation–augmentation framing; the Naive ("Retrieve-Read") / Advanced
  (pre-/post-retrieval) / Modular paradigm spectrum and Naive RAG's drawbacks.
  *(Heavily-cited preprint, self-labeled "Ongoing Work" — not peer-reviewed; quotes
  pinned to v5.)*
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
  — Liu, Lin, Hewitt, Paranjape, et al., TACL 2023. **[3]** Positional bias (the
  U-shaped curve): LLMs use information at the start/end of a long context better
  than in the middle — why post-retrieval ordering/re-ranking matters.
