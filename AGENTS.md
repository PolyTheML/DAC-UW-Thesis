# DAC-UW-Thesis — Agent Guide

## Project Overview

This is the thesis workspace for **Chanpoly** (lun.chanpoly@student.itc.edu.kh / chanpoly3@gmail.com), an MSc student at ITC Cambodia advised by **Has Sothea**. The research title is:

> *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*

**Defense target**: ~2026-06-26 (8-week writing sprint from 2026-04-21).  
**Client/Advisor**: Chris & Peter — DAC (Decent Actuarial Consultants).

The repository was migrated from `C:\DAC-UW-Agent` (the DAC HealthPrice platform repo) so that thesis work lives independently from production platform code. The DAC platform itself (wiki, sources, backend, frontend) remains at `C:\DAC-UW-Agent`.

**Core claim**: Traditional static underwriting rules are suboptimal for emerging-market health insurance because they ignore feature interactions and cannot adapt to portfolio drift. Contextual bandits (LinUCB, Thompson Sampling) can learn optimal accept/rate/decline/refer decisions from feedback, while PSI monitors ensure the approved portfolio does not drift too far from the actuarial reference. The thesis demonstrates this on a synthetic Cambodia health insurance dataset of 2,000 applicants.

---

## Technology Stack

| Layer | Tools / Libraries |
|-------|-------------------|
| Language | Python 3.11 |
| Data & ML | numpy, pandas, xgboost, shap, statsmodels |
| Telematics / Geo | googlemaps, polyline |
| Reporting | python-pptx, matplotlib |
| Testing | pytest |
| Env config | python-dotenv |

**Note**: There is no `pyproject.toml`, `requirements.txt`, `setup.py`, or virtual environment inside this repo. Dependencies are installed globally in the system Python environment. A `.gitignore` is present at repo root.

---

## Directory Structure

```
C:\DAC-UW-Thesis\
  case-study/                          # Datasets & trained models
    generate_cambodia_dataset.py       # Synthetic Cambodia health dataset (2,000 records)
    train_cambodia_models.py           # Trains GLM + XGBoost models; saves to models/
    cambodia_dataset.csv / .parquet    # Generated synthetic dataset
    generate_vietnam_dataset.py        # Synthetic Vietnam health/life dataset (ARCHIVED)
    train_models.py                    # Vietnam model training (ARCHIVED)
    vietnam_dataset.csv / .parquet     # Vietnam dataset (ARCHIVED)
    phnom_penh_pings.csv               # ~1.16M GPS pings (ARCHIVED auto data)
    phnom_penh_trip_features.csv       # 1,500 trip-level rows (ARCHIVED)
    models/                            # Pickled GLM/XGB models + SHAP + JSON results
                                       #   cambodia_*: current RL experiments
                                       #   health_* / life_*: archived Vietnam models

  stress_testing/                      # Stress-testing framework
    __init__.py                        # Package docstring
    generator.py                       # SyntheticApplicantGenerator (life insurance, 10K applicants)
    harness.py                         # StressTestHarness — PSI computation + alert validation
    scenarios.py                       # DistortionScenario dataclass + predefined scenarios
    adversarial.py                     # FailureModeDetector — 3 classes of silent concept drift
    rl/                                # CURRENT experiments (adaptive underwriting)
      __init__.py
      underwriting_bandit.py           # LinUCB, LinTS, EpsilonGreedy + simulator
      experiments/
        exp_005_underwriting_convergence.py   # Bandit learns risk-appropriate decisions
        exp_006_fairness_audit.py             # Regional / occupational bias check
        exp_007_benchmark_comparison.py       # Regret analysis vs static baseline
    auto_insurance/                    # ARCHIVED experiments (auto telematics)
      exp_001_baseline.py              # PSI = 0.000 validation
      exp_002_responsiveness.py        # Monotonic PSI vs drift fraction
      exp_003_failure_modes.py         # 3 behavioral failure modes
      exp_004_temporal_drift.py        # Consecutive-month vs YoY vs rolling window
      real_route_telematics_generator.py
      .env
    experiments/                        # ARCHIVED life insurance experiments
      exp_001_baseline.py
      exp_002_bmi_courier_spike.py
      exp_003_adversarial.py

  thesis/
    archive-life-insurance-2026-04-19/  # Archived life insurance chapters 1-5
    auto/
      build_presentation.py            # Generates 20-slide defense PPTX (ARCHIVED auto version — COMPLETE)
      auto_defense_presentation.pptx   # Generated output
      figures/                         # 4 matplotlib charts for auto presentation
    health_rl/                         # CURRENT thesis drafts (adaptive underwriting)
      chapter1_introduction.md         # ~1,450 words, COMPLETE
      chapter2_literature_review.md    # ~2,200 words, COMPLETE
      chapter3_methodology.md          # Skeleton only
      chapter4_results.md              # Skeleton only
      chapter5_conclusion.md           # Skeleton only
      chapterI_*.md .. chapterIV_*.md  # ITC internship-report template versions
      build_presentation.py            # Generates 20-slide health/RL defense PPTX (COMPLETE)
      build_thesis_docx.py             # Converts Markdown chapters → ITC-formatted Word doc
      health_rl_defense_presentation.pptx  # Generated output
      ITC_Thesis_Draft.docx            # Generated Word draft
      ITC_STYLE_GUIDE.md               # Formatting reference extracted from ITC template
      template_extract_full.txt        # Raw OCR text from official ITC thesis template DOCX
      figures/                         # 6 matplotlib charts (regret, reward, fairness, framework)
    vietnam_case_study.html            # Vietnam demo HTML (ARCHIVED)

  tests/
    test_build_presentation.py         # pytest: validates 20 slides, presenter name, key titles

  docs/
    superpowers/
      plans/                           # Step-by-step implementation plans
      specs/                           # Design specifications

  wiki/
    sources/                           # Thesis templates (abstract, acknowledgement, cover, etc.)
    topics/                            # Research topic pages & guides
```

