"""
Generate auto_defense_presentation.pptx — 20-slide thesis defense deck.
Run:    python thesis/auto/build_presentation.py
Output: thesis/auto/auto_defense_presentation.pptx
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).parent / "auto_defense_presentation.pptx"
FIGURES_DIR = Path(__file__).parent / "figures"

# ── Style constants ────────────────────────────────────────────────────────
BLUE       = RGBColor(0x2E, 0x5F, 0xA3)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK       = RGBColor(0x26, 0x26, 0x26)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.50)
ML      = Inches(0.60)    # left margin
CNTW    = Inches(12.13)   # content width

# Matplotlib theme matching pptx
MPL_BLUE   = "#2E5FA3"
MPL_AMBER  = "#F5A623"
MPL_RED    = "#D0021B"
MPL_GREEN  = "#7ED321"
MPL_GRAY   = "#B8B8B8"


# ── Chart generation ───────────────────────────────────────────────────────

def _generate_charts():
    """Generate matplotlib figures and save to thesis/auto/figures/."""
    FIGURES_DIR.mkdir(exist_ok=True)

    # ── Chart 1: EXP-002 Responsiveness ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(5.2, 3.0), dpi=150)
    drift_pct = [0, 10, 20, 30, 40, 50]
    max_psi = [0.000, 0.035, 0.092, 0.168, 0.245, 0.312]
    bar_colors = [
        MPL_BLUE if p < 0.10 else MPL_AMBER if p < 0.25 else MPL_RED
        for p in max_psi
    ]
    ax.bar([f"{d}%" for d in drift_pct], max_psi, color=bar_colors,
           edgecolor="white", linewidth=0.5, width=0.65)
    ax.axhline(y=0.10, color=MPL_GREEN, linestyle="--", linewidth=1.5,
               label="GREEN (0.10)")
    ax.axhline(y=0.25, color=MPL_AMBER, linestyle="--", linewidth=1.5,
               label="AMBER (0.25)")
    ax.set_ylabel("Max PSI", fontsize=10, fontfamily="sans-serif")
    ax.set_xlabel("Drift Fraction", fontsize=10, fontfamily="sans-serif")
    ax.set_title("PSI Increases Monotonically with Drift",
                 fontsize=12, fontweight="bold", color=MPL_BLUE,
                 fontfamily="sans-serif")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_ylim(0, 0.36)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_exp002_responsiveness.png",
                bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # ── Chart 2: Failure Modes ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(6.0, 3.0), dpi=150)
    modes = ["FM1\nHighway", "FM2\nMonsoon", "FM3\nTail Risk"]
    primary = [0.04, 0.03, 0.02]
    secondary = [0.23, 0.30, 0.50]  # FM3 capped for visual scale
    x = np.arange(len(modes))
    width = 0.35
    bars1 = ax.bar(x - width / 2, primary, width,
                   label="Primary (Premium PSI)", color=MPL_GRAY,
                   edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x + width / 2, secondary, width,
                   label="Secondary Metric", color=MPL_RED,
                   edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars1, primary):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.008,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9)
    for bar, val in zip(bars2, secondary):
        label = "42.3" if val > 1 else f"{val:.2f}"
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.008,
                label, ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("PSI", fontsize=10, fontfamily="sans-serif")
    ax.set_title("Primary vs Secondary Detection",
                 fontsize=12, fontweight="bold", color=MPL_BLUE,
                 fontfamily="sans-serif")
    ax.set_xticks(x)
    ax.set_xticklabels(modes, fontsize=9, fontfamily="sans-serif")
    ax.legend(loc="upper right", fontsize=8)
    ax.axhline(y=0.10, color=MPL_GREEN, linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(y=0.25, color=MPL_AMBER, linestyle="--", linewidth=1, alpha=0.7)
    ax.set_ylim(0, 0.58)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_failure_modes.png",
                bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # ── Chart 3: EXP-004 Temporal Drift ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=150)
    months = ["Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    psi_vals = [0.052, 0.089, 0.071, 0.098, 0.063,
                0.095, 0.112, 0.084, 0.058, 0.091, 0.047]
    point_colors = [MPL_RED if p >= 0.10 else MPL_BLUE for p in psi_vals]
    ax.plot(months, psi_vals, marker="o", markersize=5, linewidth=1.8,
            color=MPL_BLUE, zorder=3)
    for m, p, c in zip(months, psi_vals, point_colors):
        ax.scatter(m, p, color=c, s=50, zorder=4,
                   edgecolors="white", linewidth=0.5)
    ax.axhline(y=0.10, color=MPL_GREEN, linestyle="--", linewidth=1.5,
               label="GREEN (0.10)")
    ax.axhline(y=0.25, color=MPL_AMBER, linestyle="--", linewidth=1.5,
               label="AMBER (0.25)")
    ax.axvspan(4.5, 6.5, alpha=0.12, color=MPL_RED,
               label="Monsoon onset")
    ax.set_ylabel("Consecutive-Month PSI", fontsize=10,
                  fontfamily="sans-serif")
    ax.set_xlabel("Month Transition", fontsize=10,
                  fontfamily="sans-serif")
    ax.set_title("Signal Lost in Sampling Noise (n=125)",
                 fontsize=12, fontweight="bold", color=MPL_BLUE,
                 fontfamily="sans-serif")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, 0.20)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURES_DIR / "fig_exp004_temporal.png",
                bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # ── Chart 4: Framework Diagram ───────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9.0, 2.6), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.3, 0.9, 2.6, 1.3, "Season-Aware\nComparison",
         "YoY / rolling-window"),
        (3.7, 0.9, 2.6, 1.3, "Secondary\nMetrics",
         "idle_pct, braking, jerk"),
        (7.1, 0.9, 2.6, 1.3, "Cohort-Level\nPSI",
         "High-risk & low-risk\nsub-populations"),
    ]
    for x, y, w, h, title, subtitle in boxes:
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.05,rounding_size=0.18",
            facecolor=MPL_BLUE, edgecolor="white", linewidth=2
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2 + 0.18, title,
                ha="center", va="center", fontsize=10,
                fontweight="bold", color="white",
                fontfamily="sans-serif")
        ax.text(x + w / 2, y + h / 2 - 0.32, subtitle,
                ha="center", va="center", fontsize=8.5,
                color="white", alpha=0.9, fontfamily="sans-serif")
    ax.annotate("", xy=(3.6, 1.55), xytext=(3.05, 1.55),
                arrowprops=dict(arrowstyle="->", color=MPL_BLUE, lw=2.5))
    ax.annotate("", xy=(7.0, 1.55), xytext=(6.45, 1.55),
                arrowprops=dict(arrowstyle="->", color=MPL_BLUE, lw=2.5))
    ax.set_title("Temporal Multi-Metric Monitoring Framework",
                 fontsize=13, fontweight="bold", color=MPL_BLUE,
                 fontfamily="sans-serif", y=0.96)
    fig.savefig(FIGURES_DIR / "fig_framework.png",
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ── Core helpers ───────────────────────────────────────────────────────────

def _blank(prs: Presentation):
    """Add a blank slide (layout index 6 = Blank in Office default theme)."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def _title(slide, text: str, top=Inches(0.35)):
    """Blue bold 28pt title text box pinned to the top."""
    txb = slide.shapes.add_textbox(ML, top, CNTW, Inches(0.90))
    tf = txb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = BLUE
    return txb


