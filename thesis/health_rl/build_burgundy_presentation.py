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
DEMO_SHOT_DIR = FIG_DIR / "demo_shots"

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
BLUE_TITLE    = RGBColor(0x1B, 0x56, 0x97)   # content titles + underline accent
BLUE_DIVIDER  = RGBColor(0x1F, 0x6F, 0xC4)   # divider numerals/titles
BLUE_DEEP     = RGBColor(0x14, 0x3D, 0x6B)   # footer org block / deep accent
BLUE_TINT     = RGBColor(0xAF, 0xC4, 0xE4)   # footer center block tint
BLUE_NODE     = RGBColor(0xDC, 0xE8, 0xF6)   # flowchart node fill (pale blue)
NODE_START    = RGBColor(0x2E, 0x9E, 0x5B)   # flowchart Start node (green)
NODE_END      = RGBColor(0xE6, 0x8A, 0x2E)   # flowchart End node (orange)
GREEN_HILITE  = RGBColor(0x2E, 0x9E, 0x5B)   # methodology "you are here" outline
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT     = RGBColor(0x1A, 0x1A, 0x1A)
SOFT_TEXT     = RGBColor(0x3A, 0x3A, 0x3A)
LIGHT_GRAY    = RGBColor(0xF2, 0xF4, 0xF7)
MED_GRAY      = RGBColor(0x80, 0x80, 0x80)
ACCENT_RED    = RGBColor(0xD9, 0x3B, 0x3B)
ACCENT_GREEN  = RGBColor(0x2E, 0x8B, 0x57)
ACCENT_AMBER  = RGBColor(0xE6, 0xA6, 0x2E)
ACCENT_BLUE   = RGBColor(0x1F, 0x6F, 0xC4)
GRAY_LABEL    = RGBColor(0x77, 0x77, 0x77)   # stat labels / footnotes
HAIRLINE      = RGBColor(0xDD, 0xDD, 0xDD)   # 1px separators
PANEL         = RGBColor(0xF3, 0xF6, 0xFB)   # flat panel fill (pale blue-gray)
HEAD_FONT     = "Segoe UI"                    # headings (rounded reference feel)
BODY_FONT     = "Calibri"                     # body text

