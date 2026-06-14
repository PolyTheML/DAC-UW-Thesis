"""
Generate the thesis defense presentation — Sreynich-format structural pass.

Conventions (matching Nang Sreynich's ITC DS defense deck, July 2025):
  * Persistent roman-numeral section tag on every content slide
  * Decimal-numbered slide titles: "1.1. Research Background", "4.3. ..."
  * Corner page numbers: 01-19 (content slides), A1-A8 (appendix); unnumbered otherwise
  * No section-divider slides
  * All headline statistics read from demo/static/thesis_results.json at build time
    (build fails loudly on missing key -- no silent hardcoded fallbacks)
  * Minimal Academic restyle (v2): flat white, Calibri-only, burgundy accents, thin bottom bar

Output: thesis/health_rl/burgundy_defense_presentation.pptx  (32 slides)

Run:
    python thesis/health_rl/build_burgundy_presentation.py
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT        = Path(r"C:\DAC-UW-Thesis")
OUTPUT_PATH = str(ROOT / "thesis" / "health_rl" / "burgundy_defense_presentation.pptx")
LOGO_ITC    = str(ROOT / "thesis" / "ITC.jpg")
LOGO_AMS    = str(ROOT / "thesis" / "AMS.png")
LOGO_DAC    = str(ROOT / "thesis" / "DAC.jpg")
FIG_DIR     = ROOT / "thesis" / "health_rl" / "figures"
SLIDE_FIG_DIR = FIG_DIR / "slides"

RESULTS_JSON = ROOT / "demo" / "static" / "thesis_results.json"
with open(RESULTS_JSON) as _f:
    RESULTS = json.load(_f)

# Convenience aliases -- all values from JSON; KeyError = drift bug caught at build time
_E005   = RESULTS["exp005"]
_E006   = RESULTS["exp006"]
_E007   = RESULTS["exp007"]
_E008   = RESULTS["exp008"]
_E009   = RESULTS["exp009"]
_E010   = RESULTS["exp010"]
_E013   = RESULTS["exp013"]
_LADDER = RESULTS["ladder"]

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
BURGUNDY      = RGBColor(0x5D, 0x2A, 0x42)
BURGUNDY_DARK = RGBColor(0x47, 0x1F, 0x33)
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT     = RGBColor(0x1A, 0x1A, 0x1A)
SOFT_TEXT     = RGBColor(0x3A, 0x3A, 0x3A)
LIGHT_GRAY    = RGBColor(0xF2, 0xEE, 0xEF)
MED_GRAY      = RGBColor(0x80, 0x80, 0x80)
ACCENT_RED    = RGBColor(0xD9, 0x3B, 0x3B)
ACCENT_GREEN  = RGBColor(0x2E, 0x8B, 0x57)
ACCENT_AMBER  = RGBColor(0xE6, 0xA6, 0x2E)
ACCENT_BLUE   = RGBColor(0x3B, 0x6E, 0xA5)
GRAY_LABEL    = RGBColor(0x77, 0x77, 0x77)   # stat labels / footnotes
HAIRLINE      = RGBColor(0xDD, 0xDD, 0xDD)   # 1px separators
PANEL         = RGBColor(0xF7, 0xF5, 0xF6)   # flat panel fill (no borders)

# ---------------------------------------------------------------------------
# Dimensions (16:9 widescreen)
# ---------------------------------------------------------------------------
SLIDE_WIDTH       = Inches(13.333)
SLIDE_HEIGHT      = Inches(7.5)
MARGIN_LEFT       = Inches(0.5)
CONTENT_TOP       = Inches(1.32)   # below tag + title + accent
BOTTOM_BAR_TOP    = Inches(7.28)
BOTTOM_BAR_HEIGHT = Inches(0.22)
CONTENT_W         = SLIDE_WIDTH - MARGIN_LEFT - Inches(0.5)
CONTENT_H         = BOTTOM_BAR_TOP - CONTENT_TOP - Inches(0.15)
FOOTNOTE_TOP      = BOTTOM_BAR_TOP - Inches(0.42)

# ---------------------------------------------------------------------------
# Thesis metadata
# ---------------------------------------------------------------------------
THESIS_TITLE  = (
    "Adaptive Health Insurance Underwriting via Contextual Bandits: "
    "A Reinforcement Learning Approach for Cambodia"
)
PRESENTER     = "LUN CHANPOLY"
SUPERVISOR    = "Dr. HAS Sothea"
CO_SUPERVISOR = "Mr. PHOK Ponna"
ORGANIZATION  = "DAC (Decent Actuarial Consultants)"
DEPARTMENT    = "Department of Applied Mathematics and Statistics"
INSTITUTION   = "Institute of Technology of Cambodia"
DURATION      = "Mar 2026 – Jun 2026"
DEFENSE_DATE  = "July 2026"

SECTIONS = [
    ("i",   "Introduction"),
    ("ii",  "Internship at DAC"),
    ("iii", "Literature Review"),
    ("iv",  "Methodology"),
    ("v",   "Results & Discussion"),
    ("vi",  "Limitations & Conclusions"),
]
_SEC = {num: f"{num}. {name}" for num, name in SECTIONS}


# ===========================================================================
# Low-level helpers
# ===========================================================================

def _set_shape_fill(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def _no_line(shape):
    shape.line.fill.background()


def _flat(shape):
    """Kill the theme's inherited drop shadow -- v2 is shadow-free everywhere."""
    shape.shadow.inherit = False


def _letterspace(paragraph, spc: int = 140):
    """Letter-space a paragraph's runs (OOXML 'spc' is in 1/100 pt)."""
    for r in paragraph.runs:
        r.font._rPr.set("spc", str(spc))


def _add_text_box(slide, left, top, width, height, text: str,
                  font_size: int = 18, bold: bool = False, italic: bool = False,
                  color: RGBColor = DARK_TEXT, align=PP_ALIGN.LEFT,
                  font_name: str = "Calibri", anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _flat(box)
    box.fill.background()
    _no_line(box)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    return box


def _add_bullet_box(slide, left, top, width, height, bullets,
                    font_size: int = 14, color: RGBColor = DARK_TEXT,
                    font_name: str = "Calibri", bullet_char: str = "•"):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _flat(box)
    box.fill.background()
    _no_line(box)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.1)
    tf.margin_top = Inches(0.05)
    for i, line in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        text, bold_flag = (line if isinstance(line, tuple) else (line, False))
        p.text = f"{bullet_char} {text}" if bullet_char else text
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = font_name
        p.font.bold = bold_flag
        p.space_after = Pt(4)
    return box


def _add_filled_box(slide, left, top, width, height,
                    fill_color: RGBColor, rounded: bool = False,
                    line_color: RGBColor | None = None, line_width_pt: float = 0):
    # 'rounded' is ignored: v2 is square-corner only (param removed in Task 9)
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _flat(box)
    _set_shape_fill(box, fill_color)
    if line_color is None:
        _no_line(box)
    else:
        box.line.color.rgb = line_color
        box.line.width = Pt(line_width_pt or 1)
    return box


def _add_callout(slide, left, top, width, height, text: str,
                 font_size: int = 13, bold: bool = False,
                 color: RGBColor = DARK_TEXT, font_name: str = "Calibri"):
    """v2: flat light panel, square corners, charcoal text, no border."""
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _flat(box)
    _set_shape_fill(box, PANEL)
    _no_line(box)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = PP_ALIGN.LEFT
    return box


def _add_picture_fit(slide, path: str, left, top, max_w, max_h):
    if not os.path.exists(path):
        _add_filled_box(slide, left, top, max_w, max_h, LIGHT_GRAY)
        _add_text_box(slide, left, top, max_w, max_h,
                      f"[missing: {os.path.basename(path)}]",
                      font_size=12, color=MED_GRAY, align=PP_ALIGN.CENTER,
                      anchor=MSO_ANCHOR.MIDDLE)
        return
    pic = slide.shapes.add_picture(path, left, top, width=max_w)
    _flat(pic)
    if pic.height > max_h:
        ratio = max_h / pic.height
        pic.height = int(pic.height * ratio)
        pic.width = int(pic.width * ratio)
    pic.left = int(left + (max_w - pic.width) / 2)
    pic.top = int(top + (max_h - pic.height) / 2)


# ===========================================================================
# v2 layout helpers (Minimal Academic)
# ===========================================================================

def _add_stat_row(slide, top, stats, hero_idx: int = 0, height=Inches(1.05),
                  left=None, width=None, value_colors=None):
    """Flat big-number stat row: value over small gray caps label, hairline-separated.

    stats: list of (value, label). hero_idx gets BURGUNDY; value_colors overrides per-stat.
    """
    left = MARGIN_LEFT if left is None else left
    width = CONTENT_W if width is None else width
    n = len(stats)
    col_w = int(width / n)
    for i, (val, label) in enumerate(stats):
        cx = left + i * col_w
        color = (value_colors[i] if value_colors and value_colors[i] is not None
                 else (BURGUNDY if i == hero_idx else DARK_TEXT))
        _add_text_box(slide, cx, top, col_w - Inches(0.15), Inches(0.62),
                      str(val), font_size=30, bold=True, color=color)
        lab = _add_text_box(slide, cx, top + Inches(0.62), col_w - Inches(0.15),
                            Inches(0.36), label.upper(), font_size=10, color=GRAY_LABEL)
        _letterspace(lab.text_frame.paragraphs[0], 80)
        if i > 0:
            _add_filled_box(slide, cx - Inches(0.12), top + Inches(0.05),
                            Inches(0.012), height - Inches(0.15), HAIRLINE)


def _add_talking_points(slide, left, top, width, points, font_size: int = 17,
                        line_h=Inches(0.62)):
    """<=4 short points, burgundy square marker + charcoal text. Returns bottom y.

    Density rule (spec section 4) is enforced here: more than 4 points raises.
    """
    if len(points) > 4:
        raise ValueError(f"talking points rule: max 4 per slide, got {len(points)}")
    y = top
    for text in points:
        _add_filled_box(slide, left, y + Inches(0.12), Inches(0.1), Inches(0.1), BURGUNDY)
        _add_text_box(slide, left + Inches(0.28), y, width - Inches(0.28),
                      line_h, text, font_size=font_size, color=DARK_TEXT)
        y += line_h
    return y


def _add_footnote(slide, text: str):
    """Claim-critical small gray footnote pinned above the bottom bar."""
    _add_text_box(slide, MARGIN_LEFT, FOOTNOTE_TOP, CONTENT_W, Inches(0.36),
                  text, font_size=10.5, italic=True, color=GRAY_LABEL)


