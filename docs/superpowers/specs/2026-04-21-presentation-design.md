# Defense Presentation Design Spec
**Date**: 2026-04-21  
**Project**: DAC-UW-Thesis — Auto Insurance Telematics  
**Output**: `thesis/auto/auto_defense_presentation.pptx`  
**Generator**: `thesis/auto/build_presentation.py` (python-pptx)

---

## Overview

A 20-slide PowerPoint defense presentation following the thesis chapter arc (Option B). Generated programmatically via `python-pptx`. Style: clean/minimal — white background, muted accent colors, simple tables, no embedded charts.

**Audience**: Thesis committee and advisor  
**Presenter**: LUN CHANPOLY  
**Advisor**: HAS SOTHEA  
**Date on title slide**: (blank — to be filled before defense)

---

## Slide Inventory

### Section 1 — Opening (Slides 1–2)

| Slide | Title | Content |
|-------|-------|---------|
| 1 | Title Slide | Thesis title: *"Validating Population Stability Metrics for Dynamic Auto Insurance Pricing with Telematics Data"*. Presenter: LUN CHANPOLY. Advisor: HAS SOTHEA. Date: blank. |
| 2 | Agenda | One-line per chapter (Ch1–Ch6) as a visual roadmap. |

---

### Section 2 — Chapter 1: Introduction (Slides 3–4)

| Slide | Title | Content |
|-------|-------|---------|
| 3 | Why Auto Insurance Telematics? | Cambodia context: 4.8M motorcycles, 8–15% claim frequency, seasonal patterns. Gap: existing drift detection assumes batch data; telematics is streaming. |
| 4 | Research Claim | Single-metric PSI monitoring is insufficient for continuous dynamic pricing. Thesis introduces a temporal multi-metric framework as the solution. |

---

### Section 3 — Chapter 2: Background (Slides 5–7)

| Slide | Title | Content |
|-------|-------|---------|
| 5 | PSI: Definition & Thresholds | Formula: PSI = Σ(A_i − E_i) × ln(A_i / E_i). Table: GREEN < 0.10, AMBER 0.10–0.25, RED > 0.25. 10-bin percentile approach. |
| 6 | Telematics Features & Risk Signals | Table of 7 features (speed_avg_kmh, speed_p90_kmh, hard_braking_events, harsh_jerk_events, jerk_rms, idle_pct, vibration_avg) with NHTSA correlation to claims. |
| 7 | Prior Work & Gap | Batch vs. stream drift detection literature. Why existing methods break under continuous repricing. Gap statement leading into methodology. |

---

### Section 4 — Chapter 3: Methodology (Slides 8–9)

| Slide | Title | Content |
|-------|-------|---------|
| 8 | Synthetic Data Generator | 30 Phnom Penh O-D pairs × 3 traffic snapshots → 1,500 trips (1,161,881 GPS pings). Three driver archetypes. Dataset dimensions table. |
| 9 | Experiment Design Overview | 2×4 table: EXP-001/002/003/004 with one-line purpose each. Premium GLM-proxy formula: risk_score weights + $45 base rate. 10 percentile bins. |

---

### Section 5 — Chapter 4: Results (Slides 10–16)

| Slide | Title | Content |
|-------|-------|---------|
| 10 | EXP-001: Baseline Validation | Table: all 7 features, PSI = 0.000, all GREEN. Takeaway: PSI correctly returns zero when distributions are identical. |
| 11 | EXP-002: Responsiveness | Table: drift fraction 0%→50% vs. PSI for idle_pct, speed_avg_kmh, hard_braking_events, jerk_rms. GREEN→AMBER→RED progression. Callout: `idle_pct` most sensitive. |
| 12 | EXP-003: Failure Modes Overview | Problem: 3 scenarios where premium PSI stays GREEN despite real behavioral shifts. One-line description of FM1, FM2, FM3. |
| 13 | EXP-003: FM1 & FM2 | Two-column layout. FM1: premium PSI GREEN (false negative) vs. idle_pct PSI = 0.23 AMBER. FM2: season-adjusted premium GREEN vs. raw idle_pct PSI = 0.30 RED. |
| 14 | EXP-003: FM3 Tail Risk Flip | Bottom-5% safe cohort flips to extreme profile. Full-pop PSI GREEN. Cohort PSI = 42.3 RED. Fix: cohort-level PSI required. |
| 15 | EXP-004: Temporal Drift — The Problem | Consecutive-month PSI: 71% false-positive rate in dry season. Monsoon onset signal (Jun→Jul) indistinguishable from sampling noise. |
| 16 | EXP-004: Temporal Drift — The Fix | YoY PSI Jul = 3.007 RED. Rolling 3-month window PSI = 0.731 RED. Both methods detect genuine regime shift. |

---

### Section 6 — Chapter 5: Discussion (Slides 17–18)

| Slide | Title | Content |
|-------|-------|---------|
| 17 | Main Finding & Limitations | PSI alone insufficient for continuous pricing. Three failure modes identified. Limitations: synthetic data, assumed feature independence, hypothetical seasonality. |
| 18 | Temporal Multi-Metric Framework | 5 metrics in parallel (PSI, feature PSI, quantile PSI, seasonal decomp, model performance). Cadence: every 2 weeks → alert → retrain → price update → audit. Text-based flow diagram. |

---

### Section 7 — Chapter 6: Conclusion (Slides 19–20)

| Slide | Title | Content |
|-------|-------|---------|
| 19 | Conclusion | Life vs. auto: monitoring requirements scale with pricing update frequency. Generalization to emerging markets. Future work: real telematics validation, LangGraph retraining agent, publication. |
| 20 | Thank You / Q&A | Acknowledgements, contact: chanpoly3@gmail.com, "Questions?" |

---

## Style Guidelines

- **Background**: white
- **Accent color**: muted blue (`#2E5FA3`) for headers and table headers
- **Body font**: Calibri 18pt
- **Title font**: Calibri Bold 28pt
- **Tables**: light gray row alternation, no heavy borders
- **No embedded matplotlib charts** — data presented as tables
- **Slide dimensions**: standard widescreen 13.33" × 7.5"

---

## File Locations

| File | Path |
|------|------|
| Generator script | `thesis/auto/build_presentation.py` |
| Output .pptx | `thesis/auto/auto_defense_presentation.pptx` |
| Data source | `case-study/phnom_penh_trip_features.csv` |

---

## Data / Numbers Used

All PSI values are hardcoded from confirmed experiment runs (no re-execution needed):

| Experiment | Key Numbers |
|------------|-------------|
| EXP-001 | PSI = 0.000 for all 7 features |
| EXP-002 | idle_pct: 0%→GREEN, 30%→AMBER, 50%→RED |
| EXP-003 FM1 | Premium PSI GREEN; idle_pct PSI = 0.23 AMBER |
| EXP-003 FM2 | Premium PSI GREEN; idle_pct PSI = 0.30 RED |
| EXP-003 FM3 | Full-pop PSI GREEN; cohort PSI = 42.3 RED |
| EXP-004 | Consec-month: 71% FP rate; YoY Jul PSI = 3.007 RED; Rolling PSI = 0.731 RED |
