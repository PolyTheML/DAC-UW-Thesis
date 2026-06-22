import copy
from pptx.util import Emu, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.dml.color import RGBColor

# Import defense_tokens — handle both module and builder contexts
try:
    from defense_tokens import *
except ImportError:
    from thesis.health_rl.defense_tokens import *


def rect(slide, l, t, w, h, fill=None, line_color=None):
    shp = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Emu(l), Emu(t), Emu(w), Emu(h))
    if fill:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    if line_color:
        shp.line.color.rgb = line_color
    else:
        shp.line.fill.background()
    return shp


def textbox(slide, l, t, w, h, word_wrap=True):
    tb = slide.shapes.add_textbox(Emu(l), Emu(t), Emu(w), Emu(h))
    tb.text_frame.word_wrap = word_wrap
    return tb.text_frame


def add_run(para, text, size, bold=False, italic=False, color=DARK_TXT):
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return run


def para(tf, text, size, bold=False, italic=False, color=DARK_TXT,
         align=PP_ALIGN.LEFT, space_before=0, space_after=0):
    """Add paragraph to a text frame. Reuses first empty para; otherwise appends."""
    if tf.paragraphs and tf.paragraphs[0].text == "":
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    add_run(p, text, size, bold=bold, italic=italic, color=color)
    return p


def new_para(tf, text, size, bold=False, italic=False, color=DARK_TXT,
             align=PP_ALIGN.LEFT, space_before=0):
    """Always append a new paragraph."""
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    add_run(p, text, size, bold=bold, italic=italic, color=color)
    return p


def title_block(slide, text):
    """Standard centred title + navy underline."""
    tf = textbox(slide, MARGIN_L, TITLE_T, CONTENT_W, TITLE_H)
    para(tf, text, 26, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    underline_w = 2391695
    underline_l = (SW - underline_w) // 2
    rect(slide, underline_l, UNDERLINE_T, underline_w, UNDERLINE_H, fill=NAVY)


def footer(slide, section_name, slide_num, total=29):
    """3-panel footer matching deck design."""
    h = 420624
    # Left panel (navy bg)
    rect(slide, 0, FOOTER_TOP, 3108960, h, fill=NAVY)
    tf = textbox(slide, 164592, FOOTER_TOP, 2834640, h)
    para(tf, "DAC  ·  ITC-AMS", 9, bold=True, color=WHITE,
         align=PP_ALIGN.LEFT)
    # Centre panel (light blue bg)
    rect(slide, 3108960, FOOTER_TOP, 6126480, h, fill=RGBColor(0xBD, 0xCE, 0xE4))
    tf2 = textbox(slide, 3200400, FOOTER_TOP, 5943600, h)
    para(tf2, section_name, 9, color=NAVY, align=PP_ALIGN.CENTER)
    # Right panel (navy bg)
    rect(slide, 9235440, FOOTER_TOP, 2956255, h, fill=NAVY)
    tf3 = textbox(slide, 9326880, FOOTER_TOP, 2743200, h)
    para(tf3, f"July 2026  ·  {slide_num} / {total}", 9,
         color=WHITE, align=PP_ALIGN.RIGHT)


def section_divider(slide, section_name, slide_num, numeral, total=29):
    """Full-blue section divider matching Yuth deck style."""
    rect(slide, 0, 0, SW, SH, fill=NAVY)
    tf = textbox(slide, MARGIN_L, SH // 2 - 300000, CONTENT_W, 600000)
    para(tf, numeral, 48, bold=True, color=WHITE)
    rect(slide, MARGIN_L, SH // 2 + 150000, 2926080, 54864,
         fill=RGBColor(0xFF, 0xFF, 0xFF))
    tf2 = textbox(slide, MARGIN_L, SH // 2 + 280000, CONTENT_W, 800000)
    para(tf2, section_name, 28, bold=True, color=WHITE)
    # Footer (white text on navy — reuse footer with override)
    h = 420624
    rect(slide, 0, FOOTER_TOP, SW, h, fill=RGBColor(0x16, 0x2D, 0x58))
    tf3 = textbox(slide, 164592, FOOTER_TOP, 2834640, h)
    para(tf3, "DAC  ·  ITC-AMS", 9, bold=True, color=WHITE)
    tf4 = textbox(slide, 3200400, FOOTER_TOP, 5943600, h)
    para(tf4, section_name, 9, color=RGBColor(0xBD, 0xCE, 0xE4),
         align=PP_ALIGN.CENTER)
    tf5 = textbox(slide, 9326880, FOOTER_TOP, 2743200, h)
    para(tf5, f"July 2026  ·  {slide_num} / {total}", 9,
         color=WHITE, align=PP_ALIGN.RIGHT)


def card(slide, l, t, w, h, header=None, body_lines=None,
         bg=LIGHT_BG, accent=NAVY, header_size=14, body_size=11):
    """Card box: light bg + left navy border + optional header + body lines."""
    rect(slide, l, t, w, h, fill=bg)
    rect(slide, l, t, 91440, h, fill=accent)
    pad_l = l + 150000
    pad_t = t + 120000
    pad_w = w - 180000
    if header:
        tf = textbox(slide, pad_l, pad_t, pad_w, 380000)
        para(tf, header, header_size, bold=True, color=NAVY)
        pad_t += 420000
    if body_lines:
        tf2 = textbox(slide, pad_l, pad_t, pad_w, h - (pad_t - t) - 100000)
        first = True
        for line in body_lines:
            if first:
                para(tf2, line, body_size, color=GRAY)
                first = False
            else:
                new_para(tf2, line, body_size, color=GRAY, space_before=4)