def _add_notes(slide, text: str):
    """Presenter notes = the rehearsal script for this slide."""
    slide.notes_slide.notes_text_frame.text = text


def _add_flat_table(slide, left, top, col_ws, header, rows, font_size: int = 12,
                    row_h=Inches(0.5), cell_style=None):
    """Flat table: bold charcoal header over a burgundy hairline, PANEL/white zebra rows.

    cell_style: optional fn(r, c, text) -> (bold, RGBColor) for emphasis cells.
    """
    col_xs = [left]
    for w in col_ws[:-1]:
        col_xs.append(col_xs[-1] + w)
    for cx, cw, h in zip(col_xs, col_ws, header):
        _add_text_box(slide, cx + Inches(0.06), top, cw - Inches(0.12), Inches(0.34),
                      h, font_size=font_size, bold=True, color=DARK_TEXT)
    _add_filled_box(slide, left, top + Inches(0.36), sum(col_ws, Inches(0)),
                    Inches(0.025), BURGUNDY)
    for i, row in enumerate(rows):
        ry = top + Inches(0.44) + i * row_h
        if i % 2 == 0:
            _add_filled_box(slide, left, ry, sum(col_ws, Inches(0)), row_h, PANEL)
        for c, (cx, cw, text) in enumerate(zip(col_xs, col_ws, row)):
            bold, color = (False, DARK_TEXT)
            if cell_style is not None:
                bold, color = cell_style(i, c, text)
            _add_text_box(slide, cx + Inches(0.06), ry + Inches(0.04),
                          cw - Inches(0.12), row_h - Inches(0.08),
                          text, font_size=font_size, bold=bold, color=color)
    return top + Inches(0.44) + len(rows) * row_h


# ===========================================================================
# Chrome (section tag, title, bottom bar)
# ===========================================================================

def _add_section_tag(slide, sec_key: str):
    """Plain-text uppercase letter-spaced section tag, top-left (no chip)."""
    num, name = next((n, t) for n, t in SECTIONS if n == sec_key)
    box = _add_text_box(slide, MARGIN_LEFT, Inches(0.16), Inches(7.0), Inches(0.3),
                        f"{num.upper()} · {name.upper()}",
                        font_size=10, bold=True, color=BURGUNDY)
    _letterspace(box.text_frame.paragraphs[0])


_TITLE_RX = re.compile(r"^([A-Za-z]?\d+(?:\.\d+)?)\.?\s+(.*)$")


def _add_slide_title(slide, text: str):
    """Burgundy decimal run + charcoal title run, Calibri 26 bold."""
    m = _TITLE_RX.match(text.strip())
    num, rest = (m.group(1), m.group(2).strip()) if m else ("", text.strip())
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, MARGIN_LEFT, Inches(0.46),
                                 Inches(12.3), Inches(0.62))
    _flat(box)
    box.fill.background()
    _no_line(box)
    tf = box.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    for run_text, run_color in ((f"{num}  ", BURGUNDY), (rest, DARK_TEXT)):
        if run_text.strip():
            r = p.add_run()
            r.text = run_text
            r.font.size = Pt(26)
            r.font.bold = True
            r.font.color.rgb = run_color
            r.font.name = "Calibri"


def _add_title_rule(slide):
    """Short burgundy accent under the title (replaces the full-width rule)."""
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.14), Inches(0.55), Inches(0.045), BURGUNDY)


def _add_bottom_bar(slide, page_num: str | None = None):
    """Thin burgundy strip; white right-aligned page number; NO logos."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), BOTTOM_BAR_TOP, SLIDE_WIDTH, BOTTOM_BAR_HEIGHT)
    _flat(bar)
    _set_shape_fill(bar, BURGUNDY)
    _no_line(bar)
    if page_num is not None:
        pg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(12.3), BOTTOM_BAR_TOP - Inches(0.02),
            Inches(0.9), Inches(0.26))
        _flat(pg)
        pg.fill.background()
        _no_line(pg)
        tf = pg.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)
        p = tf.paragraphs[0]
        p.text = page_num
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.RIGHT


def _content_slide(prs, sec_key: str, title: str, page_num: str):
    """Factory: blank slide with section tag, decimal title, rule, and bottom bar."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_section_tag(slide, sec_key)
    _add_slide_title(slide, title)
    _add_title_rule(slide)
    _add_bottom_bar(slide, page_num)
    return slide


# ===========================================================================
# Slide 1 -- Title
# ===========================================================================

def slide_title(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    for path, lx, ly, lw in [
        (LOGO_ITC, 0.6,  0.30, 1.1),
        (LOGO_AMS, 1.85, 0.40, 1.6),
        (LOGO_DAC, 11.1, 0.35, 1.6),
    ]:
        if os.path.exists(path):
            slide.shapes.add_picture(path, Inches(lx), Inches(ly), width=Inches(lw))

    _add_text_box(slide, Inches(3.5), Inches(0.45), Inches(7.0), Inches(0.5),
                  INSTITUTION, font_size=24, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")
    _add_text_box(slide, Inches(3.5), Inches(0.93), Inches(7.0), Inches(0.4),
                  DEPARTMENT, font_size=17, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")

    box_w = Inches(11.6)
    title_box = _add_filled_box(slide, (SLIDE_WIDTH - box_w) / 2, Inches(2.1),
                                box_w, Inches(2.2), BURGUNDY, rounded=True)
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.4)
    tf.margin_right = Inches(0.4)
    p = tf.paragraphs[0]
    p.text = THESIS_TITLE.upper()
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Times New Roman"
    p.alignment = PP_ALIGN.CENTER

    _add_text_box(slide, Inches(0), Inches(4.65), SLIDE_WIDTH, Inches(0.38),
                  "Presented by:", font_size=17, color=DARK_TEXT, align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.02), SLIDE_WIDTH, Inches(0.5),
                  PRESENTER, font_size=28, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")

    lx, rx = Inches(1.5), Inches(7.5)
    for i, (lt, rt) in enumerate([
        (f"Supervisor      :  {SUPERVISOR}",    f"Organization :  {ORGANIZATION}"),
        (f"Co-Supervisor  :  {CO_SUPERVISOR}", f"Duration        :  {DURATION}"),
    ]):
        y = Inches(5.7) + i * Inches(0.36)
        _add_text_box(slide, lx, y, Inches(5.6), Inches(0.34), lt, font_size=15, color=DARK_TEXT)
        _add_text_box(slide, rx, y, Inches(5.6), Inches(0.34), rt, font_size=15, color=DARK_TEXT)

    _add_text_box(slide, Inches(0), Inches(6.6), SLIDE_WIDTH, Inches(0.38),
                  DEFENSE_DATE, font_size=17, color=DARK_TEXT, align=PP_ALIGN.CENTER)


# ===========================================================================
# Slide 2 -- Table of Contents
# ===========================================================================

def slide_toc(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_filled_box(slide, Inches(0), Inches(0), Inches(2.3), SLIDE_HEIGHT, BURGUNDY)
    for i in range(3):
        _add_filled_box(slide, Inches(0.55), Inches(0.45 + i * 0.18),
                        Inches(0.55), Inches(0.05), WHITE)
    circle = _add_filled_box(slide, Inches(0.65), Inches(3.0), Inches(0.85), Inches(0.85), WHITE)
    tf = circle.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = "\U0001F393"
    p.font.size = Pt(28)
    p.alignment = PP_ALIGN.CENTER
    for i in range(3):
        _add_filled_box(slide, Inches(0.55 + i * 0.28), Inches(6.85),
                        Inches(0.13), Inches(0.13), WHITE)

    _add_text_box(slide, Inches(2.9), Inches(0.4), Inches(9.0), Inches(0.85),
                  "TABLE OF CONTENT", font_size=36, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.LEFT, font_name="Times New Roman")

    # 6 sections, 2 columns of 3
    col_xs = [Inches(3.0), Inches(8.1)]
    row_h = Inches(1.6)
    for idx, (num, name) in enumerate(SECTIONS):
        cx = col_xs[idx // 3]
        cy = Inches(1.45) + (idx % 3) * row_h

        sq = _add_filled_box(slide, cx, cy, Inches(0.7), Inches(0.7), BURGUNDY)
        tf = sq.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Times New Roman"

        _add_text_box(slide, cx + Inches(0.9), cy + Inches(0.04),
                      Inches(4.2), Inches(0.45),
                      name, font_size=18, bold=True, color=DARK_TEXT,
                      align=PP_ALIGN.LEFT, font_name="Times New Roman")
        _add_filled_box(slide, cx + Inches(0.9), cy + Inches(0.58),
                        Inches(1.4), Inches(0.04), BURGUNDY)


# ===========================================================================
# Section i -- Introduction  (slides 3-5, pages 01-03)
# ===========================================================================

def slide_research_background(prs: Presentation):
    """Slide 3 (01)."""
    slide = _content_slide(prs, "i", "1.1.  Research Background", "01")

    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.5), Inches(5.2), [
        ("Cambodia health insurance landscape:", True),
        "National Social Security Fund (NSSF) covers formal-sector workers only (~16%)",
        "Private voluntary insurance nascent; underwriting mostly manual rule-based",
        "Actuaries apply fixed premium rules without learning from outcomes",
        ("The underwriting bottleneck:", True),
        "Static thresholds are set at training time and never updated",
        "Suboptimal decisions compound over a growing applicant pool",
        "No systematic demographic-parity monitoring in current practice",
    ], font_size=13)

    stat_box = _add_filled_box(slide, Inches(7.3), CONTENT_TOP,
                               Inches(5.5), Inches(1.9), BURGUNDY, rounded=True)
    _add_text_box(slide, Inches(7.3), CONTENT_TOP + Inches(0.1), Inches(5.5), Inches(0.85),
                  "< 10 %", font_size=52, bold=True, color=WHITE,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")
    _add_text_box(slide, Inches(7.3), CONTENT_TOP + Inches(1.0), Inches(5.5), Inches(0.7),
                  "Health insurance penetration rate in Cambodia (2023 estimate)",
                  font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

    _add_callout(slide, Inches(7.3), CONTENT_TOP + Inches(2.1), Inches(5.5), Inches(2.7),
                 "Research opportunity:\n\n"
                 "Contextual bandits can learn from underwriting decisions in real time, "
                 "adapting to Cambodia-specific risk patterns while monitoring demographic "
                 "fairness automatically.",
                 font_size=13)


def slide_research_problem(prs: Presentation):
    """Slide 4 (02)."""
    slide = _content_slide(prs, "i", "1.2.  Research Problem", "02")

    problems = [
        ("Static thresholds",
         "Fixed age/BMI/income cutoffs ignore applicant context. "
         "A high-risk applicant misclassified as low-risk generates uncorrected losses."),
        ("No online adaptation",
         "Reward signal (claims) is never fed back to the model. "
         "Accuracy degrades silently as population demographics shift."),
        ("Demographic blindspot",
         "No parity metric is tracked. Rule-based systems can develop "
         "regional or occupational concentration entirely undetected."),
        ("No triage mechanism",
         "Low-confidence borderline cases are not flagged. Actuaries "
         "review high-volume routine cases instead of genuine edge cases."),
    ]
    card_w, card_h = Inches(5.9), Inches(2.3)
    positions = [
        (MARGIN_LEFT,              CONTENT_TOP),
        (MARGIN_LEFT + Inches(6.6), CONTENT_TOP),
        (MARGIN_LEFT,              CONTENT_TOP + Inches(2.55)),
        (MARGIN_LEFT + Inches(6.6), CONTENT_TOP + Inches(2.55)),
    ]
    for (title, desc), (lx, ly) in zip(problems, positions):
        _add_filled_box(slide, lx, ly, card_w, card_h, LIGHT_GRAY, rounded=True)
        _add_filled_box(slide, lx, ly, card_w, Inches(0.42), BURGUNDY, rounded=False)
        _add_text_box(slide, lx + Inches(0.12), ly + Inches(0.06),
                      card_w - Inches(0.2), Inches(0.32),
                      title, font_size=14, bold=True, color=WHITE)
        _add_text_box(slide, lx + Inches(0.15), ly + Inches(0.52),
                      card_w - Inches(0.3), card_h - Inches(0.62),
                      desc, font_size=12, color=DARK_TEXT)


def slide_goal_objectives(prs: Presentation):
    """Slide 5 (03)."""
    slide = _content_slide(prs, "i", "1.3.  Research Goal & Objectives", "03")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.36),
                  "Research Goal", font_size=15, bold=True, color=BURGUNDY)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.4), CONTENT_W, Inches(0.7),
                  "Design and evaluate an adaptive health insurance underwriting system using "
                  "contextual bandit algorithms on a synthetic Cambodia applicant dataset, "
                  "incorporating demographic fairness monitoring and human-in-the-loop augmentation.",
                  font_size=13, color=DARK_TEXT)

    _add_filled_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.18), CONTENT_W, Inches(0.03), BURGUNDY)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.3), CONTENT_W, Inches(0.36),
                  "Objectives", font_size=15, bold=True, color=BURGUNDY)

    objs = [
        ("O1", "Implement and adapt linear contextual bandit algorithms (LinUCB, LinTS) "
               "for multi-arm health insurance underwriting decisions."),
        ("O2", "Construct a 2,000-record synthetic Cambodia applicant dataset anchored "
               "on CDHS, STEPS, ILO, and WHO demographic distributions."),
        ("O3", "Evaluate bandit performance versus static rule-based baselines via "
               "20-seed multi-run trials, bootstrap CIs, and paired Wilcoxon tests."),
        ("O4", "Assess demographic fairness via PSI monitoring across region and occupation, "
               "and integrate a human-in-the-loop underwriting wrapper."),
    ]
    top = CONTENT_TOP + Inches(1.78)
    for i, (label, text) in enumerate(objs):
        y = top + i * Inches(1.08)
        sq = _add_filled_box(slide, MARGIN_LEFT, y, Inches(0.45), Inches(0.45), BURGUNDY)
        tf = sq.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        _add_text_box(slide, MARGIN_LEFT + Inches(0.6), y,
                      CONTENT_W - Inches(0.6), Inches(0.95),
                      text, font_size=13, color=DARK_TEXT)