# ---------------------------------------------------------------------------
# Dimensions (16:9 widescreen)
# ---------------------------------------------------------------------------
SLIDE_WIDTH       = Inches(13.333)
SLIDE_HEIGHT      = Inches(7.5)
MARGIN_LEFT       = Inches(0.5)
CONTENT_TOP       = Inches(1.30)   # below underline (v3: centered title at 0.34, underline at 1.02)
FOOTER_TOP        = Inches(7.04)
FOOTER_HEIGHT     = Inches(0.46)
CONTENT_W         = SLIDE_WIDTH - MARGIN_LEFT - Inches(0.5)
CONTENT_H         = FOOTER_TOP - CONTENT_TOP - Inches(0.15)
FOOTNOTE_TOP      = FOOTER_TOP - Inches(0.42)

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
    ("I",   "Introduction & Problem Background"),
    ("II",  "Literature Review"),
    ("III", "Methodology & Model Design"),
    ("IV",  "Results & Evaluation"),
    ("V",   "Conclusion & Future Work"),
]


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
                    fill_color: RGBColor,
                    line_color: RGBColor | None = None, line_width_pt: float = 0):
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

    stats: list of (value, label). hero_idx gets BLUE_TITLE; value_colors overrides per-stat.
    """
    left = MARGIN_LEFT if left is None else left
    width = CONTENT_W if width is None else width
    n = len(stats)
    col_w = int(width / n)
    for i, (val, label) in enumerate(stats):
        cx = left + i * col_w
        color = (value_colors[i] if value_colors and value_colors[i] is not None
                 else (BLUE_TITLE if i == hero_idx else DARK_TEXT))
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
    """<=4 short points, blue square marker + charcoal text. Returns bottom y.

    Density rule (spec section 4) is enforced here: more than 4 points raises.
    """
    if len(points) > 4:
        raise ValueError(f"talking points rule: max 4 per slide, got {len(points)}")
    y = top
    for text in points:
        _add_filled_box(slide, left, y + Inches(0.12), Inches(0.1), Inches(0.1), BLUE_TITLE)
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
    """Flat table: bold charcoal header over a blue hairline, PANEL/white zebra rows.

    cell_style: optional fn(r, c, text) -> (bold, RGBColor) for emphasis cells.
    """
    col_xs = [left]
    for w in col_ws[:-1]:
        col_xs.append(col_xs[-1] + w)
    for cx, cw, h in zip(col_xs, col_ws, header):
        _add_text_box(slide, cx + Inches(0.06), top, cw - Inches(0.12), Inches(0.34),
                      h, font_size=font_size, bold=True, color=DARK_TEXT)
    _add_filled_box(slide, left, top + Inches(0.36), sum(col_ws, Inches(0)),
                    Inches(0.025), BLUE_TITLE)
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


FLOW_STAGES = ["Applicant Context", "Bandit Policy", "Underwriting Action",
               "Actuarial Reward", "PSI Fairness + HITL", "Decision"]


def _add_overview_flowchart(slide, top, highlight=None, node_h=Inches(1.4)):
    """Single-row 6-node pipeline. `highlight` (str or list) gets a green outline box.

    Returns dict[stage_name] -> (left, top, width, height) for callers that overlay.
    """
    if isinstance(highlight, str):
        highlight = [highlight]
    highlight = highlight or []
    n = len(FLOW_STAGES)
    node_w = Inches(1.72)
    arrow_w = Inches(0.22)
    total = n * node_w + (n - 1) * arrow_w
    x0 = (SLIDE_WIDTH - total) / 2
    geom = {}
    x = x0
    for i, stage in enumerate(FLOW_STAGES):
        fill = NODE_START if i == 0 else NODE_END if i == n - 1 else BLUE_NODE
        txt_color = WHITE if i in (0, n - 1) else DARK_TEXT
        _add_filled_box(slide, x, top, node_w, node_h, fill,
                        line_color=BLUE_TITLE, line_width_pt=1.0)
        _add_text_box(slide, x + Inches(0.05), top, node_w - Inches(0.1), node_h,
                      stage, font_size=11, bold=True, color=txt_color,
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        geom[stage] = (x, top, node_w, node_h)
        if i < n - 1:
            arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + node_w,
                                         top + node_h / 2 - Inches(0.12),
                                         arrow_w, Inches(0.24))
            _flat(arr); _set_shape_fill(arr, BLUE_TITLE); _no_line(arr)
        x += node_w + arrow_w
    # green "you are here" outline around highlighted node(s)
    for stage in highlight:
        gx, gy, gw, gh = geom[stage]
        box = _add_filled_box(slide, gx - Inches(0.08), gy - Inches(0.08),
                              gw + Inches(0.16), gh + Inches(0.16), WHITE,
                              line_color=GREEN_HILITE, line_width_pt=3.0)
        box.fill.background()   # outline only
    return geom


def _add_buildup_stage(slide, top, stages):
    """Horizontal chain of (label, output_example) boxes; newest stage greened.

    stages: list[(label, output_example)]. The last item is highlighted as 'new'.
    """
    n = len(stages)
    box_w, box_h = Inches(3.5), Inches(1.5)
    arrow_w = Inches(0.45)
    total = n * box_w + (n - 1) * arrow_w
    x = (SLIDE_WIDTH - total) / 2 if total <= CONTENT_W else MARGIN_LEFT
    for i, (label, output) in enumerate(stages):
        newest = (i == n - 1)
        fill = PANEL
        edge = GREEN_HILITE if newest else BLUE_TITLE
        _add_filled_box(slide, x, top, box_w, box_h, fill,
                        line_color=edge, line_width_pt=2.5 if newest else 1.0)
        _add_text_box(slide, x + Inches(0.12), top + Inches(0.1), box_w - Inches(0.24),
                      Inches(0.6), label, font_size=14, bold=True,
                      color=GREEN_HILITE if newest else BLUE_TITLE,
                      align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
        _add_text_box(slide, x + Inches(0.12), top + Inches(0.72), box_w - Inches(0.24),
                      Inches(0.7), f"output:\n{output}", font_size=12, color=SOFT_TEXT,
                      align=PP_ALIGN.CENTER, font_name="Consolas")
        if i < n - 1:
            arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + box_w,
                                         top + box_h / 2 - Inches(0.13),
                                         arrow_w, Inches(0.26))
            _flat(arr); _set_shape_fill(arr, BLUE_TITLE); _no_line(arr)
        x += box_w + arrow_w


def _add_placeholder_image(slide, left, top, width, height, caption: str,
                           real_path: str | None = None):
    """Labeled swap-target frame. If real_path exists, embed it instead."""
    if real_path and os.path.exists(real_path):
        _add_picture_fit(slide, real_path, left, top, width, height)
        return
    _add_filled_box(slide, left, top, width, height, PANEL,
                    line_color=BLUE_TINT, line_width_pt=1.5)
    _add_text_box(slide, left, top, width, height,
                  f"[ PHOTO PLACEHOLDER ]\n\n{caption}\n\n(swap in a real photo before defense)",
                  font_size=14, color=GRAY_LABEL, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE, font_name=BODY_FONT)


def _add_demo_screenshot(slide, left, top, width, height, filename: str, caption: str):
    """Embed a real demo screenshot if present, else a labeled placeholder frame."""
    path = str(DEMO_SHOT_DIR / filename)
    if os.path.exists(path):
        _add_picture_fit(slide, path, left, top, width, height)
        _add_text_box(slide, left, top + height + Inches(0.02), width, Inches(0.3),
                      caption, font_size=11, italic=True, color=GRAY_LABEL,
                      align=PP_ALIGN.CENTER)
    else:
        _add_placeholder_image(slide, left, top, width, height,
                               f"Demo screenshot: {caption}")


# ===========================================================================
# Chrome (section tag, title, bottom bar)
# ===========================================================================

def _add_content_title(slide, text: str):
    """Centered ALL-CAPS bold steel-blue title + short centered underline."""
    box = _add_text_box(slide, MARGIN_LEFT, Inches(0.34), CONTENT_W, Inches(0.62),
                        text.upper(), font_size=26, bold=True, color=BLUE_TITLE,
                        align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
    box.text_frame.word_wrap = True
    # short centered underline
    rule_w = Inches(2.2)
    _add_filled_box(slide, (SLIDE_WIDTH - rule_w) / 2, Inches(1.02), rule_w,
                    Inches(0.04), BLUE_TITLE)


def _content_slide(prs, title: str, page_label: str):
    """Blank slide with centered title + underline + footer ribbon."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_content_title(slide, title)
    _add_footer_ribbon(slide, page_label)
    return slide


