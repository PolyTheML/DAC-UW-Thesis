# 3-Month Internship Plan — Adaptive Health Insurance Underwriting

> **Internship duration:** March 2026 – June 2026 (3 months active work + defense)  
> **Student:** LUN CHANPOLY  
> **Advisor:** HAS SOTHEA  
> **Defense target:** 26 June 2026  
> **Research title:** *Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia*

---

## 1. Overview

This plan compresses the full MSc thesis lifecycle into a **12-week active work period** (March–May) with **Week 13+** reserved for defense rehearsal, final formatting, and submission. The schedule is designed around four concurrent work-streams:

| Stream | Description |
|--------|-------------|
| **A. Research & Modeling** | Literature review, dataset construction, baseline models, bandit algorithms |
| **B. Experiments** | EXP-005 through EXP-008 design, execution, and validation |
| **C. Engineering** | Web demos (`/demo`, `/hitl`, `/drift`), offline demo package, tests |
| **D. Writing** | Chapter drafts, defense presentation, ITC-formatted thesis DOCX |

---

## 2. High-Level Timeline (Gantt View)

```
Week:  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 12| 13|
       |---|---|---|---|---|---|---|---|---|---|---|---|---|
A. Research & Modeling
  ├─ Lit. review & scope freeze        [===]
  ├─ Cambodia dataset generation           [===]
  ├─ GLM + XGB baseline training               [===]
  └─ Bandit algo implementation (LinUCB/TS)        [===]

B. Experiments
  ├─ EXP-005: Convergence validation                   [===]
  ├─ EXP-006: Fairness audit                               [===]
  ├─ EXP-007: Benchmark comparison                             [===]
  └─ EXP-008: Human-in-the-loop                                    [===]

C. Engineering
  ├─ PSI guardrail module                                            [===]
  ├─ Web demo /demo (baseline bandit)                                    [===]
  ├─ Web demo /hitl (human-in-the-loop)                                      [===]
  ├─ Web demo /drift (non-stationary drift)                                      [===]
  └─ Offline demo package (`final-demo/`)                                            [===]

D. Writing & Defense
  ├─ Ch1 Introduction & Ch2 Literature Review                                [=======]
  ├─ Ch3 Methodology                                                               [=======]
  ├─ Ch4 Results & Discussion                                                          [=======]
  ├─ Ch5 Conclusion                                                                        [===]
  ├─ Defense presentation (20 slides)                                                          [===]
  └─ Final review, formatting, rehearsal                                                           [====]
```

**Legend:** `[===]` = active work period for that task.

---

## 3. Weekly Breakdown

### Month 1 — Foundation (March)

#### Week 1: Scope Freeze & Literature Review
- [ ] Finalize research question and claim with advisor
- [ ] Complete annotated bibliography (20+ papers: LinUCB, LinTS, PSI, fairness in ML, health insurance underwriting)
- [ ] Draft Chapter 1 (Introduction) — Sections 1.1–1.6
- [ ] Set up repository structure, CI skeleton, pytest harness
- [ ] **Deliverable:** Chapter 1 v1.0 + lit-review bibliography

#### Week 2: Dataset & Baselines
- [ ] Design synthetic Cambodia health insurance schema (demographics, health conditions, region, occupation, economic features)
- [ ] Implement `generate_cambodia_dataset.py` (2,000 records, CDHS 2021-22 anchored)
- [ ] Train GLM and XGBoost baselines (`train_cambodia_models.py`)
- [ ] Generate SHAP values and coefficient JSON for interpretability
- [ ] **Deliverable:** `cambodia_dataset.csv/parquet` + 4 trained models in `case-study/models/`

#### Week 3: Bandit Core Implementation
- [ ] Implement `LinUCB` with matrix inversion update (`alpha = 1.0`)
- [ ] Implement `LinTS` with posterior sampling (`v² = 1.0`)
- [ ] Implement `EpsilonGreedy` linear regression baseline (`epsilon = 0.15`)
- [ ] Build `StaticXGBBaseline` deterministic rule engine
- [ ] Unit-test each algorithm on a toy 2D context
- [ ] **Deliverable:** `underwriting_bandit.py` with 3+ algorithms + tests

#### Week 4: Reward Simulator & PSI Module
- [ ] Build actuarial reward simulator:
  - Base premium formula: `200 × mortality_multiplier` (USD/year)
  - Customer acceptance probability model
  - 4 actions: STANDARD, RATED (+25%), DECLINE, REFER
- [ ] Implement PSI computation with 10 equal-frequency bins
- [ ] Implement fairness constraint checker (50% of max approval rate)
- [ ] **Deliverable:** Reward simulator + PSI module passing sanity checks

---

### Month 2 — Experiments & Demos (April)

#### Week 5: EXP-005 — Convergence Validation
- [ ] Design experiment: 5,000 rounds, 2,000-record dataset (2.5 passes)
- [ ] Hypothesis: LinUCB cumulative reward > Static XGB baseline
- [ ] Run simulation, collect cumulative reward and per-window regret
- [ ] Assert: LinUCB reward > baseline AND avg regret in last 500 rounds < baseline
- [ ] **Deliverable:** `exp_005_underwriting_convergence.py` passing + figure

