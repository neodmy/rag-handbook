# Appendix — Parsing & extraction tools (PDF · OCR · HTML)

A reference catalogue of the tools used to turn raw documents into the clean,
structured text that RAG ingestion needs. It is the companion to **[Lesson 07 —
Document loading and parsing](./README.md)**:
the lesson teaches the *concepts* (loading vs
parsing, reading order, tables, OCR) and uses two tools as vehicles; this appendix
is the wider map.

This is a **reference document**, not a lesson — it has no prerequisites and no
gradual-release structure. But it follows the same evidence discipline as the rest
of the handbook.

## How to read this

- **Every tool links to its authoritative primary** — the official GitHub repo or
  the vendor's official docs. Capabilities, licenses, and categories were **verified
  at those primaries on 2026-06-07**, not recalled from memory. A repo/official-doc
  page is authoritative ("high") for that tool's *own* behavior; the few entries that
  rest on single-vendor prescriptive copy, or that we could not fully verify, are
  flagged inline.
- **Open-source tools are ordered by GitHub stars (descending)** within each group,
  as a rough popularity proxy. Star *counts* are deliberately omitted — they drift and
  they are noisy. Where a star count is misleading (legacy popularity on an
  unmaintained project, or a project hosted off GitHub), that is flagged.
- **No pricing.** Cloud services change prices constantly; we record only *capability*
  and that they are paid/hosted. Check the vendor's current pricing page yourself.
- **Licenses are decision-critical and are called out** — especially copyleft (GPL/AGPL)
  and model-weight licenses with commercial revenue caps, which can disqualify a tool
  for a closed-source product regardless of how good it is.
- **Registry relationship.** `docs/sources.md` (the source registry that *lessons* cite)
  carries only the tools a lesson actually cites. This appendix is its own verified
  surface for the broader catalogue; it does not duplicate every tool into the registry.

> **A recurring boundary.** *Parsing* a table out of a document (recovering its
> row/column grid) is not the same as *querying* tabular data with aggregations/joins —
> that is text-to-SQL, a separate retrieval technique (syllabus Lesson 20). This
> appendix is about getting structure *out of documents* faithfully.

---

## 0. How to choose — selection criteria (read before the catalogue)

There is no universally "best" parser. The right tool is the one that preserves the
structure your queries depend on, at an acceptable cost and license. Decide along these
axes:

1. **What structure can you not afford to lose?** If your corpus is tables, a text-only
   extractor is disqualified no matter how fast it is. If it is multi-column prose,
   reading-order reconstruction matters. If it is plain single-column text, the
   lightweight tools are exactly right and anything heavier is wasted.
2. **Is the input text-based or scanned?** Text-based PDFs carry an embedded text layer
   the lightweight/table tools can read directly. **Scanned or image-only documents have
   no text** — they require an OCR stage *first* (see §B), and OCR introduces its own
   errors that then propagate.
3. **Fidelity vs. speed vs. cost.** ML layout models and cloud services give the best
   structure recovery but are the slowest/heaviest (GPUs, large installs) or metered.
   Heuristic/pure-Python tools are fast and free but degrade on complex layouts.
4. **Local vs. hosted.** Hosted APIs (LlamaParse, the cloud document-AI services) mean
   **your documents leave your environment** — often a hard blocker for sensitive,
   regulated, or air-gapped data. Self-hostable tools keep data in-house.
5. **License.** Permissive (MIT/Apache/BSD) is safe to embed anywhere. **Copyleft (GPL,
   AGPL) and weight licenses with revenue caps** (some ML parsers) can be incompatible
   with a closed-source commercial product. Check before you build, not after.

---

## A. PDF parsing

PDFs store *positioned glyphs and drawing operations*, not logical text — so "getting the
text out" ranges from a one-liner that ignores structure to ML pipelines that reconstruct
reading order and tables. Five groups, lightest to heaviest.

### A.1 Lightweight text extraction (pure-Python, no layout model)

