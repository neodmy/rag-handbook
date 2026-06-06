# Lesson 02 — Embeddings and Search

**Type:** theory

> After this lesson you can explain how text is turned into **vectors** so that
> *meaning* can be compared and searched: what an embedding is, how vector
> similarity (cosine) measures closeness, how **semantic** search differs from
> **keyword** search and when each wins, and the distinction between
> **parametric** knowledge (baked into model weights) and **non-parametric**
> knowledge (looked up at query time) — the idea RAG is built on.

## Prerequisites

- [Lesson 01 — LLMs, Tokens, and Prompting](../01-llms-tokens-and-prompting/README.md)

## Why this matters

Lesson 01 left us with an LLM as a black box: a next-token predictor whose only
input is the text in its **prompt**, and whose knowledge is whatever got baked
into its weights during training. That raises the question this whole handbook
answers: *how do we get the right text into that prompt?* For a corpus of
thousands of documents that will never fit in the context window, we cannot paste
it all in — we have to **find** the relevant pieces first.

"Find the relevant pieces" is a search problem, and the central difficulty is that
**the user's words and the document's words rarely match exactly.** A question
about "how do I cancel my plan" should find a passage titled "terminating your
subscription" — even though they share almost no words. Classic keyword search
struggles with that; **embeddings** are the tool that lets a machine compare text
by *meaning* instead of by surface words.

Two ideas from this lesson will recur for the rest of the handbook:

- **Text becomes a vector (an *embedding*), and closeness in that vector space
  approximates closeness in meaning.** This is the mechanism behind the "retrieval"
  in retrieval-augmented generation.
- **Knowledge lives in two places: inside the model (*parametric*) and outside it,
  fetched on demand (*non-parametric*).** RAG is precisely the move of putting
  knowledge in the second place so it can be updated, audited, and grounded.

This is still a black-box, build-and-evaluate depth: we need to reason about *what*
an embedding gives us and *how* similarity is measured, not how an embedding model
is trained.

## The concept

We build up three ideas, concrete before abstract: (1) embeddings and vector
similarity, (2) semantic search versus keyword search, and (3) parametric versus
non-parametric knowledge.

### 1. Embeddings and vector similarity

An **embedding** is a list of numbers — a **vector** — that represents a piece of
text as a point in a high-dimensional space. The defining property is that **text
with similar meaning is placed close together** in that space, and dissimilar text
far apart.

The length of that list is the embedding's **dimensionality**: each number is a
coordinate along one axis of the space, so a 3-number vector is a point in 3-D space
(which we can picture), and a 1,536-number vector is a point in 1,536-dimensional
space (which we cannot picture, but the arithmetic works identically). Real
embedding models output **hundreds to thousands** of dimensions — that high
dimensionality is what gives the space enough "room" to separate fine-grained
differences in meaning. We can't visualize it, but every operation below (distance,
angle, similarity) is defined by formulas that don't care how many dimensions there
are.

The intuition goes back to word vectors. Mikolov et al. (2013), introducing
word2vec, built representations "with the expectation that not only will similar
words tend to be close to each other, but that words can have multiple degrees of
similarity" [1]. The striking demonstration that these vectors capture *meaning*
(not just co-occurrence) is the analogy result from the companion paper: the
relationships between words show up as consistent **vector offsets**, so that
`vector("King") − vector("Man") + vector("Woman")` lands very close to
`vector("Queen")` [2]. Meaning had become arithmetic.

> Modern RAG systems embed whole sentences, chunks, or passages, not single words.
> The leap from word vectors to good *sentence* vectors is what Reimers & Gurevych
> (2019) addressed with Sentence-BERT: a way "to derive semantically meaningful
> sentence embeddings that can be compared using cosine-similarity" [3]. We will
> use sentence/passage embeddings throughout; word2vec is here for the intuition.

**How do we measure "close"?** The standard answer comes from classical
information retrieval. In the **vector space model**, "the representation of a set
of documents as vectors in a common vector space … is fundamental to a host of
information retrieval operations," with "one axis for each term" [4]. To compare
two vectors we use the **cosine similarity** — the cosine of the angle between
them [4]:

```
cosine(A, B) = (A · B) / (‖A‖ · ‖B‖)
```

