# Lesson 04 — Architecture and Model Strategy

**Type:** theory

> After this lesson you can decide *whether* RAG is the right tool for a given
> problem — versus long-context prompting, fine-tuning, or hybrids like RAFT and
> CAG — say *when not* to use RAG at all, and name the properties that matter when
> choosing the generator model.

## Prerequisites

- [Lesson 03 — Why RAG, and What It Is](../03-why-rag-and-what-it-is/README.md)

## Why this matters

Lesson 03 made the case *for* RAG: it fixes three structural limits of a bare LLM
(hallucination, outdated knowledge, untraceable reasoning) by moving knowledge out
of the frozen weights into an external, searchable store. But it ended with an
explicit promissory note: *that is the motivation for RAG, not a proof that RAG is
always the right tool.*

This lesson cashes that note. Before we spend the rest of the handbook building and
evaluating a RAG pipeline, we should be able to answer a prior question an engineer
is actually paid to answer: **given this problem and this knowledge, is RAG the
right architecture — and if so, which model do I put at the end of it?** RAG is one
of *several* ways to get knowledge into an LLM's answer, and sometimes a cheaper or
simpler one wins. Knowing where the boundaries are is what separates "we use RAG
because it's the thing you use" from an engineering decision you can defend.

This is still black-box, decision-level depth: we compare *approaches* by what they
cost and what they buy, not by their training internals.

## The concept

We build up five ideas: (1) the real question — how do you give an LLM knowledge it
doesn't already have; (2) what fine-tuning is, and RAG versus fine-tuning; (3) RAG
versus long-context; (4) the hybrids, RAFT and CAG; (5) when *not* to use RAG, and
how to choose the generator.

### 1. The real question: how do you get knowledge into the answer?

A bare LLM answers from two places only: the **parametric** knowledge frozen in its
weights (Lesson 02), and whatever text sits in its **prompt** at query time
(Lesson 01's in-context learning). So if the model needs knowledge it doesn't
reliably have in its weights, you have exactly two levers:

- **Change the prompt** — put the knowledge *in front of* the model at query time.
  This is in-context learning. RAG is one way to do it (retrieve the relevant text
  and insert it); **long-context** prompting is another (just paste a lot of text
  in); **CAG** is a third (preload the whole corpus once). None of these touch the
  weights.
- **Change the weights** — keep training the model on your data so the knowledge (or
  skill, or style) is baked in. This is **fine-tuning**.

RAG is the first lever done selectively. To choose it well, you have to know what
the alternatives on *both* levers actually deliver. Start with the weight-changing
one, because it's the one Lesson 01 deliberately left undefined.

### 2. What fine-tuning is — and RAG versus fine-tuning

**Fine-tuning** means continuing to train an already-trained model on additional
data, so that **its weights change** via gradient updates. The result is a *new set
of weights*. This is the precise opposite of in-context learning, which Brown et al.
(2020) define as the model performing a task "without any gradient updates or
fine-tuning" — purely from text in the prompt [1]. So the dividing line is concrete:
fine-tuning rewrites the model; in-context learning (and therefore RAG) leaves the
model untouched and only changes its input.

A natural intuition is: *to teach the model our company's facts, fine-tune it on our
documents.* The evidence says this is the wrong tool for **injecting knowledge**.
Ovadia et al. (Microsoft) compared the two head to head and found that "while
unsupervised fine-tuning offers some improvement, **RAG consistently outperforms it,
both for existing knowledge encountered during training and entirely new
knowledge**" [2]. They also report that "LLMs struggle to learn new factual
information through unsupervised fine-tuning" [2].

Two honest caveats on that result, because the scope matters:

- The fine-tuning they tested is **unsupervised** (continuing to train on the raw
  corpus text). That is the specific comparison; it is *not* a blanket verdict that
  all fine-tuning is useless. [2]
- Fine-tuning is genuinely good at a *different* job: teaching a model a **skill,
  format, tone, or domain behavior** — "always answer in this JSON shape," "adopt
  this clinical register" — rather than memorizing volatile facts. (This is the
  widely-held framing; we flag it as engineering consensus rather than a single
  measured claim, and the handbook does not teach fine-tuning hands-on.)