---

## Build, Run & Test Commands

### Run experiments (adaptive underwriting — current)
```powershell
# EXP-005: Bandit convergence validation
python stress_testing/rl/experiments/exp_005_underwriting_convergence.py

# EXP-006: Fairness audit (regional / occupational bias)
python stress_testing/rl/experiments/exp_006_fairness_audit.py

# EXP-007: Benchmark comparison + regret analysis
python stress_testing/rl/experiments/exp_007_benchmark_comparison.py

# EXP-008: Human-in-the-loop underwriting
python stress_testing/rl/experiments/exp_008_human_in_the_loop.py
```

### Run archived experiments (auto insurance)
```powershell
# EXP-001 through EXP-004 (auto telematics — archived)
python stress_testing/auto_insurance/exp_001_baseline.py
python stress_testing/auto_insurance/exp_002_responsiveness.py
python stress_testing/auto_insurance/exp_003_failure_modes.py
python stress_testing/auto_insurance/exp_004_temporal_drift.py
```

All experiment scripts exit with code `0` on PASS and code `1` on FAIL.

### Generate telematics dataset (requires Google Maps API key)
```powershell
# Set key in stress_testing/auto_insurance/.env  OR
$env:GOOGLE_MAPS_API_KEY = "your_key"

python stress_testing/auto_insurance/real_route_telematics_generator.py
# Optional flags:
#   --trips-per-route 60
#   --with-drift
#   --stream
```

### Generate defense presentations
```powershell
# CURRENT — health/RL thesis (20 slides)
python thesis/health_rl/build_presentation.py
# Output: thesis/health_rl/health_rl_defense_presentation.pptx

# ARCHIVED — auto insurance thesis (20 slides)
python thesis/auto/build_presentation.py
# Output: thesis/auto/auto_defense_presentation.pptx

# Generate Word draft from Markdown chapters
python thesis/health_rl/build_thesis_docx.py
# Output: thesis/health_rl/ITC_Thesis_Draft.docx
```

### Run tests
```powershell
pytest tests/
# Or specifically:
pytest tests/test_build_presentation.py -v
```

### Generate / retrain Cambodia models
```powershell
python case-study/generate_cambodia_dataset.py
python case-study/train_cambodia_models.py
```

### Generate archived Vietnam models
```powershell
python case-study/generate_vietnam_dataset.py
python case-study/train_models.py
```

---

## Code Organization & Module Divisions

