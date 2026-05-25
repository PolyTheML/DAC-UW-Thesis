# Prioritized Improvements

**Date**: 2026-05-25
**Frame**: written from the perspective of an external senior ML researcher / thesis examiner. Numbered items have IDs; refer to them in your follow-up plan.

---

## Tier 1 — CRITICAL (must address before submission)

These are findings that will be raised in defense or that compromise the basic integrity of the thesis.

### IMP-C1. Reconcile chapter numbering and remove duplicates
Eliminate the 9-files-for-6-chapters confusion (see RI-1, RI-2). Decide canonical structure, rename files to match declared chapter numbers, delete the two untracked superseded drafts (`chapter5_results.md`, `chapter6_conclusion.md`), and dedupe Ch II content across `chapter1_introduction.md` and `chapter2_presentation_of_project.md`. **Estimated effort**: 2 hours.

### IMP-C2. Standardize on the 20-seed multi-run methodology
Choose one statistical methodology and rewrite all chapter V/VI tables to use it (see RI-5). Recommend 20-seed mean ± std with 95 % bootstrap CI — what the experiment scripts actually run. Single-seed numbers should be removed or relegated to a "Reproducibility" sidebar. Currently the same statistic has two different reported values, and the conclusion mixes both. **Estimated effort**: 4 hours.

### IMP-C3. Fix the `d = 25` vs `d = 34` contradiction
Find every occurrence of `25` referring to feature dimensionality and change to `34`. Verified locations: ch4_project_analysis.md §4.4.2 ("d = 25 in this implementation"), §4.4.4 item 6 ("d = 25 features"), ch5_conclusion.md §6.3.2 ("For a 25-feature dataset"). Use grep to catch others. **Estimated effort**: 30 minutes.

### IMP-C4. Fix the `ε = 0.10` vs `ε = 0.15` contradiction
Change ch4_results.md §5.3.2 ("With ε = 0.10, the algorithm wastes 10 %") to 0.15 / 15 %. Confirmed via `exp_007:64`. **Estimated effort**: 5 minutes.

### IMP-C5. Resolve the Bastani et al. (2021) citation misapplication
This is the most embarrassing finding (see lit-validation M1 and RI-6). The paper cited does not say what the chapter claims it says. Three options:
1. Replace with a correct citation. For the "bandit finds different-but-profitable policy" claim, consider:
   - Foster & Krishnamurthy (2021) *Efficient First-Order Contextual Bandits* (arXiv 2107.02237) — discusses partial-information settings.
   - Krishnamurthy, Agarwal & Langford (2017) *Contextual Decision Processes with Low Bellman Rank* — discusses what bandits can learn under reduced observability.
   - Or admit no citation and present the claim as your own empirical observation.
2. Reframe the paragraph to honestly describe what Bastani et al. *do* prove (covariate-diversity-driven exploration-free greedy can be rate-optimal), and use it to justify why simple methods often work.
3. Remove the citation entirely.
**Recommend option 2** as the most defensible. **Estimated effort**: 1 hour (including re-reading the Bastani paper to write an accurate two-sentence summary).

### IMP-C6. Add the two missing references to the bibliography
Bastani et al. (2021) and Shadish, Cook & Leviton (1991) appear in chapter bodies but no References list (RI-7). Add to `chapter2_literature_review.md` References section. **Estimated effort**: 10 minutes.

### IMP-C7. Resolve the Shadow Mode contradiction
Chapter 3 §3.6.1 describes Shadow Mode as a recommended Phase-1 deployment with a real implementation in `backend/`. But `.gitignore` line 73 marks `backend/` as "Old backend API (superseded by demo/)" (RI-8). Pick one of:
1. Revive `backend/`: remove the `.gitignore` line, ensure `tests/test_shadow_mode.py` passes, mention in README.
2. Demote ch3 §3.6.1 to a design proposal, remove `backend/` from tracking (`git rm -r backend/ tests/test_shadow_mode.py`), keep the architectural diagram.
**Estimated effort**: 2 hours (option 1) or 30 minutes (option 2).

---

## Tier 2 — IMPORTANT (strengthens credibility; address before submission if time permits)