So the clean rule of thumb: **RAG for knowledge (facts that change, must be cited,
or are too many to memorize); fine-tuning for behavior (how to answer, not what is
true).** And they are not mutually exclusive — §4 shows a method that does both.

### 3. RAG versus long-context

Modern LLMs accept very large prompts (Lesson 01's *context window* has grown by
orders of magnitude). That raises a sharp challenge to RAG: if you can simply paste
the *entire* relevant corpus into the prompt — **long-context (LC)** — why retrieve
a handful of chunks at all?

The most direct study is Li et al. (Google DeepMind, EMNLP 2024). Their headline,
verbatim: "when resourced sufficiently, **LC consistently outperforms RAG in terms
of average performance. However, RAG's significantly lower cost remains a distinct
advantage**" [3]. Put plainly: when you can afford to feed the model everything,
long-context tends to give *better answers*; RAG's win is **cost**, not quality.

Two forces are in tension, and both trace to things we've already met:

- **Quality.** Giving the model the full context avoids the risk that retrieval
  *misses* the right passage (a retrieval failure, Lesson 03). But it is not free of
  hazards — Lesson 03's *lost-in-the-middle* positional bias means a model can still
  use information buried in a huge context poorly [6].
- **Cost.** Generation cost scales with the number of tokens in the prompt
  (Lesson 01). Pasting an entire corpus into *every* query is expensive and slow;
  retrieving a few relevant chunks is cheap. The paper frames RAG as expanding "access
  to vast amounts of information at a minimal cost" [3].

Li et al. propose a hybrid, **Self-Route**, that captures most of the value of both.
It "utilizes LLM itself to route queries based on self-reflection, under the
assumption that LLMs are well-calibrated in predicting whether a query is answerable
given provided context" [3]. Mechanically: first try RAG, but give the model the
option to decline — the prompt instructs it to "Write unanswerable if the query can
not be answered based on the provided text"; answerable queries are settled cheaply
by RAG, and only the declined ones escalate to full long-context [3]. The lesson to
carry forward: *RAG vs LC is not a war with one winner — it's a cost/quality dial,
and you can route per query.*

### 4. The hybrids: RAFT and CAG

Two named approaches sit between the pure options. You don't need to implement them
now; you need to recognize what problem each solves so you can spot when it applies.

**RAFT — Retrieval-Augmented Fine-Tuning.** This is the "do both levers" approach:
fine-tune the model *specifically for the retrieval setting*. RAFT is "a training
recipe that improves the model's ability to answer questions in a 'open-book'
in-domain setting"; given a question and a set of retrieved documents, "we train the
model to ignore those documents that don't help in answering the question, which we
call … **distractor documents**" [4]. It also trains the model to cite "verbatim the
right sequence from the relevant document" and reason chain-of-thought style [4]. So
RAFT keeps the RAG architecture (retrieve at query time) but additionally *adapts the
weights* so the generator is better at using good chunks and ignoring noise — the
direct counterexample to "RAG and fine-tuning are mutually exclusive."

**CAG — Cache-Augmented Generation.** This attacks the *retrieval step itself*. CAG
"bypasses real-time retrieval" by "preloading all relevant resources, especially when
the documents or knowledge for retrieval are of a limited and manageable size, into
the LLM's extended context and caching its runtime parameters"; then "during
inference, the model utilizes these preloaded parameters to answer queries without
additional retrieval steps" [5]. In plain terms: if your whole knowledge base fits in
the context window, load it *once*, persist the model's precomputed internal state,
and skip retrieval on every query — which "eliminates retrieval latency and minimizes
retrieval errors" [5]. The stated precondition is explicit: it applies "particularly
for cases where the documents or knowledge for retrieval are of limited, manageable
size" [5].

