# Repository Structure Overview

**Date**: 2026-05-25

---

## Current structure (annotated)

```
C:\DAC-UW-Thesis\
├── CLAUDE.md                       🟩 instructions
├── AGENTS.md                       🟩 instructions for sub-agents
├── COLLAB.md                       🟩 collaboration log
├── .gitignore                      🟩 — note: backend/ is gitignored as deprecated
├── requirements.txt                🟩 runtime deps (>= pins; tighten to ==)
├── render.yaml                     🟩 Render PaaS config (entry: demo.main:app)
│
├── analyze2..6.py                  🟥 DELETE — throwaway docx scripts
├── analyze_build*.py               🟥 DELETE
├── analyze_template.py             🟥 DELETE
├── shadow_mode.db                  🟥 DELETE — runtime sqlite, gitignored
│
├── backend/                        🟧 DEPRECATED (.gitignore says "superseded by demo/")
│   ├── main.py                     FastAPI app for shadow mode
│   ├── shadow/                     ORM + service + router + schemas + smoke test
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── smoke_test.py
│
├── case-study/                     🟨 RENAME → data/cambodia/
│   ├── cambodia_dataset.csv        🟩 2,000-record dataset
│   ├── cambodia_dataset.parquet    🟩 same, parquet
│   ├── generate_cambodia_dataset.py 🟩 generator (CDHS-anchored)
│   ├── train_cambodia_models.py    🟩 GLM + XGBoost training
│   ├── train_cambodia_rl.py        🟩 bandit training driver
│   └── models/                     🟩 trained model artifacts
│       ├── cambodia_health_glm.pkl
│       ├── cambodia_health_xgb.pkl
│       ├── cambodia_life_glm.pkl
│       ├── cambodia_life_xgb.pkl
│       ├── cambodia_bandit_ts.pkl
│       ├── cambodia_encoders.pkl
│       ├── cambodia_glm_coefficients.json
│       ├── cambodia_model_results.json
│       ├── cambodia_shap_values.pkl
│       ├── cambodia_test_predictions.csv
│       ├── cambodia_rl_results.json
│       ├── cambodia_rl_regret_curves.parquet
│       └── cambodia_rl_trajectory.parquet
│
├── demo/                           🟩 LIVE PLATFORM (Render-deployed)
│   ├── main.py                     FastAPI app
│   ├── pricing_engine.py
│   ├── hitl_db.py
│   ├── hitl.db                     🟥 runtime sqlite, gitignored
│   ├── static/
│   │   ├── app.js
│   │   ├── coefficients_linucb_seed42.json
│   │   ├── defense.html
│   │   ├── defense.js
│   │   ├── exp005_results_seed42.json
│   │   ├── exp007_results_seed42.json
│   │   └── fig_loglog_regret.png
│   └── templates/
│       └── index.html
│
├── docs/superpowers/               🟩 specs and plans
│   ├── plans/
│   │   ├── 2026-04-21-defense-presentation.md
│   │   ├── 2026-05-05-three-month-internship-plan.md
│   │   ├── 2026-05-12-autoresearch-chapter-loop.md
│   │   └── section-iv-project-analysis-plan.md
│   ├── specs/
│   │   ├── 2026-04-21-presentation-design.md
│   │   ├── 2026-05-11-chapter4-rewrite-design.md
│   │   ├── 2026-05-12-autoresearch-chapter-loop-design.md
│   │   └── 2026-05-25-repo-audit-design.md
│   └── audit/2026-05-25/           🟩 (this audit's outputs)
│       ├── 01-cleanup-report.md
│       ├── 02-structure-overview.md
│       ├── 03-research-integrity.md
│       ├── 04-literature-validation.md
│       ├── 05-improvements.md
│       └── 06-final-assessment.md
│
├── scripts/                        🟩 thesis-automation loop
│   ├── thesis_loop.py              orchestrator (score → rewrite until pass)
│   ├── thesis_rewriter.py
│   └── thesis_scorer.py
│
├── stress_testing/                 🟨 RENAME → experiments/
│   └── rl/
│       ├── underwriting_bandit.py  🟩 core: LinUCB, LinTS, ε-Greedy, StaticXGB, Oracle, RewardConfig, preprocessor
│       └── experiments/            🟩
│           ├── exp_005_underwriting_convergence.py    documented in Ch V §5.1
│           ├── exp_006_fairness_audit.py              documented in Ch V §5.2
│           ├── exp_007_benchmark_comparison.py        documented in Ch V §5.3
│           ├── exp_008_human_in_the_loop.py           documented in Ch V §5.4
│           ├── exp_009_drift_adaptation.py            ❌ NOT documented in any chapter
│           ├── exp_010_cold_start_analysis.py         ❌ NOT documented
│           ├── exp_011_ablation_study.py              ❌ NOT documented
│           ├── exp_012_sensitivity_analysis.py        ❌ NOT documented
│           ├── exp_013_loglog_regret_validation.py    ❌ NOT documented
│           ├── experiment_utils.py                    multi-seed harness
│           ├── statistical_utils.py                   bootstrap CI + paired tests
│           └── exp_*_output*.txt                      🟥 DELETE — generated stdout
│
├── tests/                          🟩
│   ├── test_build_presentation.py
│   ├── test_shadow_mode.py         🟥 DELETE — imports deprecated backend/
│   ├── test_thesis_loop.py
│   ├── test_thesis_rewriter.py
│   └── test_thesis_scorer.py
│
├── thesis/                         🟩
│   ├── AMS.png, DAC.jpg, ITC.jpg                              🟧 verify usage
│   ├── I5_ITC_POLY.docx + _BACKUP.docx                        🟧 one is template, one is build output
│   ├── I5_ITC_Thesis_Template_Guideline-AMS_BACKUP_CLEAN.docx 🟧
│   ├── docx_structure*.txt, template_*.txt                    🟥 DELETE
│   └── health_rl/                                             🟩
│       ├── chapter1_introduction.md         Ch I (currently also contains Ch II content — dedupe)
│       ├── chapter2_presentation_of_project.md   Ch II
│       ├── chapter2_literature_review.md    🟨 actually Ch III — rename
│       ├── chapter3_methodology.md          🟧 ALSO claims Ch III — resolve duplicate-number
│       ├── chapter4_project_analysis.md     Ch IV
│       ├── chapter4_results.md              🟨 actually Ch V — rename
│       ├── chapter5_conclusion.md           🟨 actually Ch VI — rename
│       ├── chapter5_results.md              🟥 DELETE — superseded
│       ├── chapter6_conclusion.md           🟥 DELETE — mixes inconsistent numbers
│       ├── AGENT_BRIEF.md
│       ├── DEMO_DEFENSE_REDEMPTION_PLAN.md
│       ├── ITC_STYLE_GUIDE.md
│       ├── ITC_Thesis_Draft.docx            build output
│       ├── _fix_theta.py                    🟥 DELETE
│       ├── build_thesis_docx.py             🟩 docx builder
│       ├── build_presentation.py            🟧 one of 3 builders
│       ├── build_burgundy_presentation.py   🟧 one of 3 builders
│       ├── build_presentation_sothea_format.py 🟧 one of 3 builders
│       ├── burgundy_defense_presentation.pptx
│       ├── burgundy_defense_presentation_filled.pptx
│       ├── health_rl_defense_presentation.pptx
│       ├── generate_eda_figures.py          🟩 EDA figure generator
│       ├── latex_render.py                  🟩 math equation render to PNG
│       ├── slide_content.txt                🟥
│       ├── template_extract_full.txt        🟥
│       ├── figures/
│       │   ├── fig_action_evolution.png         used in Ch V §5.1
│       │   ├── fig_reward_curves.png            used in Ch V §5.1
│       │   ├── fig_fairness_region.png          used in Ch V §5.2
│       │   ├── fig_fairness_occupation.png      used in Ch V §5.2
│       │   ├── fig_regret_curves.png            used in Ch V §5.3
│       │   ├── fig_hitl_experiment.png          used in Ch V §5.4
│       │   ├── fig_framework.png                used in Ch III §3.6
│       │   ├── fig_ch2_system_architecture.png/.svg     Ch II
│       │   ├── fig_ch2_project_timeline.png/.svg        Ch II
│       │   ├── fig_ch4_architecture.png         used in Ch IV §4.4.3
│       │   ├── fig_ch4_bandit_loop.png          used in Ch IV §4.4.3
│       │   ├── fig_organization_chart.png       used in Ch I §1.2.4
│       │   ├── fig_project_timeline_3month.png  Ch I
│       │   ├── fig_loglog_regret.png            ❌ orphan — not embedded
│       │   ├── fig_009_drift_adaptation.png     ❌ orphan
│       │   ├── fig_010_cold_start.png           ❌ orphan
│       │   ├── fig_eda_01..14.png (14 EDA figures)  ❌ orphan — generated but unused
│       │   ├── eda_summary_statistics.csv       ❌ orphan
│       │   ├── generate_fig_project_timeline_3month.py
│       │   └── math_cache/                      🟩 LaTeX-rendered formula PNGs
│       │       └── math_block_*.png (14 files)
│       └── scripts/
│           ├── build_fig_ch4_architecture.py
│           └── build_fig_ch4_bandit_loop.py
│
└── wiki/                           🟨 RENAME → docs/templates/ (or thesis/templates/)
    ├── sources/                    writing templates
    │   ├── adaptive_underwriting_cambodia.md
    │   ├── psi-literature-references.md
    │   ├── thesis-abstract-template.md
    │   ├── thesis-acknowledgement-template.md
    │   ├── thesis-cover-template.md
    │   ├── thesis-discussion-template.md
    │   ├── thesis-formatting-guide.md
    │   ├── thesis-introduction-template.md
    │   ├── thesis-methodology-template.md
    │   └── thesis-results-template.md
    └── topics/
        ├── thesis-defense-stress-testing-framework.md
        └── thesis-presentation-guide.md
```

