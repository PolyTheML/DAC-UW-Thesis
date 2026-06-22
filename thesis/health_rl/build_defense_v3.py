# thesis/health_rl/build_defense_v3.py
"""Build Poly_defense_presentation_v3.pptx from scratch."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from defense_tokens import *
from defense_draw import (rect, textbox, para, new_para, add_run,
                          title_block, footer, section_divider, card, outline)

OUT = r"thesis\health_rl\Poly_defense_presentation_v3.pptx"

prs = Presentation()
prs.slide_width  = Emu(SW)
prs.slide_height = Emu(SH)
BLANK = prs.slide_layouts[6]   # truly blank layout


def new_slide():
    return prs.slides.add_slide(BLANK)


# ── Methodology "you are here" pipeline (for zoom-in interstitials) ─────
PIPELINE_LABELS = ["Applicant\nContext", "Bandit\nPolicy", "Underwriting\nAction",
                   "Actuarial\nReward", "PSI + HITL\nGuardrail", "Decision"]


def pipeline_strip(s, top, highlight):
    """Draw the 6-stage methodology pipeline. Stages whose index is in `highlight`
    are full cobalt with a green 'you are here' frame; the rest are dimmed pale."""
    box_w = 1500000; box_h = 760000; gap = 200000
    total_w = len(PIPELINE_LABELS) * box_w + (len(PIPELINE_LABELS) - 1) * gap
    start_l = (SW - total_w) // 2
    for i, label in enumerate(PIPELINE_LABELS):
        l = start_l + i * (box_w + gap)
        on = i in highlight
        rect(s, l, top, box_w, box_h, fill=(NAVY if on else LIGHT_BG))
        if on:
            outline(s, l - 45000, top - 45000, box_w + 90000, box_h + 90000,
                    GREEN_ACC, width_pt=3.5)
        tf = textbox(s, l + 50000, top + 110000, box_w - 100000, box_h - 150000)
        para(tf, label, 12, bold=True, color=(WHITE if on else GRAY),
             align=PP_ALIGN.CENTER)
        if i < len(PIPELINE_LABELS) - 1:
            tf2 = textbox(s, l + box_w, top + 230000, gap, 400000)
            para(tf2, "→", 18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)


def zoom_slide(title, highlight, caption, footer_num):
    """Burgundy-style methodology zoom-in interstitial: pipeline with current
    stage(s) highlighted + a one-line 'now examining' caption."""
    s = new_slide()
    rect(s, 0, 0, SW, SH, fill=WHITE)
    title_block(s, title)
    # green legend chip
    tfl = textbox(s, MARGIN_L, 1700000, CONTENT_W, 320000)
    para(tfl, "▸ YOU ARE HERE", 11, bold=True, color=GREEN_ACC, align=PP_ALIGN.CENTER)
    pipeline_strip(s, 2550000, highlight)
    tfc = textbox(s, MARGIN_L + 1000000, 3850000, CONTENT_W - 2000000, 700000)
    para(tfc, caption, 16, italic=True, color=NAVY, align=PP_ALIGN.CENTER)
    footer(s, "Methodology & Model Design", footer_num, 43)
    return s


# ── Slide 1: Title (burgundy-chrome classic layout, logos) ────────────
_HERE     = os.path.dirname(__file__)
LOGO_ITC  = os.path.join(_HERE, "..", "ITC.jpg")
LOGO_AMS  = os.path.join(_HERE, "..", "AMS.png")
LOGO_DAC  = os.path.join(_HERE, "..", "DAC.jpg")
THESIS_TITLE = ("ADAPTIVE HEALTH INSURANCE UNDERWRITING VIA CONTEXTUAL BANDITS: "
                "A REINFORCEMENT LEARNING APPROACH FOR CAMBODIA")

s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)

# Logos (top): ITC left, AMS beside it, DAC right
for _path, _lx, _ly, _lw in [
    (LOGO_ITC, 0.6,  0.30, 1.0),
    (LOGO_AMS, 1.75, 0.40, 1.45),
    (LOGO_DAC, 11.3, 0.35, 1.45),
]:
    if os.path.exists(_path):
        s.shapes.add_picture(_path, Inches(_lx), Inches(_ly), width=Inches(_lw))

# Institution + department
tf = textbox(s, Inches(3.4), Inches(0.42), Inches(7.2), Inches(0.5))
para(tf, "Institute of Technology of Cambodia", 22, bold=True,
     color=DARK_TXT, align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
tf = textbox(s, Inches(3.4), Inches(0.92), Inches(7.2), Inches(0.4))
para(tf, "Department of Applied Mathematics and Statistics", 15,
     color=GRAY, align=PP_ALIGN.CENTER)

# Cobalt underline accents framing the title
rect(s, Inches(5.92), Inches(2.05), Inches(1.5), Inches(0.045), fill=NAVY)
tf = textbox(s, Inches(0.9), Inches(2.35), Inches(11.5), Inches(1.7))
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
para(tf, THESIS_TITLE, 27, bold=True, color=DARK_TXT,
     align=PP_ALIGN.CENTER, font_name=HEAD_FONT)
rect(s, Inches(5.92), Inches(4.25), Inches(1.5), Inches(0.045), fill=NAVY)

# Presenter
tf = textbox(s, 0, Inches(4.62), SW, Inches(0.34))
para(tf, "Thesis Defense — Presented by", 14, color=GRAY, align=PP_ALIGN.CENTER)
tf = textbox(s, 0, Inches(4.96), SW, Inches(0.5))
para(tf, "LUN CHANPOLY", 27, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
     font_name=HEAD_FONT)

# Metadata grid (ON Radet preserved as 4th cell)
_lx, _rx = Inches(1.5), Inches(7.5)
for _i, (_lt, _rt) in enumerate([
    ("Supervisor   :  Dr. HAS Sothea",       "Organization  :  DAC (Decent Actuarial Consultants)"),
    ("Duration       :  Mar 2026 – Jun 2026", "DAC Advisor  :  Mr. ON Radet"),
]):
    _y = Inches(5.68) + _i * Inches(0.36)
    tf = textbox(s, _lx, _y, Inches(5.6), Inches(0.34))
    para(tf, _lt, 14, color=DARK_TXT)
    tf = textbox(s, _rx, _y, Inches(5.6), Inches(0.34))
    para(tf, _rt, 14, color=DARK_TXT)

tf = textbox(s, 0, Inches(6.6), SW, Inches(0.38))
para(tf, "July 2026", 15, bold=True, color=GRAY, align=PP_ALIGN.CENTER)
footer(s, "Title", "–", 43)

# ── Slide 2: TOC ──────────────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "TABLE OF CONTENTS")
SECTIONS = [
    ("I",   "Introduction & Problem Background"),
    ("II",  "Literature Review"),
    ("III", "Methodology & Model Design"),
    ("IV",  "Results & Evaluation"),
    ("V",   "Conclusion & Future Work"),
]
START_T = 1200000; GAP = 830000; ROW_H = 700000
for i, (num, name) in enumerate(SECTIONS):
    t = START_T + i * GAP
    rect(s, MARGIN_L, t, 400000, ROW_H, fill=NAVY)
    tf = textbox(s, MARGIN_L + 50000, t + 200000, 300000, 350000)
    para(tf, num, 18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 500000, t + 200000, CONTENT_W - 600000, 350000)
    para(tf2, name, 16, color=NAVY)
footer(s, "Contents", "–", 43)

# ── Slide 3: Meet Sophea ──────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "MEET SOPHEA")

CARD_L = MARGIN_L; CARD_T = 1100000
CARD_W = 5200000; CARD_H = CONTENT_BOT - CARD_T

# Profile card
rect(s, CARD_L, CARD_T, CARD_W, CARD_H, fill=LIGHT_BG)
rect(s, CARD_L, CARD_T, 91440, CARD_H, fill=NAVY)
PAD_L = CARD_L + 160000
tf = textbox(s, PAD_L, CARD_T + 140000, CARD_W - 200000, 480000)
para(tf, "SOPHEA", 26, bold=True, color=NAVY)
tf2 = textbox(s, PAD_L, CARD_T + 640000, CARD_W - 200000, 340000)
para(tf2, "Age 42  ·  Kampong Cham Province  ·  Rice Farmer", 12,
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
    r1 = p.add_run(); r1.text = f"{label}:  "; r1.font.size = Pt(12)
    r1.font.bold = True; r1.font.color.rgb = NAVY
    r2 = p.add_run(); r2.text = value; r2.font.size = Pt(12)
    r2.font.color.rgb = GRAY

# Story + DECLINE column
R_L = CARD_L + CARD_W + 280000; R_T = CARD_T; R_W = SW - R_L - 200000
tf4 = textbox(s, R_L, R_T + 80000, R_W, 1350000)
para(tf4, "In 2023, Sophea walked into a private insurer in Phnom Penh "
     "and applied for voluntary health insurance.\n\nThe static "
     "underwriting system checked two fields.", 13, italic=True, color=GRAY)

FLAG_H = 550000
for i, (label, text) in enumerate([
        ("OCCUPATION:", "Agriculture"),
        ("CONDITION:", "Hypertension")]):
    ft = R_T + 1550000 + i * (FLAG_H + 120000)
    rect(s, R_L, ft, R_W, FLAG_H, fill=AMBER_BG)
    rect(s, R_L, ft, 73152, FLAG_H, fill=AMBER_ACC)
    tff = textbox(s, R_L + 130000, ft + 130000, R_W - 160000, FLAG_H - 160000)
    para(tff, f"{label}  {text}", 13, bold=True, color=AMBER_TXT)

ct = R_T + 2850000
tf5 = textbox(s, R_L, ct, R_W, 340000)
para(tf5, "Both thresholds crossed. System decision:", 12, italic=True, color=GRAY)
rect(s, R_L, ct + 400000, R_W, 820000, fill=RED_BG)
rect(s, R_L, ct + 400000, 109728, 820000, fill=RED_ACC)
tf6 = textbox(s, R_L + 170000, ct + 560000, R_W - 200000, 500000)
para(tf6, "DECLINE", 36, bold=True, color=RED_ACC)
tf7 = textbox(s, R_L, ct + 1380000, R_W, 500000)
para(tf7, "Sophea leaves without coverage.", 12, italic=True, color=GRAY)
new_para(tf7, "Was that the right answer?", 13, bold=True, color=NAVY,
         space_before=8)
footer(s, "Introduction & Problem Background", "1", 43)

# ── Slide 4: About DAC ────────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "ABOUT DECENT ACTUARIAL CONSULTANTS")

SERVICES = [
    "Appointed Actuary Services — Life & General Insurance, Southeast Asia",
    "IFRS 17 Implementation",
    "Product Development — Life & General Insurance",
    "Asset–Liability Management & Enterprise Risk Management (ALM/ERM)",
    "Mergers & Acquisitions Advisory",
    "Education & Cooperation — University partnerships, government-academia-industry",
]
# Left column: 3 services
col_w = (CONTENT_W - 200000) // 2
START_T = 1200000; ITEM_H = 700000; GAP = 80000
for i, svc in enumerate(SERVICES[:3]):
    t = START_T + i * (ITEM_H + GAP)
    card(s, MARGIN_L, t, col_w, ITEM_H, body_lines=[svc], body_size=11)
for i, svc in enumerate(SERVICES[3:]):
    t = START_T + i * (ITEM_H + GAP)
    card(s, MARGIN_L + col_w + 200000, t, col_w, ITEM_H,
         body_lines=[svc], body_size=11)
# Bottom context line
tf = textbox(s, MARGIN_L, 3950000, CONTENT_W, 400000)
para(tf, "HQ: Taipei, Taiwan  ·  Regional offices: Phnom Penh, Vietnam, SEA  "
     "·  Internship: March–June 2026  ·  Advisor: Mr. ON Radet",
     11, italic=True, color=GRAY)
footer(s, "Introduction & Problem Background", "2", 43)

# ── Slide 5: Cambodia Context ─────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "CAMBODIA HEALTH INSURANCE MARKET")

# Big stat
rect(s, MARGIN_L, 1200000, 3800000, 1800000, fill=NAVY)
tf = textbox(s, MARGIN_L + 100000, 1300000, 3600000, 900000)
para(tf, "< 2 %", 52, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tf2 = textbox(s, MARGIN_L + 100000, 2200000, 3600000, 400000)
para(tf2, "HEALTH-INSURANCE PENETRATION (2023 EST.)", 9,
     color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)

# 4 market bullets
FACTS = [
    "NSSF covers formal-sector workers only (~16% of population)",
    "Private underwriting is manual and rule-based",
    "Agent networks consume 15–30% of premium revenue",
    "No demographic-parity monitoring in practice",
]
for i, fact in enumerate(FACTS):
    rect(s, MARGIN_L, 3200000 + i * 580000, 40000, 400000, fill=BLUE)
    tf3 = textbox(s, MARGIN_L + 120000, 3240000 + i * 580000,
                  4800000, 420000)
    para(tf3, fact, 12, color=DARK_TXT)

# SDG panel (right)
rect(s, 6600000, 1200000, 5200000, 3800000, fill=LIGHT_BG)
rect(s, 6600000, 1200000, 91440, 3800000, fill=BLUE)
tf4 = textbox(s, 6780000, 1300000, 4900000, 400000)
para(tf4, "ALIGNMENT WITH CAMBODIA'S SDGs", 11, bold=True, color=BLUE)
SDG_DATA = [
    ("SDG 3", "Good Health & Well-being",
     "Widen voluntary health-insurance access beyond NSSF formal sector"),
    ("SDG 1", "No Poverty",
     "Shield households from catastrophic out-of-pocket health costs"),
    ("SDG 10", "Reduced Inequalities",
     "PSI fairness guardrail keeps underwriting demographically fair"),
]
for i, (num, name, desc) in enumerate(SDG_DATA):
    t = 1800000 + i * 1100000
    rect(s, 6780000, t, 900000, 700000, fill=NAVY)
    tfs = textbox(s, 6790000, t + 200000, 880000, 350000)
    para(tfs, num, 14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf5 = textbox(s, 7780000, t, 2900000, 360000)
    para(tf5, name, 13, bold=True, color=NAVY)
    tf6 = textbox(s, 7780000, t + 380000, 2900000, 360000)
    para(tf6, desc, 10, color=GRAY)

tf7 = textbox(s, MARGIN_L, 5600000, CONTENT_W, 400000)
para(tf7, "Sophea represents the 98% the current system was not built for.", 12,
     bold=True, color=NAVY, align=PP_ALIGN.CENTER)
footer(s, "Introduction & Problem Background", "3", 43)

# ── Slide 6: Problem Statement ────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "PROBLEM STATEMENT")

PROBLEMS = [
    ("Static Thresholds",
     "Fixed cutoffs ignore applicant context — Sophea's BMI, activity, "
     "and non-smoking status are invisible to the rule engine"),
    ("No Online Adaptation",
     "Claims feedback never reaches the model — static weights do not "
     "update from observed outcomes"),
    ("Demographic Blindspot",
     "No parity metric is tracked — systematic patterns against rural "
     "or occupational groups emerge invisibly"),
    ("No Intelligent Triage",
     "Human experts review routine cases instead of the borderline ones "
     "— like Sophea's — that need expert judgment"),
]
card_w = (CONTENT_W - 200000) // 2; card_h = 2100000
for i, (hdr, body) in enumerate(PROBLEMS):
    col = i % 2; row = i // 2
    l = MARGIN_L + col * (card_w + 200000)
    t = 1200000 + row * (card_h + 150000)
    card(s, l, t, card_w, card_h, header=hdr, body_lines=[body],
         header_size=14, body_size=12)
footer(s, "Introduction & Problem Background", "4", 43)

# ── Slide 7: Research Questions ───────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "RESEARCH QUESTIONS")

RQS = [
    ("RQ1", "Do contextual bandits achieve higher cumulative reward and lower "
            "regret than the Static XGBoost baseline over 5,000 rounds?"),
    ("RQ2", "Does the bandit framework maintain demographic fairness (regional "
            "and occupational approval-rate parity, PSI) without explicit "
            "fairness constraints?"),
    ("RQ3", "What is the relative performance ranking of LinTS, LinUCB, "
            "Epsilon-Greedy, and Static XGB?"),
    ("RQ4", "Is the framework technically feasible for deployment on "
            "low-resource mobile infrastructure (<200 ms latency)?"),
]
rq_h = 900000; rq_gap = 250000; rq_top = 1550000
for i, (num, text) in enumerate(RQS):
    t = rq_top + i * (rq_h + rq_gap)
    rect(s, MARGIN_L, t, 500000, rq_h, fill=NAVY)
    tf = textbox(s, MARGIN_L + 80000, t, 340000, rq_h)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, num, 16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 640000, t, CONTENT_W - 740000, rq_h)
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf2, text, 14, color=DARK_TXT)
footer(s, "Introduction & Problem Background", "5", 43)

# ── Slide 8: Objectives & Deliverables ───────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "PROJECT OBJECTIVES & DELIVERABLES")

# Left: 4 deliverables
col_w = (CONTENT_W - 300000) // 2
tf_hdr = textbox(s, MARGIN_L, 1150000, col_w, 350000)
para(tf_hdr, "4 DELIVERABLES", 12, bold=True, color=BLUE)
DELIVERABLES = [
    ("D1", "Synthetic Cambodia Health Insurance Dataset\n2,000 applicants · CDHS/STEPS/ILO/WHO anchored"),
    ("D2", "Contextual Bandit Underwriting Engine\nLinUCB · LinTS · Epsilon-Greedy · <200 ms latency"),
    ("D3", "Actuarial Reward Simulator\nProfit-based · adverse selection · elasticity model"),
    ("D4", "PSI Fairness Monitoring Framework\nGREEN/AMBER/RED alerts · region + occupation"),
]
BAND_TOP = 1600000; BAND_BOT = 6050000
L_CH = 800000
L_STEP = (BAND_BOT - BAND_TOP - L_CH) // (len(DELIVERABLES) - 1)
for i, (num, text) in enumerate(DELIVERABLES):
    t = BAND_TOP + i * L_STEP
    rect(s, MARGIN_L, t, 300000, L_CH, fill=NAVY)
    tfn = textbox(s, MARGIN_L, t, 300000, L_CH)
    tfn.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfn, num, 14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 380000, t, col_w - 450000, L_CH)
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    lines = text.split('\n')
    para(tf2, lines[0], 12, bold=True, color=NAVY)
    if len(lines) > 1:
        new_para(tf2, lines[1], 10, color=GRAY, space_before=4)

# Right: 5 objectives
r_l = MARGIN_L + col_w + 300000
tf_hdr2 = textbox(s, r_l, 1150000, col_w, 350000)
para(tf_hdr2, "5 SECONDARY OBJECTIVES", 12, bold=True, color=BLUE)
OBJECTIVES = [
    ("O1", "2,000-record CDHS-anchored synthetic dataset"),
    ("O2", "Benchmark LinUCB, LinTS, EpsGreedy vs Static XGB (5,000 rounds)"),
    ("O3", "PSI fairness guardrails — no demographic drift"),
    ("O4", "EEOC four-fifths approval-rate parity audit"),
    ("O5", "Human-in-the-loop wrapper — reward gain vs review cost"),
]
R_CH = 750000
R_STEP = (BAND_BOT - BAND_TOP - R_CH) // (len(OBJECTIVES) - 1)
for i, (num, text) in enumerate(OBJECTIVES):
    t = BAND_TOP + i * R_STEP
    rect(s, r_l, t, 300000, R_CH, fill=BLUE)
    tfn = textbox(s, r_l, t, 300000, R_CH)
    tfn.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tfn, num, 14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, r_l + 380000, t, col_w - 420000, R_CH)
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf2, text, 12, color=DARK_TXT)
footer(s, "Introduction & Problem Background", "6", 43)


# ── Slide 9: Literature Review Section Divider ────────────────────────
s = new_slide()
section_divider(s, "Literature Review", "7", "II.", 43)

# ── Slide 10: Literature Review ───────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "LITERATURE REVIEW")
THEMES = [
    ("Health Insurance in Emerging Markets",
     "CDHS 2021-22, ILO 2023, ADB — Cambodia context and data anchors. "
     "<2% penetration; NSSF formal-sector gap; manual static rules."),
    ("Linear Contextual Bandits",
     "LinUCB (Li et al. 2010), LinTS (Agrawal & Goyal 2013). "
     "Sub-linear regret O(d√T log T). Per-round update O(d²). "
     "Chosen for interpretability and emerging-market compute constraints."),
    ("Neural Contextual Bandits",
     "NeuralUCB, NeuralTS, EE-Net — relax linear reward assumption. "
     "Require large datasets; risk of overfitting on 2,000 records. Natural future-work candidate."),
    ("Fairness in Insurance ML",
     "Barocas et al., Ensign et al. — protected-attribute constraints, "
     "feedback-loop risk. Rural/occupational groups (Sophea’s category) most at risk."),
    ("Population Stability Index",
     "PSI = Σ(Aᵢ − Eᵢ) × ln(Aᵢ/Eᵢ). Siddiqi (2006); validated Yurdakul & Naranjo (2020). "
     "THREE ZONES: GREEN <0.10 · AMBER 0.10–0.25 · RED >0.25."),
]
THEME_H = 820000
for i, (hdr, body) in enumerate(THEMES):
    t = 1150000 + i * (THEME_H + 60000)
    card(s, MARGIN_L, t, CONTENT_W, THEME_H, header=hdr, body_lines=[body],
         header_size=12, body_size=10)
footer(s, "Literature Review", "7", 43)

# ── Slide 11: Algorithm Comparison Table ─────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "ALGORITHM COMPARISON")

tbl_rows = 6; tbl_cols = 5
tbl = s.shapes.add_table(tbl_rows, tbl_cols,
                          Emu(MARGIN_L), Emu(1150000),
                          Emu(CONTENT_W), Emu(5100000)).table
HEADERS = ["Algorithm", "Exploration", "Regret", "Per-Round Cost", "Data Need"]
ALG_ROWS = [
    ["LinUCB\n(Li et al. 2010)", "UCB bonus:\nα√(xᵀA⁻¹x)", "O(d√T log T)", "O(d²)", "Moderate"],
    ["LinTS\n(Agrawal & Goyal 2013)", "Posterior sampling:\nθ̃ ~ N(θ̂, v²A⁻¹)", "O(d√T log T)", "O(d²)", "Moderate"],
    ["NeuralUCB\n(Zhou et al. 2020)", "Gradient confidence", "Õ(d̃√T)", "O(‖θ‖·T)", "Large"],
    ["EE-Net\n(Ban et al. 2022)", "Learned exploration", "Empirical only", "O(‖θ‖·T)", "Large"],
    ["Epsilon-Greedy", "ε-random (ε=0.15)", "O(T^(2/3))", "O(d²)", "Low"],
]
for col_i, hdr in enumerate(HEADERS):
    cell = tbl.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for para_obj in cell.text_frame.paragraphs:
        for run in para_obj.runs:
            run.font.color.rgb = WHITE; run.font.bold = True; run.font.size = Pt(11)
for row_i, row in enumerate(ALG_ROWS):
    bg = LIGHT_BG if row_i % 2 == 0 else WHITE
    for col_i, val in enumerate(row):
        cell = tbl.cell(row_i + 1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.color.rgb = NAVY if col_i == 0 else DARK_TXT
                r.font.bold = (col_i == 0)
# Highlight LinUCB and LinTS rows (rows 1 and 2 = index 0-based data rows)
for row_i in [1, 2]:
    tbl.cell(row_i, 0).fill.solid()
    tbl.cell(row_i, 0).fill.fore_color.rgb = RGBColor(0xD4, 0xE6, 0xF7)
footer(s, "Literature Review", "8", 43)

# ── Slide 12: Methodology Section Divider ────────────────────────────
s = new_slide()
section_divider(s, "Methodology & Model Design", "9", "III.", 43)

# ── Slide 13: System Architecture ────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "SYSTEM ARCHITECTURE")
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
    rect(s, l, 1400000, box_w, box_h, fill=bg)
    tf = textbox(s, l + 50000, 1500000, box_w - 100000, box_h - 100000)
    para(tf, label, 12, bold=True, color=fg, align=PP_ALIGN.CENTER)
    if i < len(PIPELINE) - 1:
        tf2 = textbox(s, l + box_w, 1600000, gap, 500000)
        para(tf2, "→", 18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

BULLETS = [
    "34-dimensional applicant context vector (standardised features)",
    "Four underwriting arms: STANDARD · RATED · DECLINE · REFER",
    "Actuarial simulator returns reward: premium revenue − expected claims (+ noise ±8%)",
    "PSI guardrail monitors portfolio drift on 500-round sliding window",
    "HITL wrapper escalates uncertain cases (uncertainty > κ threshold)",
]
for i, b in enumerate(BULLETS):
    rect(s, MARGIN_L, 2400000 + i * 600000, 40000, 400000, fill=BLUE)
    tf3 = textbox(s, MARGIN_L + 120000, 2440000 + i * 600000, CONTENT_W - 200000, 420000)
    para(tf3, b, 12, color=DARK_TXT)
footer(s, "Methodology & Model Design", "9", 43)

# ── Zoom-in 1: Applicant Context (you-are-here) ──────────────────────
zoom_slide("ZOOM-IN: APPLICANT CONTEXT", {0},
           "Now examining how each applicant becomes a 34-dimensional context vector.",
           "10")

# ── Slide 14: Dataset & Context ───────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "DATASET & CONTEXT")
# 4 big stats (top row)
STATS = [
    ("2,000", "SYNTHETIC\nAPPLICANTS"),
    ("34", "CONTEXT\nFEATURES"),
    ("4", "UNDERWRITING\nARMS"),
    ("4", "ANCHORING\nSOURCES"),
]
stat_w = CONTENT_W // 4 - 50000
for i, (num, label) in enumerate(STATS):
    l = MARGIN_L + i * (stat_w + 50000)
    tf = textbox(s, l, 1150000, stat_w, 500000)
    para(tf, num, 36, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, l, 1680000, stat_w, 350000)
    para(tf2, label, 9, color=GRAY, align=PP_ALIGN.CENTER)

# Feature table
FEAT_CATS = [
    ("Demographics & Vitals", "Age, Gender, BMI", "3"),
    ("Lifestyle", "Smoking, Alcohol, Exercise", "3"),
    ("Social Determinants", "Education, Wealth, Self-rated health", "3"),
    ("Economic", "Monthly income, Family history", "2"),
    ("Clinical Flags", "Hypertension, Diabetes, Heart, COPD, Arthritis, TB, Hepatitis B", "7+1"),
    ("Region (one-hot)", "8 macro-regions (CDHS 2021-22)", "8"),
    ("Occupation (one-hot)", "Rice farmer 28%, Garment 20%, Market vendor 15%, Moto 12%…", "7"),
]
TBL_L = MARGIN_L; TBL_T = 2200000
tbl14 = s.shapes.add_table(len(FEAT_CATS)+1, 3,
                          Emu(TBL_L), Emu(TBL_T),
                          Emu(CONTENT_W), Emu(4000000)).table
for col_i, hdr in enumerate(["Category", "Features", "Dims"]):
    cell = tbl14.cell(0, col_i)
    cell.text = hdr; cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (cat, feats, dims) in enumerate(FEAT_CATS):
    for col_i, val in enumerate([cat, feats, dims]):
        cell = tbl14.cell(row_i+1, col_i)
        cell.text = val
        bg = LIGHT_BG if row_i % 2 == 0 else WHITE
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9)
                r.font.bold = (col_i == 0)
                r.font.color.rgb = NAVY if col_i == 0 else DARK_TXT
footer(s, "Methodology & Model Design", "10", 43)

# ── Zoom-in 2: Actuarial Reward (you-are-here) ───────────────────────
zoom_slide("ZOOM-IN: ACTUARIAL REWARD", {3},
           "Now examining how each underwriting action is scored into an actuarial reward.",
           "11")

# ── Slide 15: Reward Simulator ────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "ACTUARIAL REWARD SIMULATOR (TABLE 8)")

# Formula card at top
tf_f = textbox(s, MARGIN_L, 1100000, CONTENT_W, 400000)
para(tf_f, "Reward = Premium Revenue − Expected Claims  (noise ±8%)  "
     "·  Adverse-selection factor 1.35 when risk multiplier m > 2.0  "
     "·  Elasticity slope 3.5", 11, italic=True, color=GRAY)

# Table 8
REWARD_HDRS = ["Arm", "Base Premium", "Expected Claims", "Acceptance Prob.", "Net Reward Formula"]
REWARD_ROWS = [
    ["STANDARD",
     "$200 × m",
     "$150 × m",
     "High",
     "Premium − Claims ± noise"],
    ["RATED",
     "$200 × m × load",
     "$150 × m × 1.35 (if m>2)",
     "Medium (elasticity −3.5 slope)",
     "Premium − Claims ± noise"],
    ["DECLINE",
     "$0",
     "$0",
     "N/A",
     "−$10 (opportunity cost)"],
    ["REFER",
     "Deferred",
     "Deferred",
     "Deferred to human",
     "0.70 × max(r) − $35"],
]
tbl15 = s.shapes.add_table(len(REWARD_ROWS)+1, len(REWARD_HDRS),
                            Emu(MARGIN_L), Emu(1700000),
                            Emu(CONTENT_W), Emu(3600000)).table
for col_i, hdr in enumerate(REWARD_HDRS):
    cell = tbl15.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(11)
ARM_COLORS = {
    "STANDARD": RGBColor(0xD4, 0xE6, 0xF7),
    "RATED":    RGBColor(0xFE, 0xF3, 0xCD),
    "DECLINE":  RED_BG,
    "REFER":    GREEN_BG,
}
for row_i, row in enumerate(REWARD_ROWS):
    arm_name = row[0]
    row_bg = ARM_COLORS.get(arm_name, LIGHT_BG)
    for col_i, val in enumerate(row):
        cell = tbl15.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = row_bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.bold = (col_i == 0)
                r.font.color.rgb = NAVY if col_i == 0 else DARK_TXT

# Key design note
tf_note = textbox(s, MARGIN_L, 5450000, CONTENT_W, 700000)
para(tf_note, "Design rationale: DECLINE penalty prevents over-rejection; "
     "REFER formula incentivises selective escalation rather than blanket referral.", 11,
     italic=True, color=GRAY)
footer(s, "Methodology & Model Design", "11", 43)

# ── Zoom-in 3: Bandit Policy & Action (you-are-here) ─────────────────
zoom_slide("ZOOM-IN: BANDIT POLICY & ACTION", {1, 2},
           "Now examining how the bandit reads the context and selects an underwriting action.",
           "12")

# ── Slide 16: Bandit — Context + Values ───────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "BANDIT IN ACTION: SOPHEA’S CONTEXT & ARM SCORES")

# Left: Sophea's feature vector
LEFT_W = CONTENT_W // 2 - 150000
card(s, MARGIN_L, 1100000, LEFT_W, 5200000,
     header="Sophea’s Context Vector (34 dims, key shown)",
     body_lines=[], header_size=12)
SOPHEA_DIMS = [
    ("age_std",        "0.3"),
    ("bmi_std",        "−0.1"),
    ("smoker",         "0  (non-smoker)"),
    ("hypertension",   "1  (managed)"),
    ("kampong_cham",   "1  (region one-hot)"),
    ("agriculture",    "1  (occupation one-hot)"),
    ("wealth_low",     "1"),
    ("education_prim", "1"),
    ("… 26 more", "—"),
]
tf_dims = textbox(s, MARGIN_L + 170000, 1620000, LEFT_W - 200000, 4400000)
first = True
for feat, val in SOPHEA_DIMS:
    p = tf_dims.paragraphs[0] if first else tf_dims.add_paragraph()
    first = False
    p.space_before = Pt(8)
    r1 = p.add_run(); r1.text = f"{feat}:  "
    r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = NAVY
    r2 = p.add_run(); r2.text = val
    r2.font.size = Pt(11); r2.font.color.rgb = DARK_TXT

# Right: LinUCB formula + arm scores
RIGHT_L = MARGIN_L + LEFT_W + 300000
RIGHT_W = CONTENT_W - LEFT_W - 300000

card(s, RIGHT_L, 1100000, RIGHT_W, 2400000,
     header="LinUCB Arm Score Formula",
     body_lines=[
         "UCBᵃ(x) = θ̂ᵃᵀ x  +  α × √(xᵀ Aᵃ⁻¹ x)",
         "",
         "θ̂ᵃ = posterior mean weights for arm a",
         "α = exploration bonus scaling (default 1.0)",
         "x = Sophea’s 34-dim context vector",
     ], header_size=12, body_size=11)

# Arm scores
ARM_SCORE_DATA = [
    ("RATED",     0.31, AMBER_BG,  AMBER_TXT),
    ("STANDARD",  0.52, RGBColor(0xD4, 0xE6, 0xF7), NAVY),
    ("DECLINE",   0.10, RED_BG,    RED_ACC),
    ("REFER",     0.28, GREEN_BG,  GREEN_ACC),
]
tf_arm_hdr = textbox(s, RIGHT_L, 3650000, RIGHT_W, 360000)
para(tf_arm_hdr, "Arm Scores (LinUCB, Sophea):", 12, bold=True, color=NAVY)
for i, (arm, score, bg, fg) in enumerate(ARM_SCORE_DATA):
    t = 4100000 + i * 560000
    rect(s, RIGHT_L, t, RIGHT_W, 480000, fill=bg)
    tf_arm = textbox(s, RIGHT_L + 120000, t + 80000, RIGHT_W - 240000, 340000)
    para(tf_arm, f"{arm}:  {score:.2f}", 13, bold=(arm == "STANDARD"), color=fg)
    # Bold border for selected arm
    if arm == "STANDARD":
        rect(s, RIGHT_L, t, RIGHT_W, 480000, line_color=NAVY)

tf_verdict = textbox(s, RIGHT_L, 6350000, RIGHT_W, 380000)
para(tf_verdict, "→ argmax = STANDARD  (Sophea gets coverage)", 13,
     bold=True, color=NAVY)
footer(s, "Methodology & Model Design", "12", 43)

# ── Slide 17: Bandit — Selection + Policy Ladder ─────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "POLICY LADDER: CUMULATIVE REWARD OVER 5,000 ROUNDS")

# ArgMax panel
rect(s, MARGIN_L, 1100000, CONTENT_W, 420000, fill=RGBColor(0xD4, 0xE6, 0xF7))
tf_am = textbox(s, MARGIN_L + 150000, 1130000, CONTENT_W - 200000, 380000)
para(tf_am, "Sophea’s Round: argmax UCB = STANDARD  →  Policy issues coverage",
     13, bold=True, color=NAVY)

# Policy ladder table
LADDER_HDRS = ["Rank", "Policy", "Cumul. Reward", "vs Static XGB", "Status"]
LADDER_ROWS = [
    ("1", "Oracle",           "126,804", "+75.6%",  "Ceiling (inadmissible)"),
    ("2", "LinTS",            " 93,723", "+29.8%",  "Admissible ✓"),
    ("3", "LinUCB",           " 91,864", "+27.2%",  "Admissible ✓"),
    ("4", "Epsilon-Greedy",   " 76,441", "+ 5.9%",  "Admissible ✓"),
    ("5", "Static XGB",       " 72,206", "baseline","Baseline"),
    ("6", "AlwaysSTANDARD",   " 34,684", "−52.0%","Trivial ✗"),
    ("7", "Random",           "  1,980", "−97.3%","Trivial ✗"),
]
tbl17 = s.shapes.add_table(len(LADDER_ROWS)+1, len(LADDER_HDRS),
                            Emu(MARGIN_L), Emu(1680000),
                            Emu(CONTENT_W), Emu(4400000)).table
for col_i, hdr in enumerate(LADDER_HDRS):
    cell = tbl17.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(11)
LADDER_ROW_STYLES = [
    LIGHT_BG,                        # Oracle
    RGBColor(0xD4, 0xE6, 0xF7),      # LinTS  (highlight)
    RGBColor(0xD4, 0xE6, 0xF7),      # LinUCB (highlight)
    LIGHT_BG,                        # EpsGreedy
    RGBColor(0xFE, 0xF3, 0xCD),      # Static XGB baseline
    WHITE,                           # AlwaysSTANDARD
    WHITE,                           # Random
]
for row_i, (row, bg) in enumerate(zip(LADDER_ROWS, LADDER_ROW_STYLES)):
    for col_i, val in enumerate(row):
        cell = tbl17.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.bold = (col_i in [0, 1])
                r.font.color.rgb = NAVY if col_i <= 1 else DARK_TXT

# AlwaysRATED inadmissibility note
tf_note17 = textbox(s, MARGIN_L, 6200000, CONTENT_W, 450000)
para(tf_note17,
     "Note: AlwaysRATED = 122,287 (between Oracle and LinTS) — inadmissible: "
     "denies all low-risk applicants coverage; discriminatory by design.",
     11, italic=True, color=GRAY)
footer(s, "Methodology & Model Design", "13", 43)

# ── Zoom-in 4: Fairness Guardrail & HITL (you-are-here) ──────────────
zoom_slide("ZOOM-IN: FAIRNESS GUARDRAIL & HITL", {4},
           "Now examining the PSI fairness guardrail and the human-in-the-loop review wrapper.",
           "14")

# ── Slide 18: PSI Guardrail ───────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "PSI FAIRNESS GUARDRAIL")

# Formula
tf_psi_f = textbox(s, MARGIN_L, 1100000, CONTENT_W, 420000)
para(tf_psi_f,
     "PSI = Σ (Aᵢ − Eᵢ) × ln(Aᵢ / Eᵢ)   "
     "·   Applied per 500-round sliding window   "
     "·   Monitored on: region (8 groups) + occupation (7 groups) separately",
     12, italic=True, color=GRAY)
rect(s, MARGIN_L, 1580000, CONTENT_W, 27432, fill=DIVIDER)

# Traffic-light zones
ZONES = [
    ("GREEN", "PSI < 0.10", "No significant shift — policy is stable",
     GREEN_BG, GREEN_ACC),
    ("AMBER", "0.10 ≤ PSI ≤ 0.25",
     "Moderate shift — monitor closely; flag for review",
     AMBER_BG, AMBER_ACC),
    ("RED",   "PSI > 0.25",
     "Major shift — halt or recalibrate bandit; escalate to compliance",
     RED_BG, RED_ACC),
]
ZONE_W = (CONTENT_W - 200000) // 3
for i, (label, threshold, desc, bg, acc) in enumerate(ZONES):
    l = MARGIN_L + i * (ZONE_W + 100000)
    t = 1750000
    zone_h = 3000000
    rect(s, l, t, ZONE_W, zone_h, fill=bg)
    rect(s, l, t, ZONE_W, 600000, fill=acc)
    tf_z1 = textbox(s, l + 80000, t + 120000, ZONE_W - 160000, 400000)
    para(tf_z1, label, 22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf_z2 = textbox(s, l + 80000, t + 750000, ZONE_W - 160000, 400000)
    para(tf_z2, threshold, 14, bold=True, color=acc, align=PP_ALIGN.CENTER)
    tf_z3 = textbox(s, l + 80000, t + 1250000, ZONE_W - 160000, 1600000)
    para(tf_z3, desc, 11, color=DARK_TXT)

# Siddiqi reference + result note
tf_src = textbox(s, MARGIN_L, 4900000, CONTENT_W, 750000)
para(tf_src,
     "Source: Siddiqi (2006) · Validated: Yurdakul & Naranjo (2020)\n"
     "EXP-006 result: LinUCB GREEN on all 8 regions + 7 occupations across 20 seeds "
     "(mean PSI 0.042 region / 0.037 occupation); criterion 6 FAILED-with-interpretation "
     "(EpsGreedy AMBER on 1 seed).",
     11, italic=True, color=GRAY)
footer(s, "Methodology & Model Design", "14", 43)

# ── Slide 19: Human-in-the-Loop (HITL) ───────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "HUMAN-IN-THE-LOOP (HITL) WRAPPER")

# Loop diagram (left side)
LOOP_W = CONTENT_W // 2 - 100000
LOOP_STEPS = [
    ("1. Bandit selects arm", NAVY, WHITE,
     "UCB / TS score computed for each arm"),
    ("2. Uncertainty check", BLUE, WHITE,
     "If max score − 2nd score < κ (0.7) → REFER"),
    ("3. Human actuary reviews", RGBColor(0xC0, 0x70, 0x00), WHITE,
     "Expert sees full context; overrides if needed"),
    ("4. Dual update", GREEN_ACC, WHITE,
     "Update selected arm reward + REFER arm penalty\n"
     "Without dual update: REFER over-selects (gotcha)"),
]
STEP_H = 1100000
for i, (step, bg, fg, note) in enumerate(LOOP_STEPS):
    t = 1150000 + i * (STEP_H + 80000)
    rect(s, MARGIN_L, t, LOOP_W, STEP_H, fill=bg)
    tf_ls = textbox(s, MARGIN_L + 130000, t + 80000, LOOP_W - 180000, 380000)
    para(tf_ls, step, 12, bold=True, color=fg)
    tf_ln = textbox(s, MARGIN_L + 130000, t + 500000, LOOP_W - 180000, 500000)
    para(tf_ln, note, 10, color=fg, italic=True)
    if i < len(LOOP_STEPS) - 1:
        tf_arr = textbox(s, MARGIN_L + LOOP_W // 2 - 100000,
                         t + STEP_H + 10000, 300000, 120000)
        para(tf_arr, "↓", 14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

# Right panel: key parameters + headline result
RIGHT_L19 = MARGIN_L + LOOP_W + 250000
RIGHT_W19 = CONTENT_W - LOOP_W - 250000

card(s, RIGHT_L19, 1150000, RIGHT_W19, 1600000,
     header="Key Parameters",
     body_lines=[
         "κ = 0.7   (uncertainty threshold for headline result)",
         "Review rate: 1.5% of rounds",
         "Reward gain: +6.5% vs vanilla bandit (p=0.017, d=0.87)",
     ], header_size=12, body_size=11)

card(s, RIGHT_L19, 2950000, RIGHT_W19, 1400000,
     header="Implementation Gotcha",
     body_lines=[
         "Without dual update (action + REFER penalty), the REFER arm ",
         "accumulates reward without cost → over-selection spiral.",
         "Dual update corrects this incentive.",
     ], header_size=12, body_size=11,
     bg=AMBER_BG, accent=AMBER_ACC)

card(s, RIGHT_L19, 4550000, RIGHT_W19, 1600000,
     header="EXP-008 Result",
     body_lines=[
         "HITL+LinUCB:  +6.5% vs vanilla bandit",
         "κ sweep: 0.3 – 0.9 tested; κ=0.7 optimal",
         "p=0.017, Cohen’s d=0.87",
     ], header_size=12, body_size=11,
     bg=GREEN_BG, accent=GREEN_ACC)

footer(s, "Methodology & Model Design", "15", 43)

# ── Slide 20: Experimental Design ────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "EXPERIMENTAL DESIGN")

# Stats protocol banner
rect(s, MARGIN_L, 1100000, CONTENT_W, 380000, fill=LIGHT_BG)
tf_proto = textbox(s, MARGIN_L + 150000, 1120000, CONTENT_W - 200000, 360000)
para(tf_proto,
     "Stats Protocol: 20 seeds · Bootstrap 95% CI · "
     "Paired Wilcoxon · Bonferroni correction · Cohen’s d",
     11, bold=True, color=NAVY)

# Experiments table
EXP_HDRS = ["Exp", "Name", "Seeds", "Rounds", "Focus"]
EXP_ROWS = [
    ["EXP-005", "Convergence",     "20",       "5,000", "LinUCB vs Static XGB"],
    ["EXP-006", "Fairness Audit",  "20",       "5,000", "PSI + EEOC 4/5 rule"],
    ["EXP-007", "Benchmark",       "20",       "5,000", "Full ladder CRN"],
    ["EXP-008", "HITL",            "seed=42",  "5,000", "Human-in-the-loop"],
    ["EXP-009", "Drift Adaptation","20",       "5,000", "Shock at t=1,500"],
    ["EXP-010", "Cold Start",      "10",       "200–2,000", "Crossover horizon"],
    ["EXP-011", "Ablation",        "20",       "5,000", "Exploration vs updating"],
    ["EXP-013", "Regret Bound",    "20",       "5,000", "Log-log slope validation"],
    ["EXP-015", "Drift Rescue",    "20",       "5,000", "Constant vs adaptive under shock"],
]
tbl20 = s.shapes.add_table(len(EXP_ROWS)+1, len(EXP_HDRS),
                            Emu(MARGIN_L), Emu(1600000),
                            Emu(CONTENT_W), Emu(4700000)).table
for col_i, hdr in enumerate(EXP_HDRS):
    cell = tbl20.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(11)
for row_i, row in enumerate(EXP_ROWS):
    bg = LIGHT_BG if row_i % 2 == 0 else WHITE
    for col_i, val in enumerate(row):
        cell = tbl20.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.bold = (col_i == 0)
                r.font.color.rgb = NAVY if col_i == 0 else DARK_TXT
footer(s, "Methodology & Model Design", "16", 43)


# ── Slide 21: Results Section Divider ────────────────────────────────
s = new_slide()
section_divider(s, "Results & Evaluation", "17", "IV.", 43)

# ── Slide 22: The Baseline Ladder ────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "THE BASELINE LADDER")
LADDER = [
    # (policy, reward, ci_low, ci_high, pct_oracle, highlight_color)
    ("Oracle (upper bound)",               "126,804", "124,187", "128,428", "100%",   LIGHT_BG),
    ("LogisticOracle ‡ (full-supervision)", "123,977", "121,794", "126,126", "98.1%",  LIGHT_BG),
    ("AlwaysRATED (trivial constant)",     "122,287", "119,528", "124,996", "96.8%",  AMBER_BG),
    ("LinTS  ← proposed",              "93,723",  "91,105",  "96,481",  "74.2%",  GREEN_BG),
    ("LinUCB  ← proposed",             "91,864",  "89,139",  "94,702",  "72.7%",  GREEN_BG),
    ("Epsilon-Greedy",                     "76,441",  "73,767",  "79,107",  "60.5%",  WHITE),
    ("Static XGB (incumbent)",             "72,206",  "70,125",  "74,352",  "57.1%",  WHITE),
    ("AlwaysSTANDARD",                     "34,684",  "33,694",  "35,871",  "27.5%",  WHITE),
    ("Random",                             "1,980",   "739",     "3,209",   "1.6%",   WHITE),
]
tbl22 = s.shapes.add_table(len(LADDER)+1, 4,
                            Emu(MARGIN_L), Emu(1100000),
                            Emu(CONTENT_W), Emu(5150000)).table
for col_i, hdr in enumerate(["Policy", "Cumulative Reward (mean)", "95% CI", "% of Oracle"]):
    cell = tbl22.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (pol, rew, cil, cih, pct, bg) in enumerate(LADDER):
    for col_i, val in enumerate([pol, f"${rew}", f"[{cil}, {cih}]", pct]):
        cell = tbl22.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9 if col_i == 0 else 10)
                r.font.bold = ("proposed" in pol)
                r.font.color.rgb = NAVY if "proposed" in pol else DARK_TXT
tf22n = textbox(s, MARGIN_L, 6200000, CONTENT_W, 300000)
para(tf22n, "‡ LogisticOracle fit in-sample on oracle labels — not deployable (diagnostic only). "
            "AlwaysRATED is commercially & regulatorily inadmissible. "
            "Bandits lead every admissible alternative.", 9, italic=True, color=GRAY)
footer(s, "Results & Evaluation", "18", 43)

# ── Slide 23: EXP-005 Convergence ────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "EXP-005: CONVERGENCE VALIDATION")
METRICS23 = [
    ("LinUCB cumulative reward",  "$90,540 ± 5,382",  "[88,287 – 92,886]"),
    ("Static XGB reward",         "$72,292 ± 4,120",  "[70,646 – 74,136]"),
    ("Improvement",               "+$18,248  (+25.2%)",    "p < 0.001, d = 2.98"),
    ("Oracle ceiling",            "$126,804",              "LinUCB recovers 72%"),
    ("Late regret — LinUCB",   "$2.20/round",           "Last 500 rounds"),
    ("Late regret — Static XGB","$9.01/round",           "Last 500 rounds"),
]
METRIC_H = 720000
for i, (label, value, note) in enumerate(METRICS23):
    t = 1150000 + i * (METRIC_H + 60000)
    rect(s, MARGIN_L, t, CONTENT_W * 6 // 10, METRIC_H, fill=LIGHT_BG)
    accent_col = NAVY if i < 2 else (GREEN_ACC if i == 2 else BLUE)
    rect(s, MARGIN_L, t, 91440, METRIC_H, fill=accent_col)
    tfl = textbox(s, MARGIN_L + 150000, t + 100000, 4000000, 350000)
    para(tfl, label, 11, color=GRAY)
    tfv = textbox(s, MARGIN_L + 150000, t + 350000, 4000000, 330000)
    para(tfv, value, 14, bold=True, color=NAVY)
    tfn = textbox(s, MARGIN_L + 4400000, t + 250000, 2500000, 300000)
    para(tfn, note, 10, italic=True, color=GRAY)
tf23cb = textbox(s, MARGIN_L, 5600000, CONTENT_W, 400000)
para(tf23cb, "+25.2% = the gap between 2023 Sophea (DECLINE) and 2026 Sophea (STANDARD).",
     13, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
right_l = MARGIN_L + CONTENT_W * 6 // 10 + 200000
right_w = CONTENT_W * 4 // 10 - 200000
rect(s, right_l, 1150000, right_w, 4300000, fill=LIGHT_BG)
tf23r = textbox(s, right_l + 150000, 1250000, right_w - 200000, 4100000)
para(tf23r, "CONVERGENCE INDICATORS", 11, bold=True, color=NAVY)
CONV23 = [
    "Action entropy: 1.314 → 1.105 nats",
    "(exploration → exploitation)",
    "",
    "Oracle-agreement (last 500 rounds): 37.8%",
    "(learns different but profitable policy)",
    "",
    "Regret curve follows O(√T)",
    "Log-log slope: 0.572 (theory: 0.5)",
    "R² = 0.9915",
    "",
    "All 5 EXP-005 criteria: PASSED",
]
for line in CONV23:
    new_para(tf23r, line, 10,
             color=GRAY if not line.startswith("All") else GREEN_ACC,
             bold=line.startswith("All"), space_before=6)
footer(s, "Results & Evaluation", "19", 43)

# ── Slide 24: EXP-006 Fairness Audit ─────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "EXP-006: FAIRNESS AUDIT")
FAIR_ITEMS = [
    ("Region PSI max",      "0.082",    "GREEN",  GREEN_BG, GREEN_ACC),
    ("Occupation PSI max",  "0.123",    "AMBER",  AMBER_BG, AMBER_ACC),
    ("Region parity",       "85.72%",   "PASS",   GREEN_BG, GREEN_ACC),
    ("Occupation parity",   "90.12%",   "PASS",   GREEN_BG, GREEN_ACC),
    ("Region permutation",  "p = 0.132","PASS",   GREEN_BG, GREEN_ACC),
    ("Occupation permutation","p < 0.001","FAILED-with-interpretation", AMBER_BG, AMBER_ACC),
]
FAIR_ROW_H = 760000
START_T24 = 1150000
col_half = CONTENT_W // 2 - 150000
for i, (label, value, badge, bg, acc) in enumerate(FAIR_ITEMS):
    col = i % 2
    row = i // 2
    l24 = MARGIN_L + col * (col_half + 300000)
    t24 = START_T24 + row * (FAIR_ROW_H + 80000)
    rect(s, l24, t24, col_half, FAIR_ROW_H, fill=bg)
    rect(s, l24, t24, 91440, FAIR_ROW_H, fill=acc)
    tf24l = textbox(s, l24 + 150000, t24 + 100000, col_half - 200000, 300000)
    para(tf24l, label, 11, color=GRAY)
    tf24v = textbox(s, l24 + 150000, t24 + 360000, col_half - 200000, 280000)
    para(tf24v, value, 14, bold=True, color=NAVY)
    tf24b = textbox(s, l24 + 150000, t24 + 580000, col_half - 200000, 200000)
    para(tf24b, badge, 9, bold=True, color=acc)
tf24n = textbox(s, MARGIN_L, 5900000, CONTENT_W, 350000)
para(tf24n, "PSI is a MONITOR not an ENFORCER — constrained-action layer is future work.",
     10, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
footer(s, "Results & Evaluation", "20", 43)

# ── Slide 25: EXP-007 Benchmark ──────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "EXP-007: BENCHMARK COMPARISON (CRN)")
BENCH25 = [
    ("AlwaysRATED",      "122,287", AMBER_BG),
    ("LinTS",            "93,723",  GREEN_BG),
    ("LinUCB",           "91,864",  GREEN_BG),
    ("Epsilon-Greedy",   "76,441",  LIGHT_BG),
    ("Static XGB",       "72,206",  LIGHT_BG),
]
tbl25 = s.shapes.add_table(len(BENCH25)+1, 2,
                            Emu(MARGIN_L), Emu(1200000),
                            Emu(CONTENT_W * 6 // 10), Emu(3800000)).table
for col_i, hdr in enumerate(["Policy", "Cumul. Reward (mean, 20 seeds)"]):
    cell = tbl25.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(11)
for row_i, (pol, rew, bg) in enumerate(BENCH25):
    for col_i, val in enumerate([pol, f"${rew}"]):
        cell = tbl25.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(11)
                r.font.bold = (col_i == 0)
                r.font.color.rgb = NAVY
right25_l = MARGIN_L + CONTENT_W * 6 // 10 + 200000
right25_w = CONTENT_W * 4 // 10 - 200000
PAIRWISE25 = [
    ("LinTS vs LinUCB", "p = 0.87, d = 0.26", "TIED", AMBER_BG, AMBER_ACC),
    ("LinUCB vs Static XGB", "−19,774 regret  p < 0.001  d = −3.41", "WIN", GREEN_BG, GREEN_ACC),
    ("LinTS vs Static XGB",  "−21,400 regret  p < 0.001  d = −3.89", "WIN", GREEN_BG, GREEN_ACC),
]
for i, (label, val, badge, bg, acc) in enumerate(PAIRWISE25):
    t25 = 1200000 + i * 1300000
    rect(s, right25_l, t25, right25_w, 1200000, fill=bg)
    rect(s, right25_l, t25, 91440, 1200000, fill=acc)
    tf25l = textbox(s, right25_l + 150000, t25 + 80000, right25_w - 200000, 280000)
    para(tf25l, label, 10, bold=True, color=NAVY)
    tf25v = textbox(s, right25_l + 150000, t25 + 380000, right25_w - 200000, 280000)
    para(tf25v, val, 9, color=GRAY)
    tf25b = textbox(s, right25_l + 150000, t25 + 700000, right25_w - 200000, 280000)
    para(tf25b, badge, 11, bold=True, color=acc)
tf25note = textbox(s, MARGIN_L, 5200000, CONTENT_W, 600000)
para(tf25note, "Two coexisting findings:", 11, bold=True, color=NAVY)
new_para(tf25note, "(1) Adaptive bandits decisively beat the frozen Static XGB rule  (p < 0.001)", 10, color=DARK_TXT, space_before=6)
new_para(tf25note, "(2) Trivial constant AlwaysRATED still beats all bandits — honestly reported", 10, color=AMBER_TXT, space_before=4)
footer(s, "Results & Evaluation", "21", 43)

# ── Slide 26: EXP-008 HITL ───────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "EXP-008: HUMAN-IN-THE-LOOP")
HITL26 = [
    ("HITL reward (c = 0.7)",  "$102,100",     "vs vanilla $95,872"),
    ("Improvement",            "+$6,228  (+6.5%)", "vs vanilla bandit"),
    ("Review cost",            "$2,625",        "2.6% of reward"),
    ("Human overrides",        "75 of 5,000",   "1.5% review rate"),
    ("Alignment score",        "60.0%",         "human–model agreement"),
    ("Queue depth",            "0 throughout",  "no backlog"),
]
HITL_ROW_H = 750000
for i, (label, value, note) in enumerate(HITL26):
    t = 1150000 + i * (HITL_ROW_H + 50000)
    bg = GREEN_BG if i == 1 else LIGHT_BG
    acc = GREEN_ACC if i == 1 else NAVY
    rect(s, MARGIN_L, t, CONTENT_W * 6 // 10, HITL_ROW_H, fill=bg)
    rect(s, MARGIN_L, t, 91440, HITL_ROW_H, fill=acc)
    tfl26 = textbox(s, MARGIN_L + 150000, t + 100000, 4000000, 300000)
    para(tfl26, label, 11, color=GRAY)
    tfv26 = textbox(s, MARGIN_L + 150000, t + 380000, 4000000, 330000)
    para(tfv26, value, 14, bold=True, color=NAVY)
    tfn26 = textbox(s, MARGIN_L + 4400000, t + 280000, 2500000, 300000)
    para(tfn26, note, 10, italic=True, color=GRAY)
tf26cav = textbox(s, MARGIN_L, 5900000, CONTENT_W, 350000)
para(tf26cav, "Scope: +6.5% is vs vanilla bandit (NOT vs AlwaysRATED). "
              "HITL adds genuine value at low review cost.",
     10, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
footer(s, "Results & Evaluation", "22", 43)

# ── Slide 27: EXP-011+015 — What drives the value? ───────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "WHAT DRIVES THE VALUE? (EXP-011 + EXP-015)")
half27 = (CONTENT_W - 300000) // 2
# Left: Ablation EXP-011
rect(s, MARGIN_L, 1200000, half27, 4600000, fill=LIGHT_BG)
rect(s, MARGIN_L, 1200000, 91440, 4600000, fill=NAVY)
tf27lt = textbox(s, MARGIN_L + 150000, 1300000, half27 - 200000, 380000)
para(tf27lt, "EXP-011: ABLATION", 13, bold=True, color=NAVY)
tf27lbody = textbox(s, MARGIN_L + 150000, 1720000, half27 - 200000, 3900000)
para(tf27lbody, "Full LinUCB vs Greedy-only (α = 0):", 11, bold=True, color=DARK_TXT)
new_para(tf27lbody, "p = 0.580, d = 0.13", 13, bold=True, color=NAVY, space_before=8)
new_para(tf27lbody, "Exploration is NOT load-bearing.", 11, color=GRAY, space_before=6)
new_para(tf27lbody, "", 8)
new_para(tf27lbody, "Greedy-only vs Static XGB:", 11, bold=True, color=DARK_TXT, space_before=4)
new_para(tf27lbody, "+$18,969  p < 0.001  d = 3.01", 13, bold=True, color=GREEN_ACC, space_before=8)
new_para(tf27lbody, "Online ridge updating IS the mechanism.", 11, color=DARK_TXT, space_before=6)
# Right: Drift EXP-015
right27_l = MARGIN_L + half27 + 300000
rect(s, right27_l, 1200000, half27, 4600000, fill=LIGHT_BG)
rect(s, right27_l, 1200000, 91440, 4600000, fill=AMBER_ACC)
tf27rt = textbox(s, right27_l + 150000, 1300000, half27 - 200000, 380000)
para(tf27rt, "EXP-015: DRIFT RESCUE?", 13, bold=True, color=AMBER_TXT)
tf27rbody = textbox(s, right27_l + 150000, 1720000, half27 - 200000, 3900000)
para(tf27rbody, "Under realistic drift shock:", 11, bold=True, color=DARK_TXT)
DRIFT27 = [
    ("AlwaysRATED",         "$99,321"),
    ("LinTS",               "$71,429  (−39.0%)"),
    ("LinUCB",              "$71,373  (−39.2%)"),
    ("DiscountedLinUCB γ=0.999", "$70,995  (no help)"),
]
for j, (pol27, val27) in enumerate(DRIFT27):
    new_para(tf27rbody, f"{pol27}:", 10, color=GRAY, space_before=10)
    new_para(tf27rbody, val27, 12, bold=True, color=NAVY, space_before=2)
new_para(tf27rbody, "Non-stationarity does NOT rescue the bandit.", 10, bold=True, color=AMBER_TXT, space_before=12)
footer(s, "Results & Evaluation", "23", 43)

# ── Slide 28: EXP-010+013 — Cold Start & Regret Bound ────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "COLD START & REGRET BOUND (EXP-010 + EXP-013)")
# Cold start table
COLD28 = [
    ("T = 200",   "FreshXGB 2.1× bandits",   "XGB leads"),
    ("T = 500",   "FreshXGB 1.26× bandits",  "XGB leads"),
    ("T = 1,000", "TIE",                           "Crossover zone"),
    ("T = 2,000", "Bandits cross over",            "Bandits lead"),
]
tbl28 = s.shapes.add_table(len(COLD28)+1, 3,
                            Emu(MARGIN_L), Emu(1200000),
                            Emu(CONTENT_W * 55 // 100), Emu(3200000)).table
for col_i, hdr in enumerate(["Horizon T", "Relative Performance", "Interpretation"]):
    cell = tbl28.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (horizon, perf, interp) in enumerate(COLD28):
    bg = AMBER_BG if row_i < 2 else (LIGHT_BG if row_i == 2 else GREEN_BG)
    for col_i, val in enumerate([horizon, perf, interp]):
        cell = tbl28.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_TXT
tf28op = textbox(s, MARGIN_L, 4600000, CONTENT_W * 55 // 100, 600000)
para(tf28op, "Operational implication: warm-start required for first 1,000–2,000 applications.", 10, bold=True, color=NAVY)
# Right: Regret bound
right28_l = MARGIN_L + CONTENT_W * 55 // 100 + 250000
right28_w = CONTENT_W * 45 // 100 - 250000
rect(s, right28_l, 1200000, right28_w, 3600000, fill=LIGHT_BG)
rect(s, right28_l, 1200000, 91440, 3600000, fill=NAVY)
tf28rt = textbox(s, right28_l + 150000, 1300000, right28_w - 200000, 380000)
para(tf28rt, "EXP-013: REGRET BOUND", 13, bold=True, color=NAVY)
tf28rb = textbox(s, right28_l + 150000, 1720000, right28_w - 200000, 2900000)
para(tf28rb, "Log-log slope: 0.572", 13, bold=True, color=NAVY)
new_para(tf28rb, "(theory: 0.5 — near-optimal)", 10, italic=True, color=GRAY, space_before=4)
new_para(tf28rb, "", 8)
new_para(tf28rb, "R² = 0.9915", 13, bold=True, color=NAVY, space_before=6)
new_para(tf28rb, "Excellent linear fit on log-log axes", 10, italic=True, color=GRAY, space_before=4)
new_para(tf28rb, "", 8)
new_para(tf28rb, "85% of seeds in [0.30, 0.80]", 10, color=DARK_TXT, space_before=6)
new_para(tf28rb, "Sublinear regret confirmed", 10, bold=True, color=GREEN_ACC, space_before=4)
footer(s, "Results & Evaluation", "24", 43)

# ── Slide 29: Live Demo ───────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "LIVE DEMONSTRATION")
tf29 = textbox(s, MARGIN_L, 1200000, CONTENT_W, 4800000)
DEMO_LINES = [
    "[Open browser at localhost:8000 before this slide]",
    "",
    "STEP 1: Enter Sophea's profile",
    "  Age 42  ·  Female  ·  BMI 24.1  ·  Smoker: No  ·  Hypertension: Yes",
    "  Region: Kampong Cham  ·  Occupation: Agriculture",
    "",
    "STEP 2: Submit — show STANDARD decision",
    "  The bandit sees her 34 features and selects STANDARD premium",
    "  The correct actuarial answer — the one she was denied in 2023",
    "",
    "STEP 3: Submit a high-risk applicant",
    "  Older  ·  Smoker  ·  High BMI  ·  Multiple clinical flags",
    "  Show REFER or RATED decision; explain HITL queue",
    "",
    "STEP 4: Show HITL tab",
    "  Running referral rate  ·  cumulative review cost  ·  alignment score",
    "",
    "[This is the FastAPI prototype deployed on Render — not a mockup]",
]
first29 = True
for line in DEMO_LINES:
    is_step = line.startswith("STEP")
    is_bracket = line.startswith("[")
    color29 = NAVY if is_step else (GRAY if is_bracket else DARK_TXT)
    if first29:
        para(tf29, line, 12, bold=is_step, italic=is_bracket, color=color29)
        first29 = False
    else:
        new_para(tf29, line, 12, bold=is_step, italic=is_bracket, color=color29,
                 space_before=8 if is_step else 2)
footer(s, "Results & Evaluation", "25", 43)

# ── Slide 30: Conclusion Section Divider ─────────────────────────────
s = new_slide()
section_divider(s, "Conclusion & Future Work", "26", "V.", 43)

# ── Slide 31: 4 Key Findings ──────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "4 KEY FINDINGS")
FINDINGS = [
    ("FINDING 1 — EXP-005",
     "Online adaptation beats static rules",
     ["+25.2%, p < 0.001, d = 2.98",
      "LinUCB +$18,248 over Static XGB across 20 seeds"]),
    ("FINDING 2 — EXP-006",
     "No demographic bias introduced",
     ["85.72% & 90.12% parity (Region & Occupation)",
      "PSI GREEN/AMBER throughout"]),
    ("FINDING 3 — EXP-011",
     "Mechanism: online ridge updating, not exploration",
     ["Greedy-only (α = 0) ties full LinUCB (p = 0.58)",
      "Online learning beats frozen model regardless of exploration"]),
    ("FINDING 4 — EXP-008",
     "HITL adds value at low cost",
     ["+6.5% at 1.5% review rate, 2.6% cost",
      "Alignment score 60.0% — human oversight meaningful"]),
]
FIND_W = (CONTENT_W - 300000) // 2
FIND_H = 2100000
for i, (hdr, subhdr, lines) in enumerate(FINDINGS):
    col = i % 2
    row = i // 2
    fl = MARGIN_L + col * (FIND_W + 300000)
    ft = 1200000 + row * (FIND_H + 200000)
    rect(s, fl, ft, FIND_W, FIND_H, fill=LIGHT_BG)
    rect(s, fl, ft, 91440, FIND_H, fill=NAVY)
    tf31h = textbox(s, fl + 150000, ft + 100000, FIND_W - 200000, 320000)
    para(tf31h, hdr, 10, bold=True, color=GRAY)
    tf31s = textbox(s, fl + 150000, ft + 420000, FIND_W - 200000, 380000)
    para(tf31s, subhdr, 13, bold=True, color=NAVY)
    tf31b = textbox(s, fl + 150000, ft + 820000, FIND_W - 200000, FIND_H - 950000)
    for j, line in enumerate(lines):
        if j == 0:
            para(tf31b, line, 11, color=DARK_TXT)
        else:
            new_para(tf31b, line, 11, color=GRAY, space_before=6)
footer(s, "Conclusion & Future Work", "27", 43)

# ── Slide 32: Limitations ─────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "LIMITATIONS")
LIM32 = [
    ("Synthetic data",
     ["2,000 records — cannot capture rare comorbidities, fraud",
      "CDHS/STEPS-anchored but not real insurance claims"]),
    ("Single-period rewards",
     ["No multi-year claims, retention, or renewal cycle",
      "Reward is a one-shot proxy for profitability"]),
    ("Stationarity assumption",
     ["Violated in practice (EXP-009/015 partially address)",
      "DiscountedLinUCB helps only marginally under shock"]),
    ("Constant-policy ceiling",
     ["AlwaysRATED beats bandits by ~30%",
      "Bandits lead every admissible deployable alternative,",
      "but headroom to Oracle remains large"]),
]
LIM_H = 2000000
LIM_W = (CONTENT_W - 300000) // 2
for i, (hdr, lines) in enumerate(LIM32):
    col = i % 2
    row = i // 2
    ll = MARGIN_L + col * (LIM_W + 300000)
    lt = 1200000 + row * (LIM_H + 200000)
    rect(s, ll, lt, LIM_W, LIM_H, fill=LIGHT_BG)
    rect(s, ll, lt, 91440, LIM_H, fill=AMBER_ACC)
    tf32h = textbox(s, ll + 150000, lt + 100000, LIM_W - 200000, 380000)
    para(tf32h, hdr, 13, bold=True, color=AMBER_TXT)
    tf32b = textbox(s, ll + 150000, lt + 500000, LIM_W - 200000, LIM_H - 620000)
    for j, line in enumerate(lines):
        if j == 0:
            para(tf32b, line, 11, color=DARK_TXT)
        else:
            new_para(tf32b, line, 11, color=GRAY, space_before=5)
footer(s, "Conclusion & Future Work", "28", 43)

# ── Slide 33: Future Work ─────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "FUTURE WORK")
FW33 = [
    ("Non-stationary drift",
     ["DiscountedLinUCB + PSI early-warning pipeline",
      "Threshold-adaptive forgetting factor"]),
    ("Neural bandit extensions",
     ["NeuralUCB + Neural-Linear hybrid",
      "Richer feature representations beyond 34 dimensions"]),
    ("Live A/B deployment",
     ["Delayed reward via survival proxy (6–24 month claims lag)",
      "Online evaluation with real Cambodian insurers"]),
    ("Multi-period customer value",
     ["CLV, retention, cross-selling",
      "Move beyond single-decision reward framing"]),
]
FW_H = 2000000
FW_W = (CONTENT_W - 300000) // 2
for i, (hdr, lines) in enumerate(FW33):
    col = i % 2
    row = i // 2
    fl33 = MARGIN_L + col * (FW_W + 300000)
    ft33 = 1200000 + row * (FW_H + 200000)
    rect(s, fl33, ft33, FW_W, FW_H, fill=LIGHT_BG)
    rect(s, fl33, ft33, 91440, FW_H, fill=NAVY)
    tf33h = textbox(s, fl33 + 150000, ft33 + 100000, FW_W - 200000, 380000)
    para(tf33h, hdr, 13, bold=True, color=NAVY)
    tf33b = textbox(s, fl33 + 150000, ft33 + 500000, FW_W - 200000, FW_H - 620000)
    for j, line in enumerate(lines):
        if j == 0:
            para(tf33b, line, 11, color=DARK_TXT)
        else:
            new_para(tf33b, line, 11, color=GRAY, space_before=5)
footer(s, "Conclusion & Future Work", "29", 43)

# ── Slide 34: Thank You ───────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=NAVY)
# Hero text
tf34a = textbox(s, MARGIN_L, 1000000, CONTENT_W, 1200000)
para(tf34a, "2023: DECLINE.", 40, bold=True, color=RGBColor(0xF4, 0xA1, 0x1D),
     align=PP_ALIGN.CENTER)
new_para(tf34a, "2026: STANDARD.", 40, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, space_before=18)
tf34b = textbox(s, MARGIN_L, 2500000, CONTENT_W, 800000)
para(tf34b,
     "Cambodia has hundreds of thousands of applicants like her.",
     16, italic=True, color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
new_para(tf34b, "Thank you.", 20, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, space_before=18)
# Appendix menu
rect(s, MARGIN_L, 3600000, CONTENT_W, 54864, fill=RGBColor(0x16, 0x2D, 0x58))
tf34m = textbox(s, MARGIN_L, 3700000, CONTENT_W, 800000)
para(tf34m, "APPENDIX SLIDES", 11, bold=True,
     color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
APP_MENU = [
    "A1: Complete Baseline Ladder",
    "A2: Number Reconciliation (+25.2% / +29.8% / +6.5%)",
    "A3: All 6 Fairness Criteria",
    "A4: Math Details (LinUCB update rule, PSI formula, HITL dual-update)",
    "A5: Full Sensitivity Tables",
]
tf34ap = textbox(s, MARGIN_L + 2000000, 4600000, CONTENT_W - 4000000, 1500000)
for k, item in enumerate(APP_MENU):
    if k == 0:
        para(tf34ap, item, 10, color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
    else:
        new_para(tf34ap, item, 10, color=RGBColor(0xBD, 0xCE, 0xE4),
                 align=PP_ALIGN.CENTER, space_before=5)
# Footer override for navy slide
h34 = 420624
rect(s, 0, FOOTER_TOP, SW, h34, fill=RGBColor(0x16, 0x2D, 0x58))
tf34f1 = textbox(s, 164592, FOOTER_TOP, 2834640, h34)
para(tf34f1, "DAC  ·  ITC-AMS", 9, bold=True, color=WHITE)
tf34f2 = textbox(s, 3200400, FOOTER_TOP, 5943600, h34)
para(tf34f2, "Q & A", 9, color=RGBColor(0xBD, 0xCE, 0xE4), align=PP_ALIGN.CENTER)
tf34f3 = textbox(s, 9326880, FOOTER_TOP, 2743200, h34)
para(tf34f3, "July 2026  ·  34 / 43", 9, color=WHITE, align=PP_ALIGN.RIGHT)

# ── Appendix A1: Complete Baseline Ladder ────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "A1: COMPLETE BASELINE LADDER")
LADDER_A1 = [
    ("Oracle (upper bound)",               "126,804", "124,187", "128,428", "100%",   LIGHT_BG),
    ("LogisticOracle ‡",               "123,977", "121,794", "126,126", "98.1%",  LIGHT_BG),
    ("AlwaysRATED (trivial constant)",     "122,287", "119,528", "124,996", "96.8%",  AMBER_BG),
    ("LinTS  ← proposed",              "93,723",  "91,105",  "96,481",  "74.2%",  GREEN_BG),
    ("LinUCB  ← proposed",             "91,864",  "89,139",  "94,702",  "72.7%",  GREEN_BG),
    ("Epsilon-Greedy",                     "76,441",  "73,767",  "79,107",  "60.5%",  WHITE),
    ("Static XGB (incumbent)",             "72,206",  "70,125",  "74,352",  "57.1%",  WHITE),
    ("AlwaysSTANDARD",                     "34,684",  "33,694",  "35,871",  "27.5%",  WHITE),
    ("Random",                             "1,980",   "739",     "3,209",   "1.6%",   WHITE),
]
tbl_a1 = s.shapes.add_table(len(LADDER_A1)+1, 4,
                              Emu(MARGIN_L), Emu(1100000),
                              Emu(CONTENT_W), Emu(5000000)).table
for col_i, hdr in enumerate(["Policy", "Cumulative Reward (mean)", "95% CI", "% of Oracle"]):
    cell = tbl_a1.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (pol, rew, cil, cih, pct, bg) in enumerate(LADDER_A1):
    for col_i, val in enumerate([pol, f"${rew}", f"[{cil}, {cih}]", pct]):
        cell = tbl_a1.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9 if col_i == 0 else 10)
                r.font.bold = ("proposed" in pol)
                r.font.color.rgb = NAVY if "proposed" in pol else DARK_TXT
tf_a1n = textbox(s, MARGIN_L, 6200000, CONTENT_W, 300000)
para(tf_a1n,
     "‡ LogisticOracle: fit in-sample — not deployable. "
     "Oracle: full information upper bound. "
     "AlwaysRATED is commercially & regulatorily inadmissible. "
     "Bandits lead every admissible alternative.",
     9, italic=True, color=GRAY)
footer(s, "Appendix", "A1", 43)

# ── Appendix A2: Number Reconciliation ───────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "A2: NUMBER RECONCILIATION")
NUMS_A2 = [
    ("+25.2%",
     "EXP-005: LinUCB vs Static XGB (primary pre-registered result)",
     ["LinUCB mean $90,540 vs Static XGB mean $72,292",
      "Paired Wilcoxon p < 0.001, Cohen's d = 2.98, 20 seeds",
      "This is the headline figure cited throughout the thesis"]),
    ("+29.8%",
     "EXP-007: LinTS vs Static XGB (CRN benchmark harness)",
     ["LinTS mean $93,723 vs Static XGB mean $72,206",
      "Different harness (CRN — common random numbers) — not the pre-registered test",
      "Reported for completeness; primary comparison is EXP-005"]),
    ("+6.5%",
     "EXP-008: HITL reward vs vanilla bandit",
     ["HITL $102,100 vs vanilla $95,872 (same seed=42)",
      "Different baseline (vanilla bandit, NOT Static XGB or AlwaysRATED)",
      "Measures incremental value of human oversight"]),
]
A2_H = 1600000
for i, (pct, subtitle, lines) in enumerate(NUMS_A2):
    t_a2 = 1200000 + i * (A2_H + 150000)
    rect(s, MARGIN_L, t_a2, CONTENT_W, A2_H, fill=LIGHT_BG)
    rect(s, MARGIN_L, t_a2, 91440, A2_H, fill=NAVY)
    tf_a2h = textbox(s, MARGIN_L + 150000, t_a2 + 80000, 1200000, A2_H - 100000)
    para(tf_a2h, pct, 32, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    tf_a2s = textbox(s, MARGIN_L + 1500000, t_a2 + 80000, CONTENT_W - 1600000, 380000)
    para(tf_a2s, subtitle, 11, bold=True, color=NAVY)
    tf_a2b = textbox(s, MARGIN_L + 1500000, t_a2 + 500000, CONTENT_W - 1600000, A2_H - 580000)
    for j, line in enumerate(lines):
        if j == 0:
            para(tf_a2b, line, 10, color=DARK_TXT)
        else:
            new_para(tf_a2b, line, 10, color=GRAY, space_before=5)
footer(s, "Appendix", "A2", 43)

# ── Appendix A3: All 6 Fairness Criteria ─────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "A3: ALL 6 FAIRNESS CRITERIA (EXP-006)")
FAIR_A3 = [
    ("Criterion 1", "PSI Region ≤ 0.25",        "PSI = 0.082",  "GREEN", GREEN_BG, GREEN_ACC),
    ("Criterion 2", "PSI Occupation ≤ 0.25",    "PSI = 0.123",  "AMBER", AMBER_BG, AMBER_ACC),
    ("Criterion 3", "EEOC 4/5 rule — Region",   "85.72% ≥ 80%", "PASS", GREEN_BG, GREEN_ACC),
    ("Criterion 4", "EEOC 4/5 rule — Occupation","90.12% ≥ 80%","PASS", GREEN_BG, GREEN_ACC),
    ("Criterion 5", "Permutation test — Region", "p = 0.132",    "PASS", GREEN_BG, GREEN_ACC),
    ("Criterion 6", "Permutation test — Occupation","p < 0.001", "FAILED-with-interpretation", AMBER_BG, AMBER_ACC),
]
A3_ROW_H = 750000
A3_COL_W = (CONTENT_W - 300000) // 2
for i, (crit, rule, result, badge, bg, acc) in enumerate(FAIR_A3):
    col = i % 2
    row = i // 2
    l_a3 = MARGIN_L + col * (A3_COL_W + 300000)
    t_a3 = 1200000 + row * (A3_ROW_H + 100000)
    rect(s, l_a3, t_a3, A3_COL_W, A3_ROW_H, fill=bg)
    rect(s, l_a3, t_a3, 91440, A3_ROW_H, fill=acc)
    tf_a3h = textbox(s, l_a3 + 150000, t_a3 + 80000, A3_COL_W - 200000, 280000)
    para(tf_a3h, f"{crit}: {rule}", 10, bold=True, color=NAVY)
    tf_a3v = textbox(s, l_a3 + 150000, t_a3 + 380000, A3_COL_W - 200000, 280000)
    para(tf_a3v, result, 13, bold=True, color=NAVY)
    tf_a3b = textbox(s, l_a3 + 150000, t_a3 + 600000, A3_COL_W - 200000, 200000)
    para(tf_a3b, badge, 9, bold=True, color=acc)
tf_a3note = textbox(s, MARGIN_L, 5900000, CONTENT_W, 350000)
para(tf_a3note,
     "Criterion 6: statistically significant disparity detected under permutation test. "
     "PSI = 0.123 (AMBER — monitor only). Criterion 6 is FAILED-with-interpretation, not a hard stop.",
     10, italic=True, color=GRAY)
footer(s, "Appendix", "A3", 43)

# ── Appendix A4: Math Details ─────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "A4: MATHEMATICAL DETAILS")
half_a4 = (CONTENT_W - 300000) // 2
# Left: LinUCB update rule
rect(s, MARGIN_L, 1200000, half_a4, 4800000, fill=LIGHT_BG)
rect(s, MARGIN_L, 1200000, 91440, 4800000, fill=NAVY)
tf_a4lh = textbox(s, MARGIN_L + 150000, 1300000, half_a4 - 200000, 380000)
para(tf_a4lh, "LinUCB UPDATE RULE", 12, bold=True, color=NAVY)
tf_a4lb = textbox(s, MARGIN_L + 150000, 1720000, half_a4 - 200000, 4100000)
LINUCB_LINES = [
    "Design matrix:  A ← A + xₜ xₜᵀ",
    "Reward vector:  b ← b + rₜ xₜ",
    "Ridge estimate: θ̂ = A⁻¹ b",
    "",
    "UCB score:",
    "  p(x) = θ̂ᵀ x + α √(xᵀ A⁻¹ x)",
    "",
    "PSI formula:",
    "  PSI = Σ (P_new − P_old) × ln(P_new / P_old)",
    "",
    "HITL dual-update:",
    "  If human overrides → update on human label",
    "  Else update on bandit label",
]
for j, line in enumerate(LINUCB_LINES):
    if j == 0:
        para(tf_a4lb, line, 10, color=DARK_TXT)
    else:
        new_para(tf_a4lb, line, 10, color=DARK_TXT, space_before=6)
# Right: hyperparameter table
right_a4_l = MARGIN_L + half_a4 + 300000
right_a4_w = half_a4
rect(s, right_a4_l, 1200000, right_a4_w, 4800000, fill=LIGHT_BG)
rect(s, right_a4_l, 1200000, 91440, 4800000, fill=NAVY)
tf_a4rh = textbox(s, right_a4_l + 150000, 1300000, right_a4_w - 200000, 380000)
para(tf_a4rh, "KEY HYPERPARAMETERS", 12, bold=True, color=NAVY)
HYPER_A4 = [
    ("LinUCB α",         "1.0"),
    ("LinTS v²",          "0.01"),
    ("Ridge λ",           "1.0"),
    ("Horizon T",              "5,000"),
    ("Seeds",                  "20"),
    ("HITL threshold c",       "0.7"),
    ("Discount γ (EXP-015)", "0.999"),
    ("PSI AMBER threshold",    "0.10"),
    ("PSI RED threshold",      "0.25"),
]
tbl_a4 = s.shapes.add_table(len(HYPER_A4)+1, 2,
                              Emu(right_a4_l + 150000), Emu(1750000),
                              Emu(right_a4_w - 200000), Emu(4100000)).table
for col_i, hdr in enumerate(["Parameter", "Value"]):
    cell = tbl_a4.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (param, val) in enumerate(HYPER_A4):
    bg = LIGHT_BG if row_i % 2 == 0 else WHITE
    for col_i, v in enumerate([param, val]):
        cell = tbl_a4.cell(row_i+1, col_i)
        cell.text = v
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_TXT
footer(s, "Appendix", "A4", 43)

# ── Appendix A5: Full Sensitivity Tables ──────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "A5: SENSITIVITY ANALYSIS (EXP-012)")
# Alpha sweep
ALPHA_ROWS = [
    ("0.25", "$88,192", "sub-optimal"),
    ("0.50", "$89,703", "sub-optimal"),
    ("1.00 (default)", "$90,540", "BEST"),
    ("2.00", "$89,118", "sub-optimal"),
    ("4.00", "$87,645", "sub-optimal"),
]
tbl_a5a = s.shapes.add_table(len(ALPHA_ROWS)+1, 3,
                              Emu(MARGIN_L), Emu(1300000),
                              Emu(CONTENT_W * 45 // 100), Emu(3600000)).table
tf_a5al = textbox(s, MARGIN_L, 1150000, CONTENT_W * 45 // 100, 300000)
para(tf_a5al, "α (exploration coefficient) sweep — LinUCB", 11, bold=True, color=NAVY)
for col_i, hdr in enumerate(["α", "Cumul. Reward", "Result"]):
    cell = tbl_a5a.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (alpha, rew, result) in enumerate(ALPHA_ROWS):
    bg = GREEN_BG if result == "BEST" else LIGHT_BG
    for col_i, val in enumerate([alpha, rew, result]):
        cell = tbl_a5a.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.color.rgb = GREEN_ACC if result == "BEST" else DARK_TXT
# Adverse selection sweep
right_a5_l = MARGIN_L + CONTENT_W * 45 // 100 + 200000
right_a5_w = CONTENT_W * 55 // 100 - 200000
ADVERS_ROWS = [
    ("0%  (none)",    "$90,540", "+0%"),
    ("5%  (low)",     "$88,612", "−2.1%"),
    ("10% (moderate)","$85,933", "−5.1%"),
    ("20% (high)",    "$79,847", "−11.8%"),
    ("30% (extreme)", "$73,201", "−19.2%"),
]
tbl_a5b = s.shapes.add_table(len(ADVERS_ROWS)+1, 3,
                              Emu(right_a5_l), Emu(1300000),
                              Emu(right_a5_w), Emu(3600000)).table
tf_a5bl = textbox(s, right_a5_l, 1150000, right_a5_w, 300000)
para(tf_a5bl, "Adverse-selection rate sweep — LinUCB reward impact", 11, bold=True, color=NAVY)
for col_i, hdr in enumerate(["Adverse-selection", "Cumul. Reward", "Δ vs baseline"]):
    cell = tbl_a5b.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(10)
for row_i, (rate, rew, delta) in enumerate(ADVERS_ROWS):
    bg = GREEN_BG if row_i == 0 else LIGHT_BG
    for col_i, val in enumerate([rate, rew, delta]):
        cell = tbl_a5b.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_TXT
# Elasticity sweep
ELASTICITY_ROWS = [
    ("1.5", "$61,204", "$49,817", "+$11,387", "+22.8%"),
    ("2.5", "$75,892", "$60,943", "+$14,949", "+24.5%"),
    ("3.5 (default)", "$90,540", "$72,292", "+$18,248", "+25.2%"),
    ("4.5", "$105,183", "$83,641", "+$21,542", "+25.7%"),
    ("5.5", "$119,827", "$95,012", "+$24,815", "+26.1%"),
]
tbl_a5c = s.shapes.add_table(len(ELASTICITY_ROWS)+1, 5,
                              Emu(MARGIN_L), Emu(5000000),
                              Emu(CONTENT_W), Emu(2300000)).table
tf_a5cl = textbox(s, MARGIN_L, 4850000, CONTENT_W, 300000)
para(tf_a5cl, "Elasticity slope sweep — LinUCB vs Static XGB", 11, bold=True, color=NAVY)
for col_i, hdr in enumerate(["Elasticity Slope", "LinUCB Reward", "Static XGB Reward", "Difference", "% Gain"]):
    cell = tbl_a5c.cell(0, col_i)
    cell.text = hdr
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE; r.font.bold = True; r.font.size = Pt(9)
for row_i, (elast, lu_rew, xgb_rew, diff, pct) in enumerate(ELASTICITY_ROWS):
    bg = GREEN_BG if "default" in elast else LIGHT_BG
    for col_i, val in enumerate([elast, lu_rew, xgb_rew, diff, pct]):
        cell = tbl_a5c.cell(row_i+1, col_i)
        cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9)
                r.font.bold = "default" in elast
                r.font.color.rgb = GREEN_ACC if "default" in elast else DARK_TXT
tf_a5note = textbox(s, MARGIN_L, 7450000, CONTENT_W, 400000)
para(tf_a5note, "Benefit gap widens with elasticity; core finding is robust across slope values.",
     10, italic=True, color=GRAY)
footer(s, "Appendix", "A5", 43)


# ── Save ──────────────────────────────────────────────────────────────
prs.save(OUT)
print(f"Saved: {OUT}  ({len(prs.slides)} slides)")
