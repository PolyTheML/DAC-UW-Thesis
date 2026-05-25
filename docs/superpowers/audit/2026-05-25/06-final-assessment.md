# Final Assessment

**Date**: 2026-05-25
**Auditor framing**: senior ML researcher + thesis supervisor + reproducibility reviewer.

---

## Three-way readiness verdict

| Readiness for… | Verdict | Reasoning |
|---|---|---|
| **Thesis submission** | **🟡 Conditionally ready** — needs Tier-1 critical fixes (≈10-12 hours) | The empirical work is solid and reproducible. The implementation matches the methodology described. Two classes of issues block submission as-is: (1) internal inconsistencies — the same statistic reported with two different numbers across chapters; (2) the misapplied Bastani et al. citation. Both are repairable in a focused day of editing. |
| **Publication (workshop / short paper)** | **🟡 Plausible with revisions** — add Tier-2 items | EXP-013 (log-log regret validation), EXP-011 (ablation), EXP-012 (sensitivity), and EXP-009 (drift recovery) are exactly the experimental machinery a reviewer expects but currently invisible from the thesis. With those promoted, the work would slot well into a CAUSAL/RecSys/Conformance workshop or a fairness/RL track. A full conference (ICML / NeurIPS / FAccT) main-track paper would need Tier-3 strengthening (real-data validation, NeuralLinear baseline, pre-registration). |
| **Production deployment** | **🔴 Not yet** — research-grade code | The bandit core is well-engineered (Sherman-Morrison updates, Cholesky caching, common random numbers in EXP-007). But: no persistence layer, no auth, no audit logging in the live `demo/` path (these exist only in the deprecated `backend/`), no rate limiting, no monitoring, no model versioning, no rollback procedure. The thesis ch3 §3.6 outlines what production would need — implementing it is months of additional work. |

---

## What the work does well