---

## Proposed clean structure (target)

The goal: research project that is unambiguously navigable, naming consistent with the thesis topic (RL health insurance, not the predecessor "auto insurance / stress testing" naming).

```
C:\DAC-UW-Thesis\
├── README.md                       # NEW — short orientation: what, how to run, where the chapters are
├── CLAUDE.md                       # existing, update auto/PSI references → RL/bandit references
├── AGENTS.md                       # existing
├── COLLAB.md                       # existing
├── .gitignore                      # existing
├── pyproject.toml                  # NEW — replace requirements.txt + lock with == pins
├── requirements.txt                # keep for Render compatibility, but pin to ==
├── render.yaml                     # existing
│
├── data/                           # RENAMED from case-study/
│   └── cambodia/
│       ├── cambodia_dataset.csv
│       ├── cambodia_dataset.parquet
│       ├── generate_cambodia_dataset.py
│       └── models/
│           └── (XGB + GLM + encoders + RL pickles)
│
├── healthrl/                       # NEW python package; RENAMED from stress_testing/rl/
│   ├── __init__.py
│   ├── bandit.py                   # RENAMED from underwriting_bandit.py; same content
│   ├── config.py                   # NEW — central hyperparameters (alpha, v2, epsilon, n_seeds, N_ROUNDS)
│   ├── reward.py                   # NEW — extract RewardConfig + reward fns from bandit.py
│   ├── preprocessor.py             # NEW — extract preprocess_cambodia_data
│   ├── statistics.py               # RENAMED from statistical_utils.py
│   └── experiments/
│       ├── __init__.py
│       ├── _harness.py             # RENAMED from experiment_utils.py
│       ├── exp_005_convergence.py
│       ├── exp_006_fairness.py
│       ├── exp_007_benchmark.py
│       ├── exp_008_hitl.py
│       ├── exp_009_drift.py        # promote — write up in Ch V
│       ├── exp_010_cold_start.py   # promote
│       ├── exp_011_ablation.py     # promote
│       ├── exp_012_sensitivity.py  # promote
│       └── exp_013_loglog_regret.py
│
├── demo/                           # KEEP — live Render platform
│
├── thesis/                         # KEEP — chapter sources + figures + builders
│   ├── ITC_STYLE_GUIDE.md
│   ├── AGENT_BRIEF.md
│   ├── chapters/                   # NEW subfolder
│   │   ├── 01_introduction.md
│   │   ├── 02_presentation.md
│   │   ├── 03_literature_review.md
│   │   ├── 04_methodology.md       # or merged into 05_project_analysis
│   │   ├── 05_project_analysis.md
│   │   ├── 06_results.md
│   │   └── 07_conclusion.md
│   ├── figures/                    # KEEP, prune orphans (EDA → appendix)
│   │   ├── ...
│   │   └── math_cache/
│   ├── build/                      # NEW — all docx/pptx build outputs go here, gitignored
│   │   ├── ITC_Thesis_Draft.docx
│   │   └── defense_presentation.pptx
│   ├── build_docx.py               # RENAMED from build_thesis_docx.py
│   ├── build_presentation.py       # consolidated single builder (theme via config)
│   ├── generate_eda_figures.py
│   └── latex_render.py
│
├── docs/                           # KEEP
│   ├── README.md                   # NEW orientation for docs structure
│   ├── templates/                  # RENAMED from wiki/sources/
│   ├── guides/                     # RENAMED from wiki/topics/
│   └── superpowers/                # KEEP specs + plans + audit
│
├── scripts/                        # KEEP
│   ├── thesis_loop.py
│   ├── thesis_rewriter.py
│   └── thesis_scorer.py
│
└── tests/                          # KEEP
    ├── test_bandit.py              # NEW — unit tests for LinUCB/LinTS/Oracle (currently no such tests exist!)
    ├── test_reward.py              # NEW
    ├── test_preprocessor.py        # NEW
    ├── test_build_presentation.py
    └── test_thesis_*.py
```