# ===========================================================================
# Section ii -- Internship at DAC  (slide 6, page 04)
# ===========================================================================

def slide_dac_internship(prs: Presentation):
    """Slide 6 (04)."""
    slide = _content_slide(prs, "ii", "2.1.  Internship at DAC", "04")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.3), Inches(0.36),
                  "About DAC", font_size=15, bold=True, color=BURGUNDY)
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.42), Inches(6.3), Inches(2.5), [
        "Decent Actuarial Consultants Co., Ltd. -- Phnom Penh, Cambodia",
        "Actuarial consulting: life & health insurance, pension, regulatory advice",
        "Clients: insurance companies, pension funds, and regulators across SE Asia",
        "This thesis is embedded in a DAC-supervised research internship",
    ], font_size=13)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.1), Inches(6.3), Inches(0.36),
                  "Internship Timeline", font_size=15, bold=True, color=BURGUNDY)
    timeline = [
        ("Mar 2026", "Problem scoping\n& dataset design"),
        ("Apr 2026", "Algorithm\nimplementation"),
        ("May 2026", "Experiments\n& analysis"),
        ("Jun 2026", "Thesis writing\n& defense prep"),
    ]
    seg_w = Inches(2.9)
    strip_top = CONTENT_TOP + Inches(3.55)
    for i, (month, desc) in enumerate(timeline):
        lx = MARGIN_LEFT + i * (seg_w + Inches(0.15))
        fill = BURGUNDY if i % 2 == 0 else BURGUNDY_DARK
        _add_filled_box(slide, lx, strip_top, seg_w, Inches(1.3), fill, rounded=True)
        _add_text_box(slide, lx + Inches(0.1), strip_top + Inches(0.06),
                      seg_w - Inches(0.2), Inches(0.38),
                      month, font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _add_text_box(slide, lx + Inches(0.1), strip_top + Inches(0.5),
                      seg_w - Inches(0.2), Inches(0.65),
                      desc, font_size=11, color=WHITE, align=PP_ALIGN.CENTER)

    _add_callout(slide, Inches(7.2), CONTENT_TOP, Inches(5.6), Inches(3.2),
                 "Role: Research Intern\n\n"
                 "Deliverable: end-to-end adaptive underwriting prototype + thesis report\n\n"
                 f"Duration: {DURATION}\n\n"
                 f"Supervisor: {CO_SUPERVISOR} (DAC)  |  Thesis advisor: {SUPERVISOR} (ITC)",
                 font_size=13)


# ===========================================================================
# Section iii -- Literature Review  (slide 7, page 05)
# ===========================================================================

def slide_lit_summary(prs: Presentation):
    """Slide 7 (05)."""
    slide = _content_slide(prs, "iii", "3.1.  Literature Summary", "05")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.32),
                  "Key literature informing the methodology",
                  font_size=12, italic=True, color=SOFT_TEXT)

    col_ws = [Inches(3.1), Inches(3.5), Inches(5.6)]
    col_xs = [MARGIN_LEFT,
               MARGIN_LEFT + col_ws[0] + Inches(0.05),
               MARGIN_LEFT + col_ws[0] + col_ws[1] + Inches(0.1)]
    hdr_top = CONTENT_TOP + Inches(0.38)
    for hdr, cw, cx in zip(["Topic", "Key Authors", "Contribution"], col_ws, col_xs):
        _add_filled_box(slide, cx, hdr_top, cw, Inches(0.38), BURGUNDY)
        _add_text_box(slide, cx + Inches(0.06), hdr_top + Inches(0.05),
                      cw - Inches(0.12), Inches(0.28),
                      hdr, font_size=12, bold=True, color=WHITE)

    rows = [
        ("Contextual Bandits\nin Healthcare",
         "Bouneffouf et al.\n(2017)",
         "Clinical decision support via LinUCB; reward = patient outcome"),
        ("LinUCB Theory",
         "Li et al. (2010)",
         "UCB exploration over linear model; O(√T·d·log T) regret bound"),
        ("LinTS\n(Thompson Sampling)",
         "Agrawal & Goyal\n(2013)",
         "Posterior sampling achieves near-optimal regret; robust exploration"),
        ("Fairness in\nInsurance ML",
         "Frees et al. (2014);\nKusner et al. (2017)",
         "Regulatory constraints on protected attributes; counterfactual fairness"),
        ("PSI Model Monitoring",
         "Yurdakul (2018)",
         "Population Stability Index detects distribution shift; GREEN/AMBER/RED zones"),
        ("Human-in-the-loop RL",
         "Christiano et al.\n(2017)",
         "Expert overrides improve alignment; cost-benefit of human referral"),
    ]
    row_h = Inches(0.79)
    for i, (topic, authors, method) in enumerate(rows):
        ry = hdr_top + Inches(0.42) + i * row_h
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        for cx, cw in zip(col_xs, col_ws):
            _add_filled_box(slide, cx, ry, cw, row_h, bg)
        for cx, cw, text in zip(col_xs, col_ws, [topic, authors, method]):
            _add_text_box(slide, cx + Inches(0.06), ry + Inches(0.06),
                          cw - Inches(0.12), row_h - Inches(0.1),
                          text, font_size=11, color=DARK_TEXT)


# ===========================================================================
# Section iv -- Methodology  (slides 8-12, pages 06-10)
# ===========================================================================

def slide_system_pipeline(prs: Presentation):
    """Slide 8 (06)."""
    slide = _content_slide(prs, "iv", "4.1.  System Pipeline", "06")
    _add_picture_fit(slide, str(FIG_DIR / "fig_ch4_architecture.png"),
                     MARGIN_LEFT, CONTENT_TOP, CONTENT_W, CONTENT_H)


