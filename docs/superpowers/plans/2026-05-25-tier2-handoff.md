# Tier-2 Session Handoff

**Date written**: 2026-05-25
**Branch base for next session**: `main` at `6f08820` (last Tier-1 commit)

## What's done (Tier-1, this session)

13 commits between `cb32b9e` and `6f08820`. Audit findings IMP-C1..C7 (critical) and IMP-S1..S4 (structural) all resolved. Repo is **submission-ready** per final reviewer. See `docs/superpowers/audit/2026-05-25/` (full audit) and `docs/superpowers/plans/2026-05-25-tier1-critical-fixes.md` (the plan that was executed).

Current state in one paragraph: 6 zero-padded chapter files (`chapterNN_*.md`); methodology folded into Ch IV §§4.5–4.10; all stats in chs V & VI use 20-seed methodology; references list correct; Shadow Mode demoted to design proposal; `backend/` removed; `stress_testing/rl/` → `healthrl/`; `case-study/` → `data/cambodia/`; hyperparameters live in `healthrl/config.py`; new `README.md`; updated `CLAUDE.md`. `EXP-005: PASS` confirmed.

---

## Tier-2 work, ranked by leverage

### 1. IMP-I1 — Write up EXP-009/010/011/012/013 into Ch V *(highest impact)*

**Why first**: the experiments already exist and pass. The thesis under-claims its own evidence. Ch V §5.5.4 currently says "ablation / sensitivity remains future work" — that statement is *factually wrong* because `exp_011` (ablation) and `exp_012` (sensitivity) both run today. A defense examiner will ask "did you do an ablation?" and you can either answer "no, future work" (current state, weak) or "yes, here are the results" (after this fix, strong).

**Scope** (~6-8 hours total, ~1-2 hours per experiment write-up):

| Experiment | What to add to Ch V | Suggested section |
|---|---|---|
| EXP-013 log-log regret | Empirical validation that regret grows as $O(d\sqrt T)$ — bandit theory check | new §5.6 |
| EXP-011 ablation | Table comparing LinUCB-full vs 3-arm vs greedy-only (α=0) | new §5.7 |
| EXP-012 sensitivity | α sweep curve, adverse_factor sweep, acceptance-elasticity sweep | new §5.8 |
| EXP-009 drift adaptation | DiscountedLinUCB recovery curve after mid-run shock — supports the future-work narrative in Ch VI §6.3.1 (this then becomes "preliminary results", not pure future work) | new §5.9 |
| EXP-010 cold-start | When does each algorithm cross the profitability threshold? Operationally crucial. | new §5.10 |

**Where to start**: run each `python healthrl/experiments/exp_NNN_*.py` to confirm current pass-state. Each produces stdout with the headline statistics — those become the canonical numbers for the writeup. Some have figures already (`fig_009_drift_adaptation.png`, `fig_010_cold_start.png`, `fig_loglog_regret.png` — currently orphan figures in `thesis/health_rl/figures/`, ready to embed).

**Delete the wrong claim**: while you're in Ch V, remove the "remains future work" line in §5.5.4 (now wrong).

### 2. IMP-I7 — Bandit-core unit tests *(~2 hours)*

`tests/` covers the thesis-loop scripts and presentation builders but **not** the algorithms themselves. Recommended `tests/test_bandit.py`:

```python
# Test cases
- LinUCB Sherman-Morrison update equals direct (A + xxᵀ)⁻¹ to 1e-10
- LinTS Cholesky cache invalidates correctly after update (sample differs after observed reward)
- LinTS sample shape == n_features, mean ≈ posterior mean over many draws
- expected_rewards() is deterministic across calls (same input → same output)
- preprocess_cambodia_data() returns X.shape == (2000, 34)
- StaticXGBBaseline's _preprocess_row returns shape (1, 21)
- RewardConfig defaults: base_premium=200, decline=-10, refer_admin=35
- _compute_reward at DECLINE returns -10 exactly
- run_bandit with deterministic seed reproduces identical results across runs
```

A passing `tests/test_bandit.py` would have caught the Task 11 SHOCK_ROUND discrepancy (1500 vs 2500) AND the NFR-8 contradiction flagged by final review. Cheap insurance for the whole codebase.

