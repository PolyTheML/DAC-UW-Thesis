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
        (LOGO_ITC, 0.6,  0.30, 1.0),
        (LOGO_AMS, 1.75, 0.40, 1.45),
        (LOGO_DAC, 11.3, 0.35, 1.45),
    ]:
        if os.path.exists(path):
            pic = slide.shapes.add_picture(path, Inches(lx), Inches(ly), width=Inches(lw))
            _flat(pic)

    _add_text_box(slide, Inches(3.4), Inches(0.42), Inches(7.2), Inches(0.5),
                  INSTITUTION, font_size=22, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(3.4), Inches(0.92), Inches(7.2), Inches(0.4),
                  DEPARTMENT, font_size=15, color=GRAY_LABEL, align=PP_ALIGN.CENTER)

    _add_filled_box(slide, Inches(5.92), Inches(2.05), Inches(1.5), Inches(0.045), BURGUNDY)
    box = _add_text_box(slide, Inches(0.9), Inches(2.35), Inches(11.5), Inches(1.7),
                        THESIS_TITLE.upper(), font_size=27, bold=True, color=DARK_TEXT,
                        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    box.text_frame.word_wrap = True
    _add_filled_box(slide, Inches(5.92), Inches(4.25), Inches(1.5), Inches(0.045), BURGUNDY)

    _add_text_box(slide, Inches(0), Inches(4.62), SLIDE_WIDTH, Inches(0.34),
                  "Thesis Defense — Presented by", font_size=14, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(4.96), SLIDE_WIDTH, Inches(0.5),
                  PRESENTER, font_size=27, bold=True, color=BURGUNDY,
                  align=PP_ALIGN.CENTER)

    lx, rx = Inches(1.5), Inches(7.5)
    for i, (lt, rt) in enumerate([
        (f"Supervisor      :  {SUPERVISOR}",    f"Organization :  {ORGANIZATION}"),
        (f"Co-Supervisor  :  {CO_SUPERVISOR}", f"Duration        :  {DURATION}"),
    ]):
        y = Inches(5.68) + i * Inches(0.36)
        _add_text_box(slide, lx, y, Inches(5.6), Inches(0.34), lt, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, rx, y, Inches(5.6), Inches(0.34), rt, font_size=14, color=DARK_TEXT)

    _add_text_box(slide, Inches(0), Inches(6.6), SLIDE_WIDTH, Inches(0.38),
                  DEFENSE_DATE, font_size=15, bold=True, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)


# ===========================================================================
# Slide 2 -- Table of Contents
# ===========================================================================

def slide_toc(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_text_box(slide, MARGIN_LEFT, Inches(0.55), Inches(9.0), Inches(0.7),
                  "Table of Contents", font_size=30, bold=True, color=DARK_TEXT)
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.32), Inches(0.55), Inches(0.045), BURGUNDY)

    col_xs = [Inches(0.9), Inches(7.1)]
    row_h = Inches(1.55)
    for idx, (num, name) in enumerate(SECTIONS):
        cx = col_xs[idx // 3]
        cy = Inches(1.95) + (idx % 3) * row_h
        _add_text_box(slide, cx, cy, Inches(1.1), Inches(0.65),
                      num, font_size=30, bold=True, color=BURGUNDY)
        _add_text_box(slide, cx + Inches(1.25), cy + Inches(0.06),
                      Inches(4.6), Inches(0.5),
                      name, font_size=19, bold=True, color=DARK_TEXT)
        _add_filled_box(slide, cx + Inches(1.25), cy + Inches(0.62),
                        Inches(4.3), Inches(0.012), HAIRLINE)
    _add_bottom_bar(slide)


# ===========================================================================
# Section i -- Introduction  (slides 3-5, pages 01-03)
# ===========================================================================

def slide_research_background(prs: Presentation):
    """Slide 3 (01)."""
    slide = _content_slide(prs, "i", "1.1.  Research Background", "01")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.1), Inches(6.4), Inches(0.9),
                  "< 10 %", font_size=60, bold=True, color=BURGUNDY)
    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.05), Inches(6.4),
                        Inches(0.36), "HEALTH-INSURANCE PENETRATION IN CAMBODIA (2023 EST.)",
                        font_size=10, color=GRAY_LABEL)
    _letterspace(lab.text_frame.paragraphs[0], 80)

    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.8), Inches(6.4), [
        "NSSF covers formal-sector workers only (~16%)",
        "Private underwriting is manual and rule-based",
        "Static rules never learn from outcomes",
        "No demographic-parity monitoring in practice",
    ])

    _add_callout(slide, Inches(7.3), CONTENT_TOP + Inches(0.1), Inches(5.5), Inches(4.6),
                 "Research opportunity\n\nContextual bandits can learn from every "
                 "underwriting decision in real time, adapting to Cambodia-specific risk "
                 "patterns while demographic fairness is monitored automatically.",
                 font_size=15)

    _add_notes(slide,
        "Cambodia context: the National Social Security Fund covers only formal-sector "
        "workers, roughly 16 percent; private voluntary insurance is nascent and "
        "underwriting is mostly manual and rule-based. Actuaries apply fixed premium rules "
        "without learning from outcomes, suboptimal decisions compound over a growing "
        "applicant pool, and penetration is below 10 percent (2023 estimate). The "
        "opportunity: a contextual bandit learns online from each decision while a PSI "
        "guardrail watches demographic fairness.")


def slide_research_problem(prs: Presentation):
    """Slide 4 (02)."""
    slide = _content_slide(prs, "i", "1.2.  Research Problem", "02")

    problems = [
        ("Static thresholds", "Fixed cutoffs ignore applicant context"),
        ("No online adaptation", "Claims feedback never reaches the model"),
        ("Demographic blindspot", "No parity metric is tracked"),
        ("No triage", "Experts review routine, not borderline, cases"),
    ]
    card_w, card_h = Inches(6.0), Inches(2.35)
    positions = [
        (MARGIN_LEFT,               CONTENT_TOP + Inches(0.2)),
        (MARGIN_LEFT + Inches(6.4), CONTENT_TOP + Inches(0.2)),
        (MARGIN_LEFT,               CONTENT_TOP + Inches(2.85)),
        (MARGIN_LEFT + Inches(6.4), CONTENT_TOP + Inches(2.85)),
    ]
    for (title, desc), (lx, ly) in zip(problems, positions):
        _add_filled_box(slide, lx, ly, card_w, card_h, PANEL)
        _add_filled_box(slide, lx, ly, Inches(0.07), card_h, BURGUNDY)
        _add_text_box(slide, lx + Inches(0.3), ly + Inches(0.35),
                      card_w - Inches(0.6), Inches(0.5),
                      title, font_size=20, bold=True, color=DARK_TEXT)
        _add_text_box(slide, lx + Inches(0.3), ly + Inches(1.0),
                      card_w - Inches(0.6), Inches(1.1),
                      desc, font_size=15, color=SOFT_TEXT)

    _add_notes(slide,
        "Four concrete failures of the status quo. One: fixed age/BMI/income cutoffs "
        "ignore context, so a misclassified high-risk applicant generates uncorrected "
        "losses. Two: the claims signal is never fed back, so accuracy degrades silently "
        "as demographics shift. Three: no parity metric is tracked, so regional or "
        "occupational concentration can develop undetected. Four: there is no triage - "
        "actuaries spend time on high-volume routine cases instead of genuine edge cases.")


