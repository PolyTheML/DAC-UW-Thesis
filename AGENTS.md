<!-- From: C:\DAC-UW-Thesis\AGENTS.md -->
# DAC-UW-Thesis — Agent Guide

## Project Overview

This is the thesis workspace for **Chanpoly** (lun.chanpoly@student.itc.edu.kh / chanpoly3@gmail.com), an MSc student at ITC Cambodia advised by **Has Sothea**. The research title is:

> *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*

**Defense target**: ~2026-06-26 (8-week writing sprint from 2026-04-21).  
**Client/Advisor**: Chris & Peter — DAC (Decent Actuarial Consultants).

The repository was migrated from `C:\DAC-UW-Agent` (the DAC HealthPrice platform repo) so that thesis work lives independently from production platform code. The DAC platform itself (wiki, sources, backend, frontend) remains at `C:\DAC-UW-Agent`.

**Core claim**: Traditional static underwriting rules are suboptimal for emerging-market health insurance because they ignore feature interactions and cannot adapt to portfolio drift. Contextual bandits (LinUCB, Thompson Sampling) can learn optimal accept/rate/decline/refer decisions from feedback, while PSI monitors ensure the approved portfolio does not drift too far from the actuarial reference. The thesis demonstrates this on a synthetic Cambodia health insurance dataset of 2,000 applicants anchored on the Cambodia Demographic and Health Survey (CDHS) 2021-22.

---

## Technology Stack

| Layer | Tools / Libraries |
|-------|-------------------|
| Language | Python 3.11 |
| Data & ML | numpy, pandas, xgboost, shap, statsmodels |
| Reporting | python-pptx, matplotlib |
| Testing | pytest |
| Env config | python-dotenv |

**Note**: There is no `pyproject.toml`, `requirements.txt`, `setup.py`, or virtual environment inside this repo. Dependencies are installed globally in the system Python environment. A `.gitignore` is present at repo root.

---

## Directory Structure

```
C:\DAC-UW-Thesis\
  data/cambodia/                       # Datasets & trained models
    generate_cambodia_dataset.py       # Synthetic Cambodia health dataset (2,000 records)
    train_cambodia_models.py           # Trains GLM + XGBoost models; saves to models/
    cambodia_dataset.csv / .parquet    # Generated synthetic dataset
    models/                            # Pickled GLM/XGB models + SHAP + JSON results
                                       #   cambodia_*: current RL experiments

  stress_testing/                      # Stress-testing framework (RL underwriting only)
    rl/                                # CURRENT experiments (adaptive underwriting)
      __init__.py
      underwriting_bandit.py           # LinUCB, LinTS, EpsilonGreedy + simulator
      experiments/
        exp_005_underwriting_convergence.py   # Bandit learns risk-appropriate decisions
        exp_006_fairness_audit.py             # Regional / occupational bias check
        exp_007_benchmark_comparison.py       # Regret analysis vs static baseline
        exp_008_human_in_the_loop.py          # Human-in-the-loop underwriting

  thesis/
    health_rl/                         # CURRENT thesis drafts (adaptive underwriting)
      chapter1_introduction.md         # ~1,450 words, COMPLETE
      chapter2_literature_review.md    # ~2,200 words, COMPLETE
      chapter3_methodology.md          # Skeleton only
      chapter4_results.md              # Skeleton only
      chapter5_conclusion.md           # Skeleton only
      chapterI_*.md .. chapterIV_*.md  # ITC internship-report template versions
      build_presentation.py            # Generates 20-slide health/RL defense PPTX
      build_thesis_docx.py             # Converts Markdown chapters → ITC-formatted Word doc
      health_rl_defense_presentation.pptx  # Generated output
      ITC_Thesis_Draft.docx            # Generated Word draft
      ITC_STYLE_GUIDE.md               # Formatting reference extracted from ITC template
      template_extract_full.txt        # Raw OCR text from official ITC thesis template DOCX
      figures/                         # 6 matplotlib charts (regret, reward, fairness, framework)
      presentation_script.md           # Speaker notes for defense
    I5_ITC_Thesis_Template_Guideline-AMS (1).docx
    ITC.jpg
    template_extract.txt
    template_tables.txt

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

### Run experiments (adaptive underwriting)
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

All experiment scripts exit with code `0` on PASS and code `1` on FAIL.

### Generate defense presentations
```powershell
# Health/RL thesis (20 slides)
python thesis/health_rl/build_presentation.py
# Output: thesis/health_rl/health_rl_defense_presentation.pptx

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
python data/cambodia/generate_cambodia_dataset.py
python data/cambodia/train_cambodia_models.py
```

---

## Code Organization & Module Divisions

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
- `experiments/exp_008_human_in_the_loop.py` — Measures HITL reward lift, alignment rate, and human cost.

### Cambodia Dataset (`data/cambodia/`)
- `generate_cambodia_dataset.py` — Produces 2,000 synthetic Cambodia health insurance records with Cambodia-specific demographics, occupations, and disease prevalence (TB, Hepatitis B).
- `train_cambodia_models.py` — Trains health (`cambodia_health_xgb` + `cambodia_health_glm`) and mortality (`cambodia_life_xgb` + `cambodia_life_glm`) models; exports SHAP values, GLM coefficients JSON, and test predictions CSV.

### Health/RL Presentation Builder (`thesis/health_rl/build_presentation.py`)
- Uses `python-pptx` + `matplotlib` to generate a 20-slide widescreen deck (13.33" × 7.5").
- One function per slide (`slide_01_title` through `slide_20_thank_you`).
- Generates 6 matplotlib figures on-the-fly into `thesis/health_rl/figures/`.
- Content: title/agenda, Cambodia market context, research claim, bandit framework, dataset, algorithms, reward design, EXP-005/006/007 results, PSI guardrails, implementation, social impact, discussion, conclusion.
- Style: white background, muted blue (`#2E5FA3`) headers, Calibri font, alternating gray table rows.

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
- Scripts are self-contained: each has a `main()` function guarded by `if __name__ == "__main__":`.
- Reproducibility: `np.random.default_rng(seed=...)` with documented seeds (typically 42, or per-experiment seeds like 1/2/3/4).

