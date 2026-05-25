"""
Generate a thesis defense presentation in the burgundy style
similar to Rith Chanthyda's slides.

Run: python thesis/health_rl/build_burgundy_presentation.py
Output: thesis/health_rl/burgundy_defense_presentation.pptx
"""
from __future__ import annotations

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
import os

# ─── Configuration ───
OUTPUT_PATH = r"C:\DAC-UW-Thesis\thesis\health_rl\burgundy_defense_presentation.pptx"
LOGO_ITC = r"C:\DAC-UW-Thesis\thesis\ITC.jpg"
LOGO_AMS = r"C:\DAC-UW-Thesis\thesis\AMS.png"
LOGO_DAC = r"C:\DAC-UW-Thesis\thesis\DAC.jpg"

# Colors (burgundy theme sampled from the reference slides)
BURGUNDY = RGBColor(0x5D, 0x2A, 0x42)   # primary accent
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = RGBColor(0x1A, 0x1A, 0x1A)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
MEDIUM_GRAY = RGBColor(0x80, 0x80, 0x80)

# Slide dimensions (16:9)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Content bounds
MARGIN_LEFT = Inches(0.5)
MARGIN_RIGHT = Inches(0.5)
MARGIN_TOP = Inches(0.6)
CONTENT_TOP = Inches(1.1)
BOTTOM_BAR_TOP = Inches(6.85)
BOTTOM_BAR_HEIGHT = Inches(0.65)

# Thesis info
THESIS_TITLE = "Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"
SHORT_TITLE = "Adaptive Health Insurance Underwriting via Contextual Bandits"
PRESENTER = "LUN CHANPOLY"
SUPERVISOR = "Dr. HAS Sothea"
CO_SUPERVISOR = "Mr. PHOK Ponna"  # placeholder – update if needed
ORGANIZATION = "DAC (Decent Actuarial Consultants)"
DEPARTMENT = "Department of Applied Mathematics and Statistics"
INSTITUTION = "Institute of Technology of Cambodia"
DURATION = "March 2026 – May 2026"
DEFENSE_DATE = "June 2026"

SECTIONS = [
    ("1", "INTRODUCTION"),
    ("2", "LITERATURE REVIEW"),
    ("3", "METHODOLOGY"),
    ("4", "RESULTS AND DISCUSSION"),
    ("5", "DEMONSTRATION"),
    ("6", "CONCLUSION"),
]

BREADCRUMB = "Introduction → Literature Review → Methodology → Results → Demo → Conclusion"


