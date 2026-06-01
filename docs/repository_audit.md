# Repository Audit — Demo ↔ Thesis Alignment

**Date:** 2026-06-01
**Scope:** the live demo (`demo/`) and its evidence assets, audited against `docs/thesis_analysis.md`. This **extends** the prior editorial/research audit in `docs/superpowers/audit/2026-05-25/` (which covered chapter consistency, citations, and code quality) — it does **not** repeat it. Focus here: *does the demo accurately demonstrate and validate the thesis?*

**Severity legend:** 🔴 Critical (would visibly contradict the thesis in front of an examiner) · 🟠 Major (gap between thesis and demo) · 🟡 Minor (polish / framing) · 🟢 Working (keep).

---

## A. The two surfaces

| Surface | Files | Role | Verdict |
|---|---|---|---|
| **Defense deck** | `static/defense.html` + `defense.js` (`/defense` route) | 10-scene narrative for the defense | **Primary defense deliverable.** Strong skeleton, but carries fabricated/mismatched numbers (§B). |
| **Sandbox tool** | `templates/index.html` + `app.js` (`/` route) | 4-tab interactive actuarial tool | **Secondary / "explore live" companion.** Works; framing & a missing FR-1 view (§C). |

**Decision:** the `/defense` deck is the centrepiece to align and harden; `/` remains the interactive sandbox a reviewer can open for hands-on exploration. Both already share the FastAPI backend (`main.py`) and the thesis colour system.

Backend (`main.py`): 🟢 Endpoints are correct and reuse the real `healthrl` package (`expected_rewards`, `run_bandit`, real `LinUCB`/`LinTS`/`StaticXGB`, real `compute_psi` via `hitl_db`). No fabrication server-side. Note `HITL_BANDIT` is a process-global that mutates across requests (acceptable for demo; see §D).

---

## B. Defense deck — thesis-alignment defects

### B0 🔴🔴 `defense.js` did not parse at all — the deck was completely non-functional
- Two bracket errors shipped on `main`: a **missing `}`** in `renderBenchmark` (Scene 5, line ~228) and an **extra `}`** in `renderCoefficients` (Scene 6, line ~253). A single syntax error aborts parsing of the *entire* script, so `init()` never ran — no nav dots, no charts, no scene logic anywhere in `/defense`.
- **How found:** `node --check` / V8 `new Function` rejected the file at the benchmark line; a string-aware bracket linter localised both (16 `{`/15 `}` at 228; 11 `{`/12 `}` at 253).
- **Status:** **FIXED** (commit "repair two pre-existing syntax errors"). File now parses cleanly under V8; server-verified that `/defense` serves and the scene endpoints respond.
- This is the single most important fix: no amount of number-alignment matters if the JavaScript never executes.

### B1 🔴 Scene 7 (Fairness & PSI) — fabricated data + wrong fairness rule
- `FAIRNESS_DATA` in `defense.js:255-268` is **hardcoded and invented**. Several rates fall **below 80%** (Prey Veng 56.2%, Monk/Retired 51.1%) and the chart enforces a **50% parity floor** (`defense.js:275-279`), not the thesis's **EEOC four-fifths (80%) rule**.
- The HTML PSI scorecard (`defense.html:368-377`) shows "Region 0.0050 / Occupation 0.0100 GREEN".
- **Conflict:** the thesis (§5.2, §6.1) reports parity **85.72% region / 90.12% occupation** (both ≥80%), max sliding PSI **0.082 region (GREEN) / 0.123 occupation (AMBER)**, and *passes* the EEOC 80% rule. The deck would show the demo **failing** a rule the thesis says it **passes**, with different PSI values. This is the highest-risk defect.
- **Why it conflicts:** directly contradicts EXP-006 pass criteria and RQ2.
- **Effort:** ~1.5h. **Solution:** generate `static/exp006_results.json` from the real EXP-006 numbers (20-seed), drive Scene 7 from it, switch the parity line to **80%**, and show the AMBER occupation PSI honestly with the §5.2.3 interpretation (statistically significant but within threshold).

### B2 🔴 Scene 4 (Arena) — single-seed lift presented as the result; entropy hardcoded wrong
- `initArena()` computes lift live from seed-42 JSON → ≈**+27.7%** (`defense.js:181-184`), with no reference to the canonical **+25.2%** 20-seed claim.
- Entropy is hardcoded "Early 1.386 → Late 1.053" (`defense.html:248-253`); the seed-42 JSON itself says 1.320→1.053 and the 20-seed thesis value is **1.314→1.105**.
- **Conflict:** an examiner comparing the screen to §5.1 sees a different headline number and wrong entropy.
- **Effort:** ~1.5h. **Solution:** add a **canonical 20-seed headline card** (+25.2%, p<0.001, d=2.98, 90,540 vs 72,292, sourced from a results JSON), and explicitly label the live curve "illustrative single seed (42)". Fix entropy to 1.314→1.105.

### B3 🟠 Scene 8 (HITL) — non-headline conservatism cell
- Diagnostics hardcoded to c=0.3 values: $101,646 / $95,872 / **+6.0%** / $2,555 / 1.46% (`defense.html:446-452`, `defense.js:307-310`).
- **Conflict:** thesis headline is **c=0.7: 102,100 / +6.5% / 2,625 / 1.5%** (§5.4.2, §6.1 Finding 4).
- **Effort:** ~0.5h. **Solution:** use the c=0.7 headline numbers (or show all three cells with c=0.7 marked as headline); fix the waterfall constants.