def _add_footer_ribbon(slide, page_label: str | None = None):
    """3-part footer: blue org block | center deck title (tint) | date + page (right)."""
    # left org block
    _add_filled_box(slide, Inches(0), FOOTER_TOP, Inches(3.4), FOOTER_HEIGHT, BLUE_DEEP)
    _add_text_box(slide, Inches(0.18), FOOTER_TOP, Inches(3.1), FOOTER_HEIGHT,
                  "DAC  ·  ITC-AMS", font_size=11, bold=True, color=WHITE,
                  font_name=HEAD_FONT, anchor=MSO_ANCHOR.MIDDLE)
    # center deck-title block (lighter tint, dark text for contrast)
    _add_filled_box(slide, Inches(3.4), FOOTER_TOP, Inches(6.7), FOOTER_HEIGHT, BLUE_TINT)
    _add_text_box(slide, Inches(3.5), FOOTER_TOP, Inches(6.5), FOOTER_HEIGHT,
                  "Adaptive Underwriting via Contextual Bandits", font_size=11,
                  color=BLUE_DEEP, font_name=BODY_FONT, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE)
    # right date + page block
    _add_filled_box(slide, Inches(10.1), FOOTER_TOP, Inches(3.233), FOOTER_HEIGHT, BLUE_DEEP)
    page = f"July 2026   ·   {page_label}" if page_label else "July 2026"
    _add_text_box(slide, Inches(10.2), FOOTER_TOP, Inches(3.0), FOOTER_HEIGHT,
                  page, font_size=11, bold=True, color=WHITE, font_name=HEAD_FONT,
                  align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def _add_divider(prs, number: str, name: str, page_label: str):
    """Full-bleed cobalt divider: big 'N.' over the section name, left-aligned."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_filled_box(slide, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT, BLUE_DIVIDER)
    _add_text_box(slide, Inches(0.9), Inches(2.35), Inches(11.0), Inches(1.6),
                  f"{number}.", font_size=120, bold=True, color=WHITE,
                  font_name=HEAD_FONT, anchor=MSO_ANCHOR.MIDDLE)
    _add_filled_box(slide, Inches(1.0), Inches(4.15), Inches(3.2), Inches(0.06), WHITE)
    _add_text_box(slide, Inches(0.95), Inches(4.35), Inches(11.4), Inches(0.9),
                  name, font_size=32, bold=True, color=WHITE, font_name=HEAD_FONT)
    _add_footer_ribbon(slide, page_label)
    return slide


def _pg(n: int) -> str:
    """Footer page label for a presented (main) slide: 'n / 27'."""
    return f"{n} / 27"


def _stub(prs, title, page_label):
    slide = _content_slide(prs, title, page_label)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.5), CONTENT_W, Inches(1.0),
                  "[ content pending ]", font_size=18, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
    _add_notes(slide, "Stub — content filled in a later task. " + title)
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

    _add_filled_box(slide, Inches(5.92), Inches(2.05), Inches(1.5), Inches(0.045), BLUE_TITLE)
    box = _add_text_box(slide, Inches(0.9), Inches(2.35), Inches(11.5), Inches(1.7),
                        THESIS_TITLE.upper(), font_size=27, bold=True, color=DARK_TEXT,
                        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                        font_name=HEAD_FONT)
    box.text_frame.word_wrap = True
    _add_filled_box(slide, Inches(5.92), Inches(4.25), Inches(1.5), Inches(0.045), BLUE_TITLE)

    _add_text_box(slide, Inches(0), Inches(4.62), SLIDE_WIDTH, Inches(0.34),
                  "Thesis Defense — Presented by", font_size=14, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(4.96), SLIDE_WIDTH, Inches(0.5),
                  PRESENTER, font_size=27, bold=True, color=BLUE_TITLE,
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
    _add_footer_ribbon(slide, "1 / 27")


# ===========================================================================
# Slide 2 -- Table of Contents
# ===========================================================================

def slide_toc(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_content_title(slide, "Table of Contents")
    row_h = Inches(1.0)
    top = CONTENT_TOP + Inches(0.2)
    for i, (num, name) in enumerate(SECTIONS):
        y = top + i * row_h
        _add_text_box(slide, Inches(2.2), y, Inches(1.4), Inches(0.7),
                      num, font_size=34, bold=True, color=BLUE_TITLE, font_name=HEAD_FONT)
        _add_text_box(slide, Inches(3.7), y + Inches(0.08), Inches(7.4), Inches(0.6),
                      name, font_size=22, bold=True, color=DARK_TEXT, font_name=HEAD_FONT)
        _add_filled_box(slide, Inches(3.7), y + Inches(0.72), Inches(7.0),
                        Inches(0.012), HAIRLINE)
    _add_footer_ribbon(slide, "2 / 27")

def slide_thanks(prs: Presentation):
    """Slide 23."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_filled_box(slide, Inches(5.92), Inches(2.0), Inches(1.5), Inches(0.045), BLUE_TITLE)
    _add_text_box(slide, Inches(0), Inches(2.35), SLIDE_WIDTH, Inches(1.0),
                  "Thank you.", font_size=54, bold=True, color=BLUE_TITLE,
                  align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
    _add_text_box(slide, Inches(0), Inches(3.45), SLIDE_WIDTH, Inches(0.5),
                  "Questions & Answers", font_size=20, color=BLUE_TITLE,
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
    _add_footer_ribbon(slide, "27 / 27")


# ===========================================================================
# Stub aliases — v3 inventory (content filled in Tasks 12-17)
# ===========================================================================

def slide_about_company(prs):
    slide = _content_slide(prs, "About Decent Actuarial Consultants", _pg(2))
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.2), Inches(6.2), [
        "DAC is a Phnom Penh actuarial consultancy",
        "Clients: insurers, pension funds, regulators across SE Asia",
        "This thesis is a DAC-supervised research internship (Mar–Jun 2026)",
        "Deliverable: an adaptive underwriting prototype + this report",
    ])
    _add_placeholder_image(slide, Inches(7.1), CONTENT_TOP + Inches(0.1),
                           Inches(5.7), Inches(4.4), "Phnom Penh — DAC office",
                           real_path=LOGO_DAC)
    _add_notes(slide,
        "Decent Actuarial Consultants is a Phnom Penh actuarial consultancy serving "
        "insurers, pension funds and regulators across Southeast Asia. The thesis is "
        "embedded in a DAC-supervised research internship, March through June 2026; the "
        "deliverable is the end-to-end adaptive underwriting prototype plus this report. "
        "Timeline: March scoping and dataset design, April algorithms, May experiments, "
        "June writing and defense preparation.")
    return slide


def slide_introduction(prs):
    slide = _content_slide(prs, "Introduction", _pg(3))
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(6.0), Inches(0.9),
                  "< 10 %", font_size=56, bold=True, color=BLUE_TITLE, font_name=HEAD_FONT)
    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.95), Inches(6.0),
                        Inches(0.36), "HEALTH-INSURANCE PENETRATION IN CAMBODIA (2023 EST.)",
                        font_size=10, color=GRAY_LABEL)
    _letterspace(lab.text_frame.paragraphs[0], 80)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.6), Inches(6.0), [
        "NSSF covers formal-sector workers only (~16%)",
        "Private underwriting is manual and rule-based",
        "Static rules never learn from outcomes",
        "No demographic-parity monitoring in practice",
    ])
    _add_placeholder_image(slide, Inches(7.1), CONTENT_TOP, Inches(5.7), Inches(4.6),
                           "Cambodian clinic / insurance context")
    _add_notes(slide,
        "Cambodia context: the National Social Security Fund covers only formal-sector "
        "workers, roughly 16 percent; private voluntary insurance is nascent and "
        "underwriting is mostly manual and rule-based. Actuaries apply fixed premium rules "
        "without learning from outcomes, suboptimal decisions compound over a growing "
        "applicant pool, and penetration is below 10 percent (2023 estimate). The "
        "opportunity: a contextual bandit learns online from each decision while a PSI "
        "guardrail watches demographic fairness.")
    return slide


