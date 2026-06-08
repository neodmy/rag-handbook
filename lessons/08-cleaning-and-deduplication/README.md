# Lesson 08 — Cleaning and Deduplication

**Type:** theory+practice

> After this lesson you can explain why parsed text is still not index-ready, tell
> **normalization**, **cleaning**, and **deduplication** apart and say why they run in
> that order, distinguish **exact** from **near-duplicate** removal (and why exact
> hashing silently misses near-duplicates), and run a demo that detects near-duplicates
> with shingling + Jaccard similarity and shows them crowding a retriever's top-k.

## Prerequisites

- [Lesson 07 — Document Loading and Parsing](../07-document-loading-and-parsing/README.md)

(Lesson 07 is the only hard prerequisite. This lesson assumes you have parsed text out
of files and met ingestion's defining hazard — it fails *silently*. It also reuses two
ideas already introduced earlier on the baseline: that retrieval returns a **top-k** set
of chunks, and that a document file arrives wrapped in **boilerplate**. We do not assume
chunking yet — that is the next lesson.)

## Why this matters

Lesson 07 got *structure* out of a file: the right characters, in the right reading order,
with tables kept as grids. That is necessary, but it is not enough to index. The text a
good parser hands you is still, almost always, **dirty in three specific ways**, and each
one quietly degrades retrieval:

1. **It carries boilerplate.** A crawled help-center page is mostly *not* the help article —
   it is the nav bar, the breadcrumb, the cookie banner, the "Was this helpful? Yes / No"
   footer, the copyright line. Lesson 07 already noted that HTML "has structure, but it is
   buried in boilerplate." Parsing recovers the text; it does not decide which of it is
   *content*.
2. **Its characters are inconsistent.** The same word can arrive encoded several ways — a
   curly `'` vs a straight `'`, a non-breaking space vs a normal one, the `ﬁ` ligature vs
   the two letters `fi`, the accented `é` as one code point or as `e` + a combining accent.
   To a human these look identical; to a byte-comparing computer they are *different
   strings*, and that difference breaks both exact-duplicate detection and exact-match
   retrieval.
3. **It is full of duplicates.** Real corpora ingest the same document twice (two URLs, a
   PDF and its HTML version), and they accumulate near-identical revisions (policy v1, v2,
   v3). Left in, duplicates **crowd the top-k**: if three of your `k` retrieved chunks are
   the same answer, the model sees one idea three times and two genuinely different
   documents never make it into the context.

This lesson is the second stop in **Part II: Ingestion**, and it is the cleanup crew for
what parsing leaves behind. The slogan is still **garbage in, garbage retrieved** — here
the garbage is boilerplate, encoding noise, and redundancy.

## The concept

Three jobs, run in order — normalize, then clean, then deduplicate — followed by the one
that needs the most care: telling *near*-duplicates from exact ones.

### Normalization, cleaning, and deduplication are three different jobs

It is worth separating them precisely, because they are easy to conflate and they must run
in a particular order:

- **Normalization** makes *equivalent characters identical*. It does not delete anything;
  it rewrites characters into a canonical form so that strings a human would call "the same"
  really are the same bytes.
- **Cleaning** *removes text that is not content* — boilerplate (nav/footers/banners) and
  noise (runs of whitespace, stray markup) — and is lossy on purpose.
- **Deduplication** *removes whole documents (or chunks)* that duplicate others.

The order matters: **normalize first, then clean, then dedup.** Deduplication compares text,
and two copies of the same article will *not* compare equal if one uses curly quotes and the
other straight ones, or if one is still wrapped in a different footer. Normalize and clean
first, and the comparison becomes meaningful. (This ordering is an engineering convention,
demonstrated in the code below, not a law from a paper.)

### Normalization: the same word must become the same bytes

Unicode often offers several encodings for what is visually one string. The authority here
is **Unicode Standard Annex #15**, which defines normalization forms precisely so that
"equivalent strings have a unique binary representation" [3]. It distinguishes two kinds of
equivalence:

- **Canonical** equivalence — truly the same character, e.g. `é` written as the single code
  point U+00E9 vs as `e` (U+0065) + a combining acute accent (U+0301). Forms **NFC** /
  **NFD** reconcile these (compose to one code point, or decompose to base + accent) [3].
