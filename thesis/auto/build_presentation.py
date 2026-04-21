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


# ── Build entry point ──────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # Slide functions will be added in subsequent tasks

    prs.save(OUT)
    print(f"Saved {len(prs.slides)} slides -> {OUT}")


if __name__ == "__main__":
    build()