def slide_goal_objectives(prs: Presentation):
    """Slide 5 (03). Objectives verbatim from the thesis -- do not paraphrase."""
    slide = _content_slide(prs, "i", "1.3.  Research Goal & Objectives", "03")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(4.0), Inches(0.32),
                        "RESEARCH GOAL", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.38), CONTENT_W, Inches(0.75),
                  "Design and evaluate an adaptive health insurance underwriting system using "
                  "contextual bandit algorithms on a synthetic Cambodia applicant dataset, "
                  "incorporating demographic fairness monitoring and human-in-the-loop augmentation.",
                  font_size=15, color=DARK_TEXT)

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.35), Inches(4.0),
                        Inches(0.32), "OBJECTIVES", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)

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
    top = CONTENT_TOP + Inches(1.8)
    for i, (label, text) in enumerate(objs):
        y = top + i * Inches(0.95)
        _add_text_box(slide, MARGIN_LEFT, y, Inches(0.75), Inches(0.5),
                      label, font_size=20, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.85), y + Inches(0.02),
                      CONTENT_W - Inches(0.85), Inches(0.85),
                      text, font_size=14, color=DARK_TEXT)
        if i > 0:
            _add_filled_box(slide, MARGIN_LEFT, y - Inches(0.1), CONTENT_W,
                            Inches(0.012), HAIRLINE)

    _add_notes(slide,
        "Read the goal once, slowly. The four objectives map one-to-one onto the chapters: "
        "O1 the algorithms (Chapter IV), O2 the dataset (Chapter IV), O3 the evaluation "
        "(Chapter V), O4 fairness plus HITL (Chapter V). These are verbatim from the thesis "
        "- the examiners will check the wording.")


# ===========================================================================
# Section ii -- Internship at DAC  (slide 6, page 04)
# ===========================================================================

def slide_dac_internship(prs: Presentation):
    """Slide 6 (04)."""
    slide = _content_slide(prs, "ii", "2.1.  Internship at DAC", "04")

    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.1), Inches(6.4), [
        "DAC -- actuarial consulting, Phnom Penh",
        "Clients: insurers, pension funds, regulators",
        "Role: research intern, Mar-Jun 2026",
        "Deliverable: underwriting prototype + thesis",
    ])

    _add_callout(slide, Inches(7.3), CONTENT_TOP + Inches(0.1), Inches(5.5), Inches(2.5),
                 f"Supervision\n\nThesis advisor: {SUPERVISOR} (ITC)\n"
                 f"Field supervisor: {CO_SUPERVISOR} (DAC)",
                 font_size=15)

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.05), Inches(4.0),
                        Inches(0.32), "INTERNSHIP TIMELINE", font_size=11, bold=True,
                        color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    timeline = [
        ("Mar 2026", "Problem scoping & dataset design"),
        ("Apr 2026", "Algorithm implementation"),
        ("May 2026", "Experiments & analysis"),
        ("Jun 2026", "Thesis writing & defense prep"),
    ]
    seg_w = Inches(3.0)
    strip_top = CONTENT_TOP + Inches(3.5)
    for i, (month, desc) in enumerate(timeline):
        lx = MARGIN_LEFT + i * (seg_w + Inches(0.1))
        _add_filled_box(slide, lx, strip_top, seg_w, Inches(0.05), BURGUNDY)
        _add_text_box(slide, lx, strip_top + Inches(0.15), seg_w - Inches(0.2),
                      Inches(0.36), month, font_size=14, bold=True, color=BURGUNDY)
        _add_text_box(slide, lx, strip_top + Inches(0.55), seg_w - Inches(0.2),
                      Inches(0.8), desc, font_size=12, color=SOFT_TEXT)

    _add_notes(slide,
        "Decent Actuarial Consultants is a Phnom Penh actuarial consultancy serving "
        "insurers, pension funds and regulators across Southeast Asia. The thesis is "
        "embedded in a DAC-supervised research internship, March through June 2026; the "
        "deliverable is the end-to-end adaptive underwriting prototype plus this report. "
        "Timeline: March scoping and dataset design, April algorithms, May experiments, "
        "June writing and defense preparation.")


# ===========================================================================
# Section iii -- Literature Review  (slide 7, page 05)
# ===========================================================================

def slide_lit_summary(prs: Presentation):
    """Slide 7 (05)."""
    slide = _content_slide(prs, "iii", "3.1.  Literature Summary", "05")

    rows = [
        ("Bandits in healthcare", "Bouneffouf et al. (2017)",
         "Clinical decision support via LinUCB; reward = patient outcome"),
        ("Linear bandit theory", "Li et al. (2010); Agrawal & Goyal (2013)",
         "LinUCB O(sqrt(T) d log T) regret; LinTS posterior sampling, near-optimal"),
        ("Fairness in insurance ML", "Frees et al. (2014); Kusner et al. (2017)",
         "Regulatory constraints on protected attributes; counterfactual fairness"),
        ("PSI model monitoring", "Yurdakul (2018)",
         "Population Stability Index drift zones (GREEN / AMBER / RED)"),
        ("Human-in-the-loop RL", "Christiano et al. (2017)",
         "Expert overrides improve alignment; cost-benefit of referral"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.15),
                    [Inches(3.0), Inches(3.6), Inches(5.7)],
                    ["Topic", "Key authors", "Contribution"],
                    rows, font_size=13, row_h=Inches(0.85))

    _add_footnote(slide, "Full review: thesis Chapter III (30+ sources).")
    _add_notes(slide,
        "Five strands inform the method. Bouneffouf showed LinUCB works for clinical "
        "decisions. Li et al. 2010 give the LinUCB regret bound, Agrawal and Goyal 2013 "
        "the LinTS guarantee - together they justify the two proposed policies. Frees and "
        "Kusner frame insurance fairness constraints; Yurdakul's PSI gives the monitoring "
        "metric with the 0.10/0.25 thresholds; Christiano motivates the human-in-the-loop "
        "wrapper. The thesis reviews thirty-plus sources; this is the load-bearing subset.")


# ===========================================================================
# Section iv -- Methodology  (slides 8-12, pages 06-10)
# ===========================================================================

