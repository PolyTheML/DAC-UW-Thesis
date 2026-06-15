# Adaptive Underwriting — Clean Demo Rebuild (Design Spec)

**Date:** 2026-06-15
**Status:** Approved in brainstorm (this session); ready for implementation plan.
**Author context:** thesis defense demo + DAC-usable tool. Supersedes the messy 7-tab sandbox + separate `/defense` deck in `demo/`.

## 1. Motivation & context

The current demo (`demo/main.py` + `demo/templates/index.html` 7-tab sandbox + `demo/static/defense.html` deck) is two competing surfaces with seven tabs of features. The mess is **feature sprawl + a split-brain of two surfaces** (confirmed with the user). This spec defines a clean rebuild from zero: **one** FastAPI app, **one** single-page UI, **two** views behind a top toggle, reusing the real `healthrl` engine — usable by a DAC underwriter day-to-day *and* used directly as the defense demo (no separate deck).

Reference (do not duplicate): existing engine `healthrl/underwriting_bandit.py`, pricing `demo/pricing_engine.py`, canonical numbers `demo/static/thesis_results.json`, fitted coefficients `demo/static/coefficients_linucb_seed42.json`, old demo behaviour `demo/README.md`.

## 2. Goals / Non-goals

**Goals**
- One clean applicant→result flow ("Underwriting Desk") that a DAC underwriter could actually use.
- One online-learning showcase ("Watch it Learn") that makes the thesis's core claim tangible.
- Offline/local-robust, defense-room safe; consistent with the thesis-documented stack (FastAPI + vanilla JS + Chart.js + Jinja2, §4.3).
- Reuse the real engine; introduce **no new modelling math**.

**Non-goals (deferred):** HITL override loop, batch/portfolio scoring, multi-algorithm arena/benchmark, a separate scripted defense deck.

## 3. Locked decisions (brainstorm 2026-06-15)

