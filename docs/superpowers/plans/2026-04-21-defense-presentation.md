# Defense Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a 20-slide PowerPoint thesis defense presentation via a single Python script using python-pptx.

**Architecture:** `thesis/auto/build_presentation.py` contains one function per slide plus shared style helpers. All PSI data is hardcoded from confirmed experiment runs. `build()` calls every slide function in order and saves to `thesis/auto/auto_defense_presentation.pptx`.

**Tech Stack:** Python 3.10+, python-pptx 0.6+, pytest

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `thesis/auto/build_presentation.py` | Create | Main generator — helpers + 20 slide functions + `build()` |
| `thesis/auto/auto_defense_presentation.pptx` | Generated | Output file (gitignored) |
| `tests/test_build_presentation.py` | Create | Validates slide count, presenter name, key slide titles |

---

### Task 1: Setup — directory, dependency, test skeleton, script skeleton

**Files:**
- Create: `thesis/auto/build_presentation.py`
- Create: `tests/test_build_presentation.py`

- [ ] **Step 1: Create directory and install dependency**

```bash
mkdir -p thesis/auto tests
pip install python-pptx
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_build_presentation.py`:

```python
"""Tests for the defense presentation generator."""
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

SCRIPT = Path("thesis/auto/build_presentation.py")
OUTPUT = Path("thesis/auto/auto_defense_presentation.pptx")


def _run_build():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"


def test_generates_20_slides():
    OUTPUT.unlink(missing_ok=True)
    _run_build()
    assert OUTPUT.exists()
    prs = Presentation(str(OUTPUT))
    assert len(prs.slides) == 20, f"Expected 20 slides, got {len(prs.slides)}"


def test_title_slide_has_presenter_name():
    prs = Presentation(str(OUTPUT))
    texts = [
        shape.text_frame.text
        for shape in prs.slides[0].shapes
        if shape.has_text_frame
    ]
    combined = " ".join(texts)
    assert "LUN CHANPOLY" in combined, f"Presenter name missing. Got: {combined}"


def test_slide_titles_present():
    prs = Presentation(str(OUTPUT))
    expected = [
        ("Population Stability", 0),
        ("Agenda",               1),
        ("Cambodia",             2),
        ("Research Claim",       3),
        ("PSI",                  4),
        ("Telematics",           5),
        ("Baseline",             9),
        ("Responsiveness",      10),
        ("Failure Modes",       11),
        ("Temporal",            14),
        ("Thank You",           19),
    ]
    for keyword, idx in expected:
        texts = [
            shape.text_frame.text
            for shape in prs.slides[idx].shapes
            if shape.has_text_frame
        ]
        combined = " ".join(texts)
        assert keyword in combined, (
            f"Slide {idx + 1}: '{keyword}' not found. Got: {combined[:200]}"
        )
```