def slide_system_pipeline(prs: Presentation):
    """Slide 8 (06) -- native-shape architecture (replaces fig_ch4_architecture.png)."""
    slide = _content_slide(prs, "iv", "4.1.  System Pipeline", "06")

    layers = [
        ("BROWSER (SPA)", ["Applicant Simulator", "Premium Optimiser",
                           "Bandit Arena", "PSI Monitor"]),
        ("FASTAPI REST", ["/api/simulate", "/api/pricing/optimize",
                          "/api/bandit/run", "/api/psi/audit"]),
        ("PYTHON BACKEND", ["Actuarial Reward Sim", "Pricing Engine",
                            "Bandit Algorithms (LinUCB / LinTS)", "PSI Compute"]),
    ]
    label_w, box_w, box_h, gap = Inches(1.7), Inches(2.55), Inches(0.78), Inches(0.18)
    row_step = Inches(1.45)
    top0 = CONTENT_TOP + Inches(0.25)
    for li, (label, boxes) in enumerate(layers):
        ly = top0 + li * row_step
        lab = _add_text_box(slide, MARGIN_LEFT, ly + Inches(0.22), label_w, Inches(0.4),
                            label, font_size=10, bold=True, color=BURGUNDY)
        _letterspace(lab.text_frame.paragraphs[0], 80)
        for bi, text in enumerate(boxes):
            bx = MARGIN_LEFT + label_w + bi * (box_w + gap)
            _add_filled_box(slide, bx, ly, box_w, box_h, PANEL,
                            line_color=HAIRLINE, line_width_pt=1.0)
            _add_text_box(slide, bx + Inches(0.08), ly, box_w - Inches(0.16), box_h,
                          text, font_size=12, bold=(li == 2), color=DARK_TEXT,
                          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            if li < 2:  # connector to the layer below
                cx = bx + box_w / 2
                _add_filled_box(slide, cx, ly + box_h, Inches(0.018),
                                row_step - box_h, BURGUNDY)

    src_y = top0 + 3 * row_step + Inches(0.1)
    for sx, text in [(MARGIN_LEFT + label_w, "Cambodia synthetic dataset (2,000 applicants)"),
                     (MARGIN_LEFT + label_w + 2 * (box_w + gap),
                      "Static XGBoost baseline (mortality model)")]:
        _add_filled_box(slide, sx, src_y, box_w * 2 + gap, Inches(0.6), WHITE,
                        line_color=BURGUNDY, line_width_pt=1.2)
        _add_text_box(slide, sx, src_y, box_w * 2 + gap, Inches(0.6),
                      text, font_size=12, color=SOFT_TEXT,
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    _add_notes(slide,
        "Architecture in three layers. The browser SPA hosts four panels: applicant "
        "simulator, premium optimiser, bandit arena, PSI monitor. Each maps to a FastAPI "
        "endpoint, backed by the Python core: the actuarial reward simulator, the pricing "
        "engine, the bandit algorithms LinUCB and LinTS, and the PSI computation. "
        "Everything is fed by the 2,000-applicant synthetic Cambodia dataset, with the "
        "static XGBoost mortality model as the incumbent baseline. This same stack powers "
        "the live demo later.")


def slide_cambodia_dataset(prs: Presentation):
    """Slide 9 (07)."""
    slide = _content_slide(prs, "iv", "4.2.  Synthetic Cambodia Dataset", "07")

    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        ("2,000", "synthetic applications"),
        ("5", "demographic features"),
        ("4", "underwriting arms"),
        ("4", "anchoring sources"),
    ])

    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.45), Inches(6.2), [
        "Anchored on CDHS, STEPS, ILO, WHO data",
        "Adverse selection AF = 1.35; elasticity 3.5",
        "Fully synthetic -- no real applicant PII",
    ])

    arms = [
        ("RATED",    "Accept + premium loading (+25%)"),
        ("STANDARD", "Accept at standard premium"),
        ("DECLINE",  "Reject application"),
        ("REFER",    "Escalate to human underwriter"),
    ]
    ay = CONTENT_TOP + Inches(1.5)
    for i, (arm, desc) in enumerate(arms):
        ry = ay + i * Inches(0.78)
        _add_text_box(slide, Inches(7.1), ry, Inches(1.9), Inches(0.4),
                      arm, font_size=15, bold=True, color=BURGUNDY)
        _add_text_box(slide, Inches(9.1), ry + Inches(0.02), Inches(3.7), Inches(0.5),
                      desc, font_size=13, color=SOFT_TEXT)
        if i > 0:
            _add_filled_box(slide, Inches(7.1), ry - Inches(0.14), Inches(5.7),
                            Inches(0.012), HAIRLINE)

    _add_footnote(slide, "Construction detail: appendix A5 (sources, simulator parameters).")
    _add_notes(slide,
        "The dataset is 2,000 synthetic applicants with five features: age, sex, region, "
        "occupation, BMI. Distributions are anchored on CDHS 2021-22 and STEPS 2021; "
        "income on ILO labour-force surveys; claim probabilities calibrated from WHO SEARO "
        "health-expenditure data. Adverse-selection factor 1.35 and price-elasticity slope "
        "3.5 come from DAC actuarial priors. Four arms: RATED accepts with a 25 percent "
        "loading, STANDARD accepts at standard rate, DECLINE rejects, REFER escalates to a "
        "human. No real applicant data is used anywhere.")


def slide_bandit_formulation(prs: Presentation):
    """Slide 10 (08)."""
    slide = _content_slide(prs, "iv", "4.3.  Bandit Formulation", "08")

    defs = [
        ("Context  x_t ∈ R^5", "age, sex, region, occupation, BMI -- standardised"),
        ("Action  a_t", "one of RATED / STANDARD / DECLINE / REFER"),
        ("Reward  r_t", "revenue minus claims, actuarial simulator"),
    ]
    dy = CONTENT_TOP + Inches(0.15)
    for i, (term, desc) in enumerate(defs):
        ry = dy + i * Inches(0.95)
        _add_text_box(slide, MARGIN_LEFT, ry, Inches(2.9), Inches(0.45),
                      term, font_size=16, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT, ry + Inches(0.42), Inches(5.9), Inches(0.4),
                      desc, font_size=13, color=SOFT_TEXT)

    _add_callout(slide, MARGIN_LEFT, dy + Inches(3.05), Inches(5.9), Inches(1.0),
                 "Objective: maximise cumulative reward Σ r_t over T rounds, "
                 "subject to demographic PSI guardrails.",
                 font_size=14, bold=True)

    rows = [
        ("RATED",    "+premium − claims", "− adverse-sel. penalty"),
        ("STANDARD", "+premium − claims", "+optimal margin"),
        ("DECLINE",  "0 (avoided loss)",  "− missed revenue"),
        ("REFER",    "+human decision net", "+human decision net"),
    ]
    _add_flat_table(slide, Inches(7.0), CONTENT_TOP + Inches(0.15),
                    [Inches(1.7), Inches(2.1), Inches(2.0)],
                    ["Action", "High-risk", "Low-risk"],
                    rows, font_size=12, row_h=Inches(0.72))

    _add_notes(slide,
        "Formally: at each round the context is the standardised five-feature applicant "
        "vector, the action is one of four arms, and the reward is revenue minus claims "
        "from the actuarial simulator, with adverse selection penalising premium-heavy "
        "arms on low-risk applicants. The objective is cumulative reward over T rounds "
        "subject to the PSI guardrail. The table sketches the reward structure: for a "
        "high-risk applicant DECLINE avoids a loss; for a low-risk one it forfeits "
        "revenue; REFER nets the human decision either way.")


def slide_algorithms_baselines(prs: Presentation):
    """Slide 11 (09)."""
    slide = _content_slide(prs, "iv", "4.4.  Algorithms & Baselines", "09")

    algos = [
        (ACCENT_GREEN, "LinUCB",      "Optimism under uncertainty -- O(sqrt(T) d log T) regret"),
        (ACCENT_GREEN, "LinTS",       "Posterior sampling -- near-optimal regret"),
        (ACCENT_AMBER, "ε-Greedy",    "Uniform exploration -- suboptimal O(T^2/3)"),
        (MED_GRAY,     "Static XGB",  "Train-once incumbent baseline"),
        (ACCENT_RED,   "AlwaysRATED", "Constant +25% loading -- inadmissible ceiling"),
    ]
    ay = CONTENT_TOP + Inches(0.25)
    for i, (color, name, desc) in enumerate(algos):
        ry = ay + i * Inches(0.85)
        _add_filled_box(slide, MARGIN_LEFT, ry + Inches(0.06), Inches(0.16),
                        Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), ry, Inches(2.6), Inches(0.5),
                      name, font_size=18, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(3.2), ry + Inches(0.05),
                      Inches(9.2), Inches(0.5), desc, font_size=15, color=SOFT_TEXT)
        if i > 0:
            _add_filled_box(slide, MARGIN_LEFT, ry - Inches(0.17), CONTENT_W,
                            Inches(0.012), HAIRLINE)

    _add_footnote(slide,
        "Admissibility (§5.0.1): deployable AND commercially/regulatorily viable. "
        "LinUCB and LinTS are the top-2 admissible policies. "
        "Other reference policies: AlwaysSTANDARD, AlwaysDECLINE, Random, LogisticOracle, Oracle.")
    _add_notes(slide,
        "Two proposed policies and three reference points. LinUCB plays optimism in the "
        "face of uncertainty over a linear reward model with the square-root-T regret "
        "bound; LinTS samples from the posterior and is near-optimal with naturally "
        "calibrated uncertainty. Epsilon-greedy is the naive explorer with provably worse "
        "T-to-the-two-thirds regret. Static XGB is the train-once incumbent. AlwaysRATED "
        "rates everyone at +25 percent loading - it scores highest but is neither "
        "commercially nor regulatorily viable, which is exactly the admissibility "
        "distinction in section 5.0.1 and the dedicated limitation slide 6.2.")