1. **Purpose = C:** clean tool that doubles as the defense demo (usable by DAC afterward).
2. **Results scope = C:** Desk shows a full underwriting card; a *separate* "Watch it Learn" view holds the adaptive showcase.
3. **Stack:** FastAPI + vanilla JS + Chart.js (thesis-mandated). Reuse `healthrl`.
4. **Structure = A:** two views behind one top toggle; no second surface, no tab sprawl.
5. **Fairness badge = model-level:** PSI is a population metric, so the Desk shows a **standing model-level guardrail status** (computed on the dataset's protected-attribute distributions), never a per-applicant PSI.
6. **Scoring policy:** the Desk uses a **representative trained LinUCB policy** (θ from `coefficients_linucb_seed42.json`) — i.e. a deployed, already-trained model. "Watch it Learn" shows *how* such a policy is learned online. Coherent story: Learn = training; Desk = the trained model in use.
7. **Location:** build isolated in `demo/desk/`; cut over later (see §10).
8. **HITL:** deferred; when added it lives as a second act inside "Watch it Learn" and reuses the Desk applicant card.

## 4. Architecture overview

```
Browser (one page, two views)
  ├─ Underwriting Desk  ──POST /api/score──►  FastAPI ──► healthrl engine (θ scoring) + pricing_engine
  └─ Watch it Learn     ──POST /api/learn/run─► FastAPI ──► healthrl run_bandit (bandit vs static)
  Canonical headline ◄── thesis_results.json (static)
```

Single FastAPI app, single HTML page, small vanilla-JS modules, Chart.js vendored. All numbers either (a) canonical from `thesis_results.json` or (b) computed live and explicitly labelled illustrative/single-seed.

## 5. Backend — FastAPI endpoints (reuse only, no new math)

`demo/desk/app.py`:
- `GET /` → serve `demo/desk/static/index.html`.
- `GET /api/applicant/fields` → categorical options (regions, occupations, educations, wealth quintiles, health statuses, condition list) from the dataset. (Port from existing `applicant_fields`.)
- `GET /api/applicant/random` → a random CDHS applicant row. (Port from existing `random_applicant`.)
- `POST /api/score` → the underwriting-card payload (see §6).
- `POST /api/learn/run` → `{algorithm: LinUCB|LinTS, seed, n_rounds}` → cumulative-reward trajectory for the adaptive policy **and** the static baseline, plus early/late action-mix. Reuse `run_bandit` + `StaticXGBBaseline` (cf. existing `/api/bandit/compare`). Returns the full trajectory; the client animates it (no server streaming — simpler and robust).
- `GET /api/health` → `{status: ok}`.

Engine surface reused: `preprocess_cambodia_data`, `LinUCB`, `LinTS`, `StaticXGBBaseline`, `run_bandit`, `ACTION_NAMES = ["STANDARD","RATED","DECLINE","REFER"]`, `RewardConfig`; `pricing_engine.optimize_premium`. (`expected_rewards` is used transitively by `run_bandit`, not called directly by the app.)

## 6. Scoring model — `demo/desk/scoring.py`

`/api/score` receives the raw applicant fields, preprocesses them to a feature vector `x`, and scores with the representative trained policy θ (loaded once from `coefficients_linucb_seed42.json` at startup):

- **Estimated rewards** per action `r_a = θ_aᵀ x` → the four bars.
- **Decision** `a* = argmax_a r_a` (one of STANDARD / RATED / DECLINE / REFER).
- **Confidence** = `softmax(r)[a*]` with a fixed presentation temperature (default τ = 1.0 on the reward scale); a 0–1 "how sure" aid, labelled illustrative. (Tunable constant; not a thesis metric.)
- **Drivers** = top-3 features by `|θ_{a*,i} · x_i|`, each tagged ▲/▼ by sign, mapped to human labels via `FEATURES` from `preprocess_cambodia_data`. Illustrative interpretability.
- **Recommended premium** = `pricing_engine.optimize_premium(row, config)` → profit-optimal monthly premium + multiplier. **Action↔premium consistency:** STANDARD → base premium; RATED → loaded premium; DECLINE → premium card shows "—/declined"; REFER → "pending review".
- **Fairness status** (model-level, §3.5): standing PSI on the dataset's protected-attribute distributions (region, occupation) vs the reference window, with GREEN<0.10 / AMBER 0.10–0.25 / RED>0.25 (project thresholds). Computed once/cached; displayed as a standing badge, not per-applicant.

`mortality_multiplier` is hidden from the form: a loaded CDHS sample carries its row value; fully-manual entry defaults to 1.0 (neutral) with an internal note. (Known wrinkle — see §13.)

## 7. Frontend — one page, small modules (`demo/desk/static/`)

- `index.html` — two-view shell + top toggle pills (Underwriting Desk / Watch it Learn) + app header.
- `api.js` — thin `fetch` wrappers for the four endpoints.
- `desk.js` — applicant form render + result-card render.
- `learn.js` — Chart.js divergence chart + Play/Reset animation + action-mix bars.
- `main.js` — view toggle + shared state.
- Vendored `chart.umd.min.js` (copy from existing `demo/static/`).

### 7.1 Underwriting Desk (view 1)
- **Form (left):** "⟳ Load CDHS sample" + Clear; fields grouped **Demographics** (age, gender, region, occupation) / **Health & lifestyle** (BMI, self-reported health; smoker/alcohol/exercise/family-history toggles; pre-existing conditions chips) / **Socioeconomic** (income, education, wealth quintile). `mortality_multiplier` hidden. **Score applicant →** button. All ~14 fields shown grouped (no Advanced toggle — user approved depth).
- **Result card (right):** big decision badge + confidence; model-level fairness badge; four expected-reward bars (winner highlighted); recommended premium; "why this decision" top-3 drivers; a persistent *"Illustrative · single seed (42)"* line.

### 7.2 Watch it Learn (view 2)
- **Canonical headline strip:** +25.2% vs Static XGB · 20 seeds · p<0.001 · d=2.98, tagged "thesis Ch.5" — loaded from `thesis_results.json`.
- **Divergence chart:** cumulative reward over rounds, adaptive policy vs Static XGB, animated by ▶ Play to the current round; **Reset**; **LinUCB/LinTS** selector; round counter; live **"+X% (illustrative, seed 42)"** readout.
- **Behaviour-shift panels:** early (exploring, spread) vs late (exploiting, concentrated) action mix.

## 8. Canonical vs illustrative discipline

Carry over the existing demo's rule (README §"Authoritative vs illustrative"): headline claims (means, CIs, p, d) come **only** from `thesis_results.json`; anything computed live is single-seed and visibly labelled illustrative. Never quote a live single-seed number as the result.

## 9. Error handling & offline robustness

Pydantic validation on `/api/score`; inline form errors, never a crash; engine exceptions return a clean JSON error rendered as a card message. Everything local; Chart.js vendored; "Load sample" always works (deterministic dataset). No network/CDN dependency → safe in a wifi-free defense room.

## 10. File layout & migration / cutover

```
demo/desk/
  __init__.py
  app.py          # FastAPI app + routes
  scoring.py      # θ scoring, confidence, drivers, premium, model PSI
  learning.py     # bandit-vs-static trajectory + action mix
  static/         # index.html, api.js, desk.js, learn.js, main.js, chart.umd.min.js
```

Build alongside the old demo (which keeps backing the Render deploy and the PPTX Live-Demo screenshots). **Cutover (separate, later step):** repoint `render.yaml` from `demo.main:app` to `demo.desk.app:app`, then delete `demo/main.py`, the 7-tab `demo/templates/index.html`, and `demo/static/defense.{html,js}`. Cutover is out of scope for the first implementation; it happens once the new app is validated.

## 11. Testing plan

`tests/test_desk_app.py` (pytest, mirrors repo conventions):
- `/api/applicant/fields` returns non-empty option lists.
- `/api/applicant/random` returns a valid applicant dict.
- `/api/score` returns a well-formed card: a valid action in `ACTION_NAMES`, four numeric rewards, a numeric premium (or declined), exactly 3 drivers, a fairness status in {GREEN,AMBER,RED}.
- `/api/learn/run` returns adaptive + static trajectories of length `n_rounds` and early/late action mixes summing to ~1.
- Canonical headline loader reads from `thesis_results.json` (no hardcoded fallback).
- Boot/serve smoke test (`GET /` 200, `GET /api/health` ok).

## 12. Out of scope / deferred

HITL override; batch/portfolio; arena/benchmark; the separate defense deck; the cutover/deletion of the old demo; deploy changes.

## 13. Open details / risks

- **`mortality_multiplier` default (1.0) for manual entry** shifts results vs a loaded sample's real value. Acceptable for a demo; revisit if it confuses. The "Load CDHS sample" path (real value) is the primary demo flow.
- **Confidence τ** is a presentation constant, not a thesis quantity — keep it labelled illustrative so it isn't mistaken for a calibrated probability.
- **Representative θ (seed 42)** means the Desk is a fixed deployed policy, not retrained per session — intended, and consistent with the Learn view's framing.
- **Model-level PSI** badge must be worded as model/guardrail status, never per-applicant (examiner-sensitive).
