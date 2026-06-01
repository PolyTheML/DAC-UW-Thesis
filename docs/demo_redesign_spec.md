# Demo Redesign Specification — Defense-Quality Demonstration

**Date:** 2026-06-01
**Goal:** a demonstration that makes the thesis contributions *obvious and unimpeachable* to an examiner — every headline number on screen matches the thesis, and the system's novelty (PSI-as-external-guardrail + HITL dual-update) is visually unmistakable.

**Governing principle (the one that prevents self-sabotage):**

> **Separate "authoritative" from "illustrative."** Headline statistical claims (20-seed means, CIs, p-values, Cohen's d) are surfaced from **pre-computed canonical artifacts** and labelled as such. Live, interactive controls run **a single seed** and are explicitly framed as *illustrative intuition*, never as the result. NFR-6: any PSI shown live must match EXP-006 to 4 d.p.

**Constraints (non-negotiable):** keep the working demo working (defense is in days); keep the thesis-mandated stack (FastAPI + vanilla JS + Chart.js + Jinja2 — §4.3); make additive, reversible changes; the `/defense` deck is the primary deliverable, `/` the sandbox companion.

---

## 1. Canonical evidence layer (the foundation)

Create **`demo/static/thesis_results.json`** — a single provenance-tagged file holding the *thesis's own published 20-seed numbers* (transcribed verbatim from the ch5 tables, each with a `source` field, e.g. `"§5.1.1 Table 5.1.1"`). This is the authoritative source every headline card reads from. It contains:

```
{
  "exp005": { linucb_reward, static_reward, lift_pct: 25.2, p, cohen_d, regret_late_linucb, regret_late_static, entropy_early: 1.314, entropy_late: 1.105, action_accuracy, source },
  "exp006": { region: {parity_pct: 85.72, psi_max: 0.082, psi_zone: "GREEN", perm_p, rates_by_group}, occupation: {parity_pct: 90.12, psi_max: 0.123, psi_zone: "AMBER", perm_p, rates_by_group}, eeoc_threshold: 80, source },
  "exp007": { ranking: [LinTS, LinUCB, EpsGreedy, StaticXGB] with reward/regret/CI, oracle, source },
  "exp008": { headline_c: 0.7, hitl_reward: 102100, baseline: 95872, lift_pct: 6.5, human_cost: 2625, referral_pct: 1.5, alignment: 60, cells: {0.3,0.5,0.7}, source },
  "exp009": { post_pre_ratio: {linucb:0.29, lints:0.29, static:0.85}, caveat, source },
  "exp013": { slope: 0.572, r2: 0.992, asymptotic_slope: 0.511, source }
}
```

> **Provenance, not fabrication:** these are the thesis's *validated* results; transcribing them into JSON (with section citations) is legitimate. Optionally regenerate them by running `exp_005/006/007/008.py` (20 seeds, ~5–10 min each) and serialising — but for an imminent defense the transcribe-with-citation path is the safe default. `repository_audit.md §D1` tracks this.

The single-seed trajectory JSONs (`exp005/007/coef_seed42`) remain for the *illustrative* live curves.

---

## 2. User Journey (defense deck `/defense`)

A 10-scene linear narrative (already scaffolded), revised so each scene answers a reviewer question:

1. **The 1% Problem** — why this matters (penetration vs mobile). *Anchored in §2.1.*
2. **Why Static Rules Fail** — illustrative static rule vs adaptive 4-action reward (live `/api/simulate`). *Relabelled per audit B5.*
3. **Explore vs Exploit** — the core RL idea (client-side toy, clearly pedagogical).
4. **Bandit Arena (EXP-005, RQ1)** — **canonical headline card (+25.2%, p<0.001, d=2.98)** beside an *illustrative* single-seed convergence curve + correct entropy + action-distribution evolution.
5. **Benchmark Race (EXP-007, RQ3)** — ranking + regret curves + **EXP-013 Õ(d√T) validation**.
6. **Coefficient Audit (NFR-7)** — per-action θ_a bars; "the bandit prices risk, not geography."
7. **Fairness & PSI (EXP-006, RQ2)** — **corrected**: EEOC 80% line, real parity 85.7%/90.1%, PSI 0.082 GREEN / 0.123 AMBER with honest interpretation.
8. **Human-in-the-Loop (EXP-008, RQ4)** — live review queue + **headline c=0.7 waterfall** + dual-update explanation (the novel bit).
9. **Drift Adaptation (future work)** — **real EXP-009 figure/numbers**; DiscountedLinUCB clearly marked as proposed.
10. **Four Contributions + Pass Stamps** — close.

## 3. Screens

- `/defense` — the 10-scene deck (primary).
- `/` — the sandbox tool, tabs in this order: **Applicant Simulator (new, FR-1)** · Pricing Engine (FR-2) · Bandit Arena (FR-3) · Benchmark Race (FR-3) · Fairness & PSI (FR-4) · Underwriter Review (HITL) · **Interpretability (new)**. A persistent "Canonical 20-seed results" evidence strip links the two surfaces.

## 4. Components

| Component | Reused / New | Source |
|---|---|---|
| `CanonicalCard` (headline stat + CI + p + d + "20 seeds" badge + source tooltip) | **New** | `thesis_results.json` |
| `IllustrativeBadge` ("single seed 42 — illustrative") | **New** | static label |
| 4-action reward bars (argmax starred) | Exists (Scene 2) → promote to sandbox FR-1 | `/api/simulate` |
| Convergence/regret line charts | Exists | seed-42 JSON |
| Coefficient θ_a bar chart | Exists (Scene 6) → also sandbox | `coefficients_linucb_seed42.json` |
| Fairness bar + EEOC 80% line + PSI scorecard | **Rewrite** (B1) | `thesis_results.json` |
| HITL queue + reward waterfall | Exists → fix constants (B3) | `/api/hitl/*` + `thesis_results.json` |
| Drift figure panel | **Rewrite** (B4) | `fig_009_drift_adaptation.png` + `thesis_results.json` |
| PSI traffic-light cards (GREEN/AMBER/RED) | Exists | live `/api/hitl/metrics` + canonical |

## 5. Visualizations (recommended)

- **Architecture diagram** — reuse `fig_ch2_system_architecture.png` / `fig_framework.png` on Scene 2 or an "About" panel.
- **Bandit decision-loop diagram** — `fig_ch4_bandit_loop.png` on Scene 3.
- **Convergence + regret curves** — live single-seed, with canonical headline overlay text.
- **Action-distribution evolution** (stacked) — exists; keep.
- **Benchmark regret race** + **log-log regret** (`fig_loglog_regret.png`) — exists; keep.
- **Coefficient bars** (top-12 |θ| per action) — exists; keep.
- **Fairness parity bars + EEOC 80% line**; **PSI traffic-light scorecard** — rewrite.
- **HITL reward waterfall** (baseline → +lift → −cost → net) — fix to c=0.7.
- **Drift recovery curve** — real `fig_009_drift_adaptation.png`.

## 6. Demo Scenarios (defense narratives)

1. **"The profitable applicant static rules reject"** — Scene 2: a fit 55-y/o, BMI 31 civil servant; static rule → DECLINE (−$10), bandit → STANDARD (positive). Shows suboptimal selection (Problem 1).
2. **"Watch it learn, then see the proof"** — Scene 4: play the single-seed convergence (illustrative), then reveal the canonical +25.2% / d=2.98 card. Separates intuition from evidence.
3. **"Fair without being told to be"** — Scene 7: no fairness term in the reward, yet 85.7%/90.1% parity and GREEN/AMBER PSI — the decoupled-guardrail contribution.
4. **"The human and the machine"** — Scene 8: referee a few REFER cases; show +6.5% at 1.5% referral and explain the dual-update that keeps REFER alive.
5. **"What happens when the world changes"** — Scene 9: real shock-recovery (0.29× vs 0.85×) + the PSI-triggered DiscountedLinUCB plan.

## 7. Acceptance criteria (demo-level)

- Every numeric claim on `/defense` matches `docs/thesis_analysis.md` / the ch5 tables (spot-checkable against the source tooltip).
- Scene 7 uses the **80%** rule and shows parity ≥80% for all groups + correct PSI zones.
- Scene 4 shows both the **canonical +25.2%** and an explicitly-labelled illustrative single-seed curve.
- No scene fabricates data where a real artifact exists (drift uses the real figure).
- `/` gains an Applicant Simulator (FR-1) and an Interpretability panel; all existing tools still work.
- Demo runs on the existing stack with `uvicorn demo.main:app`; deploys unchanged on Render.
