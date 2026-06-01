# Demo — Adaptive Underwriting via Contextual Bandits

Two surfaces over one FastAPI backend (`demo/main.py`), both on the thesis-mandated stack (FastAPI + vanilla JS + Chart.js + Jinja2, §4.3):

| URL | Surface | Use |
|-----|---------|-----|
| `/defense` | 10-scene **defense deck** | The guided narrative for the defense. |
| `/` | 6-tab **sandbox tool** | Hands-on exploration a reviewer can drive. |

## Run

```bash
uvicorn demo.main:app --reload --port 8000
# open http://localhost:8000/        (sandbox)
#      http://localhost:8000/defense (deck)
```

Requires the repo's pinned deps (`requirements.txt`): numpy, pandas, scikit-learn, xgboost, fastapi, uvicorn, pydantic.

## Authoritative vs illustrative — read this first

The demo deliberately separates two kinds of numbers:

- **Authoritative / canonical** — the **20-seed** headline results (means, 95% CIs, p-values, Cohen's d). These are served from **`demo/static/thesis_results.json`** (transcribed verbatim from the Chapter V tables, each tagged with its source section) and from the static thesis figures. They are what the thesis *claims*.
- **Illustrative** — anything computed **live** in the browser runs a **single seed** and is labelled "Illustrative". A single seed (e.g. seed 42 = +27.7%) does **not** equal the 20-seed headline (+25.2%); the live charts build intuition, the canonical cards carry the claim.

Never quote a live single-seed number as the result.

## Defense deck — scene → chapter map

| Scene | Title | Backs | Source |
|------:|-------|-------|--------|
| 1 | The 1% Problem | Motivation | §2.1 |
| 2 | Why Static Rules Fail | Problem 1 (risk selection) | §2.2; live `/api/simulate` |
| 3 | Explore vs Exploit | Core RL idea + decision-loop diagram | §4.4 |
| 4 | Bandit Arena | **RQ1 / EXP-005** — canonical +25.2%, d=2.98 + live seed-42 curve + Fig 5.1 | §5.1 |
| 5 | Benchmark Race | **RQ3 / EXP-007** + **EXP-013** Õ(d√T) | §5.3, §5.6 |
| 6 | Coefficient Audit | NFR-7 interpretability (θ per action) | §4.6 |
| 7 | Fairness & PSI | **RQ2 / EXP-006** — EEOC 80%, parity 85.7%/90.1%, PSI 0.082 GREEN / 0.123 AMBER | §5.2 |
| 8 | Human-in-the-Loop | **RQ4 / EXP-008** — c=0.7: +6.5% @ 1.5% referral; dual-update | §5.4 |
| 9 | Drift Adaptation | EXP-009 (real fig + 0.29×/0.85×) + DiscountedLinUCB (future work) | §5.9, §6.3.1 |
| 10 | Four Contributions | Close | §6 |

## Sandbox tabs

1. **Applicant Simulator** (FR-1) — expected reward for all four actions + the bandit's argmax pick.
2. **Pricing Engine** (FR-2) — continuous premium optimiser + profit curve + batch portfolio + live PSI.
3. **Bandit Arena** (FR-3) — single-algorithm run with the Õ(d√t) overlay.
4. **Benchmark Race** (FR-3) — all four algorithms head-to-head.
5. **Underwriter Review** (HITL) — bandit recommends → you override → it learns; PSI on the approved pool; CSV export; **Reset Session** to start clean.
6. **Interpretability** (NFR-7) — per-action θ weights.
7. **More Experiments** — EXP-010 cold-start, EXP-011 ablation, EXP-012 sensitivity (canonical numbers).

A top strip surfaces the canonical 20-seed headline on every tab and links to `/defense`.

## Notes
- `POST /api/hitl/reset` clears the review log (sqlite `hitl.db`) and resets the in-memory bandit — handy between rehearsals.
- All headline numbers trace to `docs/thesis_analysis.md` and the Chapter V tables; see `docs/repository_audit.md` and `docs/demo_redesign_spec.md` for the alignment rationale.