def slide_problem_statement(prs):
    slide = _content_slide(prs, "Problem Statement", _pg(4))
    problems = [
        ("Static thresholds", "Fixed cutoffs ignore applicant context"),
        ("No online adaptation", "Claims feedback never reaches the model"),
        ("Demographic blindspot", "No parity metric is tracked"),
        ("No triage", "Experts review routine, not borderline, cases"),
    ]
    card_w, card_h = Inches(6.0), Inches(2.3)
    positions = [
        (MARGIN_LEFT,               CONTENT_TOP + Inches(0.2)),
        (MARGIN_LEFT + Inches(6.4), CONTENT_TOP + Inches(0.2)),
        (MARGIN_LEFT,               CONTENT_TOP + Inches(2.75)),
        (MARGIN_LEFT + Inches(6.4), CONTENT_TOP + Inches(2.75)),
    ]
    for (title, desc), (lx, ly) in zip(problems, positions):
        _add_filled_box(slide, lx, ly, card_w, card_h, PANEL)
        _add_filled_box(slide, lx, ly, Inches(0.07), card_h, BLUE_TITLE)
        _add_text_box(slide, lx + Inches(0.3), ly + Inches(0.3),
                      card_w - Inches(0.6), Inches(0.5),
                      title, font_size=20, bold=True, color=DARK_TEXT, font_name=HEAD_FONT)
        _add_text_box(slide, lx + Inches(0.3), ly + Inches(0.95),
                      card_w - Inches(0.6), Inches(1.1),
                      desc, font_size=15, color=SOFT_TEXT)
    _add_notes(slide,
        "Four concrete failures of the status quo. One: fixed age/BMI/income cutoffs "
        "ignore context, so a misclassified high-risk applicant generates uncorrected "
        "losses. Two: the claims signal is never fed back, so accuracy degrades silently "
        "as demographics shift. Three: no parity metric is tracked, so regional or "
        "occupational concentration can develop undetected. Four: there is no triage - "
        "actuaries spend time on high-volume routine cases instead of genuine edge cases.")
    return slide


def slide_project_objective(prs):
    slide = _content_slide(prs, "Project Objective", _pg(5))
    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(4.0), Inches(0.32),
                        "RESEARCH GOAL", font_size=11, bold=True, color=BLUE_TITLE)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.38), CONTENT_W, Inches(0.75),
                  "Design and evaluate an adaptive health insurance underwriting system using "
                  "contextual bandit algorithms on a synthetic Cambodia applicant dataset, "
                  "incorporating demographic fairness monitoring and human-in-the-loop augmentation.",
                  font_size=15, color=DARK_TEXT)
    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.35), Inches(4.0),
                        Inches(0.32), "OBJECTIVES", font_size=11, bold=True, color=BLUE_TITLE)
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
                      label, font_size=20, bold=True, color=BLUE_TITLE, font_name=HEAD_FONT)
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
    return slide
def slide_literature_review(prs):
    slide = _content_slide(prs, "Literature Review", _pg(6))
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
    return slide
def slide_methodology_overview(prs):
    slide = _content_slide(prs, "Methodology Overview", _pg(8))
    _add_overview_flowchart(slide, CONTENT_TOP + Inches(0.3), highlight=None)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.4), CONTENT_W, Inches(1.6),
                  "Each applicant flows left to right: their context drives a bandit policy "
                  "that picks an underwriting action; the actuarial simulator returns a "
                  "reward that updates the policy; a PSI guardrail and a human-in-the-loop "
                  "wrapper watch fairness before the final decision.",
                  font_size=16, color=SOFT_TEXT)
    _add_notes(slide, "Walk the whole pipeline once, left to right, naming each of the six "
               "stages. Tell the panel we will now zoom into three of them in turn.")
    return slide