- **Compatibility** equivalence (the "K" forms, **NFKC** / **NFKD**) — characters that are
  *formatting variants*: the `ﬁ` ligature folds to `fi`, a non-breaking space folds to a
  normal space, full-width characters fold to ASCII [3].

One step comes *before* any of this: the text must already be decoded into a consistent
Unicode encoding. Transcoding everything to **UTF-8** is the near-universal first move — it
is lossless (UTF-8 can represent every Unicode code point) and it is the precondition for
comparison and normalization [5]. The real risk there is not the conversion but decoding
from the *correct source encoding*; guess wrong and you get plausible-looking corrupted text
(*mojibake*) — another silent failure.

**Which form, though — and is any form "always safe"?** This is the trap to avoid. There is
a conservative default and an aggressive one, and they are not interchangeable:

- **NFC** (canonical only) is the safe default. It reconciles characters that are *truly the
  same* (the two `é` encodings) and **preserves every meaningful distinction**. The W3C
  Character Model recommends it for content: "Content authors SHOULD use Unicode
  Normalization Form C (NFC) wherever possible" [5].
- **NFKC** (compatibility) is **lossy**. It additionally folds *formatting* variants, and some
  of those distinctions carry meaning: `¼ → 1/4`, the superscript `x² → x2` (the exponent
  collapses to the baseline!), `① → 1`, full-width CJK folding. UAX #15 warns that these
  variants "may represent a visual distinction that is significant in some textual contexts …
  greater care is required" [3]. On a corpus of math, chemistry, code, or CJK, blind NFKC
  corrupts meaning.

The demo uses **NFKC** deliberately — for *retrieval matching* you often want maximal folding
(so `¼` and `1/4`, or `ﬁ` and `fi`, match a query), the same recall-for-precision trade-off
you make when you lowercase. That is a defensible **retrieval-time** choice, *not* a universal
"always apply." When you must not lose meaning (archival storage, scientific text), prefer NFC.

**A note for non-English corpora.** Normalization matters far more once your text leaves plain
ASCII. English without accents has nothing to compose or decompose, so normalizing barely
changes it — which is why an English-only pipeline can skip it and seem fine. But Spanish,
French, German, Portuguese and most other languages are full of accented letters and `ñ`/`ü`
that can arrive **precomposed or decomposed**. For those corpora, normalizing
to **NFC** is the precaution that makes "café" match "café" in dedup and retrieval, and the W3C
recommends NFC for content for exactly this reason [5]. Use **NFC**, not NFKC, for this: accents
are *canonical* equivalence, so you fix them without NFKC's lossy compatibility folding.

There is also a sharp limit on *any* form: normalization handles only what Unicode *defines*
as equivalent. Typographic **quotes** (`"` `"` `'`) are **not** compatibility-equivalent to
straight ASCII quotes, so even NFKC leaves them untouched — those need an explicit replacement
rule. That is the cleanest illustration that **normalization and cleaning are different jobs**:
one is a standard, the other is your own rules.

### Cleaning: strip the boilerplate, keep the content

Parsing recovers the text; cleaning decides which of it to keep. For HTML the well-worn
approach is a **main-content extractor** — Lesson 07's appendix met `trafilatura`, which
"strips boilerplate (nav/ads/footers) to keep the article text" [4]. For other formats you
write rules: drop lines matching known chrome (breadcrumbs, "© …", feedback footers), then
collapse the runs of whitespace that parsing tends to leave. The demo uses a transparent
line-based rule so you can see exactly what is dropped; in production you would lean on a
content extractor for HTML. The principle is the same: **only the content should reach the
index.**

### Exact deduplication: hash the cleaned text

The cheapest duplicate to remove is the exact one — the same document ingested twice. Hash
each cleaned document (e.g. SHA-256) and keep the first of each hash. The catch you just
set up: this only works **after** normalization and cleaning. Two captures of the same
article with different boilerplate, or different quote characters, have different raw bytes
and so different hashes — they look unique until you have folded them to the same canonical,
boilerplate-free text. In the demo, document **D5** is byte-for-byte different from **D1**
(different nav crumb and footer) yet collapses onto it once cleaned.