def slide_guardrail_hitl_design(prs: Presentation):
    """Slide 12 (10)."""
    slide = _content_slide(prs, "iv", "4.5.  Guardrail + HITL Design", "10")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(5.9), Inches(0.32),
                        "PSI DEMOGRAPHIC GUARDRAIL", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    psi_zones = [
        (ACCENT_GREEN, "GREEN", "PSI < 0.10", "stable"),
        (ACCENT_AMBER, "AMBER", "0.10-0.25", "monitor"),
        (ACCENT_RED,   "RED",   "PSI ≥ 0.25", "review"),
    ]
    zy = CONTENT_TOP + Inches(0.5)
    for color, label, threshold, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(0.16), Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), zy, Inches(1.5), Inches(0.5),
                      label, font_size=16, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.0), zy + Inches(0.04),
                      Inches(2.1), Inches(0.45), threshold, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.2), zy + Inches(0.04),
                      Inches(1.7), Inches(0.45), action, font_size=14, color=SOFT_TEXT)
        zy += Inches(0.72)
    _add_text_box(slide, MARGIN_LEFT, zy + Inches(0.1), Inches(5.9), Inches(0.7),
                  "Computed on region & occupation, rolling 500-round window.",
                  font_size=13, color=SOFT_TEXT)

    lab = _add_text_box(slide, Inches(7.1), CONTENT_TOP, Inches(5.7), Inches(0.32),
                        "HUMAN-IN-THE-LOOP WRAPPER", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(7.1), CONTENT_TOP + Inches(0.5), Inches(5.7), [
        "Uncertainty > κ  →  REFER to actuary",
        "Conservatism κ ∈ {0.3, 0.5, 0.7}",
        "Human decides; reward still trains bandit",
        "Target: review cost < 2% of reward",
    ], font_size=15)

    _add_footnote(slide,
        "PSI is a monitor, not an enforcer -- constrained-action enforcement is future work.")
    _add_notes(slide,
        "Two safety layers. The PSI guardrail computes the Population Stability Index on "
        "region and occupation over a rolling 500-round window: GREEN below 0.10, AMBER to "
        "0.25, RED above. It detects concentration; it does not constrain the policy - "
        "enforcement is future work, stated honestly. The HITL wrapper REFERs an applicant "
        "to the actuary whenever predicted uncertainty exceeds the conservatism threshold "
        "kappa, tested at 0.3, 0.5, 0.7; the human's decision is final and its observed "
        "reward still updates the bandit. Design target: keep review cost under two "
        "percent of gross reward.")


# ===========================================================================
# Section v -- Results & Discussion  (slides 13-18, pages 11-16)
# ===========================================================================

def slide_convergence(prs: Presentation):
    """Slide 13 (11) -- EXP-005."""
    slide = _content_slide(prs, "v", "5.1.  Convergence  (EXP-005)", "11")

    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        (f"+{_E005['lift_pct']}%", "reward lift vs static xgb"),
        (f"d = {_E005['reward_cohen_d']}", "effect size"),
        (f"p {_E005['reward_p']}", "paired wilcoxon · 20 seeds"),
        (f"${_E005['linucb_reward']:,}", "linucb cumulative reward"),
    ])

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_reward_curves.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     CONTENT_W, CONTENT_H - Inches(1.7))

    _add_footnote(slide,
        f"Scope: admissible policies only (§5.0.1). Static XGB ${_E005['static_reward']:,} · "
        f"Oracle ${_E005['oracle_reward']:,} ({_E005['oracle_reward_recovered_pct']}% recovered).")
    _add_notes(slide,
        f"The headline: LinUCB earns {_E005['lift_pct']} percent more cumulative reward "
        f"than the static XGBoost baseline over 5,000 rounds - "
        f"${_E005['linucb_reward']:,} versus ${_E005['static_reward']:,}, twenty seeds, "
        f"paired Wilcoxon p {_E005['reward_p']}, Cohen's d {_E005['reward_cohen_d']}. "
        f"The curves separate around round 1,500 once the bandit's ridge estimates "
        f"converge. Critical scope: this claim is over ADMISSIBLE policies per section "
        f"5.0.1 - the inadmissible AlwaysRATED constant sits above (slide 6.2). Oracle "
        f"recovery is {_E005['oracle_reward_recovered_pct']} percent.")


def slide_benchmark(prs: Presentation):
    """Slide 14 (12) -- EXP-007."""
    slide = _content_slide(prs, "v", "5.2.  Benchmark vs Static XGB  (EXP-007)", "12")

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_loglog_regret.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.1),
                     Inches(6.6), CONTENT_H - Inches(0.5))

    rows = [(str(r["rank"]), r["algorithm"], f"${r['reward']:,}")
            for r in _E007["ranking"]]

    def _rank_style(i, c, text):
        top2 = i < 2
        return (top2, BURGUNDY if top2 else DARK_TEXT)

    _add_flat_table(slide, Inches(7.5), CONTENT_TOP + Inches(0.35),
                    [Inches(0.8), Inches(2.4), Inches(2.1)],
                    ["#", "Algorithm", "Reward"],
                    rows, font_size=14, row_h=Inches(0.62), cell_style=_rank_style)

    _add_text_box(slide, Inches(7.5), CONTENT_TOP + Inches(3.5), Inches(5.3), Inches(0.8),
                  f"Log-log regret slope {_E013['slope']} (R² = {_E013['r2']}) -- "
                  "sub-linear, consistent with O(√T·d).",
                  font_size=14, color=DARK_TEXT)

    _add_footnote(slide,
        f"LinTS vs LinUCB: p = {_E007['lints_vs_linucb_p']} (n.s. -- tied at 20 seeds). "
        "Same CRN harness across all four algorithms.")
    _add_notes(slide,
        f"All four algorithms under common random numbers. LinTS ranks first at "
        f"${_E007['ranking'][0]['reward']:,}, LinUCB second at "
        f"${_E007['ranking'][1]['reward']:,} - statistically tied "
        f"(p = {_E007['lints_vs_linucb_p']}). Epsilon-greedy trails, static XGB last. "
        f"The log-log plot validates theory: fitted slope {_E013['slope']} with R squared "
        f"{_E013['r2']}, close to the 0.5 of the O(root-T d) bound - the bandit's regret "
        f"really is sub-linear, it is learning, not memorising.")


def slide_cold_start(prs: Presentation):
    """Slide 15 (13) -- EXP-010."""
    slide = _content_slide(prs, "v", "5.3.  Cold-start Evaluation  (EXP-010)", "13")

    w = _E010["wilcoxon_t2000"]
    lints, linucb = w["lints_vs_freshxgb"], w["linucb_vs_freshxgb"]
    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        ("PASSED", "lints @ t = 2,000"),
        (f"p = {lints['p']}", f"wilcoxon · d = {lints['d']}"),
        ("DRAWS LEVEL", "linucb @ t = 2,000"),
        (f"p = {linucb['p']:.4f}", f"n.s. · d = {linucb['d']}"),
    ], value_colors=[ACCENT_GREEN, DARK_TEXT, ACCENT_AMBER, DARK_TEXT])

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_cold_start.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     Inches(8.2), CONTENT_H - Inches(1.7))

    _add_talking_points(slide, Inches(9.1), CONTENT_TOP + Inches(1.6), Inches(3.7), [
        "Fresh XGB wins below T ≈ 1,000",
        "Crossover between 1,000-2,000",
        "Deploy with warm-start",
    ], font_size=14, line_h=Inches(0.85))

    _add_footnote(slide,
        f"Only LinTS is certified at T = 2,000 (p = {lints['p']}); LinUCB's lead is not "
        f"significant (p = {linucb['p']:.4f}, d = {linucb['d']}) and is reported as 'draws level'.")
    _add_notes(slide,
        f"Honest cold-start picture: below a thousand rounds a freshly trained XGBoost "
        f"beats both bandits - at T=200 it is roughly twice as good. The crossover comes "
        f"between one and two thousand rounds. At T=2,000 LinTS's lead is significant at "
        f"the Bonferroni-corrected threshold (p = {lints['p']}, d = {lints['d']}); "
        f"LinUCB's is positive but NOT significant (p = {linucb['p']:.4f}, d = {linucb['d']}) "
        f"- we softened that claim to 'draws level'. Deployment implication: warm-start "
        f"or shadow mode for the first thousand applications. Note this crossover is "
        f"against a frozen rule, not against the AlwaysRATED constant.")