def slide_zoom_dataset(prs):
    slide = _content_slide(prs, "Zoom-in: Dataset & Context", _pg(9))
    _add_overview_flowchart(slide, CONTENT_TOP, highlight="Applicant Context",
                            node_h=Inches(0.95))
    _add_stat_row(slide, CONTENT_TOP + Inches(1.3), [
        ("2,000", "synthetic applications"),
        ("5", "demographic features"),
        ("4", "underwriting arms"),
        ("4", "anchoring sources"),
    ])
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.6), Inches(6.2), [
        "Anchored on CDHS, STEPS, ILO, WHO data",
        "Adverse selection AF = 1.35; elasticity 3.5",
        "Fully synthetic — no real applicant PII",
    ])
    arms = [("RATED", "Accept + premium loading (+25%)"),
            ("STANDARD", "Accept at standard premium"),
            ("DECLINE", "Reject application"),
            ("REFER", "Escalate to human underwriter")]
    ay = CONTENT_TOP + Inches(2.5)
    for i, (arm, desc) in enumerate(arms):
        ry = ay + i * Inches(0.6)
        _add_text_box(slide, Inches(7.3), ry, Inches(1.9), Inches(0.4), arm,
                      font_size=14, bold=True, color=BLUE_TITLE)
        _add_text_box(slide, Inches(9.2), ry + Inches(0.02), Inches(3.6), Inches(0.5),
                      desc, font_size=12, color=SOFT_TEXT)
    _add_notes(slide,
        "The dataset is 2,000 synthetic applicants with five features: age, sex, region, "
        "occupation, BMI. Distributions are anchored on CDHS 2021-22 and STEPS 2021; "
        "income on ILO labour-force surveys; claim probabilities calibrated from WHO SEARO "
        "health-expenditure data. Adverse-selection factor 1.35 and price-elasticity slope "
        "3.5 come from DAC actuarial priors. Four arms: RATED accepts with a 25 percent "
        "loading, STANDARD accepts at standard rate, DECLINE rejects, REFER escalates to a "
        "human. No real applicant data is used anywhere.")
    return slide


def slide_reward_simulator(prs):
    slide = _content_slide(prs, "Reward Simulator", _pg(10))
    defs = [
        ("Context  x_t ∈ R^5", "age, sex, region, occupation, BMI -- standardised"),
        ("Action  a_t", "one of RATED / STANDARD / DECLINE / REFER"),
        ("Reward  r_t", "revenue minus claims, actuarial simulator"),
    ]
    dy = CONTENT_TOP + Inches(0.15)
    for i, (term, desc) in enumerate(defs):
        ry = dy + i * Inches(0.95)
        _add_text_box(slide, MARGIN_LEFT, ry, Inches(2.9), Inches(0.45),
                      term, font_size=16, bold=True, color=BLUE_TITLE)
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
    return slide


def slide_zoom_bandit(prs):
    slide = _content_slide(prs, "Zoom-in: Bandit Policy", _pg(11))
    _add_overview_flowchart(slide, CONTENT_TOP, highlight="Bandit Policy",
                            node_h=Inches(0.95))
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.4), CONTENT_W, Inches(1.0),
                  "We now build the bandit policy one component at a time — context in, "
                  "value estimates, then selection — each step with a concrete output.",
                  font_size=17, color=SOFT_TEXT, align=PP_ALIGN.CENTER)
    _add_notes(slide, "Signpost the build-up: three slides, each adds one box to the "
               "policy and shows what that box outputs for a single applicant.")
    return slide


def slide_buildup_context(prs):
    slide = _content_slide(prs, "Bandit Build-up: Context", _pg(12))
    _add_buildup_stage(slide, CONTENT_TOP + Inches(0.5), [
        ("Context vector  x_t ∈ R^5", "[age 0.4, sex -1.1, region 0, occ 2, BMI 0.8]"),
    ])
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.6), CONTENT_W, [
        "Five standardised features: age, sex, region, occupation, BMI",
        "This is the bandit's only view of each applicant",
    ])
    _add_notes(slide, "Start the build-up with the input: the standardised five-feature "
               "context vector — show the example numbers.")
    return slide


def slide_buildup_estimates(prs):
    slide = _content_slide(prs, "Bandit Build-up: Value Estimates", _pg(13))
    _add_buildup_stage(slide, CONTENT_TOP + Inches(0.5), [
        ("Context  x_t", "[0.4, -1.1, 0, 2, 0.8]"),
        ("Per-arm value\n(LinUCB / LinTS)", "RATED 0.31 · STD 0.52 · DEC 0.10 · REF 0.28"),
    ])
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(2.6), CONTENT_W, [
        "LinUCB: θ̂ᵀx + α·√(xᵀA⁻¹x)  — optimism under uncertainty",
        "LinTS: sample θ̃ from the posterior — exploration by randomisation",
    ])
    _add_notes(slide, "Add the value-estimation box: each arm gets a score; explain the "
               "LinUCB optimism bonus and the LinTS posterior sample.")
    return slide


