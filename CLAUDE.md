# DAC-UW-Thesis — Claude Code Session Instructions

## What this repo is

This is the thesis workspace for the auto insurance telematics research project, separated from the DAC HealthPrice platform repo (`C:\DAC-UW-Agent`). The DAC platform (wiki, sources, backend, frontend) remains at `C:\DAC-UW-Agent`.

## Thesis

**Title**: *"Validating Population Stability Metrics for Dynamic Auto Insurance Pricing with Telematics Data"*  
**Student**: Chanpoly (chanpoly3@gmail.com)  
**Target Defense**: ~2026-06-26 (8 weeks from 2026-04-21)  
**Advisor/Client**: Chris & Peter — DAC (Decent Actuarial Consultants)

**Core claim**: PSI successfully detects driver behavior distribution shifts, but fails under continuous dynamic pricing (3 identified failure modes). Solution: temporal multi-metric monitoring framework.

---

## Current Status (as of 2026-04-21)

**Phase**: Week 1 of 8 — writing phase begins (all experiments done early)

### Experiments — ALL COMPLETE

| Exp | File | Key Result |
|-----|------|------------|
| EXP-001 | `stress_testing/auto_insurance/exp_001_baseline.py` | PSI = 0.000 baseline (all GREEN) |
| EXP-002 | `stress_testing/auto_insurance/exp_002_responsiveness.py` | PSI monotonic: GREEN→AMBER→RED at 0%→30%→50% distortion; `idle_pct` most sensitive |
| EXP-003 | `stress_testing/auto_insurance/exp_003_failure_modes.py` | 3/3 failure modes caught: FM1 Highway Migration (idle_pct PSI=0.23 AMBER), FM2 Monsoon Surge (idle_pct PSI=0.30 RED), FM3 Tail Risk Flip (cohort PSI=42.3 RED) |
| EXP-004 | `stress_testing/auto_insurance/exp_004_temporal_drift.py` | Consecutive-month PSI unreliable (71% false-positive rate); YoY PSI detects (Jul RED PSI=3.007); rolling 3-month window detects (PSI=0.731 RED) |

### Synthetic Dataset

- `case-study/phnom_penh_pings.csv` — 1,161,881 GPS pings from 1,500 real-route trips
- `case-study/phnom_penh_trip_features.csv` — 1,500 trip-level rows (PSI-ready)
- `case-study/routes_cache.json` — 30 Phnom Penh O-D pairs × 3 traffic snapshots
- Generator: `stress_testing/auto_insurance/real_route_telematics_generator.py`

### Writing — NOT STARTED

No chapters written yet for the auto thesis. Life insurance chapters (Chs 1-5) are archived at `thesis/archive-life-insurance-2026-04-19/` for reference only.

---

## Week-by-Week Plan

| Week | Dates | Writing | Platform |
|------|-------|---------|----------|
| **Week 1** | Apr 21-27 | Ch1 (Intro) + Ch2 (Background) | — |
| **Week 2** | Apr 28-May 4 | Ch3 (Methodology) + Ch4 draft | Driver onboarding form |
| **Week 3** | May 5-11 | Ch4 (Results — all 4 experiments) | Quote display + policy tracker |
| **Week 4** | May 12-18 | Ch5 (Discussion & Implications) | Admin monitor dashboard (5 metrics) |
| **Week 5** | May 19-25 | Ch6 (Conclusion) | Retraining logic + versioning |
| **Week 6** | May 26-Jun 1 | Full draft review | Platform polish |
| **Week 7** | Jun 2-8 | Advisor feedback + revisions | — |
| **Week 8** | Jun 9-26 | Final proof + defense prep | Defense presentation |

---

## Chapter Structure (6 chapters)

### Ch1: Introduction & Background
- Why auto insurance + telematics in emerging markets
- Cambodia: 4.8M motorcycles, seasonal patterns, 8-15% claim frequency
- Gap: existing drift detection assumes batch data; telematics is streaming
- Key claim: single-metric monitoring insufficient for continuous pricing

### Ch2: Background
- PSI definition, formula, thresholds (GREEN <0.10, AMBER 0.10-0.25, RED >0.25)
- Telematics: NHTSA correlations (harsh braking, speeding, nighttime → claims)
- Prior drift detection literature (batch vs. stream context)
- Cambodia market context