def _body(slide, text: str, left, top, width, height,
          size: int = 18, bold: bool = False,
          color=None, align=PP_ALIGN.LEFT):
    """Plain body text box with word wrap."""
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


def _bullets(slide, items: list, left, top, width, height, size: int = 16):
    """Bulleted text box — each item gets a bullet prefix."""
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


def _set_cell(cell, text: str, size: int = 12, bold: bool = False,
              color=None, fill=None):
    """Set table cell text + optional fill. Adds a run to the empty paragraph."""
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


def _table(slide, headers: list, rows: list,
           left, top, width, height,
           hdr_size: int = 13, body_size: int = 12):
    """Styled table: blue header row, alternating light-gray data rows."""
    tbl = slide.shapes.add_table(
        len(rows) + 1, len(headers), left, top, width, height
    ).table
    for c, h in enumerate(headers):
        _set_cell(tbl.cell(0, c), h,
                  size=hdr_size, bold=True, color=WHITE, fill=BLUE)
    for r, row in enumerate(rows):
        fill = LIGHT_GRAY if r % 2 == 1 else None
        for c, val in enumerate(row):
            _set_cell(tbl.cell(r + 1, c), val, size=body_size, fill=fill)
    return tbl


# ── Slide functions ────────────────────────────────────────────────────────