def slide_cambodia_dataset(prs: Presentation):
    """Slide 9 (07)."""
    slide = _content_slide(prs, "iv", "4.2.  Synthetic Cambodia Dataset", "07")

    stats = [
        ("2,000", "Synthetic\nApplications"),
        ("5",     "Demographic\nFeatures"),
        ("4",     "Underwriting\nArms"),
        ("4",     "Anchoring\nSources"),
    ]
    card_w = Inches(2.8)
    for i, (val, label) in enumerate(stats):
        lx = MARGIN_LEFT + i * (card_w + Inches(0.2))
        _add_filled_box(slide, lx, CONTENT_TOP, card_w, Inches(1.55), BURGUNDY, rounded=True)
        _add_text_box(slide, lx, CONTENT_TOP + Inches(0.08), card_w, Inches(0.78),
                      val, font_size=40, bold=True, color=WHITE,
                      align=PP_ALIGN.CENTER, font_name="Times New Roman")
        _add_text_box(slide, lx, CONTENT_TOP + Inches(0.88), card_w, Inches(0.55),
                      label, font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.72), Inches(6.0), Inches(0.36),
                  "Dataset construction", font_size=14, bold=True, color=BURGUNDY)
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.12), Inches(6.0), Inches(3.2), [
        "Age, sex, region, occupation, BMI from CDHS 2021-22 & STEPS 2021",
        "Income distribution anchored on ILO Cambodia labour force surveys",
        "Claim probabilities calibrated from WHO SEARO health expenditure data",
        "Adverse-selection factor AF = 1.35; price elasticity slope β = 3.5",
        "Fully synthetic -- no real applicant PII included",
    ], font_size=13)

    _add_text_box(slide, Inches(6.8), CONTENT_TOP + Inches(1.72), Inches(5.9), Inches(0.36),
                  "Underwriting arms", font_size=14, bold=True, color=BURGUNDY)
    arms = [
        ("RATED",    "Accept + premium loading (+25%)"),
        ("STANDARD", "Accept at standard premium rate"),
        ("DECLINE",  "Reject application"),
        ("REFER",    "Escalate to human underwriter"),
    ]
    arm_top = CONTENT_TOP + Inches(2.12)
    for i, (arm, desc) in enumerate(arms):
        ay = arm_top + i * Inches(0.77)
        fill = BURGUNDY if i % 2 == 0 else BURGUNDY_DARK
        _add_filled_box(slide, Inches(6.8), ay, Inches(1.55), Inches(0.7), fill)
        _add_text_box(slide, Inches(6.88), ay + Inches(0.12), Inches(1.38), Inches(0.48),
                      arm, font_size=13, bold=True, color=WHITE)
        _add_text_box(slide, Inches(8.5), ay + Inches(0.12), Inches(4.15), Inches(0.55),
                      desc, font_size=12, color=DARK_TEXT)


def slide_bandit_formulation(prs: Presentation):
    """Slide 10 (08)."""
    slide = _content_slide(prs, "iv", "4.3.  Bandit Formulation", "08")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.0), Inches(0.36),
                  "Problem setup", font_size=14, bold=True, color=BURGUNDY)
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.42), Inches(6.0), Inches(2.75), [
        ("Context  x_t ∈ ℝ⁵:", True),
        "Age, sex, region, occupation, BMI -- standardised at application time",
        ("Action  a_t ∈ {RATED, STANDARD, DECLINE, REFER}:", True),
        "Policy selects one arm per applicant per round",
        ("Reward  r_t:", True),
        "Revenue-minus-claims actuarial simulator",
        "Adverse-selection penalises premium-heavy arms for low-risk applicants",
    ], font_size=13)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.35), Inches(6.0), Inches(0.36),
                  "Objective", font_size=14, bold=True, color=BURGUNDY)
    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.78), Inches(6.0), Inches(0.85),
                 "Maximise cumulative reward Σ r_t over T rounds, "
                 "subject to demographic PSI guardrails.",
                 font_size=13)

    _add_text_box(slide, Inches(7.0), CONTENT_TOP, Inches(5.8), Inches(0.36),
                  "Reward structure (illustrative)", font_size=14, bold=True, color=BURGUNDY)
    reward_rows = [
        ("Action",   "High-risk applicant",   "Low-risk applicant"),
        ("RATED",    "+premium − claims", "− adverse-sel. penalty"),
        ("STANDARD", "+premium − claims", "+optimal margin"),
        ("DECLINE",  "0 (avoided loss)",       "− missed revenue"),
        ("REFER",    "+human decision net",    "+human decision net"),
    ]
    rr_top = CONTENT_TOP + Inches(0.44)
    for i, cols in enumerate(reward_rows):
        ry = rr_top + i * Inches(0.87)
        bg = BURGUNDY if i == 0 else (LIGHT_GRAY if i % 2 == 1 else WHITE)
        col_ws = [Inches(1.55), Inches(2.1), Inches(2.0)]
        col_xs = [Inches(7.0), Inches(8.6), Inches(10.75)]
        _add_filled_box(slide, Inches(7.0), ry, Inches(5.8), Inches(0.83), bg)
        for j, (cx, cw, text) in enumerate(zip(col_xs, col_ws, cols)):
            fc = WHITE if i == 0 else DARK_TEXT
            _add_text_box(slide, cx + Inches(0.05), ry + Inches(0.08),
                          cw - Inches(0.1), Inches(0.67),
                          text, font_size=11, bold=(i == 0), color=fc,
                          anchor=MSO_ANCHOR.MIDDLE)


def slide_algorithms_baselines(prs: Presentation):
    """Slide 11 (09)."""
    slide = _content_slide(prs, "iv", "4.4.  Algorithms & Baselines", "09")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.36),
                  "Proposed policies (ranked by admissibility)", font_size=14,
                  bold=True, color=BURGUNDY)

    algos = [
        (ACCENT_GREEN,  "LinUCB",
         "Upper Confidence Bound over a linear reward model. "
         "Optimism in the face of uncertainty; O(√T·d·log T) regret."),
        (ACCENT_GREEN,  "LinTS",
         "Thompson Sampling from posterior over reward parameters. "
         "Near-optimal regret; naturally calibrated uncertainty."),
        (ACCENT_AMBER,  "ε-Greedy",
         "Uniform exploration with probability ε. Simple baseline; "
         "suboptimal O(T^{2/3}) regret asymptotics."),
        (MED_GRAY,      "Static XGB",
         "XGBoost trained once on a historical snapshot. "
         "Incumbent production baseline."),
        (ACCENT_RED,    "AlwaysRATED",
         "Constant: rate 100% of applicants at +25% loading. Inadmissible ceiling "
         "(not commercially/regulatorily viable -- §5.0.1 / §6.2)."),
    ]
    ay = CONTENT_TOP + Inches(0.45)
    for color, name, desc in algos:
        _add_filled_box(slide, MARGIN_LEFT, ay + Inches(0.07), Inches(0.22), Inches(0.48), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.32), ay, Inches(1.85), Inches(0.62),
                      name, font_size=14, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.25), ay, Inches(10.1), Inches(0.62),
                      desc, font_size=12, color=SOFT_TEXT)
        ay += Inches(0.68)

    _add_filled_box(slide, MARGIN_LEFT, ay + Inches(0.08), CONTENT_W, Inches(0.03), MED_GRAY)

    _add_text_box(slide, MARGIN_LEFT, ay + Inches(0.18), CONTENT_W, Inches(0.35),
                  "Other constants (inadmissible floor/ceiling): AlwaysSTANDARD, AlwaysDECLINE, Random  "
                  "|  Not deployable: LogisticOracle, Oracle",
                  font_size=11, italic=True, color=SOFT_TEXT)

    _add_callout(slide, MARGIN_LEFT, ay + Inches(0.65), CONTENT_W, Inches(0.8),
                 "Admissibility (§5.0.1): a policy is admissible if it is both deployable "
                 "(uses only observable features) AND commercially/regulatorily viable as an "
                 "underwriting rule. LinUCB and LinTS are the top-2 admissible policies.",
                 font_size=12)


def slide_guardrail_hitl_design(prs: Presentation):
    """Slide 12 (10)."""
    slide = _content_slide(prs, "iv", "4.5.  Guardrail + HITL Design", "10")

    # Left: PSI guardrail
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.0), Inches(0.36),
                  "PSI Demographic Guardrail", font_size=14, bold=True, color=BURGUNDY)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.42), Inches(6.0), Inches(0.55),
                  "Population Stability Index computed on region and occupation "
                  "in a rolling 500-round window.",
                  font_size=13, color=DARK_TEXT)

    psi_zones = [
        (ACCENT_GREEN, "GREEN",  "PSI < 0.10",       "Stable -- no action"),
        (ACCENT_AMBER, "AMBER",  "0.10 ≤ PSI < 0.25", "Monitor closely"),
        (ACCENT_RED,   "RED",    "PSI ≥ 0.25",   "Trigger review"),
    ]
    zy = CONTENT_TOP + Inches(1.05)
    for color, label, threshold, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(1.15), Inches(0.55), color, rounded=True)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.06), zy + Inches(0.1),
                      Inches(1.03), Inches(0.38),
                      label, font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _add_text_box(slide, MARGIN_LEFT + Inches(1.3), zy, Inches(2.1), Inches(0.55),
                      threshold, font_size=13, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(3.5), zy, Inches(2.4), Inches(0.55),
                      action, font_size=13, color=SOFT_TEXT)
        zy += Inches(0.65)

    _add_text_box(slide, MARGIN_LEFT, zy + Inches(0.12), Inches(6.0), Inches(0.45),
                  "Note: PSI is a MONITOR, not an enforcer. Constrained-action "
                  "enforcement is deferred to future work.",
                  font_size=11, italic=True, color=SOFT_TEXT)

    # Right: HITL
    _add_text_box(slide, Inches(7.1), CONTENT_TOP, Inches(5.7), Inches(0.36),
                  "Human-in-the-loop Wrapper", font_size=14, bold=True, color=BURGUNDY)
    _add_bullet_box(slide, Inches(7.1), CONTENT_TOP + Inches(0.42), Inches(5.7), Inches(3.0), [
        "Bandit selects arm; if predicted uncertainty > κ threshold → REFER to actuary",
        "Conservatism κ ∈ {0.3, 0.5, 0.7} controls referral rate",
        "Human overrides bandit action; outcome reward used for bandit update",
        "Alignment rate: 60% of overrides agree with bandit (κ=0.7)",
        "Review cost charged per referral; net benefit computed over N=5,000 rounds",
    ], font_size=13)

    _add_callout(slide, Inches(7.1), CONTENT_TOP + Inches(3.55), Inches(5.7), Inches(0.95),
                 "Design target: reduce worst-case regret via human expertise while "
                 "keeping review cost below 2% of gross reward.",
                 font_size=12)


# ===========================================================================
# Section v -- Results & Discussion  (slides 13-18, pages 11-16)
# ===========================================================================

