# DAC-UW-Thesis — Adaptive Health Insurance Underwriting via Contextual Bandits

Master's thesis at ITC (Institut de Technologie du Cambodge): a contextual bandit framework for health insurance underwriting in Cambodia, with PSI-based fairness guardrails and a human-in-the-loop extension.

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) regenerate the synthetic dataset deterministically
python data/cambodia/generate_cambodia_dataset.py

# (Optional) retrain baseline models (XGBoost + GLM)
python data/cambodia/train_cambodia_models.py

# Run the headline experiment (LinUCB convergence vs Static XGB, 20 seeds, ~5-10 min)
python healthrl/experiments/exp_005_underwriting_convergence.py

# Launch the live demo dashboard locally
uvicorn demo.main:app --reload --port 8000
```

## Repository layout

| Path | Purpose |
|---|---|
| `healthrl/` | Core bandit package: LinUCB, LinTS, ε-Greedy, StaticXGB, Oracle, reward simulator, preprocessor |
| `healthrl/config.py` | Central hyperparameters (`EXPERIMENT`, `BANDIT`) |
| `healthrl/experiments/` | 9 experiments (EXP-005 to EXP-013) with pre-registered pass criteria + exit codes |
| `data/cambodia/` | Synthetic CDHS-anchored applicant dataset (2,000 records) + trained baseline models |
| `demo/` | FastAPI actuarial dashboard (Render-deployed) |
| `thesis/health_rl/` | Chapter sources + figures + docx/pptx builders |
| `scripts/` | Thesis automation loop (chapter scoring + rewriting) |
| `wiki/` | ITC writing templates and topic guides |
| `docs/superpowers/` | Specs, plans, audits |

## Reproducibility

- **Methodology**: 20 independent seeds (1–20), `N = 5,000` rounds per seed, bootstrap 95 % confidence intervals, paired Wilcoxon signed-rank tests with Bonferroni correction, Cohen's d for effect sizes.
- **Primary seed for trajectory figures**: SEED = 42.
- **Exit codes**: every `exp_*.py` exits 0 if pass criteria satisfied, 1 otherwise — suitable for CI.
- **Hyperparameters**: defined once in `healthrl/config.py` (`EXPERIMENT`, `BANDIT` dataclasses). Sweep experiments (EXP-011 ablation, EXP-012 sensitivity) intentionally override these.

## Thesis structure

| Chapter | File |
|---|---|
| I. Introduction | `thesis/health_rl/chapter01_introduction.md` |
| II. Presentation of the Project | `thesis/health_rl/chapter02_presentation.md` |
| III. Literature Review | `thesis/health_rl/chapter03_literature_review.md` |
| IV. Project Analysis (includes methodology §§4.5-4.10) | `thesis/health_rl/chapter04_project_analysis.md` |
| V. Results and Discussion | `thesis/health_rl/chapter05_results.md` |
| VI. Conclusion | `thesis/health_rl/chapter06_conclusion.md` |

Build the docx draft:
```bash
python thesis/health_rl/build_thesis_docx.py
```

## Headline results (EXP-005, EXP-007, 20 seeds)

| Algorithm | Cumulative Reward | Cumulative Regret |
|---|---|---|
| LinTS | $93,572 ± 6,229 | $21,149 ± 6,458 |
| LinUCB | $91,947 ± 6,439 | $22,774 ± 6,627 |
| Epsilon-Greedy | $76,441 ± 6,250 | $38,281 ± 6,320 |
| Static XGB | $72,173 ± 4,997 | $42,548 ± 4,970 |

LinUCB vs Static XGB on cumulative reward: +25.2 % (p < 0.001, Cohen's d = 2.98). LinTS vs LinUCB: not significantly different (p = 0.87) — for production deployment, prefer LinTS for parameter-free operation.

## License

[TBD by candidate]
