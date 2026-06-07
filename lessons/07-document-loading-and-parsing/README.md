# Lesson 07 — Document Loading and Parsing

**Type:** theory+practice

> After this lesson you can explain why a document *file* is not the same thing as
> usable *text*, name the two things parsing must recover (reading order and
> structure — including tables), parse a real PDF four different ways and read where
> each one silently loses information, and choose a parsing tool deliberately
> instead of by default.

## Prerequisites

- [Lesson 05 — A Minimal End-to-End RAG](../05-minimal-end-to-end-rag/README.md)

(Lesson 05 is the only hard prerequisite — ingestion branches off the runnable
baseline, not off the evaluation lessons. This lesson assumes you have seen the
**load → chunk → embed → retrieve → generate** pipeline and know that retrieval
operates on chunked text.)

## Why this matters

In Lesson 05 the corpus was a folder of clean `.txt` files. That was a convenience
for a first run, and it hid the single most under-appreciated fact about production
RAG: **real documents do not arrive as clean text.** They arrive as PDFs exported
from word processors, web pages wrapped in navigation and ads, slide decks, scanned
contracts that are images of text, and spreadsheets. Before any of Lesson 05's five
stages can run, something has to turn those files into text — and *how well* it does
that sets a ceiling on everything downstream.

This is the start of **Part II: Ingestion**, and it is first on purpose. Ingestion is
where production RAG most often quietly fails, because its failures are **silent**.
A bad parse does not raise an exception; it returns *text*, just the wrong text — a
two-column page read straight across so sentences are spliced together, a table
collapsed into a meaningless run of numbers, a heading lost so a chunk has no idea
what it is about. Nothing crashes. The pipeline runs, embeds the garbage, retrieves
the garbage, and generates a confident answer from it. The slogan for this whole part
is **garbage in, garbage retrieved**: the cleanest retriever and the best generator in
the world cannot recover information that was destroyed at the loading step.

## The concept

We introduce four ideas — load vs parse, reading order, tables, and OCR — then step
back to the tool ecosystem and how to choose. One idea at a time.

### A document file is not text

Open a PDF in a text editor and you will not find your paragraphs. A PDF is a
*page-description* format: it stores instructions for *drawing* — "place this glyph
at these coordinates, in this font" — plus images and vector graphics. There is no
guaranteed notion of "paragraph", often no reliable notion of "this word comes before
that one", and certainly no marker saying "this block is a table." HTML is the
opposite problem: it has structure (tags), but it is buried in boilerplate — navigation
bars, cookie banners, ads, footers — that is not the content you want to retrieve. A
scanned document is the hardest case: it is just *pixels*, an image of text, with no
characters at all until something recognizes them.

So the first ingestion step is really two jobs, and it helps to name them separately:

- **Loading** — recover the *characters*. Get the text out of the file at all.
- **Parsing** — recover the *structure*: the reading order, the headings, the lists,
  the tables — the organization that the text's *meaning* depends on.

A useful mental model for the output of a good parser is a **list of typed elements** —
a `Title`, then several `NarrativeText` blocks, a `ListItem` or two, a `Table` — rather
than one undifferentiated string. This is exactly the model the Unstructured library
uses: partitioning a document returns "a list of document `Element` objects," each with
a `type`, the extracted `text`, and metadata [1]. Typed structure is not a luxury; it is
the supply side for everything later in Part II — you chunk *along* structure (Lesson 09),
you filter on the metadata you extract (Lesson 10), and you can serialize a `Table`
faithfully instead of shredding it.

### Reading order is inferred, not stored

Here is the idea that surprises people most. A PDF records *where* each piece of text
sits on the page, but not the *order* a human would read it in. For a single column of
prose the two usually coincide. For anything else — two columns, sidebars, headers and
footers, footnotes — they can diverge, and the parser has to *guess* the reading order.
Different parsers guess differently, and a wrong guess splices unrelated text together.

This is not a quirk of one library; it is *why* a whole research area — layout-aware
document understanding — exists. Models like LayoutLMv3 are built to combine the text
with its **layout and image** information precisely because the linear text stream alone
underdetermines a document's two-dimensional structure [2]. (The phrase "reading order"
is our framing of that problem; LayoutLMv3's own headline contribution is unifying the
text and image modalities — see the source note [2]. The point stands either way: 2-D
structure is information that plain text loses.)