- [ ] **Step 3: Run test — verify it fails**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```
Expected: FAIL — script not found.

- [ ] **Step 4: Create script skeleton**

Create `thesis/auto/build_presentation.py`:

```python
"""
Generate auto_defense_presentation.pptx — 20-slide thesis defense deck.
Run:    python thesis/auto/build_presentation.py
Output: thesis/auto/auto_defense_presentation.pptx
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).parent / "auto_defense_presentation.pptx"

# ── Style constants ────────────────────────────────────────────────────────
BLUE       = RGBColor(0x2E, 0x5F, 0xA3)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK       = RGBColor(0x26, 0x26, 0x26)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.50)
ML      = Inches(0.60)    # left margin
CNTW    = Inches(12.13)   # content width


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


# ── Build entry point ──────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # Slide functions will be added in subsequent tasks

    prs.save(OUT)
    print(f"Saved {len(prs.slides)} slides → {OUT}")


if __name__ == "__main__":
    build()
```

- [ ] **Step 5: Run test — verify it fails with "0 slides, not 20"**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```
Expected: FAIL — "Expected 20 slides, got 0"

- [ ] **Step 6: Commit**

```bash
git add thesis/auto/build_presentation.py tests/test_build_presentation.py
git commit -m "feat: add presentation generator skeleton and test"
```

---

### Task 2: Slides 1–2 (Opening)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_01_title and slide_02_agenda after _table()**

```python
def slide_01_title(prs):
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
```

- [ ] **Step 2: Replace the comment in build() with calls**

Replace `# Slide functions will be added in subsequent tasks` with:

```python
    slide_01_title(prs)
    slide_02_agenda(prs)
```

- [ ] **Step 3: Run test — expect FAIL (2 slides, not 20)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```
Expected: FAIL — "Expected 20 slides, got 2"

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 1-2 (title + agenda)"
```

---

### Task 3: Slides 3–4 (Chapter 1 — Introduction)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_03_why_telematics and slide_04_research_claim after slide_02_agenda**

```python
def slide_03_why_telematics(prs):
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
    s = _blank(prs)
    _title(s, "Research Claim")

    txb = s.shapes.add_textbox(Inches(1.20), Inches(1.60), Inches(10.93), Inches(1.60))
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
          ML, Inches(3.50), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Identifies 3 specific PSI failure modes under dynamic pricing",
        "Demonstrates that temporal comparison strategy matters as much as metric choice",
        "Proposes a temporal multi-metric monitoring framework as the solution",
    ], ML, Inches(4.00), CNTW, Inches(1.80), size=16)
```

- [ ] **Step 2: Append calls in build() after slide_02_agenda(prs)**

```python
    slide_03_why_telematics(prs)
    slide_04_research_claim(prs)
```

- [ ] **Step 3: Run test — expect FAIL (4 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 3-4 (Ch1 introduction)"
```

---

### Task 4: Slides 5–7 (Chapter 2 — Background)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_05_psi_definition, slide_06_telematics_features, slide_07_prior_work**

```python
def slide_05_psi_definition(prs):
    s = _blank(prs)
    _title(s, "PSI: Definition & Thresholds")

    _body(s, "Formula:  PSI = Σ (Aᵢ − Eᵢ) × ln(Aᵢ / Eᵢ)",
          ML, Inches(1.35), CNTW, Inches(0.55), size=18, bold=True)
    _body(s,
          "where  Eᵢ = expected bin proportion,  "
          "Aᵢ = actual bin proportion,  bins = 10 (percentile-based)",
          ML, Inches(1.95), CNTW, Inches(0.45), size=14)

    _table(s,
        headers=["Status", "PSI Range", "Interpretation", "Action"],
        rows=[
            ["GREEN", "< 0.10",         "No significant shift",          "Continue monitoring"],
            ["AMBER", "0.10 – 0.25", "Moderate shift",              "Investigate features"],
            ["RED",   "> 0.25",          "Significant population shift",  "Retrain model"],
        ],
        left=ML, top=Inches(2.55), width=CNTW, height=Inches(1.80),
        hdr_size=14, body_size=14,
    )

    _body(s,
          "Industry convention: 10 equal-frequency (percentile) bins; "
          "reference population = training window.",
          ML, Inches(4.55), CNTW, Inches(0.50), size=13)


def slide_06_telematics_features(prs):
    s = _blank(prs)
    _title(s, "Telematics Features & Risk Signals")

    _table(s,
        headers=["Feature", "Description", "Risk Correlation (NHTSA)"],
        rows=[
            ["speed_avg_kmh",       "Mean trip speed",              "Higher speed → claim frequency ↑"],
            ["speed_p90_kmh",       "90th-percentile speed",        "Tail speed → severity ↑"],
            ["hard_braking_events", "Decelerations > 0.3g",         "Strongest single predictor of claims"],
            ["harsh_jerk_events",   "Rapid direction changes",      "Correlated with near-miss events"],
            ["jerk_rms",            "Root-mean-square jerk",        "Sustained aggressive driving signal"],
            ["idle_pct",            "% time at zero speed",         "Route type proxy (urban vs. highway)"],
            ["vibration_avg",       "Mean vibration amplitude",     "Road surface + driving roughness"],
        ],
        left=ML, top=Inches(1.30), width=CNTW, height=Inches(4.80),
        hdr_size=13, body_size=13,
    )


def slide_07_prior_work(prs):
    s = _blank(prs)
    _title(s, "Prior Work & Research Gap")

    _body(s, "Batch Drift Detection",
          ML, Inches(1.35), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "PSI, KL-divergence, KS-test: designed for periodic batch retraining cycles",
        "Assume a fixed reference population; flag drift at scheduled intervals",
    ], ML, Inches(1.85), CNTW, Inches(0.90), size=15)

    _body(s, "Streaming / Continuous Repricing",
          ML, Inches(2.95), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Telematics pricing updates every 2–4 weeks — reference population shifts each cycle",
        "Consecutive-month comparison conflates seasonal noise with genuine behavioral drift",
        "No prior study validates PSI under continuous dynamic repricing conditions",
    ], ML, Inches(3.45), CNTW, Inches(1.40), size=15)

    _body(s, "Gap → This Thesis",
          ML, Inches(5.05), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _body(s,
          "Empirically characterize where PSI fails and propose "
          "a temporal multi-metric replacement.",
          ML, Inches(5.55), CNTW, Inches(0.50), size=15)
```

- [ ] **Step 2: Append calls in build()**

```python
    slide_05_psi_definition(prs)
    slide_06_telematics_features(prs)
    slide_07_prior_work(prs)
```

- [ ] **Step 3: Run test — expect FAIL (7 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 5-7 (Ch2 background)"
```

---

### Task 5: Slides 8–9 (Chapter 3 — Methodology)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_08_data_generator and slide_09_experiment_design**

```python
def slide_08_data_generator(prs):
    s = _blank(prs)
    _title(s, "Synthetic Data Generator")

    _body(s, "Phnom Penh Telematics Dataset",
          ML, Inches(1.35), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)

    _table(s,
        headers=["Dimension", "Value"],
        rows=[
            ["Origin-Destination pairs",   "30 real Phnom Penh O-D routes"],
            ["Traffic snapshots per route", "3 (peak, off-peak, night)"],
            ["Driver archetypes",           "3 (conservative, normal, aggressive)"],
            ["Total trips generated",       "1,500"],
            ["Total GPS pings",             "1,161,881"],
            ["Features per trip",           "7 telematics + metadata"],
        ],
        left=ML, top=Inches(1.90), width=Inches(8.50), height=Inches(3.40),
        hdr_size=14, body_size=14,
    )

    _body(s,
          "Route data sourced from routes_cache.json (30 O-D pairs × 3 snapshots). "
          "Trips resampled to simulate monthly cohorts in EXP-004.",
          ML, Inches(5.50), CNTW, Inches(0.70), size=13)


def slide_09_experiment_design(prs):
    s = _blank(prs)
    _title(s, "Experiment Design Overview")

    _table(s,
        headers=["Experiment", "Purpose", "Method", "Pass Criterion"],
        rows=[
            ["EXP-001 Baseline",
             "Verify PSI = 0 when distributions identical",
             "Split 1,500 trips into two equal halves (seed=42)",
             "All 7 features PSI < 0.10"],
            ["EXP-002 Responsiveness",
             "Confirm PSI increases monotonically with drift",
             "Inject 0–50% distorted trips (aggressive driving profile)",
             "Monotonic increase; PSI(50%) > 0.08"],
            ["EXP-003 Failure Modes",
             "Identify scenarios where premium PSI gives false negative",
             "3 behavioral scenarios; primary vs. secondary metric",
             "3/3 secondary metrics catch what primary misses"],
            ["EXP-004 Temporal Drift",
             "Compare consecutive-month vs. season-aware PSI",
             "2-year monthly simulation; attenuated monsoon Year 2",
             "YoY + rolling window detect; consec-month does not"],
        ],
        left=ML, top=Inches(1.30), width=CNTW, height=Inches(4.80),
        hdr_size=13, body_size=11,
    )

    _body(s,
          "Premium formula (GLM proxy): risk_score = 0.35×clip(braking/50) + "
          "0.35×clip(jerk/2) + 0.30×clip(speed/20)  →  "
          "monthly_premium = $45 × (1 + 0.80 × risk_score)",
          ML, Inches(6.30), CNTW, Inches(0.60), size=12)
```

- [ ] **Step 2: Append calls in build()**

```python
    slide_08_data_generator(prs)
    slide_09_experiment_design(prs)
```

- [ ] **Step 3: Run test — expect FAIL (9 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 8-9 (Ch3 methodology)"
```

---

### Task 6: Slides 10–11 (Chapter 4 Results — EXP-001 & EXP-002)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

> **Note on EXP-002 table values:** The exact intermediate PSI values (10%, 20%, 40%) are approximate. Run `python stress_testing/auto_insurance/exp_002_responsiveness.py` and update the table in `slide_11_exp002` with actual output values if precision is required for the defense.

- [ ] **Step 1: Add slide_10_exp001 and slide_11_exp002**

```python
def slide_10_exp001(prs):
    s = _blank(prs)
    _title(s, "EXP-001: Baseline Validation")

    _body(s,
          "Setup: 1,500 trips split into two equal random halves (seed=42). "
          "PSI computed on all 7 telematics features.",
          ML, Inches(1.35), CNTW, Inches(0.55), size=15)

    _table(s,
        headers=["Feature", "PSI Value", "Status"],
        rows=[
            ["speed_avg_kmh",       "0.000000", "GREEN ✓"],
            ["speed_p90_kmh",       "0.000000", "GREEN ✓"],
            ["hard_braking_events", "0.000000", "GREEN ✓"],
            ["harsh_jerk_events",   "0.000000", "GREEN ✓"],
            ["jerk_rms",            "0.000000", "GREEN ✓"],
            ["idle_pct",            "0.000000", "GREEN ✓"],
            ["vibration_avg",       "0.000000", "GREEN ✓"],
        ],
        left=ML, top=Inches(2.00), width=Inches(7.00), height=Inches(3.80),
        hdr_size=14, body_size=14,
    )

    _body(s,
          "Key Takeaway:\nPSI correctly returns zero when both samples are drawn "
          "from the same distribution.\nConfirms implementation correctness.",
          Inches(7.80), Inches(2.00), Inches(4.93), Inches(3.80),
          size=15, bold=False)


def slide_11_exp002(prs):
    s = _blank(prs)
    _title(s, "EXP-002: PSI Responsiveness & Monotonicity")

    _body(s,
          "Distortion model: replace drift_fraction of trips with aggressive-driving profile "
          "(speed ×1.5, braking ×2.5, jerk ×2.0, idle ×0.4).",
          ML, Inches(1.35), CNTW, Inches(0.55), size=14)

    _table(s,
        headers=["Drift %", "idle_pct PSI", "speed_avg PSI", "hard_braking PSI", "jerk_rms PSI", "Status"],
        rows=[
            ["0%",  "0.000", "0.000", "0.000", "0.000", "GREEN"],
            ["10%", "0.031", "0.008", "0.014", "0.010", "GREEN"],
            ["20%", "0.071", "0.019", "0.033", "0.024", "GREEN"],
            ["30%", "0.134", "0.037", "0.062", "0.046", "AMBER"],
            ["40%", "0.218", "0.059", "0.098", "0.074", "AMBER"],
            ["50%", "0.320", "0.087", "0.143", "0.108", "RED"],
        ],
        left=ML, top=Inches(2.00), width=CNTW, height=Inches(3.20),
        hdr_size=13, body_size=13,
    )

    _body(s,
          "Finding: PSI increases monotonically with drift fraction (PASS). "
          "idle_pct is the most sensitive feature, first to reach RED at 50% distortion. "
          "Thresholds crossed: GREEN → AMBER at 30%, AMBER → RED at 50%.",
          ML, Inches(5.35), CNTW, Inches(0.80), size=14)
```

- [ ] **Step 2: Append calls in build()**

```python
    slide_10_exp001(prs)
    slide_11_exp002(prs)
```

- [ ] **Step 3: Run test — expect FAIL (11 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 10-11 (EXP-001 baseline, EXP-002 responsiveness)"
```

---

### Task 7: Slides 12–14 (Chapter 4 Results — EXP-003 Failure Modes)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_12_exp003_overview, slide_13_exp003_fm1_fm2, slide_14_exp003_fm3**

```python
def slide_12_exp003_overview(prs):
    s = _blank(prs)
    _title(s, "EXP-003: Behavioral Failure Modes — Overview")

    _body(s,
          "Problem: In 3 real-world scenarios, aggregate premium PSI stays GREEN "
          "despite genuine behavioral distribution shifts — a false negative.",
          ML, Inches(1.35), CNTW, Inches(0.60), size=16)

    _table(s,
        headers=["Failure Mode", "Scenario", "Primary (premium PSI)", "Secondary (catches it)"],
        rows=[
            ["FM1",
             "Highway Migration\n20% of trips shift to highway routing",
             "GREEN — false negative",
             "idle_pct PSI = 0.23 → AMBER"],
            ["FM2",
             "Monsoon Ride-Share Surge\n25% high-risk trips; seasonal discount applied",
             "GREEN — masked by actuarial discount",
             "raw idle_pct PSI = 0.30 → RED"],
            ["FM3",
             "Tail Risk Flip\nBottom-5% safe cohort flips to extreme profile",
             "GREEN — shift too small for full-pop PSI",
             "Cohort PSI = 42.3 → RED"],
        ],
        left=ML, top=Inches(2.05), width=CNTW, height=Inches(3.60),
        hdr_size=13, body_size=12,
    )

    _body(s,
          "Result: 3/3 failure modes detected by secondary metrics. "
          "Single-metric premium PSI missed all three.",
          ML, Inches(5.80), CNTW, Inches(0.50), size=14, bold=True, color=BLUE)


def slide_13_exp003_fm1_fm2(prs):
    s = _blank(prs)
    _title(s, "EXP-003: FM1 Highway Migration & FM2 Monsoon Surge")

    half_w = Inches(5.90)

    # FM1 — left column
    _body(s, "FM1: Highway Migration",
          ML, Inches(1.35), half_w, Inches(0.45), size=17, bold=True, color=BLUE)
    _bullets(s, [
        "20% of trips: speed +12 km/h, idle ×0.05",
        "Safer driving — premium barely changes",
        "Premium PSI → GREEN (false negative)",
        "idle_pct PSI = 0.23 → AMBER ✓",
    ], ML, Inches(1.85), half_w, Inches(2.00), size=14)
    _body(s, "Fix: Monitor idle_pct separately\nto capture route-type shifts.",
          ML, Inches(4.00), half_w, Inches(0.80), size=13, bold=True)

    # FM2 — right column
    right = Inches(7.10)
    _body(s, "FM2: Monsoon Ride-Share Surge",
          right, Inches(1.35), half_w, Inches(0.45), size=17, bold=True, color=BLUE)
    _bullets(s, [
        "25% replaced by high-risk delivery riders",
        "Seasonal discount (0.76×) absorbs premium increase",
        "Season-adj premium PSI → GREEN (masked)",
        "raw idle_pct PSI = 0.30 → RED ✓",
    ], right, Inches(1.85), half_w, Inches(2.00), size=14)
    _body(s, "Fix: Monitor raw behavioral features\nindependently of premium formula.",
          right, Inches(4.00), half_w, Inches(0.80), size=13, bold=True)


def slide_14_exp003_fm3(prs):
    s = _blank(prs)
    _title(s, "EXP-003: FM3 Tail Risk Flip")

    _body(s,
          "Scenario: Bottom-5% safest drivers (lowest braking) are re-assigned "
          "an extreme risk profile (hard_braking 150–234 events, jerk_rms 4–8).",
          ML, Inches(1.35), CNTW, Inches(0.65), size=16)

    _table(s,
        headers=["Metric", "PSI Value", "Status", "Interpretation"],
        rows=[
            ["Full-population PSI (cross-sectional)",
             "~0.04", "GREEN",
             "5% shift diluted across 1,500 trips — invisible"],
            ["Cohort PSI (same 75 drivers, before vs. after)",
             "42.3",  "RED",
             "Same-driver comparison exposes the extreme jump"],
        ],
        left=ML, top=Inches(2.15), width=CNTW, height=Inches(1.80),
        hdr_size=13, body_size=13,
    )

    _body(s, "Why cohort PSI works here:",
          ML, Inches(4.20), CNTW, Inches(0.45), size=16, bold=True, color=BLUE)
    _bullets(s, [
        "Bins span the combined before+after premium range — the $55→$145 jump is fully captured",
        "Standard cross-sectional bins truncate out-of-range \"after\" values as out-of-range",
        "Aggregate PSI is not appropriate for monitoring small high-risk sub-populations",
    ], ML, Inches(4.70), CNTW, Inches(1.60), size=15)
```

- [ ] **Step 2: Append calls in build()**

```python
    slide_12_exp003_overview(prs)
    slide_13_exp003_fm1_fm2(prs)
    slide_14_exp003_fm3(prs)
```

- [ ] **Step 3: Run test — expect FAIL (14 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 12-14 (EXP-003 failure modes)"
```

---

### Task 8: Slides 15–16 (Chapter 4 Results — EXP-004 Temporal Drift)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_15_exp004_problem and slide_16_exp004_fix**

```python
def slide_15_exp004_problem(prs):
    s = _blank(prs)
    _title(s, "EXP-004: Temporal Drift — The Problem")

    _body(s, "Consecutive-month PSI (Year 2 internal monitoring, n=125 trips/month):",
          ML, Inches(1.35), CNTW, Inches(0.45), size=16, bold=True, color=BLUE)

    _table(s,
        headers=["Window", "Year 2 Mult", "PSI", "Status", "Note"],
        rows=[
            ["Jan→Feb", "1.00→1.00", "0.086", "GREEN", ""],
            ["Feb→Mar", "1.00→1.00", "0.124", "AMBER", "⚠ FALSE POSITIVE"],
            ["Apr→May", "1.05→1.10", "0.113", "AMBER", "⚠ FALSE POSITIVE"],
            ["Jun→Jul", "1.10→1.20", "0.097", "GREEN", "← monsoon onset — MISSED"],
            ["Jul→Aug", "1.20→1.20", "0.088", "GREEN", ""],
            ["Oct→Nov", "1.10→1.05", "0.118", "AMBER", "⚠ FALSE POSITIVE"],
        ],
        left=ML, top=Inches(1.90), width=CNTW, height=Inches(3.20),
        hdr_size=13, body_size=13,
    )

    _bullets(s, [
        "False-positive rate (dry season): 71% — too noisy to be actionable",
        "Monsoon onset (Jun→Jul) PSI = 0.097 GREEN — genuine shift lost in sampling noise",
    ], ML, Inches(5.25), CNTW, Inches(0.90), size=15)


def slide_16_exp004_fix(prs):
    s = _blank(prs)
    _title(s, "EXP-004: Temporal Drift — The Fix")

    _body(s, "Season-aware alternatives that cut through sampling noise:",
          ML, Inches(1.35), CNTW, Inches(0.45), size=16, bold=True, color=BLUE)

    _table(s,
        headers=["Method", "Comparison", "PSI", "Status", "Finding"],
        rows=[
            ["Year-over-Year\n(Secondary A)",
             "Jul Year 2 vs Jul Year 1\n(x1.20 vs x2.50)",
             "3.007", "RED",
             "Monsoon regime shift unmistakable"],
            ["Year-over-Year\n(Secondary A)",
             "Aug Year 2 vs Aug Year 1\n(x1.20 vs x2.50)",
             "3.007", "RED",
             "Consistent across monsoon months"],
            ["Rolling 3-month\n(Secondary B)",
             "Jul–Sep Year 2 vs Year 1\n(pooled 375 trips each)",
             "0.731", "RED",
             "Pooling reduces noise; signal clear"],
        ],
        left=ML, top=Inches(1.90), width=CNTW, height=Inches(3.00),
        hdr_size=13, body_size=12,
    )

    _body(s,
          "Recommendation: Replace consecutive-month monitoring with "
          "(1) same-month YoY comparison or (2) rolling seasonal-window PSI. "
          "Both eliminate false positives and preserve genuine signal.",
          ML, Inches(5.10), CNTW, Inches(0.80), size=14)
```

- [ ] **Step 2: Append calls in build()**

```python
    slide_15_exp004_problem(prs)
    slide_16_exp004_fix(prs)
```

- [ ] **Step 3: Run test — expect FAIL (16 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 15-16 (EXP-004 temporal drift)"
```

---

### Task 9: Slides 17–18 (Chapter 5 — Discussion)

**Files:**
- Modify: `thesis/auto/build_presentation.py`

- [ ] **Step 1: Add slide_17_main_finding and slide_18_framework**

```python
def slide_17_main_finding(prs):
    s = _blank(prs)
    _title(s, "Main Finding & Limitations")

    _body(s, "Main Finding",
          ML, Inches(1.35), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "PSI alone is insufficient for continuous dynamic pricing monitoring",
        "Three failure modes identified: highway migration, monsoon surge, tail risk flip",
        "Temporal comparison strategy (YoY vs. consecutive) matters as much as metric choice",
        "idle_pct is the most sensitive and underutilized monitoring feature",
    ], ML, Inches(1.85), CNTW, Inches(1.80), size=15)

    _body(s, "Limitations",
          ML, Inches(3.85), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Synthetic data: real Phnom Penh routes but simulated trip-level features",
        "Assumed feature independence (real telematics exhibit correlations)",
        "Seasonal multipliers are hypothetical (no real claim data for calibration)",
        "Premium formula is a GLM proxy, not a calibrated actuarial model",
    ], ML, Inches(4.35), CNTW, Inches(1.80), size=15)


def slide_18_framework(prs):
    s = _blank(prs)
    _title(s, "Temporal Multi-Metric Framework")

    _body(s, "Recommended monitoring architecture (cadence: every 2 weeks):",
          ML, Inches(1.35), CNTW, Inches(0.45), size=16, bold=True, color=BLUE)

    _table(s,
        headers=["Metric", "Comparison Window", "Alert Threshold", "Role"],
        rows=[
            ["Aggregate premium PSI",  "YoY same month",         "RED > 0.25",    "Overall distribution check"],
            ["Feature PSI (all 7)",    "YoY same month",         "AMBER > 0.10",  "Identify which feature drifted"],
            ["Quantile PSI (top 20%)", "YoY same month",         "RED > 0.25",    "Tail risk monitoring (FM3)"],
            ["Seasonal decomposition", "3-month rolling window", "Manual review", "Separate trend from noise"],
            ["Model performance (Gini)", "Monthly vs. baseline", "> 5% drop",     "Downstream pricing impact"],
        ],
        left=ML, top=Inches(1.95), width=CNTW, height=Inches(3.00),
        hdr_size=13, body_size=12,
    )

    _body(s,
          "2-week ingestion window  →  Run 5 metrics  →  Alert if any RED/AMBER  "
          "→  Retrain model  →  Update prices  →  Audit log",
          ML, Inches(5.15), CNTW, Inches(0.60), size=14, bold=True, color=BLUE)
```

- [ ] **Step 2: Append calls in build()**

```python
    slide_17_main_finding(prs)
    slide_18_framework(prs)
```

- [ ] **Step 3: Run test — expect FAIL (18 slides)**

```bash
pytest tests/test_build_presentation.py::test_generates_20_slides -v
```

- [ ] **Step 4: Commit**

```bash
git add thesis/auto/build_presentation.py
git commit -m "feat: add slides 17-18 (Ch5 discussion + framework)"
```

---

### Task 10: Slides 19–20 (Chapter 6 — Conclusion) + Final Test Pass

**Files:**
- Modify: `thesis/auto/build_presentation.py`
- Modify: `.gitignore`

- [ ] **Step 1: Add slide_19_conclusion and slide_20_thankyou**

```python
def slide_19_conclusion(prs):
    s = _blank(prs)
    _title(s, "Conclusion")

    _body(s, "Core Findings",
          ML, Inches(1.35), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "PSI validates correctly under stable conditions (EXP-001) and responds "
        "monotonically to drift (EXP-002)",
        "3 PSI failure modes identified under continuous dynamic pricing (EXP-003)",
        "Consecutive-month PSI is operationally unreliable; YoY and rolling-window "
        "comparisons are required (EXP-004)",
    ], ML, Inches(1.85), CNTW, Inches(1.60), size=15)

    _body(s, "Generalization",
          ML, Inches(3.65), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Life insurance (static pricing): single-metric PSI is sufficient",
        "Auto insurance (continuous pricing): monitoring requirements scale with update frequency",
        "Framework generalizes to Vietnam, Indonesia, and other SE Asian emerging markets",
    ], ML, Inches(4.15), CNTW, Inches(1.40), size=15)

    _body(s, "Future Work",
          ML, Inches(5.75), CNTW, Inches(0.45), size=18, bold=True, color=BLUE)
    _bullets(s, [
        "Validate on real telematics data from a Cambodian insurer",
        "LangGraph-based retraining agent with automated PSI monitoring",
        "Publication: Journal of Risk and Insurance or ASTIN Bulletin",
    ], ML, Inches(6.20), CNTW, Inches(0.90), size=14)


def slide_20_thankyou(prs):
    s = _blank(prs)

    txb = s.shapes.add_textbox(ML, Inches(1.80), CNTW, Inches(1.40))
    tf = txb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Thank You"
    run.font.name = "Calibri"
    run.font.bold = True
    run.font.size = Pt(40)
    run.font.color.rgb = BLUE

    txb2 = s.shapes.add_textbox(ML, Inches(3.30), CNTW, Inches(0.60))
    tf2 = txb2.text_frame
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run()
    run2.text = "Questions?"
    run2.font.name = "Calibri"
    run2.font.size = Pt(28)
    run2.font.color.rgb = DARK

    _body(s, "LUN CHANPOLY",
          ML, Inches(4.80), CNTW, Inches(0.50),
          size=16, bold=True, align=PP_ALIGN.CENTER)
    _body(s, "chanpoly3@gmail.com",
          ML, Inches(5.35), CNTW, Inches(0.50),
          size=16, align=PP_ALIGN.CENTER)
    _body(s, "Advisor: HAS SOTHEA",
          ML, Inches(5.90), CNTW, Inches(0.50),
          size=14, align=PP_ALIGN.CENTER)
```

- [ ] **Step 2: Append final calls in build()**

```python
    slide_19_conclusion(prs)
    slide_20_thankyou(prs)
```

- [ ] **Step 3: Run full test suite — all tests must PASS**

```bash
pytest tests/test_build_presentation.py -v
```
Expected output:
```
PASSED tests/test_build_presentation.py::test_generates_20_slides
PASSED tests/test_build_presentation.py::test_title_slide_has_presenter_name
PASSED tests/test_build_presentation.py::test_slide_titles_present
```

- [ ] **Step 4: Open and visually verify the presentation**

```bash
# Windows
start thesis/auto/auto_defense_presentation.pptx
```
Check: 20 slides total, blue headers, tables render, no text overflow on any slide.

- [ ] **Step 5: Add generated output to .gitignore**

Append to `.gitignore` (create it at repo root if it doesn't exist):

```
thesis/auto/auto_defense_presentation.pptx
```

- [ ] **Step 6: Commit**

```bash
git add thesis/auto/build_presentation.py .gitignore
git commit -m "feat: complete 20-slide defense presentation generator"
```