Cosine ranges from `1` (same direction → maximally similar) through `0`
(perpendicular → unrelated) to `−1` (opposite). Crucially, it compares **direction,
not magnitude**: a long document and a short one about the same topic still score
as similar, because normalizing by the vector lengths (`‖A‖`, `‖B‖`) cancels out
length differences [4]. That is exactly the property we want — relevance shouldn't
depend on how *long* a passage is.

So the retrieval primitive is: embed the query into a vector, embed every document
(chunk) into a vector, and rank documents by cosine similarity to the query. The
"meaning search" we wanted reduces to "find the nearest vectors."

### 2. Semantic search versus keyword search

There are two fundamentally different ways to decide whether a document matches a
query, and a RAG engineer must understand both because they fail in *opposite*
ways.

**Keyword (lexical) search** matches on the **words themselves**. The classic
methods — TF-IDF and Okapi BM25 — score a document by how often the query's terms
appear in it (weighted so that rare terms count more and long documents don't win
by sheer length); they are "the de facto method" for sparse retrieval [5]. This is
fast, transparent, and unbeatable when the query and document genuinely share
terms (names, error codes, exact phrases).

Its weakness is **synonymy**: "In most collections, the same concept may be
referred to using different words. This issue, known as synonymy, has an impact on
the recall of most information retrieval systems" [4]. A search for *aircraft*
will not match a passage that only says *plane* [4]. The query "cancel my plan"
shares no content words with "terminate your subscription," so a pure keyword
system scores them near zero — a miss, even though they mean the same thing. (This
mismatch is often called the *vocabulary mismatch* problem; note that the textbook's
own term for the underlying cause is *synonymy* [4] — "vocabulary mismatch" is
common community phrasing, not IIR's wording.)

**Semantic (dense) search** matches on **meaning**, using the embeddings from §1:
embed the query and the documents, rank by cosine similarity. Because synonyms land
near each other in vector space, "cancel my plan" and "terminate your subscription"
are close *even with no shared words*. Karpukhin et al. (2020) showed this is not
just theory: implementing retrieval "using dense representations alone," their dense
retriever "outperforms a strong Lucene-BM25 system greatly by 9%-19% absolute in
terms of top-20 passage retrieval accuracy" [6].

But dense search has the *opposite* failure mode: it can **miss exact matches**. A
specific part number like `A1-2231-X`, a surname, or a rare technical token may not
be well represented in the embedding space, and semantic search can rank a
"topically similar" passage above the one containing the literal string the user
needs. Keyword search would nail that case.

> The practical upshot — which we will build later — is that production systems
> often combine the two (**hybrid retrieval**), getting lexical precision *and*
> semantic recall. For now the durable idea is the trade-off: **keyword search
> matches words and misses synonyms; semantic search matches meaning and can miss
> exact tokens.** Neither is universally "better."

### 3. Parametric versus non-parametric knowledge

We can now name the distinction that motivates RAG itself. An LLM trained on a
large corpus stores what it "knows" **in its weights** — its parameters. Lewis et
al. (2020), the paper that named RAG, call this the model acting "as a
parameterized implicit knowledge base" — **parametric memory** [7]. Lesson 01's
black box is exactly this: ask it a question and it generates an answer from
knowledge frozen into its parameters at training time.

Parametric knowledge has hard limits, and they are the reason RAG exists:

- It is **frozen** at training cutoff — it cannot know anything newer.
- It is **not updatable** without retraining or fine-tuning the weights.
- It is **opaque** — there is no source to cite or audit; the model cannot show you
  *where* a fact came from.
- It can be **wrong with confidence** (it will happily generate a plausible-sounding
  but false answer — a hallucination, studied later).

The alternative is to keep knowledge **outside** the model, in a searchable store,
and fetch the relevant pieces at query time. Lewis et al. build their RAG models so
that, alongside the parametric seq2seq generator, "the non-parametric memory is a
dense vector index of Wikipedia, accessed with a pre-trained neural retriever" [7].
That dense vector index is precisely the embeddings-plus-similarity machinery of §1
and §2.

This is the whole shape of RAG, in one sentence: **combine a parametric model (good
at language and reasoning) with a non-parametric store (current, updatable,
auditable knowledge), by embedding a query, retrieving the nearest passages, and
putting them in the prompt.** Non-parametric knowledge can be updated by editing the
store (no retraining), is auditable (you know which passage was retrieved), and can
be cited. Every later lesson is, in some sense, about doing each step of that
sentence well.

## Worked example

Let's make "similarity is direction, not word overlap" concrete with real
arithmetic. We will compare one query against two candidate passages.

```
Query  Q:  "how do I cancel my plan"
Doc    A:  "steps to terminate your subscription"
Doc    B:  "our company picnic is planned for July"
```

A human sees instantly that **A** is the right answer: it means the same thing.
But notice the trap — **B** shares the word *plan*/*planned* with the query, while
**A** shares *no content words at all*. Watch how the two search methods react.

### Keyword search

A lexical method scores by shared terms. Stripping stopwords, the query's content
words are `{cancel, plan}`.

- **Doc A** (`{steps, terminate, subscription}`): shares **zero** content words →
  score ≈ 0. *Missed*, despite being the correct answer — this is the synonymy
  problem [4].
- **Doc B** (`{company, picnic, planned, July}`): shares `plan`/`planned` → a
  small **positive** score. The wrong document outranks the right one.

Keyword search is fooled by surface words.

### Semantic search

Now embed each text into a vector. The embeddings are illustrative 3-dimensional
toy vectors (recall that real models use hundreds to thousands of dimensions; we
use three only so the arithmetic is visible) — chosen so that
*cancel/terminate/subscription* ideas point one way and *event/scheduling* ideas
point another:

| text | vector |
|------|--------|
| Q (cancel my plan)            | `[0.9, 0.8, 0.1]` |
| A (terminate subscription)    | `[0.8, 0.9, 0.0]` |
| B (picnic is planned)         | `[0.1, 0.2, 0.9]` |

Compute cosine similarity, `cos(Q, D) = (Q · D) / (‖Q‖ ‖D‖)` [4]. With
`‖Q‖ = √(0.81 + 0.64 + 0.01) = √1.46 ≈ 1.208`:

**Q vs A:**
- dot product `Q · A = (0.9)(0.8) + (0.8)(0.9) + (0.1)(0.0) = 0.72 + 0.72 + 0 = 1.44`
- `‖A‖ = √(0.64 + 0.81 + 0.0) = √1.45 ≈ 1.204`
- `cos(Q, A) = 1.44 / (1.208 × 1.204) ≈ 1.44 / 1.454 ≈ **0.990**`

**Q vs B:**
- dot product `Q · B = (0.9)(0.1) + (0.8)(0.2) + (0.1)(0.9) = 0.09 + 0.16 + 0.09 = 0.34`
- `‖B‖ = √(0.01 + 0.04 + 0.81) = √0.86 ≈ 0.927`
- `cos(Q, B) = 0.34 / (1.208 × 0.927) ≈ 0.34 / 1.120 ≈ **0.304**`

Semantic search ranks **A (0.990) far above B (0.304)** — the exact opposite of the
keyword verdict, and the *correct* one. The shared word *plan* didn't help B,
because direction in meaning-space, not word overlap, drove the score. This is why
dense retrieval beats lexical retrieval on synonym-heavy queries [6].

### The honest counter-case

Now imagine the query were `"error code A1-2231-X"`. That exact token is rare; an
embedding may place it vaguely, and semantic search could rank a passage about
"common error codes" above the one document that literally contains `A1-2231-X`.
Here **keyword search wins** — it matches the literal string. That is the §2
trade-off in one example, and the reason real systems often run both.

## Your turn

No code yet — this is a reasoning exercise.

1. **Predict the failure.** You have a FAQ where one entry is titled "Resetting a
   forgotten password." A user searches "I can't log in, what do I do." Which
   retrieval method (keyword or semantic) is more likely to surface that entry, and
   why? Now the user searches for the literal error string `ERR_AUTH_017` that
   appears verbatim in a different entry — which method wins *that* one?

2. **Reason about cosine.** Two passages about the same topic, one a single
   sentence and one three paragraphs long, are embedded. Why does cosine similarity
   let them still score as similar, where a raw "vector difference" measure might
   not? (Tie your answer to "direction, not magnitude.")

3. **Locate the knowledge.** Your LLM was trained with a cutoff before your
   company's latest product launched. A user asks about that new product. Explain,
   in terms of parametric vs non-parametric knowledge, why fine-tuning is *one* fix
   but RAG is the more practical one — and what RAG would do at query time instead.

## Common pitfalls / misconceptions

- **"An embedding stores the words / lets you reconstruct the text."** No — it is a
  fixed-length vector of numbers positioning the text *by meaning* in a space; you
  generally cannot read the original text back out of it. What it preserves is
  *relative* similarity: nearby = similar meaning [1].

- **"Semantic search is just better, so keyword search is obsolete."** They fail in
  opposite ways. Dense search beats lexical on synonyms [6] but can miss exact
  tokens (codes, names, rare strings) that keyword search nails [4]. Production
  systems frequently combine them.

- **"The word2vec king/queen analogy comes from the word2vec paper."** The analogy
  and the vector-offset method are from the companion paper, *Linguistic
  Regularities* [2]; the better-known word2vec paper [1] only restates that result
  (citing it). Worth getting right when you cite it.

- **"More shared words = more relevant."** That is the *keyword* assumption, and the
  worked example shows it failing: a shared word (*plan*) ranked the wrong document
  first, while the right answer shared no words at all [4].

- **"The model already knows everything, so why retrieve?"** Parametric knowledge is
  frozen at training cutoff, not updatable without retraining, and not auditable [7].
  Non-parametric retrieval is how we add current, citable, editable knowledge.

## Check your understanding

1. A query and a relevant document share **no** words, yet a semantic search ranks
   the document highly. Explain the mechanism that makes this possible. Then
   describe a query where this same mechanism would *hurt* you relative to keyword
   search.

2. Cosine similarity divides the dot product by the product of the vector lengths.
   What real-world problem would you get if you ranked documents by raw dot product
   (or by raw distance) *without* that normalization? (Hint: think about a very long
   document.)

3. Define parametric and non-parametric knowledge in one sentence each, and name two
   concrete advantages non-parametric (retrieved) knowledge has over parametric
   knowledge for a question about last week's news.

4. Your team measures that semantic retrieval misses queries containing exact
   product SKUs but does well on natural-language questions. Using only the concepts
   in this lesson, what change to the *retrieval method* would you propose, and why?

## Summary & next

We added the other half of the foundation. Text becomes an **embedding** — a vector
whose **direction encodes meaning**, compared with **cosine similarity** [1][3][4].
That gives **semantic search**, which matches meaning and beats keyword search on
synonyms [6] but can miss exact tokens where lexical matching still wins [4]. And we
named the distinction RAG is built on: **parametric** knowledge frozen in the
model's weights versus **non-parametric** knowledge fetched at query time from a
dense vector index [7] — updatable, auditable, citable.

Next (lesson 03, *Why RAG and what it is*) we assemble these pieces into the full
**index → retrieve → augment → generate** pipeline: how a non-parametric store and
a parametric generator combine into a working retrieval-augmented system, and the
naive/advanced/modular paradigms for organizing it.

## Sources

- [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781)
  — Mikolov, Chen, Corrado, Dean, ICLR 2013 (workshop). **[1]** Embedding intuition:
  text as vectors, "similar words tend to be close to each other."
- [Linguistic Regularities in Continuous Space Word Representations](https://aclanthology.org/N13-1090/)
  — Mikolov, Yih, Zweig, NAACL-HLT 2013. **[2]** The `King − Man + Woman ≈ Queen`
  analogy and the vector-offset method.
- [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://aclanthology.org/D19-1410/)
  — Reimers, Gurevych, EMNLP-IJCNLP 2019. **[3]** Semantically meaningful *sentence*
  embeddings "that can be compared using cosine-similarity."
- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/)
  — Manning, Raghavan, Schütze, Cambridge University Press, 2008. **[4]** The vector
  space model and cosine similarity (Ch. 6); synonymy / term mismatch (Ch. 9).
- [The Probabilistic Relevance Framework: BM25 and Beyond](https://doi.org/10.1561/1500000019)
  — Robertson, Zaragoza, FnT IR, 2009. **[5]** Okapi BM25, the standard lexical
  ranking function. *(Primary paywalled; confirmed via Crossref DOI.)*
- [Dense Passage Retrieval for Open-Domain Question Answering](https://aclanthology.org/2020.emnlp-main.550/)
  — Karpukhin, Oguz, Min, Lewis, et al., EMNLP 2020. **[6]** Dense retrieval beats
  BM25 by 9–19% top-20 accuracy; semantic matching where lexical fails.
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
  — Lewis, Perez, Piktus, Petroni, et al., NeurIPS 2020. **[7]** Parametric memory
  (the seq2seq model) vs non-parametric memory (a dense vector index).