### Data constants
- Underwriting actions: 4 arms — STANDARD, RATED (+25%), DECLINE, REFER.
- `N_ROUNDS = 5000` for bandit simulations (2.5 passes through 2,000-record dataset).
- Base premium formula: `base_premium = 200 * mortality_multiplier` (USD/year).
- Customer acceptance: `p_accept = max(0.05, 0.95 - 3.5 * (monthly_premium / monthly_income))`.
- Dataset anchor: Cambodia Demographic and Health Survey (CDHS) 2021-22 [NIS/ICF].
- New social-determinant features: `education`, `wealth_quintile`, `alcohol_use`, `self_reported_health`.

### Reward simulator (`RewardConfig`)
The actuarial reward simulator is now parameterised via `RewardConfig` (dataclass) in `stress_testing/rl/underwriting_bandit.py`.

**Default (simple) mode** reproduces the original hardcoded model:
- `base_premium_rate = 200`, `expected_claims_rate = 150`
- No expense loading, no lapse, CLV multiplier = 1.0

**Realistic mode** (`RewardConfig.realistic()`) adds:
- `expense_fixed = 25.0` USD per accepted policy
- `expense_ratio = 0.05` (5% of premium)
- `lapse_prob = 0.08` with `lapse_premium_factor = 0.5` and `lapse_claims_factor = 0.5`
- `clv_multiplier = 2.5` (customer lifetime value scaling)

All experiments, the demo API, and the backend support an optional `config` argument.  Passing `None` preserves backward-compatible default behaviour.

---

## Testing Strategy

- **pytest** is the test runner.
  - `tests/test_build_presentation.py` — validates the PPTX generator produces exactly 20 slides, contains the presenter name "LUN CHANPOLY", and has expected keywords on specific slide indices.
- **Experiments are their own tests**: each `exp_00X_*.py` script contains assertions and exits non-zero on failure. They are designed to be run in CI or manually before committing results.

---

## Deployment & Output Targets

- **Defense presentation**: `thesis/health_rl/health_rl_defense_presentation.pptx` (generated locally, not deployed).
- **Thesis Word draft**: `thesis/health_rl/ITC_Thesis_Draft.docx` (generated locally).

---

## Quick Reference: Experiment Results

| Exp | File | Key Result |
|-----|------|------------|
| EXP-005 | `stress_testing/rl/experiments/exp_005_underwriting_convergence.py` | LinUCB cumulative reward $99,706 vs Static XGB $72,540 (+37%); avg regret $5.16 vs $12.26 in last 500 rounds |
| EXP-006 | `stress_testing/rl/experiments/exp_006_fairness_audit.py` | No region/occupation approval rate < 50% of max; Region PSI=0.0041 GREEN, Occupation PSI=0.0104 GREEN |
| EXP-007 | `stress_testing/rl/experiments/exp_007_benchmark_comparison.py` | LinUCB lowest regret ($14,840), followed by LinTS ($17,036), EpsilonGreedy ($31,760), StaticXGB ($42,052) |
| EXP-008 | `stress_testing/rl/experiments/exp_008_human_in_the_loop.py` | HITL reward $101,646 vs baseline $99,706 (+1.9%); late-stage alignment 46%; human cost $2,555 (2.5% of reward) |
| EXP-013 | `stress_testing/rl/experiments/exp_013_loglog_regret_validation.py` | Log-log slope 0.572 (R²=0.992); converges to 0.511 at burn-in=1000, empirically validating O(√T) bound |

---

## Current Status Snapshot (as of latest commit)

- **Experiments**: ALL 4 RL underwriting experiments (EXP-005 through EXP-008) are complete and passing.
- **Chapters**: Chapters 1 & 2 are **complete drafts** (~1,450 and ~2,200 words). Chapters 3, 4, and 5 are **skeletons only** (section headers + placeholders). ITC internship-report template versions (`chapterI`–`chapterIV`) also exist.
- **Defense presentation**: **COMPLETE** — `thesis/health_rl/build_presentation.py` generates a full 20-slide deck. Output `health_rl_defense_presentation.pptx` already generated.
- **Thesis DOCX**: **COMPLETE** — `build_thesis_docx.py` converts Markdown chapters to ITC-formatted Word. Output `ITC_Thesis_Draft.docx` already generated (contains Ch1–2 body + Ch3–5 skeletons).
- **Figures**: 6 PNGs generated in `thesis/health_rl/figures/` (regret curves, reward curves, action evolution, fairness region, fairness occupation, framework).
- **Cambodia dataset & models**: Complete (`data/cambodia/models/` populated with `cambodia_*.pkl`, `.json`, `.csv`).

---

## Security Considerations

- `.gitignore` is present and excludes `.env`, `node_modules/`, `__pycache__/`, `.next/`, `.vercel/`, `.claude/`, and large data files.
- The repo is **not** a sandbox. It operates on the local filesystem and writes to `data/cambodia/`, `thesis/health_rl/`, etc.
- No secrets or credentials should be added to generated `.pptx`, `.csv`, `.html`, or markdown files.