### Life Insurance Framework (`stress_testing/` root)
These modules are **archived** for reference. They depend on external packages in `C:\DAC-UW-Agent` (`medical_reader.pricing.calculator`, `analytics.monitor`, `portfolio.generator.py`).

- `generator.py` — `SyntheticApplicantGenerator`: creates 10,000 synthetic Cambodian applicants with demographics, health flags, and computed `mortality_ratio`.
- `scenarios.py` — `DistortionScenario` dataclass + predefined scenarios (`BASELINE`, `MILD_DRIFT`, `COURIER_SPIKE`, `RURAL_ENDEMIC`, `AGING_COHORT`).
- `harness.py` — `StressTestHarness`: runs scenarios, computes PSI against reference distribution, classifies alerts (GREEN/AMBER/RED), validates expected PSI bands.
- `adversarial.py` — `FailureModeDetector`: exposes 3 silent failure modes (Label Drift, Feature-PSI Decoupling, Bin Edge Camouflage) using secondary metrics.

### RL Underwriting Framework (`stress_testing/rl/`)
- `underwriting_bandit.py` — Core bandit module:
  - `LinUCB`: Frequentist linear upper confidence bound (Li et al. 2010)
  - `LinTS`: Bayesian linear Thompson Sampling (Agrawal & Goyal 2013)
  - `EpsilonGreedy`: Simple linear regression baseline
  - `StaticXGBBaseline`: Pre-trained XGBoost + deterministic rule benchmark
  - Actuarial reward simulator: 4 actions (standard, rated, decline, refer) with customer acceptance model
- `experiments/exp_005_underwriting_convergence.py` — Validates LinUCB learns risk-appropriate decisions and beats static baseline on cumulative reward and average regret.
- `experiments/exp_006_fairness_audit.py` — Checks regional and occupational approval-rate parity + PSI between applicant pool and approved pool.
- `experiments/exp_007_benchmark_comparison.py` — Compares LinUCB, LinTS, EpsilonGreedy, and StaticXGB on cumulative regret over 5,000 rounds.

### Cambodia Case Study (`case-study/`)
- `generate_cambodia_dataset.py` — Produces 2,000 synthetic Cambodia health insurance records with Cambodia-specific demographics, occupations, and disease prevalence (TB, Hepatitis B).
- `train_cambodia_models.py` — Trains health (`cambodia_health_xgb` + `cambodia_health_glm`) and mortality (`cambodia_life_xgb` + `cambodia_life_glm`) models; exports SHAP values, GLM coefficients JSON, and test predictions CSV.

### Auto Insurance Experiments (`stress_testing/auto_insurance/`)
**Archived**. Self-contained scripts with no external DAC-platform dependencies. Each script:
1. Loads `case-study/phnom_penh_trip_features.csv`
2. Computes PSI with a local `psi()` helper (percentile-based 10 bins)
3. Prints formatted results tables
4. Asserts pass criteria and exits with code `0` or `1`

### Vietnam Case Study (`case-study/`)
**Archived**. `generate_vietnam_dataset.py` and `train_models.py` produce 2,000 synthetic Vietnam health/life insurance records and train GLM + XGBoost models.

### Health/RL Presentation Builder (`thesis/health_rl/build_presentation.py`)
- Uses `python-pptx` + `matplotlib` to generate a 20-slide widescreen deck (13.33" × 7.5").
- One function per slide (`slide_01_title` through `slide_20_thank_you`).
- Generates 6 matplotlib figures on-the-fly into `thesis/health_rl/figures/`.
- Content: title/agenda, Cambodia market context, research claim, bandit framework, dataset, algorithms, reward design, EXP-005/006/007 results, PSI guardrails, implementation, social impact, discussion, conclusion.
- Style: white background, muted blue (`#2E5FA3`) headers, Calibri font, alternating gray table rows.

### Auto Presentation Builder (`thesis/auto/build_presentation.py`)
- ARCHIVED but complete. Generates 20-slide auto-insurance telematics deck.
- Same style helpers as health/RL version.
- Generates 4 matplotlib figures into `thesis/auto/figures/`.

