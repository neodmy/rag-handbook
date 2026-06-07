"""Generate the sample PDF used by this lesson's demo.

This is a *fixture generator*, not part of the lesson's runnable practice. It
builds ``data/acme-cloud-plans.pdf`` once with ReportLab — a fictional two-column
"plan comparison" sheet (two columns of prose plus a small pricing table). The
two-column flow and the table are deliberate: they are the structure that a naive
text dump tends to mangle, so the demo can show what layout-aware parsing recovers.

The generated PDF is committed under ``data/`` so the demo runs without ReportLab.
Re-run this only if you want to regenerate the fixture:

    uv run python -m lessons.07-document-loading-and-parsing.make_sample_pdf

The content is invented ("Acme Cloud", the running example from Lesson 05). It is
not a real product and not an evaluation dataset.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).parent / "data" / "acme-cloud-plans.pdf"

# Two columns of body prose. The left column is drawn first, then the right —
# exactly how a two-column magazine article reads. A naive extractor that walks
# the content stream can read straight across both columns and scramble the order.
LEFT_COLUMN = [
    "Choosing an Acme Cloud Plan",
    "Acme Cloud offers three subscription tiers designed for "
    "individuals, growing teams, and large organizations. Every tier "
    "includes encrypted storage, automatic backups, and access to the "
    "Acme Cloud web console.",
    "The Starter tier is intended for a single user who needs a "
    "dependable place to keep documents and photos. It includes a "
    "generous storage allowance and the full set of sharing features, "
    "but it does not include the team administration console.",
    "The Team tier adds shared workspaces, role-based permissions, and "
    "an administration console for inviting and removing members. Most "
    "small companies start here, because billing is consolidated into a "
    "single monthly invoice.",
]

RIGHT_COLUMN = [
    "Storage, Backups, and Limits",
    "Storage is measured per account, not per device, so connecting a "
    "second computer does not consume additional quota. Backups run "
    "automatically every night and are retained for thirty days on every "
    "tier.",
    "The Enterprise tier removes the per-account storage cap and replaces "
    "it with a pooled allowance shared across the whole organization. It "
    "also adds single sign-on, audit logging, and a dedicated support "
    "contact with a guaranteed response time.",
    "If you exceed your storage allowance, uploads are paused until you "
    "remove files or upgrade. Acme Cloud never deletes data automatically "
    "to enforce a limit.",
]

# The pricing table. A naive text dump tends to flatten a 2-D table into a flat
# run of cells, losing which number belongs to which plan/column.
TABLE_DATA = [
    ["Plan", "Storage", "Members", "Price / month"],
    ["Starter", "100 GB", "1", "$5"],
    ["Team", "1 TB", "Up to 25", "$40"],
    ["Enterprise", "Pooled", "Unlimited", "Custom"],
]


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    h = ParagraphStyle("h", parent=styles["Heading2"], spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["BodyText"], spaceAfter=8, leading=13)

    doc = BaseDocTemplate(
        str(OUT),
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        title="Acme Cloud Plans",
    )

    # Page 1: two side-by-side frames (the two columns).
    gap = 0.3 * inch
    col_w = (doc.width - gap) / 2
    left = Frame(doc.leftMargin, doc.bottomMargin, col_w, doc.height, id="left")
    right = Frame(
        doc.leftMargin + col_w + gap,
        doc.bottomMargin,
        col_w,
        doc.height,
        id="right",
    )
    # Page 2: a single full-width frame for the table.
    full = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="full")

    doc.addPageTemplates(
        [
            PageTemplate(id="two-col", frames=[left, right]),
            PageTemplate(id="one-col", frames=[full]),
        ]
    )

    story: list = []
    for i, para in enumerate(LEFT_COLUMN):
        story.append(Paragraph(para, h if i == 0 else body))
    story.append(FrameBreak())  # jump to the right column
    for i, para in enumerate(RIGHT_COLUMN):
        story.append(Paragraph(para, h if i == 0 else body))

    story.append(NextPageTemplate("one-col"))
    story.append(PageBreak())
    story.append(Paragraph("Plan Comparison", h))
    story.append(Spacer(1, 6))
    table = Table(TABLE_DATA, hAlign="LEFT", colWidths=[1.4 * inch] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b3a55")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef1f6")]),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(table)

    doc.build(story)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