> **Naming caution.** CAG is *not* "semantic caching" (caching a query→answer pair to
> reuse later). CAG caches the *model's state over a preloaded corpus*, not past
> answers. The two are unrelated; the paper does not equate them.

### 5. When *not* to use RAG, and choosing the generator

Pulling §§2–4 together, RAG is the right call when knowledge is **large, changing,
must be cited, or domain-specific** — exactly the conditions Lesson 03's three gaps
described, and what Gao et al. mean when they say RAG "allows for continuous knowledge
updates and integration of domain-specific information" and merges the model's
intrinsic knowledge "with the vast, dynamic repositories of external databases" [7].
But there are clean cases where a *different* lever is simpler or better:

| Situation | Better fit than naive RAG | Why |
|---|---|---|
| Corpus is small/bounded **and** fairly static | **CAG** (or long-context) | Whole corpus fits the window; preload once, skip retrieval — no retrieval errors or latency [5] |
| You can afford full context and want top quality | **Long-context** | LC beats RAG on average quality when resourced [3] |
| The need is *behavior* (format/tone/skill), not facts | **Fine-tuning** | Unsupervised FT underperforms RAG at injecting *knowledge* [2]; FT's strength is behavior |
| The model already knows it / no external knowledge needed | **Plain prompting** | Adding retrieval is cost and complexity with nothing to retrieve |
| You have RAG **and** want the generator better at it | **RAFT** | Fine-tune for the open-book setting: use good chunks, ignore distractors [4] |

The realistic answer is often *combine*: RAG for the volatile facts, fine-tuning for
the response behavior, per-query routing (Self-Route) for the cost/quality dial. The
point of this lesson is not to memorize a winner but to *ask the question* — what
knowledge, how big, how often it changes, what budget — before reaching for any tool.

**Choosing the generator.** Once you've decided retrieval belongs in the design, the
LLM at the *generate* step (Lesson 03) is itself a choice. The properties that
actually matter for a RAG generator follow from what we've established:

- **Context window size.** It must comfortably hold the augmentation prompt
  (instruction + retrieved chunks + question). The RAG-vs-LC trade-off [3] and
  lost-in-the-middle behavior [6] both live here: more room helps, but a model that
  uses the *middle* of its context poorly will waste it.
- **Grounding and instruction-following.** A RAG generator must reliably *use the
  supplied context* and *abstain* when the context doesn't contain the answer.
  Anthropic's guidance, for instance, recommends giving the model "permission to say
  'I don't know'" and asking it to ground answers in supporting quotes [8] — a
  generator that can't follow such instructions will hallucinate past the context.
- **Cost and latency.** Per-token cost and time-to-first-token bound what you can
  afford at the prompt sizes RAG produces (Lesson 01). This is the same cost axis the
  RAG-vs-LC study turns on [3].

We deliberately do *not* prescribe a specific model here (model capabilities and
prices change fast, and the handbook pins versions only where it runs code). Treat
these three as the *criteria*; the hands-on grounding craft that exploits them comes
when we build generation later in the handbook.

## Worked example

Continue the help-desk assistant from Lesson 03 — but now imagine it three different
ways, and decide the architecture for each *before* defaulting to RAG.

**Case A — a 12-page "Getting Started" guide, rewritten once a quarter.**
The entire knowledge base is tiny and nearly static. It fits in a modern context
window with room to spare. Building an index, embedding chunks, and retrieving per
query is real machinery for almost no benefit. **Decision: CAG or long-context** —
preload the guide once and answer from it, skipping retrieval entirely [5]. You'd
revisit only if the corpus grows or starts changing often.

**Case B — 80,000 support articles, with dozens edited every day.**
Large *and* volatile — the canonical RAG case. You cannot fit 80k articles in the
prompt affordably (cost, §3), and you cannot fine-tune the facts in (they change
daily, and FT underperforms at knowledge injection anyway [2]). Retrieving the few
relevant articles per query is exactly the cost win RAG is for [3], and updating a
fact is a re-index, not a retrain (Lesson 03). **Decision: RAG.**