### Thesis DOCX Builder (`thesis/health_rl/build_thesis_docx.py`)
- Converts Markdown chapter drafts into ITC-formatted `.docx`.
- Builds complete front matter: Khmer + French/English title pages, acknowledgement, abstracts, auto-generated TOC, list of figures/tables/abbreviations.
- Handles inline markdown (`**bold**`, `*italic*`, `$math$`), bullet/numbered lists, code blocks with gray shading, markdown tables, and placeholders like `[FIGURE: ...]`, `[TABLE: ...]`, `[CITATION: ...]`.
- Font: Times New Roman, 1.5 line spacing, justified body, 16pt bold ALL CAPS chapter headings.

---

## Development Conventions

### File naming
- **Experiment files**: `stress_testing/rl/experiments/exp_{NNN}_{slug}.py`
- **Chapter drafts**: `thesis/health_rl/chapter{N}_{slug}.md`
- **Figures**: `thesis/health_rl/figures/fig_{N}_{slug}.png`
- **Dates in filenames**: ISO `YYYY-MM-DD` (e.g., `2026-04-21-defense-presentation.md`)

### PSI thresholds (hardcoded across the codebase)
| Level | PSI Range |
|-------|-----------|
| GREEN | < 0.10 |
| AMBER | 0.10 – 0.25 |
| RED   | > 0.25 |

### Code style
- Extensive module-level and function-level docstrings.
- Type hints used (`from __future__ import annotations`, `list[dict]`, `np.ndarray`, etc.).
- `dataclass` for result containers (`ScenarioResult`, `AdversarialTestResult`, `DistortionScenario`).
- Scripts are self-contained: each has a `main()` function guarded by `if __name__ == "__main__":`.
- Reproducibility: `np.random.default_rng(seed=...)` with documented seeds (typically 42, or per-experiment seeds like 1/2/3/4).

### Data constants
- `N_BINS = 10` for PSI in auto experiments.
- `MONTH_N = 125` trips per monthly window in EXP-004.
- Premium GLM-proxy formula (used in EXP-003 and EXP-004):
  ```
  risk_score = 0.35 * clip(hard_braking / 50)
             + 0.35 * clip(jerk_rms    /  2)
             + 0.30 * clip(speed_avg   / 20)
  monthly_premium = 45 * (1 + 0.80 * risk_score)
  ```
- Underwriting actions (current RL experiments): 4 arms — STANDARD, RATED (+25%), DECLINE, REFER.
- `N_ROUNDS = 5000` for bandit simulations (2.5 passes through 2,000-record dataset).
- Base premium formula: `base_premium = 200 * mortality_multiplier` (USD/year).
- Customer acceptance: `p_accept = max(0.05, 0.95 - 3.5 * (monthly_premium / monthly_income))`.

---

## Testing Strategy

- **pytest** is the test runner. Only one test file exists at the moment:
  - `tests/test_build_presentation.py` — validates the PPTX generator produces exactly 20 slides, contains the presenter name "LUN CHANPOLY", and has expected keywords on specific slide indices.
- **Experiments are their own tests**: each `exp_00X_*.py` script contains assertions and exits non-zero on failure. They are designed to be run in CI or manually before committing results.
- **No unit tests** for the life-insurance `stress_testing/` core modules (generator, harness, scenarios, adversarial). Those modules are archived reference code.

---

## External Dependencies & Cross-Repo References

Several files in `stress_testing/` (root level) import modules that live in `C:\DAC-UW-Agent`:
- `medical_reader.pricing.calculator`
- `medical_reader.pricing.assumptions`
- `analytics.monitor`

**Implication**: The life insurance stress-testing framework will **not run standalone** in this repo. It requires the DAC platform repo to be on `PYTHONPATH` or installed. The auto insurance experiments in `stress_testing/auto_insurance/` are fully standalone and do not share this dependency.

---

## Deployment & Output Targets

- **Defense presentation**: `thesis/health_rl/health_rl_defense_presentation.pptx` (generated locally, not deployed). Archived auto version at `thesis/auto/auto_defense_presentation.pptx`.
- **Thesis Word draft**: `thesis/health_rl/ITC_Thesis_Draft.docx` (generated locally).
- **Vietnam demo HTML**: `thesis/vietnam_case_study.html` (static HTML, archived).
- **Next.js web app** (`web/`): Self-contained full-stack app with standard demo (`/demo`) and Human-in-the-Loop underwriting demo (`/hitl`). Run with `cd web && npm install && npm run dev`.