def slide_buildup_action(prs):
    slide = _content_slide(prs, "Bandit Build-up: Selection & Action", _pg(14))
    _add_buildup_stage(slide, CONTENT_TOP + Inches(0.3), [
        ("Context  x_t", "[0.4, -1.1, 0, 2, 0.8]"),
        ("Per-arm value", "RATED 0.31 · STD 0.52 · DEC 0.10 · REF 0.28"),
        ("argmax → action\n+ reward update", "STANDARD; r_t = +premium − claims; A←A+xxᵀ"),
    ])
    algos = [
        (ACCENT_GREEN, "LinUCB / LinTS", "the two proposed admissible policies"),
        (ACCENT_AMBER, "ε-Greedy", "naive explorer — provably worse O(T^2/3)"),
        (MED_GRAY,     "Static XGB", "train-once incumbent baseline"),
        (ACCENT_RED,   "AlwaysRATED", "constant +25% loading — inadmissible ceiling"),
    ]
    ay = CONTENT_TOP + Inches(2.4)
    for i, (color, name, desc) in enumerate(algos):
        ry = ay + i * Inches(0.52)
        _add_filled_box(slide, MARGIN_LEFT, ry + Inches(0.04), Inches(0.16), Inches(0.34), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), ry, Inches(3.0), Inches(0.42),
                      name, font_size=15, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(3.6), ry + Inches(0.03), Inches(8.6),
                      Inches(0.42), desc, font_size=14, color=SOFT_TEXT)
    _add_footnote(slide,
        "Admissibility (§5.0.1): deployable AND commercially/regulatorily viable. "
        "AlwaysRATED is the inadmissible ceiling; LinUCB/LinTS are the top-2 admissible policies.")
    _add_notes(slide,
        "Two proposed policies and three reference points. LinUCB plays optimism in the "
        "face of uncertainty over a linear reward model with the square-root-T regret "
        "bound; LinTS samples from the posterior and is near-optimal with naturally "
        "calibrated uncertainty. Epsilon-greedy is the naive explorer with provably worse "
        "T-to-the-two-thirds regret. Static XGB is the train-once incumbent. AlwaysRATED "
        "rates everyone at +25 percent loading - it scores highest but is neither "
        "commercially nor regulatorily viable, which is exactly the admissibility "
        "distinction in section 5.0.1 and the baseline-ladder appendix (A1).")
    return slide


def slide_zoom_fairness(prs):
    slide = _content_slide(prs, "Zoom-in: Fairness Guardrail & HITL", _pg(15))
    _add_overview_flowchart(slide, CONTENT_TOP, highlight="PSI Fairness + HITL",
                            node_h=Inches(0.95))
    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.25), Inches(5.9),
                        Inches(0.32), "PSI DEMOGRAPHIC GUARDRAIL", font_size=11, bold=True,
                        color=BLUE_TITLE)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    psi_zones = [
        (ACCENT_GREEN, "GREEN", "PSI < 0.10", "stable"),
        (ACCENT_AMBER, "AMBER", "0.10-0.25", "monitor"),
        (ACCENT_RED,   "RED",   "PSI ≥ 0.25", "review"),
    ]
    zy = CONTENT_TOP + Inches(1.75)
    for color, label, threshold, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(0.16), Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), zy, Inches(1.5), Inches(0.5),
                      label, font_size=16, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.0), zy + Inches(0.04),
                      Inches(2.1), Inches(0.45), threshold, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.2), zy + Inches(0.04),
                      Inches(1.7), Inches(0.45), action, font_size=14, color=SOFT_TEXT)
        zy += Inches(0.62)
    _add_text_box(slide, MARGIN_LEFT, zy + Inches(0.05), Inches(5.9), Inches(0.6),
                  "Computed on region & occupation, rolling 500-round window.",
                  font_size=13, color=SOFT_TEXT)
    lab = _add_text_box(slide, Inches(7.1), CONTENT_TOP + Inches(1.25), Inches(5.7),
                        Inches(0.32), "HUMAN-IN-THE-LOOP WRAPPER", font_size=11, bold=True,
                        color=BLUE_TITLE)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(7.1), CONTENT_TOP + Inches(1.75), Inches(5.7), [
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
    return slide
def slide_headline_benchmark(prs):
    slide = _content_slide(prs, "Headline Benchmark", _pg(16))
    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_loglog_regret.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.1),
                     Inches(6.6), CONTENT_H - Inches(0.5))
    rows = [(str(r["rank"]), r["algorithm"], f"${r['reward']:,}")
            for r in _E007["ranking"]]
    def _rank_style(i, c, text):
        top2 = i < 2
        return (top2, BLUE_TITLE if top2 else DARK_TEXT)
    _add_flat_table(slide, Inches(7.5), CONTENT_TOP + Inches(0.35),
                    [Inches(0.8), Inches(2.4), Inches(2.1)],
                    ["#", "Algorithm", "Reward"],
                    rows, font_size=14, row_h=Inches(0.62), cell_style=_rank_style)
    _add_text_box(slide, Inches(7.5), CONTENT_TOP + Inches(3.5), Inches(5.3), Inches(0.8),
                  f"Log-log regret slope {_E013['slope']} (R² = {_E013['r2']}) -- "
                  "sub-linear, consistent with O(√T·d).",
                  font_size=14, color=DARK_TEXT)
    _add_footnote(slide,
        f"Scope: admissible policies only (§5.0.1). LinTS vs LinUCB p = "
        f"{_E007['lints_vs_linucb_p']} (n.s. — tied at 20 seeds); same CRN harness.")
    _add_notes(slide,
        f"All four algorithms under common random numbers. LinTS ranks first at "
        f"${_E007['ranking'][0]['reward']:,}, LinUCB second at "
        f"${_E007['ranking'][1]['reward']:,} - statistically tied "
        f"(p = {_E007['lints_vs_linucb_p']}). Epsilon-greedy trails, static XGB last. "
        f"The log-log plot validates theory: fitted slope {_E013['slope']} with R squared "
        f"{_E013['r2']}, close to the 0.5 of the O(root-T d) bound - the bandit's regret "
        f"really is sub-linear, it is learning, not memorising.")
    return slide