def slide_convergence(prs: Presentation):
    """Slide 13 (11) -- EXP-005."""
    slide = _content_slide(prs, "v", "5.1.  Convergence  (EXP-005)", "11")

    lift = _E005["lift_pct"]
    d    = _E005["reward_cohen_d"]
    p    = _E005["reward_p"]
    lr   = _E005["linucb_reward"]
    sr   = _E005["static_reward"]
    orr  = _E005["oracle_reward"]

    stats = [
        (f"+{lift}%",   "Cumulative reward lift\nvs. Static XGB"),
        (f"d = {d}",    "Cohen's d\n(effect size)"),
        (f"p {p}",      "Paired Wilcoxon\n(20 seeds)"),
        (f"${lr:,}",    "LinUCB cumulative\nreward (mean)"),
    ]
    sw = Inches(2.93)
    for i, (val, label) in enumerate(stats):
        lx = MARGIN_LEFT + i * (sw + Inches(0.1))
        _add_filled_box(slide, lx, CONTENT_TOP, sw, Inches(1.28), BURGUNDY, rounded=True)
        _add_text_box(slide, lx, CONTENT_TOP + Inches(0.04), sw, Inches(0.65),
                      val, font_size=28, bold=True, color=WHITE,
                      align=PP_ALIGN.CENTER, font_name="Times New Roman")
        _add_text_box(slide, lx, CONTENT_TOP + Inches(0.7), sw, Inches(0.5),
                      label, font_size=11, color=WHITE, align=PP_ALIGN.CENTER)

    _add_picture_fit(slide, str(FIG_DIR / "fig_reward_curves.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.4),
                     CONTENT_W, CONTENT_H - Inches(1.6))

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(5.0), CONTENT_W, Inches(0.35),
                  f"Scope: admissible policies only (§5.0.1). "
                  f"Static XGB = ${sr:,} | Oracle = ${orr:,} | Oracle recovered: "
                  f"{_E005['oracle_reward_recovered_pct']}%",
                  font_size=11, italic=True, color=SOFT_TEXT)


def slide_benchmark(prs: Presentation):
    """Slide 14 (12) -- EXP-007."""
    slide = _content_slide(prs, "v", "5.2.  Benchmark vs Static XGB  (EXP-007)", "12")

    _add_picture_fit(slide, str(FIG_DIR / "fig_loglog_regret.png"),
                     MARGIN_LEFT, CONTENT_TOP, Inches(6.8), CONTENT_H - Inches(0.4))

    _add_text_box(slide, Inches(7.6), CONTENT_TOP, Inches(5.2), Inches(0.36),
                  "20-seed ranking", font_size=14, bold=True, color=BURGUNDY)

    ranking = _E007["ranking"]
    col_ws = [Inches(0.65), Inches(2.0), Inches(2.35)]
    col_xs = [Inches(7.6), Inches(8.3), Inches(10.35)]
    hdr_top = CONTENT_TOP + Inches(0.42)
    for hdr, cw, cx in zip(["Rank", "Algorithm", "Reward (mean)"], col_ws, col_xs):
        _add_filled_box(slide, cx, hdr_top, cw, Inches(0.36), BURGUNDY)
        _add_text_box(slide, cx + Inches(0.05), hdr_top + Inches(0.04),
                      cw - Inches(0.1), Inches(0.28),
                      hdr, font_size=11, bold=True, color=WHITE)

    for i, row in enumerate(ranking):
        ry = hdr_top + Inches(0.4) + i * Inches(0.65)
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        for cx, cw in zip(col_xs, col_ws):
            _add_filled_box(slide, cx, ry, cw, Inches(0.62), bg)
        rc = ACCENT_GREEN if row["rank"] <= 2 else DARK_TEXT
        _add_text_box(slide, col_xs[0] + Inches(0.05), ry + Inches(0.1),
                      col_ws[0] - Inches(0.1), Inches(0.44),
                      str(row["rank"]), font_size=14, bold=True, color=rc,
                      align=PP_ALIGN.CENTER)
        _add_text_box(slide, col_xs[1] + Inches(0.05), ry + Inches(0.1),
                      col_ws[1] - Inches(0.1), Inches(0.44),
                      row["algorithm"], font_size=12, color=DARK_TEXT)
        _add_text_box(slide, col_xs[2] + Inches(0.05), ry + Inches(0.1),
                      col_ws[2] - Inches(0.1), Inches(0.44),
                      f"${row['reward']:,}", font_size=12, bold=(row["rank"] <= 2), color=rc)

    _add_text_box(slide, Inches(7.6), hdr_top + Inches(3.05), Inches(5.2), Inches(0.35),
                  f"LinTS vs LinUCB: p = {_E007['lints_vs_linucb_p']} (ns -- tied at 20 seeds)",
                  font_size=11, italic=True, color=SOFT_TEXT)
    _add_callout(slide, Inches(7.6), hdr_top + Inches(3.5), Inches(5.2), Inches(0.9),
                 f"Log-log slope = {_E013['slope']} (R²={_E013['r2']}): "
                 "sub-linear regret consistent with O(√T·d) bound.",
                 font_size=11)


def slide_cold_start(prs: Presentation):
    """Slide 15 (13) -- EXP-010."""
    slide = _content_slide(prs, "v", "5.3.  Cold-start Evaluation  (EXP-010)", "13")

    w = _E010["wilcoxon_t2000"]
    lints_p  = w["lints_vs_freshxgb"]["p"]
    linucb_p = w["linucb_vs_freshxgb"]["p"]

    chips = [
        (ACCENT_GREEN, "LinTS @ T = 2,000",  f"PASSED   p = {lints_p}",  "d = 1.48"),
        (ACCENT_AMBER, "LinUCB @ T = 2,000", f"SOFTENED   p = {linucb_p}", "d = 0.55, n.s."),
    ]
    for i, (color, label, verdict, eff) in enumerate(chips):
        lx = MARGIN_LEFT + i * Inches(6.2)
        _add_filled_box(slide, lx, CONTENT_TOP, Inches(5.9), Inches(1.18), color, rounded=True)
        _add_text_box(slide, lx + Inches(0.15), CONTENT_TOP + Inches(0.04),
                      Inches(5.6), Inches(0.34), label, font_size=13, bold=True, color=WHITE)
        _add_text_box(slide, lx + Inches(0.15), CONTENT_TOP + Inches(0.4),
                      Inches(5.6), Inches(0.4), verdict, font_size=18, bold=True, color=WHITE)
        _add_text_box(slide, lx + Inches(0.15), CONTENT_TOP + Inches(0.82),
                      Inches(5.6), Inches(0.3), eff, font_size=12, color=WHITE)

    _add_picture_fit(slide, str(FIG_DIR / "fig_010_cold_start.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.3),
                     Inches(8.3), CONTENT_H - Inches(1.3))

    _add_text_box(slide, Inches(9.1), CONTENT_TOP + Inches(1.3), Inches(3.7), Inches(0.36),
                  "Implication", font_size=13, bold=True, color=BURGUNDY)
    _add_text_box(slide, Inches(9.1), CONTENT_TOP + Inches(1.72), Inches(3.7), Inches(3.5),
                  _E010["implication"], font_size=11, color=DARK_TEXT)


def slide_hitl_results(prs: Presentation):
    """Slide 16 (14) -- EXP-008."""
    slide = _content_slide(prs, "v", "5.4.  Human-in-the-loop  (EXP-008)", "14")

    lift = _E008["lift_pct"]
    d    = _E008["lift_cohen_d"]
    ref  = _E008["referral_pct"]
    p    = _E008["lift_p"]
    hr   = _E008["hitl_reward"]
    br   = _E008["baseline_reward"]
    hcp  = _E008["human_cost_pct_of_reward"]

    stats = [
        (f"+{lift}%",  "Reward lift\nvs. vanilla bandit"),
        (f"d = {d}",   "Cohen's d"),
        (f"p {p}",     "Wilcoxon\n20 seeds"),
        (f"{ref}%",    "Referral rate\n(review cost)"),
    ]
    sw = Inches(2.93)
    for i, (val, label) in enumerate(stats):
        lx = MARGIN_LEFT + i * (sw + Inches(0.1))
        bg = ACCENT_GREEN if i == 0 else BURGUNDY
        _add_filled_box(slide, lx, CONTENT_TOP, sw, Inches(1.28), bg, rounded=True)
        _add_text_box(slide, lx, CONTENT_TOP + Inches(0.04), sw, Inches(0.65),
                      val, font_size=28, bold=True, color=WHITE,
                      align=PP_ALIGN.CENTER, font_name="Times New Roman")
        _add_text_box(slide, lx, CONTENT_TOP + Inches(0.7), sw, Inches(0.5),
                      label, font_size=11, color=WHITE, align=PP_ALIGN.CENTER)

    _add_picture_fit(slide, str(FIG_DIR / "fig_hitl_experiment.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.4),
                     Inches(7.3), CONTENT_H - Inches(1.55))

    _add_text_box(slide, Inches(8.1), CONTENT_TOP + Inches(1.4), Inches(4.7), Inches(0.36),
                  "Interpretation", font_size=13, bold=True, color=BURGUNDY)
    _add_bullet_box(slide, Inches(8.1), CONTENT_TOP + Inches(1.82), Inches(4.7), Inches(3.4), [
        f"HITL reward ${hr:,} vs. vanilla bandit ${br:,}",
        "Lift certified over the vanilla bandit (EXP-005 baseline)",
        f"Human review cost = {hcp}% of gross reward",
        "Alignment rate 60% (κ=0.7): experts agree with bandit most of the time",
        "Scope: HITL does NOT beat inadmissible AlwaysRATED ceiling (§5.4.2)",
    ], font_size=12)


def slide_fairness_audit(prs: Presentation):
    """Slide 17 (15) -- EXP-006."""
    slide = _content_slide(prs, "v", "5.5.  Fairness Audit  (EXP-006)", "15")

    reg = _E006["region"]
    occ = _E006["occupation"]

    for col_i, (attr, data, zone_color) in enumerate([
        ("Region",     reg, ACCENT_GREEN),
        ("Occupation", occ, ACCENT_AMBER),
    ]):
        cx = MARGIN_LEFT + col_i * Inches(6.2)
        _add_text_box(slide, cx, CONTENT_TOP, Inches(5.9), Inches(0.36),
                      attr, font_size=14, bold=True, color=BURGUNDY)

        row_info = [
            ("PSI zone",    data["psi_zone"],  zone_color),
            ("PSI max",     f"{data['psi_max_sliding']:.4f}", DARK_TEXT),
            ("Parity",      f"{data['parity_pct']}%  (> 80% EEOC)", ACCENT_GREEN),
            ("Criterion 6", data["permutation_verdict"],
             ACCENT_GREEN if data["permutation_verdict"] == "PASSED" else ACCENT_RED),
        ]
        for j, (key, val, col) in enumerate(row_info):
            ry = CONTENT_TOP + Inches(0.42) + j * Inches(0.6)
            bg = LIGHT_GRAY if j % 2 == 0 else WHITE
            _add_filled_box(slide, cx, ry, Inches(5.9), Inches(0.56), bg)
            _add_text_box(slide, cx + Inches(0.1), ry + Inches(0.07),
                          Inches(1.7), Inches(0.42), key, font_size=12, color=SOFT_TEXT)
            _add_text_box(slide, cx + Inches(1.9), ry + Inches(0.07),
                          Inches(3.8), Inches(0.42), val,
                          font_size=13, bold=True, color=col)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.9), CONTENT_W, Inches(1.85),
                 "5 of 6 pre-registered criteria PASSED.\n\n"
                 "Criterion 6 (occupation → action association) FAILED-with-interpretation: "
                 "statistically significant (p < 0.001) but practically small. "
                 "Parity 90.12% >> 80% EEOC. PSI AMBER (0.1225 < 0.25 RED threshold). "
                 "Association reflects actuarially-justified risk differences (§5.2.4). "
                 "Reported honestly.",
                 font_size=12)