def _set_shape_fill(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def _set_text_frame_props(tf, font_name: str = "Calibri", color: RGBColor = DARK_TEXT):
    for paragraph in tf.paragraphs:
        paragraph.font.name = font_name
        paragraph.font.color.rgb = color


def _add_text_box(slide, left, top, width, height, text: str,
                  font_size: int = 18, bold: bool = False,
                  color: RGBColor = DARK_TEXT, align=PP_ALIGN.LEFT,
                  font_name: str = "Calibri"):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    box.fill.background()
    box.line.fill.background()
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    return box


def _add_bottom_bar(slide, page_num: str | None = None):
    """Maroon bottom bar with breadcrumb, logos, page number."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), BOTTOM_BAR_TOP,
        SLIDE_WIDTH, BOTTOM_BAR_HEIGHT
    )
    _set_shape_fill(bar, BURGUNDY)
    bar.line.fill.background()

    # Breadcrumb text (left side, inside bar)
    bread = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.4), BOTTOM_BAR_TOP + Inches(0.15),
        Inches(9.5), Inches(0.35)
    )
    bread.fill.background()
    bread.line.fill.background()
    tf = bread.text_frame
    p = tf.paragraphs[0]
    p.text = BREADCRUMB
    p.font.size = Pt(16)
    p.font.color.rgb = WHITE
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.LEFT

    # Page number (right side)
    if page_num:
        pg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(11.8), BOTTOM_BAR_TOP + Inches(0.15),
            Inches(1.2), Inches(0.35)
        )
        pg.fill.background()
        pg.line.fill.background()
        tf = pg.text_frame
        p = tf.paragraphs[0]
        p.text = f"Page {page_num}"
        p.font.size = Pt(16)
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.RIGHT

    # Small logos in bottom-right corner (inside white area above bar)
    # We place them just above the bar on the right side
    if os.path.exists(LOGO_ITC):
        slide.shapes.add_picture(LOGO_ITC, Inches(10.5), Inches(6.35), width=Inches(0.7))
    if os.path.exists(LOGO_DAC):
        slide.shapes.add_picture(LOGO_DAC, Inches(11.3), Inches(6.35), width=Inches(0.7))


def _add_top_right_header(slide):
    """Thesis title + presenter name in top-right corner."""
    box = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(7.5), Inches(0.15),
        Inches(5.2), Inches(0.7)
    )
    box.fill.background()
    box.line.fill.background()
    tf = box.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = SHORT_TITLE
    p1.font.size = Pt(14)
    p1.font.color.rgb = BURGUNDY
    p1.font.name = "Calibri"
    p1.alignment = PP_ALIGN.RIGHT

    p2 = tf.add_paragraph()
    p2.text = f"{PRESENTER} Bhd Thesis"
    p2.font.size = Pt(12)
    p2.font.italic = True
    p2.font.color.rgb = BURGUNDY
    p2.font.name = "Calibri"
    p2.alignment = PP_ALIGN.RIGHT


def slide_title(prs: Presentation):
    """Slide 1: Title slide."""
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)

    # Top logos
    if os.path.exists(LOGO_ITC):
        slide.shapes.add_picture(LOGO_ITC, Inches(0.6), Inches(0.3), width=Inches(1.0))
    if os.path.exists(LOGO_AMS):
        slide.shapes.add_picture(LOGO_AMS, Inches(1.7), Inches(0.3), width=Inches(1.0))
    if os.path.exists(LOGO_DAC):
        slide.shapes.add_picture(LOGO_DAC, Inches(11.0), Inches(0.3), width=Inches(1.2))

    # Institution & department
    _add_text_box(slide, Inches(3.0), Inches(0.35), Inches(7.0), Inches(0.5),
                  INSTITUTION, font_size=28, bold=True, color=DARK_TEXT, align=PP_ALIGN.CENTER,
                  font_name="Times New Roman")
    _add_text_box(slide, Inches(3.0), Inches(0.85), Inches(7.0), Inches(0.4),
                  DEPARTMENT, font_size=20, color=DARK_TEXT, align=PP_ALIGN.CENTER,
                  font_name="Times New Roman")

    # Center maroon rounded rectangle with title
    box_width = Inches(11.5)
    box_height = Inches(2.2)
    box_left = (SLIDE_WIDTH - box_width) / 2
    box_top = Inches(2.3)

    title_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        box_left, box_top, box_width, box_height
    )
    _set_shape_fill(title_box, BURGUNDY)
    title_box.line.fill.background()

    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = THESIS_TITLE.upper()
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Times New Roman"
    p.alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].space_before = Pt(20)

    # Presenter info
    _add_text_box(slide, Inches(0), Inches(4.9), SLIDE_WIDTH, Inches(0.4),
                  "Presented by:", font_size=18, color=DARK_TEXT, align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.25), SLIDE_WIDTH, Inches(0.5),
                  PRESENTER, font_size=28, bold=True, color=DARK_TEXT, align=PP_ALIGN.CENTER,
                  font_name="Times New Roman")

    # Bottom info columns
    left_col_x = Inches(1.5)
    right_col_x = Inches(7.5)
    info_y = Inches(5.9)
    info_line_height = Inches(0.35)

    infos = [
        (left_col_x, f"Supervisor      : {SUPERVISOR}"),
        (left_col_x, f"Co-Supervisor   : {CO_SUPERVISOR}"),
        (right_col_x, f"Organization    : {ORGANIZATION}"),
        (right_col_x, f"Duration        : {DURATION}"),
    ]
    for i, (x, text) in enumerate(infos):
        y = info_y + (i % 2) * info_line_height
        _add_text_box(slide, x, y, Inches(5.0), Inches(0.35),
                      text, font_size=16, color=DARK_TEXT, align=PP_ALIGN.LEFT)

    _add_text_box(slide, Inches(0), Inches(6.7), SLIDE_WIDTH, Inches(0.4),
                  DEFENSE_DATE, font_size=18, color=DARK_TEXT, align=PP_ALIGN.CENTER)

    # Bottom bar (no breadcrumb on title, just color strip)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), BOTTOM_BAR_TOP,
        SLIDE_WIDTH, BOTTOM_BAR_HEIGHT
    )
    _set_shape_fill(bar, BURGUNDY)
    bar.line.fill.background()

    # Small logos inside bottom bar area
    if os.path.exists(LOGO_ITC):
        slide.shapes.add_picture(LOGO_ITC, Inches(10.5), Inches(6.35), width=Inches(0.7))
    if os.path.exists(LOGO_DAC):
        slide.shapes.add_picture(LOGO_DAC, Inches(11.3), Inches(6.35), width=Inches(0.7))


def slide_toc(prs: Presentation):
    """Slide 2: Table of Contents with left sidebar."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    # Left sidebar
    sidebar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        Inches(2.3), SLIDE_HEIGHT
    )
    _set_shape_fill(sidebar, BURGUNDY)
    sidebar.line.fill.background()

    # Hamburger icon (three white lines)
    for i in range(3):
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.5), Inches(0.4 + i * 0.18),
            Inches(0.6), Inches(0.06)
        )
        _set_shape_fill(line, WHITE)
        line.line.fill.background()

    # Graduation cap icon placeholder (white circle)
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(0.4), Inches(3.0),
        Inches(0.8), Inches(0.8)
    )
    _set_shape_fill(circle, WHITE)
    circle.line.fill.background()
    tf = circle.text_frame
    p = tf.paragraphs[0]
    p.text = "🎓"
    p.font.size = Pt(28)
    p.alignment = PP_ALIGN.CENTER

    # Dots at bottom
    for i in range(3):
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(0.5 + i * 0.35), Inches(6.8),
            Inches(0.12), Inches(0.12)
        )
        _set_shape_fill(dot, WHITE)
        dot.line.fill.background()

    # Heading
    _add_text_box(slide, Inches(2.8), Inches(0.4), Inches(9.0), Inches(0.8),
                  "TABLE OF CONTENT", font_size=40, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.LEFT, font_name="Times New Roman")

    # Numbered sections
    col1_x = Inches(3.0)
    col2_x = Inches(7.5)
    start_y = Inches(1.6)
    item_height = Inches(1.1)

    for idx, (num, name) in enumerate(SECTIONS):
        col_x = col1_x if idx < 4 else col2_x
        row_y = start_y + (idx % 4) * item_height

        # Number square
        sq = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            col_x, row_y,
            Inches(0.65), Inches(0.65)
        )
        _set_shape_fill(sq, BURGUNDY)
        sq.line.fill.background()
        tf = sq.text_frame
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Section name
        _add_text_box(slide, col_x + Inches(0.9), row_y, Inches(3.5), Inches(0.4),
                      name, font_size=22, bold=True, color=DARK_TEXT,
                      align=PP_ALIGN.LEFT, font_name="Times New Roman")

        # Underline
        underline = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            col_x + Inches(0.9), row_y + Inches(0.45),
            Inches(1.2), Inches(0.06)
        )
        _set_shape_fill(underline, BURGUNDY)
        underline.line.fill.background()

    _add_bottom_bar(slide)


