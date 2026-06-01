# Thesis Analysis — Source of Truth for the Demo Revamp

**Date:** 2026-06-01
**Purpose:** Reverse-engineer the thesis so the demo can be aligned to *what the thesis actually claims*. This document is the reference against which `repository_audit.md`, `demo_redesign_spec.md`, and `implementation_plan.md` are written.

**Source of truth:** the markdown chapters in `thesis/health_rl/chapterNN_*.md` (the `.docx` is built from these). Every number below is quoted from those chapters; the demo must match these, not the other way around.

---

## 1. Core Research Problem

Static rule-based / pre-trained underwriting in Cambodia applies one fixed decision boundary to every applicant and never learns from outcomes. This produces three coupled failures (§2.2):

1. **Suboptimal risk selection** — ignores feature interactions (e.g. declines a fit, non-smoking 55-year-old with BMI 31 who is actually a profitable STANDARD risk).
2. **Inability to adapt to portfolio drift** — a model trained in 2023 cannot adjust to a 2026 applicant pool.
3. **Fairness / demographic parity** — accuracy-optimised static models can systematically exclude rural applicants / garment workers (≈700k garment workers, 85% women; ≈2.5m rice farmers).

Market context (§2.1): <2% insurance penetration, >100% mobile penetration, ~80% of adults on digital payments — i.e. the bottleneck is the underwriting decision engine, not distribution.

## 2. Research Objectives (§2.3)

- **Primary:** design, implement, and empirically validate a contextual bandit framework that beats static rule baselines on cumulative profitability *while* maintaining regional/occupational fairness on a synthetic Cambodia dataset.
- **Secondary:** (1) build a reproducible CDHS-anchored 2,000-applicant dataset; (2) implement & compare LinUCB, LinTS, Epsilon-Greedy vs Static XGB; (3) design PSI fairness guardrails; (4) run a fairness audit against the EEOC four-fifths (80%) rule.

## 3. Hypotheses / Research Questions (§2.3, §4.9)

| RQ | Question | Experiment |
|----|----------|-----------|
| **RQ1** | Do LinUCB/LinTS beat Static XGB on cumulative reward & regret? | EXP-005 |
| **RQ2** | Is demographic fairness preserved (parity + PSI) *without* an explicit fairness term in the reward? | EXP-006 |
| **RQ3** | What is the ranking LinTS ≤ LinUCB ≤ ε-Greedy ≤ Static XGB, and why? | EXP-007 |
| **RQ4** | Is the framework deployable on low-resource mobile infra, and what is the rollout path? | §4.10 / EXP-008 |

## 4. Methodology (§5.0, §4.9)

- **20 independent seeds (1–20)**, **N = 5,000 rounds** per seed for all headline numbers (§5.1–5.4, 5.6, 5.7, 5.9). Two supplementary experiments use **10 seeds/cell** by design (§5.8 sensitivity, §5.10 cold-start).
- Tables report **mean ± std with 95% bootstrap CI**; pairwise tests are **paired Wilcoxon signed-rank** with **Bonferroni correction**; effect size = **Cohen's d**.
- **Primary illustrative seed = 42** (trajectory figures only).
- Every experiment script exits 0 iff pre-registered pass criteria hold (CI-ready).

> **Critical distinction for the demo:** seed 42 ≠ the 20-seed headline. Seed 42 gives LinUCB 95,872 vs Static 75,067 (**+27.7%**). The *thesis claim* is the 20-seed mean **+25.2%** (90,540 vs 72,292). Any live single-seed run is **illustrative**, never the headline.

## 5. System Architecture (§4.4.3)

Browser tabs → FastAPI endpoints → six backend modules (Actuarial Reward Simulator, Pricing Engine, Bandit Algorithms, PSI Compute, Cambodia Dataset, Static XGB Baseline). The isolated decision loop: context `x_t` → action selection → reward `r_t` → rank-one update of `(A_a, b_a)` → next round.

Stack (§4.3, **fixed by the thesis**): Python 3.11, FastAPI, Uvicorn, Pydantic, NumPy, Pandas, scikit-learn, XGBoost; frontend = **HTML5/CSS3 + vanilla ES6 JS + Chart.js 4 + Jinja2**; Matplotlib for static figures; Render free tier. *Introducing React/Vue would manufacture a thesis↔implementation mismatch — do not.*

## 6. Data Flow

Applicant (34-dim z-scored context: demographics, lifestyle, social determinants, economic, 7 clinical flags, condition_count, 8-region one-hot, 7-occupation one-hot) → bandit selects action ∈ {STANDARD, RATED, DECLINE, REFER} → actuarial reward simulator returns profit → bandit updates `(A_a,b_a)` → PSI computed on a 500-round sliding window over the *approved* portfolio (STANDARD+RATED) vs the fixed 2,000-record reference.

## 7. Algorithms / Models (§4.6)

- **LinUCB** (Li et al. 2010), α=1.0; Sherman–Morrison O(d²) updates.
- **LinTS** (Agrawal & Goyal 2013), v²=1.0; cached Cholesky sampling.
- **Epsilon-Greedy**, ε=0.15 (literature default).
- **Static XGB baseline** — XGBoost mortality-multiplier predictor (21 label-encoded features, 1,600-record train) + deterministic rule engine: R1 m≤1.5→STANDARD; R2 1.5<m≤2.2→RATED; R3 2.2<m≤2.6→REFER; R4 m>2.6→DECLINE. `update()` is a no-op.
- **Oracle** — always picks the max-expected-reward action (ceiling).

Reward design (§4.7): P_base = 200·m, C_exp = 150·m; adverse-selection ×1.35 for m>2.0 on STANDARD; acceptance p = max(0.05, 0.95 − 3.5·p_monthly/income); DECLINE = −10; REFER = 0.70·max(others) − 35; processing cost −25 / walk cost −20.