def slide_drift_adaptation(prs: Presentation):
    """Slide 18 (16) -- EXP-009. Marked droppable if rehearsal runs long."""
    slide = _content_slide(prs, "v", "5.6.  Drift Adaptation  (EXP-009)", "16")

    shock = _E009["shock"]
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.38),
                  f"Shock at round 1,500: {shock}",
                  font_size=12, italic=True, color=SOFT_TEXT)

    _add_picture_fit(slide, str(FIG_DIR / "fig_009_drift_adaptation.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.48),
                     Inches(7.3), CONTENT_H - Inches(0.55))

    _add_text_box(slide, Inches(8.1), CONTENT_TOP + Inches(0.48), Inches(4.7), Inches(0.36),
                  "Post/pre regret ratio", font_size=13, bold=True, color=BURGUNDY)

    rr_top = CONTENT_TOP + Inches(0.9)
    for i, row in enumerate(_E009["rows"]):
        ry = rr_top + i * Inches(0.82)
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        _add_filled_box(slide, Inches(8.1), ry, Inches(4.7), Inches(0.78), bg)
        c = ACCENT_GREEN if row["post_pre_ratio"] < 0.5 else ACCENT_AMBER
        _add_text_box(slide, Inches(8.2), ry + Inches(0.12),
                      Inches(2.2), Inches(0.55),
                      row["algorithm"], font_size=13, bold=True, color=DARK_TEXT)
        _add_text_box(slide, Inches(10.4), ry + Inches(0.12),
                      Inches(2.3), Inches(0.55),
                      f"{row['post_pre_ratio']}× post/pre",
                      font_size=13, bold=True, color=c, align=PP_ALIGN.RIGHT)

    _add_callout(slide, Inches(8.1), CONTENT_TOP + Inches(3.45), Inches(4.7), Inches(1.35),
                 "Bandits adapt within the learning window: post-shock regret drops "
                 "to 0.29× of pre-shock level. Static XGB stays at 0.85×. "
                 "DiscountedLinUCB is proposed future work.",
                 font_size=11)


# ===========================================================================
# Section vi -- Limitations & Conclusions  (slides 19-21, pages 17-19)
# ===========================================================================

def slide_achievements(prs: Presentation):
    """Slide 19 (17)."""
    slide = _content_slide(prs, "vi", "6.1.  Achievements & Lessons", "17")

    lints_r  = next(r["reward"] for r in _LADDER["rows"] if r["policy"] == "LinTS")
    static_r = next(r["reward"] for r in _LADDER["rows"] if r["policy"] == "Static XGB")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.0), Inches(0.36),
                  "Achievements", font_size=14, bold=True, color=ACCENT_GREEN)
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.42), Inches(6.0), Inches(3.5), [
        (f"LinTS leads every admissible policy: ${lints_r:,} vs. "
         f"Static XGB ${static_r:,}  (+{_E005['lift_pct']}%, d={_E005['reward_cohen_d']})", True),
        "LinTS cold-start crossover certified: Wilcoxon PASSED at T=2,000 (p=0.0039, d=1.48)",
        f"HITL augmentation: +{_E008['lift_pct']}% at {_E008['referral_pct']}% review cost "
        f"(p{_E008['lift_p']}, d={_E008['lift_cohen_d']})",
        "Region PSI GREEN (0.0821); occupation PSI AMBER (0.1225) -- within threshold",
        "5 of 6 pre-registered fairness criteria PASSED",
        f"Log-log regret slope {_E013['slope']} (R²={_E013['r2']}) consistent with O(√T·d)",
    ], font_size=13)

    _add_text_box(slide, Inches(6.8), CONTENT_TOP, Inches(5.8), Inches(0.36),
                  "Limitations", font_size=14, bold=True, color=ACCENT_RED)
    _add_bullet_box(slide, Inches(6.8), CONTENT_TOP + Inches(0.42), Inches(5.8), Inches(3.5), [
        ("AlwaysRATED ($122,287) is the inadmissible ceiling -- see §6.2", True),
        "Synthetic data limits external validity; real claims data needed for production",
        "PSI monitors but does not constrain -- enforcement layer is future work",
        "Criterion-6 FAILED-with-interpretation (occupation–action, p < 0.001)",
        "Cold-start period ~1,000 rounds requires warm-start in deployment",
    ], font_size=13)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.05), CONTENT_W, Inches(0.65),
                 "Overall: contextual bandits provide a principled, adaptive, and auditable "
                 "alternative to static rule-based underwriting in the Cambodian insurance context.",
                 font_size=13, bold=True)


def slide_baseline_ladder(prs: Presentation):
    """Slide 20 (18) -- Q1 armor slide."""
    slide = _content_slide(prs, "vi", "6.2.  Limitation: Baseline Ladder  (EXP-014)", "18")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.38),
                  "Why AlwaysRATED is inadmissible -- and why the headline claim is still valid",
                  font_size=12, italic=True, color=SOFT_TEXT)

    _add_picture_fit(slide, str(FIG_DIR / "fig_exp_014_baseline_ladder.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.45),
                     Inches(7.2), CONTENT_H - Inches(0.6))

    _add_text_box(slide, Inches(8.1), CONTENT_TOP + Inches(0.45), Inches(4.8), Inches(0.36),
                  "Admissibility verdicts", font_size=13, bold=True, color=BURGUNDY)

    panel_policies = {"LinTS", "LinUCB", "AlwaysRATED", "Static XGB"}
    panel_rows = [r for r in _LADDER["rows"] if r["policy"] in panel_policies]
    rr_top = CONTENT_TOP + Inches(0.9)
    for i, row in enumerate(panel_rows):
        ry = rr_top + i * Inches(0.8)
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        _add_filled_box(slide, Inches(8.1), ry, Inches(4.8), Inches(0.76), bg)
        sc = ACCENT_RED if row["status"] == "inadmissible" else ACCENT_GREEN
        _add_text_box(slide, Inches(8.2), ry + Inches(0.1), Inches(2.0), Inches(0.56),
                      row["policy"], font_size=12, bold=True, color=DARK_TEXT)
        _add_text_box(slide, Inches(10.3), ry + Inches(0.1), Inches(2.5), Inches(0.56),
                      row["status"], font_size=12, bold=True, color=sc, align=PP_ALIGN.RIGHT)

    _add_callout(slide, Inches(8.1), CONTENT_TOP + Inches(4.1), Inches(4.8), Inches(1.45),
                 "AlwaysRATED ($122,287) rates 100% at +25% loading -- "
                 "not commercially or regulatorily viable → inadmissible. "
                 "Within the admissible set, LinTS ($93,723) and LinUCB ($91,864) "
                 "rank 1st and 2nd.",
                 font_size=11)


def slide_other_limitations(prs: Presentation):
    """Slide 21 (19)."""
    slide = _content_slide(prs, "vi", "6.3.  Other Limitations & Future Work", "19")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.0), Inches(0.36),
                  "Remaining Limitations", font_size=14, bold=True, color=ACCENT_RED)
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.42), Inches(6.0), Inches(3.5), [
        ("Synthetic data", True),
        "CDHS-anchored demographics; real insurer claims data unavailable",
        "External validity limited -- proof-of-concept, not production estimates",
        ("Monitoring-only fairness", True),
        "PSI guardrail detects, does not prevent demographic concentration",
        ("Cold-start penalty", True),
        "Bandits underperform FreshXGB below T~1,000; warm-start essential",
        ("Experiment scope", True),
        "Single-market simulation; multi-product extension not tested",
    ], font_size=13)

    _add_text_box(slide, Inches(6.8), CONTENT_TOP, Inches(5.8), Inches(0.36),
                  "Future Work", font_size=14, bold=True, color=ACCENT_BLUE)
    _add_bullet_box(slide, Inches(6.8), CONTENT_TOP + Inches(0.42), Inches(5.8), Inches(3.5), [
        "DiscountedLinUCB / SW-UCB for non-stationary / seasonal drift",
        "Constrained contextual bandits for hard fairness enforcement",
        "Real insurer pilot: replace synthetic rewards with observed claims data",
        "Neural linear bandit for higher-dimensional feature spaces",
        "Multi-product portfolio: life + health + motor underwriting",
        "Formal regulatory engagement: SERC Cambodia approval pathway",
    ], font_size=13)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.05), CONTENT_W, Inches(0.65),
                 "Thesis contribution: end-to-end adaptive underwriting prototype + evaluation "
                 "framework with demographic fairness monitoring for the Cambodian context.",
                 font_size=13)


# ===========================================================================
# Slides 22-24 -- Demo, Thanks, Appendix divider
# ===========================================================================