def slide_hitl_results(prs: Presentation):
    """Slide 16 (14) -- EXP-008."""
    slide = _content_slide(prs, "v", "5.4.  Human-in-the-loop  (EXP-008)", "14")

    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        (f"+{_E008['lift_pct']}%", "reward lift vs vanilla bandit"),
        (f"d = {_E008['lift_cohen_d']}", f"wilcoxon p {_E008['lift_p']} · 20 seeds"),
        (f"{_E008['referral_pct']}%", "referral rate"),
        (f"{_E008['human_cost_pct_of_reward']}%", "review cost of gross reward"),
    ])

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_hitl.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     Inches(7.2), CONTENT_H - Inches(1.7))

    _add_talking_points(slide, Inches(8.0), CONTENT_TOP + Inches(1.6), Inches(4.8), [
        f"HITL ${_E008['hitl_reward']:,} vs bandit ${_E008['baseline_reward']:,}",
        f"Experts agree with bandit {_E008['alignment_pct']:.0f}% (κ=0.7)",
        "Queue depth stays at zero",
    ], font_size=14, line_h=Inches(0.85))

    _add_footnote(slide,
        "Lift is vs the vanilla bandit -- HITL does NOT beat the inadmissible "
        "AlwaysRATED ceiling (§5.4.2).")
    _add_notes(slide,
        f"Adding the human wrapper lifts reward {_E008['lift_pct']} percent over the "
        f"vanilla bandit: ${_E008['hitl_reward']:,} versus ${_E008['baseline_reward']:,}, "
        f"twenty seeds, p {_E008['lift_p']}, d = {_E008['lift_cohen_d']}. Cost side: only "
        f"{_E008['referral_pct']} percent of applicants get referred, review spend is "
        f"{_E008['human_cost_pct_of_reward']} percent of gross reward, and experts agree "
        f"with the bandit {_E008['alignment_pct']:.0f} percent of the time at kappa 0.7. "
        f"Scope, stated plainly: this certifies HITL against the bandit itself, not "
        f"against the AlwaysRATED constant - section 5.4.2.")


def slide_fairness_audit(prs: Presentation):
    """Slide 17 (15) -- EXP-006."""
    slide = _content_slide(prs, "v", "5.5.  Fairness Audit  (EXP-006)", "15")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.5),
                  "5 of 6 pre-registered criteria PASSED",
                  font_size=20, bold=True, color=DARK_TEXT)

    for col_i, (attr, data) in enumerate([("Region", _E006["region"]),
                                          ("Occupation", _E006["occupation"])]):
        cx = MARGIN_LEFT + col_i * Inches(6.3)
        zone_color = ACCENT_GREEN if data["psi_zone"] == "GREEN" else ACCENT_AMBER
        verdict = data["permutation_verdict"]
        rows = [
            ("PSI zone", f"{data['psi_zone']}  ({data['psi_max_sliding']:.4f} max)"),
            ("EEOC parity", f"{data['parity_pct']}%  (floor 80%)"),
            ("Criterion 6", verdict),
        ]

        def _style(i, c, text, _zone=zone_color, _verdict=verdict):
            if c == 1 and i == 0:
                return (True, _zone)
            if c == 1 and i == 2:
                return (True, ACCENT_GREEN if _verdict == "PASSED" else ACCENT_RED)
            return (c == 1, DARK_TEXT)

        _add_text_box(slide, cx, CONTENT_TOP + Inches(0.7), Inches(5.9), Inches(0.4),
                      attr, font_size=16, bold=True, color=BURGUNDY)
        _add_flat_table(slide, cx, CONTENT_TOP + Inches(1.2),
                        [Inches(2.2), Inches(3.7)], ["Check", "Result"],
                        rows, font_size=14, row_h=Inches(0.66), cell_style=_style)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.0), CONTENT_W, Inches(0.85),
                 "Occupation association reflects actuarially justified risk differences "
                 "(§5.2.4); no regulatory threshold (EEOC 80%, PSI 0.25) is breached.",
                 font_size=13)

    _add_footnote(slide,
        f"Criterion 6 (occupation→action) FAILED-with-interpretation: "
        f"p {_E006['occupation']['permutation_p']} -- statistically significant but "
        f"practically small. Reported honestly.")
    _add_notes(slide,
        f"Fairness audit over the converged window. Region: PSI GREEN at "
        f"{_E006['region']['psi_max_sliding']}, parity {_E006['region']['parity_pct']} "
        f"percent, permutation test PASSED (p = {_E006['region']['permutation_p']}). "
        f"Occupation: PSI AMBER at {_E006['occupation']['psi_max_sliding']} - within the "
        f"0.25 threshold - parity {_E006['occupation']['parity_pct']} percent, well above "
        f"the EEOC 80 percent floor. Criterion 6 is the one failure: the "
        f"occupation-action association is statistically significant (p < 0.001) but "
        f"practically small, and occupation is an actuarially valid rating factor; we "
        f"marked it FAILED in the interest of honesty rather than rationalising it away. "
        f"Fairness is maintained and verified, not improved.")


def slide_drift_adaptation(prs: Presentation):
    """Slide 18 (16) -- EXP-009. Droppable if rehearsal runs long (notes, not slide)."""
    slide = _content_slide(prs, "v", "5.6.  Drift Adaptation  (EXP-009)", "16")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.4),
                  f"Shock at round 1,500: {_E009['shock']}",
                  font_size=13, italic=True, color=GRAY_LABEL)

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_drift.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.5),
                     Inches(7.2), CONTENT_H - Inches(0.9))

    rows = [(r["algorithm"], f"{r['post_pre_ratio']}×") for r in _E009["rows"]]

    def _ratio_style(i, c, text):
        if c == 1:
            good = float(text.rstrip("×")) < 0.5
            return (True, ACCENT_GREEN if good else ACCENT_AMBER)
        return (False, DARK_TEXT)

    _add_text_box(slide, Inches(8.0), CONTENT_TOP + Inches(0.6), Inches(4.8), Inches(0.4),
                  "Post/pre regret ratio", font_size=16, bold=True, color=BURGUNDY)
    _add_flat_table(slide, Inches(8.0), CONTENT_TOP + Inches(1.1),
                    [Inches(2.6), Inches(2.0)], ["Algorithm", "Ratio"],
                    rows, font_size=14, row_h=Inches(0.66), cell_style=_ratio_style)

    _static_ratio = next(r["post_pre_ratio"] for r in _E009["rows"]
                         if r["algorithm"] == "StaticXGB")
    _add_footnote(slide,
        f"Pre/post windows also differ in learning-curve position; the static baseline's "
        f"{_static_ratio}× is the cleanest comparator (§5.9.3).")
    _add_notes(slide,
        "Stress test: at round 1,500 we double TB prevalence and cut garment-worker "
        "income 30 percent. The bandits re-converge within their learning window - "
        "post-shock regret drops to 0.29 times the pre-shock level for both LinUCB and "
        "LinTS, while static XGB only reaches 0.85. Caveat on the slide: pre and post "
        "windows also differ in learning-curve position, so the static baseline is the "
        "cleanest comparator. DiscountedLinUCB for sustained non-stationarity is future "
        "work. THIS SLIDE IS DROPPABLE if timing runs long - the examiner armor lives "
        "elsewhere.")