#### Week 6: EXP-006 — Fairness Audit
- [ ] Design audit: regional and occupational approval-rate parity
- [ ] Compute PSI between applicant pool and approved pool for region & occupation
- [ ] Assert: No group approval rate < 50% of max; PSI < 0.10 (GREEN)
- [ ] **Deliverable:** `exp_006_fairness_audit.py` passing + fairness figures

#### Week 7: EXP-007 & EXP-008 — Benchmark + HITL
- [ ] EXP-007: Compare LinUCB, LinTS, EpsilonGreedy, StaticXGB on cumulative regret over 5,000 rounds
- [ ] Assert: LinUCB lowest regret, followed by LinTS
- [ ] EXP-008: Human-in-the-loop simulation with override cost ($35/override)
- [ ] Assert: HITL reward lift > 0%, alignment rate > 40%, human cost < 15% of reward
- [ ] **Deliverable:** `exp_007_benchmark_comparison.py` + `exp_008_human_in_the_loop.py` passing

#### Week 8: Web Demo Platform
- [ ] Build `/demo` — interactive bandit underwriting with live decision output
- [ ] Build `/hitl` — human review queue, override workflow, alignment dashboard
- [ ] Build `/drift` — DiscountedLinUCB vs Static LinUCB race with outbreak labeling
- [ ] Build `final-demo/` offline package (`output: 'standalone'`)
- [ ] **Deliverable:** All 3 demos running locally + offline package defense-ready

---

### Month 3 — Writing & Defense Prep (May)

#### Week 9: Chapter 2 & Chapter 3
- [ ] Finalize Chapter 2 (Literature Review) — Sections 2.1–2.6 (~2,200 words)
  - Contextual bandits (LinUCB, LinTS, Epsilon-Greedy)
  - PSI and population stability
  - Fairness in automated underwriting
  - Human-in-the-loop RL
- [ ] Draft Chapter 3 (Methodology) — Sections 3.1–3.5 (~2,500–3,000 words)
  - Dataset design and feature engineering
  - Algorithm descriptions with formal notation
  - Reward design rationale
  - PSI guardrails and fairness metrics
  - Experimental design for EXP-005–008
- [ ] **Deliverable:** Ch2 complete + Ch3 full draft

#### Week 10: Chapter 4 — Results
- [ ] Write Section 4.1 (EXP-005 results with table)
- [ ] Write Section 4.2 (EXP-006 results with regional/occupation figures)
- [ ] Write Section 4.3 (EXP-007 regret curves and ranking)
- [ ] Write Section 4.5 (EXP-008 HITL metrics and dual-arm update insight)
- [ ] **Deliverable:** Chapter 4 results sections (~1,800 words)

#### Week 11: Chapter 4 Discussion & Chapter 5
- [ ] Write Section 4.4 Discussion (~600 words)
  - 4.4.1 Implications for practice
  - 4.4.2 Connection to literature
  - 4.4.3 Limitations
  - 4.4.4 Threats to validity
- [ ] Draft Chapter 5 (Conclusion) — Sections 5.1–5.4 (~1,400 words)
  - Summary of findings across all 4 experiments
  - Limitations and future work (neural bandits, A/B testing, multi-period value)
- [ ] Build defense presentation (`build_presentation.py`) — 20 slides
- [ ] Generate all 6 matplotlib figures
- [ ] **Deliverable:** Ch4 complete + Ch5 complete + presentation v1.0

#### Week 12: Integration & Formatting
- [ ] Run `build_thesis_docx.py` → generate `ITC_Thesis_Draft.docx`
- [ ] Verify all tables, figures, and citations are resolved
- [ ] Review cross-references between chapters and experiments
- [ ] Run full test suite: `pytest tests/`
- [ ] Run all experiments: `exp_005` → `exp_008` and confirm 0 exit codes
- [ ] **Deliverable:** Complete thesis draft + defense deck + all tests green

---

### June — Defense & Submission

#### Week 13: Defense Rehearsal
- [ ] Internal rehearsal with advisor (mock Q&A)
- [ ] Timing run: 20-minute presentation + 10-minute Q&A
- [ ] Polish speaker notes (`presentation_script.md`)
- [ ] Prepare backup laptop with `final-demo/` offline package
- [ ] **Deliverable:** Rehearsal feedback addressed, demo smoke-tested

#### Defense Day (~26 June 2026)
- [ ] Submit final printed thesis (ITC format)
- [ ] Submit digital copy + source code archive
- [ ] Defense presentation + Q&A

---

## 4. Milestones & Checkpoints