def slide_01_title(prs):
    """Slide 1: Title slide with thesis title and presenter info."""
    s = _blank(prs)
    txb = s.shapes.add_textbox(ML, Inches(1.40), CNTW, Inches(2.80))
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = (
        "Validating Population Stability Metrics for\n"
        "Dynamic Auto Insurance Pricing with Telematics Data"
    )
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(30)
    run.font.color.rgb = BLUE

    for label, value, top_in in [
        ("Presenter:", "LUN CHANPOLY", 4.40),
        ("Advisor:",   "HAS SOTHEA",  4.95),
        ("Date:",      "",            5.50),
    ]:
        _body(s, label, Inches(4.20), Inches(top_in), Inches(2.20), Inches(0.45),
              size=16, bold=True, color=BLUE, align=PP_ALIGN.RIGHT)
        _body(s, value, Inches(6.55), Inches(top_in), Inches(4.00), Inches(0.45),
              size=16, color=DARK)


def slide_02_agenda(prs):
    """Slide 2: Agenda slide with 6 chapters."""
    s = _blank(prs)
    _title(s, "Agenda")
    chapters = [
        ("Chapter 1", "Introduction — Why auto insurance telematics?"),
        ("Chapter 2", "Background — PSI, telematics features, prior work"),
        ("Chapter 3", "Methodology — Synthetic data & experiment design"),
        ("Chapter 4", "Results — EXP-001 through EXP-004"),
        ("Chapter 5", "Discussion — Framework & limitations"),
        ("Chapter 6", "Conclusion — Findings & future work"),
    ]
    top = Inches(1.50)
    for ch, desc in chapters:
        _body(s, ch,   ML,           top, Inches(1.80), Inches(0.50),
              size=16, bold=True, color=BLUE)
        _body(s, desc, Inches(2.55), top, Inches(9.80), Inches(0.50),
              size=16, color=DARK)
        top += Inches(0.80)


def slide_03_why_telematics(prs):
    """Slide 3: Why Auto Insurance Telematics? — Cambodia context & problem statement."""
    s = _blank(prs)
    _title(s, "Why Auto Insurance Telematics?")

    _body(s, "Cambodia Market Context",
          ML, Inches(1.35), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "4.8 million motorcycles — dense, under-insured fleet",
        "Claim frequency: 8–15% annually, highly seasonal",
        "Monsoon season (Jul–Sep): hard braking events spike 150–250%",
        "Emerging market: limited historical actuarial data",
    ], ML, Inches(1.85), CNTW, Inches(1.80), size=16)

    _body(s, "The Problem",
          ML, Inches(3.80), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Existing drift detection assumes static batch data",
        "Telematics pricing updates continuously — distributions shift every repricing cycle",
        "No established method for monitoring PSI stability under continuous repricing",
    ], ML, Inches(4.30), CNTW, Inches(1.60), size=16)


def slide_04_research_claim(prs):
    """Slide 4: Research Claim — thesis statement and scope."""
    s = _blank(prs)
    _title(s, "Research Claim")

    txb = s.shapes.add_textbox(Inches(1.20), Inches(1.40), Inches(10.93), Inches(1.60))
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = (
        "Single-metric PSI monitoring is insufficient\n"
        "for continuous dynamic auto insurance pricing."
    )
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = BLUE

    _body(s, "This thesis:",
          ML, Inches(3.30), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Identifies 3 specific PSI failure modes under dynamic pricing",
        "Demonstrates that temporal comparison strategy matters as much as metric choice",
        "Proposes a temporal multi-metric monitoring framework as the solution",
    ], ML, Inches(3.75), CNTW, Inches(1.40), size=16)

    _body(s, "Key Contributions",
          ML, Inches(5.40), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "First empirical validation of PSI under continuous repricing (telematics UBI)",
        "Quantified false-positive rate of consecutive-month monitoring: 71%",
        "Actionable 3-pillar framework ready for production dashboard integration",
    ], ML, Inches(5.85), CNTW, Inches(1.10), size=16)