def slide_section_divider(prs: Presentation, number: str, title: str, page_num: str):
    """Section divider with large maroon rounded rectangle."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    _add_top_right_header(slide)

    # Large centered rounded rectangle
    box_width = Inches(10.0)
    box_height = Inches(2.5)
    box_left = (SLIDE_WIDTH - box_width) / 2
    box_top = Inches(2.3)

    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        box_left, box_top, box_width, box_height
    )
    _set_shape_fill(box, BURGUNDY)
    box.line.fill.background()

    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"{number}. {title}"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Times New Roman"
    p.alignment = PP_ALIGN.CENTER

    _add_bottom_bar(slide, page_num)


def slide_content(prs: Presentation, slide_title_text: str, page_num: str):
    """Generic content slide with title area and content placeholder."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    _add_top_right_header(slide)

    # Slide title (top left, large, burgundy)
    _add_text_box(slide, MARGIN_LEFT, Inches(0.25), Inches(8.0), Inches(0.7),
                  slide_title_text, font_size=36, bold=True, color=BURGUNDY,
                  align=PP_ALIGN.LEFT, font_name="Times New Roman")

    # Content placeholder area (light dashed border)
    content_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        MARGIN_LEFT, CONTENT_TOP,
        SLIDE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT, Inches(5.4)
    )
    content_box.fill.background()
    content_box.line.color.rgb = MEDIUM_GRAY
    content_box.line.width = Pt(1.5)
    # Dashed line not directly supported in python-pptx easily, solid is okay

    # Placeholder text
    tf = content_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "[Insert content here]"
    p.font.size = Pt(18)
    p.font.color.rgb = MEDIUM_GRAY
    p.alignment = PP_ALIGN.CENTER

    _add_bottom_bar(slide, page_num)