def slide_convergence_regret(prs):
    slide = _content_slide(prs, "Convergence & Regret", _pg(17))
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
        f"5.0.1 - the inadmissible AlwaysRATED constant sits above (appendix A1). Oracle "
        f"recovery is {_E005['oracle_reward_recovered_pct']} percent.")
    return slide


def slide_coldstart_hitl(prs):
    slide = _content_slide(prs, "Cold-start & Human-in-the-Loop", _pg(18))
    w = _E010["wilcoxon_t2000"]
    lints, linucb = w["lints_vs_freshxgb"], w["linucb_vs_freshxgb"]
    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        (f"p = {lints['p']}", "lints PASSED @ t=2,000"),
        (f"p = {linucb['p']:.4f}", "linucb draws level @ t=2,000"),
        (f"+{_E008['lift_pct']}%", "hitl lift vs vanilla bandit"),
        (f"{_E008['referral_pct']}%", "referral rate"),
    ], value_colors=[ACCENT_GREEN, ACCENT_AMBER, ACCENT_GREEN, DARK_TEXT])
    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_cold_start.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     Inches(6.4), CONTENT_H - Inches(1.7))
    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_hitl.png"),
                     Inches(7.0), CONTENT_TOP + Inches(1.25),
                     Inches(5.8), CONTENT_H - Inches(1.7))
    _add_footnote(slide,
        f"Only LinTS is certified at T = 2,000 (p = {lints['p']}); LinUCB's lead is not "
        f"significant (p = {linucb['p']:.4f}, d = {linucb['d']}) and is reported as 'draws level'. "
        f"HITL +{_E008['lift_pct']}% is vs the vanilla bandit, not the AlwaysRATED ceiling (§5.4.2).")
    _add_notes(slide,
        f"Two results on one slide. Cold-start (EXP-010): below a thousand rounds a freshly "
        f"trained XGBoost beats both bandits; the crossover comes between one and two "
        f"thousand. At T=2,000 LinTS is significant at the Bonferroni threshold "
        f"(p = {lints['p']}, d = {lints['d']}); LinUCB's lead is positive but NOT significant "
        f"(p = {linucb['p']:.4f}, d = {linucb['d']}) - softened to 'draws level'. Deploy with "
        f"warm-start for the first thousand applications. Human-in-the-loop (EXP-008): the "
        f"wrapper lifts reward {_E008['lift_pct']} percent over the vanilla bandit "
        f"(${_E008['hitl_reward']:,} vs ${_E008['baseline_reward']:,}, p {_E008['lift_p']}, "
        f"d = {_E008['lift_cohen_d']}) at only {_E008['referral_pct']} percent referrals and "
        f"{_E008['human_cost_pct_of_reward']} percent review cost. Both scopes are against "
        f"admissible comparators, not the AlwaysRATED ceiling.")
    return slide


def slide_fairness_drift(prs):
    slide = _content_slide(prs, "Fairness Audit & Drift", _pg(19))
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), Inches(6.4), Inches(0.45),
                  "5 of 6 fairness criteria PASSED", font_size=18, bold=True, color=DARK_TEXT)
    for col_i, (attr, data) in enumerate([("Region", _E006["region"]),
                                          ("Occupation", _E006["occupation"])]):
        cx = MARGIN_LEFT + col_i * Inches(3.3)
        zone_color = ACCENT_GREEN if data["psi_zone"] == "GREEN" else ACCENT_AMBER
        verdict = data["permutation_verdict"]
        rows = [
            ("PSI zone", f"{data['psi_zone']} ({data['psi_max_sliding']:.4f})"),
            ("EEOC parity", f"{data['parity_pct']}%"),
            ("Crit. 6", verdict),
        ]
        def _style(i, c, text, _zone=zone_color, _verdict=verdict):
            if c == 1 and i == 0:
                return (True, _zone)
            if c == 1 and i == 2:
                return (True, ACCENT_GREEN if _verdict == "PASSED" else ACCENT_RED)
            return (c == 1, DARK_TEXT)
        _add_text_box(slide, cx, CONTENT_TOP + Inches(0.6), Inches(3.1), Inches(0.4),
                      attr, font_size=15, bold=True, color=BLUE_TITLE)
        _add_flat_table(slide, cx, CONTENT_TOP + Inches(1.05),
                        [Inches(1.5), Inches(1.6)], ["Check", "Result"],
                        rows, font_size=12, row_h=Inches(0.6), cell_style=_style)
    _add_text_box(slide, Inches(8.0), CONTENT_TOP + Inches(0.4), Inches(4.8), Inches(0.4),
                  "Drift: post/pre regret ratio (shock @ 1,500)", font_size=14, bold=True,
                  color=BLUE_TITLE)
    drows = [(r["algorithm"], f"{r['post_pre_ratio']}×") for r in _E009["rows"]]
    def _ratio_style(i, c, text):
        if c == 1:
            good = float(text.rstrip("×")) < 0.5
            return (True, ACCENT_GREEN if good else ACCENT_AMBER)
        return (False, DARK_TEXT)
    _add_flat_table(slide, Inches(8.0), CONTENT_TOP + Inches(0.95),
                    [Inches(2.6), Inches(2.0)], ["Algorithm", "Ratio"],
                    drows, font_size=13, row_h=Inches(0.58), cell_style=_ratio_style)
    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.5), CONTENT_W, Inches(0.85),
                 "Occupation association reflects actuarially justified risk differences "
                 "(§5.2.4); no regulatory threshold (EEOC 80%, PSI 0.25) is breached.",
                 font_size=13)
    _add_footnote(slide,
        f"Criterion 6 (occupation→action) FAILED-with-interpretation: "
        f"p {_E006['occupation']['permutation_p']} — statistically significant but "
        f"practically small. Reported honestly.")
    _add_notes(slide,
        f"Fairness audit (EXP-006): Region PSI GREEN at "
        f"{_E006['region']['psi_max_sliding']}, parity {_E006['region']['parity_pct']} "
        f"percent, PASSED (p = {_E006['region']['permutation_p']}). Occupation PSI AMBER at "
        f"{_E006['occupation']['psi_max_sliding']} - within the 0.25 threshold - parity "
        f"{_E006['occupation']['parity_pct']} percent, above the EEOC 80 floor. Criterion 6 "
        f"is the single failure: occupation-action association is statistically significant "
        f"but practically small, and occupation is an actuarially valid factor; marked "
        f"FAILED-with-interpretation in the interest of honesty. Drift (EXP-009): at the "
        f"round-1,500 shock both bandits re-converge toward pre-shock regret while static "
        f"XGB lags; sustained-drift handling is future work.")
    return slide