### 3. IMP-I4 — Pin `requirements.txt` to `==` *(~15 min)*

```bash
pip freeze > requirements-lock.txt
# Then manually transcribe the actually-used pins back into requirements.txt
```

Currently uses `>=` pins. A reviewer 6+ months from now installing fresh dependencies may get a numpy that subtly changes a random draw → reproducibility breaks. The deployed `demo/` on Render also benefits.

### 4. IMP-I6 — Verify BIMA "430,000 mobile life policies in 18 months" claim *(~30 min)*

Ch I §1.2 cites this number from "BIMA (2022)" but web search could not corroborate it. The actual BIMA + Smart Axiata partnership figures circulating in trade press are different (cumulative "1 million Cambodians" over multiple years; "350,000 customers" at one point). Either:
- Find the exact BIMA report page and pin the citation, or
- Replace with a corroborated number from Khmer Times / BIMA press archives, or
- Soften to "hundreds of thousands of mobile micro-policies".

A defense examiner *will* Google this.

### 5. IMP-I2 — EXP-010 seed count *(~5 min footnote, or ~1 h rerun)*

`exp_010_cold_start_analysis.py` uses `n_seeds=10` (with comment); methodology declares 20. When IMP-I1 promotes EXP-010 into Ch V, decide: add a footnote justifying the divergence, or re-run at 20 seeds. Footnote is cheaper and honest.

### 6. IMP-I8 — Statistical reporting hygiene *(~1 hour)*

Ch V tables mix `mean ± std` and `[95% CI]` notations in the same row. Pick a convention or label clearly that `±` is std (not SE). Some readers will interpret `±` as SE and get the CI width wrong.

---

## Smaller items flagged by final reviewer

- **`thesis/health_rl/build_presentation_sothea_format.py:711`** still contains a `ε=0.10` literal. Not a thesis-facing file (it's a presentation builder variant), but worth fixing for consistency. 5 min.
- **`wiki/topics/thesis-defense-stress-testing-framework.md`** still has `stress_testing` references. Wiki context, not load-bearing. Optional rename to match new structure.
- **`SHOCK_ROUND = 1500` in code vs `2500` in (old) plan spec.** Task 11 implementer chose code value. Verify no chapter cites `2500` — if so, align.

---

## Operating recommendation for the next session

1. **Start with**: `python healthrl/experiments/exp_011_ablation_study.py` and `python healthrl/experiments/exp_013_loglog_regret_validation.py`. Capture the headline numbers.

2. **Then write**: Ch V §§5.6, 5.7, 5.8 (log-log regret, ablation, sensitivity) — these are the three experiments most readily defensible. Each is ~1-2 pages.

3. **Then write**: §§5.9, 5.10 (drift, cold-start) — these need slightly more contextualisation because they involve concepts not previously introduced in Ch IV (DiscountedLinUCB, profitability-crossover round).

4. **In parallel**: while chapter writing is happening, dispatch a subagent (or do inline) for IMP-I7 unit tests and IMP-I4 pinned requirements — both are mechanical and don't conflict with chapter edits.

5. **Defer to Tier-3** (publication polish, not submission-blocking):
   - NeuralLinear baseline (IMP-O4)
   - Real-data validation discussion (IMP-O1)
   - Heavy-tailed claims (IMP-O6)
   - Pre-registered confirmation study (IMP-O3)
   - PSI guardrail value experiment (IMP-O5)

---

## Useful invocations to start the session

```bash
# Re-orient
cat docs/superpowers/audit/2026-05-25/05-improvements.md
git log --oneline -15

# Verify nothing has regressed since the Tier-1 baseline
python healthrl/experiments/exp_005_underwriting_convergence.py 2>&1 | tail -3

# Read the previous plan to see what's already done
cat docs/superpowers/plans/2026-05-25-tier1-critical-fixes.md | head -60
```

## What NOT to redo

- Chapter renames, methodology fold, Shadow Mode demotion — all committed.
- `case-study/` → `data/cambodia/` and `stress_testing/rl/` → `healthrl/` renames — committed.
- `healthrl/config.py` centralization — committed; use `EXPERIMENT` / `BANDIT` imports for any new experiment code.
- The 20-seed standardization in chs V & VI — committed; new writeups should use the same convention.
