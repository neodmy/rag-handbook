# Lesson 06 — Why Evaluation Is Hard

**Type:** theory

> After this lesson you can name *what* a RAG system has to be evaluated on
> (retrieval vs generation as separable failure modes, plus the abilities beyond
> them), distinguish **reference-based vs reference-free** and **offline vs
> online** evaluation, attribute an end-to-end failure to the right pipeline
> stage (and explain the *retrieval recall ceiling*), and design a fair
> comparison using a baseline and one-component **ablation**.

## Prerequisites

- [Lesson 05 — A Minimal End-to-End RAG](../05-minimal-end-to-end-rag/README.md)

## Why this matters

In Lesson 05 we built a RAG system that runs end to end and prints an answer. It
*works* in the sense that it does not crash. But "it produced an answer" is not
"it produced a good answer," and "this answer looks good" is not "the system is
good." The moment you want to *improve* the thing — swap the embedding model, change
the chunk size, rewrite the prompt — you need a way to tell whether a change helped,
hurt, or did nothing. That is evaluation, and it is the spine of everything that
follows in this handbook.

Evaluating a RAG system is genuinely harder than evaluating most software, for
reasons that are structural, not a matter of effort:

- The system has **two engines** (retrieval and generation) that fail in different
  ways, but it emits **one output** — so a single bad answer doesn't tell you which
  engine to fix.
- There is often **no single correct answer** to compare against. "How do I cancel
  my plan?" has many acceptable phrasings; a gold-answer key that classical software
  tests rely on may not exist.
- The generator is **stochastic** (Lesson 01): the same input can yield different
  outputs, so a metric measured once is a sample, not a fixed truth.

This lesson is the pivot from *building* to *measuring*. It does **not** teach any
specific metric — precision@k, faithfulness, nDCG, RAGAS, and the rest come in later
lessons. Its job is to give you the *shape of the problem*: the targets, the failure
attribution, the kinds of evaluation, and the design discipline. Get that shape
right and every later metric slots into a place you already understand.

## The concept

We build up six ideas, each answering one question you must settle before you can
trust any number:

1. **What** are we even measuring? (two engines, two failure modes)
2. **Which** engine failed when the answer is wrong? (attribution + the recall ceiling)
3. **Against what** do we compare? (reference-based vs reference-free)
4. **When** do we measure? (offline vs online)
5. What **counts** as good beyond "the answer is right"? (abstention, robustness)
6. **How** do we run a comparison we can trust? (baselines + ablation)

### 1. Two engines, two failure modes — the evaluation *targets*

A RAG pipeline is, at heart, a retriever feeding a generator. Those are two
different machines doing two different jobs, and **each can fail on its own**. The
RAGAS paper (Es et al., EACL 2024) opens by naming exactly this difficulty:

> "RAG systems are composed of a retrieval and an LLM based generation module …
> Evaluating RAG architectures is, however, challenging because there are several
> dimensions to consider: the ability of the retrieval system to identify relevant
> and focused context passages, the ability of the LLM to exploit such passages in
> a faithful way, or the quality of the generation itself." [1]

Read that as **two targets**:

- **Retrieval quality** — did the *retrieve* stage surface the right passages? (Did
  it find the chunk that actually answers the question, and not bury it under
  irrelevant ones?)
- **Generation quality** — given whatever was retrieved, did the *generate* stage
  produce a good answer? (Is the answer grounded in that context? Does it actually
  address the question?)

The Eval-of-RAG survey (Yu et al., 2024) makes the same split formal. It proposes a
framework whose table of evaluation targets, in its words, "distinguishes between
the core areas of **Retrieval and Generation** considered in the evaluation" [2],
and it lists the relationships each side is scored on — retrieval against the query,
generation against the query, against the retrieved documents (faithfulness), and
against a gold answer (correctness).

> **Source scope, flagged.** The survey's taxonomy is one proposed framework, not a
> settled industry standard — it is a non-peer-reviewed preprint (rated *medium* in
> our registry). We borrow its retrieval-vs-generation split because it is clean and
> widely echoed, not because it is canonical. The RAGAS paper [1] frames the same
> idea as "several dimensions" rather than a formal two-target taxonomy.

