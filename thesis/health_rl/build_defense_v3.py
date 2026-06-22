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


# ── Save ──────────────────────────────────────────────────────────────
prs.save(OUT)
print(f"Saved: {OUT}  ({len(prs.slides)} slides)")