---

## Naming standardization recommendations

| Current | Proposed | Reason |
|---|---|---|
| `stress_testing/rl/` | `healthrl/` | "stress_testing" is a holdover from the predecessor (auto insurance / PSI) thesis. The current thesis is health-RL. |
| `case-study/` | `data/cambodia/` | The Cambodia dataset is the primary corpus, not a "case study". |
| `underwriting_bandit.py` | `bandit.py` (in `healthrl/`) | Package namespace already says `healthrl`; "underwriting" is implicit in the project context. |
| `experiment_utils.py` | `_harness.py` | Make the "test-runner-like" role explicit. |
| `chapter2_literature_review.md` | `03_literature_review.md` | Make filename match declared chapter number. |
| `chapter4_results.md` | `06_results.md` | Same. |
| `wiki/sources/` and `wiki/topics/` | `docs/templates/` and `docs/guides/` | "wiki" suggests a published wiki; these are local docs. |
| Three `build_*_presentation.py` files | One `build_presentation.py --theme {burgundy,sothea,default}` | DRY. |

---

## Config-centralization recommendation

Currently the following constants are scattered across 9 files:

```
N_ROUNDS = 5000        # in every exp_*.py
SEED = 42              # primary seed
n_seeds=20             # in every multi-seed call, exp_010 uses 10
alpha=1.0              # LinUCB hyperparameter
v2=1.0                 # LinTS hyperparameter
epsilon=0.15           # ε-greedy
WINDOW = 500           # PSI sliding window (exp_006)
SHOCK_ROUND = 2500     # drift shock (exp_009)
```

Propose a single `healthrl/config.py`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Experiment:
    n_rounds: int = 5000
    n_seeds: int = 20
    primary_seed: int = 42
    psi_window: int = 500
    drift_shock_round: int = 2500

@dataclass(frozen=True)
class Bandit:
    linucb_alpha: float = 1.0
    lints_v2: float = 1.0
    epsilon: float = 0.15

EXPERIMENT = Experiment()
BANDIT = Bandit()
```

Each `exp_*.py` then becomes `from healthrl.config import EXPERIMENT, BANDIT` and uses `EXPERIMENT.n_rounds`, `BANDIT.linucb_alpha`, etc. A single hyperparameter sweep edit no longer requires touching nine files.