### Ch3: Methodology
- Synthetic telematics data generator (30 Phnom Penh O-D pairs, 3 archetypes, 1,500 trips)
- Features: speed_mean, speed_std, hard_braking_events, idle_pct, trip_duration_min, trips_per_day, hour_of_day
- Experiment design rationale for EXP-001/002/003/004
- PSI formula and binning approach

### Ch4: Results
- EXP-001: PSI = 0.000 (all 7 features GREEN)
- EXP-002: Monotonicity confirmed; `idle_pct` most sensitive feature
- EXP-003: 3 failure modes — FM1 highway migration, FM2 monsoon surge, FM3 tail risk flip
- EXP-004: Consecutive-month PSI unreliable; YoY + rolling window required

### Ch5: Discussion & Implications
- Main finding: PSI insufficient alone for continuous pricing
- Recommendation: temporal multi-metric framework (5 metrics in parallel, checked every 2 weeks)
- Architecture: 2-week ingestion windows → alert → retrain → price update → audit
- Limitations: synthetic data, assumed independence, hypothetical seasonality
- Contrast with life insurance thesis (static vs. dynamic, batch vs. stream)

### Ch6: Conclusion
- Life vs. auto: monitoring requirements scale with pricing update frequency
- Generalization to other emerging markets
- Future work: real telematics validation, LangGraph retraining agent, publication

---

## Thesis Demo Platform Plan

A separate SPA (similar to DAC HealthPrice) demonstrating dynamic pricing + drift monitoring.

### Frontend screens
1. **Driver Onboarding** — personal info + telematics consent + quote generation
2. **Quote Display** — base premium, behavior adjustments, SHAP waterfall
3. **Policy Tracker** — current metrics (miles, harsh braking, speeding) + next repricing date
4. **Admin Monitor** — 5-metric dashboard (PSI, feature PSI, quantile PSI, seasonal decomp, model perf), alert colors, retrain trigger, version history

### Backend endpoints
```
POST /api/v1/telematics/quote      → premium + SHAP
GET  /api/v1/telematics/metrics    → 5-metric dashboard
POST /api/v1/telematics/retrain    → trigger retraining
GET  /api/v1/telematics/model-versions
POST /api/v1/telematics/policies/{id}/track
```

### Deployment target
- Frontend: `https://dac-auto-insurance.vercel.app`
- Backend: Same Render instance as DAC HealthPrice (`/api/v1/telematics/*`)

---

## Repo Structure

```
C:\DAC-UW-Thesis\
  thesis/
    archive-life-insurance-2026-04-19/  ← archived, reference only
    vietnam_case_study.html             ← Vietnam demo (May 1 deadline)
    auto/                               ← CREATE THIS: chapter drafts
      chapter1_introduction.md
      chapter2_background.md
      chapter3_methodology.md
      chapter4_results.md
      chapter5_discussion.md
      chapter6_conclusion.md
    auto_defense_presentation.html      ← CREATE: 20-slide deck
  stress_testing/
    auto_insurance/                     ← all 4 experiments live here
    experiments/                        ← life insurance experiments (archived)
  case-study/
    phnom_penh_pings.csv
    phnom_penh_trip_features.csv
    vietnam_dataset.csv
    models/                             ← GLM + XGBoost models (Vietnam)
```

---

## "hey" Protocol

When the user types **"hey"**, immediately provide:

1. **Thesis Status** — current week, what's done, what's pending (chapters + experiments)
2. **Vietnam Demo Status** — days complete, days remaining, May 1 deadline
3. **Next Actions** — top 3 prioritized items

Check `wiki/log.md` in `C:\DAC-UW-Agent` for recent activity (requires switching repos).

---

## Key Conventions

- Chapter files: `thesis/auto/chapter{N}_{slug}.md`
- Experiment files: `stress_testing/auto_insurance/exp_{NNN}_{slug}.py`
- Figures referenced in chapters: `thesis/auto/figures/fig_{N}_{slug}.png`
- Dates: always ISO `YYYY-MM-DD`
- PSI thresholds: GREEN < 0.10, AMBER 0.10–0.25, RED > 0.25

## Relationship to DAC Platform

This thesis demo will be a **new tab** ("Auto Insurance") on the DAC HealthPrice frontend, OR a standalone SPA. The architecture mirrors DAC HealthPrice Phase 4 but for telematics/auto product. Backend shared with existing Render deployment.
