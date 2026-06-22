# thesis/health_rl/build_defense_v3.py
"""Build Poly_defense_presentation_v3.pptx from scratch."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.text import PP_ALIGN
from defense_tokens import *
from defense_draw import (rect, textbox, para, new_para, add_run,
                          title_block, footer, section_divider, card)

OUT = r"thesis\health_rl\Poly_defense_presentation_v3.pptx"

prs = Presentation()
prs.slide_width  = Emu(SW)
prs.slide_height = Emu(SH)
BLANK = prs.slide_layouts[6]   # truly blank layout


def new_slide():
    return prs.slides.add_slide(BLANK)


# ── Slide 1: Title ────────────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
# Navy top bar
rect(s, 0, 0, SW, 1200000, fill=NAVY)
# Title text
tf = textbox(s, MARGIN_L, 200000, CONTENT_W, 700000)
para(tf, "ADAPTIVE HEALTH INSURANCE UNDERWRITING", 24, bold=True,
     color=WHITE, align=PP_ALIGN.CENTER)
new_para(tf, "VIA CONTEXTUAL BANDITS", 24, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, space_before=6)
# Sub-title
tf2 = textbox(s, MARGIN_L, 1300000, CONTENT_W, 600000)
para(tf2, "A Reinforcement Learning Approach for Cambodia", 16,
     italic=True, color=NAVY, align=PP_ALIGN.CENTER)
# Presenter info card
rect(s, MARGIN_L + 2000000, 2200000, CONTENT_W - 4000000, 800000, fill=LIGHT_BG)
tf3 = textbox(s, MARGIN_L + 2150000, 2300000, CONTENT_W - 4300000, 700000)
para(tf3, "LUN CHANPOLY", 16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
new_para(tf3, "ITC-AMS  ·  July 2026", 12, color=GRAY, align=PP_ALIGN.CENTER, space_before=6)
new_para(tf3, "Supervisor: Dr. HAS Sothea  ·  DAC Advisor: Mr. ON Radet", 11,
         color=GRAY, align=PP_ALIGN.CENTER, space_before=4)
# DAC logo placeholder text
tf4 = textbox(s, MARGIN_L, 3300000, CONTENT_W, 400000)
para(tf4, "Decent Actuarial Consultants Co., Ltd.", 12,
     color=GRAY, align=PP_ALIGN.CENTER)
footer(s, "Title", "–", 29)

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
footer(s, "Contents", "–", 29)

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
footer(s, "Introduction & Problem Background", "1", 29)

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
footer(s, "Introduction & Problem Background", "2", 29)

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
footer(s, "Introduction & Problem Background", "3", 29)

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
footer(s, "Introduction & Problem Background", "4", 29)

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
rq_h = 1050000
for i, (num, text) in enumerate(RQS):
    t = 1200000 + i * (rq_h + 100000)
    rect(s, MARGIN_L, t, 500000, rq_h, fill=NAVY)
    tf = textbox(s, MARGIN_L + 80000, t + 330000, 340000, 400000)
    para(tf, num, 16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 600000, t + 200000, CONTENT_W - 700000, rq_h - 400000)
    para(tf2, text, 13, color=DARK_TXT)
footer(s, "Introduction & Problem Background", "5", 29)

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
for i, (num, text) in enumerate(DELIVERABLES):
    t = 1550000 + i * 1000000
    rect(s, MARGIN_L, t, 300000, 800000, fill=NAVY)
    tfn = textbox(s, MARGIN_L + 80000, t + 280000, 200000, 250000)
    para(tfn, num, 14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, MARGIN_L + 380000, t + 100000, col_w - 450000, 700000)
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
for i, (num, text) in enumerate(OBJECTIVES):
    t = 1550000 + i * 950000
    rect(s, r_l, t, 300000, 750000, fill=BLUE)
    tfn = textbox(s, r_l + 80000, t + 260000, 200000, 250000)
    para(tfn, num, 14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tf2 = textbox(s, r_l + 380000, t + 150000, col_w - 420000, 600000)
    para(tf2, text, 12, color=DARK_TXT)
footer(s, "Introduction & Problem Background", "6", 29)


# ── Slide 9: Literature Review Section Divider ────────────────────────
s = new_slide()
section_divider(s, "Literature Review", "7", "II.", 29)

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
footer(s, "Literature Review", "7", 29)

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
footer(s, "Literature Review", "8", 29)

# ── Slide 12: Methodology Section Divider ────────────────────────────
s = new_slide()
section_divider(s, "Methodology & Model Design", "9", "III.", 29)

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
footer(s, "Methodology & Model Design", "9", 29)

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
footer(s, "Methodology & Model Design", "10", 29)

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
footer(s, "Methodology & Model Design", "11", 29)

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
footer(s, "Methodology & Model Design", "12", 29)

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
footer(s, "Results & Evaluation", "13", 29)

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
footer(s, "Methodology & Model Design", "14", 29)

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
         "Reward gain: +14.8% vs bandit-alone (20-seed, p<0.001, d=2.65)",
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
         "HITL+LinUCB:  +14.8%  (seed=42 headline)",
         "κ sweep: 0.3 – 0.9 tested; κ=0.7 optimal",
         "20-seed: paired Wilcoxon p<0.001, Cohen’s d=2.65",
     ], header_size=12, body_size=11,
     bg=GREEN_BG, accent=GREEN_ACC)

footer(s, "Methodology & Model Design", "15", 29)

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
footer(s, "Methodology & Model Design", "16", 29)


# ── Save ──────────────────────────────────────────────────────────────
prs.save(OUT)
print(f"Saved: {OUT}  ({len(prs.slides)} slides)")