Why does this separation matter so much? Because **the two failures need different
fixes and different metrics.** A retrieval failure is fixed by changing the index,
the embedding model, the chunking, the query. A generation failure is fixed by
changing the prompt or the generator. If you only ever look at the final answer, you
cannot tell which lever to pull. Almost every metric you will meet later is anchored
to one of these two targets — that is the organizing principle of the whole
evaluation half of this handbook.

### 2. The attribution problem and the *recall ceiling*

Here is the trap that makes RAG evaluation hard. The system gives you **one string**
— the final answer. When that string is wrong, *which engine broke?* This is the
**error-attribution problem**, and you cannot solve it by staring at the answer
alone. Consider a wrong answer; at least two very different stories produce it:

- **Retrieval failed.** The passage that answers the question was never retrieved.
  The generator did its best with irrelevant context and either refused or made
  something up. Fixing the *prompt* here would change nothing.
- **Generation failed.** The right passage *was* retrieved and sat in the prompt,
  but the generator ignored it, misread it, or added an unsupported claim. Fixing
  the *retriever* here would change nothing.

Same symptom, opposite cures. The only way to tell them apart is to inspect the two
stages separately — look at *what was retrieved* before judging *what was generated*.
This is why the field measures the two targets with separate instruments instead of
one end-to-end score.

There is a sharp asymmetry between the two engines that you must internalize early.
Generation runs **on top of** retrieval: the generator can only use what the
retriever put in front of it. So **generation quality is capped by retrieval
quality** — if the answer-bearing passage was never retrieved, no amount of prompt
engineering or model upgrading can produce a faithful answer, because the
information simply isn't there to ground on. Call this the **retrieval recall
ceiling**: retrieval sets an upper bound that generation cannot exceed.

> **Honesty flag — this framing is a synthesis, not a quotation.** No single source
> states a "retrieval recall ceiling" in those words. We are inferring it from two
> verified facts: the Eval-of-RAG survey calls for metrics that capture the
> "**interplay between retrieval accuracy and generative quality**" [2] (generation
> is judged *relative to* what was retrieved), and the RGB benchmark (§5 below)
> constructs cases where the answer is absent from every retrieved document and the
> only correct behavior is to refuse [3]. The ceiling is the logical consequence of
> those, not a theorem any of them prints.

The practical upshot: **measure retrieval first.** If retrieval recall is poor, your
generation numbers are reporting on a problem you can't fix downstream. Improving the
generator while the retriever is starving it is effort spent below the ceiling.

### 3. Against what do we compare? — reference-based vs reference-free

To say an answer is "good," you need a notion of *good* to compare against. There
are two broad stances.

- **Reference-based** evaluation compares the system's output to a **gold answer** (a
  "reference" or "ground truth") written by a human. This is the classic setup: you
  have a test set of `(question, correct answer)` pairs and you score how close the
  system's answer is to the correct one. It is rigorous — but it requires someone to
  *write and maintain* those correct answers, which is slow, expensive, and itself
  subjective when many phrasings are acceptable.
- **Reference-free** evaluation scores an output **without** a pre-written gold
  answer, judging properties you can check against the inputs themselves — e.g. "is
  this answer grounded in the retrieved context?" needs only the answer and the
  context, not a human-authored ideal answer. The RAGAS paper is explicitly built on
  this stance:

  > "We introduce RAGAs … a framework for **reference-free evaluation** of Retrieval
  > Augmented Generation (RAG) pipelines … a suite of metrics which can be used to
  > evaluate these different dimensions **without having to rely on ground truth
  > human annotations**." [1]

Neither stance is universally better. Reference-based answers the question "is the
answer *correct*?" — which reference-free metrics like faithfulness *cannot*, because
an answer can be perfectly grounded in a retrieved passage that is itself wrong or
off-topic. Reference-free answers "is the answer *grounded / relevant*?" cheaply and
at scale, with no annotation budget. Mature evaluation uses both.