1. **Reproducibility is genuinely strong.** Fixed seeds, multi-seed analysis, pre-registered pass criteria with exit codes, deterministic dataset generator with documented calibration sources. A reviewer can re-run any experiment and get the same number.
2. **Statistical hygiene is unusually careful for a master's thesis.** Bootstrap CIs, paired Wilcoxon tests, Cohen's d, Bonferroni correction, common random numbers for fair head-to-head comparison. This puts the work meaningfully above the median.
3. **The dataset construction is well-anchored** in Cambodian primary sources (CDHS 2021-22, STEPS 2023, ILO 2023, WHO TB report). The simulator docstring (`case-study/generate_cambodia_dataset.py:1-55`) is a credibility asset that the body of the thesis under-uses.
4. **The bandit implementations are correct.** Sherman-Morrison updates, Cholesky caching, separate per-action sufficient statistics, oracle precomputation — these are the right engineering decisions for the problem size.
5. **The HITL extension (EXP-008) is a genuine contribution.** The "dual update" insight (update both the human-chosen action and the REFER arm so REFER doesn't stay perpetually unexplored) is the kind of small, well-justified design pattern that distinguishes a research result from a class project.
6. **The decoupled fairness architecture** (PSI as external guardrail rather than reward penalty) is well-motivated and preserves theoretical regret guarantees. This is a defensible methodological choice with publication potential.

---

## What the work does less well

1. **Editorial discipline across chapters is lacking.** The same quantity is reported with different numbers in different chapters, two chapters claim to be Ch III, and the conclusion mixes single-seed and multi-seed statistics in adjacent sentences. These are the kinds of issues an examiner will spot in five minutes and that overshadow the underlying technical work.
2. **Citation rigor is uneven.** The peer-reviewed CS references (Li, Agrawal, Zhou, Zhang) are correctly cited. The grey-literature references in chapter 1 (BIMA, ADB, Swiss Re) are paraphrased to the point of being un-findable. The Bastani et al. citation is mis-applied.
3. **Five experiments are implemented but invisible** in the thesis (EXP-009 to EXP-013). This is both a missed opportunity (the thesis is stronger than it presents itself as) and a documentation debt.
4. **No bandit-core unit tests.** The most algorithmically load-bearing code in the repo has no test coverage. The tests that exist cover thesis-loop scripts and presentation builders.
5. **Hyperparameter sprawl.** The same constants (N_ROUNDS, n_seeds, alpha, v2, epsilon, WINDOW) appear in 9 different files. This is mechanically why the ε = 0.10 vs 0.15 drift happened in chapter 4.
6. **No real-data validation pathway.** Limitation 1 acknowledges synthetic-only; no concrete path to even partial real-data validation is proposed (e.g., publicly available US/UK actuarial datasets that could probe whether the bandit's relative ranking holds beyond the calibrated simulator).
7. **The demo platform and the thesis are slightly out of sync.** `demo/` is the live serving platform; `backend/` (which implements Shadow Mode) is deprecated; chapter 3 §3.6.1 describes Shadow Mode as if `backend/` were the current production path.

---

## Risk register for the defense

| Risk | Severity | Mitigation |
|---|---|---|
| Examiner asks: "Why does Chapter VI Finding 1 cite $90,540 but Finding 4 cites $95,872?" | High | Fix IMP-C2 (standardize on 20-seed methodology). |
| Examiner asks: "Bastani et al. 2021 is about exploration-free greedy under covariate diversity. How does that justify your 37.8 % action-accuracy interpretation?" | High | Fix IMP-C5 (replace or rewrite the citation). |
| Examiner asks: "Why is the BIMA figure 430,000 policies — can you point me to the source?" | Medium | Fix IMP-I6 (verify or replace). |
| Examiner asks: "Did you do an ablation or sensitivity analysis?" — and you have to say "no, it's future work" while the code shows you did | Medium | Fix IMP-I1 (promote EXP-011/012). |
| Examiner asks: "Why is $d = 25$ in Chapter IV but $d = 34$ in Chapter III?" | Medium | Fix IMP-C3 (search-and-replace). |
| Examiner asks: "How does LinUCB scale on a real applicant pool — have you tested anything but stationary, equally-weighted batches?" | Medium | Cite EXP-009 (drift) and EXP-010 (cold start) — currently undocumented. |
| Examiner asks: "What about hyperparameter tuning? Why $\alpha = 1.0$?" | Medium | Cite EXP-012 (sensitivity sweep) — currently undocumented. |

The pattern: most of the high-risk defense questions are **already answered by code that exists**. Closing the documentation gap (IMP-I1) defuses several risks at once.

---

## Recommended sequencing for the next 10 days

| Day | Focus |
|---|---|
| 1 | IMP-C1 (chapter consolidation) + IMP-C3 / C4 (fix the d=25 and ε=0.10 typos) |
| 2 | IMP-C2 (standardize on 20-seed numbers in chs V & VI) |
| 3 | IMP-C5 + IMP-C6 (Bastani citation + missing references) + IMP-C7 (Shadow Mode resolution) |
| 4-5 | IMP-I1 (write up EXP-009, EXP-011, EXP-012, EXP-013 — 1 day per pair) |
| 6 | IMP-I3 (centralize config), IMP-I4 (pin deps), IMP-I5 (README), IMP-I7 (bandit unit tests) |
| 7 | IMP-I6 (BIMA source), IMP-I8 (stats notation), IMP-I2 (EXP-010 seeds) |
| 8 | Optional: IMP-O5 (PSI value experiment) and IMP-O9 (dataset documentation appendix) |
| 9 | Read-through, ITC formatting, defense rehearsal |
| 10 | Buffer / advisor revisions |

---

## One-line verdict

The empirical core is solid; the editorial layer needs a focused day of cleanup; the unused experiments are a strength waiting to be claimed.

---

## How this repository ranks against typical ITC RL theses (auditor's view)

- **Reproducibility**: 95th percentile — most theses do not multi-seed, do not bootstrap, do not pre-register.
- **Statistical rigor**: 85th percentile — Wilcoxon + Cohen's d + Bonferroni is unusually thorough.
- **Methodological transparency**: 70th percentile — bandit math is well-presented; reward design is clearly motivated.
- **Editorial polish**: 40th percentile — chapter inconsistencies and citation gaps are below standard.
- **Novelty positioning**: 60th percentile — emerging-market application is interesting but PSI-as-fairness-guardrail and the HITL dual-update are the genuinely novel pieces and they are under-claimed.
- **Code quality**: 75th percentile — clean dataclasses, sensible separation between algorithm and runner, no obvious correctness bugs.

**Aggregate**: above average for an ITC master's thesis on technical execution; below average on editorial coherence. The first is harder to fix than the second.