**Case C — RAG works, but answers must always be valid JSON for a downstream UI, and
sometimes ramble or ignore a clearly-relevant article.**
Two *different* problems. The "always valid JSON / consistent tone" need is
*behavior*, not knowledge — a fit for **fine-tuning** (or, more cheaply, strict
output formatting later in the handbook). The "ignores a clearly-relevant retrieved
article / gets distracted by an irrelevant one" need is precisely what **RAFT**
trains for: use the helpful documents, ignore the distractors [4]. **Decision: keep
RAG, and add fine-tuning for behavior** — the two levers together, not instead of
each other.

Notice the move in all three: we asked *what kind of need is this — knowledge or
behavior? how big and how volatile is the corpus? what's the budget?* — and let the
answer pick the tool. That question, not a fixed preference for RAG, is the lesson.

## Your turn

No code — these are decision exercises. For each, name the approach and justify it
from the lesson's sources, not from preference.

1. **The static manual.** A legal team wants a Q&A bot over a single 40-page contract
   template that changes maybe once a year. Argue for an approach other than naive
   RAG, and name the precondition that makes it valid.

2. **Knowledge vs behavior.** A colleague says "our model keeps using American date
   formats and we need European ones, so let's add RAG over a style guide." Diagnose
   whether this is a knowledge problem or a behavior problem, and say which lever
   (RAG / fine-tuning) actually fits — citing the Ovadia finding.

3. **The cost argument.** A stakeholder reads that "long-context models beat RAG" and
   wants to drop retrieval and paste the whole knowledge base into every prompt. Using
   Li et al., give the one sentence that concedes their point *and* the one sentence
   that defends keeping RAG — and name the hybrid that does both.

4. **Combine the levers.** Describe a single system that uses RAG *and* fine-tuning at
   the same time without contradiction, and name the technique from the lesson that
   formalizes it.

## Common pitfalls / misconceptions

- **"Fine-tune the model on our docs to teach it our facts."** The measured result is
  the opposite: RAG "consistently outperforms" unsupervised fine-tuning for knowledge
  injection, including for entirely new knowledge [2]. Use fine-tuning for *behavior*,
  RAG for *facts*.

- **"Long-context made RAG obsolete."** Long-context wins on average *quality* when
  resourced, but "RAG's significantly lower cost remains a distinct advantage" [3].
  It's a cost/quality dial, and you can route per query (Self-Route), not a knockout.

- **"RAG and fine-tuning are mutually exclusive."** RAFT does both: it keeps
  retrieval and fine-tunes the generator to use relevant chunks and ignore distractor
  documents [4]. The levers compose.

- **"CAG is just caching answers."** No — CAG preloads the *corpus* into the context
  window and caches the model's runtime state to skip retrieval [5]; it is unrelated
  to semantic (query→answer) caching. And it only applies when the corpus is "of
  limited, manageable size" [5].

- **"Pick the biggest/best model and you're done."** A RAG generator's relevant
  properties are specific: a context window that holds the augmentation prompt (and
  uses its middle well [6]), the ability to follow grounding instructions and abstain
  [8], and acceptable cost/latency [3] — not raw leaderboard rank.

## Check your understanding