def slide_05_psi_background(prs):
    """Slide 5: PSI Background — formula, thresholds, industry usage."""
    s = _blank(prs)
    _title(s, "Population Stability Index (PSI)")

    _body(s, "Definition",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _body(s, "PSI = Σ (Aᵢ – Eᵢ) × ln(Aᵢ / Eᵢ)",
          ML, Inches(1.75), CNTW, Inches(0.45), size=20, bold=True, color=DARK)
    _body(s, "Measures distributional shift between an Expected (reference) and Actual (current) population.",
          ML, Inches(2.25), CNTW, Inches(0.50), size=16, color=DARK)

    _body(s, "Industry Thresholds",
          ML, Inches(2.90), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _table(s,
           ["Level", "PSI Range", "Interpretation"],
           [
               ["GREEN", "< 0.10", "No significant shift — model stable"],
               ["AMBER", "0.10 – 0.25", "Moderate drift — investigate"],
               ["RED",   "> 0.25", "Significant drift — recalibrate"],
           ],
           ML, Inches(3.35), Inches(7.50), Inches(1.50),
           hdr_size=14, body_size=13)

    _body(s, "Limitation",
          Inches(8.80), Inches(2.90), Inches(4.00), Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Designed for static batch scoring (credit risk)",
        "Assumes a single, stable reference distribution",
        "No guidance for continuous repricing cycles",
    ], Inches(8.80), Inches(3.35), Inches(4.00), Inches(1.60), size=15)


def slide_06_telematics_features(prs):
    """Slide 6: Telematics Features — the 7 features used in experiments."""
    s = _blank(prs)
    _title(s, "Telematics Features")

    _body(s, "Dataset: Phnom Penh GPS pings → 1,500 trip-level records",
          ML, Inches(1.30), CNTW, Inches(0.40), size=16, bold=False, color=DARK)

    _table(s,
           ["Feature", "Description", "Relevance to Risk"],
           [
               ["speed_avg_kmh",       "Mean trip speed (km/h)",                "Higher speed → higher severity"],
               ["speed_p90_kmh",       "90th-percentile speed",                 "Captures extreme speeding events"],
               ["hard_braking_events", "Count of deceleration > 3 m/s²",        "Direct proxy for near-miss frequency"],
               ["harsh_jerk_events",   "Count of jerk > 2.5 m/s³",              "Aggressive driving style indicator"],
               ["jerk_rms",            "Root-mean-square of jerk profile",      "Smoothness of driving"],
               ["idle_pct",            "% of trip time spent idling",           "Route type signature (urban vs highway)"],
               ["vibration_avg",       "Average vertical acceleration (m/s²)",  "Road quality exposure"],
           ],
           ML, Inches(1.85), Inches(12.00), Inches(3.20),
           hdr_size=14, body_size=13)

    _body(s, "Premium Proxy Formula",
          ML, Inches(5.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _body(s, "risk_score = 0.35·clip(hard_braking/50) + 0.35·clip(jerk_rms/2) + 0.30·clip(speed_avg/20)",
          ML, Inches(5.75), CNTW, Inches(0.40), size=15, color=DARK)
    _body(s, "monthly_premium = $45 × (1 + 0.80 × risk_score)",
          ML, Inches(6.20), CNTW, Inches(0.40), size=15, bold=True, color=DARK)


def slide_07_prior_work(prs):
    """Slide 7: Prior Work & Research Gap."""
    s = _blank(prs)
    _title(s, "Prior Work & Research Gap")

    _body(s, "What PSI Literature Already Does Well",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Yurdakul & Naranjo (2020): Statistical properties of PSI; sample-size-dependent thresholds",
        "Siddiqi (2017): Binning strategies and threshold calibration (Intelligent Credit Scoring, Wiley)",
        "Multiple actuarial papers: PSI for model validation on annual renewals",
    ], ML, Inches(1.75), CNTW, Inches(1.50), size=16)

    _body(s, "The Gap — Why Existing Work Falls Short",
          ML, Inches(3.50), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "ALL existing work assumes a STATIC reference distribution — none address continuous repricing",
        "Telematics UBI reprices monthly: reference shifts every cycle, invalidating the baseline",
        "No published framework handles seasonality-induced drift (monsoon, holiday traffic)",
        "Silent failures: aggregate premium can stay GREEN while behavior changes catastrophically",
    ], ML, Inches(3.95), CNTW, Inches(1.90), size=16)


def slide_08_methodology(prs):
    """Slide 8: Methodology — four-experiment pipeline."""
    s = _blank(prs)
    _title(s, "Methodology — Four Experiment Pipeline")

    experiments = [
        ("EXP-001", "Baseline Validation", "Split same distribution → PSI must be 0.000 ± 0.010"),
        ("EXP-002", "Responsiveness",      "Inject 0%→50% drift → PSI must increase monotonically"),
        ("EXP-003", "Failure Modes",       "3 scenarios where single-metric PSI gives false negatives"),
        ("EXP-004", "Temporal Drift",      "Consecutive-month vs YoY vs rolling-window monitoring"),
    ]
    top = Inches(1.45)
    for num, name, desc in experiments:
        _body(s, num,   ML,           top, Inches(1.40), Inches(0.50),
              size=17, bold=True, color=BLUE)
        _body(s, name,  Inches(2.15), top, Inches(3.20), Inches(0.50),
              size=17, bold=True, color=DARK)
        _body(s, desc,  Inches(5.55), top, Inches(7.00), Inches(0.50),
              size=16, color=DARK)
        top += Inches(0.85)

    _body(s, "Design Principle",
          ML, Inches(5.20), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Each experiment is self-contained: loads CSV, computes PSI, asserts pass/fail",
        "Reproducible seeds (42, 1, 2, 3, 4) — identical results on every run",
        "Exit code 0 = PASS, 1 = FAIL — CI-ready",
    ], ML, Inches(5.65), CNTW, Inches(1.20), size=16)


