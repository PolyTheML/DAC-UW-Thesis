# Research Integrity Report — Code ↔ Thesis Cross-check

**Date**: 2026-05-25
**Scope**: All 9 chapter files in `thesis/health_rl/chapter*.md` vs. all source under `stress_testing/rl/`, `case-study/`, `demo/`, `backend/`.

---

## Severity legend

- 🔴 **CRITICAL** — Internal contradiction between chapters, or numeric disagreement, or unimplemented claim. Will be flagged in defense.
- 🟡 **IMPORTANT** — Inaccuracy that weakens credibility but is not load-bearing.
- 🟢 **MINOR** — Cosmetic / pedagogical clarity issue.

---

## 1. Chapter-file structure (🔴 CRITICAL)

The thesis directory contains **9 chapter files** that cover **6 ITC chapters** with overlap and ambiguity:

| File | Header it declares | Tracked? | Status |
|---|---|---|---|
| `chapter1_introduction.md` | Ch I + Ch II | tracked, modified | Carries both Ch I (Introduction) and Ch II (Presentation) content in one file. |
| `chapter2_presentation_of_project.md` | Ch II | tracked | Stand-alone Ch II. **Duplicates content already in `chapter1_introduction.md` lines 51-150.** |
| `chapter2_literature_review.md` | Ch II → Ch III (with disclaimer note) | tracked, modified | Filename says "ch2" but content is the **canonical Ch III**. |
| `chapter3_methodology.md` | **Ch III METHODOLOGY** | tracked, modified | Also claims to be Ch III — conflicts with `chapter2_literature_review.md`. Methodology has no slot in current ITC structure. |
| `chapter4_project_analysis.md` | Ch IV | tracked | Canonical Ch IV (Requirements & Technology). |
| `chapter4_results.md` | **Ch V RESULTS AND DISCUSSION** | tracked, modified | Filename says "ch4" but content is the **canonical Ch V**. Uses 20-seed statistics. |
| `chapter5_results.md` | Ch V RESULTS AND ANALYSIS | **untracked** | Older single-seed version of Ch V. Superseded. |
| `chapter5_conclusion.md` | **Ch VI CONCLUSION** | tracked, modified | Filename says "ch5" but content is the **canonical Ch VI**. Uses 20-seed statistics. |
| `chapter6_conclusion.md` | Ch VI CONCLUSION | **untracked** | Alternate conclusion that **mixes single-seed and 20-seed numbers** — internally inconsistent. |

**Critical actions:**
1. **Decide canonical chapter structure**. The most coherent reading: Ch I (chapter1), Ch II (chapter2_presentation_of_project), Ch III (chapter2_literature_review), Ch IV (chapter4_project_analysis), Ch V (chapter4_results), Ch VI (chapter5_conclusion). This leaves **`chapter3_methodology.md` orphaned** — yet its content (datasets, algorithms, reward design, PSI) is essential and not covered by Ch IV. Either insert it as Chapter IV with the current "Project Analysis" becoming Ch V (and renumber Results to Ch VI, Conclusion to Ch VII), or fold methodology into Ch IV.
2. **Remove duplicate Ch II content from `chapter1_introduction.md`** (lines 51-150). It is identical in spirit to `chapter2_presentation_of_project.md`. Leaving both creates contradiction risk.
3. **Delete the untracked `chapter5_results.md` and `chapter6_conclusion.md`** after archiving them (they are superseded but were never committed). The `chapter6_conclusion.md` in particular is dangerous because its Finding 4 mixes single-seed and 20-seed numbers in the same paragraph.
4. **Rename canonical chapter files** to match their declared chapter numbers (e.g., `chapter4_results.md` → `chapter5_results.md`) so that the filename ordering matches the chapter ordering. Currently the alphabetical sort order is misleading.

---

## 2. Numeric inconsistencies between chapters (🔴 CRITICAL)

Multiple key quantities have **two different reported values** depending on which chapter you read:

| Quantity | Value A (source) | Value B (source) | Code says | Resolution |
|---|---|---|---|---|
| Feature dimension $d$ | **34** (ch3 §3.1.2, ch5_concl §6.3) | **25** (ch4 §4.4.2, §4.4.4 item 6; ch5_concl §6.3.2) | **34** — confirmed by counting `preprocess_cambodia_data()` outputs: 12 + 7 + 8 + 7 = 34 | **Use 34 everywhere**. Fix all "25" occurrences in ch4_project_analysis.md and ch5_concl §6.3.2. |
| Epsilon (ε-greedy) | **0.15** (ch3 §3.2.3, ch5_results §5.3.2) | **0.10** (ch4_results §5.3.2) | **0.15** — `exp_007_benchmark_comparison.py:64` instantiates `EpsilonGreedy(..., epsilon=0.15, ...)` | **Use 0.15**. The 0.10 in ch4_results §5.3.2 is wrong (and inconsistent with that chapter's own ε wording). Note: `underwriting_bandit.py:490` default is 0.1, but experiments override it. |
| LinUCB cumulative reward | **$90,540 (20 seeds, mean ± std)** (ch4_results §5.1.1, ch5_concl Finding 1) | **$95,872 (seed 42)** (ch5_results §5.1.1, ch5_concl Finding 4, ch6_concl multiple) | Both numbers come from real runs. ch4_results uses 20-seed mean; ch5_results uses seed 42 only. | **Standardize on 20-seed mean ± std with 95 % CI**. Single-seed numbers should be removed from final-thesis text or labeled as "primary seed = 42 illustrative run". Ch5_concl currently violates this by quoting both styles in different findings. |
| LinTS cumulative reward | **$93,572 (20 seeds)** | **$101,266 (seed 42)** | Same — methodology difference. | Same as above. |
| Region PSI (EXP-006) | **0.0821 max sliding-window (20 seeds)** | **0.0050 final-state (seed 42)** | Same — definition difference (max sliding-window vs final-state). | These are **different metrics**, not contradictions, but the thesis presents them as if both are "the PSI for region". Always disambiguate: "max 500-round sliding-window PSI = X" vs "end-of-run PSI = Y". |
| LinUCB reward lift over Static XGB | **+25.2 %** (ch4_results, ch5_concl) | **+27.7 %** (ch5_results, ch6_concl) | Different baselines per methodology. | Same. Standardize. |

**Action**: For each table and headline statistic in chapters V and VI, decide whether the canonical methodology is **20-seed multi-run** (more rigorous, what the experiment scripts actually run) or **single-seed=42 illustrative**. Recommend 20-seed everywhere; reserve seed-42 numbers for the "Reproducibility" sidebar. Anything else invites the examiner to ask which figure is correct.

---

## 3. Code-thesis claim mismatches (🟡 IMPORTANT)

| Claim | Where in thesis | Code state | Status |
|---|---|---|---|
| "Shadow Mode (Phase 1)" deployment is described in ch3 §3.6.1 as a recommended production rollout phase, with sufficient-statistic updates from static-rule outcomes. | ch3 §3.6.1 | Implemented in `backend/shadow/` (router, service, database, models, schemas). **But `backend/` is gitignored as "Old backend API (superseded by demo/)"** (.gitignore line 73). | Thesis presents shadow mode as live design; code says backend is deprecated. Either reactivate `backend/shadow/` and remove the .gitignore line, or rewrite ch3 §3.6.1 to present shadow mode purely as a design proposal. |
| Static XGB rule thresholds (ch3 Table 3.2.4): ≤1.5 STANDARD, ≤2.2 RATED, ≤2.6 REFER, >2.6 DECLINE. | ch3 §3.2.4 | Exactly matches `underwriting_bandit.py:580-586`. | ✅ Verified |
| Reward parameters: $200 base, $150 expected claims, adverse factor 1.35 above m=2.0, accept slope 3.5, decline -$10, refer 0.70 × max - $35, walk -$20, processing -$25, noise ±8 %. | ch3 §3.3.1-3.3.3 | All match `RewardConfig` dataclass exactly. | ✅ Verified |
| Sherman-Morrison O(d²) update for LinUCB / LinTS / ε-greedy. | ch3 §3.2.1 | Implemented exactly as described in all three classes. | ✅ Verified |
| EXP-005 hypothesis: action accuracy > 30 % "not oracle convergence but discovery of distinct profitable policy". Citation: Bastani et al. 2021. | ch3 §3.5.1, ch4_results §5.1.3 | Confirmed in `exp_005_underwriting_convergence.py:178-184`. **However the citation does not support the claim** (see lit-validation report M1). | 🔴 Citation misapplied — needs fix. |
| "20 seeds (1–20)" multi-seed analysis. | ch3 §3.5.4 | `n_seeds=20` confirmed in exp_005, exp_006, exp_007, exp_009, exp_011, exp_012. Exception: `exp_010_cold_start_analysis.py:252` uses **`n_seeds=10`** for the cold-start scan. | 🟡 Note this — either rerun exp_010 at 20 seeds or footnote the exception. |
| Common random numbers used in EXP-007 (acceptance draws and claims noise shared across algorithms). | ch3 §3.5.3 | Confirmed in `exp_007_benchmark_comparison.py:55-58`. | ✅ Verified |

---

## 4. Experiments described vs. experiments implemented (🟡 IMPORTANT)

| Experiment | In thesis? | In code? | Comment |
|---|---|---|---|
| EXP-005 Convergence | ✅ Yes (ch3, ch4_results §5.1, ch5_concl) | ✅ `exp_005_underwriting_convergence.py` | Aligned. |
| EXP-006 Fairness | ✅ Yes | ✅ `exp_006_fairness_audit.py` | Aligned. |
| EXP-007 Benchmark | ✅ Yes | ✅ `exp_007_benchmark_comparison.py` | Aligned. |
| EXP-008 HITL | ✅ Yes (ch4_results §5.4, ch5_concl Finding 4) | ✅ `exp_008_human_in_the_loop.py` | Aligned. |
| EXP-009 Drift adaptation | ❌ Not described in any chapter | ✅ `exp_009_drift_adaptation.py` | **Unused implementation**. Ch5_concl §6.3.1 mentions DiscountedLinUCB as *future work*, but the code already implements + tests it. Promote to Chapter V results, or delete from code as dead. |
| EXP-010 Cold-start | ❌ Not described | ✅ `exp_010_cold_start_analysis.py` (10 seeds) | Same — undocumented working experiment. |
| EXP-011 Ablation study | ❌ Not described | ✅ `exp_011_ablation_study.py` | Ch4_results §5.5.4 says "A full grid-search sensitivity analysis (α ∈ [0.1, 5.0], …) remains future work." Yet `exp_012_sensitivity_analysis.py` does this. **Direct contradiction** — the "remains future work" line is wrong. |
| EXP-012 Sensitivity analysis | ❌ Not described | ✅ `exp_012_sensitivity_analysis.py` | See above. |
| EXP-013 Log-log regret validation | ❌ Not described | ✅ `exp_013_loglog_regret_validation.py` | Ch4_results §5.1.3 says "regret curve grows approximately as $O(\sqrt{t})$" but doesn't cite the validating experiment. Promote EXP-013 results into Ch V. |

**Action**: 5 experiments are implemented but invisible in the thesis. This is a missed opportunity for thesis strength (and a documentation debt). For each of EXP-009 / 011 / 012 / 013, either add a Chapter V results subsection, or move the code to `stress_testing/rl/experiments/_unused/` to make the discrepancy explicit.

---

## 5. Figure ↔ source mapping (🟢 MINOR)

I verified each `[FIGURE: …]` reference resolves to a file:

| Reference | Path | Exists? |
|---|---|---|
| `fig_reward_curves.png` | `thesis/health_rl/figures/` | ✅ |
| `fig_action_evolution.png` | same | ✅ |
| `fig_fairness_region.png` | same | ✅ |
| `fig_fairness_occupation.png` | same | ✅ |
| `fig_regret_curves.png` | same | ✅ |
| `fig_hitl_experiment.png` | same | ✅ |
| `fig_framework.png` | same | ✅ |
| `fig_ch4_architecture.png` / `fig_ch4_bandit_loop.png` | same | ✅ |
| `fig_ch2_system_architecture.png` / `_timeline.png` | same | ✅ |
| `fig_organization_chart.png` | same | ✅ |
| `fig_009_drift_adaptation.png` / `fig_010_cold_start.png` / `fig_loglog_regret.png` | same | ✅ exist on disk but **not referenced** by any chapter — orphan figures generated by the undocumented experiments. |

The eda_* figures (14 of them) appear to be EDA outputs generated by `thesis/health_rl/generate_eda_figures.py` but only `fig_eda_*` are stored on disk; no chapter currently embeds them. Either embed in Ch III (data section) or move to an appendix.

---

## 6. Reproducibility assessment (🟢 MINOR)

| Aspect | Status |
|---|---|
| Fixed seeds | ✅ All experiments take a `seed` parameter; multi-seed harness fixes SEED=42 primary and 1-20 multi. |
| Dataset reproducible from source | ✅ `case-study/generate_cambodia_dataset.py` regenerates `cambodia_dataset.csv` from documented CDHS/STEPS/ILO parameters. |
| Models reproducible from source | ✅ `case-study/train_cambodia_models.py` retrains XGBoost + GLM; pickled artifacts in `case-study/models/`. |
| Software versions pinned | ⚠ `requirements.txt` exists but uses lower-bound pins (`>=`) rather than exact versions; this is fine for thesis reproducibility but should be `==` for exact replication. |
| Statistical scripts deterministic | ✅ `experiment_utils.py` and `statistical_utils.py` use fixed bootstrap seeds. |
| Pre-registered hypotheses | ✅ Each `exp_*.py` has a top-level docstring listing the pass criteria before main(). Good practice. |

**Reproducibility verdict**: **High** for the implemented experiments. A reviewer can clone the repo, `pip install -r requirements.txt`, `python case-study/generate_cambodia_dataset.py`, and re-run any `exp_*.py` to reproduce the numbers in the 20-seed chapter version.

---

## 7. Summary table of integrity issues

| ID | Severity | Description | Where |
|---|---|---|---|
| RI-1 | 🔴 | 9 chapter files for 6 ITC chapters; duplicates & filename/header mismatches | structure |
| RI-2 | 🔴 | `chapter6_conclusion.md` mixes 20-seed and single-seed numbers in adjacent findings | ch6_concl |
| RI-3 | 🔴 | `d=34` vs `d=25` contradiction across chapters | ch4 §4.4.2, ch5_concl §6.3 |
| RI-4 | 🔴 | `ε=0.15` vs `ε=0.10` contradiction | ch4_results §5.3.2 |
| RI-5 | 🔴 | LinUCB reward = $90,540 (20-seed) vs $95,872 (seed-42); same for LinTS, PSI, lift | chs V & VI |
| RI-6 | 🔴 | Bastani et al. 2021 cited 3× to support claim the paper does not make | ch3, ch4_results, ch5_concl |
| RI-7 | 🔴 | Bastani 2021 & Shadish 1991 cited in body but missing from any References list | bibliography |
| RI-8 | 🟡 | Shadow Mode described in ch3 §3.6.1 but `backend/` is gitignored as deprecated | ch3 §3.6.1 |
| RI-9 | 🟡 | EXP-009/010/011/012/013 implemented but undocumented | code vs thesis |
| RI-10 | 🟡 | "Ablation/sensitivity remains future work" claim in ch4_results §5.5.4 but exp_011/012 already do them | ch4_results §5.5.4 |
| RI-11 | 🟡 | EXP-010 uses 10 seeds while methodology declares 20 | exp_010 |
| RI-12 | 🟡 | BIMA "430,000 policies in 18 months" stat unverified | ch1 |
| RI-13 | 🟢 | NIS/ICF CDHS citation omits MoH co-publisher | ch2 refs |
| RI-14 | 🟢 | EDA figures generated but not embedded in any chapter | figures dir |
| RI-15 | 🟢 | `requirements.txt` uses `>=` not `==` pins | repo root |