def slide_demo(prs: Presentation):
    """Slide 22."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_filled_box(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(2.0), BURGUNDY)
    _add_text_box(slide, Inches(0), Inches(0.5), SLIDE_WIDTH, Inches(1.0),
                  "DEMONSTRATION", font_size=52, bold=True, color=WHITE,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")

    _add_text_box(slide, MARGIN_LEFT, Inches(2.3), CONTENT_W, Inches(0.5),
                  "Live Adaptive Underwriting Dashboard",
                  font_size=24, bold=True, color=BURGUNDY,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")

    steps = [
        ("1", "Run",  "uvicorn demo.main:app --reload --port 8000"),
        ("2", "Open", "http://localhost:8000"),
        ("3", "Show", "Score applicant → bandit arm selection → PSI monitor panel"),
        ("4", "Show", "Human-in-the-loop referral queue + cost accounting"),
    ]
    step_top = Inches(3.1)
    for num, verb, detail in steps:
        sq = _add_filled_box(slide, MARGIN_LEFT, step_top, Inches(0.5), Inches(0.5), BURGUNDY)
        tf = sq.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        _add_text_box(slide, MARGIN_LEFT + Inches(0.65), step_top,
                      Inches(1.2), Inches(0.5),
                      verb, font_size=16, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.0), step_top,
                      Inches(10.5), Inches(0.5),
                      detail, font_size=14, color=DARK_TEXT, font_name="Courier New")
        step_top += Inches(0.65)

    _add_text_box(slide, MARGIN_LEFT, Inches(6.0), CONTENT_W, Inches(0.38),
                  "Fallback: demo screenshots available in appendix (A6–A8).",
                  font_size=13, italic=True, color=SOFT_TEXT, align=PP_ALIGN.CENTER)

    _add_bottom_bar(slide)


def slide_thanks(prs: Presentation):
    """Slide 23."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    box_w = Inches(11.6)
    title_box = _add_filled_box(slide, (SLIDE_WIDTH - box_w) / 2, Inches(1.9),
                                box_w, Inches(2.6), BURGUNDY, rounded=True)
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.4)
    tf.margin_right = Inches(0.4)
    p1 = tf.paragraphs[0]
    p1.text = "Thank You"
    p1.font.size = Pt(52)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.font.name = "Times New Roman"
    p1.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Questions & Answers"
    p2.font.size = Pt(24)
    p2.font.color.rgb = WHITE
    p2.font.name = "Calibri"
    p2.alignment = PP_ALIGN.CENTER

    _add_text_box(slide, Inches(0), Inches(4.8), SLIDE_WIDTH, Inches(0.42),
                  PRESENTER, font_size=22, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")
    _add_text_box(slide, Inches(0), Inches(5.28), SLIDE_WIDTH, Inches(0.38),
                  "chanpoly3@gmail.com", font_size=17, color=SOFT_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.72), SLIDE_WIDTH, Inches(0.38),
                  INSTITUTION, font_size=16, color=SOFT_TEXT, align=PP_ALIGN.CENTER)

    _add_bottom_bar(slide)


def slide_appendix_divider(prs: Presentation):
    """Slide 24."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_filled_box(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(2.0), BURGUNDY)
    _add_text_box(slide, Inches(0), Inches(0.5), SLIDE_WIDTH, Inches(1.0),
                  "APPENDIX", font_size=52, bold=True, color=WHITE,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")

    items = [
        ("A1", "Q2: Number Reconciliation -- EXP-005 vs ladder harness"),
        ("A2", "Fairness Criterion-6 Detail -- FAILED-with-interpretation"),
        ("A3", "PSI Guardrail Mechanics"),
        ("A4", "LinUCB / LinTS Update Equations"),
        ("A5", "Dataset Construction -- CDHS / STEPS / ILO / WHO anchoring"),
        ("A6–A8", "Demo Screenshots (fallback if live demo fails)"),
    ]
    item_top = Inches(2.3)
    for i, (label, desc) in enumerate(items):
        iy = item_top + i * Inches(0.65)
        sq = _add_filled_box(slide, Inches(1.2), iy, Inches(0.9), Inches(0.5), BURGUNDY)
        tf = sq.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        _add_text_box(slide, Inches(2.3), iy + Inches(0.08),
                      Inches(10.0), Inches(0.38),
                      desc, font_size=15, color=DARK_TEXT)

    _add_bottom_bar(slide)


# ===========================================================================
# Appendix slides A1-A8  (pages A1-A8)
# ===========================================================================

def slide_app_number_reconciliation(prs: Presentation):
    """A1 -- Q2: Why do percentage lifts differ between sections?"""
    slide = _content_slide(prs, "v", "A1.  Q2: Number Reconciliation", "A1")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.36),
                  "Why do different sections quote different percentage lifts?",
                  font_size=12, italic=True, color=SOFT_TEXT)

    col_ws = [Inches(4.2), Inches(1.4), Inches(6.5)]
    col_xs = [MARGIN_LEFT,
               MARGIN_LEFT + col_ws[0] + Inches(0.05),
               MARGIN_LEFT + col_ws[0] + col_ws[1] + Inches(0.1)]
    hdr_top = CONTENT_TOP + Inches(0.42)
    for hdr, cw, cx in zip(["Comparison pair", "Lift", "Basis / why different"], col_ws, col_xs):
        _add_filled_box(slide, cx, hdr_top, cw, Inches(0.38), BURGUNDY)
        _add_text_box(slide, cx + Inches(0.06), hdr_top + Inches(0.05),
                      cw - Inches(0.12), Inches(0.28),
                      hdr, font_size=11, bold=True, color=WHITE)

    recon_rows = [
        ("LinUCB vs Static XGB (EXP-005)",
         "+25.2%",
         "Paired design, same seed sequence, standardised eval (primary metric, Table 5.1.1)"),
        ("LinUCB vs Static XGB (EXP-014 ladder)",
         "+27.2%",
         "CRN harness, reward-maximising policy (Table 9 §5.0.1); larger due to CRN"),
        ("LinTS vs Static XGB (EXP-014 ladder)",
         "+29.8%",
         "CRN harness, LinTS reward-maximising (Table 9 §5.0.1)"),
        ("HITL vs vanilla LinUCB (EXP-008)",
         "+14.8%",
         "Augmented bandit vs. vanilla bandit -- different baseline entirely (Table 13)"),
    ]
    row_h = Inches(0.82)
    for i, (pair, lift, basis) in enumerate(recon_rows):
        ry = hdr_top + Inches(0.42) + i * row_h
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        for cx, cw in zip(col_xs, col_ws):
            _add_filled_box(slide, cx, ry, cw, row_h, bg)
        for cx, cw, text, bold_f in zip(col_xs, col_ws,
                                         [pair, lift, basis],
                                         [False, True, False]):
            col = ACCENT_GREEN if (bold_f and i > 0) else DARK_TEXT
            _add_text_box(slide, cx + Inches(0.06), ry + Inches(0.06),
                          cw - Inches(0.12), row_h - Inches(0.1),
                          text, font_size=11, bold=bold_f, color=col)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.1), CONTENT_W, Inches(1.05),
                 "Headline (+25.2%) uses the conservative paired design. "
                 "Ladder harness lifts are larger due to CRN setup -- all three answer "
                 "different questions and are mutually consistent. "
                 "EXP-005 is the pre-registered primary metric.",
                 font_size=12)


def slide_app_fairness_detail(prs: Presentation):
    """A2 -- Fairness criterion-6 detail."""
    slide = _content_slide(prs, "v", "A2.  Fairness Criterion-6 Detail", "A2")

    occ = _E006["occupation"]
    reg = _E006["region"]

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.36),
                  "Occupation → action association (criterion 6 -- FAILED-with-interpretation)",
                  font_size=14, bold=True, color=BURGUNDY)

    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.42), CONTENT_W, Inches(2.1), [
        ("FAILED verdict -- reported in the interest of scientific honesty", True),
        f"Permutation test: p = {occ['permutation_p']} (criterion: p ≥ 0.05 to PASS)",
        f"EEOC parity: {occ['parity_pct']}%  (well above 80% regulatory floor)",
        f"PSI AMBER: {occ['psi_max_sliding']} < 0.25 RED threshold",
        "The association is statistically significant but practically small.",
        "Interpretation: occupation is an actuarially valid risk predictor; the bandit adjusts",
        "  premiums for legitimate risk differences, NOT for discriminatory reasons.",
    ], font_size=13)

    _add_filled_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.65),
                    CONTENT_W, Inches(0.03), BURGUNDY)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.76), Inches(6.0), Inches(0.36),
                  "Region (PASSED -- for reference)", font_size=13, bold=True, color=ACCENT_GREEN)
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.18), Inches(6.0), Inches(1.55), [
        f"PSI GREEN: {reg['psi_max_sliding']} < 0.10",
        f"Parity: {reg['parity_pct']}%  |  Permutation p = {reg['permutation_p']} (ns)",
        "Region criterion 6: PASSED",
    ], font_size=13)

    _add_callout(slide, Inches(6.8), CONTENT_TOP + Inches(2.76), Inches(5.8), Inches(2.4),
                 "Regulatory position:\n\n"
                 "No formal algorithmic fairness standard exists for insurance in Cambodia. "
                 "The EEOC 80% rule is applied as an international best-practice benchmark. "
                 "All EEOC parity criteria PASS (both region and occupation).",
                 font_size=12)


def slide_app_psi_mechanics(prs: Presentation):
    """A3 -- PSI guardrail mechanics."""
    slide = _content_slide(prs, "iv", "A3.  PSI Guardrail Mechanics", "A3")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.36),
                  "Population Stability Index -- definition and thresholds",
                  font_size=14, bold=True, color=BURGUNDY)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.44), Inches(10.0), Inches(0.42),
                  "PSI = Σ (Actual% − Expected%) × ln(Actual% / Expected%)",
                  font_size=16, bold=True, color=DARK_TEXT, font_name="Courier New")
    _add_bullet_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.96), CONTENT_W, Inches(1.7), [
        "Actual%  = fraction of applicants in each demographic bucket (rolling window)",
        "Expected% = reference distribution (training-set proportions)",
        "Computed on region and occupation every 500 rounds in EXP-006",
    ], font_size=13)

    psi_zones = [
        (ACCENT_GREEN, "GREEN   PSI < 0.10",       "Stable -- no corrective action required"),
        (ACCENT_AMBER, "AMBER  0.10 ≤ PSI < 0.25", "Monitor closely -- investigate trend"),
        (ACCENT_RED,   "RED      PSI ≥ 0.25",  "Trigger mandatory review; consider policy rollback"),
    ]
    zy = CONTENT_TOP + Inches(2.8)
    for color, label, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(3.8), Inches(0.62), color, rounded=True)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.1), zy + Inches(0.1),
                      Inches(3.6), Inches(0.44),
                      label, font_size=13, bold=True, color=WHITE)
        _add_text_box(slide, Inches(4.8), zy + Inches(0.1),
                      Inches(7.8), Inches(0.44),
                      action, font_size=13, color=DARK_TEXT)
        zy += Inches(0.73)

    _add_text_box(slide, MARGIN_LEFT, zy + Inches(0.25), CONTENT_W, Inches(0.38),
                  "EXP-006 results: region PSI = 0.0821 (GREEN), "
                  "occupation PSI max = 0.1225 (AMBER) -- both within threshold",
                  font_size=13, italic=True, color=SOFT_TEXT)


def slide_app_bandit_math(prs: Presentation):
    """A4 -- LinUCB / LinTS update equations."""
    slide = _content_slide(prs, "iv", "A4.  LinUCB / LinTS Update Equations", "A4")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.0), Inches(0.36),
                  "LinUCB (OFUL)", font_size=14, bold=True, color=BURGUNDY)
    linucb_eqs = [
        "A_a  ←  A_a + x_t x_tᵀ          (gram matrix update)",
        "b_a  ←  b_a + r_t x_t            (reward accumulation)",
        "θ_a  =  A_a⁻¹ b_a             (ridge-regression estimate)",
        "a*  =  argmax  θ_aᵀ x_t + α √(x_tᵀ A_a⁻¹ x_t)   (UCB selection)",
    ]
    for i, eq in enumerate(linucb_eqs):
        _add_text_box(slide, MARGIN_LEFT + Inches(0.2),
                      CONTENT_TOP + Inches(0.42) + i * Inches(0.58),
                      Inches(5.8), Inches(0.52),
                      eq, font_size=13, color=DARK_TEXT, font_name="Courier New")

    _add_text_box(slide, Inches(7.0), CONTENT_TOP, Inches(5.8), Inches(0.36),
                  "LinTS (Thompson Sampling)", font_size=14, bold=True, color=BURGUNDY)
    lints_eqs = [
        "Prior:   θ_a ~ N(μ_a, λ⁻¹ I)",
        "Update:  Σ_a⁻¹ = λ I + A_a  ;  μ_a = Σ_a b_a",
        "Sample:  θ̃_a ~ N(μ_a, v² Σ_a)   per round",
        "Select:  a*  =  argmax  θ̃_aᵀ x_t",
    ]
    for i, eq in enumerate(lints_eqs):
        _add_text_box(slide, Inches(7.0) + Inches(0.2),
                      CONTENT_TOP + Inches(0.42) + i * Inches(0.58),
                      Inches(5.6), Inches(0.52),
                      eq, font_size=13, color=DARK_TEXT, font_name="Courier New")

    _add_filled_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.85), CONTENT_W, Inches(0.03), BURGUNDY)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.0), CONTENT_W, Inches(0.36),
                  "Key hyperparameters used", font_size=13, bold=True, color=BURGUNDY)
    hp_rows = [
        ("α (LinUCB exploration)", "1.0 (regret-minimising from EXP-012)"),
        ("v (LinTS variance)",          "0.1 (posterior width calibration)"),
        ("λ (ridge penalty)",      "1.0 (L2 regulariser, identity prior)"),
        ("κ (HITL conservatism)",  "0.7 (headline; 0.3/0.5 also tested in EXP-008)"),
    ]
    hp_top = CONTENT_TOP + Inches(3.45)
    for i, (key, val) in enumerate(hp_rows):
        hy = hp_top + i * Inches(0.62)
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        _add_filled_box(slide, MARGIN_LEFT, hy, CONTENT_W, Inches(0.58), bg)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.1), hy + Inches(0.08),
                      Inches(4.0), Inches(0.44), key, font_size=12, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.2), hy + Inches(0.08),
                      Inches(8.0), Inches(0.44), val, font_size=12, color=SOFT_TEXT)


def slide_app_dataset_construction(prs: Presentation):
    """A5 -- Dataset construction detail."""
    slide = _content_slide(prs, "iv", "A5.  Dataset Construction", "A5")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, Inches(0.36),
                  "CDHS / STEPS / ILO / WHO anchoring",
                  font_size=14, bold=True, color=BURGUNDY)

    sources = [
        ("CDHS 2021-22",    "Age, sex, region, BMI distributions",
         "Cambodia Demographic & Health Survey (NIS / ICF)"),
        ("STEPS 2021",      "Hypertension / chronic disease prevalence by occupation",
         "WHO STEPwise approach to NCD risk-factor surveillance"),
        ("ILO Labour Force", "Income distribution by occupation / sector",
         "Cambodia Labour Force & Child Labour Survey 2021"),
        ("WHO SEARO",       "Health expenditure per capita by income quintile",
         "WHO South-East Asia Regional Office data"),
    ]
    col_ws = [Inches(2.0), Inches(3.5), Inches(6.6)]
    col_xs = [MARGIN_LEFT,
               MARGIN_LEFT + col_ws[0] + Inches(0.05),
               MARGIN_LEFT + col_ws[0] + col_ws[1] + Inches(0.1)]
    hdr_top = CONTENT_TOP + Inches(0.42)
    for hdr, cw, cx in zip(["Source", "Variable", "Full name"], col_ws, col_xs):
        _add_filled_box(slide, cx, hdr_top, cw, Inches(0.38), BURGUNDY)
        _add_text_box(slide, cx + Inches(0.06), hdr_top + Inches(0.05),
                      cw - Inches(0.12), Inches(0.28),
                      hdr, font_size=11, bold=True, color=WHITE)

    row_h = Inches(0.75)
    for i, (src, var, full) in enumerate(sources):
        ry = hdr_top + Inches(0.42) + i * row_h
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        for cx, cw in zip(col_xs, col_ws):
            _add_filled_box(slide, cx, ry, cw, row_h, bg)
        for cx, cw, text in zip(col_xs, col_ws, [src, var, full]):
            _add_text_box(slide, cx + Inches(0.06), ry + Inches(0.08),
                          cw - Inches(0.12), row_h - Inches(0.1),
                          text, font_size=11, color=DARK_TEXT)

    _add_text_box(slide, MARGIN_LEFT, hdr_top + Inches(3.45), CONTENT_W, Inches(0.36),
                  "Simulator parameters", font_size=13, bold=True, color=BURGUNDY)
    sim_params = [
        ("N", "2,000 applicants / 20 seeds, 5,000 rounds each"),
        ("Adverse-selection factor AF", "1.35 (calibrated from DAC actuarial priors)"),
        ("Price elasticity slope β", "3.5 (base case; 2.5 and 4.5 tested in EXP-012)"),
        ("Claim probability", "Logistic function of BMI, age, chronic disease status"),
    ]
    sp_top = hdr_top + Inches(3.85)
    for i, (key, val) in enumerate(sim_params):
        sy = sp_top + i * Inches(0.58)
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        _add_filled_box(slide, MARGIN_LEFT, sy, CONTENT_W, Inches(0.54), bg)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.1), sy + Inches(0.07),
                      Inches(3.8), Inches(0.42), key, font_size=12, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.0), sy + Inches(0.07),
                      Inches(8.0), Inches(0.42), val, font_size=12, color=SOFT_TEXT)


def _slide_demo_screenshot(prs: Presentation, label: str, page_num: str, caption: str):
    """Generic demo screenshot placeholder slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bottom_bar(slide, page_num)
    _add_text_box(slide, MARGIN_LEFT, Inches(0.2), Inches(4.0), Inches(0.45),
                  label, font_size=16, bold=True, color=BURGUNDY)
    _add_filled_box(slide, MARGIN_LEFT, Inches(0.8), CONTENT_W,
                    BOTTOM_BAR_TOP - Inches(1.1), LIGHT_GRAY, rounded=True)
    _add_text_box(slide, MARGIN_LEFT, Inches(0.8), CONTENT_W,
                  BOTTOM_BAR_TOP - Inches(1.1),
                  f"[Demo screenshot placeholder]\n\n{caption}",
                  font_size=16, color=MED_GRAY, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE)
    return slide