def slide_09_data_generation(prs):
    """Slide 9: Synthetic Telematics Data Generation."""
    s = _blank(prs)
    _title(s, "Synthetic Telematics Data Generation")

    _body(s, "Phnom Penh Route Cache",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "30 origin-destination pairs across Phnom Penh (residential, commercial, highway)",
        "Google Maps Directions API → route polylines for 3 traffic snapshots",
        "~1.16 million GPS pings simulated at 1 Hz along real road geometry",
    ], ML, Inches(1.75), CNTW, Inches(1.40), size=16)

    _body(s, "Trip Feature Extraction",
          ML, Inches(3.40), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "1,500 trips aggregated to 7 telematics features per trip",
        "Baseline cohort (no distortion) + drift-injection cohorts for experiments",
        "All features percentile-binned (N=10) for PSI computation",
    ], ML, Inches(3.85), CNTW, Inches(1.40), size=16)

    _body(s, "Why Synthetic?",
          ML, Inches(5.40), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Cambodia has no publicly available telematics dataset",
        "Controlled distortion injection lets us know ground-truth shift magnitude",
        "Reproducible and auditable for thesis defense",
    ], ML, Inches(5.85), CNTW, Inches(1.20), size=16)


def slide_10_exp001_baseline(prs):
    """Slide 10: EXP-001 Baseline PSI Validation."""
    s = _blank(prs)
    _title(s, "EXP-001: Baseline PSI Validation")

    _body(s, "Setup",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "1,500 trips split into two random halves (seed=42)",
        "Both halves drawn from the SAME distribution — no drift injected",
        "Expected: PSI ≈ 0.000 for every feature",
    ], ML, Inches(1.75), CNTW, Inches(1.20), size=16)

    _table(s,
           ["Feature", "PSI", "Status"],
           [
               ["speed_avg_kmh",       "0.000000", "GREEN"],
               ["speed_p90_kmh",       "0.000000", "GREEN"],
               ["hard_braking_events", "0.000000", "GREEN"],
               ["harsh_jerk_events",   "0.000000", "GREEN"],
               ["jerk_rms",            "0.000000", "GREEN"],
               ["idle_pct",            "0.000000", "GREEN"],
               ["vibration_avg",       "0.000000", "GREEN"],
           ],
           ML, Inches(3.20), Inches(5.00), Inches(2.20),
           hdr_size=14, body_size=13)

    _body(s, "Why this matters",
          Inches(6.50), Inches(3.20), Inches(5.50), Inches(0.50),
          size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Validates that PSI = 0.000 when no drift exists — no systematic bias",
        "N=10 percentile bins are stable for n=750 samples per half",
        "Foundation confirmed: any drift detected in later experiments is REAL",
    ], Inches(6.50), Inches(3.80), Inches(5.50), Inches(1.60), size=15)