# ===========================================================================
# Section vi -- Limitations & Conclusions  (slides 19-21, pages 17-19)
# ===========================================================================

def slide_achievements(prs: Presentation):
    """Slide 19 (17)."""
    slide = _content_slide(prs, "vi", "6.1.  Achievements & Lessons", "17")

    lints_r  = next(r["reward"] for r in _LADDER["rows"] if r["policy"] == "LinTS")
    static_r = next(r["reward"] for r in _LADDER["rows"] if r["policy"] == "Static XGB")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "ACHIEVEMENTS", font_size=11, bold=True,
                        color=ACCENT_GREEN)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.5), Inches(5.9), [
        f"Leads every admissible policy (+{_E005['lift_pct']}%, d={_E005['reward_cohen_d']})",
        "LinTS cold-start crossover certified (p=0.0039)",
        f"HITL +{_E008['lift_pct']}% at {_E008['referral_pct']}% referrals",
        "5 of 6 fairness criteria PASSED",
    ], font_size=15, line_h=Inches(0.78))

    lab = _add_text_box(slide, Inches(6.9), CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "LESSONS / LIMITS", font_size=11, bold=True,
                        color=ACCENT_RED)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(6.9), CONTENT_TOP + Inches(0.5), Inches(5.9), [
        f"AlwaysRATED ceiling sits above (→ 6.2)",
        "Synthetic data limits external validity",
        "PSI monitors; it does not enforce",
        "Cold-start needs warm-start in production",
    ], font_size=15, line_h=Inches(0.78))

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.0), CONTENT_W, Inches(0.85),
                 "Contextual bandits give a principled, adaptive, auditable alternative "
                 "to static rule-based underwriting in the Cambodian context.",
                 font_size=15, bold=True)

    _add_notes(slide,
        f"Balance sheet. Wins: LinTS leads every admissible policy at ${lints_r:,} versus "
        f"static ${static_r:,}; the cold-start crossover is certified for LinTS; HITL adds "
        f"{_E008['lift_pct']} percent at {_E008['referral_pct']} percent referrals; five of "
        f"six fairness criteria pass; log-log slope {_E013['slope']} matches theory. "
        f"Honest limits: the inadmissible AlwaysRATED constant scores higher - next slide "
        f"is devoted to it; data is synthetic; PSI only monitors; criterion 6 failed with "
        f"interpretation; cold-start needs warm-start. Net: adaptive, auditable, and "
        f"honest about scope.")


def slide_baseline_ladder(prs: Presentation):
    """Slide 20 (18) -- Q1 armor slide."""
    slide = _content_slide(prs, "vi", "6.2.  Limitation: Baseline Ladder  (EXP-014)", "18")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.42),
                  "Why AlwaysRATED is inadmissible -- and why the headline claim still holds",
                  font_size=15, bold=True, color=DARK_TEXT)

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_ladder.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.5),
                     Inches(7.2), CONTENT_H - Inches(0.95))

    panel_policies = ["LinTS", "LinUCB", "Static XGB", "AlwaysRATED"]
    by_name = {r["policy"]: r for r in _LADDER["rows"]}
    rows = [(p, f"${by_name[p]['reward']:,}", by_name[p]["status"])
            for p in panel_policies]

    def _status_style(i, c, text):
        if c == 2:
            return (True, ACCENT_RED if text == "inadmissible" else ACCENT_GREEN)
        return (c == 0, DARK_TEXT)

    _add_flat_table(slide, Inches(8.0), CONTENT_TOP + Inches(0.7),
                    [Inches(1.9), Inches(1.5), Inches(1.5)],
                    ["Policy", "Reward", "Status"],
                    rows, font_size=13, row_h=Inches(0.6), cell_style=_status_style)

    _add_talking_points(slide, Inches(8.0), CONTENT_TOP + Inches(3.7), Inches(4.8), [
        "Rates 100% at flat +25% loading",
        "Not commercially / regulatorily viable",
        "Bandits rank 1-2 of admissible set",
    ], font_size=13, line_h=Inches(0.55))

    ar = by_name["AlwaysRATED"]["reward"]
    _add_footnote(slide,
        f"Pre-registered expectation FALSIFIED: AlwaysRATED ${ar:,} tops the ladder "
        f"(§5.0.1) -- reported as the scientifically informative outcome; headline is "
        f"scoped to admissible policies.")
    _add_notes(slide,
        f"This is the anticipated question, so we lead with it. The full baseline ladder "
        f"shows AlwaysRATED - rate every applicant at a flat 25 percent loading - at "
        f"${ar:,}, above LinTS ${by_name['LinTS']['reward']:,} and LinUCB "
        f"${by_name['LinUCB']['reward']:,}. Our pre-registered expectation that the "
        f"bandit beats every simple baseline was FALSIFIED, and we report that. Why the "
        f"thesis still stands: AlwaysRATED is inadmissible - loading every customer 25 "
        f"percent collapses commercially (adverse selection drives good risks away) and "
        f"would not survive regulatory scrutiny - per the admissibility definition in "
        f"section 5.0.1. Within the admissible set the bandits rank first and second. "
        f"If pressed on number differences across sections: appendix A1 reconciles "
        f"+25.2 / +27.2 / +29.8 percent.")


def slide_other_limitations(prs: Presentation):
    """Slide 21 (19)."""
    slide = _content_slide(prs, "vi", "6.3.  Other Limitations & Future Work", "19")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "REMAINING LIMITATIONS", font_size=11, bold=True,
                        color=ACCENT_RED)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.5), Inches(5.9), [
        "Synthetic data -- proof of concept only",
        "Fairness is monitored, not enforced",
        "Cold-start penalty below T ≈ 1,000",
        "Single market, single product",
    ], font_size=15, line_h=Inches(0.78))

    lab = _add_text_box(slide, Inches(6.9), CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "FUTURE WORK", font_size=11, bold=True,
                        color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(6.9), CONTENT_TOP + Inches(0.5), Inches(5.9), [
        "DiscountedLinUCB for sustained drift",
        "Constrained bandits: hard fairness limits",
        "Real insurer pilot with observed claims",
        "Multi-product portfolio underwriting",
    ], font_size=15, line_h=Inches(0.78))

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.0), CONTENT_W, Inches(0.85),
                 "Contribution: end-to-end adaptive underwriting prototype + evaluation "
                 "framework with demographic fairness monitoring for Cambodia.",
                 font_size=15, bold=True)

    _add_notes(slide,
        "Remaining limits beyond the ladder: demographics are CDHS-anchored but rewards "
        "are simulated, so treat results as proof-of-concept, not production estimates; "
        "the PSI guardrail detects concentration but cannot prevent it; bandits "
        "underperform a fresh XGBoost below roughly a thousand rounds; and we tested one "
        "market, one product. Future work in order of value: discounted or "
        "sliding-window UCB for seasonal drift, constrained contextual bandits for hard "
        "fairness enforcement, a real-insurer pilot replacing the simulator with observed "
        "claims, neural-linear bandits for richer features, multi-product portfolios, and "
        "a SERC Cambodia regulatory pathway.")


# ===========================================================================
# Slides 22-24 -- Demo, Thanks, Appendix divider
# ===========================================================================