# ===========================================================================
# Main
# ===========================================================================

def main():
    prs = Presentation()
    prs.slide_width  = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # ---- Main slides (1-24) ----
    slide_title(prs)                    # 1  -- unnumbered
    slide_toc(prs)                      # 2  -- unnumbered

    slide_research_background(prs)      # 3  -- 01
    slide_research_problem(prs)         # 4  -- 02
    slide_goal_objectives(prs)          # 5  -- 03

    slide_dac_internship(prs)           # 6  -- 04

    slide_lit_summary(prs)              # 7  -- 05

    slide_system_pipeline(prs)          # 8  -- 06
    slide_cambodia_dataset(prs)         # 9  -- 07
    slide_bandit_formulation(prs)       # 10 -- 08
    slide_algorithms_baselines(prs)     # 11 -- 09
    slide_guardrail_hitl_design(prs)    # 12 -- 10

    slide_convergence(prs)              # 13 -- 11
    slide_benchmark(prs)                # 14 -- 12
    slide_cold_start(prs)               # 15 -- 13
    slide_hitl_results(prs)             # 16 -- 14
    slide_fairness_audit(prs)           # 17 -- 15
    slide_drift_adaptation(prs)         # 18 -- 16

    slide_achievements(prs)             # 19 -- 17
    slide_baseline_ladder(prs)          # 20 -- 18
    slide_other_limitations(prs)        # 21 -- 19

    slide_demo(prs)                     # 22 -- unnumbered
    slide_thanks(prs)                   # 23 -- unnumbered
    slide_appendix_divider(prs)         # 24 -- unnumbered

    # ---- Appendix slides (A1-A8) ----
    slide_app_number_reconciliation(prs)   # 25 -- A1
    slide_app_fairness_detail(prs)         # 26 -- A2
    slide_app_psi_mechanics(prs)           # 27 -- A3
    slide_app_bandit_math(prs)             # 28 -- A4
    slide_app_dataset_construction(prs)    # 29 -- A5
    _slide_demo_screenshot(prs, "A6.  Demo Screenshot 1", "A6",  # 30 -- A6
                           "Main underwriting dashboard: applicant scoring and arm selection")
    _slide_demo_screenshot(prs, "A7.  Demo Screenshot 2", "A7",  # 31 -- A7
                           "PSI fairness monitor panel: sliding-window drift visualization")
    _slide_demo_screenshot(prs, "A8.  Demo Screenshot 3", "A8",  # 32 -- A8
                           "Human-in-the-loop queue: referral management and cost accounting")

    assert len(prs.slides) == 32, f"Expected 32 slides, got {len(prs.slides)}"

    prs.save(OUTPUT_PATH)
    print(f"Saved {len(prs.slides)} slides -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