| Milestone | Target Date | Success Criteria |
|-----------|-------------|------------------|
| M1 — Dataset + Baselines Ready | End of Week 2 | `cambodia_dataset.parquet` exists; GLM/XGB models trained; test predictions CSV generated |
| M2 — Bandit Core Ready | End of Week 4 | All 3 bandit algorithms pass unit tests; reward simulator produces sensible ranges |
| M3 — All Experiments Passing | End of Week 7 | EXP-005 → EXP-008 exit 0; key numbers recorded in `COLLAB.md` |
| M4 — Demos Defense-Ready | End of Week 8 | `/demo`, `/hitl`, `/drift` build and run; `final-demo/` smoke-tested offline |
| M5 — Thesis Draft Complete | End of Week 12 | Ch1–Ch5 written; DOCX generated; all figures embedded |
| M6 — Defense Success | ~26 June 2026 | Presentation delivered; committee Q&A completed; thesis submitted |

---

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Synthetic dataset lacks realism | Medium | High | Anchor on CDHS 2021-22; validate marginal distributions with advisor |
| Bandit convergence is unstable | Low | High | Use fixed seeds (42); test on smaller `n_rounds` first; debug reward function sign |
| Web demo build failures | Medium | Medium | Lock dependency versions; maintain `final-demo/` as fallback; test on clean machine |
| Chapter 3 (Methodology) expands beyond scope | Medium | Medium | Hard limit: 3,000 words; use algorithm pseudocode blocks instead of full proofs |
| Defense laptop has no Node.js | Low | Medium | `final-demo/` includes `node.exe` + `server.js`; also keep Python scripts as fallback |
| Advisor review delays | Medium | High | Share Chapter drafts weekly; use `COLLAB.md` for async feedback with co-advisor |

---

## 6. Weekly Time Budget

For a full-time 3-month internship, assume **35–40 hours/week**:

| Activity | Hours/Week |
|----------|-----------|
| Research & reading | 5–6 |
| Coding (experiments + demos) | 12–15 |
| Writing (chapters + presentation) | 10–12 |
| Meeting with advisor / feedback | 2–3 |
| Testing, debugging, formatting | 4–5 |
| **Total** | **33–41** |

---

## 7. File Map

| File | Purpose | Owner Stream |
|------|---------|--------------|
| `case-study/generate_cambodia_dataset.py` | Synthetic dataset generator | A |
| `case-study/train_cambodia_models.py` | GLM + XGB training | A |
| `stress_testing/rl/underwriting_bandit.py` | Core bandit algorithms | A |
| `stress_testing/rl/experiments/exp_005*.py` | Convergence validation | B |
| `stress_testing/rl/experiments/exp_006*.py` | Fairness audit | B |
| `stress_testing/rl/experiments/exp_007*.py` | Benchmark comparison | B |
| `stress_testing/rl/experiments/exp_008*.py` | Human-in-the-loop | B |
| `web/app/demo/page.tsx` | Interactive bandit demo | C |
| `web/app/hitl/page.tsx` | HITL review dashboard | C |
| `web/app/drift/page.tsx` | Drift detection race | C |
| `final-demo/` | Offline defense package | C |
| `thesis/health_rl/chapter1_introduction.md` | Ch1 draft | D |
| `thesis/health_rl/chapter2_literature_review.md` | Ch2 draft | D |
| `thesis/health_rl/chapter3_methodology.md` | Ch3 draft | D |
| `thesis/health_rl/chapter4_results.md` | Ch4 draft | D |
| `thesis/health_rl/chapter5_conclusion.md` | Ch5 draft | D |
| `thesis/health_rl/build_presentation.py` | 20-slide PPTX generator | D |
| `thesis/health_rl/build_thesis_docx.py` | ITC Word doc generator | D |

---

## 8. Current Status (as of 2026-05-05)

| Week | Planned Task | Actual Status |
|------|--------------|---------------|
| 1–2 | Lit. review + Dataset + Baselines | ✅ Complete — Ch1 drafted; dataset & models generated |
| 3–4 | Bandit core + Reward/PSI modules | ✅ Complete — `underwriting_bandit.py` fully implemented |
| 5–6 | EXP-005 + EXP-006 | ✅ Complete — both passing with figures |
| 7 | EXP-007 + EXP-008 | ✅ Complete — all 4 experiments passing |
| 8 | Web demos + Offline package | ✅ Complete — `final-demo/` defense-ready |
| 9 | Ch2 + Ch3 | 🔄 Partial — Ch2 complete; **Ch3 still skeleton** |
| 10 | Ch4 Results | 🔄 Partial — Sections 4.1–4.3 & 4.5 done; **Section 4.4 Discussion is skeleton** |
| 11 | Ch5 + Presentation | ✅ Complete — Ch5 written; presentation generated |
| 12 | Integration | 🔄 Pending — DOCX stale; chapters restored from git today |
| 13 | Defense rehearsal | ⏳ Scheduled for mid-June |

### Immediate Actions (Week 12 Remaining)
1. **Write Chapter 3** from skeleton → full draft (~2,500 words)
2. **Write Section 4.4** Discussion (~600 words)
3. **Regenerate** `ITC_Thesis_Draft.docx` via `build_thesis_docx.py`
4. **Run full validation**: all experiments + pytest + presentation build