You will *see* this divergence in the worked example: the same two-column page comes out
in the right order from one extractor and scrambled from another, and **neither one is
"buggy."** They simply made different, equally defensible guesses about an order the file
never recorded.

### Tables are two-dimensional; flattening destroys them

A table's meaning lives in its **grid**: the cell `$40` means nothing until you know it
sits in the *Team* row under the *Price* column. A naive text extractor walks the cells
and emits them as a flat sequence — `Team`, `1 TB`, `Up to 25`, `$40`, … — and the
row-and-column relationship, which *was* the information, is gone. For a small table a
human can still squint and reconstruct it; for a wide or multi-row table the flattened
stream interleaves into nonsense, and an embedding of that stream cannot reliably answer
"how many members does the Team plan allow?"

Recovering a table is therefore its own problem, with its own sub-tasks. The PubTables-1M
work frames table extraction as "all three tasks of detection, structure recognition, and
functional analysis" [3] — find the table on the page, recover its row/column grid, and
work out which cells are headers versus data. A structure-aware extractor gives you the
grid back as rows; you can then serialize it to something that *keeps* the structure (e.g.
Markdown or HTML) so the relationship survives into the chunk.

> **A boundary, to avoid a forward-reference trap.** *Parsing* a table out of a document
> (recovering its grid) is a different problem from *querying* tabular data — running
> aggregations or joins over a database. The latter is **text-to-SQL**, a retrieval
> technique covered much later (Lesson 20). Here we only care about getting the table out
> of the document without shredding it.

### Scanned and image-only documents need OCR first

If the document is a scan or a photo, there are no characters to load — only pixels.
**Optical Character Recognition (OCR)** is the step that turns those pixels into text, and
it must run *before* any of the above. OCR is its own engineering surface (it can misread
characters, and its output quality depends on scan resolution and layout), and it commonly
introduces a fresh layer of errors that then propagate through reading-order and table
recovery. We do **not** run OCR in this lesson's code — it needs a separate engine
(e.g. Tesseract) and a system binary — but you should know it is the mandatory first stage
for any image-only source, and a real source of silent corruption. *(This paragraph is
conceptual orientation, not a sourced claim about a specific OCR engine.)*

### The tool ecosystem, and how to choose

There is no single "correct" parser — the right tool depends on the file types you face,
the structure you must preserve, and your fidelity/speed/licensing constraints. A rough map
of well-regarded options is below; for the **fuller verified catalogue** (PDF, OCR, and HTML
tools, with licenses and selection criteria) see the companion
[**Appendix — Parsing & extraction tools**](./appendix-parsing-tools.md) in this folder.

- **Lightweight, pure-Python PDF** — **pypdf** [5] for quick text extraction (no structure),
  and **pdfplumber** [4] when you need layout and **table** extraction with positional
  control. We use both below because they make the trade-offs visible.
- **High-level / structured** — **Unstructured** [1] turns many formats into the typed
  `Element` list described above; **MarkItDown** (Microsoft) converts PDF/Office/HTML/etc.
  to **Markdown** aimed at LLM ingestion, though its docs note it targets text-analysis
  tools, "not the best option for high-fidelity document conversions for human consumption"
  [6]; **PyMuPDF** is a fast extractor with rich position metadata — note its **AGPL** license
  if you ship a closed-source product [7].
- **Orchestration wrappers** — LangChain's **document loaders** (`PyPDFLoader`,
  `UnstructuredLoader`, …) wrap these underlying parsers behind one uniform `Document`
  interface [8], the same `Document` object Lesson 05 used. The wrapper does not change the
  parsing quality; it just standardizes the hand-off.