> **Scope, flagged.** "Reference-free" in the RAGAS *paper* describes its original
> three metrics — faithfulness, answer relevance, context relevance [1]. The RAGAS
> *library* (which this repo pins at `0.4.3`) also ships reference-*based* metrics
> that do need a gold answer. So "RAGAS is reference-free" is true of the original
> metric idea, **not** of the whole toolkit — a distinction we'll make concrete when
> we actually use the library later.

### 4. When do we measure? — offline vs online

The two questions "is it good *before* I ship it?" and "is it good *for real users
once shipped*?" are answered by two different kinds of evaluation. This distinction
predates RAG; it comes from decades of information-retrieval practice. Hofmann, Li &
Radlinski's monograph on online IR evaluation draws the line:

> "Online evaluation … involves fielding the information retrieval system to **real
> users, and observing these users' interactions in-situ** … online evaluation
> **complements the common alternative offline evaluation approaches** which may
> provide more easily interpretable outcomes, yet are often less realistic when
> measuring … quality and actual user experience." [4]

So:

- **Offline** evaluation runs the system against a **fixed, held-out test set** with
  known relevance/answers, before (and independent of) deployment. It is repeatable,
  cheap to re-run, and lets you compare two versions on identical inputs — but it is
  only as realistic as the test set, and it cannot see real user behavior.
- **Online** evaluation measures the system **with live users**, from their actual
  interactions (clicks, follow-ups, thumbs-up, task completion). It is the realistic
  signal — but it is slow, only available after you ship, and confounded by
  everything else in the user's world. Hofmann et al. frame online evaluation around
  **controlled experiments** that give either "**absolute or relative quality
  assessments**" [4] — in everyday practice these are run as **A/B tests**
  (two versions to two user groups) and **interleaving** (results from two systems
  mixed into one list).

> **Honesty flags.** (a) The terms "A/B testing" and "interleaving" are standard IR
> practice and map onto Hofmann's "absolute / relative" experiment designs, but they
> are *not* a verbatim quote from the (paywalled) body — only "controlled
> experiments / absolute or relative quality assessments" is quoted directly [4].
> (b) This monograph is about information retrieval **in general** and predates RAG;
> the offline/online distinction transfers cleanly to RAG, but Hofmann et al. did not
> write about RAG specifically.

For most of this handbook we work **offline** (it's what you can do on day one, with
a test set and no users). Online evaluation and observability return as their own
topic late in the course, once we operate a system in production.

### 5. "Good" is more than "the answer is right" — abstention and robustness

A subtle point that trips up beginners: a RAG system's job is not only to answer
correctly when it can, but also to **behave well when it can't or shouldn't**. These
are evaluation targets in their own right. The RGB benchmark (Chen et al., AAAI 2024)
distilled them into "**4 fundamental abilities required for RAG**, including **noise
robustness, negative rejection, information integration, and counterfactual
robustness**" [3]. Two of these are easy to forget and important to measure:

- **Negative rejection (abstention).** When the retrieved context does not contain
  the answer, the right behavior is to *refuse*, not to invent. RGB defines it
  directly: "a LLM should **reject to answer the question when the required knowledge
  is not present in any retrieved document**" [3]. A system that confidently
  hallucinates instead of saying "I don't know" is failing — even though it produced
  a fluent answer. (This is the *measurement* counterpart to the abstaining prompt we
  wrote in Lesson 05's demo: "If the context does not contain the answer, say you
  don't know." There we *asked* for it; here we ask whether it actually happens.)
- **Noise robustness.** Real retrieval returns some passages that are "**relevant to
  the question but do not contain any information of the answer**" [3]; a good
  generator extracts the useful bit and ignores the noise instead of being derailed
  by it.

The other two — **information integration** (answering questions that "require
integrating information from multiple documents" [3]) and **counterfactual
robustness** — round out the set. Counterfactual robustness is worth a caveat:

> **Flagged nuance.** Counterfactual robustness tests whether a system can "identify
> and disregard incorrect information, even when alerted about potential
> misinformation" [2]. But RGB itself notes that "retrieval-augmented generation is
> **not designed to automatically address factual errors** within a given context,
> as this contradicts the underlying assumption that the model … relies on retrieved
> documents" [3]. So this is a *stress test* of behavior that is out-of-scope by
> design, not a baseline expectation. And RGB's rejection/error-detection rates are
> measured by brittle exact-match-style checks [3] — teach the *abilities* as real
> evaluation targets, but treat the specific numbers as setup-dependent.

The lesson here: when you design an evaluation, "accuracy on answerable questions" is
necessary but not sufficient. You also have to test what the system does with
unanswerable questions and noisy context — because in production, most questions
arrive with imperfect retrieval.

### 6. How do we run a comparison we can trust? — baselines and ablation

Finally, the design discipline. You will constantly want to claim "change X improved
the system." That claim is only trustworthy if the experiment isolates X. Two ideas
make this rigorous:

- **A baseline.** A number means nothing alone; it means something *relative to a
  reference point*. Your Lesson-05 naive RAG is the baseline. Every improvement is
  measured as a delta against it (and against the previous best).
- **Ablation: change one component at a time.** To attribute a change in the score to
  a specific component, you hold everything else fixed and vary that one component.
  The "Searching for Best Practices in RAG" study (Wang et al., EMNLP 2024) is built
  exactly this way: it sets up a default pipeline and, for each module, "review[s]
  commonly used approaches and **select[s] the default and alternative methods**,"
  so as to "investigate[ ] the **contribution of each component**" [5]. That is the
  template — swap one module (say, the reranker), keep the rest constant, and the
  change in score is attributable to that module.

If you change three things at once and the score moves, you have learned nothing
about *which* of the three did it (or whether two helped and one hurt). One variable
at a time is what turns "the number went up" into "this specific change caused the
number to go up."

> **Flagged.** The Best-Practices study's specific scores (and which exact methods
> "win") are tied to *their* benchmark and setup [5]; treat the **methodology**
> (ablate one component, attribute the delta) and the **qualitative** findings (e.g.
> reranking matters) as transferable, and the precise numbers as not.

## Worked example

Let's reuse Lesson 05's help-desk RAG over the toy "Acme Cloud" support corpus, and
walk through *evaluating* one interaction rather than just producing it.

A user asks:

```
What's the maximum file size I can upload?
```

The system answers:

```
The maximum upload size is 5 GB.
```

It looks like a clean, confident answer. **Is the system good?** We cannot tell from
the answer alone — we have to do the work this lesson describes.

**Step 1 — split the target.** Two separate questions: did *retrieval* find the right
passage, and did *generation* use it well? We must inspect the retrieved context, not
just the answer.

**Step 2 — attribute.** Suppose we look at what was retrieved and find that the
support corpus actually says the limit is **2 GB**, and the chunk stating that *was*
retrieved and sat in the prompt. Then this is a **generation failure** (faithfulness):
the right context was present, and the model contradicted it — invented "5 GB."
Fixing the retriever would do nothing; the lever is the prompt/generator.

Now suppose instead that the "2 GB" chunk was **never retrieved** (retrieval surfaced
only billing passages), and the model produced "5 GB" from its own weights. Then it is
a **retrieval failure**, and it hit the **recall ceiling**: the answer-bearing passage
wasn't in the prompt, so no generator could have answered faithfully. The lever is the
index/embeddings/chunking — and, separately, the system *should have refused*
("negative rejection") instead of guessing.

> Same wrong answer — "5 GB" — but two different broken engines and two different
> fixes. That is the attribution problem made concrete, and it is exactly why we
> refuse to score RAG with one end-to-end number.

**Step 3 — choose how to score it.**

- *Reference-free*: "Is the answer grounded in the retrieved context?" In the first
  scenario, no (it contradicts the 2 GB chunk) — we catch the failure with **only**
  the answer and the context, no gold key needed.
- *Reference-based*: if our test set records the gold answer "2 GB," we can also say
  the answer is *incorrect*, which faithfulness alone wouldn't establish if the
  retrieved passage were itself wrong.

**Step 4 — offline vs online.** Everything above is **offline**: a fixed question
with a known corpus, run before deployment, repeatable. An **online** signal would be
different — e.g. after shipping, the user immediately re-asks or clicks "this didn't
help," revealing dissatisfaction we'd never see in a static test set.

**Step 5 — design the fix as an ablation.** We hypothesize the second scenario
(retrieval miss) and want to try a bigger `top-k`. We change **only** `top-k` (from 3
to 5), hold the embedding model, chunking, and prompt fixed, and re-run the *same*
offline test set. If retrieval recall goes up and the answer becomes correct, the
delta is attributable to `top-k`. If we'd also swapped the embedding model in the same
run, we couldn't say which change did it.

## Your turn

No code — this is a reasoning lesson.

1. **Attribute the failure.** A RAG answer to "what regions is the service available
   in?" lists three regions; the docs list four, and the chunk listing all four was
   in the retrieved context. Is this a retrieval or a generation failure? Name the
   target, and say which lever you'd reach for. Then describe a *different* scenario
   that produces the same wrong answer but is the *other* kind of failure.

2. **Pick the comparison basis.** You want to know (a) whether answers are grounded in
   the retrieved passages, and (b) whether answers match the officially correct
   wording. For each, say whether you'd use reference-based or reference-free
   evaluation, and why one cannot substitute for the other.

3. **Spot the ceiling.** A teammate proposes spending a week prompt-tuning the
   generator to raise answer quality. Retrieval recall on your test set is currently
   40% (the right passage is retrieved for only 40% of questions). Using the recall
   ceiling, explain what's wrong with the plan and what you'd measure/fix first.

4. **Critique an experiment.** Someone reports: "I switched to a better embedding
   model *and* increased chunk size, and the score went up 6 points — the embedding
   model is clearly better." What is the methodological flaw, and how would you redo
   the experiment to support that conclusion?

## Common pitfalls / misconceptions

- **"The answer looks right, so the system works."** One good-looking answer is a
  single stochastic sample from a two-engine system. It tells you almost nothing about
  whether retrieval reliably finds the right context, whether the model stays
  faithful, or how the system behaves on hard or unanswerable questions.

- **"One end-to-end score is enough."** A single number hides *which* engine failed.
  Retrieval and generation are separable targets with different fixes [1][2]; collapse
  them and you can't act on the result.

- **"If the answer is wrong, fix the prompt."** Often the prompt is innocent: the
  answer-bearing passage was never retrieved (recall ceiling). Inspect the retrieved
  context *before* deciding the generator is at fault.

- **"Reference-free metrics tell you the answer is correct."** They don't. Faithfulness
  says "grounded in the retrieved context," which can be high even when the answer is
  wrong (because the retrieved passage was wrong or off-topic). Correctness needs a
  reference [1].

- **"A good RAG system always answers."** No — sometimes the right behavior is to
  **refuse**. Negative rejection / abstention is its own evaluation target [3]; a
  system that hallucinates rather than saying "I don't know" is failing even when it
  sounds confident.

- **"Offline wins prove production wins."** Offline scores are measured on a static
  test set; real users behave in ways a test set can't capture [4]. Offline gates a
  change; online confirms it.

## Check your understanding

1. A RAG system returns a fluent but factually wrong answer. List the **two**
   structurally different causes, and describe the *one thing you must look at* to
   tell them apart. Why can't you decide from the answer text alone?

2. Explain the **retrieval recall ceiling** in your own words, and use it to argue why
   "measure and fix retrieval before tuning the generator" is usually the right order.
   (Flag honestly: is "recall ceiling" a direct quote from a source, or a synthesis?)

3. Give one evaluation question that **reference-free** evaluation can answer but
   **reference-based** cannot, and one that reference-based can answer but
   reference-free cannot. Why does mature evaluation usually need both?

4. Your colleague says "our RAG never says 'I don't know,' so it's very capable." Using
   the idea of negative rejection, explain why that might be a *weakness*, not a
   strength — and name the situation where refusing is the correct behavior.

5. Why does changing only one component per experiment matter? Give a concrete example
   where changing two at once would leave you unable to attribute the result.

## Summary & next

Evaluating RAG is hard for structural reasons, and this lesson gave you the map. A RAG
system has **two evaluation targets** — retrieval quality and generation quality — that
fail independently and need different fixes [1][2]; because the system emits one
output, you face an **attribution problem**, and because generation rides on top of
retrieval, generation quality is capped by the **retrieval recall ceiling** (a
synthesis, not a quote). You compare outputs either **reference-based** (against a gold
answer — needed for correctness) or **reference-free** (against the inputs themselves,
e.g. grounding — cheap, no annotation) [1]; you measure **offline** (fixed test set,
before deploy) or **online** (live users, after deploy) [4]. "Good" extends past
correctness to **abstention/negative rejection** and **robustness** to noise [3]. And to
trust any "X improved Y" claim, you need a **baseline** and **one-component ablation** [5].

Notice we taught *no metric* — only the shape of the problem. That was deliberate: the
metrics that come next (retrieval metrics, faithfulness, LLM-as-judge, RAGAS) each
attach to one of the targets, stances, and design ideas established here.

Next we leave the evaluation overview and start **building the retrieval engine for
real** — ingestion (loading, cleaning, chunking, enrichment) and then retrieval proper —
before circling back to *measure* retrieval with the metrics this lesson set up. The
build → measure → improve loop begins in earnest.

## Sources

- [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/)
  ([arXiv:2309.15217](https://arxiv.org/abs/2309.15217)) — Es, James, Espinosa-Anke,
  Schockaert, EACL 2024 (Demos). **[1]** RAG as a retrieval + generation system with
  "several dimensions" to evaluate; the three reference-free metric dimensions
  (faithfulness / answer relevance / context relevance); "reference-free evaluation …
  without … ground truth human annotations." *(Demo paper; "reference-free" describes
  the original three metrics, not the entire current RAGAS library.)*
- [Evaluation of Retrieval-Augmented Generation: A Survey](https://arxiv.org/abs/2405.07437)
  — Yu, Gan, Zhang, et al., arXiv:2405.07437, 2024. **[2]** The retrieval-vs-generation
  evaluation-target split ("distinguishes between the core areas of Retrieval and
  Generation"); the call for metrics capturing "the interplay between retrieval accuracy
  and generative quality" (the basis for the recall-ceiling synthesis); the
  counterfactual-robustness one-line definition. *(Non-peer-reviewed preprint — rated
  medium; its RGAR taxonomy is one proposed framework, not a standard.)*
- [Benchmarking Large Language Models in Retrieval-Augmented Generation (RGB)](https://arxiv.org/abs/2309.01431)
  — Chen, Lin, Han, Sun, AAAI 2024. **[3]** The four RAG abilities (noise robustness,
  negative rejection, information integration, counterfactual robustness); the
  definition of negative rejection (refuse when the answer is in no retrieved document)
  and the empirical grounding for the recall ceiling; the caveat that RAG is "not
  designed to automatically address factual errors." *(Rejection/error-detection rates
  are setup-specific — teach the abilities, flag the numbers.)*
- [Online Evaluation for Information Retrieval](https://doi.org/10.1561/9781680831627)
  — Hofmann, Li, Radlinski, Foundations and Trends in IR, 2016. **[4]** The offline vs
  online distinction — online = real users observed in-situ, complementing offline
  test-collection evaluation; online eval as controlled experiments giving "absolute or
  relative quality assessments." *(Abstract verified; publisher body paywalled. "A/B
  testing / interleaving" is general IR practice mapped onto the absolute/relative
  designs, not a verbatim quote; the monograph is about IR in general, predating RAG.)*
- [Searching for Best Practices in Retrieval-Augmented Generation](https://arxiv.org/abs/2407.01219)
  — Wang, Wang, et al. (Fudan), EMNLP 2024. **[5]** The ablation methodology — a default
  pipeline with one component varied at a time to "investigate the contribution of each
  component." *(Its specific scores/winners are benchmark-specific; the one-variable
  methodology and qualitative findings transfer, the numbers don't.)*
