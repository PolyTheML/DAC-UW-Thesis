# Figure Overhaul — Design Spec (2026-06-08)

Publication-ready (IEEE/Springer/Elsevier/Nature-grade) figures for the thesis,
resolved via `/grill-me`. Thesis builds on Overleaf/XeLaTeX; figures embed via the
`\fg{width}{caption}{path}` macro (preamble `Main_content.tex`). Current r3 = 92pp,
17 figures, all PNG `\fg{0.85\textwidth}{...}{images/NAME.png}`.

## Locked decisions (grill, 2026-06-08)

1. **Scope** — full overhaul: restyle all 17 in-thesis figures **and** build the
   F1–F8 reviewer-grade set from `research/figures_plan.md` (F1 already shipped = Fig 7).
2. **Font** — Times New Roman serif for ALL figures (match the thesis body). Figures
   pre-render on the user's Windows box (Times installed) → no Overleaf font dependency.
3. **Format** — vector **PDF**; repoint `\fg` paths `.png`→`.pdf`; rebuild + verify **r4**.
   PNGs kept as fallback.
4. **In-figure titles** — **stripped** (the LaTeX caption already describes each figure);
   keep axis labels, legends, and multi-panel (a)/(b)/(c)/(d) labels.
5. **Diagrams (Fig 1–6)** — redraw as native **TikZ** (all six, for consistency), inline in
   the chapters; exact Times match, true vector, compiles in-preamble (`tikz` already loaded).
6. **Data plots (Fig 7–17)** — re-render through a shared style module; **re-run**
   EXP-005/006/007/008/009/010/013 to regenerate faithfully (deterministic: pinned seeds
   1–20 + `config.py` + `requirements.lock.txt`). **Verify** each figure's headline numbers
   against the frozen captions; flag any drift — do NOT silently swap.
7. **New figures** — F2 (ablation forest) + F4 (PSI bands) → **body** (one referencing
   sentence each + renumber); F3, F5, F6, F7, F8 → **Supplementary Figures appendix**
   (Appendix A is kept) so the frozen body numbering is otherwise undisturbed.
8. **Execution** — **phased with a style checkpoint**. Phase 1 produces the style module +
   2 sample vectors for sign-off BEFORE mass production.

## Implementation specifics

- **Palette** — Okabe-Ito colorblind-safe (from `figures_plan.md`): oracle `#000000`,
  lints `#0072B2`, linucb `#009E73`, epsilon `#E69F00`, static `#D55E00`,
  logistic `#CC79A7`, random `#999999`, constant `#56B4E9`. Unify `make_reward_figures.py`'s
  ad-hoc COLORS onto this.
- **Shared module** — `thesis/health_rl/figures/_style.py`: rcParams (Times serif text +
  mathtext, label/tick sizes tuned for `0.85\textwidth` ≈ 13.6 cm single column), CI-band
  helper, palette, no-title convention, `savefig` → PDF (vector) **and** 300 dpi PNG, tight bbox.
  All result generators import it.
- **Integration** — each data plot → `images/NAME.pdf` (+ keep `NAME.png`); `\fg` 3rd arg → `.pdf`.
  Diagrams → TikZ blocks replace the `\fg{...png}` lines for Fig 1–6.
- **Build** — `%TEMP%\zip_thesis_r4.py` (extend r3 asserts: `\fg` targets are `.pdf`, the 6
  TikZ blocks present, new figure files present, renumber clean, 0 residual chapter-prefixed nums).

## Figure register (source · technique · placement)

