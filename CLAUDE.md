# DAC-UW-Thesis — Claude Code Session Instructions

## What this repo is

This is the thesis workspace for *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*, a master's thesis at ITC (Institut de Technologie du Cambodge). The repo contains: bandit algorithm implementations, a synthetic Cambodia applicant dataset, all experiment scripts, the chapter sources, a Render-deployed FastAPI demo, and build pipelines for the docx thesis + pptx defense presentation.

## Thesis

**Title**: *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*
**Student**: Chanpoly (chanpoly3@gmail.com)
**Advisor/Client**: DAC (Decent Actuarial Consultants — Chris & Peter)

**Core claim**: Linear contextual bandits (LinUCB, LinTS) decisively outperform static rule-based underwriting on synthetic Cambodian health insurance data (+25.2 % cumulative reward over Static XGB, 20 seeds, p < 0.001, d = 2.98), while maintaining demographic parity via external PSI guardrails. A human-in-the-loop wrapper adds another +6.5 % at 1.5 % human-review cost.

---

## Repository structure

```
C:\DAC-UW-Thesis\
  CLAUDE.md
  README.md
  requirements.txt
  render.yaml                  # Render PaaS config (entry: demo.main:app)
  .gitignore

  healthrl/                    # core bandit package
    __init__.py
    underwriting_bandit.py     # LinUCB, LinTS, ε-Greedy, StaticXGB, Oracle,
                               # RewardConfig, preprocess_cambodia_data
    config.py                  # central hyperparameters (EXPERIMENT, BANDIT)
    experiments/
      exp_005_underwriting_convergence.py
      exp_006_fairness_audit.py
      exp_007_benchmark_comparison.py
      exp_008_human_in_the_loop.py
      exp_009_drift_adaptation.py
      exp_010_cold_start_analysis.py
      exp_011_ablation_study.py
      exp_012_sensitivity_analysis.py
      exp_013_loglog_regret_validation.py
      experiment_utils.py
      statistical_utils.py

  data/
    cambodia/
      cambodia_dataset.csv     # 2,000-record synthetic dataset (CDHS-anchored)
      cambodia_dataset.parquet
      generate_cambodia_dataset.py
      train_cambodia_models.py # GLM + XGBoost training
      train_cambodia_rl.py     # bandit training driver
      models/                  # trained model pickles + metric JSONs

  demo/                        # live FastAPI actuarial dashboard (Render)
    main.py
    pricing_engine.py
    hitl_db.py
    static/                    # frontend assets
    templates/

  scripts/                     # thesis automation loop (score → rewrite)
    thesis_loop.py
    thesis_scorer.py
    thesis_rewriter.py

  thesis/
    health_rl/
      chapter01_introduction.md
      chapter02_presentation.md
      chapter03_literature_review.md
      chapter04_project_analysis.md   # includes methodology §§4.5-4.10
      chapter05_results.md
      chapter06_conclusion.md
      figures/                 # chapter figures + math_cache
      build_thesis_docx.py     # docx builder
      build_burgundy_presentation.py
      generate_eda_figures.py
      latex_render.py
      ITC_STYLE_GUIDE.md

  wiki/                        # writing templates + topic guides
    sources/                   # ITC chapter templates, references
    topics/                    # defense framework, presentation guide

  tests/                       # pytest suite
    test_build_presentation.py
    test_thesis_loop.py
    test_thesis_rewriter.py
    test_thesis_scorer.py

  docs/superpowers/            # specs + plans + audits
    specs/
    plans/
    audit/2026-05-25/          # the audit driving the current cleanup
```

---

## Key conventions

- **Chapter files**: `thesis/health_rl/chapterNN_<slug>.md`, zero-padded to match declared chapter numbers.
- **Experiment files**: `healthrl/experiments/exp_NNN_<slug>.py` with pre-registered pass criteria + exit codes.
- **Hyperparameters**: import `from healthrl.config import EXPERIMENT, BANDIT` — do NOT introduce module-level constants in new experiments.
- **Statistical methodology**: 20-seed multi-run, bootstrap 95 % CI, paired Wilcoxon, Bonferroni correction, Cohen's d. Primary illustrative seed = 42.
- **PSI thresholds**: GREEN < 0.10, AMBER 0.10–0.25, RED > 0.25.
- **Dates**: ISO `YYYY-MM-DD`.

## How to run the headline experiment

```bash
python healthrl/experiments/exp_005_underwriting_convergence.py
```

Exit 0 = pre-registered pass criteria satisfied. Takes ~5-10 minutes on a standard CPU (20 seeds × 5,000 rounds × 3 algorithms).

## How to launch the demo locally

```bash
uvicorn demo.main:app --reload --port 8000
```

## Where to find things

| What | Where |
|---|---|
| Bandit math | `healthrl/underwriting_bandit.py` |
| Reward simulator | `healthrl/underwriting_bandit.py` (`RewardConfig`, `expected_rewards`, `make_reward_simulator`) |
| Dataset spec | `data/cambodia/generate_cambodia_dataset.py` (docstring is anchored on CDHS / STEPS / ILO / WHO sources) |
| Live audit | `docs/superpowers/audit/2026-05-25/` (6 reports) |
| Implementation plan in progress | `docs/superpowers/plans/2026-05-25-tier1-critical-fixes.md` |

## "hey" protocol

When the user types **hey**, immediately provide:

1. **Thesis status**: which chapters are done, which experiments pass, any pending Tier-1/2/3 audit items.
2. **Last commit**: `git log -1 --oneline` and a one-sentence summary of what that commit accomplished.
3. **Next actions**: top 3 prioritized items from `docs/superpowers/audit/2026-05-25/05-improvements.md` that are not yet committed.