def slide_live_demo(prs):
    slide = _content_slide(prs, "Live Demonstration", _pg(20))
    shots = [("shot_dashboard.png", "Applicant scoring & bandit arm selection"),
             ("shot_pricing.png",   "Premium optimiser & pricing curve"),
             ("shot_hitl.png",      "Human-in-the-loop referral queue & cost")]
    w = Inches(4.0); h = Inches(3.0); gap = Inches(0.25)
    x0 = (SLIDE_WIDTH - (3 * w + 2 * gap)) / 2
    for i, (fn, cap) in enumerate(shots):
        _add_demo_screenshot(slide, x0 + i * (w + gap), CONTENT_TOP + Inches(0.5),
                             w, h, fn, cap)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.0), CONTENT_W, Inches(0.45),
                  "Same FastAPI stack as the architecture — live at localhost:8000",
                  font_size=15, italic=True, color=GRAY_LABEL, align=PP_ALIGN.CENTER)
    _add_notes(slide, "Switch to the browser and walk one applicant through scoring, the "
               "arm the bandit picks, the PSI monitor, and the HITL queue. If the live run "
               "fails, narrate over these three screenshots.")
    return slide
def slide_conclusion(prs):        return _stub(prs, "Conclusion", _pg(21))
def slide_app_ladder(prs):        return _stub(prs, "A1  Baseline Ladder", "A1")
def slide_app_reconciliation(prs): return _stub(prs, "A2  Number Reconciliation", "A2")
def slide_app_criteria_matrix(prs): return _stub(prs, "A3  Criteria Verdicts", "A3")
def slide_app_sensitivity(prs):   return _stub(prs, "A4  Sensitivity and Ablation", "A4")
def slide_app_math_psi(prs):      return _stub(prs, "A5  Bandit Math and PSI", "A5")


def main():
    prs = Presentation()
    prs.slide_width  = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    slide_title(prs)                                  # 0  Title
    slide_toc(prs)                                    # 1  ToC
    _add_divider(prs, "I", "Introduction & Problem Background", _pg(1))   # 2
    slide_about_company(prs)                          # 3  About DAC
    slide_introduction(prs)                           # 4  Introduction
    slide_problem_statement(prs)                      # 5  Problem
    slide_project_objective(prs)                      # 6  O1-O4
    _add_divider(prs, "II", "Literature Review", _pg(7))                  # 7
    slide_literature_review(prs)                      # 8  Lit table
    _add_divider(prs, "III", "Methodology & Model Design", _pg(9))       # 9
    slide_methodology_overview(prs)                   # 10 overview flowchart
    slide_zoom_dataset(prs)                           # 11 zoom 1
    slide_reward_simulator(prs)                       # 12 reward
    slide_zoom_bandit(prs)                            # 13 zoom 2
    slide_buildup_context(prs)                        # 14 build-up A
    slide_buildup_estimates(prs)                      # 15 build-up B
    slide_buildup_action(prs)                         # 16 build-up C (AlwaysRATED)
    slide_zoom_fairness(prs)                          # 17 zoom 3 (PSI+HITL)
    _add_divider(prs, "IV", "Results & Evaluation", _pg(18))             # 18
    slide_headline_benchmark(prs)                     # 19 EXP-007 (§5.0.1)
    slide_convergence_regret(prs)                     # 20 EXP-005/013 (§5.0.1)
    slide_coldstart_hitl(prs)                         # 21 EXP-008/010 (0.0840)
    slide_fairness_drift(prs)                         # 22 EXP-006/009 (FAILED-with-interpretation)
    slide_live_demo(prs)                              # 23 demo screenshots
    _add_divider(prs, "V", "Conclusion & Future Work", _pg(24))         # 24
    slide_conclusion(prs)                             # 25 O1-O4 scorecard
    slide_thanks(prs)                                 # 26 Thank You

    # ---- Appendix (backup, not walked) ----
    slide_app_ladder(prs)                             # 27 A1 (FALSIFIED, AlwaysRATED)
    slide_app_reconciliation(prs)                     # 28 A2
    slide_app_criteria_matrix(prs)                    # 29 A3
    slide_app_sensitivity(prs)                        # 30 A4
    slide_app_math_psi(prs)                           # 31 A5

    assert len(prs.slides) == 32, f"Expected 32 slides, got {len(prs.slides)}"
    prs.save(OUTPUT_PATH)
    print(f"Saved {len(prs.slides)} slides -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