def slide_two_column(prs: Presentation, slide_title_text: str, page_num: str):
    """Two-column content slide."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    _add_top_right_header(slide)

    _add_text_box(slide, MARGIN_LEFT, Inches(0.25), Inches(8.0), Inches(0.7),
                  slide_title_text, font_size=36, bold=True, color=BURGUNDY,
                  align=PP_ALIGN.LEFT, font_name="Times New Roman")

    # Left column
    left_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        MARGIN_LEFT, CONTENT_TOP,
        Inches(5.9), Inches(5.4)
    )
    left_box.fill.background()
    left_box.line.color.rgb = MEDIUM_GRAY
    left_box.line.width = Pt(1)
    tf = left_box.text_frame
    p = tf.paragraphs[0]
    p.text = "[Left column content]"
    p.font.size = Pt(16)
    p.font.color.rgb = MEDIUM_GRAY
    p.alignment = PP_ALIGN.CENTER

    # Right column
    right_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(6.9), CONTENT_TOP,
        Inches(5.9), Inches(5.4)
    )
    right_box.fill.background()
    right_box.line.color.rgb = MEDIUM_GRAY
    right_box.line.width = Pt(1)
    tf = right_box.text_frame
    p = tf.paragraphs[0]
    p.text = "[Right column content]"
    p.font.size = Pt(16)
    p.font.color.rgb = MEDIUM_GRAY
    p.alignment = PP_ALIGN.CENTER

    _add_bottom_bar(slide, page_num)


def slide_thank_you(prs: Presentation):
    """Final thank-you slide."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    box_width = Inches(10.0)
    box_height = Inches(2.0)
    box_left = (SLIDE_WIDTH - box_width) / 2
    box_top = Inches(2.5)

    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        box_left, box_top, box_width, box_height
    )
    _set_shape_fill(box, BURGUNDY)
    box.line.fill.background()

    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = "THANK YOU"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Times New Roman"
    p.alignment = PP_ALIGN.CENTER

    _add_text_box(slide, Inches(0), Inches(4.8), SLIDE_WIDTH, Inches(0.5),
                  "Q&A", font_size=28, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER, font_name="Times New Roman")

    _add_bottom_bar(slide)


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # 1. Title
    slide_title(prs)

    # 2. Table of Contents
    slide_toc(prs)

    # 3–8. Section dividers
    page_counter = 1
    for num, title in SECTIONS:
        slide_section_divider(prs, num, title, str(page_counter))
        page_counter += 1

    # 9–14. Example content slides (one per section)
    content_slides = [
        ("General Presentation", "1"),
        ("About Project", "2"),
        ("Problem Statement", "3"),
        ("Goal and Objective", "4"),
        ("Project Timeline", "5"),
        ("Conclusion", "6"),
    ]
    for title, pg in content_slides:
        slide_content(prs, title, pg)

    # 15. Two-column example
    slide_two_column(prs, "System Architecture", "7")

    # 16. Thank you
    slide_thank_you(prs)

    prs.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