### Near-duplicate detection: why exact hashing is not enough

Exact hashing is brittle: change a *single* character and the hash is completely different.
But real corpora are full of **near**-duplicates — a policy page revised to change one number,
an article copied with a tweaked sentence. These are not byte-identical, so exact dedup keeps
them all, and they crowd the top-k just as badly as exact copies.

The classical solution is **shingling**, from *Introduction to Information Retrieval*,
§19.6 [2]:

- A document's **k-shingles** are "the set of all consecutive sequences of *k* terms" in it
  [2] — e.g. the 3-shingles of "request a refund within 30 days" include `(request, a,
  refund)`, `(a, refund, within)`, …. Shingles capture *local word order*, not just a bag
  of words.
- Two documents are near-duplicates when their shingle sets are "nearly the same" [2],
  measured by the **Jaccard coefficient** — `|A ∩ B| / |A ∪ B|` — and compared to a
  **threshold** you choose (the demo uses 0.8). Changing one token in a long document
  removes only the few shingles that span it, so the Jaccard stays high — exactly the regime
  where exact hashing fails and shingling succeeds.

Computing Jaccard for *every pair* is `O(n²)`, hopeless at corpus scale. IIR's answer is to
estimate it from a small **sketch**: hash the shingles under ~200 random permutations and
keep the minimum of each (this is **MinHash**); the fraction of matching minima estimates the
Jaccard coefficient, and near-duplicates are then clustered with a union-find pass [2].
Production deduplicators (and the `NearDup` tool from the deduplication study below [1]) use
exactly this family of techniques; our demo computes the exact Jaccard directly because the
corpus is tiny and the point is the *mechanism*, not the scaling trick.

### Why this matters for RAG specifically