def slide_11_exp002_responsiveness(prs):
    """Slide 11: EXP-002 PSI Responsiveness / Monotonicity."""
    s = _blank(prs)
    _title(s, "EXP-002: PSI Responsiveness")

    _body(s, "Setup: aggressive-driving cohort injected at 0% → 50% fraction",
          ML, Inches(1.30), CNTW, Inches(0.40), size=16, color=DARK)

    _table(s,
           ["Drift %", "speed_avg", "hard_braking", "jerk_rms", "idle_pct", "Max PSI", "Status"],
           [
               ["0%",  "0.000", "0.000", "0.000", "0.000", "0.000", "GREEN"],
               ["10%", "0.008", "0.015", "0.012", "0.035", "0.035", "GREEN"],
               ["20%", "0.022", "0.042", "0.038", "0.092", "0.092", "GREEN"],
               ["30%", "0.045", "0.088", "0.078", "0.168", "0.168", "AMBER"],
               ["40%", "0.078", "0.145", "0.128", "0.245", "0.245", "AMBER"],
               ["50%", "0.118", "0.210", "0.185", "0.312", "0.312", "RED"],
           ],
           ML, Inches(1.85), Inches(6.80), Inches(2.40),
           hdr_size=12, body_size=11)

    # Chart
    s.shapes.add_picture(
        str(FIGURES_DIR / "fig_exp002_responsiveness.png"),
        Inches(7.70), Inches(1.85), Inches(5.00), Inches(2.90)
    )

    _body(s, "Key Findings",
          ML, Inches(4.50), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "PSI increases monotonically with drift fraction — PASS",
        "idle_pct is the most sensitive feature (captures route-type shift)",
        "GREEN → AMBER → RED transition occurs between 20% and 50% drift",
        "Sensitivity at 50%: 0.312 > 0.08 threshold — PASS",
    ], ML, Inches(4.95), CNTW, Inches(1.40), size=16)


def slide_12_failure_modes_overview(prs):
    """Slide 12: Overview of the 3 behavioral failure modes."""
    s = _blank(prs)
    _title(s, "Behavioral Failure Modes")

    _body(s, "Core Question: Can single-metric PSI on aggregate premium miss real behavioral shifts?",
          ML, Inches(1.30), CNTW, Inches(0.50), size=16, bold=False, color=DARK)

    _table(s,
           ["Mode", "Scenario", "Primary PSI", "Secondary Metric", "Secondary PSI"],
           [
               ["FM1", "Highway Migration (20%)",      "GREEN", "idle_pct (full pop)",      "AMBER (0.23)"],
               ["FM2", "Monsoon Surge (25% + discount)", "GREEN", "idle_pct (full pop)",      "RED (0.30)"],
               ["FM3", "Tail Risk Flip (bottom 5%)",    "GREEN", "cohort PSI (same drivers)", "RED (42.3)"],
           ],
           ML, Inches(2.00), Inches(12.00), Inches(1.70),
           hdr_size=13, body_size=12)

    # Chart
    s.shapes.add_picture(
        str(FIGURES_DIR / "fig_failure_modes.png"),
        Inches(3.00), Inches(3.90), Inches(7.50), Inches(3.20)
    )


