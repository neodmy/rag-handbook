"""Lesson 08 — Cleaning and deduplication.

Even after Lesson 07 recovers clean, well-ordered *text* from a file, that text is
usually still not ready to index: it carries **boilerplate** (nav bars, footers,
"was this helpful?"), **inconsistent Unicode** (smart quotes, non-breaking spaces,
ligatures, the same accented letter encoded two different ways), and **duplicates**
— the same article ingested twice, or near-identical revisions of one article.

This demo shows, on a tiny fictional "Acme Cloud" help-desk corpus, the four moves
that turn parsed text into index-ready text:

  1. NORMALIZE   — make equivalent characters identical (Unicode NFKC + a few rules)
  2. CLEAN       — strip boilerplate and collapse whitespace
  3. DEDUP EXACT — drop byte-identical copies (only possible *after* normalizing)
  4. DEDUP NEAR  — drop near-identical copies that exact matching misses
                   (k-shingles + Jaccard similarity)

and then why it matters: a query whose top-3 was crowded with three copies of one
answer recovers three *distinct* answers once near-duplicates are removed.

Run from the repo root:

    uv run python -m lessons.08-cleaning-and-deduplication.demo

No LLM and no network are involved — only the Python standard library — so the
output is fully reproducible. The corpus below is invented (not a real product,
not an evaluation dataset); the Unicode quirks are written in deliberately with
explicit escape sequences so the before/after is unambiguous.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from itertools import combinations

# ----------------------------------------------------------------------
# A tiny, deliberately messy corpus. Each document is wrapped in the same
# help-center boilerplate (a nav crumb line, two rule lines, a footer) so
# the boilerplate is real and repeated, exactly as a crawler would capture
# it. The Unicode quirks (’ curly apostrophe, “/” smart
# quotes,   non-breaking space, ﬁ "fi" ligature) are written in
# on purpose. D5 is the SAME content as D1 wrapped in DIFFERENT boilerplate
# (an exact duplicate once cleaned); D2/D3/D7 are three near-identical
# revisions of the refund policy.
# ----------------------------------------------------------------------

NAV = "Acme Cloud Help Center  ›  Account\n" + "-" * 52 + "\n"
FOOT = "\n" + "-" * 52 + "\n© 2026 Acme Cloud, Inc.   Was this article helpful?  Yes / No"


# The refund article exists in three revisions (D2/D3/D7) that share every word
# except one — the number of business days. Real near-duplicates are like this:
# a revision changes a detail and leaves the rest untouched. The shared body is
# long, so one changed token barely moves the similarity — which is exactly why
# exact hashing fails to catch them and near-duplicate detection must.
def _refund(days: str) -> str:
    return (
        "Refund policy\n"
        "You can request a refund within 30 days of purchase, no questions asked. "
        "After you cancel a paid subscription, the unused portion is refunded "
        "automatically to the original payment method. Refunds for one-time "
        "purchases are issued once you contact support and confirm the order. "
        f"In all cases the money reaches your account within {days} business days. "
        "If it has not arrived by then, reply to your receipt email and our team "
        "will investigate the delay."
    )


CORPUS: dict[str, str] = {
    "D1-password": NAV
    + "Resetting your password\n"
    + "If you can’t sign in, click “Forgot password” on the login page. "
    + "We’ll email a reset link that stays valid for 60 minutes."
    + FOOT,
    "D2-refund-v1": NAV + _refund("5") + FOOT,
    "D3-refund-v2": NAV + _refund("7") + FOOT,
    "D4-cancel": NAV
    + "Canceling your subscription\n"
    + "Open Billing, choose Cancel plan, and confirm. After you cancel a paid "
    + "subscription your plan stays active until the end of the current billing "
    + "period, and the unused portion may be eligible for a refund."
    + FOOT,
    # D5: identical CONTENT to D1, but a different nav crumb and footer text.
    # The raw bytes differ (so an exact hash of the RAW text would not match);
    # after cleaning strips the boilerplate, D5 == D1 exactly.
    "D5-password-dup": "Acme Cloud Support  ›  Sign-in\n"
    + "=" * 52
    + "\n"
    + "Resetting your password\n"
    + "If you can’t sign in, click “Forgot password” on the login page. "
    + "We’ll email a reset link that stays valid for 60 minutes."
    + "\n"
    + "=" * 52
    + "\nWas this helpful?  © Acme",
    "D6-storage": NAV
    + "Storage limits\n"
    + "Storage is measured per account, not per device. "
    + "The Team plan includes 1 TB shared across all members."
    + FOOT,
    "D7-refund-v3": NAV + _refund("10") + FOOT,
}

# Lines that are pure boilerplate (chrome, not content). A transparent,
# line-based rule for the demo. In production you would use a main-content
# extractor (e.g. trafilatura/readability for HTML); the principle is the same.
BOILERPLATE = re.compile(
    r"""^(
        \s*Acme\ Cloud\ (Help\ Center|Support)\b   # nav crumb
        | [-=]{3,}\s*$                              # rule lines
        | \s*(©|\(c\))\b.*                     # copyright footer
        | .*Was\ (this\ (article\ )?)?helpful\??.*  # feedback footer
    )""",
    re.VERBOSE | re.IGNORECASE,
)


def rule(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def normalize(text: str) -> str:
    """Make *equivalent* characters identical, so later steps can compare safely.

    NFKC (Unicode Standard Annex #15) folds compatibility variants — the ﬁ
    ligature becomes 'fi', the non-breaking space   becomes a normal space —
    and recomposes accents to a single canonical code point. NFKC does *not*
    touch typographic quotes, so those need explicit rules: normalization and
    cleaning are different jobs.

    We use NFKC because for retrieval we want aggressive folding, but note it is
    *lossy*: it also flattens the fraction and superscript compatibility forms.
    NFC is the conservative default when meaning must be preserved; see the README.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("“", '"').replace("”", '"')  # smart double quotes
    text = text.replace("‘", "'").replace("’", "'")  # smart single quotes
    return text


def strip_boilerplate(text: str) -> str:
    """Drop boilerplate lines and collapse whitespace within the kept content."""
    kept = [ln for ln in text.split("\n") if ln.strip() and not BOILERPLATE.match(ln)]
    body = " ".join(kept)
    return re.sub(r"\s+", " ", body).strip()


def clean(text: str) -> str:
    """The full ingestion clean: normalize, then strip boilerplate + whitespace."""
    return strip_boilerplate(normalize(text))


def shingles(text: str, k: int = 3) -> set[tuple[str, ...]]:
    """The set of k-word shingles of `text` (Introduction to IR, §19.6)."""
    words = text.lower().split()
    if len(words) < k:
        return {tuple(words)}
    return {tuple(words[i : i + k]) for i in range(len(words) - k + 1)}


def jaccard(a: set, b: set) -> float:
    """Jaccard similarity of two sets: |A ∩ B| / |A ∪ B|."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def main() -> None:
    # ------------------------------------------------------------------
    # 1. NORMALIZE — equivalent strings must become identical strings.
    # ------------------------------------------------------------------
    rule("1. NORMALIZATION  (Unicode NFKC + quote rules)")
    # An illustrative snippet carrying every quirk at once: smart quotes, a
    # non-breaking space ( ) between "Forgot" and "password", and the "fi"
    # ligature (ﬁ) inside "reconfigure".
    raw = "click “Forgot password” to reconﬁgure your account"
    print("RAW  :", repr(raw))
    print("CLEAN:", repr(normalize(raw)))
    print("\nNFKC folded \\u00a0 (NBSP -> space) and \\ufb01 (ﬁ ligature -> 'fi');")
    print("the smart quotes \\u201c \\u201d needed explicit rules — NFKC leaves them.\n")

    print("Why normalize before comparing — the SAME word, two encodings:")
    nfc = "café"  # 'é' as one code point  U+00E9
    nfd = "café"  # 'e' + combining acute  U+0065 U+0301
    print(f"  {nfc!r} (len {len(nfc)})  ==  {nfd!r} (len {len(nfd)})  -> {nfc == nfd}")
    print(
        f"  after NFKC: {nfc == unicodedata.normalize('NFKC', nfd)}"
        "  (now they match — and would hash identically)"
    )

    # ------------------------------------------------------------------
    # 2. CLEAN — strip boilerplate. Show one document end to end.
    # ------------------------------------------------------------------
    rule("2. CLEANING  (strip boilerplate + collapse whitespace)")
    print("RAW document 'D2-refund-v1' (note the nav crumb, rule lines, footer):\n")
    print(CORPUS["D2-refund-v1"])
    print("\nCLEANED — only the content survives:\n")
    print(clean(CORPUS["D2-refund-v1"]))

    cleaned = {doc_id: clean(text) for doc_id, text in CORPUS.items()}

    # ------------------------------------------------------------------
    # 3. EXACT DEDUP — hash the cleaned text; identical copies collapse.
    #    This only works AFTER normalize+clean: D5 and D1 have different
    #    RAW bytes (different boilerplate) but identical cleaned content.
    # ------------------------------------------------------------------
    rule("3. EXACT DEDUP  (hash of cleaned text)")
    seen: dict[str, str] = {}
    exact_unique: list[str] = []
    for doc_id, text in cleaned.items():
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest in seen:
            print(f"  {doc_id:16}  EXACT DUPLICATE of {seen[digest]}  (dropped)")
        else:
            seen[digest] = doc_id
            exact_unique.append(doc_id)
            print(f"  {doc_id:16}  kept   sha256={digest[:12]}…")
    print(f"\n{len(CORPUS)} documents -> {len(exact_unique)} after exact dedup.")
    print("D5 had different boilerplate from D1 but the SAME content — caught only")
    print("because we hashed the *cleaned* text, not the raw bytes.")

    # ------------------------------------------------------------------
    # 4. NEAR-DUP DETECTION — exact hashing misses D2/D3/D7 (they differ
    #    by one number). Shingling + Jaccard catches them.
    # ------------------------------------------------------------------
    rule("4. NEAR-DUP DETECTION  (3-word shingles + Jaccard)")
    sh = {doc_id: shingles(cleaned[doc_id]) for doc_id in exact_unique}
    threshold = 0.8
    print(f"Pairwise Jaccard over 3-shingles (flagging >= {threshold}):\n")
    near_pairs: list[tuple[str, str, float]] = []
    for a, b in combinations(exact_unique, 2):
        j = jaccard(sh[a], sh[b])
        flag = "  <-- NEAR-DUPLICATE" if j >= threshold else ""
        if j > 0.1:  # only print pairs that share something, to keep it readable
            print(f"  {a:16} {b:16} J={j:.2f}{flag}")
        if j >= threshold:
            near_pairs.append((a, b, j))

    # Greedy clustering: keep the first of each near-duplicate group.
    drop: set[str] = set()
    for a, b, _ in near_pairs:
        if a not in drop:
            drop.add(b)
    final = [d for d in exact_unique if d not in drop]
    print(f"\nExact hashing alone would have KEPT all {len(exact_unique)} — they are")
    print("not byte-identical. Near-dedup drops:", ", ".join(sorted(drop)) or "(none)")
    print(f"{len(exact_unique)} -> {len(final)} after near-dedup:", ", ".join(final))

    # ------------------------------------------------------------------
    # 5. WHY IT MATTERS — top-k crowding. A lexical score stands in for
    #    Lesson 05's vector retriever (crowding happens under ANY similarity
    #    metric: duplicates are, by definition, similar to the same query).
    # ------------------------------------------------------------------
    rule("5. WHY IT MATTERS  (duplicates crowd the top-k)")
    query = "refund to my payment method in business days"
    q = set(query.lower().split())

    def score(doc_id: str) -> int:
        # how many query terms the document contains (a retriever stand-in that,
        # unlike length-penalizing Jaccard, does not punish the long refund docs)
        return len(q & set(cleaned[doc_id].lower().split()))

    def top3(pool: list[str]) -> list[tuple[str, int]]:
        return sorted(((d, score(d)) for d in pool), key=lambda x: (-x[1], x[0]))[:3]

    print(f"Query: {query!r}  ({len(q)} terms)\n")
    before = top3(exact_unique)
    after = top3(final)
    print("Top-3 BEFORE near-dedup — the 3 refund copies tie and fill every slot:")
    for d, s in before:
        print(f"    {s} query-terms  {d}")
    print("\nTop-3 AFTER near-dedup — the refund answer takes ONE slot; the other")
    print("two go to the next-ranked documents (weak matches here — but no longer")
    print("wasted on duplicate copies of the same answer):")
    for d, s in after:
        print(f"    {s} query-terms  {d}")
    print(
        f"\nDistinct documents in the top-3: {len({d.split('-')[1] for d, _ in before})}"
        f" -> {len({d.split('-')[1] for d, _ in after})}."
        "  Same k, less redundancy."
    )


if __name__ == "__main__":
    main()