- **HTML, semantic extraction** — for web pages you usually want the *main content*, not the
  DOM. **trafilatura** extracts the article text and strips boilerplate [9]; the older
  **python-readability** (a port of Mozilla's Readability) does the same job; **BeautifulSoup**
  is lower-level — it parses HTML into a navigable tree that *you* query, and does no automatic
  main-content extraction. *(trafilatura/readability/BeautifulSoup mentioned for orientation;
  trafilatura is the one we verified at its source [9].)*

The decision rule that matters: **pick the tool by the structure you cannot afford to lose.**
If your corpus is tables, a text-only extractor is disqualified no matter how fast it is.

## Worked example

The runnable code is [`demo.py`](./demo.py). Run it from the repo root:

```bash
uv run python -m lessons.07-document-loading-and-parsing.demo
```

It parses one fictional PDF — `data/acme-cloud-plans.pdf`, a two-column "Acme Cloud" plan
sheet with a pricing table, generated by [`make_sample_pdf.py`](./make_sample_pdf.py) and
committed under `data/` (invented content, not a real product, not an evaluation dataset).
No LLM and no network are involved — only PDF parsers (`pypdf` 6.13.0, `pdfplumber` 0.11.9) —
so the output is **fully reproducible**. Here is the **real output** of a run, in four views
of the *same file*.

**View 1 — naive extraction (pypdf, content-stream order).** The two-column page comes out
fine here, then the table is flattened:

```
1. NAIVE EXTRACTION  (pypdf — content-stream order)
Page 1 (two-column prose):

Choosing an Acme Cloud Plan
Acme Cloud offers three subscription tiers designed
for individuals, growing teams, and large
...
The Team tier adds shared workspaces, role-based
...
Storage, Backups, and Limits
Storage is measured per account, not per device,
...

Page 2 (the pricing TABLE), extracted as plain text:

Plan Comparison
Plan
Storage
Members
Price / month
Starter
100 GB
1
$5
Team
1 TB
Up to 25
$40
Enterprise
Pooled
Unlimited
Custom
```

pypdf reads in the PDF's **content-stream order** — the order the text was written into the
file. Our generator happened to write the left column fully, then the right, so the prose comes
out correctly ordered. *That is luck, not robustness* — pypdf never asked whether the page has
columns. The **table** is the real damage: it is now a flat list of cells. The grid that told you
`$40` is *Team's* price, with *1 TB* of storage and *up to 25* members, is gone — you have the
right tokens in roughly the right order, but the *structure that was the information* has
dissolved into a column of words.

**View 2 — geometry order (pdfplumber default).** The *same* page, a different guess:

```
2. GEOMETRY-ORDER EXTRACTION  (pdfplumber default — top-to-bottom)
Page 1, same file — note the two columns are now interleaved:

Choosing an Acme Cloud Plan Storage, Backups, and Limits
Acme Cloud offers three subscription tiers designed Storage is measured per account, not per device,
for individuals, growing teams, and large so connecting a second computer does not
organizations. Every tier includes encrypted consume additional quota. Backups run
...
```

pdfplumber's default sorts text by **vertical position** and reads left-to-right across the
*whole page* — so it splices the two columns together line by line. The title now reads
"Choosing an Acme Cloud Plan Storage, Backups, and Limits"; the Starter sentence is glued to an
unrelated sentence about per-device storage. **This is the reading-order problem made concrete:**
two reputable parsers, one file, two different texts — because the reading order was never in the
file to begin with. (This is also a warning about chunking next lesson: chunk *this* text and every
chunk straddles two unrelated topics.)

**View 3 — layout-preserving (pdfplumber `layout=True`).** Ask the parser to honor geometry and
you can *see* why:

```
3. LAYOUT-PRESERVING EXTRACTION  (pdfplumber layout=True)
Page 1 — whitespace mimics the page; you can SEE two columns:

        Choosing  an Acme Cloud Plan         Storage, Backups, and Limits
        Acme Cloud offers three subscription tiers designed Storage is measured per account, not per device,
        for individuals, growing teams, and large so connecting a second computer does not
        ...
```

`layout=True` reconstructs the visual page with whitespace, and the two columns appear side by
side [4]. This is the proof that a PDF stores **positions, not reading order**: the geometry is
right there, and a downstream step (or a layout-aware model [2]) could use it to recover the two
columns — but a naive line-by-line read of that same geometry is exactly what produced the scramble
in View 2.

**View 4 — structure-aware table extraction (pdfplumber `extract_table`).** Now the table, done
right:

```
4. STRUCTURE-AWARE TABLE EXTRACTION  (pdfplumber extract_table)
Page 2 table recovered as rows (each row is a Python list):

  ['Plan', 'Storage', 'Members', 'Price / month']
  ['Starter', '100 GB', '1', '$5']
  ['Team', '1 TB', 'Up to 25', '$40']
  ['Enterprise', 'Pooled', 'Unlimited', 'Custom']

Serialized to Markdown — structure survives into the chunk:

| Plan | Storage | Members | Price / month |
| --- | --- | --- | --- |
| Starter | 100 GB | 1 | $5 |
| Team | 1 TB | Up to 25 | $40 |
| Enterprise | Pooled | Unlimited | Custom |
```

`extract_table()` recovers the **grid** — the same content View 1 flattened, but now every cell
keeps its row and column [4]. Serialized to Markdown, the relationship *survives into the text you
will embed*: a chunk containing that Markdown table can answer "what is Team's price?" because
`$40` is still attached to *Team* and *Price*. This is the whole lesson in one contrast: View 1 and
View 4 read the *identical bytes*; the difference is entirely in whether the parser recovered the
structure.

## Your turn

Run the demo, then poke at it:

1. **Diff the four views yourself.** Read View 1's page-1 prose against View 2's. Find the exact
   point where View 2 splices the columns. Then ask: if you fed View 2's text into Lesson 05's
   chunker, what would a single chunk contain?

2. **Make the table worse.** In `make_sample_pdf.py`, add two more columns to `TABLE_DATA` (e.g.
   "Backups", "SSO"), regenerate the PDF
   (`uv run python -m lessons.07-document-loading-and-parsing.make_sample_pdf`), and re-run the demo.
   Watch how the *naive* (View 1) table degrades as it gets wider, while `extract_table` (View 4) still
   returns clean rows.

3. **Change the reading-order gamble.** In `make_sample_pdf.py`, the story fills the left frame then
   the right. Nothing guarantees a real-world PDF does that. Note that pypdf's "correct" page-1 result
   is contingent on that write order — it is not the parser being smart.

4. **(Optional) Try a higher-level tool.** Point a tool from the ecosystem section at the same PDF —
   e.g. `pip install markitdown` and convert the file to Markdown — and compare how it renders the
   table versus `extract_table`'s grid. Notice you are choosing a tool by *what structure it preserves*.

You are not fixing anything here. The goal is to *feel* that "I extracted the text" is an
under-specified claim — which text, in which order, with which structure?

## Common pitfalls / misconceptions

- **"I got text out, so loading is done."** Getting *characters* is loading; getting the *right text in
  the right order with its structure* is parsing, and only the second one protects retrieval. A parser
  that returns scrambled columns or a flattened table "succeeded" and still poisoned everything downstream.

- **"The parser that scrambled the columns is buggy."** No — reading order is not stored in the file [2].
  Two correct parsers can return two different orders because each makes a different, defensible guess.
  The fix is to *know which structure you need* and pick (or configure) a tool accordingly, not to expect a
  universal right answer.

- **"Tables are just text in a grid; extraction is easy."** A table's meaning *is* the grid; flattening it
  to a text stream throws away the row/column relationship that was the point [3]. Always check what your
  parser does to tables before trusting numeric or multi-column content.

- **"Parsing a table lets me do calculations on it."** Recovering a table's grid (this lesson) is not the
  same as querying tabular data with aggregations/joins — that is text-to-SQL (Lesson 20). Parsing gets the
  table *out of the document*; it does not make it a database.

- **"Use the most powerful parser for everything."** The most powerful (or layout-aware ML) parser is also
  the slowest and heaviest, and may carry a restrictive license (e.g. PyMuPDF is AGPL [7]). Match the tool to
  the corpus: a folder of clean single-column PDFs does not need a layout model; a stack of scanned, tabular
  reports does.

- **"Parsing failures will show up as errors."** They almost never do. Ingestion fails *silently* — it
  returns plausible-looking text. The only way to catch it is to *look* at the parser's output on
  representative documents, which is exactly what the four views above train you to do.

## Check your understanding

1. View 1 (pypdf) and View 4 (`extract_table`) read the **same bytes** of page 2, yet one is usable and one
   is shredded. In your own words, what did View 4 recover that View 1 lost, and why does that matter for a
   query like "how many members does the Team plan allow?"

2. Two parsers returned two different orderings of the *same* two-column page, and we said neither is buggy.
   What fact about the PDF format makes that statement true, and what does it imply about trusting *any* single
   extractor's reading order?

3. Distinguish **loading** from **parsing** using the table on page 2 as your example. Which step does pypdf's
   View-1 output complete, and which does it fail?

4. A teammate says, "Our corpus is scanned invoices, but pdfplumber returns empty text — the library is broken."
   What is the most likely actual cause, and what stage is missing from their pipeline?

5. You must ingest a corpus that is 90% clean single-column PDFs and 10% dense financial tables. Argue for a
   parsing approach, and say explicitly which structure you are *unwilling* to lose and which tool from the
   ecosystem section protects it.

## Summary & next

A document file is not text, and "I extracted the text" is an under-specified claim. We separated **loading**
(recover characters) from **parsing** (recover structure), and saw the two things parsing must reconstruct:
**reading order** — which is *inferred, not stored*, so different parsers legitimately disagree [2] — and
**tables**, whose meaning is a 2-D grid that flattening destroys [3]. We parsed one PDF four ways and read,
in real output, how the *same bytes* become usable or useless depending entirely on whether structure was
recovered: pypdf's content-stream order [5], pdfplumber's geometry order, its layout-preserving view, and its
structure-aware `extract_table` [4]. We also mapped the tool ecosystem — lightweight (pypdf/pdfplumber),
structured (Unstructured [1] / MarkItDown [6] / PyMuPDF [7]), orchestration wrappers (LangChain loaders [8]),
and HTML main-content extractors (trafilatura [9]) — with one decision rule: **choose by the structure you
cannot afford to lose.** And we named ingestion's defining hazard: it fails *silently*.

Two threads carry forward into the rest of Part II. First, even perfectly parsed text usually still contains
**boilerplate and duplicates** — the next lesson, **Cleaning and Deduplication** (Lesson 08), strips what
parsing left behind so the top-k is not crowded with near-identical or junk chunks. Second, the *typed
structure* we recovered here is exactly what good **chunking** (Lesson 09) splits along — which is why getting
structure out *now* pays off there. Garbage in, garbage retrieved; this lesson is where you stop the garbage at
the door.

## Sources

- [Unstructured — Partitioning](https://docs.unstructured.io/open-source/core-functionality/partitioning)
  and [Document elements](https://docs.unstructured.io/open-source/concepts/document-elements)
  — Unstructured, official docs. **[1]** The model of parsing as producing a list of typed `Element`
  objects (`Title`, `NarrativeText`, `ListItem`, `Table`, …), each with `type`/`text`/metadata.
  *Verified at the primary 2026-06-07; the typed-element framing lives on the Document-elements concepts page.*
- [LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking](https://arxiv.org/abs/2204.08387)
  — Huang, Lv, Cui, Lu, Wei (Microsoft), ACM MM 2022. **[2]** Document understanding combines text with
  layout/image because a document's 2-D structure is information the plain text stream loses. *Honesty flag:
  the abstract's verbatim contribution is "unified text and image masking"; "reading order" is our framing of
  the problem, not the abstract's wording (body-/family-sourced).*
- [PubTables-1M: Towards Comprehensive Table Extraction from Unstructured Documents](https://arxiv.org/abs/2110.00061)
  — Smock, Pesala, Abraham (Microsoft), CVPR 2022. **[3]** Table extraction as "all three tasks of detection,
  structure recognition, and functional analysis" (verbatim, abstract). *"Rows/columns must be recovered" is our
  gloss of structure recognition, not abstract wording.*
- [pdfplumber](https://github.com/jsvine/pdfplumber) — J. Singer-Vine, official repo/docs. **[4]** The
  layout-aware extraction used here: `extract_text(layout=True)` (visual geometry), default `extract_text()`
  (top-to-bottom geometry order), and `extract_table()` (recover the 2-D grid). *API verified by execution this
  session (pdfplumber 0.11.9) and via Context7.*
- [pypdf](https://github.com/py-pdf/pypdf) — py-pdf maintainers, official repo/docs. **[5]** Naive text
  extraction in content-stream order with no structural typing. *Verified by execution this session (pypdf 6.13.0).*
- [MarkItDown](https://github.com/microsoft/markitdown) — Microsoft, official repo. **[6]** File-to-Markdown
  conversion aimed at LLM ingestion; its own docs note it is not for high-fidelity human-facing conversion.
  *Verified at the repo 2026-06-07. Single-vendor tool.*
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) — Artifex Software (on MuPDF), official repo. **[7]** Fast PDF
  text/layout extraction with position metadata; **AGPL v3** license (commercial use needs an Artifex license).
  *Verified 2026-06-07.*
- [LangChain — Document loaders](https://python.langchain.com/docs/concepts/document_loaders/)
  — LangChain, official docs. **[8]** A uniform `Document`-loading interface whose concrete loaders wrap the
  underlying parsers (pypdf, unstructured, …). *Page live 2026-06-07; per-loader wrapping cross-checked against
  the integrations index.*
- [trafilatura](https://github.com/adbar/trafilatura) — A. Barbaresi, official repo/docs. **[9]** HTML
  main-content extraction (boilerplate removal) for web sources. *Heuristic; quality varies by page. Verified
  2026-06-07.*