| # | Name | Source data | Technique | Placement |
|---|------|-------------|-----------|-----------|
| 1 | organization_chart | — (hand) | **TikZ redraw** | ch1 body |
| 2 | ch2_system_architecture | script+svg | **TikZ redraw** | ch2 body |
| 3 | ch2_project_timeline | script+svg | **TikZ redraw** | ch2 body |
| 4 | ch4_architecture | script | **TikZ redraw** | ch4 body |
| 5 | ch4_bandit_loop | script | **TikZ redraw** | ch4 body |
| 6 | framework | — (hand) | **TikZ redraw** | ch4 body |
| 7 | baseline_ladder (F1) | `exp_014_baseline_ladder.json` (cache) | restyle, vector | ch5 body |
| 8 | reward_curves | EXP-005 re-run | new generator, vector | ch5 body |
| 9 | action_evolution | EXP-005 re-run | new generator, vector | ch5 body |
| 10 | fairness_region | EXP-006 re-run | new generator, vector | ch5 body |
| 11 | fairness_occupation | EXP-006 re-run | new generator, vector | ch5 body |
| 12 | regret_curves | EXP-007 re-run | new generator, vector | ch5 body |
| 13 | hitl_experiment (4-panel) | EXP-008 re-run | restyle in-script, vector | ch5 body |
| 14 | loglog_regret | EXP-013 re-run | restyle in-script, vector | ch5 body |
| 15 | 009_drift_adaptation | EXP-009 re-run | restyle in-script, vector | ch5 body |
| 16 | drift_rescue_ladder | `drift_rescue_*.csv` (cache) | restyle, vector | ch5 body |
| 17 | 010_cold_start | EXP-010 re-run | restyle in-script, vector | ch5 body |
| F2 | ablation_forest | EXP-011 re-run (paired diffs) | new, vector | **ch5 body** (§5.7) |
| F4 | psi_timeseries | EXP-006 re-run (PSI(t)) | new, vector | **ch5 body** (§5.2) |
| F3 | exploration_x_regime | EXP-007 + EXP-009 | new, vector | appendix |
| F5 | xgb_calibration | `cambodia_test_predictions.csv` (cache) | new, vector | appendix |
| F6 | decision_regions | new 2-D oracle/bandit grid (new code) | new, vector | appendix |
| F7 | data_calibration | dataset marginals vs CDHS/STEPS (docstring) | new, vector | appendix |
| F8 | regret_bound_overlay | EXP-013 + theoretical O(d√T) | new, vector | appendix |

## Phase plan

- **Phase 1 (checkpoint + REPRODUCTION GATE)** —
  (a) `git diff` the modified core (`underwriting_bandit.py`, `exp_011`, `exp_010`) to learn
  whether the frozen numbers predate the edits;
  (b) build `_style.py` and immediately **stress Times mathtext** (α/β/$d$/√T/subscripts) — if it
  falls back to DejaVu, switch to matplotlib's **pgf** backend (LaTeX typesets the text); decide
  this AT the checkpoint, not after 24 figures;
  (c) run **EXP-005 as a go/no-go reproduction check** — it must return ≈ \$90,540 / \$72,292 to
  within rounding, else **HALT and reconcile** before Phase 2–5;
  (d) render **Fig 7** (ladder, cache) + one **math-bearing** sample (reward/regret curve with the
  regret notation) as vector PDF → user sign-off on the look.
- **Phase 2** — re-render the remaining data plots (Fig 9–17) via re-runs + cache; verify numbers.
- **Phase 3** — author the 6 TikZ diagrams.
- **Phase 4** — build the 7 new figures (F2/F4 body, F3/F5/F6/F7/F8 appendix).
- **Phase 5** — repoint `\fg`→`.pdf`, renumber (F2/F4 insertions), build **r4**, verify compile + numbers.

## Risks / gates

- **UNCOMMITTED CORE CODE (critical, advisor-flagged).** `underwriting_bandit.py`, `exp_011`,
  `exp_010` have uncommitted edits at session start; the frozen thesis numbers may predate them, so
  re-running could regenerate figures that *contradict* the frozen text. Gate: `git diff` first, then
  the EXP-005 reproduction go/no-go, before any mass production. F2 (body) depends on modified
  `exp_011` → verify the §5.7 ablation numbers reproduce **before** drawing it.
- **Times mathtext** in matplotlib may fall back to DejaVu for math glyphs → use the `pgf` backend
  (LaTeX typesets text) if so; decide at the Phase-1 checkpoint.
- **Framing fidelity** — every regenerated/new figure must encode the honest "beats *deployable*
  alternatives, bounded by the inadmissible AlwaysRATED constant" framing (see `thesis_reframe_status`);
  a prettier figure is the easiest place to silently re-introduce the prior overclaim. Watch the ladder
  and any constant-policy figure especially.
- **Frozen-number drift** on re-run → verify each figure's headline values vs the frozen text; reconcile, don't overwrite.
- **Renumbering**: inserting F2/F4 into the body shifts Fig numbers → re-run `renumber.py`/`renumber_md.py`, fix manual in-text refs (no `\ref` exists).
- **TikZ compile/overflow** → caught in the r4 Overleaf log.
- **F6 decision-regions** is the only genuinely new experiment code (2-D policy grid) — highest-cost new figure.
- r4 is "done" only when an Overleaf log proves it (no local TeX).
