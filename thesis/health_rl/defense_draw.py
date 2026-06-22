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


def add_run(para, text, size, bold=False, italic=False, color=DARK_TXT,
            font_name=BODY_FONT):
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_name
    return run


def para(tf, text, size, bold=False, italic=False, color=DARK_TXT,
         align=PP_ALIGN.LEFT, space_before=0, space_after=0, font_name=BODY_FONT):
    """Add paragraph to a text frame. Reuses first empty para; otherwise appends."""
    if tf.paragraphs and tf.paragraphs[0].text == "":
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    add_run(p, text, size, bold=bold, italic=italic, color=color, font_name=font_name)
    return p


def new_para(tf, text, size, bold=False, italic=False, color=DARK_TXT,
             align=PP_ALIGN.LEFT, space_before=0, font_name=BODY_FONT):
    """Always append a new paragraph."""
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    add_run(p, text, size, bold=bold, italic=italic, color=color, font_name=font_name)
    return p


def title_block(slide, text):
    """Standard centred ALL-CAPS cobalt title + cobalt underline (burgundy chrome)."""
    tf = textbox(slide, MARGIN_L, TITLE_T, CONTENT_W, TITLE_H)
    para(tf, text, 26, bold=True, color=NAVY, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
    underline_w = 2391695
    underline_l = (SW - underline_w) // 2
    rect(slide, underline_l, UNDERLINE_T, underline_w, UNDERLINE_H, fill=NAVY)


def footer(slide, section_name, slide_num, total=39):
    """3-panel footer ribbon (burgundy chrome): deep-cobalt org panels, tint centre."""
    h = 420624
    # Left panel (deep cobalt bg)
    rect(slide, 0, FOOTER_TOP, 3108960, h, fill=BLUE_DEEP)
    tf = textbox(slide, 164592, FOOTER_TOP, 2834640, h)
    para(tf, "DAC  ·  ITC-AMS", 9, bold=True, color=WHITE,
         align=PP_ALIGN.LEFT)
    # Centre panel (cobalt tint bg)
    rect(slide, 3108960, FOOTER_TOP, 6126480, h, fill=BLUE_TINT)
    tf2 = textbox(slide, 3200400, FOOTER_TOP, 5943600, h)
    para(tf2, section_name, 9, color=NAVY, align=PP_ALIGN.CENTER)
    # Right panel (deep cobalt bg)
    rect(slide, 9235440, FOOTER_TOP, 2956255, h, fill=BLUE_DEEP)
    tf3 = textbox(slide, 9326880, FOOTER_TOP, 2743200, h)
    para(tf3, f"July 2026  ·  {slide_num} / {total}", 9,
         color=WHITE, align=PP_ALIGN.RIGHT)


def outline(slide, l, t, w, h, color, width_pt=3):
    """Borderless rectangle outline (no fill) — used for 'you are here' frames."""
    shp = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Emu(l), Emu(t), Emu(w), Emu(h))
    shp.fill.background()
    shp.line.color.rgb = color
    shp.line.width = Pt(width_pt)
    return shp


def section_divider(slide, section_name, slide_num, numeral, total=39):
    """Full cobalt section divider (burgundy chrome): big white numeral-with-dot,
    white underline, white section name. Numeral sits clearly ABOVE the underline."""
    rect(slide, 0, 0, SW, SH, fill=BLUE_DIVIDER)
    tf = textbox(slide, MARGIN_L, SH // 2 - 680000, CONTENT_W, 700000)
    para(tf, numeral, 48, bold=True, color=WHITE, font_name=HEAD_FONT)
    rect(slide, MARGIN_L, SH // 2 + 60000, 2926080, 54864,
         fill=RGBColor(0xFF, 0xFF, 0xFF))
    tf2 = textbox(slide, MARGIN_L, SH // 2 + 160000, CONTENT_W, 800000)
    para(tf2, section_name, 28, bold=True, color=WHITE, font_name=HEAD_FONT)
    # Footer (white text on deep cobalt)
    h = 420624
    rect(slide, 0, FOOTER_TOP, SW, h, fill=BLUE_DEEP)
    tf3 = textbox(slide, 164592, FOOTER_TOP, 2834640, h)
    para(tf3, "DAC  ·  ITC-AMS", 9, bold=True, color=WHITE)
    tf4 = textbox(slide, 3200400, FOOTER_TOP, 5943600, h)
    para(tf4, section_name, 9, color=BLUE_TINT,
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
        para(tf, header, header_size, bold=True, color=NAVY, font_name=HEAD_FONT)
        pad_t += 420000
    if body_lines:
        tf2 = textbox(slide, pad_l, pad_t, pad_w, h - (pad_t - t) - 100000)
        first = True
        for line in body_lines:
            if first:
                para(tf2, line, body_size, color=GRAY, font_name=BODY_FONT)
                first = False
            else:
                new_para(tf2, line, body_size, color=GRAY, space_before=4, font_name=BODY_FONT)