## 8. Experimental Pipeline (EXP-005 … EXP-013)

| Exp | Topic | Headline result (20-seed unless noted) |
|-----|-------|----------------------------------------|
| **EXP-005** | Convergence | LinUCB 90,540 vs Static 72,292 = **+25.2%**, p<0.001, d=2.98; late regret 2.20 vs 9.01; entropy 1.314→1.105; action accuracy 37.8% (>30%). |
| **EXP-006** | Fairness | Region parity **85.72%**, occupation **90.12%** (both ≥80% EEOC); max sliding PSI region **0.082 (GREEN)**, occupation **0.123 (AMBER)**; region permutation p=0.13 (indep.), occupation p<0.001 (assoc. but within threshold). |
| **EXP-007** | Benchmark | LinTS 93,572 / LinUCB 91,947 (n.s., p=0.87) ≫ ε-Greedy 76,441 ≫ Static 72,173; Oracle 126,318. |
| **EXP-008** | HITL | c=0.7: **102,100 vs 95,872 = +6.5%**; review cost 2,625 (2.6%); 75/5,000 referrals (1.5%); zero queue depth; alignment 60%. |
| **EXP-009** | Drift shock | Post/pre regret ratio 0.29× (LinUCB/LinTS) vs 0.85× (Static); convergence-confound caveat (§5.9.3). |
| **EXP-010** | Cold start | FreshXGB wins at T≤500; crossover between T=1,000 and 2,000 (bandits win at 2,000). |
| **EXP-011** | Ablation | No-REFER & Greedy-only (α=0) ≈ Full LinUCB (n.s.); both ≫ Static. **Load-bearing = online linear updating, not the UCB bonus.** |
| **EXP-012** | Sensitivity | LinUCB > Static at every α, adverse factor, elasticity slope; α=1.0 regret-minimising. |
| **EXP-013** | Regret bound | Log-log slope 0.572 (R²=0.99) → 0.511 at burn-in 1,000; validates Õ(d√T). |

## 9. Evaluation Metrics

Cumulative reward; cumulative & late-window regret; action entropy (exploration→exploitation); action accuracy vs Oracle; approval-rate parity (EEOC 4/5); sliding-window PSI (GREEN<0.10 / AMBER 0.10–0.25 / RED>0.25); permutation independence p-values; HITL alignment / override / human-cost / queue depth; log-log regret slope.

## 10. User Workflow (the demo must let a reviewer *do* this)

Inspect an applicant → see expected reward for all 4 actions → watch a bandit learn (single seed, illustrative) → see the canonical 20-seed claim → compare algorithms → audit fairness/PSI → act as the human-in-the-loop reviewer → inspect per-action coefficients (interpretability) → understand the deployment path (Shadow→Assisted→Automated).

## 11. Key Thesis Contributions (§6, Closing scene)

1. **Cambodia-calibrated synthetic dataset** anchored on CDHS 2021-22 / STEPS 2023 / ILO 2023 / WHO.
2. **Decoupled fairness architecture** — PSI + approval-parity as *external* guardrails, preserving regret guarantees (vs constrained-reward formulations).
3. **HITL wrapper with the "dual-update" insight** — update both the human-chosen action *and* the REFER arm so REFER never becomes a dead action; +6.5% at 2.6% cost.
4. **Reproducible experimental harness** — pre-registered hypotheses, fixed seeds, deterministic JSON reports, CI pass/fail.

## 12. Claimed Innovations (novelty positioning, per audit §novelty)

The genuinely novel pieces are **(2) PSI-as-external-fairness-guardrail** and **(3) the HITL dual-update**. The emerging-market application and the "linear suffices for low-dimensional actuarial problems" finding (§5.5.2, reinforced by the EXP-011 ablation) are the supporting narrative. *These two should be visually unmistakable in the demo.*

## 13. Results Demonstrated in the Thesis

The four findings of §6.1: (1) bandits beat static by 25% (d=2.98); (2) fairness preserved with no explicit constraint; (3) adaptive linear estimation — any exploration wrapper — beats non-adaptive; (4) HITL adds 6.5% at low cost.

---

## What the demo must communicate (synthesis)

**Essential (defense-critical):**
- The problem framing (1% problem) and why static rules fail.
- The **canonical 20-seed headline** (+25.2%, p<0.001, d=2.98) shown as authoritative, distinct from any live single-seed run.
- The **fairness result with the correct EEOC 80% rule** and correct PSI values (region 0.082 GREEN, occupation 0.123 AMBER; parity 85.7%/90.1%).
- The **interpretability / coefficient audit** (NFR-7) — linear bandits expose θ_a.
- The **HITL** loop with headline c=0.7 numbers.
- The benchmark ranking + the Õ(d√T) regret validation (EXP-013).

**Optional / supporting (nice-to-have, lower priority for an imminent defense):**
- Live drift injection (EXP-009 real figure beats fabricated curves).
- Cold-start (EXP-010), ablation (EXP-011), sensitivity (EXP-012) as "depth on demand."
- The full premium-optimiser sandbox and batch portfolio tools (already work; keep).

**Evidence required to support each claim:** pre-computed 20-seed artifacts (JSON/figures) for every headline number; the existing thesis figures (`fig_reward_curves`, `fig_fairness_region/occupation`, `fig_loglog_regret`, `fig_hitl_experiment`, `fig_009_drift_adaptation`); `coefficients_linucb_seed42.json` for interpretability. Live API runs are framed as *illustrative*, and any PSI shown live must match EXP-006 to 4 d.p. (NFR-6).
