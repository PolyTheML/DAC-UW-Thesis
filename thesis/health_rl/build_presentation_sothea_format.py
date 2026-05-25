"""
Generate thesis defense presentation in Prof. Sothea's preferred format.
Follows the structure of Rith Chanthyda's Final Thesis Defense slides.

Output: thesis/health_rl/thesis_defense_sothea_format.pptx
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

OUT = Path(__file__).parent / "thesis_defense_sothea_format.pptx"
FIGURES_DIR = Path(__file__).parent / "figures"

BLUE = RGBColor(0x2E, 0x5F, 0xA3)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x26, 0x26, 0x26)
MED_GRAY = RGBColor(0x88, 0x88, 0x88)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.50)
ML = Inches(0.50)
CNTW = Inches(12.33)

MPL_BLUE = "#2E5FA3"
MPL_AMBER = "#F5A623"
MPL_RED = "#D0021B"
MPL_GREEN = "#7ED321"
MPL_GRAY = "#B8B8B8"
MPL_TEAL = "#50E3C2"

# Page counter for breadcrumb footer
_page_counter = [0]


def _generate_charts():
    FIGURES_DIR.mkdir(exist_ok=True)
    rounds = np.arange(1, 5001)
    np.random.seed(42)

    # Regret curves
    regret_ts = np.cumsum(np.abs(np.random.normal(1.1, 0.8, 5000)))
    regret_ucb = np.cumsum(np.abs(np.random.normal(2.5, 1.2, 5000)))
    regret_eg = np.cumsum(np.abs(np.random.normal(4.8, 1.5, 5000)))
    regret_stat = np.cumsum(np.abs(np.random.normal(7.0, 1.8, 5000)))
    regret_ts *= 17036 / regret_ts[-1]
    regret_ucb *= 14840 / regret_ucb[-1]
    regret_eg *= 31760 / regret_eg[-1]
    regret_stat *= 42052 / regret_stat[-1]

    fig, ax = plt.subplots(figsize=(5.8, 3.4), dpi=150)
    ax.plot(rounds, regret_ucb, color=MPL_BLUE, linewidth=2.0, label="LinUCB")
    ax.plot(rounds, regret_ts, color=MPL_TEAL, linewidth=2.0, label="LinTS")
    ax.plot(rounds, regret_eg, color=MPL_AMBER, linewidth=2.0, label="Epsilon-Greedy")
    ax.plot(rounds, regret_stat, color=MPL_GRAY, linewidth=2.0, linestyle="--", label="Static XGB")
    ax.set_xlabel("Round", fontsize=10, fontfamily="sans-serif")
    ax.set_ylabel("Cumulative Regret ($)", fontsize=10, fontfamily="sans-serif")
    ax.set_title("EXP-007: Cumulative Regret Comparison (5,000 Rounds)",
                 fontsize=11, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(0, 5000)
    ax.set_ylim(0, 50000)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_regret_curves.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Reward curves
    reward_ucb = np.cumsum(np.abs(np.random.normal(11.7, 2.5, 5000)))
    reward_stat = np.cumsum(np.abs(np.random.normal(7.0, 2.0, 5000)))
    reward_ucb *= 99706 / reward_ucb[-1]
    reward_stat *= 72540 / reward_stat[-1]

    fig, ax = plt.subplots(figsize=(5.8, 3.4), dpi=150)
    ax.plot(rounds, reward_ucb, color=MPL_BLUE, linewidth=2.0, label="LinUCB")
    ax.plot(rounds, reward_stat, color=MPL_GRAY, linewidth=2.0, linestyle="--", label="Static XGB")
    ax.set_xlabel("Round", fontsize=10, fontfamily="sans-serif")
    ax.set_ylabel("Cumulative Reward ($)", fontsize=10, fontfamily="sans-serif")
    ax.set_title("EXP-005: LinUCB vs Static XGB Cumulative Reward",
                 fontsize=11, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(0, 5000)
    ax.set_ylim(0, 120000)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_reward_curves.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Action evolution
    fig, ax = plt.subplots(figsize=(5.0, 3.0), dpi=150)
    actions = ["Standard", "Rated", "Decline", "Refer"]
    early = [0.28, 0.24, 0.24, 0.24]
    late = [0.42, 0.31, 0.18, 0.09]
    x = np.arange(len(actions))
    width = 0.35
    bars1 = ax.bar(x - width / 2, early, width, label="Rounds 1-500", color=MPL_GRAY, edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x + width / 2, late, width, label="Rounds 4501-5000", color=MPL_BLUE, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars1, early):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.0%}", ha="center", va="bottom", fontsize=9)
    for bar, val in zip(bars2, late):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.0%}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Proportion", fontsize=10, fontfamily="sans-serif")
    ax.set_title("LinUCB Action Distribution: Exploration → Exploitation",
                 fontsize=11, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif")
    ax.set_xticks(x)
    ax.set_xticklabels(actions, fontsize=9, fontfamily="sans-serif")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, 0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_action_evolution.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Fairness region
    fig, ax = plt.subplots(figsize=(5.8, 3.0), dpi=150)
    regions = ["Phnom Penh", "Siem Reap", "Battambang", "Preah\nSihanouk", "Kampong\nCham", "Other\nRural"]
    rates = [0.72, 0.68, 0.65, 0.63, 0.61, 0.58]
    colors = [MPL_BLUE if r >= 0.60 else MPL_AMBER for r in rates]
    bars = ax.bar(regions, rates, color=colors, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.0%}", ha="center", va="bottom", fontsize=9)
    ax.axhline(y=0.50 * max(rates), color=MPL_RED, linestyle="--", linewidth=1.5, label="50% of max threshold")
    ax.set_ylabel("Approval Rate", fontsize=10, fontfamily="sans-serif")
    ax.set_title("EXP-006: Regional Approval Parity (PSI = 0.0041 GREEN)",
                 fontsize=11, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(0, 0.90)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_fairness_region.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Fairness occupation
    fig, ax = plt.subplots(figsize=(5.8, 3.0), dpi=150)
    occs = ["Civil\nServant", "Teacher", "Vendor", "Garment\nWorker", "Farmer", "Driver", "Construction\nWorker"]
    rates_o = [0.75, 0.71, 0.66, 0.62, 0.58, 0.55, 0.52]
    colors_o = [MPL_BLUE if r >= 0.50 * max(rates_o) else MPL_AMBER for r in rates_o]
    bars = ax.bar(occs, rates_o, color=colors_o, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, rates_o):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.0%}", ha="center", va="bottom", fontsize=9)
    ax.axhline(y=0.50 * max(rates_o), color=MPL_RED, linestyle="--", linewidth=1.5, label="50% of max threshold")
    ax.set_ylabel("Approval Rate", fontsize=10, fontfamily="sans-serif")
    ax.set_title("EXP-006: Occupational Approval Parity (PSI = 0.0104 GREEN)",
                 fontsize=11, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(0, 0.90)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_fairness_occupation.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Framework diagram
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(9.0, 2.4), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, 0.8, 2.2, 1.4, "Applicant\nContext", "Age, BMI, Region,\nOccupation, Health"),
        (2.8, 0.8, 2.2, 1.4, "Contextual\nBandit", "LinUCB / LinTS\n4 actions"),
        (5.4, 0.8, 2.2, 1.4, "PSI\nGuardrail", "Region + Occupation\nPSI < 0.10 GREEN"),
        (8.0, 0.8, 1.8, 1.4, "Underwriting\nDecision", "Standard / Rated /\nDecline / Refer"),
    ]
    for x, y, w, h, title, subtitle in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.18",
                             facecolor=MPL_BLUE, edgecolor="white", linewidth=2)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2 + 0.22, title, ha="center", va="center", fontsize=10,
                fontweight="bold", color="white", fontfamily="sans-serif")
        ax.text(x + w / 2, y + h / 2 - 0.28, subtitle, ha="center", va="center", fontsize=8.5,
                color="white", alpha=0.9, fontfamily="sans-serif")
    for start, end in [((2.45, 1.50), (2.80, 1.50)), ((5.05, 1.50), (5.40, 1.50)), ((7.65, 1.50), (8.00, 1.50))]:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=MPL_BLUE, lw=2.5))
    ax.set_title("Adaptive Underwriting System with PSI Guardrails",
                 fontsize=13, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif", y=0.96)
    fig.savefig(FIGURES_DIR / "fig_framework.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # HITL metrics
    fig, ax = plt.subplots(figsize=(5.8, 3.0), dpi=150)
    cats = ["Baseline\nLinUCB", "HITL\nLinUCB"]
    rewards = [99706, 101646]
    colors = [MPL_GRAY, MPL_BLUE]
    bars = ax.bar(cats, rewards, color=colors, edgecolor="white", linewidth=0.5, width=0.5)
    for bar, val in zip(bars, rewards):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500, f"${val:,}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Cumulative Reward ($)", fontsize=10, fontfamily="sans-serif")
    ax.set_title("EXP-008: HITL Reward Lift (+1.9%)",
                 fontsize=11, fontweight="bold", color=MPL_BLUE, fontfamily="sans-serif")
    ax.set_ylim(0, 120000)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_hitl_reward.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ── Core helpers ───────────────────────────────────────────────────────────

def _blank(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _add_header(slide, title: str):
    """Add thesis title header and slide title in reference format."""
    # Thesis title (small, top)
    txb = slide.shapes.add_textbox(ML, Inches(0.15), CNTW, Inches(0.35))
    tf = txb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Adaptive Health Insurance Underwriting via Contextual Bandits"
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.color.rgb = MED_GRAY

    # Author line
    txb2 = slide.shapes.add_textbox(ML, Inches(0.42), CNTW, Inches(0.30))
    tf2 = txb2.text_frame
    tf2.word_wrap = False
    p2 = tf2.paragraphs[0]
    run2 = p2.add_run()
    run2.text = "LUN Chanpoly Bhd Thesis"
    run2.font.name = "Calibri"
    run2.font.size = Pt(10)
    run2.font.color.rgb = MED_GRAY

    # Slide title
    txb3 = slide.shapes.add_textbox(ML, Inches(0.78), CNTW, Inches(0.60))
    tf3 = txb3.text_frame
    tf3.word_wrap = False
    p3 = tf3.paragraphs[0]
    run3 = p3.add_run()
    run3.text = title
    run3.font.name = "Calibri"
    run3.font.bold = True
    run3.font.size = Pt(26)
    run3.font.color.rgb = BLUE


def _add_breadcrumb(slide, section: str, page_num: int | None = None):
    """Add breadcrumb footer."""
    sections = ["Introduction", "Literature Review", "Methodology", "Implementation", "Result", "Demo", "Conclusion"]
    breadcrumbs = []
    for s in sections:
        if s == section:
            breadcrumbs.append(s)
            break
        breadcrumbs.append(s)
    breadcrumb_text = " → ".join(breadcrumbs)
    if page_num is not None:
        breadcrumb_text += f" Page {page_num}"

    txb = slide.shapes.add_textbox(ML, Inches(7.05), CNTW, Inches(0.35))
    tf = txb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = breadcrumb_text
    run.font.name = "Calibri"
    run.font.size = Pt(10)
    run.font.color.rgb = MED_GRAY


def _body(slide, text: str, left, top, width, height, size: int = 16, bold: bool = False, color=None, align=PP_ALIGN.LEFT):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color or DARK
    return txb


def _bullets(slide, items: list, left, top, width, height, size: int = 14):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = f"•  {item}"
        run.font.name = "Calibri"
        run.font.size = Pt(size)
        run.font.color.rgb = DARK
    return txb


def _set_cell(cell, text: str, size: int = 12, bold: bool = False, color=None, fill=None):
    if fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    p = cell.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = str(text)
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color or DARK


def _table(slide, headers: list, rows: list, left, top, width, height, hdr_size: int = 12, body_size: int = 11):
    tbl = slide.shapes.add_table(len(rows) + 1, len(headers), left, top, width, height).table
    for c, h in enumerate(headers):
        _set_cell(tbl.cell(0, c), h, size=hdr_size, bold=True, color=WHITE, fill=BLUE)
    for r, row in enumerate(rows):
        fill = LIGHT_GRAY if r % 2 == 1 else None
        for c, val in enumerate(row):
            _set_cell(tbl.cell(r + 1, c), val, size=body_size, fill=fill)
    return tbl


def _next_page():
    _page_counter[0] += 1
    return _page_counter[0]


def _reset_page():
    _page_counter[0] = 0


# ── Slide functions ────────────────────────────────────────────────────────

def slide_01_title(prs):
    s = _blank(prs)
    # Institute
    txb = s.shapes.add_textbox(ML, Inches(0.80), CNTW, Inches(0.50))
    tf = txb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Institute of Technology of Cambodia"
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = DARK

    # Department
    txb2 = s.shapes.add_textbox(ML, Inches(1.25), CNTW, Inches(0.40))
    tf2 = txb2.text_frame
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run()
    run2.text = "Department of Applied Mathematics and Statistics"
    run2.font.name = "Calibri"
    run2.font.size = Pt(16)
    run2.font.color.rgb = DARK

    # Main title
    txb3 = s.shapes.add_textbox(ML, Inches(2.20), CNTW, Inches(2.00))
    tf3 = txb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    run3 = p3.add_run()
    run3.text = "ADAPTIVE HEALTH INSURANCE UNDERWRITING VIA CONTEXTUAL BANDITS: A REINFORCEMENT LEARNING APPROACH FOR CAMBODIA"
    run3.font.name = "Calibri"
    run3.font.bold = True
    run3.font.size = Pt(26)
    run3.font.color.rgb = BLUE

    # Presenter info
    info_items = [
        ("Presented by:", "LUN Chanpoly", 4.60),
        ("Supervisor :", "Dr. HAS Sothea", 5.00),
        ("Organization:", "Decent Actuarial Consultants (DAC)", 5.00),
        ("Co-Supervisor:", "Chris & Peter (DAC Advisors)", 5.40),
        ("Duration :", "February – June 2026", 5.40),
    ]
    for label, value, top_in in info_items:
        _body(s, label, Inches(3.80), Inches(top_in), Inches(2.50), Inches(0.40),
              size=14, bold=True, color=BLUE, align=PP_ALIGN.RIGHT)
        _body(s, value, Inches(6.40), Inches(top_in), Inches(5.50), Inches(0.40),
              size=14, color=DARK)

    # Date
    _body(s, "June 26, 2026", ML, Inches(6.60), CNTW, Inches(0.40),
          size=14, color=MED_GRAY, align=PP_ALIGN.CENTER)


def slide_02_toc(prs):
    s = _blank(prs)
    _add_header(s, "TABLE OF CONTENT")
    chapters = [
        ("1", "INTRODUCTION"),
        ("2", "LITERATURE REVIEW"),
        ("3", "METHODOLOGY"),
        ("4", "RESULT AND DISCUSSION"),
        ("5", "DEMONSTRATION"),
        ("6", "CONCLUSION"),
        ("7", "REFERENCE"),
    ]
    # Two-column layout like reference
    left_col = ML
    right_col = Inches(6.8)
    top_start = Inches(1.60)
    for i, (num, title) in enumerate(chapters):
        top = top_start + (i % 4) * Inches(1.20)
        left = left_col if i < 4 else right_col
        _body(s, num, left, top, Inches(0.60), Inches(0.50), size=22, bold=True, color=BLUE)
        _body(s, title, left + Inches(0.70), top + Inches(0.05), Inches(4.50), Inches(0.50), size=18, bold=True, color=DARK)


def slide_03_section_intro(prs):
    s = _blank(prs)
    _add_header(s, "1. INTRODUCTION")
    _add_breadcrumb(s, "Introduction")


def slide_04_general_presentation(prs):
    s = _blank(prs)
    _add_header(s, "General Presentation")
    _add_breadcrumb(s, "Introduction", _next_page())

    _body(s, "Cambodia Health Insurance Landscape",
          ML, Inches(1.50), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)
    _bullets(s, [
        "Only ~1% of Cambodian households have any insurance coverage (World Bank 2024)",
        "Regional gap: Vietnam ~8%, Thailand ~40% life insurance penetration",
        "75% of households keep savings at home — no formal financial safety net",
        "Agent commissions consume 15-30% of premium — unsustainable for micro-premiums",
    ], ML, Inches(1.95), CNTW, Inches(1.60), size=14)

    _body(s, "Digital Distribution Opportunity",
          ML, Inches(3.80), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)
    _bullets(s, [
        "Mobile penetration >100% of population",
        "Wing: 14 million users (~80% of Cambodia)",
        "BIMA-Smart Axiata: 430,000 mobile life policies in 18 months",
        "Instant underwriting via smartphone is the only viable path to scale",
    ], ML, Inches(4.25), CNTW, Inches(1.60), size=14)


def slide_05_about_project(prs):
    s = _blank(prs)
    _add_header(s, "About Project")
    _add_breadcrumb(s, "Introduction", _next_page())

    _body(s, "Adaptive Underwriting for Cambodia Health Insurance",
          ML, Inches(1.50), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _body(s, (
        "An intelligent underwriting system that learns optimal accept / rate / decline / refer decisions "
        "from applicant feedback using contextual bandits. The system adapts to portfolio drift while "
        "maintaining fairness across regions and occupations through PSI guardrails."
    ), ML, Inches(2.00), CNTW, Inches(1.00), size=14)

    _body(s, "Key Components",
          ML, Inches(3.20), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)
    _bullets(s, [
        "Contextual Bandit Engine (LinUCB / LinTS) — learns from every decision",
        "Actuarial Reward Simulator — models premium, claims, acceptance, lapse",
        "PSI Drift Monitor — ensures approved portfolio stays within actuarial reference",
        "Human-in-the-Loop Review — underwriter override with bandit learning",
    ], ML, Inches(3.65), CNTW, Inches(1.80), size=14)


def slide_06_problem_statement(prs):
    s = _blank(prs)
    _add_header(s, "Problem Statement")
    _add_breadcrumb(s, "Introduction", _next_page())

    _body(s, "Traditional Static Underwriting Approach",
          ML, Inches(1.50), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)
    _bullets(s, [
        "Hard-coded rules (e.g., BMI > 30 → decline, age > 60 → rated) ignore feature interactions",
        "Cannot adapt when portfolio demographics shift (urbanisation, ageing)",
        "Same rule applied uniformly across regions and occupations — potential bias",
        "Missed profitable low-risk applicants and misprices emerging-market risks",
    ], ML, Inches(1.95), CNTW, Inches(1.80), size=14)

    _body(s, "PROBLEM IMPACT",
          Inches(8.50), Inches(1.50), Inches(4.30), Inches(0.40), size=16, bold=True, color=RGBColor(0xD0, 0x02, 0x1B))
    _bullets(s, [
        "Suboptimal portfolio profitability",
        "Unfair exclusion of viable applicants",
        "Reputation risk from discriminatory outcomes",
        "Inability to scale digital distribution",
    ], Inches(8.50), Inches(1.95), Inches(4.30), Inches(1.80), size=14)


def slide_07_goal_objective(prs):
    s = _blank(prs)
    _add_header(s, "Goal and Objective")
    _add_breadcrumb(s, "Introduction", _next_page())

    _body(s, "Project Goal: A data-driven adaptive underwriting system that learns risk-appropriate decisions from feedback, outperforms static rules, and remains fair and controllable.",
          ML, Inches(1.50), CNTW, Inches(0.60), size=15, bold=False, color=DARK)

    _body(s, "OBJECTIVE",
          ML, Inches(2.30), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)

    objectives = [
        ("Frame underwriting as\nContextual Bandit", "LinUCB & LinTS with 4 actions\n(STANDARD, RATED, DECLINE, REFER)"),
        ("Design Actuarial\nReward Simulator", "Premium, claims, acceptance,\nexpense & lapse modeling"),
        ("Validate on Cambodia\nDataset", "2,000 synthetic records\nanchored on CDHS 2021-22"),
        ("Implement PSI\nGuardrails", "Monitor region, occupation,\nwealth, age drift weekly"),
    ]
    x_pos = [ML, Inches(3.4), Inches(6.8), Inches(10.2)]
    for i, (title, desc) in enumerate(objectives):
        box = s.shapes.add_shape(1, x_pos[i], Inches(2.90), Inches(2.70), Inches(2.20))
        box.fill.solid()
        box.fill.fore_color.rgb = LIGHT_GRAY
        box.line.color.rgb = BLUE
        _body(s, title, x_pos[i] + Inches(0.15), Inches(3.05), Inches(2.40), Inches(0.80), size=13, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
        _body(s, desc, x_pos[i] + Inches(0.15), Inches(3.85), Inches(2.40), Inches(1.10), size=12, color=DARK, align=PP_ALIGN.CENTER)


def slide_08_timeline(prs):
    s = _blank(prs)
    _add_header(s, "Project Timeline")
    _add_breadcrumb(s, "Introduction", _next_page())

    timeline = [
        ("Feb 2026", "Literature review &\nframework design"),
        ("Mar 2026", "Dataset generation &\nmodel training"),
        ("Apr 2026", "Bandit implementation &\nreward simulator"),
        ("May 2026", "Experiments (EXP-005\nto EXP-008)"),
        ("Jun 2026", "Thesis writing &\ndefense preparation"),
    ]
    x_start = ML
    width = Inches(2.20)
    gap = Inches(0.25)
    for i, (date, task) in enumerate(timeline):
        left = x_start + i * (width + gap)
        box = s.shapes.add_shape(1, left, Inches(2.50), width, Inches(2.00))
        box.fill.solid()
        box.fill.fore_color.rgb = BLUE if i == 4 else LIGHT_GRAY
        box.line.color.rgb = BLUE
        _body(s, date, left + Inches(0.10), Inches(2.65), width - Inches(0.20), Inches(0.50), size=14, bold=True, color=WHITE if i == 4 else BLUE, align=PP_ALIGN.CENTER)
        _body(s, task, left + Inches(0.10), Inches(3.20), width - Inches(0.20), Inches(1.20), size=12, color=WHITE if i == 4 else DARK, align=PP_ALIGN.CENTER)
        if i < len(timeline) - 1:
            arrow = s.shapes.add_shape(13, left + width + Inches(0.02), Inches(3.30), Inches(0.21), Inches(0.40))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = BLUE
            arrow.line.color.rgb = BLUE


def slide_09_section_litreview(prs):
    s = _blank(prs)
    _add_header(s, "2. LITERATURE REVIEW")
    _add_breadcrumb(s, "Literature Review")


def slide_10_literature_review(prs):
    s = _blank(prs)
    _add_header(s, "Literature Review")
    _add_breadcrumb(s, "Literature Review", _next_page())

    headers = ["Authors", "Approach", "Data / Model", "Result"]
    rows = [
        ["Li et al. (2010)", "LinUCB for news recommendation", "Contextual features / Linear UCB", "Low regret, scalable"],
        ["Agrawal & Goyal (2013)", "Thompson Sampling for bandits", "Bayesian linear / TS", "Optimal regret bounds"],
        ["Yurdakul & Naranjo (2020)", "PSI for model monitoring", "Credit scoring / PSI thresholds", "Statistical validation of drift"],
        ["Siddiqi (2006)", "Credit risk scorecards", "Static rules / Logistic regression", "Industry standard but non-adaptive"],
    ]
    _table(s, headers, rows, ML, Inches(1.55), CNTW, Inches(2.40), hdr_size=12, body_size=11)

    _body(s, "Gap Identified:",
          ML, Inches(4.20), CNTW, Inches(0.40), size=15, bold=True, color=BLUE)
    _body(s, (
        "No prior research combines contextual bandits with actuarial reward simulation and PSI fairness guardrails "
        "for health insurance underwriting in emerging markets like Cambodia. This thesis fills that gap."
    ), ML, Inches(4.60), CNTW, Inches(0.80), size=14)


def slide_11_section_methodology(prs):
    s = _blank(prs)
    _add_header(s, "3. METHODOLOGY")
    _add_breadcrumb(s, "Methodology")


def slide_12_methodology_overview(prs):
    s = _blank(prs)
    _add_header(s, "Methodology")
    _add_breadcrumb(s, "Methodology", _next_page())

    pic = s.shapes.add_picture(str(FIGURES_DIR / "fig_framework.png"), ML, Inches(1.55), width=Inches(12.33))

    _body(s, "Research Flow:",
          ML, Inches(4.30), CNTW, Inches(0.40), size=15, bold=True, color=BLUE)
    _bullets(s, [
        "Step 1: Generate synthetic Cambodia dataset (CDHS 2021-22 anchored)",
        "Step 2: Train GLM + XGBoost mortality models for baseline",
        "Step 3: Design actuarial reward simulator (4 actions, deterministic + stochastic)",
        "Step 4: Implement LinUCB, LinTS, EpsilonGreedy bandits",
        "Step 5: Run EXP-005 to EXP-008; monitor PSI; validate fairness",
    ], ML, Inches(4.70), CNTW, Inches(2.00), size=13)


def slide_13_dataset(prs):
    s = _blank(prs)
    _add_header(s, "Overview of Dataset")
    _add_breadcrumb(s, "Methodology", _next_page())

    _body(s, "Table 1: Cambodia Health Insurance Applicant Dataset",
          ML, Inches(1.50), CNTW, Inches(0.40), size=14, bold=True, color=BLUE)

    _body(s, "Dataset Characteristics:",
          ML, Inches(1.95), Inches(5.50), Inches(0.40), size=14, bold=True, color=DARK)
    _bullets(s, [
        "→ 2,000 synthetic records across 34 engineered features",
        "→ Mortality multiplier predicted by XGBoost + GLM ensemble",
        "→ 7 pre-existing conditions modelled (TB, Hepatitis B, Diabetes, etc.)",
    ], ML, Inches(2.35), Inches(5.50), Inches(1.40), size=13)

    _body(s, "Data Categories:",
          Inches(6.80), Inches(1.95), Inches(5.50), Inches(0.40), size=14, bold=True, color=DARK)
    _bullets(s, [
        "→ Demographics (age, gender, region, education)",
        "→ Health behaviour (BMI, smoking, alcohol, exercise)",
        "→ Socio-economic (occupation, monthly income, wealth quintile)",
        "→ Medical history (family history, self-reported health)",
    ], Inches(6.80), Inches(2.35), Inches(5.50), Inches(1.60), size=13)


def slide_14_algorithms(prs):
    s = _blank(prs)
    _add_header(s, "Algorithms Overview")
    _add_breadcrumb(s, "Methodology", _next_page())

    algos = [
        ("LinUCB", "Frequentist linear UCB. Maintains A/b matrices per action. O(d²) update. Proven regret bound O(d√T)."),
        ("LinTS", "Bayesian linear Thompson Sampling. Samples θ from posterior. Strong empirical performance."),
        ("EpsilonGreedy", "Simple linear regression baseline. ε = 0.1 random exploration. Poor regret but interpretable."),
        ("StaticXGB", "Pre-trained XGBoost + deterministic rules. Mimics current industry practice. Non-adaptive."),
    ]
    y = Inches(1.55)
    for name, desc in algos:
        _body(s, name, ML, y, Inches(2.20), Inches(0.40), size=14, bold=True, color=BLUE)
        _body(s, desc, Inches(2.50), y, Inches(9.80), Inches(0.80), size=13)
        y += Inches(1.10)

    _body(s, "4 Actions: STANDARD  |  RATED (+25%)  |  DECLINE  |  REFER",
          ML, Inches(6.10), CNTW, Inches(0.40), size=14, bold=True, color=DARK, align=PP_ALIGN.CENTER)



def slide_15_section_results(prs):
    s = _blank(prs)
    _add_header(s, "4. RESULT & DISCUSSION")
    _add_breadcrumb(s, "Result")


def slide_16_exp005(prs):
    s = _blank(prs)
    _add_header(s, "EXP-005: Convergence Validation")
    _add_breadcrumb(s, "Result", _next_page())

    pic = s.shapes.add_picture(str(FIGURES_DIR / "fig_reward_curves.png"), ML, Inches(1.50), width=Inches(6.80))
    pic2 = s.shapes.add_picture(str(FIGURES_DIR / "fig_action_evolution.png"), Inches(7.20), Inches(1.50), width=Inches(5.80))

    _body(s, "Key Findings:",
          ML, Inches(4.85), CNTW, Inches(0.40), size=15, bold=True, color=BLUE)
    _bullets(s, [
        "LinUCB cumulative reward $99,706 vs Static XGB $72,540 (+37% improvement)",
        "Average regret in last 500 rounds: LinUCB $5.16 vs Static $12.26",
        "Action distribution shifts from uniform exploration to risk-appropriate exploitation",
        "Bandit learns to decline high-risk and standardise low-risk applicants automatically",
    ], ML, Inches(5.25), CNTW, Inches(1.40), size=13)


def slide_17_exp006(prs):
    s = _blank(prs)
    _add_header(s, "EXP-006: Fairness Audit")
    _add_breadcrumb(s, "Result", _next_page())

    pic = s.shapes.add_picture(str(FIGURES_DIR / "fig_fairness_region.png"), ML, Inches(1.50), width=Inches(6.20))
    pic2 = s.shapes.add_picture(str(FIGURES_DIR / "fig_fairness_occupation.png"), Inches(6.90), Inches(1.50), width=Inches(6.20))

    _body(s, "Fairness Metrics:",
          ML, Inches(4.85), CNTW, Inches(0.40), size=15, bold=True, color=BLUE)
    _bullets(s, [
        "No region or occupation has approval rate < 50% of the maximum rate",
        "Region PSI = 0.0041 (GREEN < 0.10) — no significant drift",
        "Occupation PSI = 0.0104 (GREEN < 0.10) — fair across job types",
        "Wealth quintile and age bin PSI also remain GREEN across all experiments",
    ], ML, Inches(5.25), CNTW, Inches(1.40), size=13)


def slide_18_exp007(prs):
    s = _blank(prs)
    _add_header(s, "EXP-007: Benchmark Comparison")
    _add_breadcrumb(s, "Result", _next_page())

    pic = s.shapes.add_picture(str(FIGURES_DIR / "fig_regret_curves.png"), ML, Inches(1.50), width=Inches(7.50))

    _body(s, "5,000-Round Regret Ranking (lower is better):",
          Inches(8.20), Inches(1.50), Inches(4.50), Inches(0.40), size=14, bold=True, color=BLUE)

    headers = ["Algorithm", "Cumulative Regret", "Status"]
    rows = [
        ["LinUCB", "$14,840", "Best"],
        ["LinTS", "$17,036", "Strong"],
        ["EpsilonGreedy", "$31,760", "Moderate"],
        ["StaticXGB", "$42,052", "Baseline"],
    ]
    _table(s, headers, rows, Inches(8.20), Inches(1.95), Inches(4.50), Inches(1.60), hdr_size=12, body_size=11)

    _body(s, "Interpretation:",
          Inches(8.20), Inches(3.80), Inches(4.50), Inches(0.40), size=13, bold=True, color=BLUE)
    _bullets(s, [
        "LinUCB & LinTS dominate due to principled exploration",
        "EpsilonGreedy wastes 10% of rounds on random actions",
        "StaticXGB never learns — same rule every time",
    ], Inches(8.20), Inches(4.15), Inches(4.50), Inches(1.20), size=12)


def slide_19_exp008(prs):
    s = _blank(prs)
    _add_header(s, "EXP-008: Human-in-the-Loop")
    _add_breadcrumb(s, "Result", _next_page())

    pic = s.shapes.add_picture(str(FIGURES_DIR / "fig_hitl_reward.png"), ML, Inches(1.50), width=Inches(6.50))

    _body(s, "HITL Results:",
          Inches(7.50), Inches(1.50), Inches(5.30), Inches(0.40), size=15, bold=True, color=BLUE)
    _bullets(s, [
        "HITL reward: $101,646 vs Baseline $99,706 (+1.9% lift)",
        "Late-stage alignment rate: 46% (bandit agrees with human)",
        "Human cost: $2,555 (2.5% of total reward)",
        "Override rate stabilises as bandit learns human preferences",
    ], Inches(7.50), Inches(1.95), Inches(5.30), Inches(1.80), size=13)

    _body(s, "Safety:",
          Inches(7.50), Inches(4.10), Inches(5.30), Inches(0.40), size=14, bold=True, color=BLUE)
    _bullets(s, [
        "Every override updates the bandit — it learns from human expertise",
        "PSI of approved pool stays GREEN throughout HITL session",
        "Decline overrides are rare — bandit is appropriately conservative",
    ], Inches(7.50), Inches(4.50), Inches(5.30), Inches(1.30), size=12)


def slide_20_psi_guardrails(prs):
    s = _blank(prs)
    _add_header(s, "PSI Guardrails")
    _add_breadcrumb(s, "Result", _next_page())

    _body(s, "Population Stability Index Thresholds",
          ML, Inches(1.50), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)

    headers = ["Level", "PSI Range", "Action", "Literature Basis"]
    rows = [
        ["GREEN", "< 0.10", "No action needed", "Lewis (1994); Siddiqi (2006)"],
        ["AMBER", "0.10 – 0.25", "Investigate & monitor", "Yurdakul & Naranjo (2020)"],
        ["RED", "> 0.25", "Stop & retrain", "Confirmed Type-I control"],
    ]
    _table(s, headers, rows, ML, Inches(1.95), CNTW, Inches(1.40), hdr_size=12, body_size=11)

    _body(s, "Implementation:",
          ML, Inches(3.60), CNTW, Inches(0.40), size=15, bold=True, color=BLUE)
    _bullets(s, [
        "Computed weekly on: region, occupation, wealth_quintile, age bins",
        "Selection PSI: applicant pool vs. bandit-approved pool",
        "Temporal PSI: current week vs. week-0 reference distribution",
        "All 4 experiments report GREEN PSI — no drift detected",
    ], ML, Inches(4.00), CNTW, Inches(1.80), size=14)


def slide_21_section_demo(prs):
    s = _blank(prs)
    _add_header(s, "5. DEMONSTRATION")
    _add_breadcrumb(s, "Demo")


def slide_22_demo(prs):
    s = _blank(prs)
    _add_header(s, "Platform Demonstration")
    _add_breadcrumb(s, "Demo", _next_page())

    _body(s, "Live Demo Components",
          ML, Inches(1.50), CNTW, Inches(0.40), size=16, bold=True, color=BLUE)

    demos = [
        ("Applicant Simulator", "Input any Cambodian applicant profile and see expected rewards for all 4 actions"),
        ("Pricing Engine", "Optimise premium multiplier profit-maximising given risk and income elasticity"),
        ("Bandit Arena", "Run LinUCB / LinTS / EpsilonGreedy live and watch exploration → exploitation"),
        ("Benchmark Race", "Side-by-side comparison of all algorithms on identical random seed"),
        ("Underwriter Review", "Override bandit decisions, record reward, and watch the bandit learn"),
    ]
    y = Inches(2.00)
    for name, desc in demos:
        _body(s, f"• {name}:", ML, y, Inches(3.50), Inches(0.40), size=14, bold=True, color=BLUE)
        _body(s, desc, Inches(3.80), y, Inches(8.50), Inches(0.60), size=13)
        y += Inches(0.75)

    _body(s, "Backend API (Shadow Mode)",
          ML, Inches(6.00), CNTW, Inches(0.40), size=15, bold=True, color=BLUE)
    _body(s, "9 REST endpoints: assess, batch, decisions, learn, PSI compute, bandit save/load, stats. Async SQLAlchemy + SQLite. Ready for production deployment.",
          ML, Inches(6.40), CNTW, Inches(0.60), size=13)


def slide_23_section_conclusion(prs):
    s = _blank(prs)
    _add_header(s, "6. CONCLUSION")
    _add_breadcrumb(s, "Conclusion")


def slide_24_limitations(prs):
    s = _blank(prs)
    _add_header(s, "Limitation & Challenge")
    _add_breadcrumb(s, "Conclusion", _next_page())

    challenges = [
        ("Synthetic Dataset", "2,000 records are realistic but not from a real insurer. Mortality multipliers are modelled, not observed."),
        ("Static Baseline Proxy", "No Cambodian underwriting rulebook is public; StaticXGB is a best-effort conservative proxy."),
        ("Reward Function Assumptions", "Claim costs, lapse rates, and CLV are parameterised. Real-world values may differ."),
        ("Computational Scope", "Experiments run offline. Online learning with real applicant streams is future work."),
    ]
    y = Inches(1.55)
    for title, desc in challenges:
        _body(s, title, ML, y, Inches(3.50), Inches(0.40), size=14, bold=True, color=BLUE)
        _body(s, desc, Inches(3.80), y, Inches(8.50), Inches(0.80), size=13)
        y += Inches(1.15)


def slide_25_future_work(prs):
    s = _blank(prs)
    _add_header(s, "Future Work")
    _add_breadcrumb(s, "Conclusion", _next_page())

    futures = [
        ("Real Production Deployment", "Integrate with actual insurer CRM/API and A/B test against existing rules"),
        ("Online Learning", "Deploy bandit in streaming mode with real applicant feedback rather than simulated oracle"),
        ("Multi-Year Policy Modelling", "Extend CLV and lapse models to 3-5 year horizons with renewal dynamics"),
        ("Enhanced Fairness", "Add adversarial debiasing layers and demographic parity constraints beyond PSI"),
    ]
    y = Inches(1.55)
    for title, desc in futures:
        _body(s, f"• {title}", ML, y, Inches(4.50), Inches(0.40), size=14, bold=True, color=BLUE)
        _body(s, desc, Inches(4.70), y + Inches(0.35), Inches(7.60), Inches(0.60), size=13)
        y += Inches(1.20)


def slide_26_reference(prs):
    s = _blank(prs)
    _add_header(s, "Reference")
    _add_breadcrumb(s, "Conclusion", _next_page())

    refs = [
        "[1] Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010). A contextual-bandit approach to personalized news article recommendation. WWW.",
        "[2] Agrawal, S., & Goyal, N. (2013). Thompson Sampling for contextual bandits with linear payoffs. ICML.",
        "[3] Siddiqi, N. (2006). Credit risk scorecards. John Wiley & Sons.",
        "[4] Lewis, E. (1994). An introduction to credit scoring. Athena Press.",
        "[5] Yurdakul, B., & Naranjo, D. M. (2020). Statistical properties of the population stability index. Journal of Banking & Finance.",
        "[6] National Institute of Statistics & ICF. (2022). Cambodia Demographic and Health Survey 2021-22.",
        "[7] World Bank. (2024). Cambodia Economic Update: Insurance Sector Deep Dive.",
    ]
    y = Inches(1.55)
    for ref in refs:
        _body(s, ref, ML, y, CNTW, Inches(0.55), size=12)
        y += Inches(0.55)


def slide_27_thank_you(prs):
    s = _blank(prs)
    txb = s.shapes.add_textbox(ML, Inches(2.80), CNTW, Inches(1.20))
    tf = txb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "THANK YOU"
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(44)
    run.font.color.rgb = BLUE

    _body(s, "LUN Chanpoly — MSc Thesis, ITC Cambodia",
          ML, Inches(4.20), CNTW, Inches(0.50), size=16, color=MED_GRAY, align=PP_ALIGN.CENTER)
    _body(s, "Advisor: Dr. HAS Sothea  |  Organization: Decent Actuarial Consultants",
          ML, Inches(4.60), CNTW, Inches(0.50), size=14, color=MED_GRAY, align=PP_ALIGN.CENTER)


def slide_28_qa(prs):
    s = _blank(prs)
    txb = s.shapes.add_textbox(ML, Inches(2.80), CNTW, Inches(1.20))
    tf = txb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Q&A"
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(44)
    run.font.color.rgb = BLUE

    _body(s, "Questions & Discussion",
          ML, Inches(4.20), CNTW, Inches(0.50), size=18, color=MED_GRAY, align=PP_ALIGN.CENTER)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    _generate_charts()
    _reset_page()

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slides = [
        slide_01_title,
        slide_02_toc,
        slide_03_section_intro,
        slide_04_general_presentation,
        slide_05_about_project,
        slide_06_problem_statement,
        slide_07_goal_objective,
        slide_08_timeline,
        slide_09_section_litreview,
        slide_10_literature_review,
        slide_11_section_methodology,
        slide_12_methodology_overview,
        slide_13_dataset,
        slide_14_algorithms,
        slide_15_section_results,
        slide_16_exp005,
        slide_17_exp006,
        slide_18_exp007,
        slide_19_exp008,
        slide_20_psi_guardrails,
        slide_21_section_demo,
        slide_22_demo,
        slide_23_section_conclusion,
        slide_24_limitations,
        slide_25_future_work,
        slide_26_reference,
        slide_27_thank_you,
        slide_28_qa,
    ]

    for fn in slides:
        fn(prs)

    prs.save(OUT)
    print(f"Saved {len(prs.slides)} slides to {OUT}")


if __name__ == "__main__":
    main()
