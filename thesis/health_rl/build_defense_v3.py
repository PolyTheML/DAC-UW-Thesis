# thesis/health_rl/build_defense_v3.py
"""Build Poly_defense_presentation_v3.pptx from scratch.

34-slide "Nang Sreynich flow" redesign (spec 2026-07-02):
  - 7-section persistent top-nav tabs + ToC + physical page numbers
  - Cambodia map on the < 2% slide; plain-language-first everywhere
  - formulas exiled to appendix (A1-A8); Sophea threaded throughout
  - demonstration section LAST, then Thanks, then Appendices
Run order: build_defense_v3.py FIRST, then the script generators
(the builder creates a fresh Presentation() and wipes injected notes).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from defense_tokens import *
from defense_draw import (rect, textbox, para, new_para, add_run,
                          title_block, footer, card, nav_tabs)

OUT = r"thesis\health_rl\Poly_defense_presentation_v3.pptx"
TOTAL = 34

prs = Presentation()
prs.slide_width  = Emu(SW)
prs.slide_height = Emu(SH)
BLANK = prs.slide_layouts[6]   # truly blank layout

# Full section names (footer + ToC); nav-tab short forms live in NAV_SECTIONS.
SEC_FOOTER = [
    "Introduction & Problem Background",   # i   (nav idx 0)
    "Literature Review",                   # ii  (nav idx 1)
    "System Design",                       # iii (nav idx 2)
    "Implementation",                      # iv  (nav idx 3)
    "Results & Discussion",                # v   (nav idx 4)
    "Conclusion & Future Work",            # vi  (nav idx 5)
    "Demonstration",                       # vii (nav idx 6)
]


def new_slide():
    return prs.slides.add_slide(BLANK)


def content_slide(title, active_idx):
    """White content slide with the persistent nav-tab bar + standard title."""
    s = new_slide()
    rect(s, 0, 0, SW, SH, fill=WHITE)
    nav_tabs(s, active_idx)
    title_block(s, title)
    return s


def content_footer(s, active_idx, phys):
    footer(s, SEC_FOOTER[active_idx], str(phys), TOTAL)


def add_speaker_note(slide, text):
    """Append to a slide's speaker notes (kept for compatibility; the canonical
    notes are injected later by generate_defense_script_v2.py)."""
    notes_tf = slide.notes_slide.notes_text_frame
    existing = notes_tf.text
    notes_tf.text = (existing.rstrip() + "\n\n" + text) if existing.strip() else text


_HERE     = os.path.dirname(__file__)
LOGO_ITC  = os.path.join(_HERE, "..", "ITC.jpg")
LOGO_AMS  = os.path.join(_HERE, "..", "AMS.png")
LOGO_DAC  = os.path.join(_HERE, "..", "DAC.jpg")
FIG_DIR   = os.path.join(_HERE, "figures")
THESIS_TITLE = ("ADAPTIVE HEALTH INSURANCE UNDERWRITING VIA CONTEXTUAL BANDITS: "
                "A REINFORCEMENT LEARNING APPROACH FOR CAMBODIA")

# ══ Slide 1: Title ════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
for _path, _lx, _ly, _lw in [
    (LOGO_ITC, 0.6,  0.30, 1.0),
    (LOGO_AMS, 1.75, 0.40, 1.45),
    (LOGO_DAC, 11.3, 0.35, 1.45),
]:
    if os.path.exists(_path):
        s.shapes.add_picture(_path, Inches(_lx), Inches(_ly), width=Inches(_lw))

tf = textbox(s, Inches(3.4), Inches(0.42), Inches(7.2), Inches(0.5))
para(tf, "Institute of Technology of Cambodia", 22, bold=True,
     color=DARK_TXT, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
tf = textbox(s, Inches(3.4), Inches(0.92), Inches(7.2), Inches(0.4))
para(tf, "Department of Applied Mathematics and Statistics", 15,
     color=GRAY, align=PP_ALIGN.CENTER)
tf = textbox(s, Inches(1.0), Inches(1.48), Inches(11.3), Inches(0.32))
para(tf, "Introduction  ·  Literature  ·  System Design  ·  Implementation  "
     "·  Results  ·  Conclusion  ·  Demonstration",
     11, color=GRAY, align=PP_ALIGN.CENTER)

rect(s, Inches(5.92), Inches(2.05), Inches(1.5), Inches(0.045), fill=NAVY)
tf = textbox(s, Inches(0.9), Inches(2.35), Inches(11.5), Inches(1.7))
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
para(tf, THESIS_TITLE, 27, bold=True, color=DARK_TXT,
     align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
rect(s, Inches(5.92), Inches(4.25), Inches(1.5), Inches(0.045), fill=NAVY)

tf = textbox(s, 0, Inches(4.62), SW, Inches(0.34))
para(tf, "Thesis Defense — Presented by", 16, color=GRAY, align=PP_ALIGN.CENTER)
tf = textbox(s, 0, Inches(4.96), SW, Inches(0.5))
para(tf, "LUN CHANPOLY", 27, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
     font_name=HEAD_FONT)

_lx, _rx = Inches(1.5), Inches(7.5)
for _i, (_lt, _rt) in enumerate([
    ("Supervisor   :  Dr. HAS Sothea",       "Organization  :  DAC (Decent Actuarial Consultants)"),
    ("Duration       :  Mar 2026 – Jun 2026", "DAC Advisor  :  Mr. ON Radet"),
]):
    _y = Inches(5.68) + _i * Inches(0.36)
    tf = textbox(s, _lx, _y, Inches(5.6), Inches(0.34))
    para(tf, _lt, 16, color=DARK_TXT)
    tf = textbox(s, _rx, _y, Inches(5.6), Inches(0.34))
    para(tf, _rt, 16, color=DARK_TXT)

tf = textbox(s, 0, Inches(6.6), SW, Inches(0.38))
para(tf, "8 July 2026", 15, bold=True, color=GRAY, align=PP_ALIGN.CENTER)
footer(s, "Title", "–", TOTAL)

# ══ Slide 2: Table of Contents ════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "TABLE OF CONTENTS")
TOC = [
    ("i",   SEC_FOOTER[0]),
    ("ii",  SEC_FOOTER[1]),
    ("iii", SEC_FOOTER[2]),
    ("iv",  SEC_FOOTER[3]),
    ("v",   SEC_FOOTER[4]),
    ("vi",  SEC_FOOTER[5]),
    ("vii", SEC_FOOTER[6]),
]
TOC_START = 1180000; TOC_PITCH = 700000; TOC_ROW_H = 560000
for i, (num, name) in enumerate(TOC):
    t = TOC_START + i * TOC_PITCH
    rect(s, MARGIN_L, t, 560000, TOC_ROW_H, fill=NAVY)
    tf = textbox(s, MARGIN_L + 20000, t, 520000, TOC_ROW_H, word_wrap=False)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, num, 17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 700000, t, CONTENT_W - 800000, TOC_ROW_H)
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf2, name, 16, color=NAVY)
footer(s, "Contents", "–", TOTAL)

# ══ Slide 3: Cambodia map + < 2% ══════════════════════════════════════
s = content_slide("A MARKET THE SYSTEM WAS NOT BUILT FOR", 0)

# Map (centred, transparent-bg NAVY silhouette)
MAP = os.path.join(FIG_DIR, "cambodia_map_navy.png")
map_w = 3900000
map_l = (SW - map_w) // 2
map_t = 1420000
if os.path.exists(MAP):
    s.shapes.add_picture(MAP, Emu(map_l), Emu(map_t), width=Emu(map_w))

# Left-top big-stat chip
rect(s, MARGIN_L, 1420000, 3000000, 1360000, fill=NAVY)
tf = textbox(s, MARGIN_L + 120000, 1500000, 2760000, 760000)
para(tf, "< 2%", 44, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
tf2 = textbox(s, MARGIN_L + 120000, 2320000, 2760000, 380000)
para(tf2, "have any health insurance (2023 est.)", 12,
     color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)

# Left-bottom chip: NSSF
rect(s, MARGIN_L, 3000000, 3000000, 1080000, fill=LIGHT_BG)
rect(s, MARGIN_L, 3000000, 73152, 1080000, fill=NAVY)
tf = textbox(s, MARGIN_L + 170000, 3110000, 2760000, 860000)
para(tf, "The state scheme (NSSF) covers formal-sector workers only", 14,
     bold=True, color=NAVY)
new_para(tf, "— roughly 16% of the population.", 13, color=GRAY, space_before=4)

# Right chip: manual underwriting
rc_l = SW - MARGIN_L - 3000000
rect(s, rc_l, 2200000, 3000000, 1080000, fill=LIGHT_BG)
rect(s, rc_l, 2200000, 73152, 1080000, fill=NAVY)
tf = textbox(s, rc_l + 170000, 2310000, 2760000, 860000)
para(tf, "Everyone else is underwritten by hand", 14, bold=True, color=NAVY)
new_para(tf, "— fixed rules, no learning, no fairness check.", 13,
         color=GRAY, space_before=4)

# Kicker + source
tf = textbox(s, MARGIN_L, 4700000, CONTENT_W, 520000)
para(tf, "Sophea represents the 98% the current system was not built for.",
     16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
tf = textbox(s, MARGIN_L, 5980000, CONTENT_W, 300000)
para(tf, "Sources: ILO (2023) · Cambodia Demographic & Health Survey (2021-22).",
     10, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
content_footer(s, 0, 3)

# ══ Slide 4: Meet Sophea ══════════════════════════════════════════════
s = content_slide("MEET SOPHEA", 0)
CARD_L = MARGIN_L; CARD_T = 1120000
CARD_W = 5200000; CARD_H = CONTENT_BOT - CARD_T
rect(s, CARD_L, CARD_T, CARD_W, CARD_H, fill=LIGHT_BG)
rect(s, CARD_L, CARD_T, 91440, CARD_H, fill=NAVY)
PAD_L = CARD_L + 160000
tf = textbox(s, PAD_L, CARD_T + 140000, CARD_W - 200000, 480000)
para(tf, "SOPHEA", 26, bold=True, color=NAVY)
tf2 = textbox(s, PAD_L, CARD_T + 640000, CARD_W - 200000, 340000)
para(tf2, "Age 42  ·  Kampong Cham Province  ·  Rice Farmer", 14,
     color=RGBColor(0x40, 0x40, 0x40))
rect(s, PAD_L, CARD_T + 1080000, CARD_W - 250000, 27432, fill=DIVIDER)
ATTRS = [("BMI", "24.1  (Normal range)"), ("Smoker", "No"),
         ("Physical Activity", "High  (field farming)"),
         ("Clinical Flag", "Hypertension  (managed)"),
         ("Wealth Index", "Low"), ("Education", "Primary")]
tf3 = textbox(s, PAD_L, CARD_T + 1180000, CARD_W - 200000, CARD_H - 1300000)
first = True
for label, value in ATTRS:
    p = tf3.paragraphs[0] if first else tf3.add_paragraph()
    first = False
    p.space_before = Pt(10)
    r1 = p.add_run(); r1.text = f"{label}:  "; r1.font.size = Pt(14)
    r1.font.bold = True; r1.font.color.rgb = NAVY
    r2 = p.add_run(); r2.text = value; r2.font.size = Pt(14)
    r2.font.color.rgb = GRAY

R_L = CARD_L + CARD_W + 280000; R_T = CARD_T; R_W = SW - R_L - 200000
tf4 = textbox(s, R_L, R_T + 80000, R_W, 1350000)
para(tf4, "In 2023 she applies for voluntary health insurance in Phnom Penh.\n\n"
     "The static system checks just two fields.", 15, italic=True, color=GRAY)
FLAG_H = 550000
for i, (label, text) in enumerate([
        ("OCCUPATION:", "Agriculture"),
        ("CONDITION:", "Hypertension")]):
    ft = R_T + 1550000 + i * (FLAG_H + 120000)
    rect(s, R_L, ft, R_W, FLAG_H, fill=AMBER_BG)
    rect(s, R_L, ft, 73152, FLAG_H, fill=AMBER_ACC)
    tff = textbox(s, R_L + 130000, ft + 130000, R_W - 160000, FLAG_H - 160000)
    para(tff, f"{label}  {text}", 15, bold=True, color=AMBER_TXT)
ct = R_T + 2850000
tf5 = textbox(s, R_L, ct, R_W, 340000)
para(tf5, "Both thresholds crossed. In 2023 the system decides:", 14, italic=True, color=GRAY)
rect(s, R_L, ct + 400000, R_W, 820000, fill=RED_BG)
rect(s, R_L, ct + 400000, 109728, 820000, fill=RED_ACC)
tf6 = textbox(s, R_L + 170000, ct + 560000, R_W - 200000, 500000)
para(tf6, "DECLINE", 36, bold=True, color=RED_ACC)
tf7 = textbox(s, R_L, ct + 1380000, R_W, 500000)
para(tf7, "Sophea leaves without coverage.", 14, italic=True, color=GRAY)
new_para(tf7, "Was that the right answer?", 15, bold=True, color=NAVY, space_before=8)
content_footer(s, 0, 4)

# ══ Slide 5: Why static rules fail ════════════════════════════════════
s = content_slide("WHY STATIC RULES FAIL", 0)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 640000)
para(tf, "A fixed rule can't see Sophea's full picture —", 18, bold=True,
     color=NAVY, align=PP_ALIGN.CENTER)
new_para(tf, "and it never learns from its mistakes.", 18, italic=True,
         color=GRAY, align=PP_ALIGN.CENTER, space_before=4)
FAIL = [
    ("Fixed cutoffs",
     "It checks two fields and stops. Her normal BMI, active lifestyle and "
     "managed blood pressure are invisible to the rule."),
    ("Never updates",
     "Claims come back over the years, but the rule stays frozen. It repeats "
     "the same mistake on the next Sophea, and the next."),
    ("Nobody checks fairness",
     "No one tracks whether whole regions or occupations are being quietly "
     "shut out. Bias can build up unseen."),
]
fw = (CONTENT_W - 2 * 300000) // 3
ft_top = 2050000; fh = 3550000
for i, (hdr, body) in enumerate(FAIL):
    l = MARGIN_L + i * (fw + 300000)
    rect(s, l, ft_top, fw, fh, fill=LIGHT_BG)
    rect(s, l, ft_top, fw, 82000, fill=NAVY)
    tfh = textbox(s, l + 150000, ft_top + 230000, fw - 250000, 500000)
    para(tfh, hdr, 17, bold=True, color=NAVY, font_name=HEAD_FONT)
    tfb = textbox(s, l + 150000, ft_top + 850000, fw - 250000, fh - 1000000)
    para(tfb, body, 14, color=DARK_TXT)
content_footer(s, 0, 5)

# ══ Slide 6: Goal & Objectives (+ SDG strip) ══════════════════════════
s = content_slide("GOAL & OBJECTIVES", 0)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 620000)
para(tf, "Can a system that learns from every decision underwrite better — and "
     "stay fair — than today's fixed rules?", 17, bold=True, color=NAVY)
RQS = [
    ("RQ1", "Does a learning system earn more, and make fewer mistakes, than the fixed-rule baseline?"),
    ("RQ2", "Does it stay fair across regions and occupations — without being told to?"),
    ("RQ3", "Which learning method works best (LinTS, LinUCB, ε-Greedy)?"),
]
rq_top = 1900000; rq_h = 520000; rq_gap = 90000
for i, (num, text) in enumerate(RQS):
    t = rq_top + i * (rq_h + rq_gap)
    rect(s, MARGIN_L, t, 620000, rq_h, fill=NAVY)
    tf = textbox(s, MARGIN_L + 20000, t, 580000, rq_h, word_wrap=False)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, num, 15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 760000, t, CONTENT_W - 820000, rq_h)
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf2, text, 14, color=DARK_TXT)
rq_bot = rq_top + 3 * (rq_h + rq_gap) - rq_gap

# SDG strip (relocated from the old Cambodia-context slide)
tf = textbox(s, MARGIN_L, rq_bot + 160000, CONTENT_W, 300000)
para(tf, "WHY IT MATTERS — CAMBODIA'S SDGs", 13, bold=True, color=BLUE)
SDG = [
    ("SDG 3", "Good Health", "Widen coverage beyond the formal sector"),
    ("SDG 1", "No Poverty", "Shield families from catastrophic health costs"),
    ("SDG 10", "Less Inequality", "Keep underwriting demographically fair"),
]
sdg_w = (CONTENT_W - 2 * 220000) // 3
sdg_band = 1120000
sdg_t = rq_bot + 520000; sdg_h = 900000
for i, (num, name, desc) in enumerate(SDG):
    l = MARGIN_L + i * (sdg_w + 220000)
    rect(s, l, sdg_t, sdg_w, sdg_h, fill=LIGHT_BG)
    rect(s, l, sdg_t, sdg_band, sdg_h, fill=NAVY)
    tfn = textbox(s, l, sdg_t + 150000, sdg_band, 380000, word_wrap=False)
    tfn.margin_left = 0; tfn.margin_right = 0
    para(tfn, num, 16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tfnm = textbox(s, l, sdg_t + 520000, sdg_band, 320000)
    tfnm.margin_left = 0; tfnm.margin_right = 0
    para(tfnm, name, 10, color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
    tfd = textbox(s, l + sdg_band + 120000, sdg_t + 180000, sdg_w - sdg_band - 220000, sdg_h - 300000)
    tfd.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfd, desc, 13, color=DARK_TXT)
content_footer(s, 0, 6)

# ══ Slide 7: About DAC ════════════════════════════════════════════════
s = content_slide("ABOUT DECENT ACTUARIAL CONSULTANTS", 0)
SERVICES = [
    "Appointed Actuary Services — Life & General Insurance, Southeast Asia",
    "IFRS 17 Implementation",
    "Product Development — Life & General Insurance",
    "Asset–Liability Management & Enterprise Risk Management (ALM/ERM)",
    "Mergers & Acquisitions Advisory",
    "Education & Cooperation — University partnerships, government-academia-industry",
]
OVERVIEW_TEXT = (
    "Taipei-headquartered actuarial consultancy — Taiwan, Vietnam, Cambodia "
    "& wider SE Asia.\n\n"
    "Thesis completed during a 3-month internship (Mar–Jun 2026), "
    "DAC Phnom Penh office."
)
PANEL_L = MARGIN_L; PANEL_T = 1200000; PANEL_W = 3900000
PANEL_H = CONTENT_BOT - PANEL_T
rect(s, PANEL_L, PANEL_T, PANEL_W, PANEL_H, fill=LIGHT_BG)
rect(s, PANEL_L, PANEL_T, 91440, PANEL_H, fill=NAVY)
LOGO_W = 3200000; LOGO_H = 1800000
LOGO_T = PANEL_T + 280000
LOGO_L = PANEL_L + (PANEL_W - LOGO_W) // 2
if os.path.exists(LOGO_DAC):
    s.shapes.add_picture(LOGO_DAC, LOGO_L, LOGO_T, width=LOGO_W)
OVERVIEW_T = LOGO_T + LOGO_H + 250000
OVERVIEW_L = PANEL_L + 180000; OVERVIEW_W = PANEL_W - 360000
OVERVIEW_H = (PANEL_T + PANEL_H) - 100000 - OVERVIEW_T
tf = textbox(s, OVERVIEW_L, OVERVIEW_T, OVERVIEW_W, OVERVIEW_H)
para(tf, OVERVIEW_TEXT, 14, color=DARK_TXT)
ROW_L = PANEL_L + PANEL_W + 280000
ROW_W = (MARGIN_L + CONTENT_W) - ROW_L
ROW_H = 784000; ROW_GAP = 90000
for i, svc in enumerate(SERVICES):
    row_t = PANEL_T + i * (ROW_H + ROW_GAP)
    card(s, ROW_L, row_t, ROW_W, ROW_H, body_lines=[svc], body_size=15)
content_footer(s, 0, 7)

# ══ Slide 8: Project Timeline ═════════════════════════════════════════
s = content_slide("PROJECT TIMELINE", 0)
TL = os.path.join(FIG_DIR, "fig_project_timeline_3month.png")
if os.path.exists(TL):
    tl_h = 4650000; tl_w = int(tl_h * 4168 / 2366)   # native aspect
    tl_l = (SW - tl_w) // 2
    s.shapes.add_picture(TL, Emu(tl_l), Emu(1180000), height=Emu(tl_h))
tf = textbox(s, MARGIN_L, 5980000, CONTENT_W, 340000)
para(tf, "A three-month internship: research & modelling → experiments → "
     "engineering → writing & defense.", 13, italic=True, color=GRAY,
     align=PP_ALIGN.CENTER)
content_footer(s, 0, 8)

# ══ Slide 9: Literature in one table ══════════════════════════════════
s = content_slide("THE LITERATURE, IN ONE TABLE", 1)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 360000)
para(tf, "Four bodies of work meet in this thesis:", 15, italic=True, color=GRAY)
LIT_HDRS = ["Topic", "Key sources", "What it tells us (plain words)"]
LIT_ROWS = [
    ["Health insurance in\nemerging markets",
     "CDHS 2021-22 · ILO 2023 · ADB",
     "Cambodia is barely insured (<2%); the state scheme reaches only formal workers."],
    ["Contextual bandits",
     "Li et al. 2010 (LinUCB)\nAgrawal & Goyal 2013 (LinTS)",
     "Learn which action pays off, one decision at a time — no big offline dataset needed."],
    ["Fairness & drift\nmonitoring",
     "Siddiqi 2006 (PSI)\nBarocas et al.",
     "PSI flags when who-we-approve drifts away from who-we-trained-on."],
    ["Human-in-the-loop\nunderwriting",
     "HITL review literature",
     "Send only the genuinely uncertain cases to a human expert."],
]
tbl_l = MARGIN_L; tbl_t = 1560000
tbl = s.shapes.add_table(len(LIT_ROWS) + 1, 3,
                         Emu(tbl_l), Emu(tbl_t),
                         Emu(CONTENT_W), Emu(3450000)).table
tbl.columns[0].width = Emu(2900000)
tbl.columns[1].width = Emu(3200000)
tbl.columns[2].width = Emu(CONTENT_W - 6100000)
for ci, h in enumerate(LIT_HDRS):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(13)
for ri, row in enumerate(LIT_ROWS):
    bg = LIGHT_BG if ri % 2 == 0 else WHITE
    for ci, val in enumerate(row):
        c = tbl.cell(ri + 1, ci); c.text = val
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(12)
                r.font.bold = (ci == 0)
                r.font.color.rgb = NAVY if ci == 0 else DARK_TXT
tf = textbox(s, MARGIN_L, 5300000, CONTENT_W, 520000)
rect(s, MARGIN_L, 5250000, CONTENT_W, 700000, fill=GREEN_BG)
rect(s, MARGIN_L, 5250000, 91440, 700000, fill=GREEN_ACC)
tf = textbox(s, MARGIN_L + 180000, 5360000, CONTENT_W - 360000, 480000)
para(tf, "The gap: no prior work applies online-learning underwriting to Cambodia.",
     15, bold=True, color=GREEN_ACC)
content_footer(s, 1, 9)

# ══ Slide 10: System architecture ═════════════════════════════════════
s = content_slide("HOW THE SYSTEM WORKS", 2)
PIPELINE = [
    ("Applicant\nContext", NAVY, WHITE),
    ("Bandit\nPolicy", BLUE, WHITE),
    ("Underwriting\nAction", BLUE, WHITE),
    ("Actuarial\nReward", ORANGE, WHITE),
    ("PSI + HITL\nGuardrail", BLUE, WHITE),
    ("Decision", RGBColor(0xC0, 0x70, 0x00), WHITE),
]
box_w = 1500000; box_h = 700000; gap = 200000
total_w = len(PIPELINE) * box_w + (len(PIPELINE) - 1) * gap
start_l = (SW - total_w) // 2
for i, (label, bg, fg) in enumerate(PIPELINE):
    l = start_l + i * (box_w + gap)
    rect(s, l, 1450000, box_w, box_h, fill=bg)
    tf = textbox(s, l + 50000, 1550000, box_w - 100000, box_h - 100000)
    para(tf, label, 14, bold=True, color=fg, align=PP_ALIGN.CENTER)
    if i < len(PIPELINE) - 1:
        tf2 = textbox(s, l + box_w, 1650000, gap, 500000)
        para(tf2, "→", 18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
tf = textbox(s, MARGIN_L, 2450000, CONTENT_W, 520000)
para(tf, "In plain words: the system decides, sees what happens, and gets a "
     "little smarter each round.", 16, bold=True, color=NAVY,
     align=PP_ALIGN.CENTER)
BULLETS = [
    "It reads a short profile of the applicant.",
    "It picks one of four actions: Standard · Rated · Decline · Refer to a human.",
    "It earns a reward: premiums collected minus the claims that follow.",
    "A fairness guardrail (PSI) watches for demographic drift.",
    "Uncertain cases are handed to a human expert.",
]
for i, b in enumerate(BULLETS):
    rect(s, MARGIN_L + 400000, 3150000 + i * 620000, 40000, 400000, fill=BLUE)
    tf3 = textbox(s, MARGIN_L + 520000, 3190000 + i * 620000, CONTENT_W - 700000, 460000)
    para(tf3, b, 15, color=DARK_TXT)
content_footer(s, 2, 10)

# ══ Slide 11: How the bandit decides ══════════════════════════════════
s = content_slide("HOW THE SYSTEM DECIDES FOR SOPHEA", 2)
# Left: what it knows about Sophea (plain, a few facts — not 34-dim talk)
L_W = 4700000
rect(s, MARGIN_L, 1120000, L_W, 4900000, fill=LIGHT_BG)
rect(s, MARGIN_L, 1120000, 91440, 4900000, fill=NAVY)
tf = textbox(s, MARGIN_L + 170000, 1250000, L_W - 300000, 420000)
para(tf, "What it knows about Sophea", 16, bold=True, color=NAVY, font_name=HEAD_FONT)
KNOWS = ["Age 42", "Non-smoker", "Managed blood pressure",
         "Active (field farming)", "Rice farmer, Kampong Cham", "Low wealth index"]
tfk = textbox(s, MARGIN_L + 170000, 1780000, L_W - 300000, 3600000)
first = True
for k in KNOWS:
    p = tfk.paragraphs[0] if first else tfk.add_paragraph()
    first = False
    p.space_before = Pt(14)
    r1 = p.add_run(); r1.text = "•  "; r1.font.size = Pt(16); r1.font.color.rgb = BLUE; r1.font.bold = True
    r2 = p.add_run(); r2.text = k; r2.font.size = Pt(15); r2.font.color.rgb = DARK_TXT
tf = textbox(s, MARGIN_L + 170000, 5450000, L_W - 300000, 450000)
para(tf, "(A short profile — 34 facts in all.)", 12, italic=True, color=GRAY)

# Right: 4 arm scores as horizontal bars
R_L = MARGIN_L + L_W + 350000
R_W = (MARGIN_L + CONTENT_W) - R_L
tf = textbox(s, R_L, 1180000, R_W, 380000)
para(tf, "It scores each option (higher = better)", 16, bold=True, color=NAVY,
     font_name=HEAD_FONT)
ARMS = [
    ("STANDARD", 0.52, RGBColor(0xD4, 0xE6, 0xF7), NAVY, True),
    ("RATED",    0.31, AMBER_BG, AMBER_TXT, False),
    ("REFER",    0.28, GREEN_BG, GREEN_ACC, False),
    ("DECLINE",  0.10, RED_BG,   RED_ACC,   False),
]
bar_top = 1980000; bar_h = 620000; bar_gap = 260000
bar_max = R_W - 1200000
for i, (arm, score, bg, acc, sel) in enumerate(ARMS):
    t = bar_top + i * (bar_h + bar_gap)
    tf = textbox(s, R_L, t - 300000, R_W, 280000)
    para(tf, f"{arm}", 13, bold=sel, color=acc)
    # track + fill
    rect(s, R_L, t, bar_max, bar_h, fill=LIGHT_BG)
    fillw = int(bar_max * score / 0.52)
    rect(s, R_L, t, fillw, bar_h, fill=acc)
    if sel:
        from defense_draw import outline
        outline(s, R_L, t, bar_max, bar_h, NAVY, width_pt=2.5)
    tfv = textbox(s, R_L + bar_max + 60000, t, 1100000, bar_h)
    tfv.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfv, f"{score:.2f}", 18, bold=sel, color=acc)
tf = textbox(s, R_L, bar_top + 4 * (bar_h + bar_gap) - 120000, R_W, 900000)
para(tf, "Highest score wins → STANDARD. Sophea gets coverage.", 15, bold=True, color=NAVY)
new_para(tf, "In plain words: it estimates how each option would pay off for "
         "someone like her, then adds a small bonus for options it hasn't tried "
         "often. (The maths is in Appendix A7.)", 12, italic=True, color=GRAY,
         space_before=6)
content_footer(s, 2, 11)

# ══ Slide 12: What the system earns ═══════════════════════════════════
s = content_slide("WHAT THE SYSTEM EARNS", 2)
rect(s, MARGIN_L, 1150000, CONTENT_W, 780000, fill=NAVY)
tf = textbox(s, MARGIN_L, 1260000, CONTENT_W, 560000)
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
para(tf, "Reward  =  Premiums collected  −  Claims paid", 24, bold=True,
     color=WHITE, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
EARN = [
    ("Insure someone healthy", "You collect premiums and pay few claims  →  earn",
     GREEN_BG, GREEN_ACC),
    ("Insure a frequent claimer", "Claims outrun the premiums  →  lose",
     RED_BG, RED_ACC),
    ("Decline everyone", "No premiums at all  →  earn nothing",
     LIGHT_BG, NAVY),
]
ew = (CONTENT_W - 2 * 300000) // 3
et = 2350000; eh = 2400000
for i, (hdr, body, bg, acc) in enumerate(EARN):
    l = MARGIN_L + i * (ew + 300000)
    rect(s, l, et, ew, eh, fill=bg)
    rect(s, l, et, ew, 82000, fill=acc)
    tfh = textbox(s, l + 150000, et + 250000, ew - 250000, 600000)
    para(tfh, hdr, 16, bold=True, color=acc, font_name=HEAD_FONT)
    tfb = textbox(s, l + 150000, et + 950000, ew - 250000, eh - 1050000)
    para(tfb, body, 15, color=DARK_TXT)
tf = textbox(s, MARGIN_L, 5150000, CONTENT_W, 900000)
para(tf, "So the system is rewarded for insuring the right people at the right "
     "price — not for saying yes to everyone, and not for saying no to everyone.",
     15, italic=True, color=NAVY)
new_para(tf, "Full actuarial detail — risk loadings, adverse selection, price "
         "elasticity — is in the reward simulator (thesis Table 8; Appendix A5).",
         11, italic=True, color=GRAY, space_before=8)
content_footer(s, 2, 12)

# ══ Slide 13: The fairness guardrail ══════════════════════════════════
s = content_slide("THE FAIRNESS GUARDRAIL", 2)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 560000)
para(tf, "PSI asks one question:", 16, bold=True, color=NAVY)
new_para(tf, "Are the people we approve today drifting away from the people we "
         "trained on?", 16, italic=True, color=GRAY, space_before=4)
ZONES = [
    ("GREEN", "below 0.10", "All clear — the mix of approvals is stable.",
     GREEN_BG, GREEN_ACC),
    ("AMBER", "0.10 – 0.25", "Watch closely — a moderate shift; flag for review.",
     AMBER_BG, AMBER_ACC),
    ("RED",   "above 0.25", "Stop and recalibrate — a major shift; escalate.",
     RED_BG, RED_ACC),
]
zt = 1950000; zh = 900000; zg = 110000
for i, (lab, thr, desc, bg, acc) in enumerate(ZONES):
    t = zt + i * (zh + zg)
    rect(s, MARGIN_L, t, CONTENT_W, zh, fill=bg)
    rect(s, MARGIN_L, t, 120000, zh, fill=acc)
    tfl = textbox(s, MARGIN_L + 220000, t, 2400000, zh)
    tfl.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfl, lab, 22, bold=True, color=acc, font_name=HEAD_FONT)
    tft = textbox(s, MARGIN_L + 2700000, t, 2200000, zh)
    tft.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tft, thr, 15, bold=True, color=DARK_TXT)
    tfd = textbox(s, MARGIN_L + 5000000, t, CONTENT_W - 5200000, zh)
    tfd.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfd, desc, 14, color=DARK_TXT)
tf = textbox(s, MARGIN_L, zt + 3 * (zh + zg) + 60000, CONTENT_W, 560000)
para(tf, "And when the system isn't sure, the case goes to a human expert "
     "(about 1 in 70). The exact PSI formula is in Appendix A8.", 13,
     italic=True, color=GRAY)
content_footer(s, 2, 13)

# ══ Slide 14: Dataset ═════════════════════════════════════════════════
s = content_slide("THE DATA", 3)
STATS = [
    ("2,000", "SYNTHETIC\nAPPLICANTS"),
    ("34", "FACTS ABOUT\nEACH PERSON"),
    ("4", "POSSIBLE\nDECISIONS"),
    ("4", "REAL-SURVEY\nANCHORS"),
]
stat_w = CONTENT_W // 4 - 50000
for i, (num, label) in enumerate(STATS):
    l = MARGIN_L + i * (stat_w + 50000)
    tf = textbox(s, l, 1160000, stat_w, 520000)
    para(tf, num, 36, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, l, 1700000, stat_w, 380000)
    para(tf2, label, 12, color=GRAY, align=PP_ALIGN.CENTER)
FEAT_CATS = [
    ("Demographics & Vitals", "Age, Gender, BMI", "3"),
    ("Lifestyle", "Smoking, Alcohol, Exercise", "3"),
    ("Social Determinants", "Education, Wealth, Self-rated health", "3"),
    ("Economic", "Monthly income, Family history", "2"),
    ("Clinical Flags", "Hypertension, Diabetes, Heart, COPD, Arthritis, TB, Hepatitis B", "7+1"),
    ("Region (one-hot)", "8 macro-regions (CDHS 2021-22)", "8"),
    ("Occupation (one-hot)", "Rice farmer 28%, Garment 20%, Market vendor 15%, Moto 12%…", "7"),
]
TBL_T = 2280000
tbl = s.shapes.add_table(len(FEAT_CATS) + 1, 3,
                         Emu(MARGIN_L), Emu(TBL_T),
                         Emu(CONTENT_W), Emu(3350000)).table
for ci, h in enumerate(["Category", "Features", "Dims"]):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(12)
for ri, (cat, feats, dims) in enumerate(FEAT_CATS):
    for ci, val in enumerate([cat, feats, dims]):
        c = tbl.cell(ri + 1, ci); c.text = val
        bg = LIGHT_BG if ri % 2 == 0 else WHITE
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(11)
                r.font.bold = (ci == 0)
                r.font.color.rgb = NAVY if ci == 0 else DARK_TXT
tf = textbox(s, MARGIN_L, 5780000, CONTENT_W, 480000)
para(tf, "Synthetic because no insurer would share real records — but shaped to "
     "match published Cambodia statistics (CDHS 2021-22, STEPS, ILO, WHO).", 12,
     italic=True, color=GRAY)
content_footer(s, 3, 14)

# ══ Slide 15: How we tested it ════════════════════════════════════════
s = content_slide("HOW WE TESTED IT", 3)
TEST = [
    ("5,000 applicants", "seen one at a time, in order — exactly how it would run in production.", NAVY),
    ("20 independent repeats", "each with a different random draw. The learning system won every time.", GREEN_ACC),
    ("Compared head-to-head", "against the incumbent static-rules approach on the same applicants.", BLUE),
]
tw = (CONTENT_W - 2 * 300000) // 3
tt = 1250000; th = 2650000
for i, (hdr, body, acc) in enumerate(TEST):
    l = MARGIN_L + i * (tw + 300000)
    rect(s, l, tt, tw, th, fill=LIGHT_BG)
    rect(s, l, tt, tw, 82000, fill=acc)
    tfh = textbox(s, l + 150000, tt + 250000, tw - 250000, 650000)
    para(tfh, hdr, 18, bold=True, color=acc, font_name=HEAD_FONT)
    tfb = textbox(s, l + 150000, tt + 1050000, tw - 250000, th - 1150000)
    para(tfb, body, 15, color=DARK_TXT)
rect(s, MARGIN_L, 4150000, CONTENT_W, 780000, fill=LIGHT_BG)
tf = textbox(s, MARGIN_L + 180000, 4260000, CONTENT_W - 360000, 560000)
para(tf, "A learning system has no train/test split — it learns as it goes. So we "
     "judge it by how much reward it loses versus a perfect-knowledge Oracle, "
     "averaged over the 20 repeats.", 14, color=DARK_TXT)
new_para(tf, "Details: Appendix A6.", 12, italic=True, color=GRAY, space_before=4)
tf = textbox(s, MARGIN_L, 5100000, CONTENT_W, 780000)
para(tf, "Under the hood: bootstrap 95% confidence intervals, paired Wilcoxon "
     "signed-rank tests, Bonferroni correction, Cohen's d effect sizes; "
     "experiments EXP-005 through EXP-015.", 11, italic=True, color=GRAY)
content_footer(s, 3, 15)

# ══ Slide 16: The headline result ═════════════════════════════════════
s = content_slide("THE HEADLINE RESULT", 4)
# Left: the number + plain line
rect(s, MARGIN_L, 1180000, 4900000, 1650000, fill=NAVY)
tf = textbox(s, MARGIN_L, 1280000, 4900000, 900000)
para(tf, "+25.2%", 60, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
tf = textbox(s, MARGIN_L, 2280000, 4900000, 440000)
para(tf, "more cumulative reward than the static rules", 13,
     color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
tf = textbox(s, MARGIN_L, 3050000, 4900000, 1200000)
para(tf, "$90,540", 30, bold=True, color=NAVY)
new_para(tf, "learning system (LinUCB)", 13, color=GRAY, space_before=2)
new_para(tf, "vs  $72,292  static rules (XGBoost)", 15, bold=True, color=DARK_TXT, space_before=10)
tf = textbox(s, MARGIN_L, 4550000, 4900000, 1300000)
para(tf, "For every $100 the old rules earned, the learning system earned $125 —",
     15, bold=True, color=NAVY)
new_para(tf, "and the gap held across all 20 repeats.", 15, italic=True,
         color=GRAY, space_before=4)
tf = textbox(s, MARGIN_L, 5850000, 4900000, 360000)
para(tf, "20 seeds · p < 0.001 · Cohen's d = 2.98", 11, italic=True, color=GRAY)
# Right: reward-curve figure
RC = os.path.join(FIG_DIR, "slides", "slide_reward_curves.png")
if os.path.exists(RC):
    rc_w = 5900000
    rc_l = MARGIN_L + 5100000
    s.shapes.add_picture(RC, Emu(rc_l), Emu(1350000), width=Emu(rc_w))
    tf = textbox(s, rc_l, 5350000, rc_w, 340000)
    para(tf, "Cumulative reward — learning system vs static rules.", 11,
         italic=True, color=GRAY, align=PP_ALIGN.CENTER)
content_footer(s, 4, 16)

# ══ Slide 17: The baseline ladder ═════════════════════════════════════
s = content_slide("THE BASELINE LADDER", 4)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 340000)
para(tf, "Every realistic alternative we tried lands below the bandits.", 15,
     italic=True, color=GRAY)
LADDER = [
    ("Oracle (perfect knowledge)",         "126,804", "124,187", "128,428", "100%",   LIGHT_BG),
    ("LogisticOracle ‡ (full-supervision)", "123,977", "121,794", "126,126", "98.1%",  LIGHT_BG),
    ("AlwaysRATED (trivial constant)",     "122,287", "119,528", "124,996", "96.8%",  AMBER_BG),
    ("LinTS  ← proposed",                  "93,723",  "91,105",  "96,481",  "74.2%",  GREEN_BG),
    ("LinUCB  ← proposed",                 "91,864",  "89,139",  "94,702",  "72.7%",  GREEN_BG),
    ("Epsilon-Greedy",                     "76,441",  "73,767",  "79,107",  "60.5%",  WHITE),
    ("Static XGB (incumbent)",             "72,206",  "70,125",  "74,352",  "57.1%",  WHITE),
    ("AlwaysSTANDARD",                     "34,684",  "33,694",  "35,871",  "27.5%",  WHITE),
    ("Random",                             "1,980",   "739",     "3,209",   "1.6%",   WHITE),
]
tbl = s.shapes.add_table(len(LADDER) + 1, 4,
                         Emu(MARGIN_L), Emu(1540000),
                         Emu(CONTENT_W), Emu(4500000)).table
for ci, h in enumerate(["Policy", "Cumulative Reward (mean)", "95% CI", "% of Oracle"]):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(13)
for ri, (pol, rew, cil, cih, pct, bg) in enumerate(LADDER):
    for ci, val in enumerate([pol, f"${rew}", f"[{cil}, {cih}]", pct]):
        c = tbl.cell(ri + 1, ci); c.text = val
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(12 if ci == 0 else 13)
                r.font.bold = ("proposed" in pol)
                r.font.color.rgb = NAVY if "proposed" in pol else DARK_TXT
tf = textbox(s, MARGIN_L, 6120000, CONTENT_W, 320000)
para(tf, "‡ The only policies above the bandits either see the future (Oracle) or "
     "approve nobody cheaply and everybody expensively (AlwaysRATED) — no "
     "regulator would allow the latter.", 11, italic=True, color=GRAY)
content_footer(s, 4, 17)

# ══ Slide 18: Side-by-side validation ═════════════════════════════════
s = content_slide("SOPHEA, THREE WAYS", 4)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 360000)
para(tf, "The same applicant, decided by three different systems:", 15,
     italic=True, color=GRAY)
PANELS = [
    ("Static rules", "today's incumbent", "DECLINE", RED_BG, RED_ACC,
     "Sees two fields, crosses two thresholds, says no."),
    ("LinUCB bandit", "our learning system", "STANDARD", GREEN_BG, GREEN_ACC,
     "Weighs her whole profile, offers standard cover."),
    ("Oracle", "knows the true risk", "STANDARD", RGBColor(0xD4, 0xE6, 0xF7), NAVY,
     "The perfect-knowledge benchmark agrees: standard."),
]
pw = (CONTENT_W - 2 * 300000) // 3
pt = 1650000; ph = 3550000
for i, (name, sub, verdict, bg, acc, note) in enumerate(PANELS):
    l = MARGIN_L + i * (pw + 300000)
    rect(s, l, pt, pw, ph, fill=LIGHT_BG)
    rect(s, l, pt, pw, 82000, fill=acc)
    tfh = textbox(s, l + 150000, pt + 220000, pw - 250000, 420000)
    para(tfh, name, 18, bold=True, color=NAVY, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
    tfs = textbox(s, l + 150000, pt + 640000, pw - 250000, 340000)
    para(tfs, sub, 12, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
    rect(s, l + 300000, pt + 1150000, pw - 600000, 900000, fill=bg)
    tfv = textbox(s, l + 300000, pt + 1150000, pw - 600000, 900000)
    tfv.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfv, verdict, 24, bold=True, color=acc, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
    tfn = textbox(s, l + 150000, pt + 2250000, pw - 250000, ph - 2350000)
    para(tfn, note, 13, color=DARK_TXT, align=PP_ALIGN.CENTER)
tf = textbox(s, MARGIN_L, 5400000, CONTENT_W, 560000)
para(tf, "The bandit reaches the answer the all-knowing benchmark picks — the "
     "static rule never can.", 16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
content_footer(s, 4, 18)

# ══ Slide 19: Fairness + HITL results ═════════════════════════════════
s = content_slide("FAIRNESS & HUMAN OVERSIGHT — RESULTS", 4)
col_half = CONTENT_W // 2 - 150000
ROW_H = 560000; ROW_GAP = 60000


def _grid(top, items):
    for i, (label, value, badge, bg, acc) in enumerate(items):
        col = i % 2; row = i // 2
        l = MARGIN_L + col * (col_half + 300000)
        t = top + row * (ROW_H + ROW_GAP)
        rect(s, l, t, col_half, ROW_H, fill=bg)
        rect(s, l, t, 91440, ROW_H, fill=acc)
        tfl = textbox(s, l + 140000, t + 70000, col_half * 6 // 10, 230000)
        para(tfl, label, 11, color=GRAY)
        tfb = textbox(s, l + col_half * 6 // 10, t + 70000,
                      col_half * 4 // 10 - 160000, 230000)
        para(tfb, badge, 10, bold=True, color=acc, align=PP_ALIGN.RIGHT)
        tfv = textbox(s, l + 140000, t + 300000, col_half - 220000, 230000)
        para(tfv, value, 14, bold=True, color=NAVY)


tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 260000)
para(tf, "IS IT FAIR?  (EXP-006, 20 seeds)", 13, bold=True, color=BLUE)
FAIR_ITEMS = [
    ("Region — drift (PSI)",      "0.082",     "GREEN", GREEN_BG, GREEN_ACC),
    ("Occupation — drift (PSI)",  "0.123",     "AMBER", AMBER_BG, AMBER_ACC),
    ("Region — approval parity",  "85.72%",    "PASS",  GREEN_BG, GREEN_ACC),
    ("Occupation — approval parity", "90.12%", "PASS",  GREEN_BG, GREEN_ACC),
]
_grid(1420000, FAIR_ITEMS)
tf = textbox(s, MARGIN_L, 2740000, CONTENT_W, 300000)
para(tf, "1 of 6 fairness checks failed narrowly (occupation) — we report it and "
     "explain why; no regulatory threshold is breached.", 11, italic=True, color=GRAY)

tf = textbox(s, MARGIN_L, 3260000, CONTENT_W, 260000)
para(tf, "DOES HUMAN OVERSIGHT HELP?  (EXP-008, 20 seeds)", 13, bold=True, color=BLUE)
HITL_ITEMS = [
    ("With human review",       "$103,951",         "vs $90,540",     LIGHT_BG, NAVY),
    ("Improvement",             "+14.8%",           "vs the bandit",  GREEN_BG, GREEN_ACC),
    ("Cases sent to a human",   "65 / 5,000",       "1.3% of cases",  LIGHT_BG, NAVY),
    ("Cost of that review",     "$2,263",           "2.2% of reward", LIGHT_BG, NAVY),
]
_grid(3560000, HITL_ITEMS)
tf = textbox(s, MARGIN_L, 4880000, CONTENT_W, 560000)
para(tf, "A human safety net adds real reward (+14.8%) for a small cost (2.2%) — "
     "sending only about 1 in 70 cases to an expert.", 13, italic=True, color=NAVY)
content_footer(s, 4, 19)

# ══ Slide 20: Findings & limitations ══════════════════════════════════
s = content_slide("FINDINGS & LIMITATIONS", 5)
tf = textbox(s, MARGIN_L, 1120000, CONTENT_W, 260000)
para(tf, "WHAT WE FOUND", 13, bold=True, color=BLUE)
FINDINGS = [
    ("Learning beats static rules",
     "+25.2%,  p < 0.001,  d = 2.98",
     "LinUCB earned $18,248 more than the static baseline across 20 repeats."),
    ("No demographic bias introduced",
     "85.72% & 90.12% approval parity",
     "Fairness held across regions and occupations."),
    ("The learning — not the exploration — is what works",
     "greedy version ties the full one (p = 0.58)",
     "It's the updating-as-it-goes that beats a frozen model."),
    ("Human oversight adds value cheaply",
     "+14.8% for 1.3% review, 2.2% cost",
     "A small human safety net pays for itself."),
]
FIND_W = (CONTENT_W - 300000) // 2
FIND_H = 880000; FIND_GAP = 100000; FIND_TOP = 1420000
for i, (hdr, value, detail) in enumerate(FINDINGS):
    col = i % 2; row = i // 2
    fl = MARGIN_L + col * (FIND_W + 300000)
    ft = FIND_TOP + row * (FIND_H + FIND_GAP)
    rect(s, fl, ft, FIND_W, FIND_H, fill=LIGHT_BG)
    rect(s, fl, ft, 91440, FIND_H, fill=NAVY)
    tfh = textbox(s, fl + 150000, ft + 80000, FIND_W - 200000, 260000)
    para(tfh, hdr, 12, bold=True, color=NAVY)
    tfv = textbox(s, fl + 150000, ft + 360000, FIND_W - 200000, 240000)
    para(tfv, value, 13, bold=True, color=DARK_TXT)
    tfd = textbox(s, fl + 150000, ft + 620000, FIND_W - 200000, 240000)
    para(tfd, detail, 11, color=GRAY)
find_bot = FIND_TOP + 2 * (FIND_H + FIND_GAP) - FIND_GAP
tf = textbox(s, MARGIN_L, find_bot + 130000, CONTENT_W, 260000)
para(tf, "AND WHERE WE'RE HONEST ABOUT THE LIMITS", 13, bold=True, color=AMBER_TXT)
LIM = [
    ("Synthetic data", "Anchored to real surveys, but not real insurance claims."),
    ("Single-period reward", "One-shot profit proxy — no multi-year renewals yet."),
    ("Calibrated to one country", "Cambodia only; a constant policy still tops the ladder."),
]
LIM_W = (CONTENT_W - 2 * 220000) // 3
LIM_TOP = find_bot + 420000; LIM_H = 1120000
for i, (hdr, body) in enumerate(LIM):
    l = MARGIN_L + i * (LIM_W + 220000)
    rect(s, l, LIM_TOP, LIM_W, LIM_H, fill=LIGHT_BG)
    rect(s, l, LIM_TOP, 91440, LIM_H, fill=AMBER_ACC)
    tfh = textbox(s, l + 150000, LIM_TOP + 100000, LIM_W - 250000, 300000)
    para(tfh, hdr, 13, bold=True, color=AMBER_TXT)
    tfb = textbox(s, l + 150000, LIM_TOP + 420000, LIM_W - 250000, LIM_H - 500000)
    para(tfb, body, 12, color=DARK_TXT)
content_footer(s, 5, 20)

# ══ Slide 21: Future work ═════════════════════════════════════════════
s = content_slide("FUTURE WORK", 5)
FW = [
    ("Handle change over time",
     ["Forgetting-factor updates + PSI early-warning",
      "Adapt faster when the population shifts"]),
    ("Richer models",
     ["Neural bandit extensions",
      "Move beyond 34 simple features"]),
    ("Real-world deployment",
     ["Shadow-mode trial with a Cambodian insurer",
      "Delayed reward via a claims-lag proxy"]),
    ("Lifetime customer value",
     ["Retention, renewals, cross-selling",
      "Beyond a single-decision reward"]),
]
FW_H = 2000000; FW_W = (CONTENT_W - 300000) // 2
for i, (hdr, lines) in enumerate(FW):
    col = i % 2; row = i // 2
    fl = MARGIN_L + col * (FW_W + 300000)
    ft = 1220000 + row * (FW_H + 200000)
    rect(s, fl, ft, FW_W, FW_H, fill=LIGHT_BG)
    rect(s, fl, ft, 91440, FW_H, fill=NAVY)
    tfh = textbox(s, fl + 150000, ft + 100000, FW_W - 200000, 380000)
    para(tfh, hdr, 15, bold=True, color=NAVY)
    tfb = textbox(s, fl + 150000, ft + 560000, FW_W - 200000, FW_H - 660000)
    for j, line in enumerate(lines):
        if j == 0:
            para(tfb, line, 13, color=DARK_TXT)
        else:
            new_para(tfb, line, 13, color=GRAY, space_before=6)
content_footer(s, 5, 21)

# ══ Slide 22: Takeaway ════════════════════════════════════════════════
s = content_slide("THE TAKEAWAY", 5)
rect(s, MARGIN_L, 1600000, CONTENT_W, 1500000, fill=LIGHT_BG)
tf = textbox(s, MARGIN_L, 1600000, CONTENT_W, 1500000)
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
r = p.add_run(); r.text = "2023: "; r.font.size = Pt(40); r.font.bold = True
r.font.color.rgb = GRAY; r.font.name = HEAD_FONT
r = p.add_run(); r.text = "DECLINE"; r.font.size = Pt(40); r.font.bold = True
r.font.color.rgb = RED_ACC; r.font.name = HEAD_FONT
r = p.add_run(); r.text = "     2026: "; r.font.size = Pt(40); r.font.bold = True
r.font.color.rgb = GRAY; r.font.name = HEAD_FONT
r = p.add_run(); r.text = "STANDARD"; r.font.size = Pt(40); r.font.bold = True
r.font.color.rgb = GREEN_ACC; r.font.name = HEAD_FONT
tf = textbox(s, MARGIN_L, 3600000, CONTENT_W, 900000)
para(tf, "The same woman. A system that finally sees her whole picture — and keeps "
     "learning.", 18, italic=True, color=DARK_TXT, align=PP_ALIGN.CENTER)
tf = textbox(s, MARGIN_L, 4700000, CONTENT_W, 700000)
para(tf, "Cambodia has hundreds of thousands of applicants like her.", 20,
     bold=True, color=NAVY, align=PP_ALIGN.CENTER)
content_footer(s, 5, 22)

# ══ Slide 23: Demonstration ═══════════════════════════════════════════
s = content_slide("LIVE DEMONSTRATION", 6)
DEMO_BEATS = [
    ("1", "Score Sophea live", "→  decision + the fairness guardrail (PSI), on screen"),
    ("2", "A higher-risk applicant", "→  see the decision and the reward change"),
    ("3", "Watch it learn", "→  cumulative-reward animation, learning system vs static"),
]
beat_h = 1000000; beat_gap = 250000; beat_top = 1550000
for i, (num, label, result) in enumerate(DEMO_BEATS):
    t = beat_top + i * (beat_h + beat_gap)
    rect(s, MARGIN_L, t, 500000, beat_h, fill=NAVY)
    tfn = textbox(s, MARGIN_L + 40000, t, 420000, beat_h, word_wrap=False)
    tfn.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfn, num, 20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 640000, t, CONTENT_W - 740000, beat_h)
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf2, label, 17, bold=True, color=NAVY)
    new_para(tf2, result, 15, color=DARK_TXT, space_before=4)
tf = textbox(s, MARGIN_L, 5150000, CONTENT_W, 400000)
para(tf, "A live FastAPI app — not a mockup.", 13, italic=True,
     color=GRAY, align=PP_ALIGN.CENTER)
content_footer(s, 6, 23)

# ══ Slides 24-25: Demo fallbacks (only if the live app fails) ══════════
DEMO_SHOTS_DIR = os.path.join(FIG_DIR, "demo_shots")


def demo_fallback_slide(title, img_filename, caption, phys):
    s = content_slide(title, 6)
    img_path = os.path.join(DEMO_SHOTS_DIR, img_filename)
    if os.path.exists(img_path):
        img_h = 4400000; img_w = int(img_h * 1440 / 900)
        img_l = MARGIN_L + (CONTENT_W - img_w) // 2
        s.shapes.add_picture(img_path, Emu(img_l), Emu(1200000),
                             width=Emu(img_w), height=Emu(img_h))
    tf = textbox(s, MARGIN_L, 5820000, CONTENT_W, 300000)
    para(tf, caption, 12, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
    content_footer(s, 6, phys)
    return s


demo_fallback_slide(
    "IF LIVE DEMO FAILS — A SCORED APPLICANT",
    "desk_underwriting.png",
    "Fallback screenshot — Underwriting Desk view, a sample applicant scored.", 24)
demo_fallback_slide(
    "IF LIVE DEMO FAILS — WATCH IT LEARN",
    "desk_learning.png",
    "Fallback screenshot — cumulative reward, learning system vs static rules.", 25)

# ══ Slide 26: Thanks (navy hero) ══════════════════════════════════════
s = new_slide()
rect(s, 0, 0, SW, SH, fill=NAVY)
tf = textbox(s, MARGIN_L, 1500000, CONTENT_W, 1000000)
para(tf, "Thank you for your attention.", 34, bold=True, color=WHITE,
     align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
tf = textbox(s, MARGIN_L, 2700000, CONTENT_W, 600000)
para(tf, "Questions are welcome.", 20, italic=True,
     color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
# Appendix menu (moved here from the old thank-you slide)
rect(s, MARGIN_L, 3800000, CONTENT_W, 54864, fill=RGBColor(0x16, 0x2D, 0x58))
tf = textbox(s, MARGIN_L, 3920000, CONTENT_W, 340000)
para(tf, "BACKUP SLIDES IN THE APPENDIX", 13, bold=True,
     color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
APP_MENU = [
    "A1 Baseline ladder   ·   A2 Number reconciliation   ·   A3 All 6 fairness checks",
    "A4 The maths   ·   A5 Sensitivity analysis   ·   A6 No train/test split",
    "A7 The exploration bonus (α)   ·   A8 The fairness index (PSI)",
]
tf = textbox(s, MARGIN_L, 4400000, CONTENT_W, 1100000)
for k, item in enumerate(APP_MENU):
    if k == 0:
        para(tf, item, 13, color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
    else:
        new_para(tf, item, 13, color=RGBColor(0xBD, 0xCE, 0xE4),
                 align=PP_ALIGN.CENTER, space_before=8)
# Navy footer override
h26 = 420624
rect(s, 0, FOOTER_TOP, SW, h26, fill=RGBColor(0x16, 0x2D, 0x58))
tf = textbox(s, 164592, FOOTER_TOP, 2834640, h26)
para(tf, "DAC  ·  ITC-AMS", 9, bold=True, color=WHITE)
tf = textbox(s, 3200400, FOOTER_TOP, 5943600, h26)
para(tf, "Q & A", 9, color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
tf = textbox(s, 9326880, FOOTER_TOP, 2743200, h26)
para(tf, f"8 July 2026  ·  26 / {TOTAL}", 9, color=WHITE, align=PP_ALIGN.RIGHT)


# ══════════════════════════════════════════════════════════════════════
#  APPENDIX  (A1-A8) — plain title chrome, no nav tabs
# ══════════════════════════════════════════════════════════════════════

def appendix_slide(title):
    s = new_slide()
    rect(s, 0, 0, SW, SH, fill=WHITE)
    title_block(s, title)
    return s


# ── A1: Complete Baseline Ladder ─────────────────────────────────────
s = appendix_slide("A1: COMPLETE BASELINE LADDER")
LADDER_A1 = LADDER  # identical to slide 17
tbl = s.shapes.add_table(len(LADDER_A1) + 1, 4,
                         Emu(MARGIN_L), Emu(1100000),
                         Emu(CONTENT_W), Emu(4600000)).table
for ci, h in enumerate(["Policy", "Cumulative Reward (mean)", "95% CI", "% of Oracle"]):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(13)
for ri, (pol, rew, cil, cih, pct, bg) in enumerate(LADDER_A1):
    for ci, val in enumerate([pol, f"${rew}", f"[{cil}, {cih}]", pct]):
        c = tbl.cell(ri + 1, ci); c.text = val
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(12 if ci == 0 else 13)
                r.font.bold = ("proposed" in pol)
                r.font.color.rgb = NAVY if "proposed" in pol else DARK_TXT
tf = textbox(s, MARGIN_L, 5780000, CONTENT_W, 350000)
para(tf, "‡ LogisticOracle: fit in-sample — not deployable. Oracle: full-information "
     "upper bound. AlwaysRATED is commercially & regulatorily inadmissible. "
     "Bandits lead every admissible alternative.", 12, italic=True, color=GRAY)
footer(s, "Appendix", "27", TOTAL)

# ── A2: Number Reconciliation ────────────────────────────────────────
s = appendix_slide("A2: NUMBER RECONCILIATION")
NUMS_A2 = [
    ("+25.2%",
     "EXP-005: LinUCB vs Static XGB (primary pre-registered result)",
     ["LinUCB mean $90,540 vs Static XGB mean $72,292",
      "Paired Wilcoxon p < 0.001, Cohen's d = 2.98, 20 seeds",
      "This is the headline figure cited throughout the thesis"]),
    ("+29.8%",
     "EXP-007: LinTS vs Static XGB (CRN benchmark harness)",
     ["LinTS mean $93,723 vs Static XGB mean $72,206",
      "Different harness (common random numbers) — not the pre-registered test",
      "Reported for completeness; primary comparison is EXP-005"]),
    ("+14.8%",
     "EXP-008: HITL reward vs vanilla bandit (20 seeds)",
     ["HITL $103,951 vs vanilla bandit $90,540, p < 0.001, d = 2.65",
      "Baseline is the vanilla bandit (NOT Static XGB or AlwaysRATED)",
      "At the single illustrative seed 42 this reads +6.5% ($102,100 vs $95,872)"]),
]
A2_H = 1480000
for i, (pct, subtitle, lines) in enumerate(NUMS_A2):
    t_a2 = 1180000 + i * (A2_H + 150000)
    rect(s, MARGIN_L, t_a2, CONTENT_W, A2_H, fill=LIGHT_BG)
    rect(s, MARGIN_L, t_a2, 91440, A2_H, fill=NAVY)
    tfh = textbox(s, MARGIN_L + 150000, t_a2 + 80000, 1550000, A2_H - 100000, word_wrap=False)
    tfh.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfh, pct, 32, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    tfs = textbox(s, MARGIN_L + 1850000, t_a2 + 80000, CONTENT_W - 1950000, 380000)
    para(tfs, subtitle, 13, bold=True, color=NAVY)
    tfb = textbox(s, MARGIN_L + 1850000, t_a2 + 500000, CONTENT_W - 1950000, A2_H - 580000)
    for j, line in enumerate(lines):
        if j == 0:
            para(tfb, line, 13, color=DARK_TXT)
        else:
            new_para(tfb, line, 13, color=GRAY, space_before=5)
footer(s, "Appendix", "28", TOTAL)

# ── A3: All 6 Fairness Criteria ──────────────────────────────────────
s = appendix_slide("A3: ALL 6 FAIRNESS CRITERIA (EXP-006)")
FAIR_A3 = [
    ("Criterion 1", "PSI Region ≤ 0.25",         "PSI = 0.082",  "GREEN", GREEN_BG, GREEN_ACC),
    ("Criterion 2", "PSI Occupation ≤ 0.25",     "PSI = 0.123",  "AMBER", AMBER_BG, AMBER_ACC),
    ("Criterion 3", "EEOC 4/5 rule — Region",    "85.72% ≥ 80%", "PASS", GREEN_BG, GREEN_ACC),
    ("Criterion 4", "EEOC 4/5 rule — Occupation", "90.12% ≥ 80%", "PASS", GREEN_BG, GREEN_ACC),
    ("Criterion 5", "Permutation test — Region",  "p = 0.132",    "PASS", GREEN_BG, GREEN_ACC),
    ("Criterion 6", "Permutation test — Occupation", "p < 0.001", "FAILED-with-interpretation", AMBER_BG, AMBER_ACC),
]
A3_ROW_H = 880000
A3_COL_W = (CONTENT_W - 300000) // 2
for i, (crit, rule, result, badge, bg, acc) in enumerate(FAIR_A3):
    col = i % 2; row = i // 2
    l_a3 = MARGIN_L + col * (A3_COL_W + 300000)
    t_a3 = 1200000 + row * (A3_ROW_H + 100000)
    rect(s, l_a3, t_a3, A3_COL_W, A3_ROW_H, fill=bg)
    rect(s, l_a3, t_a3, 91440, A3_ROW_H, fill=acc)
    tfh = textbox(s, l_a3 + 150000, t_a3 + 70000, A3_COL_W - 200000, 250000)
    para(tfh, f"{crit}: {rule}", 13, bold=True, color=NAVY)
    tfv = textbox(s, l_a3 + 150000, t_a3 + 340000, A3_COL_W - 200000, 250000)
    para(tfv, result, 15, bold=True, color=NAVY)
    tfb = textbox(s, l_a3 + 150000, t_a3 + 610000, A3_COL_W - 200000, 220000, word_wrap=False)
    tfb.vertical_anchor = MSO_ANCHOR.MIDDLE
    tfb.margin_top = 0; tfb.margin_bottom = 0
    para(tfb, badge, 12, bold=True, color=acc)
tf = textbox(s, MARGIN_L, 4190000, CONTENT_W, 450000)
para(tf, "Criterion 6: a statistically significant occupation disparity under the "
     "permutation test. But PSI = 0.123 (AMBER, monitor only) and parity 90.12% ≥ 80% "
     "— reported FAILED in the interest of honesty, not a hard stop.", 13,
     italic=True, color=GRAY)
footer(s, "Appendix", "29", TOTAL)

# ── A4: Mathematical Details ─────────────────────────────────────────
s = appendix_slide("A4: MATHEMATICAL DETAILS")
half_a4 = (CONTENT_W - 300000) // 2
rect(s, MARGIN_L, 1200000, half_a4, 4800000, fill=LIGHT_BG)
rect(s, MARGIN_L, 1200000, 91440, 4800000, fill=NAVY)
tf = textbox(s, MARGIN_L + 150000, 1300000, half_a4 - 200000, 380000)
para(tf, "LinUCB UPDATE RULE", 14, bold=True, color=NAVY)
tf = textbox(s, MARGIN_L + 150000, 1720000, half_a4 - 200000, 4100000)
LINUCB_LINES = [
    "Design matrix:  A ← A + xₜ xₜᵀ",
    "Reward vector:  b ← b + rₜ xₜ",
    "Ridge estimate: θ̂ = A⁻¹ b",
    "",
    "UCB score:",
    "  p(x) = θ̂ᵀ x + α √(xᵀ A⁻¹ x)",
    "",
    "PSI formula:",
    "  PSI = Σ (Pₙₑw − Pₒₗd) × ln(Pₙₑw / Pₒₗd)",
    "",
    "HITL dual-update:",
    "  If human overrides → update on human label",
    "  Else update on bandit label",
]
for j, line in enumerate(LINUCB_LINES):
    if j == 0:
        para(tf, line, 13, color=DARK_TXT)
    else:
        new_para(tf, line, 13, color=DARK_TXT, space_before=6)
right_a4_l = MARGIN_L + half_a4 + 300000
rect(s, right_a4_l, 1200000, half_a4, 4800000, fill=LIGHT_BG)
rect(s, right_a4_l, 1200000, 91440, 4800000, fill=NAVY)
tf = textbox(s, right_a4_l + 150000, 1300000, half_a4 - 200000, 380000)
para(tf, "KEY HYPERPARAMETERS", 14, bold=True, color=NAVY)
HYPER_A4 = [
    ("LinUCB α", "1.0"), ("LinTS v²", "1.0"), ("Ridge λ", "1.0"),
    ("Horizon T", "5,000"), ("Seeds", "20"), ("HITL threshold κ", "0.7"),
    ("Discount γ (EXP-015)", "0.999"), ("PSI AMBER threshold", "0.10"),
    ("PSI RED threshold", "0.25"),
]
tbl = s.shapes.add_table(len(HYPER_A4) + 1, 2,
                         Emu(right_a4_l + 150000), Emu(1750000),
                         Emu(half_a4 - 200000), Emu(4100000)).table
for ci, h in enumerate(["Parameter", "Value"]):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(13)
for ri, (param, val) in enumerate(HYPER_A4):
    bg = LIGHT_BG if ri % 2 == 0 else WHITE
    for ci, v in enumerate([param, val]):
        c = tbl.cell(ri + 1, ci); c.text = v
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(12); r.font.color.rgb = DARK_TXT
footer(s, "Appendix", "30", TOTAL)

# ── A5: Sensitivity Analysis (EXP-012, canon-backed) ─────────────────
s = appendix_slide("A5: SENSITIVITY ANALYSIS (EXP-012, 10 SEEDS)")
# α sweep — LinUCB cumulative reward
ALPHA_ROWS = [
    ("0.1", "$90,645", "−0.8%"),
    ("0.5", "$88,473", "−3.2%"),
    ("1.0 (default)", "$91,378", "BEST"),
    ("2.0", "$89,953", "−1.6%"),
    ("5.0", "$90,959", "−0.5%"),
]
tf = textbox(s, MARGIN_L, 1150000, CONTENT_W * 45 // 100, 300000)
para(tf, "α sweep — LinUCB cumulative reward", 13, bold=True, color=NAVY)
tbl = s.shapes.add_table(len(ALPHA_ROWS) + 1, 3,
                         Emu(MARGIN_L), Emu(1500000),
                         Emu(CONTENT_W * 45 // 100), Emu(2500000)).table
for ci, h in enumerate(["α", "Reward", "vs best"]):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(13)
for ri, (a, rew, res) in enumerate(ALPHA_ROWS):
    bg = GREEN_BG if res == "BEST" else LIGHT_BG
    for ci, val in enumerate([a, rew, res]):
        c = tbl.cell(ri + 1, ci); c.text = val
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(13)
                r.font.color.rgb = GREEN_ACC if res == "BEST" else DARK_TXT
# Right: LinUCB advantage over Static XGB across stress settings (canon)
right_l = MARGIN_L + CONTENT_W * 45 // 100 + 220000
right_w = CONTENT_W * 55 // 100 - 220000
ADV_ROWS = [
    ("Adverse selection ×1.0",  "+$26,371", "d = 4.70"),
    ("Adverse selection ×1.35", "+$20,028", "d = 3.05"),
    ("Adverse selection ×1.7",  "+$20,239", "d = 3.34"),
    ("Elasticity slope 2.5",    "+$23,222", "d = 1.14"),
    ("Elasticity slope 4.5",    "+$17,358", "d = 2.24"),
]
tf = textbox(s, right_l, 1150000, right_w, 300000)
para(tf, "LinUCB advantage over Static XGB (every setting)", 13, bold=True, color=NAVY)
tbl = s.shapes.add_table(len(ADV_ROWS) + 1, 3,
                         Emu(right_l), Emu(1500000),
                         Emu(right_w), Emu(2500000)).table
for ci, h in enumerate(["Stress setting", "Advantage", "Effect"]):
    c = tbl.cell(0, ci); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for p in c.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(13)
for ri, (setting, adv, d) in enumerate(ADV_ROWS):
    bg = LIGHT_BG if ri % 2 == 0 else WHITE
    for ci, val in enumerate([setting, adv, d]):
        c = tbl.cell(ri + 1, ci); c.text = val
        c.fill.solid(); c.fill.fore_color.rgb = bg
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(12)
                r.font.bold = (ci == 1)
                r.font.color.rgb = GREEN_ACC if ci == 1 else DARK_TXT
rect(s, MARGIN_L, 4350000, CONTENT_W, 1000000, fill=LIGHT_BG)
rect(s, MARGIN_L, 4350000, 91440, 1000000, fill=GREEN_ACC)
tf = textbox(s, MARGIN_L + 180000, 4460000, CONTENT_W - 360000, 800000)
para(tf, "Robust: α = 1.0 is regret-minimising, and LinUCB beats Static XGB at "
     "every α, adverse-selection factor and elasticity slope tested.", 14,
     bold=True, color=GREEN_ACC)
new_para(tf, "Note: α = 1.0 gives $91,378 over 10 seeds here; the headline "
         "$90,540 is the 20-seed EXP-005 figure — both real, different seed counts.",
         12, italic=True, color=GRAY, space_before=6)
footer(s, "Appendix", "31", TOTAL)

# ── A6: Why a bandit has no train/test split ─────────────────────────
s = appendix_slide("A6: WHY A BANDIT HAS NO TRAIN/TEST SPLIT")
tf = textbox(s, MARGIN_L, 1110000, CONTENT_W, 480000)
para(tf, "A contextual bandit learns online — there is no train/test split. "
     "Here is what that means, and how generalisation is measured instead.",
     13, italic=True, color=GRAY)
half_a6 = (CONTENT_W - 300000) // 2
right_a6_l = MARGIN_L + half_a6 + 300000
card(s, MARGIN_L, 1680000, half_a6, 2640000,
     header="Supervised ML  (e.g. Static XGB incumbent)",
     body_lines=[
         "Split data: train / validation / test",
         "Fit once on the training set",
         "Freeze the weights; deploy unchanged",
         "Generalisation = score on a held-out test set",
     ], header_size=14, body_size=13)
card(s, right_a6_l, 1680000, half_a6, 2640000,
     header="Contextual bandit  (LinUCB / LinTS)",
     body_lines=[
         "No split — meets applicants one at a time",
         "Each round: select arm → observe reward → update",
         "Every round is BOTH 'train' and 'test'",
         "Ridge prior λ = 1.0 regularises online — no static fit to overfit",
     ], header_size=14, body_size=13, bg=RGBColor(0xD4, 0xE6, 0xF7), accent=NAVY)
band_t6 = 4400000
rect(s, MARGIN_L, band_t6, CONTENT_W, 1700000, fill=GREEN_BG)
rect(s, MARGIN_L, band_t6, 91440, 1700000, fill=GREEN_ACC)
tf = textbox(s, MARGIN_L + 180000, band_t6 + 110000, CONTENT_W - 360000, 1570000)
para(tf, "HOW WE EVALUATE INSTEAD — generalisation without a holdout", 14,
     bold=True, color=GREEN_ACC)
new_para(tf, "• Performance = cumulative regret vs the Oracle, averaged over 20 "
         "independent random seeds — the seeds play the role of the held-out test set.",
         13, color=DARK_TXT, space_before=8)
new_para(tf, "• Pre-registered pass criteria + fixed seeds → fully reproducible; no "
         "test-set leakage is possible because there is no test set to leak.",
         13, color=DARK_TXT, space_before=5)
new_para(tf, "• The Static XGB incumbent IS fit offline and frozen — so the benchmark "
         "is fair: a supervised model at its best vs a bandit learning from scratch.",
         13, color=DARK_TXT, space_before=5)
footer(s, "Appendix", "32", TOTAL)

# ── A7: The exploration bonus (α) in plain words ─────────────────────
s = appendix_slide("A7: THE EXPLORATION BONUS (α), IN PLAIN WORDS")
rect(s, MARGIN_L, 1120000, CONTENT_W, 700000, fill=NAVY)
tf = textbox(s, MARGIN_L, 1230000, CONTENT_W, 480000)
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
para(tf, "Arm score  =  expected payoff  +  α × how-unsure-we-still-are", 20,
     bold=True, color=WHITE, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
# Labeled formula card
half_a7 = (CONTENT_W - 300000) // 2
rect(s, MARGIN_L, 2050000, half_a7, 2400000, fill=LIGHT_BG)
rect(s, MARGIN_L, 2050000, 91440, 2400000, fill=NAVY)
tf = textbox(s, MARGIN_L + 170000, 2170000, half_a7 - 300000, 420000)
para(tf, "The one formula:", 14, bold=True, color=NAVY)
tf = textbox(s, MARGIN_L + 170000, 2600000, half_a7 - 300000, 1750000)
para(tf, "UCB  =  x̄  +  α · √(xᵀA⁻¹x)", 18, bold=True, color=DARK_TXT)
new_para(tf, "x̄   →  best guess of the payoff", 13, color=GRAY, space_before=14)
new_para(tf, "α    →  how adventurous to be (we use 1.0)", 13, color=GRAY, space_before=6)
new_para(tf, "√(…) →  how uncertain we still are", 13, color=GRAY, space_before=6)
# Sophea walk
right_a7 = MARGIN_L + half_a7 + 300000
rect(s, right_a7, 2050000, half_a7, 2400000, fill=RGBColor(0xD4, 0xE6, 0xF7))
rect(s, right_a7, 2050000, 91440, 2400000, fill=NAVY)
tf = textbox(s, right_a7 + 170000, 2170000, half_a7 - 300000, 420000)
para(tf, "Sophea's STANDARD arm:", 14, bold=True, color=NAVY)
tf = textbox(s, right_a7 + 170000, 2600000, half_a7 - 300000, 1750000)
para(tf, "score 0.52  =  payoff guess  +  a small curiosity bonus", 14,
     bold=True, color=DARK_TXT)
new_para(tf, "The bonus nudges the system to try arms it hasn't seen often — so it "
         "keeps learning instead of locking in early.", 13, color=GRAY, space_before=12)
rect(s, MARGIN_L, 4650000, CONTENT_W, 1150000, fill=GREEN_BG)
rect(s, MARGIN_L, 4650000, 91440, 1150000, fill=GREEN_ACC)
tf = textbox(s, MARGIN_L + 180000, 4760000, CONTENT_W - 360000, 950000)
para(tf, "Too high → wastes decisions exploring.  Too low → never learns.", 14,
     bold=True, color=GREEN_ACC)
new_para(tf, "We swept α ∈ {0.1, 0.5, 1, 2, 5} over 10 seeds — the reward barely "
         "moves and α = 1.0 is best (Appendix A5).", 13, color=DARK_TXT, space_before=8)
footer(s, "Appendix", "33", TOTAL)

# ── A8: The fairness index (PSI) walkthrough ─────────────────────────
s = appendix_slide("A8: THE FAIRNESS INDEX (PSI), STEP BY STEP")
# Labeled formula
rect(s, MARGIN_L, 1120000, CONTENT_W, 900000, fill=LIGHT_BG)
rect(s, MARGIN_L, 1120000, 91440, 900000, fill=NAVY)
tf = textbox(s, MARGIN_L + 180000, 1210000, CONTENT_W - 360000, 380000)
para(tf, "PSI  =  Σ  (Aᵢ − Eᵢ) × ln(Aᵢ / Eᵢ)", 20, bold=True, color=DARK_TXT)
tf = textbox(s, MARGIN_L + 180000, 1620000, CONTENT_W - 360000, 340000)
para(tf, "Aᵢ = share we approve now in group i    ·    Eᵢ = share in the training data",
     13, italic=True, color=GRAY)
# Worked mini-example (2 buckets)
half_a8 = (CONTENT_W - 300000) // 2
rect(s, MARGIN_L, 2200000, half_a8, 2650000, fill=WHITE, line_color=DIVIDER)
tf = textbox(s, MARGIN_L + 150000, 2300000, half_a8 - 250000, 380000)
para(tf, "A worked example — 2 regions", 14, bold=True, color=NAVY)
EX = [
    "Region A:  trained 60%,  now 55%",
    "Region B:  trained 40%,  now 45%",
    "",
    "A: (0.55−0.60)·ln(0.55/0.60) = 0.0044",
    "B: (0.45−0.40)·ln(0.45/0.40) = 0.0059",
    "",
    "PSI ≈ 0.010   →   GREEN (all clear)",
]
tf = textbox(s, MARGIN_L + 150000, 2740000, half_a8 - 250000, 2000000)
for j, line in enumerate(EX):
    bold = line.startswith("PSI")
    col = GREEN_ACC if bold else DARK_TXT
    if j == 0:
        para(tf, line, 13, bold=bold, color=col)
    else:
        new_para(tf, line, 13, bold=bold, color=col, space_before=6)
# Thresholds + real numbers
right_a8 = MARGIN_L + half_a8 + 300000
ZONES_A8 = [
    ("GREEN", "PSI < 0.10", GREEN_BG, GREEN_ACC),
    ("AMBER", "0.10 – 0.25", AMBER_BG, AMBER_ACC),
    ("RED",   "PSI > 0.25", RED_BG, RED_ACC),
]
zt = 2200000; zh = 560000; zg = 90000
for i, (lab, thr, bg, acc) in enumerate(ZONES_A8):
    t = zt + i * (zh + zg)
    rect(s, right_a8, t, half_a8, zh, fill=bg)
    rect(s, right_a8, t, 91440, zh, fill=acc)
    tfl = textbox(s, right_a8 + 180000, t, 1600000, zh)
    tfl.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfl, lab, 16, bold=True, color=acc, font_name=HEAD_FONT)
    tft = textbox(s, right_a8 + 1900000, t, half_a8 - 2000000, zh)
    tft.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tft, thr, 14, bold=True, color=DARK_TXT)
tf = textbox(s, right_a8, zt + 3 * (zh + zg) + 40000, half_a8, 700000)
para(tf, "Our result (EXP-006, 20 seeds):", 13, bold=True, color=NAVY)
new_para(tf, "Region 0.082 (GREEN) · Occupation 0.123 (AMBER)", 13,
         color=DARK_TXT, space_before=6)
tf = textbox(s, MARGIN_L, 5100000, CONTENT_W, 700000)
para(tf, "PSI is a monitor, not an enforcer: it detects drift but does not change "
     "the policy. An enforcement layer is future work.", 13, italic=True, color=GRAY)
footer(s, "Appendix", "34", TOTAL)


# ══ Save ══════════════════════════════════════════════════════════════
prs.save(OUT)
print(f"Saved: {OUT}  ({len(prs.slides)} slides)")