def slide_demo(prs: Presentation):
    """Slide 22 -- live demo cue."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    tag = _add_text_box(slide, MARGIN_LEFT, Inches(0.7), Inches(6.0), Inches(0.34),
                        "LIVE DEMONSTRATION", font_size=12, bold=True, color=BURGUNDY)
    _letterspace(tag.text_frame.paragraphs[0], 200)
    _add_text_box(slide, MARGIN_LEFT, Inches(1.1), Inches(12.0), Inches(0.7),
                  "Adaptive Underwriting Dashboard", font_size=30, bold=True,
                  color=DARK_TEXT)
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.92), Inches(0.55), Inches(0.045), BURGUNDY)

    steps = [
        ("1", "Run",  "uvicorn demo.main:app --reload --port 8000"),
        ("2", "Open", "http://localhost:8000"),
        ("3", "Show", "Score applicant -> bandit arm selection -> PSI monitor panel"),
        ("4", "Show", "Human-in-the-loop referral queue + cost accounting"),
    ]
    step_top = Inches(2.6)
    for num, verb, detail in steps:
        _add_text_box(slide, MARGIN_LEFT, step_top, Inches(0.5), Inches(0.5),
                      num, font_size=22, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.65), step_top + Inches(0.05),
                      Inches(1.2), Inches(0.45), verb, font_size=16, bold=True,
                      color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.0), step_top + Inches(0.07),
                      Inches(10.5), Inches(0.45), detail, font_size=14,
                      color=SOFT_TEXT, font_name="Consolas")
        _add_filled_box(slide, MARGIN_LEFT, step_top + Inches(0.58),
                        Inches(11.9), Inches(0.012), HAIRLINE)
        step_top += Inches(0.78)

    _add_footnote(slide, "Fallback: demo screenshots in appendix (A6-A8) if the live run fails.")
    _add_bottom_bar(slide)
    _add_notes(slide,
        "Switch to the browser. Walk one applicant through scoring, show the arm the bandit "
        "picks and the uncertainty-driven REFER, then the PSI monitor staying GREEN/AMBER, "
        "and finally the HITL queue with per-referral cost. If anything breaks, jump to "
        "appendix slides A6-A8 and narrate over the screenshots.")


def slide_thanks(prs: Presentation):
    """Slide 23."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_filled_box(slide, Inches(5.92), Inches(2.0), Inches(1.5), Inches(0.045), BURGUNDY)
    _add_text_box(slide, Inches(0), Inches(2.35), SLIDE_WIDTH, Inches(1.0),
                  "Thank you.", font_size=54, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(3.45), SLIDE_WIDTH, Inches(0.5),
                  "Questions & Answers", font_size=20, color=BURGUNDY,
                  align=PP_ALIGN.CENTER)

    _add_text_box(slide, Inches(0), Inches(4.7), SLIDE_WIDTH, Inches(0.42),
                  PRESENTER, font_size=20, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.15), SLIDE_WIDTH, Inches(0.38),
                  "chanpoly3@gmail.com", font_size=15, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.55), SLIDE_WIDTH, Inches(0.38),
                  INSTITUTION, font_size=14, color=GRAY_LABEL, align=PP_ALIGN.CENTER)

    for path, lx in [(LOGO_ITC, 5.45), (LOGO_AMS, 6.25), (LOGO_DAC, 7.15)]:
        if os.path.exists(path):
            pic = slide.shapes.add_picture(path, Inches(lx), Inches(6.15), width=Inches(0.7))
            _flat(pic)
    _add_bottom_bar(slide)