### B4 🟠 Scene 9 (Drift) — fabricated curves while a real experiment exists
- `renderDrift()`/`injectDrift()` synthesize trajectories from invented formulas and flip a "RED · 0.31" badge on click (`defense.js:315-346`).
- **Conflict:** EXP-009 is real (post/pre 0.29× vs 0.85×; figure `fig_009_drift_adaptation.png`). Fabrication where real evidence exists is an integrity risk.
- **Effort:** ~1h. **Solution:** present the real EXP-009 figure + the 0.29×/0.85× numbers, framed honestly (incl. the §5.9.3 convergence-confound caveat); keep DiscountedLinUCB as labelled *future-work* projection, clearly marked.

### B5 🟡 Scene 2 — illustrative rule mislabelled as the baseline
- "IF BMI>30 AND AGE>50 THEN DECLINE" is the thesis's *own pedagogical* example (§2.2) — **not invented** — but it is captioned "Static XGBoost Baseline", whereas the real baseline is the R1–R4 mortality-multiplier engine.
- **Effort:** ~0.3h. **Solution:** relabel as "Illustrative static rule" and add a one-line note that the experimental baseline is an XGBoost mortality predictor + threshold engine.

### B6 🟡 Scene 5 / Scene 10 — verify hardcoded stats against thesis
- Log-log slope 0.572 / R² 0.992 / asymptotic 0.511 ✅ match §5.6. Closing "4 passed / exit 0" and the four contributions ✅ match §6. Keep; just confirm EXP list wording.

### B7 🟡 Scene 3 / Scene 1 — illustrative, acceptable
- Scene 3 explore/exploit is a client-side toy (fine, clearly pedagogical). Scene 1 penetration figures are thesis-anchored (§2.1: <2% insurance, ~80% digital wallet) ✅.

---

## C. Sandbox tool (`index.html`/`app.js`) — gaps

### C1 🟠 No FR-1 "Applicant → 4-action expected reward" view front-and-centre
- FR-1.2 (expected reward for all four actions) is the *core* of the bandit decision, but the sandbox opens on the **Premium Optimiser** (FR-2) and only the `/defense` deck calls `/api/simulate`. A reviewer never sees the raw 4-action comparison in the tool.
- **Effort:** ~1.5h. **Solution:** add an "Applicant Simulator" panel (or promote it as the first tab) that calls `/api/simulate` and shows the 4 action rewards + the argmax, with the random-applicant loader.

### C2 🟠 No interpretability/coefficient view in the sandbox
- NFR-7 (inspectable θ_a) is only in the deck (Scene 6). The tool has the data (`coefficients_linucb_seed42.json`) but no view.
- **Effort:** ~1h. **Solution:** reuse the Scene-6 coefficient chart as a sandbox panel.

### C3 🟡 Headline 20-seed evidence absent from the tool
- The sandbox runs live single-seed only; the canonical claims live nowhere in `/`.
- **Effort:** ~0.5h. **Solution:** a small "Canonical results (20 seeds)" evidence card linking to the deck.

### C4 🟢 Working & keep: Premium Optimiser + profit curve, batch portfolio, live PSI monitor, Bandit Arena, Benchmark Race, HITL review with sqlite persistence + CSV export, realistic/simple cost modes, adverse-factor slider. These satisfy FR-2, FR-3, FR-4 and are correct.

---

## D. Cross-cutting / technical debt

| ID | Item | Sev | Note |
|----|------|-----|------|
| D1 | No `exp006_results.json` / `exp008_results.json` / 20-seed `exp005/007` artifacts in `static/` | 🟠 | Only seed-42 single-seed JSONs exist. Need canonical artifacts to drive B1/B2/B3 honestly. |
| D2 | Numbers hardcoded in HTML/JS rather than sourced from JSON | 🟠 | Root cause of B1–B3 drift; centralise into JSON the way Scenes 4/5/6 already do. |
| D3 | `HITL_BANDIT` global mutates across sessions; `hitl.db` persists across runs | 🟡 | Fine for demo; note for reproducibility — offer a reset. Don't change behaviour pre-defense. |
| D4 | `requirements.txt` modified (uncommitted) | 🟡 | Confirm pins still satisfy §4.3 before deploy. |
| D5 | Deprecated `backend/` (Shadow Mode) referenced by older chapters | 🟢 | Already flagged in prior audit; out of scope for demo revamp. |

---

## E. Summary — what to fix, in priority order

0. **B0 (dead JS)** 🔴🔴 — **DONE.** Deck JS now parses and runs.
1. **B1 (fairness)** 🔴 — correct rule + real numbers. *Highest defense risk.*
2. **B2 (arena headline)** 🔴 — canonical 20-seed vs illustrative single-seed; fix entropy.
3. **B3 (HITL)** 🟠 — headline c=0.7 numbers.
4. **B4 (drift)** 🟠 — real EXP-009 evidence.
5. **C1/C2 (sandbox FR-1 + interpretability)** 🟠 — close the functional-requirement gaps reviewers can probe.
6. **B5, C3, D-items** 🟡 — framing & polish.

The recurring root cause is **D2: evidence hardcoded instead of sourced from authoritative artifacts**. The redesign (next doc) fixes that structurally by generating canonical 20-seed JSONs and driving every headline number from them.
