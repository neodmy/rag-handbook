# Lesson 01 — LLMs, Tokens, and Prompting

**Type:** theory

> After this lesson you can explain, in black-box terms, what a large language
> model does when it generates text: how it reads a prompt as tokens, produces
> output one token at a time, why the same prompt can yield different answers, and
> how `temperature`/`top-p` control that — the vocabulary the rest of the handbook
> assumes.

## Prerequisites

None — this is the first lesson. It assumes no prior knowledge of language models
or retrieval.

## Why this matters

Everything in this handbook — building a RAG system and evaluating one — sits on
top of a large language model (LLM). Retrieval feeds text *into* an LLM; generation
*is* the LLM producing an answer; and almost every evaluation method we will study,
including the LLM-as-a-judge metrics at the core of RAGAS, uses an LLM to score
outputs.

If the LLM is a black box whose behavior feels arbitrary, none of that will make
sense. Two facts in particular will keep coming back:

- **The model sees a bounded amount of text (a *context window*) measured in
  *tokens*, not words or characters.** This is the reason we later *chunk*
  documents and worry about per-token cost.
- **Generation is *stochastic*: the same prompt can produce different outputs.**
  This is the reason that, much later, we must *pin* the judge model's settings so
  that an evaluation is reproducible.

We do not need to know how to *train* a model — only how to *use* one and reason
about its behavior. That "black-box, enough to build and evaluate" depth is the
goal of this whole first primer.

## The concept

We will build up four ideas, each concrete before abstract: (1) what an LLM is and
how it generates, (2) tokens and the context window, (3) prompting and in-context
learning, and (4) sampling — `temperature` and `top-p`.

### 1. What an LLM is, and autoregressive generation

A large language model is, at its core, a **next-token predictor**. Given a piece
of text, it outputs a probability distribution over what the *next* token should
be — a number for every possible token in its vocabulary, all summing to 1.

Modern LLMs are built on the **Transformer** architecture introduced by Vaswani et
al. (2017) [1]. For our purposes the internal mechanism (self-attention) is a black
box; what matters is the input→output behavior: text in, a probability distribution
over the next token out.

Text is generated **autoregressively** — literally "regressing on itself." The
model is run in a loop:

1. Feed the current text to the model.
2. The model outputs a probability distribution over the next token.
3. Pick one token from that distribution (how we pick is §4).
4. Append that token to the text, and go back to step 1.

The loop stops when the model emits a special "end" token or hits a length limit.
GPT-3, the model that made prompting famous, is described by its authors precisely
as "an autoregressive language model" [2]. So an LLM does not plan a whole answer
and write it out; it commits to one token, then reconsiders everything (the
original prompt *plus* what it has written so far) to choose the next one.

This single fact explains a lot of later behavior — for example, why an answer can
start confidently and then drift, and why where we place information in the prompt
affects how it is used.

### 2. Tokens and the context window

The model does not operate on words or characters. It operates on **tokens** —
chunks of text from a fixed vocabulary the model was built with. Tokenization
(splitting text into tokens) typically uses **subword units**: common words may be
a single token, while rare or unusual words are split into several smaller pieces.
This is the idea behind Byte-Pair Encoding (BPE), introduced for neural translation
by Sennrich et al. (2016) [3], which lets a fixed-size vocabulary represent *any*
word — even one it has never seen — as a sequence of known subword tokens.

> The precise BPE merge algorithm is out of scope for this black-box primer; what
> you need is the consequence: **text ↔ tokens is a fixed, model-specific mapping,
> and one token is usually a few characters, not a whole word.** A rough rule of
> thumb often cited is "~4 characters per token" for English, but this varies by
> tokenizer and language — treat exact counts as something to measure with the
> model's own tokenizer, not assume.

The model can only process a bounded number of tokens at once — its **context
window**. Everything the model "sees" on a given call — the instructions, any
retrieved documents, the conversation so far, the question, *and* the answer it is
generating — must fit within that window.

Two practical consequences follow, and they motivate large parts of this handbook:

- **Chunking.** A corpus of documents is far larger than any context window, so we
  cannot paste it all in. We will split documents into pieces ("chunks") and
  retrieve only the relevant ones — the "retrieval" in retrieval-augmented
  generation.
- **Cost and latency.** LLM usage is typically billed and timed *per token*. More
  tokens in the prompt means more money and more waiting. "Stuff every document
  into the prompt" is not free even when it fits.