1. State the dividing line between **fine-tuning** and **in-context learning** in one
   sentence — what physical thing changes in each case? (Tie it to Brown et al.'s "no
   gradient updates" wording [1].)

2. Li et al. find long-context "consistently outperforms RAG" on average quality, yet
   the field still builds RAG systems constantly. Explain *why* that finding does not
   make RAG obsolete, and describe what Self-Route does on a query it judges
   *answerable* versus *unanswerable* [3].

3. A team needs (a) answers grounded in 200,000 frequently-updated documents and (b)
   every answer formatted as a fixed JSON schema. Which need is RAG for, which is
   fine-tuning for, and why — and could one system do both? [2][4]

4. Your colleague proposes CAG for a knowledge base of 5 million regularly-changing
   web pages. Give the *two* reasons from the lesson that this violates CAG's stated
   conditions [5], and name the approach that fits instead.

## Summary & next

We turned "what RAG is" into "is RAG the right tool here, and which model." The two
levers for giving an LLM new knowledge are **changing the prompt** (RAG / long-context
/ CAG — in-context, weights untouched [1]) and **changing the weights**
(**fine-tuning**). The evidence: RAG beats unsupervised fine-tuning for *knowledge*
injection [2], while fine-tuning's strength is *behavior*; long-context beats RAG on
average *quality* but RAG wins on *cost* [3]; **RAFT** fuses the levers (fine-tune for
the open-book setting, ignoring distractors [4]) and **CAG** removes retrieval when the
corpus is small and bounded [5]. So RAG is the right call for **large, changing,
citable, domain-specific** knowledge [7] — and when it is, the generator is chosen for
context window, grounding/abstention ability [8], and cost/latency [3][6], not raw
rank.

Next (lesson 05, *A minimal end-to-end RAG*) we stop comparing and start building:
we wire a **runnable naive RAG** end to end — load → chunk → embed → retrieve →
generate — with an orchestration framework. It's the baseline system the rest of the
handbook measures and improves.

## Sources

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
  — Lewis, Perez, Piktus, Petroni, et al., NeurIPS 2020. **[1]** RAG works through
  in-context use of retrieved text, with the model's weights unchanged — the contrast
  that defines the "change the prompt vs change the weights" split.
- [Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs](https://arxiv.org/abs/2312.05934)
  — Ovadia, Brief, Mishaeli, Elisha (Microsoft), arXiv:2312.05934. **[2]** RAG
  "consistently outperforms" *unsupervised* fine-tuning for knowledge injection,
  including entirely new knowledge. *Cited preprint; the comparison is scoped to
  unsupervised FT — not a verdict on all fine-tuning.*
- [Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach](https://arxiv.org/abs/2407.16833)
  — Li, et al. (Google DeepMind), EMNLP 2024 (industry track). **[3]** Long-context
  beats RAG on average quality when resourced; RAG's advantage is cost; **Self-Route**
  routes per query by letting the model judge answerability.
- [RAFT: Adapting Language Model to Domain Specific RAG](https://arxiv.org/abs/2403.10131)
  — Zhang, Patil, Jain, Shen, …, Zaharia, Stoica, Gonzalez (UC Berkeley),
  arXiv:2403.10131. **[4]** Retrieval-augmented fine-tuning: train the generator for
  the open-book setting to use relevant docs and ignore distractor documents. *Cited
  preprint.*
- [Don't Do RAG: When Cache-Augmented Generation is All You Need for Knowledge Tasks (CAG)](https://arxiv.org/abs/2412.15605)
  — Chan, Chen, Cheng, Huang, arXiv:2412.15605. **[5]** Preload a limited, manageable
  corpus into the context window and cache the model's runtime state to bypass
  real-time retrieval. *Cited preprint; distinct from semantic caching; the KV-cache
  mechanism detail is in the body, not the abstract.*
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
  — Liu, Lin, Hewitt, Paranjape, et al., TACL 2023. **[6]** Positional bias: models use
  information at the start/end of a long context better than in the middle — relevant
  to both the long-context trade-off and choosing a generator.
- [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)
  — Gao, Xiong, et al., arXiv:2312.10997 (v5). **[7]** RAG's value framing: continuous
  knowledge updates and integration of domain-specific information from vast, dynamic
  external databases. *Heavily-cited preprint, self-labeled "Ongoing Work"; not
  peer-reviewed.*
- [Anthropic — Reduce hallucinations](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
  — Anthropic, official docs. **[8]** Generator grounding/abstention as a selection
  criterion: give the model permission to say "I don't know" and ground answers in
  supporting quotes. *Single-vendor prescriptive guidance.*