def slide_13_fm1_highway(prs):
    """Slide 13: FM1 Highway Migration."""
    s = _blank(prs)
    _title(s, "FM1: Highway Migration")

    _body(s, "Scenario: 20% of trips shift from congested urban to highway routing",
          ML, Inches(1.30), CNTW, Inches(0.40), size=16, color=DARK)

    _body(s, "Behavioral Change",
          ML, Inches(1.85), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Speed +12 km/h, braking ×0.50, jerk ×0.55, idle ×0.05",
        "Premium barely changes because speed↑ offsets braking↓",
    ], ML, Inches(2.30), CNTW, Inches(0.90), size=16)

    _body(s, "Detection Results",
          ML, Inches(3.45), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _table(s,
           ["Metric", "PSI", "Status", "Interpretation"],
           [
               ["Premium (full population)", "0.04", "GREEN", "False negative — shift missed"],
               ["idle_pct (full population)", "0.23", "AMBER", "Route-type shift captured"],
           ],
           ML, Inches(3.90), Inches(9.50), Inches(1.20),
           hdr_size=14, body_size=13)

    _body(s, "Fix: Monitor idle_pct separately — it captures route-type shifts invisible to premium PSI.",
          ML, Inches(5.40), CNTW, Inches(0.60), size=16, bold=True, color=BLUE)


def slide_14_fm2_monsoon(prs):
    """Slide 14: FM2 Monsoon Ride-Share Surge."""
    s = _blank(prs)
    _title(s, "FM2: Monsoon Ride-Share Surge")

    _body(s, "Scenario: 25% of trips replaced by monsoon-season delivery riders",
          ML, Inches(1.30), CNTW, Inches(0.40), size=16, color=DARK)

    _body(s, "Behavioral Change",
          ML, Inches(1.85), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Hard braking ×2.0, jerk ×2.5, speed ×1.08, idle ×0.15",
        "Pricing model applies seasonal discount (0.76×) to monsoon cohort",
        "Discount absorbs premium increase — aggregate premium stays flat",
    ], ML, Inches(2.30), CNTW, Inches(1.20), size=16)

    _body(s, "Detection Results",
          ML, Inches(3.80), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _table(s,
           ["Metric", "PSI", "Status", "Interpretation"],
           [
               ["Season-adjusted premium (full pop)", "0.03", "GREEN", "Masked by actuarial discount"],
               ["idle_pct (full population)",         "0.30", "RED",   "Delivery-rider signature exposed"],
           ],
           ML, Inches(4.25), Inches(9.50), Inches(1.20),
           hdr_size=14, body_size=13)

    _body(s, "Fix: Monitor idle_pct — delivery-rider signature is absent from the premium formula.",
          ML, Inches(5.80), CNTW, Inches(0.60), size=16, bold=True, color=BLUE)


def slide_15_fm3_temporal(prs):
    """Slide 15: FM3 Tail Risk Flip + Temporal Drift preview."""
    s = _blank(prs)
    _title(s, "FM3: Tail Risk Flip & Temporal Drift")

    _body(s, "FM3 — Tail Risk Flip",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Bottom-5% safest braking cohort flips to 80th–95th percentile risk profile",
        "Full-population PSI stays GREEN because only ~5% of trips are affected",
        "Cohort PSI (same 75 drivers, before vs after): PSI = 42.3 → RED",
    ], ML, Inches(1.75), CNTW, Inches(1.20), size=16)

    _body(s, "Temporal Drift Preview (EXP-004)",
          ML, Inches(3.20), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Two-year simulation: Year 1 severe monsoon → Year 2 attenuated monsoon",
        "Consecutive-month PSI at n=125: 71% false-positive rate in dry season",
        "Genuine monsoon onset (Jun→Jul) is LOST in sampling noise",
    ], ML, Inches(3.65), CNTW, Inches(1.20), size=16)

    _body(s, "Key Insight",
          ML, Inches(5.10), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _body(s, "When and how you compare matters as much as what metric you use.",
          ML, Inches(5.55), CNTW, Inches(0.50), size=18, bold=True, color=DARK)


def slide_16_exp004_results(prs):
    """Slide 16: EXP-004 Temporal Drift Results."""
    s = _blank(prs)
    _title(s, "EXP-004: Temporal Drift Detection")

    _body(s, "Problem: Consecutive-month PSI is operationally useless for seasonal products",
          ML, Inches(1.30), CNTW, Inches(0.40), size=16, color=DARK)

    # Chart on left
    s.shapes.add_picture(
        str(FIGURES_DIR / "fig_exp004_temporal.png"),
        ML, Inches(1.85), Inches(6.80), Inches(3.35)
    )

    # Results table on right
    _table(s,
           ["Detection Method", "Finding", "Result"],
           [
               ["Consecutive-month PSI",      "71% false-positive rate",        "FAIL"],
               ["YoY PSI — Jul Y2 vs Y1",     "PSI = 3.007  RED",               "PASS"],
               ["Rolling 3-month window",     "PSI = 0.731  RED",               "PASS"],
           ],
           Inches(7.60), Inches(1.85), Inches(5.00), Inches(1.50),
           hdr_size=13, body_size=12)

    _body(s, "Recommended Fixes",
          Inches(7.60), Inches(3.60), Inches(5.00), Inches(0.40),
          size=16, bold=True, color=BLUE)
    _bullets(s, [
        "Compare each monsoon month against SAME month last year (YoY)",
        "Pool Jul–Sep into rolling window; compare window-to-window YoY",
        "Both cut through noise AND detect genuine regime shifts",
    ], Inches(7.60), Inches(4.05), Inches(5.00), Inches(1.30), size=14)


def slide_17_framework(prs):
    """Slide 17: Proposed Temporal Multi-Metric Monitoring Framework."""
    s = _blank(prs)
    _title(s, "Proposed Monitoring Framework")

    # Framework diagram
    s.shapes.add_picture(
        str(FIGURES_DIR / "fig_framework.png"),
        Inches(1.50), Inches(1.35), Inches(10.50), Inches(3.00)
    )

    _body(s, "Operational Integration",
          ML, Inches(4.60), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "GREEN → continue current pricing; AMBER → trigger feature-level deep-dive",
        "RED → freeze repricing + alert actuarial team + initiate model recalibration",
        "Dashboard: 3 traffic lights (premium, behavior, cohort) instead of 1",
    ], ML, Inches(5.05), CNTW, Inches(1.20), size=16)


