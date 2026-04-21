"""
Generate auto_defense_presentation.pptx — 20-slide thesis defense deck.
Run:    python thesis/auto/build_presentation.py
Output: thesis/auto/auto_defense_presentation.pptx
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).parent / "auto_defense_presentation.pptx"

# ── Style constants ────────────────────────────────────────────────────────
BLUE       = RGBColor(0x2E, 0x5F, 0xA3)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK       = RGBColor(0x26, 0x26, 0x26)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.50)
ML      = Inches(0.60)    # left margin
CNTW    = Inches(12.13)   # content width


# ── Core helpers ───────────────────────────────────────────────────────────

def _blank(prs: Presentation):
    """Add a blank slide (layout index 6 = Blank in Office default theme)."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def _title(slide, text: str, top=Inches(0.35)):
    """Blue bold 28pt title text box pinned to the top."""
    txb = slide.shapes.add_textbox(ML, top, CNTW, Inches(0.90))
    tf = txb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = BLUE
    return txb


def _body(slide, text: str, left, top, width, height,
          size: int = 18, bold: bool = False,
          color=None, align=PP_ALIGN.LEFT):
    """Plain body text box with word wrap."""
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color or DARK
    return txb


def _bullets(slide, items: list, left, top, width, height, size: int = 16):
    """Bulleted text box — each item gets a bullet prefix."""
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = f"•  {item}"
        run.font.name = "Calibri"
        run.font.size = Pt(size)
        run.font.color.rgb = DARK
    return txb


def _set_cell(cell, text: str, size: int = 12, bold: bool = False,
              color=None, fill=None):
    """Set table cell text + optional fill. Adds a run to the empty paragraph."""
    if fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    p = cell.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = str(text)
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color or DARK


def _table(slide, headers: list, rows: list,
           left, top, width, height,
           hdr_size: int = 13, body_size: int = 12):
    """Styled table: blue header row, alternating light-gray data rows."""
    tbl = slide.shapes.add_table(
        len(rows) + 1, len(headers), left, top, width, height
    ).table
    for c, h in enumerate(headers):
        _set_cell(tbl.cell(0, c), h,
                  size=hdr_size, bold=True, color=WHITE, fill=BLUE)
    for r, row in enumerate(rows):
        fill = LIGHT_GRAY if r % 2 == 1 else None
        for c, val in enumerate(row):
            _set_cell(tbl.cell(r + 1, c), val, size=body_size, fill=fill)
    return tbl


# ── Slide functions ────────────────────────────────────────────────────────

def slide_01_title(prs):
    """Slide 1: Title slide with thesis title and presenter info."""
    s = _blank(prs)
    txb = s.shapes.add_textbox(ML, Inches(1.40), CNTW, Inches(2.80))
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = (
        "Validating Population Stability Metrics for\n"
        "Dynamic Auto Insurance Pricing with Telematics Data"
    )
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(30)
    run.font.color.rgb = BLUE

    for label, value, top_in in [
        ("Presenter:", "LUN CHANPOLY", 4.40),
        ("Advisor:",   "HAS SOTHEA",  4.95),
        ("Date:",      "",            5.50),
    ]:
        _body(s, label, Inches(4.20), Inches(top_in), Inches(2.20), Inches(0.45),
              size=16, bold=True, color=BLUE, align=PP_ALIGN.RIGHT)
        _body(s, value, Inches(6.55), Inches(top_in), Inches(4.00), Inches(0.45),
              size=16, color=DARK)


def slide_02_agenda(prs):
    """Slide 2: Agenda slide with 6 chapters."""
    s = _blank(prs)
    _title(s, "Agenda")
    chapters = [
        ("Chapter 1", "Introduction — Why auto insurance telematics?"),
        ("Chapter 2", "Background — PSI, telematics features, prior work"),
        ("Chapter 3", "Methodology — Synthetic data & experiment design"),
        ("Chapter 4", "Results — EXP-001 through EXP-004"),
        ("Chapter 5", "Discussion — Framework & limitations"),
        ("Chapter 6", "Conclusion — Findings & future work"),
    ]
    top = Inches(1.50)
    for ch, desc in chapters:
        _body(s, ch,   ML,           top, Inches(1.80), Inches(0.50),
              size=16, bold=True, color=BLUE)
        _body(s, desc, Inches(2.55), top, Inches(9.80), Inches(0.50),
              size=16, color=DARK)
        top += Inches(0.80)


def slide_03_why_telematics(prs):
    """Slide 3: Why Auto Insurance Telematics? — Cambodia context & problem statement."""
    s = _blank(prs)
    _title(s, "Why Auto Insurance Telematics?")

    _body(s, "Cambodia Market Context",
          ML, Inches(1.35), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "4.8 million motorcycles — dense, under-insured fleet",
        "Claim frequency: 8–15% annually, highly seasonal",
        "Monsoon season (Jul–Sep): hard braking events spike 150–250%",
        "Emerging market: limited historical actuarial data",
    ], ML, Inches(1.85), CNTW, Inches(1.80), size=16)

    _body(s, "The Problem",
          ML, Inches(3.80), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Existing drift detection assumes static batch data",
        "Telematics pricing updates continuously — distributions shift every repricing cycle",
        "No established method for monitoring PSI stability under continuous repricing",
    ], ML, Inches(4.30), CNTW, Inches(1.60), size=16)


def slide_04_research_claim(prs):
    """Slide 4: Research Claim — thesis statement and scope."""
    s = _blank(prs)
    _title(s, "Research Claim")

    txb = s.shapes.add_textbox(Inches(1.20), Inches(1.60), Inches(10.93), Inches(1.60))
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = (
        "Single-metric PSI monitoring is insufficient\n"
        "for continuous dynamic auto insurance pricing."
    )
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = BLUE

    _body(s, "This thesis:",
          ML, Inches(3.50), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Identifies 3 specific PSI failure modes under dynamic pricing",
        "Demonstrates that temporal comparison strategy matters as much as metric choice",
        "Proposes a temporal multi-metric monitoring framework as the solution",
    ], ML, Inches(4.00), CNTW, Inches(1.80), size=16)


# ── Build entry point ──────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_01_title(prs)
    slide_02_agenda(prs)
    slide_03_why_telematics(prs)
    slide_04_research_claim(prs)

    prs.save(OUT)
    print(f"Saved {len(prs.slides)} slides -> {OUT}")


if __name__ == "__main__":
    build()