Fast, tiny installs, **text-based PDFs only**, no OCR. They recover characters; structure
is mostly on you.

| Tool | Maintainer | Strength / what it preserves | Output | License |
|------|-----------|------------------------------|--------|---------|
| [pdfplumber](https://github.com/jsvine/pdfplumber) | J. Singer-Vine | Positioned chars/words/lines + `extract_text(layout=True)` (visual geometry) + `extract_table()` (2-D grid) | text, table rows (lists), object metadata | MIT |
| [pypdf](https://github.com/py-pdf/pypdf) | py-pdf org | Basic text in content-stream order; merge/split/encrypt | text | BSD-3-Clause *(GitHub reports `NOASSERTION` — non-standard LICENSE file; permissive)* |
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) | Artifex (on MuPDF) | Very fast text/layout extraction with position metadata; rendering | text, dict/JSON with positions; `pymupdf4llm` → Markdown | ⚠️ **AGPL-3.0** (commercial use needs an Artifex license) |

*When:* clean single-column PDFs, or when you need positional control to build structure
yourself (pdfplumber). *Honest limit:* none of these "understand" multi-column reading
order — they return glyphs in stream or geometric order, which can scramble columns (the
exact failure Lesson 07 demonstrates).

### A.2 Layout-aware document toolkits (recover reading order + structure)

ML-based pipelines that detect page layout, reconstruct reading order, and recognize table
structure — the modern choice for complex/heterogeneous corpora.

| Tool | Maintainer | Strength / what it preserves | Output | License |
|------|-----------|------------------------------|--------|---------|
| [Docling](https://github.com/docling-project/docling) | IBM → Linux Foundation | "page layout, reading order, table structure, code, formulas" (verbatim); local/air-gapped execution | Markdown / HTML / lossless JSON (`DoclingDocument`) | **MIT** (VLM weights separate) |
| [Marker](https://github.com/datalab-to/marker) | Datalab | End-to-end PDF→Markdown; layout + reading order (via Surya); dedicated table converter; optional LLM pass | Markdown / JSON / HTML / chunks | ⚠️ **GPL-3.0 code + Open-Rail-M weights** (free commercial only under ~$2M revenue/funding) |
| [Surya](https://github.com/datalab-to/surya) | Datalab | Marker's engine: layout + reading order (`position` per block) + table rows/cols/cells; multilingual | JSON (bboxes), Markdown, HTML | ⚠️ **Apache-2.0 code + Open-Rail-M weights** (cap ~$5M); needs an inference backend |
| [unstructured](https://github.com/Unstructured-IO/unstructured) | Unstructured.io | Partitions many formats into **typed elements** (`Title`/`NarrativeText`/`Table`/…); `hi_res` strategy runs layout detection; tables → HTML in `text_as_html` | typed `Element` list → JSON | **Apache-2.0** |
| [Nougat](https://github.com/facebookresearch/nougat) | Meta AI | Image→markup transformer; "understands LaTeX math and tables" — built for **academic papers** | Mathpix-Markdown (`.mmd`) | MIT code; **weights under a separate license** |
| [layoutparser](https://github.com/Layout-Parser/layout-parser) | Layout-Parser org | Low-level toolkit wrapping detection models (Detectron2) → layout regions; **you** assemble reading order/tables | Python `Layout`/`TextBlock` objects | Apache-2.0 |

*Honest limits (verified):* Docling's metadata extraction is "coming soon"; Marker warns
"very complex layouts, with nested tables and forms, may not work"; Surya is a building
block (use Marker for end-to-end) and is GPU-oriented; unstructured's good layout/table
quality needs the heavier `hi_res` path; Nougat is academic-domain-specific and effectively
unmaintained vs. Docling/Datalab; layoutparser leaves reading-order/table assembly to you and
depends on Detectron2.

### A.3 Table-specialized

When tables are the payload and you want the grid as data.

| Tool | Maintainer | Strength / what it preserves | Output | License |
|------|-----------|------------------------------|--------|---------|
| [Camelot](https://github.com/camelot-dev/camelot) | camelot-dev | Row/column cell recovery; `lattice` (ruled) vs `stream`/`network` (whitespace) vs opt-in neural `ml`; per-table quality metrics | pandas DataFrame; CSV/JSON/Excel/HTML/Markdown/SQLite | MIT *(older releases were GPLv3 — verify the pinned version)* |
| [tabula-py](https://github.com/chezou/tabula-py) | M. Ariga (wraps tabula-java) | `lattice`/`stream` table detection; explicit `area`/`columns` | DataFrame / CSV / TSV / JSON | MIT *(requires a Java runtime)* |
| [GROBID](https://github.com/grobidOrg/grobid) | P. Lopez / Inria | **Scientific** PDF structuring: sections, references, reading order, figures/tables → TEI/XML | TEI/XML | Apache-2.0 |

Plus **pdfplumber**'s `extract_table()` (§A.1) for text-based PDFs. *Honest limits:*
Camelot/tabula/pdfplumber are **text-PDF only** without OCR add-ons; GROBID is strong on
document/section/reference structure but weak on table-cell fidelity, and is tuned for
scholarly articles.

### A.4 LLM-oriented Markdown conversion

Convert many formats to LLM-friendly Markdown (token-efficient, structure-bearing).

| Tool | Maintainer | Strength | Output | License |
|------|-----------|----------|--------|---------|
| [MarkItDown](https://github.com/microsoft/markitdown) | Microsoft | PDF/Office/HTML/images/audio/… → Markdown for LLM ingestion | Markdown | MIT |

*Honest limit (its own docs):* "meant to be consumed by text-analysis tools … **not the best
option for high-fidelity document conversions for human consumption**" — i.e. it optimizes for
*LLM-readable* Markdown, not a visually faithful clone of the source. (Docling and Marker in
§A.2 also emit Markdown with stronger layout fidelity.)

### A.5 Cloud document-AI services (paid, hosted)

Highest structural fidelity (true row/column spans, merged cells, reading order) and handle
**scanned** input — but documents leave your environment, and output is a vendor JSON schema.

| Service | Vendor | Strength / what it preserves | Notes |
|---------|--------|------------------------------|-------|
| [Azure AI Document Intelligence — Layout](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-layout) | Microsoft | Rows/cols, `rowSpan`/`columnSpan`, `columnHeader`, bordered/borderless/rotated tables; reading order | multi-page tables not auto-stitched |
| [Amazon Textract](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html) | AWS | Cells, merged cells, headers, table type; separate `LAYOUT` feature for reading order; export to CSV | Tables and Forms billed as separate features |
| [Google Document AI — Layout Parser](https://cloud.google.com/document-ai/docs/processors-list) | Google | Text, tables, lists + **RAG-ready chunks**; PDF/HTML/DOCX/PPTX/XLSX | sync requests ≤10 pages (else batch) |
| [Adobe PDF Extract API](https://developer.adobe.com/document-services/docs/overview/pdf-extract-api/) | Adobe | Native + scanned; per-cell content + multi-row/col span detection; reading order | JSON + CSV/XLSX + table PNGs |
| [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/overview) | LlamaIndex | "layout-aware OCR" for multi-column layouts, merged cells, charts | **hosted-only**; capability claims are vendor copy, not independently benchmarked here |

### PDF — quick decision guide

- **Clean single-column, prototyping** → pypdf / pdfplumber (§A.1).
- **Tables in text-based PDFs** → Camelot or pdfplumber `extract_table` (§A.3).
- **Complex/heterogeneous corpus, open-source, clean license** → **Docling** (MIT) or
  **unstructured** (Apache-2.0) (§A.2).
- **Best open-source quality but you're a high-revenue company** → mind Marker/Surya's
  weight-license caps; prefer Docling/unstructured.
- **Scanned input or you need max table fidelity and can use the cloud** → the §A.5 services.
- **Scientific papers** → GROBID (structure) or Nougat (math/LaTeX).

---

## B. OCR (scanned / image documents → text)

OCR is the **mandatory first stage** for any image-only source: it turns pixels into
characters before any parsing (§A) can run, and it introduces its own error layer.

### B.1 Open-source OCR engines (ordered by stars)

| Tool | Maintainer | Strength / capability | Output | License |
|------|-----------|------------------------|--------|---------|
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | PaddlePaddle (Baidu) | OCR + layout + table (PP-Structure); **100+ languages**; "turn any PDF or image into structured data" | structured data / JSON | Apache-2.0 |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | tesseract-ocr org | The classic LSTM OCR engine; "**more than 100 languages** out of the box"; page-segmentation modes | plain text, hOCR, PDF, TSV, ALTO, PAGE | Apache-2.0 |
| [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | J. Barlow | "adds an OCR text layer to scanned PDFs"; deskew/clean; **wraps Tesseract** (100+ langs) | searchable PDF/A (+ sidecar text) | MPL-2.0 |
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Jaided AI | DL OCR, "**80+ languages**" incl. Latin/Chinese/Arabic/Devanagari/Cyrillic | list of (bbox, text, confidence) | Apache-2.0 |
| [Surya](https://github.com/datalab-to/surya) | Datalab | Multilingual OCR (~91 langs) **+ layout + reading order + tables** | JSON (reading order, html tables, polygons) | Apache-2.0 code; **weights may carry commercial terms** |
| [docTR](https://github.com/mindee/doctr) | Mindee | Two-stage detection + recognition; pages→blocks→lines→words with boxes | structured JSON | Apache-2.0 |
| [Kraken](https://github.com/mittagessen/kraken) | B. Kiessling | "turn-key OCR optimized for **historical and non-Latin script**"; trainable layout + reading order; RTL/BiDi; HTR | ALTO, PageXML, abbyyXML, hOCR | Apache-2.0 |
| [TrOCR](https://huggingface.co/docs/transformers/en/model_doc/trocr) | Microsoft | Transformer **recognition only** (printed + handwritten checkpoints); **no detection/layout** — pair with a detector | decoded text | MIT (unilm) *(per-checkpoint weights vary)* |

*Star caveats (flagged):* **Kraken**'s GitHub is a mirror (primary hosting is off-GitHub),
so its star count understates real adoption — don't rank it purely on that. **TrOCR** is a
model inside the multi-model `microsoft/unilm` monorepo + HF Transformers, not a standalone
project, so it is not star-rankable; it is listed last for that reason, not by popularity.

*Honest limits:* Tesseract is weak on handwriting and noisy scans (needs clean, deskewed
input); EasyOCR/docTR give boxes+text but not rich document layout (docTR is Latin-centric);
Surya is GPU-oriented; OCRmyPDF's accuracy *is* Tesseract's (it's a pipeline, not an engine).

### B.2 Cloud OCR (capability only)

| Service | Vendor | Capability |
|---------|--------|-----------|
| [Google Cloud Vision — OCR](https://cloud.google.com/vision/docs/ocr) | Google | Text detection (`TEXT_DETECTION`) and dense document OCR (`DOCUMENT_TEXT_DETECTION`); JSON with pages→blocks→words + boxes |
| [Amazon Textract — DetectDocumentText](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-detecting.html) | AWS | Plain OCR ("only the text detected") returning lines/words + geometry, independent of the tables/forms feature |
| [Azure Document Intelligence — Read](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/read) | Microsoft | "extracts **print and handwritten** text as lines and words" with polygons/confidence; searchable-PDF output |

*Verification flag:* Google Vision's `TEXT_DETECTION` vs `DOCUMENT_TEXT_DETECTION` definitions
and its handwriting claim did **not** render cleanly from the live (JS-heavy) page — OCR
capability + URL confirmed; those specifics are not verbatim-verified.

### OCR — quick decision guide

- **General-purpose, many languages, free, self-hosted** → PaddleOCR or Tesseract.
- **Just make scanned PDFs searchable** → OCRmyPDF.
- **OCR + layout + tables in one open-source pass** → Surya (or PaddleOCR's PP-Structure).
- **Historical / non-Latin / handwriting** → Kraken (or TrOCR's handwriting checkpoint + a detector).
- **Best accuracy incl. handwriting, cloud acceptable** → the §B.2 services.

---

## C. HTML parsing (web pages → clean content)

HTML has structure (tags) but is buried in boilerplate (nav, ads, cookie banners, footers).
The tasks split into four distinct categories — and a real pipeline often **chains** them:
*(render JS if needed) → extract main content → optionally convert to Markdown*. Picking the
wrong category is the common mistake (e.g. reaching for BeautifulSoup when you wanted
boilerplate removal).

### C.1 Main-content / article extraction (boilerplate removal)

Given a page, return just the article text/structure, dropping chrome.

| Tool | Maintainer | Output | License |
|------|-----------|--------|---------|
| [trafilatura](https://github.com/adbar/trafilatura) | A. Barbaresi | TXT/**Markdown**/CSV/JSON/XML/XML-TEI; paragraphs, titles, lists, **tables**, metadata | Apache-2.0 |
| [python-readability](https://github.com/buriy/python-readability) | buriy | cleaned **HTML** fragment + title (port of arc90 Readability) | Apache-2.0 |
| [newspaper4k](https://github.com/AndyTheFactory/newspaper4k) | AndyTheFactory | article object (text, authors, date, top image, keywords) | MIT |
| [goose3](https://github.com/goose3/goose3) | goose3 org | main text + main image + metadata + embedded videos | Apache-2.0 |
| [jusText](https://github.com/miso-belica/jusText) | M. Belica | paragraphs classified good/boilerplate (plain text) | BSD-2-Clause |

*Honest flags:* **trafilatura** is the current best-in-class general extractor (and uses
jusText/readability internally). **`newspaper3k` (the famous ~15k-star repo) is unmaintained
since ~2020** — its stars are legacy popularity; use **newspaper4k**. The article extractors
(newspaper/goose3) assume *news-article-shaped* pages and degrade on generic pages. None of
these render JavaScript — feed them already-fetched HTML (see §C.4 for SPAs).

### C.2 HTML → Markdown conversion

Reformat HTML into Markdown. They convert *whatever you give them* — they do **not** select
main content, so pair with §C.1 first.

| Tool | Maintainer | Output | License |
|------|-----------|--------|---------|
| [markdownify](https://github.com/matthewwithanm/python-markdownify) | matthewwithanm | Markdown (built on BeautifulSoup; tag filters) | MIT |
| [html2text](https://github.com/Alir3z4/html2text) | Alir3z4 | Markdown-valid plain text | ⚠️ **GPL-3.0** (copyleft — flag for proprietary products) |

### C.3 Low-level DOM parsing / navigation

Parse HTML into a tree *you* query (by tag/CSS/XPath). Not extractors and not fetchers — the
building blocks the higher-level tools sit on.

| Tool | Maintainer | Output | License |
|------|-----------|--------|---------|
| [lxml](https://github.com/lxml/lxml) | lxml project | ElementTree DOM; XPath + CSS; very fast (C libxml2) | BSD-3-Clause |
| [selectolax](https://github.com/rushter/selectolax) | A. Golubin | node tree; CSS selectors; very fast (C engines) | MIT |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) | L. Richardson | navigable object tree; `.get_text()` | MIT *(not on GitHub — no star rank; license per PyPI metadata, no SPDX file checked)* |

*Honest limits:* lxml needs C libs (heavier install) and is XPath/CSS-low-level; selectolax is
CSS-only (no XPath), smaller ecosystem; BeautifulSoup does no content extraction or HTTP, and
its speed depends on the backend parser you choose (`html.parser`/`lxml`/`html5lib`).

### C.4 JavaScript rendering / dynamic pages

For client-side-rendered (SPA) pages, you must run a real browser to get the DOM *before*
extracting. These **render** but do not extract content — chain into §C.1/§C.2.

| Tool | Maintainer | Output | License |
|------|-----------|--------|---------|
| [Playwright](https://github.com/microsoft/playwright) | Microsoft | rendered DOM / page HTML / screenshots (Chromium/Firefox/WebKit) | Apache-2.0 |
| [Selenium](https://github.com/SeleniumHQ/selenium) | SeleniumHQ | rendered DOM / page source via W3C WebDriver | Apache-2.0 |

*Honest limit:* both are heavyweight (download browser binaries; high CPU/RAM per page) and
overkill for static HTML; Playwright is generally faster/less flaky than Selenium's older
WebDriver model. Neither removes boilerplate.

### HTML — quick decision guide

- **Static page, want the article text** → **trafilatura** (§C.1).
- **Need Markdown for the LLM** → trafilatura (Markdown output) directly, or §C.1 extractor →
  markdownify (§C.2; avoid html2text in proprietary products — GPL).
- **You control exactly which elements to pull** → BeautifulSoup / lxml / selectolax (§C.3).
- **JavaScript-rendered SPA** → Playwright (§C.4) to render → trafilatura to extract.
- **News-article corpus with metadata** → newspaper4k or goose3 (§C.1).

---

## D. Cross-cutting decision summary

| Your input / need | Start here |
|-------------------|-----------|
| Clean single-column PDFs | pypdf / pdfplumber (§A.1) |
| PDFs full of tables (text-based) | Camelot / pdfplumber `extract_table` (§A.3) |
| Mixed, complex PDFs, open-source, clean license | Docling / unstructured (§A.2) |
| Max table fidelity / scanned, cloud OK | Azure DI / Textract / Google / Adobe (§A.5) |
| Scanned or photographed documents | OCR first (§B) → then a PDF/parse step |
| Many-language OCR, self-hosted | PaddleOCR / Tesseract (§B.1) |
| Make scanned PDFs searchable | OCRmyPDF (§B.1) |
| Static web pages → article text | trafilatura (§C.1) |
| JavaScript-heavy web pages | Playwright (§C.4) → trafilatura (§C.1) |
| Scientific papers | GROBID / Nougat (§A.2–A.3) |

---

## Verification notes (honesty ledger)

- All entries verified at their primary (repo / official docs) on **2026-06-07** via research
  subagents and the GitHub REST API (stars + SPDX license).
- **Could not be verified:** Google Vision OCR feature definitions/handwriting (JS-rendered
  page); LlamaParse capability claims are the vendor's own marketing copy, not independently
  benchmarked; cloud pricing intentionally omitted; some ML model-weight licenses (Surya,
  Nougat, TrOCR checkpoints) differ from their code license and were not each read in full —
  treat weight licensing as *needs-confirmation* before commercial use.
- **License flags to re-check before shipping:** PyMuPDF (AGPL-3.0), Marker (GPL code +
  Open-Rail-M weights, revenue cap), Surya (Open-Rail-M weights, revenue cap), html2text
  (GPL-3.0), Camelot (older versions GPLv3). pypdf's LICENSE is reported by GitHub as
  `NOASSERTION` (non-standard file; permissive/BSD) — confirm for your version.
- **Popularity/pricing drift:** star ordering and any "most-used" framing are point-in-time
  (2026-06-07) and will change. `newspaper3k`'s high star count is **legacy** — the maintained
  fork is `newspaper4k`.
- This appendix is a *catalogue*, not prescriptive endorsement. For any tool you adopt, verify
  its current behavior and license at the primary before relying on it.