---

## Security Considerations

- `stress_testing/auto_insurance/.env` contains `GOOGLE_MAPS_API_KEY`. It is marked as a sensitive file and should never be committed.
- `.gitignore` is now present and excludes `.env`, `node_modules/`, `__pycache__/`, `.next/`, `.vercel/`, `.claude/`, and large data files (`phnom_penh_pings.csv`).
- The repo is **not** a sandbox. It operates on the local filesystem and writes to `case-study/`, `thesis/health_rl/`, `thesis/auto/`, etc.
- No secrets or credentials should be added to generated `.pptx`, `.csv`, `.html`, or markdown files.

---

## Current Status Snapshot (as of latest commit)

- **Experiments**: ALL 4 RL underwriting experiments (EXP-005 through EXP-008) are complete and passing. Auto insurance experiments (EXP-001 through EXP-004) are archived and passing.
- **Chapters**: Chapters 1 & 2 are **complete drafts** (~1,450 and ~2,200 words). Chapters 3, 4, and 5 are **skeletons only** (section headers + placeholders). ITC internship-report template versions (`chapterI`–`chapterIV`) also exist.
- **Defense presentation**: **COMPLETE** — `thesis/health_rl/build_presentation.py` generates a full 20-slide deck. Output `health_rl_defense_presentation.pptx` already generated. Auto version (`thesis/auto/`) is also complete but archived.
- **Thesis DOCX**: **COMPLETE** — `build_thesis_docx.py` converts Markdown chapters to ITC-formatted Word. Output `ITC_Thesis_Draft.docx` already generated (contains Ch1–2 body + Ch3–5 skeletons).
- **Figures**: 6 PNGs generated in `thesis/health_rl/figures/` (regret curves, reward curves, action evolution, fairness region, fairness occupation, framework).
- **Cambodia dataset & models**: Complete (`case-study/models/` populated with `cambodia_*.pkl`, `.json`, `.csv`).
- **Vietnam dataset & models**: Archived (`case-study/models/` health_* / life_* retained for reference).
- **Demo apps**: RESTORED. Next.js (`web/`) frontend is back with a new Human-in-the-Loop underwriting demo (`/hitl`). React+Vite (`demo/`) restored from git for reference.

---

## Quick Reference: Experiment Results

| Exp | File | Key Result |
|-----|------|------------|
| EXP-005 | `stress_testing/rl/experiments/exp_005_underwriting_convergence.py` | LinUCB cumulative reward $58,642 vs Static XGB $35,032 (+67%); avg regret $5.35 vs $10.66 in last 500 rounds |
| EXP-006 | `stress_testing/rl/experiments/exp_006_fairness_audit.py` | No region/occupation approval rate < 50% of max; Region PSI=0.0057 GREEN, Occupation PSI=0.0095 GREEN |
| EXP-007 | `stress_testing/rl/experiments/exp_007_benchmark_comparison.py` | LinTS lowest regret ($5,641), followed by LinUCB ($12,954), EpsilonGreedy ($24,273), StaticXGB ($35,067) |
| EXP-008 | `stress_testing/rl/experiments/exp_008_human_in_the_loop.py` | HITL reward $61,176 vs baseline $58,642 (+4.3%); alignment 56%; human cost $3,080 (5% of reward) |
| EXP-001 | `stress_testing/auto_insurance/exp_001_baseline.py` | (ARCHIVED) PSI = 0.000 baseline (all GREEN) |
| EXP-002 | `stress_testing/auto_insurance/exp_002_responsiveness.py` | (ARCHIVED) PSI monotonic: GREEN to AMBER to RED at 0% to 30% to 50% distortion |
| EXP-003 | `stress_testing/auto_insurance/exp_003_failure_modes.py` | (ARCHIVED) 3/3 failure modes caught |
| EXP-004 | `stress_testing/auto_insurance/exp_004_temporal_drift.py` | (ARCHIVED) Consecutive-month PSI unreliable (71% false-positive rate) |

---

## Relationship to DAC Platform

The auto insurance frontend concept (`https://dac-auto-insurance.vercel.app`) is archived.