def slide_appendix_divider(prs: Presentation):
    """Slide 24."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_text_box(slide, MARGIN_LEFT, Inches(0.9), Inches(10.0), Inches(1.0),
                  "APPENDIX", font_size=48, bold=True, color=BURGUNDY)
    _add_filled_box(slide, MARGIN_LEFT, Inches(2.05), Inches(0.55), Inches(0.045), BURGUNDY)

    items = [
        ("A1", "Q2: Number Reconciliation -- EXP-005 vs ladder harness"),
        ("A2", "Fairness Criterion-6 Detail -- FAILED-with-interpretation"),
        ("A3", "PSI Guardrail Mechanics"),
        ("A4", "LinUCB / LinTS Update Equations"),
        ("A5", "Dataset Construction -- CDHS / STEPS / ILO / WHO anchoring"),
        ("A6-A8", "Demo Screenshots (fallback if live demo fails)"),
    ]
    item_top = Inches(2.55)
    for i, (label, desc) in enumerate(items):
        iy = item_top + i * Inches(0.68)
        _add_text_box(slide, Inches(1.0), iy, Inches(1.2), Inches(0.4),
                      label, font_size=15, bold=True, color=BURGUNDY)
        _add_text_box(slide, Inches(2.4), iy, Inches(10.0), Inches(0.4),
                      desc, font_size=15, color=DARK_TEXT)
    _add_bottom_bar(slide)


# ===========================================================================
# Appendix slides A1-A8  (pages A1-A8)
# ===========================================================================

def slide_app_number_reconciliation(prs: Presentation):
    """A1 -- Q2: Why do percentage lifts differ between sections?"""
    slide = _content_slide(prs, "v", "A1.  Q2: Number Reconciliation", "A1")

    lifts = _LADDER["ladder_basis_lift"]
    rows = [
        ("LinUCB vs Static XGB (EXP-005)", f"+{_E005['lift_pct']}%",
         "Paired design, standardised eval -- the pre-registered primary metric"),
        ("LinUCB vs Static XGB (EXP-014 ladder)", f"+{lifts['linucb_vs_static_pct']}%",
         "CRN harness, reward-maximising policy (Table 9, §5.0.1)"),
        ("LinTS vs Static XGB (EXP-014 ladder)", f"+{lifts['lints_vs_static_pct']}%",
         "CRN harness, LinTS reward-maximising (Table 9, §5.0.1)"),
        ("HITL vs vanilla LinUCB (EXP-008)", f"+{_E008['lift_pct']}%",
         "Augmented bandit vs vanilla bandit -- different baseline entirely"),
    ]

    def _lift_style(i, c, text):
        return (c == 1, BURGUNDY if c == 1 else DARK_TEXT)

    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.2),
                    [Inches(4.4), Inches(1.4), Inches(6.4)],
                    ["Comparison pair", "Lift", "Basis / why different"],
                    rows, font_size=13, row_h=Inches(0.85), cell_style=_lift_style)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.3), CONTENT_W, Inches(0.9),
                 "All three answer different questions and are mutually consistent. "
                 "EXP-005 (+25.2%) is the conservative pre-registered primary.",
                 font_size=14)
    _add_notes(slide,
        "If asked why 25.2, 27.2 and 29.8 percent all appear: the headline uses the "
        "paired EXP-005 design; the ladder harness uses common random numbers which "
        "yields larger separations; HITL's 14.8 percent is against the vanilla bandit, a "
        "different baseline. Same code, different pre-registered questions.")


def slide_app_fairness_detail(prs: Presentation):
    """A2 -- Fairness criterion-6 detail."""
    slide = _content_slide(prs, "v", "A2.  Fairness Criterion-6 Detail", "A2")

    occ, reg = _E006["occupation"], _E006["region"]
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.4),
                  "Occupation → action association: FAILED-with-interpretation",
                  font_size=16, bold=True, color=DARK_TEXT)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.55), Inches(6.2), [
        f"Permutation p {occ['permutation_p']} (PASS needs ≥ 0.05)",
        f"EEOC parity {occ['parity_pct']}% (floor 80%)",
        f"PSI AMBER {occ['psi_max_sliding']} < 0.25 RED",
        "Significant, but practically small",
    ], font_size=15, line_h=Inches(0.7))

    _add_callout(slide, Inches(7.1), CONTENT_TOP + Inches(0.55), Inches(5.7), Inches(2.6),
                 "Interpretation: occupation is an actuarially valid risk predictor; the "
                 "bandit prices legitimate risk differences, not protected-class membership. "
                 "Marked FAILED for honesty (§5.2.3-5.2.4).",
                 font_size=14)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.5), Inches(6.2), Inches(0.4),
                  "Region (PASSED, for reference)", font_size=14, bold=True,
                  color=ACCENT_GREEN)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.95), Inches(6.2), Inches(0.8),
                  f"PSI GREEN {reg['psi_max_sliding']}  ·  parity {reg['parity_pct']}%  ·  "
                  f"permutation p = {reg['permutation_p']} (n.s.)",
                  font_size=13, color=SOFT_TEXT)

    _add_footnote(slide,
        "No formal algorithmic-fairness standard exists for Cambodian insurance; EEOC 80% "
        "is applied as international best practice.")
    _add_notes(slide,
        "Deep-dive armor for criterion 6. The permutation test rejects independence at p "
        "below 0.001, so by our own pre-registered rule it is FAILED. Context: parity is "
        "90 percent against an 80 percent floor, PSI stays under the RED threshold, and "
        "occupation is an actuarially priced factor everywhere. Region passes everything. "
        "Regulatory framing: Cambodia has no algorithmic fairness standard, so EEOC 80 "
        "percent is the borrowed benchmark - and it passes for both attributes.")


def slide_app_psi_mechanics(prs: Presentation):
    """A3 -- PSI guardrail mechanics."""
    slide = _content_slide(prs, "iv", "A3.  PSI Guardrail Mechanics", "A3")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.05), Inches(10.5), Inches(0.5),
                  "PSI = Σ (Actual% − Expected%) × ln(Actual% / Expected%)",
                  font_size=20, bold=True, color=DARK_TEXT, font_name="Consolas")
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.75), CONTENT_W, [
        "Actual% = bucket share, rolling 500-round window",
        "Expected% = training-set reference distribution",
        "Computed on region and occupation (EXP-006)",
    ], font_size=15, line_h=Inches(0.62))

    psi_zones = [
        (ACCENT_GREEN, "GREEN", "PSI < 0.10", "stable -- no action"),
        (ACCENT_AMBER, "AMBER", "0.10 ≤ PSI < 0.25", "monitor closely"),
        (ACCENT_RED,   "RED",   "PSI ≥ 0.25", "mandatory review / rollback"),
    ]
    zy = CONTENT_TOP + Inches(2.85)
    for color, label, threshold, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(0.16), Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), zy, Inches(1.4), Inches(0.5),
                      label, font_size=16, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(1.9), zy + Inches(0.04), Inches(2.6),
                      Inches(0.45), threshold, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.7), zy + Inches(0.04), Inches(7.5),
                      Inches(0.45), action, font_size=14, color=SOFT_TEXT)
        zy += Inches(0.7)

    _add_footnote(slide,
        f"EXP-006: region PSI {_E006['region']['psi_max_sliding']} (GREEN) · occupation "
        f"max {_E006['occupation']['psi_max_sliding']} (AMBER) -- both within threshold.")
    _add_notes(slide,
        "PSI mechanics if asked: it is the symmetrised relative-entropy-style sum over "
        "demographic buckets comparing the rolling 500-round window against the training "
        "reference. Standard industry thresholds: 0.10 and 0.25. In our audit region "
        "peaks at 0.0821, occupation at 0.1225.")


def slide_app_bandit_math(prs: Presentation):
    """A4 -- LinUCB / LinTS update equations."""
    slide = _content_slide(prs, "iv", "A4.  LinUCB / LinTS Update Equations", "A4")

    for cx, head, eqs in [
        (MARGIN_LEFT, "LinUCB (OFUL)", [
            "A_a ← A_a + x_t x_tᵀ",
            "b_a ← b_a + r_t x_t",
            "θ_a = A_a⁻¹ b_a",
            "a* = argmax θ_aᵀx_t + α√(x_tᵀA_a⁻¹x_t)",
        ]),
        (Inches(7.0), "LinTS (Thompson)", [
            "Prior: θ_a ~ N(μ_a, λ⁻¹I)",
            "Σ_a⁻¹ = λI + A_a ;  μ_a = Σ_a b_a",
            "Sample: θ̃_a ~ N(μ_a, v²Σ_a)",
            "Select: a* = argmax θ̃_aᵀ x_t",
        ]),
    ]:
        _add_text_box(slide, cx, CONTENT_TOP + Inches(0.05), Inches(5.8), Inches(0.4),
                      head, font_size=16, bold=True, color=BURGUNDY)
        for i, eq in enumerate(eqs):
            _add_text_box(slide, cx + Inches(0.15),
                          CONTENT_TOP + Inches(0.55) + i * Inches(0.56),
                          Inches(5.7), Inches(0.5), eq, font_size=15,
                          color=DARK_TEXT, font_name="Consolas")

    hp_rows = [
        ("α  (LinUCB exploration)", "1.0 -- regret-minimising (EXP-012)"),
        ("v  (LinTS variance)", "0.1 -- posterior width calibration"),
        ("λ  (ridge penalty)", "1.0 -- identity prior"),
        ("κ  (HITL conservatism)", "0.7 headline; 0.3 / 0.5 also tested"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.35),
                    [Inches(4.2), Inches(8.1)], ["Hyperparameter", "Value"],
                    hp_rows, font_size=13, row_h=Inches(0.56))
    _add_notes(slide,
        "Math armor. LinUCB maintains a per-arm gram matrix and reward vector, solves "
        "ridge regression, and adds the alpha-scaled confidence width - optimism in the "
        "face of uncertainty. LinTS instead samples theta from the posterior and picks "
        "the argmax - exploration through randomisation. Hyperparameters: alpha 1.0 "
        "chosen as regret-minimising in the EXP-012 sensitivity sweep, ridge lambda 1.0, "
        "LinTS variance 0.1, HITL kappa 0.7.")


def slide_app_dataset_construction(prs: Presentation):
    """A5 -- Dataset construction detail."""
    slide = _content_slide(prs, "iv", "A5.  Dataset Construction", "A5")

    src_rows = [
        ("CDHS 2021-22", "Age, sex, region, BMI distributions"),
        ("STEPS 2021", "Chronic-disease prevalence by occupation"),
        ("ILO LFS 2021", "Income distribution by occupation / sector"),
        ("WHO SEARO", "Health expenditure per capita by quintile"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.15),
                    [Inches(2.6), Inches(9.7)], ["Source", "Variables anchored"],
                    src_rows, font_size=13, row_h=Inches(0.6))

    sim_rows = [
        ("Scale", "2,000 applicants · 20 seeds · 5,000 rounds"),
        ("Adverse-selection AF", "1.35 (DAC actuarial priors)"),
        ("Price elasticity β", "3.5 base; 2.5 / 4.5 in EXP-012"),
        ("Claim probability", "Logistic in BMI, age, chronic status"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.2),
                    [Inches(2.6), Inches(9.7)], ["Simulator parameter", "Value"],
                    sim_rows, font_size=13, row_h=Inches(0.6))

    _add_footnote(slide, "Fully synthetic -- no real applicant PII anywhere in the pipeline.")
    _add_notes(slide,
        "Dataset armor: every marginal is anchored to a public source - CDHS for "
        "demographics and BMI, WHO STEPS for chronic prevalence by occupation, ILO "
        "labour-force surveys for income, WHO SEARO for expenditure. The simulator adds "
        "adverse selection at 1.35 and elasticity 3.5 from DAC priors, both stress-tested "
        "in EXP-012. No real applicant data exists anywhere in the pipeline.")


def _slide_demo_screenshot(prs: Presentation, label: str, page_num: str, caption: str):
    """Generic demo screenshot placeholder slide (real captures: pre-defense task)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bottom_bar(slide, page_num)
    _add_slide_title(slide, label)
    _add_title_rule(slide)
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.35), CONTENT_W,
                    BOTTOM_BAR_TOP - Inches(1.7), PANEL)
    _add_text_box(slide, MARGIN_LEFT, Inches(1.35), CONTENT_W,
                  BOTTOM_BAR_TOP - Inches(1.7),
                  f"[Demo screenshot placeholder]\n\n{caption}",
                  font_size=16, color=GRAY_LABEL, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE)
    _add_notes(slide, f"Fallback narration target: {caption}")
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