> Concrete context-window sizes and per-token prices are **model-specific facts**
> that change frequently — look them up in the relevant model's official
> documentation rather than memorizing a number. The *existence* of the limit is
> the durable concept; the *size* is a lookup.

### 3. Prompting and in-context learning

The **prompt** is the text you feed the model. In a RAG system the prompt is
assembled from parts — typically an instruction ("Answer using only the context
below"), the retrieved context, and the user's question — concatenated into one
input. How those parts are arranged is itself a design decision we will study later
(augmentation-prompt design).

The reason prompting is so powerful is **in-context learning**. Brown et al. (2020),
in the GPT-3 paper "Language Models are Few-Shot Learners," showed that a
sufficiently large model can perform a new task when the task is "specified purely
via text interaction with the model" — and crucially, this is done "without any
gradient updates or fine-tuning" [2]. In other words, demonstrations or
instructions placed *in the prompt* steer the model's behavior at generation time;
the model's weights are not changed.

This gives a useful spectrum, named in the same paper:

- **Zero-shot:** the prompt gives only an instruction, no examples.
- **One-shot:** the prompt includes a single worked example.
- **Few-shot:** the prompt includes several examples before the real task.

The key takeaway for RAG: putting the *right information in the prompt* changes the
output without retraining anything. That is the entire premise that makes
retrieval-augmented generation possible — we will return to it formally in the next
lessons. (The flip side, that the model treats *whatever* is in the prompt as input
to follow, is also the root of a security problem — indirect prompt injection — we
will study much later.)

### 4. Sampling: temperature and top-p

Recall step 3 of the generation loop: "pick one token from the distribution." How
we pick is the **decoding** (or **sampling**) strategy, and it has a large effect on
the output — even from the exact same model and prompt.

The naive idea — always pick the single most probable token (or do a "maximization"
search like beam search for the highest-probability overall sequence) — turns out
to produce **degenerate** text: Holtzman et al. (2020) show it becomes "bland,
incoherent, or gets stuck in repetitive loops" [4]. The opposite extreme — sampling
freely from the full distribution — lets the long, unreliable "tail" of low-
probability tokens occasionally fire, producing incoherent gibberish [4]. Good
generation lives between these extremes, governed by three knobs that do **two
different jobs**:

- **Temperature *reshapes* the distribution.** It works on the model's raw scores
  (**logits**) before they become probabilities: each logit is divided by a value
  `t`, then a softmax turns them into probabilities. Holtzman et al. state that
  setting `t` in `[0, 1)` "skews the distribution towards high probability events,
  which implicitly lowers the mass in the tail" [4] — so **lower `t` → more
  concentrated, deterministic, "safe"** output; **higher `t` → more spread out,
  random, diverse** output; `t = 1` leaves the distribution unchanged. Crucially,
  temperature only *changes the odds* — it never deletes a token from play.

- **Top-k and top-p *truncate* the distribution.** They cut tokens out entirely so
  they can never be chosen, then renormalize and sample from what survives. The two
  "differ only in the strategy of where to truncate" [4]:
  - **Top-k** keeps a fixed *number* of tokens — the `k` most probable — regardless
    of the distribution's shape.
  - **Top-p (nucleus)** keeps the **smallest set of highest-probability tokens whose
    cumulative probability mass exceeds a threshold `p`**. Because that set "will
    adjust dynamically based on the shape of the probability distribution at each
    time step" [4], its size grows when the model is unsure and shrinks when it is
    confident — this adaptive set is the *nucleus*.

In a typical pipeline temperature is applied *first* (reshape), then top-k or top-p
*cuts* the reshaped distribution, then one token is sampled. The worked example next
puts real numbers on each — and shows why the *dynamic* nucleus behaves better than a
*fixed* `k`.

The one consequence to carry forward: because most real systems sample rather than
take the single most likely token, **the same prompt can give different answers on
different runs.** This is why, when we later use an LLM to *score* RAG outputs (the
LLM-as-a-judge approach behind RAGAS), we must pin these settings (e.g. fix the
temperature and any seed, and record the model version) — otherwise the evaluation
is not reproducible, and "the score went up" might just be sampling noise. This is a
direct application of the evidence-and-reproducibility discipline this repository
insists on.

## Worked example

We trace **one prompt through two steps of the loop**, and at each step we watch the
decoding knobs do the actual picking. The prompt:

```
The capital of France is
```

*(All probabilities are illustrative — chosen to show the mechanics, not measured
from a real model. The temperature columns are a real softmax of the stated logits,
so that arithmetic is correct.)*

### Step 1 — a confident step (peaked distribution)

The model reads the prompt and emits a probability distribution over the next token.
Here it is, computed as a softmax of the logits `4.2, 1.0, 0.5, 0.0, -0.5` — the
**`t = 1.0`** column is the model's distribution; the other temperature columns and
the cumulative total are tools we use below.

| next token | `t = 0.5` | **`t = 1.0`** | `t = 2.0` | cumulative (@ `t = 1`) |
|------------|-----------|---------------|-----------|------------------------|
| ` Paris`   | 0.997     | **0.918**     | 0.634     | 0.918                  |
| ` the`     | 0.002     | **0.037**     | 0.128     | 0.955                  |
| ` located` | 0.001     | **0.023**     | 0.100     | 0.978                  |
| ` now`     | 0.000     | **0.014**     | 0.078     | 0.992                  |
| ` a`       | 0.000     | **0.008**     | 0.060     | 1.000                  |

Now we *pick* a token from this distribution — and the knobs decide how.

**Temperature reshapes it first.** Read the three `t` columns left to right, as `t`
rises: `Paris` *loses* mass (0.997 → 0.918 → 0.634) while a weak option like ` now`
*gains* it (0.000 → 0.014 → 0.078). Low `t` sharpens toward the favorite; high `t`
flattens toward the alternatives. Note temperature only *changes the odds* — it never
removes ` now` from the table. (Temperature is one global setting applied at *every*
step; we show it once here.)

**Then top-k or top-p truncates and we sample.** Take the `t = 1.0` distribution with
`k = 5` and `p = 0.9`:

- **top-k = 5** is *forced* to keep five tokens — `Paris` plus `the, located, now, a`,
  even though those four (~0.082 of mass) are clearly wrong for a factual answer. A
  fixed `k` cannot tighten on a confident step: it **over-includes**.
- **top-p = 0.9** keeps the smallest set whose cumulative mass exceeds 0.9. `Paris`
  alone is 0.918 > 0.9, so the **nucleus is just `{Paris}`**. It tightened
  automatically because the model was sure.

We sample — almost certainly ` Paris`.

### Step 2 — append, re-feed, and an open step (flat distribution)

We append the chosen token and feed the **whole** string back in: `The capital of
France is Paris`. This is the autoregressive loop — **at every step the model
re-reads everything so far**, prompt plus what it has already written.

This time the model is genuinely unsure how the sentence continues — a period, a
comma, a parenthetical, a conjunction are all reasonable — so the distribution is
*flat* (illustrative):

| next token | p    | cumulative |
|------------|------|------------|
| `.`        | 0.22 | 0.22       |
| `,`        | 0.18 | 0.40       |
| ` (`       | 0.14 | 0.54       |
| ` and`     | 0.12 | 0.66       |
| ` —`       | 0.10 | 0.76       |
| ` in`      | 0.09 | 0.85       |
| ` which`   | 0.08 | 0.93       |
| ` a`       | 0.04 | 0.97       |
| …tail…     | 0.03 | 1.00       |

Apply the **same** `k = 5` and `p = 0.9` that gave `{Paris}` a moment ago:

- **top-k = 5** keeps only `. , ( and —` (cumulative 0.76) and discards ` in` and
  ` which` — which are *almost as likely* as ` and` and ` —`. The same fixed `k` now
  **under-includes**, amputating plausible continuations.
- **top-p = 0.9** keeps adding until the mass exceeds 0.9: through ` in` is 0.85 (not
  yet), so ` which` joins → 0.93. The **nucleus is 7 tokens** (`.` … ` which`). It
  *widened* automatically because the model was unsure.

We sample one continuation, append it, and the loop repeats until the model emits an
end token.

### What the two steps showed

A **single fixed `k` is simultaneously too large on the peaked Step 1 and too small
on the flat Step 2.** Top-p avoids both because its set size tracks the shape of the
distribution (Holtzman et al. note top-k's effective mass "can vary wildly at each
time-step, in contrast to Nucleus Sampling" [4]) — which is why `top_p` is the more
common default, though many APIs expose both. It is also why **factual RAG answers
are usually generated at low temperature with a tight `top_p`**: on a confident step
that keeps the model on its single best answer; the open-ended variety we just saw at
Step 2 is exactly what we *don't* want when the goal is a grounded, factual response.

## Your turn

No code yet — this is a reasoning exercise. Spend a few minutes on each:

1. **Token intuition.** Open any LLM provider's public *tokenizer playground* (for
   example, search for "tokenizer" on your model vendor's site) and paste in a
   sentence with an unusual word (a rare surname, a long technical term, a word in
   another language). Watch it split into several subword tokens while common words
   stay whole. Then ask yourself: *if a document is 10,000 words, will it fit in a
   model with an 8,000-token context window?* (You can't answer from word count
   alone — that's the point.)

2. **Predict the effect of a knob.** You are building a system that must return the
   *same* answer to the *same* factual question every time. Would you set
   temperature high or low? Now you instead want a brainstorming tool that offers
   varied suggestions. Which way do you move temperature, and why? Tie your answer
   back to "skews the distribution towards high probability events."

3. **Spot the reproducibility trap.** Suppose a teammate says "our new prompt scored
   higher on the eval, so it's better." Given what you now know about sampling, what
   is the *first* question you should ask before believing the result?

## Common pitfalls / misconceptions

- **"A token is a word."** No — a token is usually a *subword* piece; rare words
  span several tokens and common words may be one. Counting words is not counting
  tokens. [3]

- **"The model writes the whole answer at once."** It generates **one token at a
  time**, re-reading everything so far each step. [2] This is why answers can drift
  and why prompt *order* matters.

- **"Temperature 0 / greedy is always best because it's most accurate."** Pure
  maximization is prone to **degenerate, repetitive** text in open-ended
  generation; that surprising result is the whole motivation for nucleus sampling.
  [4] Low temperature is the right call for short, factual answers, but it is not a
  universal "best."

- **"Top-k and top-p are the same thing."** Both truncate the distribution, but
  top-k keeps a **fixed number** of tokens while top-p keeps a **dynamic set**
  defined by cumulative probability — they "differ only in the strategy of where to
  truncate." [4]

- **"Same prompt → same answer."** Only if you've forced it (greedy, or pinned
  temperature/seed and model version). By default, sampling makes generation
  **stochastic** — a fact that will matter enormously when we evaluate. [4]

## Check your understanding

1. The model assigns ` Paris` a probability of 0.97 for the next token. Under top-p
   with `p = 0.9`, how many tokens are in the nucleus, and roughly why? Now the
   distribution is much flatter — the top token is only 0.2. What happens to the
   size of the nucleus, and what does that imply about the variety of possible
   outputs?

2. A colleague wants to reduce their LLM bill and proposes "just send fewer
   documents but write a longer instruction." Using the idea of tokens and the
   context window, explain why "longer instruction" is not automatically cheaper,
   and what actually drives the cost.

3. In-context learning lets a prompt change the model's behavior "without any
   gradient updates." Why does that property make retrieval-augmented generation
   possible at all? (What would you have to do instead if changing behavior
   *required* retraining?)

4. Two runs of the *identical* prompt and model give two different answers. Name the
   mechanism responsible, and name one setting you would change to make the runs
   repeatable.

## Summary & next

We established the black-box model of an LLM the rest of the handbook relies on: a
**next-token predictor** run in an **autoregressive loop**; input and output
measured in **tokens** within a bounded **context window** (the seed of *chunking*
and *per-token cost*); behavior steered by the **prompt** via **in-context
learning** with no weight changes; and output made **stochastic** by **sampling**,
controlled by **temperature** and **top-p** (the seed of *evaluation
reproducibility*).

Next (lesson 02, *Embeddings and search*) we add the other half of the foundation:
how text becomes **vectors** so that meaning can be searched — the mechanism that
lets a RAG system *find* the right chunks to put in the prompt.

## Sources

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — Vaswani et al.,
  NeurIPS 2017. **[1]** The Transformer architecture underlying modern LLMs
  (black-box depth here).
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) — Brown
  et al., NeurIPS 2020. **[2]** Autoregressive language modeling; in-context /
  zero-/one-/few-shot learning "without any gradient updates or fine-tuning."
- [Neural Machine Translation of Rare Words with Subword Units](https://aclanthology.org/P16-1162/)
  — Sennrich, Haddow, Birch, ACL 2016. **[3]** Subword (BPE) tokenization — what
  tokens are.
- [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)
  — Holtzman, Buys, Du, Forbes, Choi, ICLR 2020. **[4]** Decoding strategies:
  degeneration of maximization, nucleus (top-p) sampling, top-k, and temperature;
  why generation is stochastic.