### IMP-I1. Promote the five undocumented experiments
EXP-009 (drift) / EXP-010 (cold-start) / EXP-011 (ablation) / EXP-012 (sensitivity) / EXP-013 (log-log regret validation) are fully implemented, peer-reviewable experiments that are invisible in the thesis (RI-9). Each is publication-worthy material. Specifically:
- **EXP-011 + EXP-012** directly address the "ablation and sensitivity remain future work" line in ch4_results §5.5.4 — that line is wrong and needs deletion. Promote both into Chapter V.
- **EXP-013** validates the $O(d\sqrt T)$ regret bound empirically via a log-log slope check — this is a *very* strong defensive talking point (you don't just cite the theoretical bound, you verify it on your data). Add as Ch V §5.6.
- **EXP-009** is the empirical foundation for the "DiscountedLinUCB" future work proposal — it shows the recovery happening. Add to Ch V or Ch VI.4.1.
- **EXP-010** (cold start) tells the reviewer how fast the bandit reaches profitability — operationally crucial. Add to Ch V.

This is **the single highest-leverage improvement to thesis strength**. You already have the experiments; you only need 2-3 pages of writing per result. **Estimated effort**: 6-8 hours.

### IMP-I2. Standardise the seed counts
EXP-010 uses `n_seeds=10` (RI-11). Methodology declares 20. Either re-run EXP-010 at 20 seeds or add a footnote justifying 10 (perhaps too computationally expensive for the cold-start range sweep). **Estimated effort**: 30 minutes (footnote) or 1 hour (rerun).

### IMP-I3. Centralize hyperparameters
Currently `N_ROUNDS=5000`, `n_seeds=20`, `alpha=1.0`, `v2=1.0`, `epsilon=0.15`, `WINDOW=500` are duplicated across 9 experiment files. Create `healthrl/config.py` with a frozen dataclass (see structure-overview report). Eliminates the kind of `ε = 0.15` vs `ε = 0.10` drift seen in IMP-C4. **Estimated effort**: 1 hour.

### IMP-I4. Tighten requirements.txt to == pins
For reproducibility, `>=` is insufficient. A reviewer 6 months from now may install a different numpy version that subtly changes a random draw. Use exact pins and check in `pip freeze` output. **Estimated effort**: 15 minutes.

### IMP-I5. Add a top-level README
The repo has CLAUDE.md, AGENTS.md, COLLAB.md but no plain README. A reader landing on the GitHub page should see in 60 seconds: what the thesis is, how to run an experiment, where to find the chapters. **Estimated effort**: 30 minutes.

### IMP-I6. Verify or replace the BIMA "430,000 mobile life policies" claim
This number could not be corroborated by web sources (lit-validation C2). Find the source or replace with a corroborated number. A defending examiner will Google it. **Estimated effort**: 30 minutes.

### IMP-I7. Add unit tests for the bandit core
`tests/` currently covers presentation builders and the thesis-loop scripts but not the bandit algorithms. A 1-hour pass on `tests/test_bandit.py` covering:
- LinUCB Sherman-Morrison update matches direct matrix inversion to numerical tolerance
- LinTS Cholesky cache invalidates correctly after update
- expected_rewards is independent of seed
- Static XGB preprocessor produces 21 features
- preprocess_cambodia_data produces 34 features
…would tighten the load-bearing code and demonstrate engineering rigor. **Estimated effort**: 2 hours.

### IMP-I8. Statistical reporting hygiene
Chapter V reports `mean ± std` and `[95 % CI]` together. Pick one (CI is more informative for inference) or label clearly that ± is std not SE. Currently ambiguous. **Estimated effort**: 1 hour.

---

## Tier 3 — OPTIONAL (publication-level rigor; nice-to-have)

### IMP-O1. Add a real-data validation discussion
Limitation 1 in Ch VI is "synthetic data" but the limitation is somewhat hand-waved. Strengthen by: (a) calibration validation — compare marginal distributions of synthetic dataset to CDHS 2021-22 published tables for the 5 most load-bearing features; (b) sensitivity analysis — re-run EXP-007 with perturbed reward parameters (already implemented in EXP-012, see IMP-I1).

### IMP-O2. Add a baseline that does not use feature engineering
Currently the static baseline (XGBoost) is given the same engineered features as the bandit. A *weaker* baseline (e.g., GLM on raw inputs, or constant-policy "always STANDARD") would show the floor more dramatically. Three-baseline framing is standard in RL papers.

### IMP-O3. Pre-register a confirmatory study
EXP-005 currently passes after exploration of pass criteria. For publication, the gold standard is to pre-register the criteria *before* running EXP-005 on a held-out seed range (e.g., seeds 21-40), then report whether they held. The current setup uses seeds 1-20 both to find the criteria and to confirm them — circular. A pre-registered confirmation block (5 minutes of compute) closes this loop.

### IMP-O4. Compare against a contextual bandit baseline beyond ε-greedy
The benchmark comparison (EXP-007) puts LinUCB and LinTS against ε-greedy and Static XGB. A reviewer at NeurIPS/ICML would ask: how do you compare against more sophisticated context-free baselines (e.g., greedy/Bayesian) or against a simple neural bandit (NeuralLinear)? Adding a NeuralLinear bandit (small MLP feature extractor + LinUCB on top) takes maybe 4 hours but is exactly the "shallow neural" middle ground the thesis already discusses.

### IMP-O5. Quantify the value of the PSI guardrail
EXP-006 verifies that PSI stays GREEN. But it doesn't quantify what would have happened *without* PSI. Run a synthetic counterfactual: inject a known biased exploration policy and show that PSI catches it before the EEOC 4/5 rule does. This converts PSI from "an extra metric we check" to "a metric with demonstrated detection power".

### IMP-O6. Heavy-tailed claim severity
Chapter 5 §5.5.3 (in ch4_results) flags that the simulator uses uniform ±8 % noise rather than a heavy-tailed claims distribution. A small extension (Pareto-tailed multiplicative noise) would test whether the bandit's regret degrades, which is a known weakness of linear UCB methods. Realistic insurance simulation literature uses Pareto or Lognormal.

### IMP-O7. Survival-style delayed rewards
The thesis honestly acknowledges (Ch VI Limitation 2) that single-period rewards are unrealistic. A discounted-reward variant (γ = 0.95) or a 2-period reward (premium - claims_period_1 - claims_period_2) would strengthen the proof-of-concept claim toward operational viability.

### IMP-O8. Compute & cite a thesis-specific regret upper bound
LinUCB has $\tilde O(d\sqrt T)$ regret; ch4_results §5.1.3 invokes this informally. EXP-013 validates the slope empirically. Plug in $d = 34$, $T = 5000$ and compute the actual constant in the bound; compare to your empirical regret. If your empirical regret is well under the bound, that's a positive result; if at the bound, that's interesting too. Either way the thesis tightens.

### IMP-O9. Calibration: dataset documentation as a separate appendix
The `case-study/generate_cambodia_dataset.py` docstring (lines 1-55) is a goldmine of CDHS / STEPS / ILO / WHO calibration sources. Lift this into Appendix A of the thesis. Demonstrates the credibility of the dataset construction in a way the body text doesn't.

### IMP-O10. Cross-validation of the static XGB baseline
The Static XGB model is trained once on 80 % of the data and used as the baseline. A reviewer will ask: was XGB tuned (hyperparameter search)? Did you do cross-validated model selection? Without this, the static baseline is intentionally weakened, making the bandit lift look larger than it should. Either: (a) document that the same baseline was used in the bandit literature for comparability, or (b) run a quick CV-tuned XGB and report the comparison.

---

## Summary table

| Tier | Count | Total effort | Defensibility delta |
|---|---|---|---|
| Critical | 7 items | ~10-12 hours | Closes integrity holes; thesis becomes submission-ready. |
| Important | 8 items | ~12-15 hours | Strengthens credibility; promotes hidden experiments into thesis content. |
| Optional | 10 items | ~30-50 hours | Publication-grade extensions. |

The highest-leverage single improvement is **IMP-I1 (promote the five undocumented experiments)** — you already have the experimental evidence, you just need to write it up. This single act could move the thesis from "competent" to "strong".
