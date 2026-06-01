# Implementation Plan — Demo Revamp

**Date:** 2026-06-01
**Context:** defense is **imminent (days)**. Therefore: accuracy-first, additive, reversible. Every task preserves the working demo and keeps the thesis-mandated stack. Complexity: **S** ≈ ≤1h, **M** ≈ 1–2h, **L** ≈ 2–4h.

Phases run in priority order; **Phase A is defense-critical and should ship first**. B–D are improvements that strengthen the demo but do not gate the defense.

> **Status (2026-06-01): Phases A, B, C, D all implemented and committed on branch `demo-thesis-alignment`.** A surprise prerequisite surfaced during A — `defense.js` had two pre-existing bracket errors that broke the entire deck's JavaScript (see audit B0); fixed first. All changes are presentation-layer only; `healthrl/`, the dataset, and experiment scripts are untouched. Server-verified: `/`, `/defense`, the new tabs, the figures, and `POST /api/hitl/reset` all respond 200.

---

## Phase A — Critical thesis alignment (defense-blocking)

### A0 — Canonical evidence artifact
- **Files:** `demo/static/thesis_results.json` (new); optional `scripts/build_thesis_results.py`.
- **Depends on:** `docs/thesis_analysis.md` (numbers), ch5 tables.
- **Complexity:** M.
- **Acceptance:** JSON contains exp005/006/007/008/009/013 headline numbers, each with a `source` section citation; values match the thesis tables exactly. Served statically.

### A1 — Fix Scene 7 (Fairness & PSI)  🔴
- **Files:** `demo/static/defense.js` (`FAIRNESS_DATA`, `renderFairness`, `setFairnessTab`), `demo/static/defense.html` (Scene 7 scorecard + parity copy).
- **Depends on:** A0.
- **Complexity:** M.
- **Acceptance:** parity line = **80%**; all displayed group rates ≥80% of max; region parity **85.72%**, occupation **90.12%**; PSI scorecard shows **0.082 GREEN / 0.123 AMBER** with the §5.2.3 interpretation note; values read from `thesis_results.json`.

### A2 — Fix Scene 4 (Arena headline vs illustrative)  🔴
- **Files:** `demo/static/defense.html` (entropy block, add canonical card), `demo/static/defense.js` (`initArena`).
- **Depends on:** A0.
- **Complexity:** M.
- **Acceptance:** a **canonical card** shows +25.2%, 90,540 vs 72,292, p<0.001, d=2.98 with a "20 seeds" badge; the live seed-42 curve is labelled "illustrative (seed 42)"; entropy corrected to **1.314 → 1.105**.

### A3 — Fix Scene 8 (HITL headline)  🟠
- **Files:** `demo/static/defense.html` (diagnostics grid), `demo/static/defense.js` (`renderHitlWaterfall`).
- **Depends on:** A0.
- **Complexity:** S.
- **Acceptance:** diagnostics + waterfall use **c=0.7: 102,100 / 95,872 / +6.5% / 2,625 / 1.5%**; dual-update one-liner present.

### A4 — Fix Scene 9 (Drift uses real evidence)  🟠
- **Files:** `demo/static/defense.html` (Scene 9), `demo/static/defense.js` (`renderDrift`/`injectDrift`); copy `thesis/health_rl/figures/fig_009_drift_adaptation.png` → `demo/static/`.
- **Depends on:** A0.
- **Complexity:** M.
- **Acceptance:** Scene shows the real EXP-009 figure + 0.29×/0.85× numbers + §5.9.3 caveat; DiscountedLinUCB curve explicitly labelled "proposed (future work)".

### A5 — Relabel Scene 2 baseline  🟡
- **Files:** `demo/static/defense.html` (Scene 2 headings/notes).
- **Complexity:** S.
- **Acceptance:** the threshold card reads "Illustrative static rule (§2.2)" with a note that the experimental baseline is XGBoost mortality predictor + R1–R4 threshold engine.

### A6 — Verify all remaining hardcoded stats (Scenes 5, 10)  🟡
- **Files:** `demo/static/defense.html`.
- **Complexity:** S.
- **Acceptance:** log-log (0.572/0.992/0.511), pass stamps, and the four contributions confirmed against §5.6/§6; any drift corrected.

**Phase A exit:** every number on `/defense` traces to the thesis. This alone makes the demo defense-safe.

---

## Phase B — UX improvements (sandbox functional gaps)

### B1 — Applicant Simulator tab (FR-1)  🟠
- **Files:** `demo/templates/index.html` (new first tab/panel), `demo/static/app.js`.
- **Depends on:** existing `/api/simulate`, `/api/applicant/random`.
- **Complexity:** M.
- **Acceptance:** entering/loading an applicant shows expected reward for all four actions + the argmax; no backend change.

### B2 — Interpretability panel (NFR-7)  🟠
- **Files:** `demo/templates/index.html`, `demo/static/app.js`; reuse Scene-6 chart logic.
- **Depends on:** `coefficients_linucb_seed42.json`.
- **Complexity:** M.
- **Acceptance:** per-action θ_a top-|coefficient| bars render in the sandbox.

### B3 — Canonical results strip in `/`  🟡
- **Files:** `demo/templates/index.html`, `demo/static/app.js`.
- **Depends on:** A0.
- **Complexity:** S.
- **Acceptance:** a compact card surfaces the 20-seed headline + a link to `/defense`.

---

## Phase C — Visualization layer

### C1 — Embed architecture + decision-loop diagrams  🟡
- **Files:** `demo/static/defense.html` (Scene 2/3 or About), copy `fig_ch2_system_architecture.png` / `fig_ch4_bandit_loop.png` to `static/`.
- **Complexity:** S.
- **Acceptance:** diagrams visible where they aid the narrative.

### C2 — Source tooltips on canonical cards  🟡
- **Files:** `demo/static/defense.js`, small CSS.
- **Depends on:** A0 `source` fields.
- **Complexity:** S.
- **Acceptance:** hovering a headline stat shows its thesis section.

---

## Phase D — Research-grade polish

### D1 — "Depth on demand" panels for EXP-010/011/012  🟡
- **Files:** new optional scene or collapsible section; uses thesis figures/tables.
- **Complexity:** L.
- **Acceptance:** cold-start crossover, ablation, sensitivity available but not cluttering the main flow.

### D2 — HITL reset control + reproducibility note  🟡
- **Files:** `demo/main.py` (`/api/hitl/reset`), `demo/hitl_db.py`, frontend button.
- **Complexity:** M.
- **Acceptance:** demo can be reset to a clean state between rehearsals; documented.

### D3 — README/demo walkthrough for the examiner  🟡
- **Files:** `demo/README.md` or repo README section.
- **Complexity:** S.
- **Acceptance:** one-page "how to run + scene-by-scene map to chapters".

---

## Sequencing recommendation (given days, not weeks)

1. **A0 → A1 → A2 → A3 → A4 → A5/A6** (one focused pass; commit per scene). *Defense-safe after this.*
2. **B1 → B2 → B3** if time permits before the defense.
3. **C/D** post-defense or as buffer allows.

## Verification per task
- Run `uvicorn demo.main:app` and open `/defense` and `/`; visually confirm each acceptance criterion.
- Cross-check every changed number against `docs/thesis_analysis.md` and the cited ch5 table.
- Commit small, one scene/panel per commit, with the thesis section in the message.
- Do not alter `healthrl/` algorithms, the dataset, or experiment scripts — the demo revamp is presentation-layer only.