def slide_18_discussion(prs):
    """Slide 18: Discussion & Limitations."""
    s = _blank(prs)
    _title(s, "Discussion & Limitations")

    _body(s, "Limitations",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Synthetic data — results need validation on real Cambodian telematics",
        "Single city (Phnom Penh) — rural highway behavior may differ",
        "No real claims data — link between telematics shift and actual loss cost is assumed",
        "Premium formula is a GLM-proxy, not a trained production model",
    ], ML, Inches(1.75), CNTW, Inches(1.70), size=16)

    _body(s, "Practical Implications",
          ML, Inches(3.70), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Insurers currently using consecutive-month PSI may be ignoring 71% of false alarms",
        "Season-aware monitoring can be retrofitted into existing actuarial workflows",
        "Framework applies beyond auto: health UBI, crop insurance, flood-index products",
    ], ML, Inches(4.15), CNTW, Inches(1.30), size=16)


def slide_19_conclusion(prs):
    """Slide 19: Conclusion & Future Work."""
    s = _blank(prs)
    _title(s, "Conclusion & Future Work")

    _body(s, "Key Findings",
          ML, Inches(1.30), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "PSI works for static batch validation (EXP-001 baseline = 0.000 all GREEN)",
        "PSI responds monotonically to known drift (EXP-002 GREEN→AMBER→RED at 0%→50%)",
        "Single-metric PSI fails under 3 distinct dynamic-pricing failure modes (EXP-003)",
        "Temporal comparison strategy matters as much as metric choice (EXP-004 71% FP rate)",
    ], ML, Inches(1.75), CNTW, Inches(1.70), size=16)

    _body(s, "Future Work",
          ML, Inches(3.70), CNTW, Inches(0.40), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Validate framework on real Cambodian telematics + claims data",
        "Build production dashboard integrating the 3-pillar framework",
        "Extend to health/life insurance dynamic pricing (Vietnam case study)",
        "Explore adaptive binning and KL-divergence as PSI alternatives",
    ], ML, Inches(4.15), CNTW, Inches(1.30), size=16)


def slide_20_thank_you(prs):
    """Slide 20: Thank You / Q&A."""
    s = _blank(prs)
    txb = s.shapes.add_textbox(ML, Inches(2.20), CNTW, Inches(1.60))
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Thank You"
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(40)
    run.font.color.rgb = BLUE

    _body(s, "Questions & Discussion",
          ML, Inches(4.00), CNTW, Inches(0.60),
          size=22, bold=True, color=DARK, align=PP_ALIGN.CENTER)

    _body(s, "Presenter: LUN CHANPOLY",
          ML, Inches(5.00), CNTW, Inches(0.45),
          size=16, color=DARK, align=PP_ALIGN.CENTER)
    _body(s, "Advisor:  HAS SOTHEA",
          ML, Inches(5.50), CNTW, Inches(0.45),
          size=16, color=DARK, align=PP_ALIGN.CENTER)
    _body(s, "Email:    chanpoly3@gmail.com",
          ML, Inches(6.00), CNTW, Inches(0.45),
          size=16, color=DARK, align=PP_ALIGN.CENTER)


# ── Build entry point ──────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # Generate charts first so pictures exist before slides are built
    _generate_charts()

    slide_01_title(prs)
    slide_02_agenda(prs)
    slide_03_why_telematics(prs)
    slide_04_research_claim(prs)
    slide_05_psi_background(prs)
    slide_06_telematics_features(prs)
    slide_07_prior_work(prs)
    slide_08_methodology(prs)
    slide_09_data_generation(prs)
    slide_10_exp001_baseline(prs)
    slide_11_exp002_responsiveness(prs)
    slide_12_failure_modes_overview(prs)
    slide_13_fm1_highway(prs)
    slide_14_fm2_monsoon(prs)
    slide_15_fm3_temporal(prs)
    slide_16_exp004_results(prs)
    slide_17_framework(prs)
    slide_18_discussion(prs)
    slide_19_conclusion(prs)
    slide_20_thank_you(prs)

    prs.save(OUT)
    print(f"Saved {len(prs.slides)} slides -> {OUT}")


if __name__ == "__main__":
    build()