There is strong evidence that duplicates in a text corpus are harmful — but read it
carefully. Lee et al. studied deduplicating **language-model pretraining data** and found
that duplicates drive verbatim memorization ("over 1% of the unprompted output … is copied
verbatim from the training data") and contaminate train/test splits, while removing them is
cheap and lets models reach "the same or better accuracy" in fewer steps [1]. That is a
**high-quality result about training corpora, not about RAG.** Extending it to "deduplicate
your RAG ingestion corpus" is *our* engineering inference, and we flag it as such.

The RAG-specific reason is simpler and follows from the baseline you already built: retrieval
returns a fixed **top-k**. Duplicates are, by definition, similar to the same queries, so they
travel to the top together — and `k` is a budget. If two of your top-3 are the same answer,
you have spent two-thirds of the context window on one idea and locked out two documents that
might have answered the rest of the question. The demo makes this concrete and measurable.

### Putting it together: where this sits in the pipeline

Now that you have met all three jobs, here is how they fit between Lesson 07's loading/parsing
and Lesson 09's chunking:

```
  file (bytes)
     │  [Lesson 07]  LOAD / PARSE — the loader turns bytes into a str
     │               (it resolves the character encoding for you; see note)
     ▼
  text (str — but in an unknown Unicode normalization form)
     │  [Lesson 08]  1. NORMALIZE → NFC   ← right after the loader's output
     │               2. CLEAN     → strip boilerplate + collapse whitespace
     │               3. DEDUP     → exact (hash), then near (shingles + Jaccard)
     ▼
  index-ready text
     │  [Lesson 09]  CHUNK → embed → index
     ▼
```

**The loader gives you characters; the normalization form is on you.** Document loaders
(`PyPDFLoader`, `TextLoader`, …) return text already decoded to a `str` — a LangChain loader
hands back a `Document` whose `page_content` is a string [6], and `pypdf`/`pdfplumber` return
`str` directly (Lesson 07). What they do **not** do is *normalize* that string: it arrives in
whatever Unicode form the source happened to use, so applying NFC is an explicit step you add
right after the loader. It is **idempotent** — a no-op on text already in NFC — so it is safe
to apply every time. (The one place the loader may *not* save you is the decoding itself: for
plain-text files you choose the encoding when you read them, and a wrong choice yields mojibake.)

## Worked example

The runnable code is [`demo.py`](./demo.py). Run it from the repo root:

```bash
uv run python -m lessons.08-cleaning-and-deduplication.demo
```

It works on a tiny **fictional** "Acme Cloud" help-desk corpus defined in the script
(invented content, not a real product, not an evaluation dataset). The Unicode quirks are
written in deliberately. No LLM and no network are involved — only the Python standard
library — so the output is **fully reproducible**. Here is the **real output** of a run.

**Section 1 — normalization.** One messy snippet, folded:

```
1. NORMALIZATION  (Unicode NFKC + quote rules)
RAW  : 'click “Forgot\xa0password” to reconﬁgure your account'
CLEAN: 'click "Forgot password" to reconfigure your account'

NFKC folded   (NBSP -> space) and ﬁ (ﬁ ligature -> 'fi');
the smart quotes “ ” needed explicit rules — NFKC leaves them.

Why normalize before comparing — the SAME word, two encodings:
  'café' (len 4)  ==  'café' (len 5)  -> False
  after NFKC: True  (now they match — and would hash identically)
```

Read the two `café`s: visually identical, but one is 4 code points and one is 5, and `==`
says **False** — until NFKC reconciles them [3]. This is *why* normalization must run before
any byte comparison: without it, exact-duplicate detection and exact-match retrieval both
treat equivalent text as different.

**Section 2 — cleaning.** The same document before and after boilerplate removal:

```
2. CLEANING  (strip boilerplate + collapse whitespace)
RAW document 'D2-refund-v1' (note the nav crumb, rule lines, footer):

Acme Cloud Help Center  ›  Account
----------------------------------------------------
Refund policy
You can request a refund within 30 days of purchase, no questions asked. ...
----------------------------------------------------
© 2026 Acme Cloud, Inc.   Was this article helpful?  Yes / No

CLEANED — only the content survives:

Refund policy You can request a refund within 30 days of purchase, no questions asked. ...
```

The breadcrumb, the rule lines, and the feedback/copyright footer are gone; the content
remains. Index the *raw* version and a query for "refund" competes against — and a chunk may
be polluted by — "Was this article helpful? Yes / No," which is on every page and about
nothing.

**Section 3 — exact dedup.** Hash the cleaned text:

```
3. EXACT DEDUP  (hash of cleaned text)
  D1-password       kept   sha256=8277b5a939ce…
  D2-refund-v1      kept   sha256=103069a63f79…
  ...
  D5-password-dup   EXACT DUPLICATE of D1-password  (dropped)
  ...
7 documents -> 6 after exact dedup.
D5 had different boilerplate from D1 but the SAME content — caught only
because we hashed the *cleaned* text, not the raw bytes.
```

D5 and D1 are the same article wrapped in different chrome. On the **raw** bytes their hashes
differ and both survive; on the **cleaned** text they collapse. Cleaning is what made exact
dedup work.

**Section 4 — near-dup detection.** The three refund revisions differ by one number, so exact
hashing kept all of them. Shingling catches them:

```
4. NEAR-DUP DETECTION  (3-word shingles + Jaccard)
Pairwise Jaccard over 3-shingles (flagging >= 0.8):

  D2-refund-v1     D3-refund-v2     J=0.92  <-- NEAR-DUPLICATE
  D2-refund-v1     D7-refund-v3     J=0.92  <-- NEAR-DUPLICATE
  D3-refund-v2     D7-refund-v3     J=0.92  <-- NEAR-DUPLICATE

Exact hashing alone would have KEPT all 6 — they are
not byte-identical. Near-dedup drops: D3-refund-v2, D7-refund-v3
6 -> 4 after near-dedup: D1-password, D2-refund-v1, D4-cancel, D6-storage
```

A one-word edit (the day count) leaves Jaccard at **0.92** — far above threshold — because
only the handful of shingles spanning that word change [2]. Exact hashing saw three unrelated
documents; shingling sees one document in three revisions and keeps a single representative.

**Section 5 — why it matters.** The payoff, on a refund query:

```
5. WHY IT MATTERS  (duplicates crowd the top-k)
Query: 'refund to my payment method in business days'  (8 terms)

Top-3 BEFORE near-dedup — the 3 refund copies tie and fill every slot:
    6 query-terms  D2-refund-v1
    6 query-terms  D3-refund-v2
    6 query-terms  D7-refund-v3

Top-3 AFTER near-dedup — the refund answer takes ONE slot; the other
two go to the next-ranked documents (weak matches here — but no longer
wasted on duplicate copies of the same answer):
    6 query-terms  D2-refund-v1
    0 query-terms  D1-password
    0 query-terms  D4-cancel

Distinct documents in the top-3: 1 -> 3.  Same k, less redundancy.
```

Before dedup, the three near-identical refund pages tie and **fill every slot** — the user's
top-3 is one answer, repeated. After dedup, the refund answer takes a single slot and the
others fall to the next-ranked documents. (The scorer here is a simple query-term overlap
count — a *stand-in* for Lesson 05's vector retriever; crowding happens under **any**
similarity function, because duplicates are similar to the same queries by definition. The
freed slots going to weak matches in this toy corpus is incidental — the point is the wasted
redundancy is gone.)

## Your turn

Run the demo, then probe it:

1. **Break exact dedup on purpose.** In `demo.py`, comment out the `normalize(...)` call
   inside `clean()` and re-run. Watch D5 stop being detected as a duplicate of D1 — the
   different footer/quotes now produce different hashes. This is the "normalize first" rule
   failing in front of you.

2. **Find the near-dup threshold's edge.** The refund revisions sit at Jaccard 0.92. Edit one
   refund revision more heavily (change a whole sentence, not one word) and watch the Jaccard
   drop. At what edit size does it fall below 0.8 and escape detection? That number *is* the
   recall/precision trade-off of the threshold — there is no universally correct value.

3. **Change the shingle size.** Set `k=1` in `shingles()` (a bag of words) and re-run. Why do
   unrelated documents start looking more similar? Then try `k=5`. What does a larger `k`
   demand of two documents before it calls them near-duplicates?

4. **Make duplicates win the whole top-k.** Add a fourth refund revision (`_refund("14")`) to
   the corpus and re-run section 5 *before* dedup. With `k=3` you already saw all slots taken;
   reason about what a real `k=5` retrieval would return on a corpus where one popular answer
   has six near-copies.

The goal is to feel that "I cleaned the text" is, like "I extracted the text" was in Lesson
07, an under-specified claim — *which* normalization, *which* boilerplate, and *how similar*
is "duplicate"?

## Common pitfalls / misconceptions

- **"Lowercasing/trimming is all the cleaning I need."** Boilerplate is the bigger problem:
  a footer repeated on every page is high-frequency noise that pollutes chunks and competes
  in retrieval. Strip non-content first [4].

- **"Two strings that look the same are the same."** Not to a byte comparison. Curly vs
  straight quotes, NBSP vs space, ligatures, and composed vs decomposed accents are all
  *visually* identical and *bytewise* different — which silently defeats exact dedup and
  exact-match retrieval until you normalize [3].

- **"Exact hashing removes duplicates."** It removes *exact* duplicates. A one-character edit
  produces a completely different hash, so near-duplicates — the common case in revised
  corpora — sail straight through. You need shingling/Jaccard (or MinHash at scale) for those
  [2].

- **"Deduplication makes the model better — there's a paper."** The paper (Lee et al.) is
  about **LM pretraining data**, where duplicates cause memorization and test-set
  contamination [1]. The RAG benefit — not wasting the top-k on redundant chunks — is a
  related but **separate** argument from first principles, not that paper's finding. Keep the
  two distinct.

- **"Dedup is free; just delete the copies."** Deduplication is **lossy** and not always safe:
  two documents can be near-identical yet differ in the one detail that matters (the refund is
  5 vs 10 days), and which copy you keep is a real decision. Keep provenance, and set the
  threshold deliberately — too low and you delete distinct documents, too high and duplicates
  survive.

## Check your understanding

1. We insisted on the order **normalize → clean → dedup**. Using document D5 (same content as
   D1, different boilerplate, curly quotes) as your example, explain what goes wrong if you
   try to deduplicate *before* normalizing and cleaning.

2. The three refund revisions differ by a single number, yet exact hashing kept all three
   while Jaccard scored them 0.92. Explain *both* halves: why does a one-character change
   defeat hashing, and why does it barely move the shingle-based Jaccard?

3. Distinguish **normalization** from **cleaning** using the smart-quote case. Why does NFKC
   fix the `ﬁ` ligature and the non-breaking space but *not* the curly quotes, and what does
   that tell you about relying on a normalization form alone?

4. A teammate says, "Lee et al. proved deduplication improves models, so dedup will improve
   our RAG answers." What is right and what is overstated in that sentence, and what is the
   *RAG-specific* reason to deduplicate that the paper does not provide?

5. You raise the near-duplicate threshold from 0.8 to 0.95 on a corpus of frequently-revised
   policy pages. Which error do you reduce and which do you increase, and how would that show
   up in a query's top-k?

## Summary & next

Parsed text is not index-ready text. We separated three jobs and ran them in order:
**normalization** folds equivalent characters to one canonical form so comparisons are
meaningful (Unicode NFC/NFKC [3], with the limit that typographic quotes need explicit rules);
**cleaning** strips boilerplate and whitespace so only content reaches the index [4]; and
**deduplication** removes redundant documents — **exact** dedup by hashing the *cleaned* text,
and **near-duplicate** dedup by **shingling + Jaccard similarity** (MinHash sketches at scale)
[2], which catches the revised-by-one-token copies that exact hashing misses. We grounded the
*why* honestly: the strongest published evidence (Lee et al. [1]) is about LM **pretraining**
corpora, while the RAG payoff — not wasting a fixed **top-k** on redundant chunks — is a
first-principles argument we demonstrated in real output (three refund copies filling every
slot, then one).

Next, **Lesson 09 — Chunking Strategies** takes this clean, deduplicated text and decides how
to *split* it into the units you actually embed and retrieve. The typed structure from Lesson
07 and the clean content from this lesson are exactly what good chunking splits *along* —
which is why getting the text right first pays off there.

## Sources

- [Deduplicating Training Data Makes Language Models Better](https://arxiv.org/abs/2107.06499)
  — Lee, Ippolito, et al. (Google/UPenn), ACL 2022. **[1]** Evidence that text-corpus
  duplicates cause verbatim memorization and train/test contamination, and that dedup is cheap
  and non-harmful (released tools: ExactSubstr / NearDup). *Honesty flag: scoped to **LM
  pretraining data**, not RAG; the "dedup your RAG corpus" motivation is our engineering
  inference, and the top-k argument is first-principles, not the paper's finding.*
- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/), Ch. 19 §19.6
  "Near-duplicates and shingling" — Manning, Raghavan, Schütze (CUP, 2008). **[2]** *k*-shingles,
  the Jaccard coefficient of shingle sets, the similarity threshold, and sketch/permutation
  (MinHash) estimation with union-find clustering — the standard near-duplicate-detection
  method.
- [Unicode Standard Annex #15 — Unicode Normalization Forms](https://www.unicode.org/reports/tr15/)
  — The Unicode Consortium. **[3]** The authority for Unicode normalization: NFC/NFD (canonical
  equivalence) and NFKC/NFKD (compatibility equivalence), so that "equivalent strings have a
  unique binary representation." *Verified at the primary 2026-06-08.*
- [trafilatura](https://github.com/adbar/trafilatura) — A. Barbaresi, official repo/docs.
  **[4]** HTML main-content extraction (boilerplate removal) — the production approach to the
  cleaning step for web sources. *Heuristic; quality varies by page (carried over from Lesson 07).*
- [Character Model for the World Wide Web: String Matching](https://www.w3.org/TR/charmod-norm/)
  — W3C, Working Group Note (2021). **[5]** NFC as the recommended default normalization for
  content ("SHOULD use … NFC wherever possible"), transcoding to a consistent Unicode form
  (UTF-8) as the first step, and the warning that normalization can remove intentional
  distinctions. *Verified at the primary 2026-06-08.*
- [LangChain — Document loaders](https://python.langchain.com/docs/concepts/document_loaders/)
  — LangChain, official docs. **[6]** Loaders return text already decoded to a `str` — a
  `Document` whose `page_content` is a string — but do not normalize it. *`page_content` is a
  string confirmed via Context7 2026-06-08; carried over from Lesson 07.*
