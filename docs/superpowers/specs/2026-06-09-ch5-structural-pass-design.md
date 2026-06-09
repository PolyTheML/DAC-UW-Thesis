# Chapter V Structural Pass — Design Spec (2026-06-09)

**Status:** approved in brainstorming; pending user spec-review → writing-plans.
**Builds on:** the figure overhaul (r4 green on Overleaf, 2026-06-09). This pass is the
"deferred structural" bucket surfaced during that work.
**Authoritative sources:** `research/reward_sensitivity_analysis.md`,
`research/elasticity_sweep_findings.md`, `research/horizon_check.py`,
`research/thesis_reframe.md` §6. Live status: memory `figure-overhaul-status`,
`latex-migration-status`, `thesis-reframe-status`.

---

## 1. Problem

`thesis/Thesis/Chapters/ch5-Results.tex` has three coupled defects, all rooted in the
docx→LaTeX port dropping content + a manual-vs-auto numbering mismatch:

1. **Phantom sections.** The prose makes **22 references** to §5.11/§5.12/§5.13, but those
   sections do not exist (the file ends at EXP-010 / §5.10). They are three real, already-run
   experiments the reframe intended for Chapter V but that were never ported to LaTeX.
2. **Section auto-numbering offset.** `secnumdepth=3` auto-numbers sections, but LaTeX numbers
   the opening "Statistical Methodology" section §5.1 while the prose treats it as §5.0 (ladder =
   §5.0.1). Everything is therefore off by one, and the EXP-013 title carries a baked-in literal
   "5.6 " that double-prints ("5.7 5.6 EXP-013").
3. **LoF double-number** (cosmetic) — **DEFERRED this pass** (see §6).

The physical `\section` order in the file **already equals** the intended prose scheme
(Methodology, 005, 006, 007, 008, Discussion, 013, 011, 012, 009, 010); only the §5.0 offset and
the baked-in "5.6 " break it.

## 2. Scope (locked)

**In:** (A) section-numbering fix; (B) re-add §5.11/§5.12/§5.13 as **tables + prose only**
(no new figures); (C) rebuild r5 + Overleaf verify.
**Out / deferred:** LoF double-number; any new figures; the `.md` mirror
(`chapter05_results.md` — docx path, not the active build); §5.7.4/Table 15 one-sided framing
(user already chose minimal).

## 3. Design

### 3.1 Section-numbering fix (low risk, 2 edits)
- Insert `\setcounter{section}{-1}` at the very top of `ch5-Results.tex` (before the first
  `\section`). The enclosing `\chapter`/`\mychapter` already reset `section` to 0; this nudges the
  first `\section` to §5.0. Localized — ch6's `\chapter` resets the counter, so ch6 is unaffected.
- Edit the EXP-013 `\section` title (currently line 454): remove the literal `5.6 ` from both the
  `\texorpdfstring` display and PDF-string halves, leaving `EXP-013: Empirical Validation of the
  $\tilde O(d\sqrt T)$ Regret Bound`. Auto-numbering supplies the 5.6.

**Resulting auto-numbers:** Methodology 5.0, EXP-005 5.1, EXP-006 5.2, EXP-007 5.3, EXP-008 5.4,
Discussion 5.5, EXP-013 5.6, EXP-011 5.7, EXP-012 5.8, EXP-009 5.9, EXP-010 5.10 — matching every
existing ref incl. subsections §5.0.1, §5.3.2, §5.4.2, §5.8.4, §5.9.3, §5.9.5, §5.10.3. The three
re-added sections then auto-number 5.11, 5.12, 5.13.

### 3.2 §5.11 Reward-Model Sensitivity
- **Title:** `\section{Reward-Model Sensitivity --- Is the Negative Result an Artifact of the
  Reward Design?}`
- **Source:** `reward_sensitivity_analysis.md` + `results/reward_sensitivity_results.csv` (6 reward
  models × 8 policies × 20 seeds, common random numbers) + `reward_sensitivity_summary.json`.
- **Content:** (a) why this experiment exists — does removing the simulator's asymmetries (A:
  symmetric adverse-selection, B: A+symmetric cost, C: swept fair-pricing loadings) overturn the
  constant-beats-bandit result? (b) the headline: the ranking
  `Oracle > AlwaysRATED > LinTS ≈ LinUCB > StaticXGB > AlwaysSTANDARD > Random` is **invariant
  across all six models**; (c) the bandit holds at **74–82 % of the best constant** in every model;
  (d) significance: every learner is worse than AlwaysRATED, p < 0.0001, |d| = 3.5–7.5; (e) the
  honest nuance — AlwaysRATED's *share of oracle* IS sensitive (96.8 %→81.8 % once A1/A4 corrected,
  so the old "97.6 % of oracle" overstated near-optimality) but the *ranking* never moves; and
  LogisticOracle ≈ Oracle in every model ⇒ structure is linearly representable, so the bandit's
  shortfall is a partial-feedback/exploration cost, not a representational limit.
- **Tables (2):**
  - **Table 22** — mean cumulative reward, 8 policies × 6 reward models (20 seeds). Wide table;
    follow the existing wide-table idiom (it will overfull-hbox harmlessly like ch4–5's others).
  - **Table 23** — learner vs AlwaysRATED: Wilcoxon p + Cohen's d across the 6 models.
- **Key numbers to reproduce from CSV before writing** (ORIGINAL column, must match ch5's existing
  EXP-007 line and the ladder): AlwaysRATED 122,287 · LinTS 93,723 · LinUCB 91,864 · StaticXGB
  72,206 · Oracle 126,351.

### 3.3 §5.12 EXP-016 Demand-Elasticity Sweep
- **Title:** `\section{EXP-016: Demand-Elasticity Sweep --- Does Any Demand Regime Rescue the
  Bandit?}`
- **Source:** `elasticity_sweep_findings.md` + `results/elasticity_sweep_results.csv` +
  `_summary.json` (`research/elasticity_sweep.py`, 20 seeds, stationary, CRN).
- **Relationship to §5.8.4:** EXP-012's existing "Customer-elasticity slope sweep" (§5.8.4,
  Table 18) is a 3-point robustness check comparing LinUCB vs Static XGB. EXP-016 is the
  **dedicated 7-point sweep comparing the learner vs the best constant**, re-anchoring acceptance
  so mean acceptance ≈ 0.5 at every slope. The section MUST open by stating it complements (not
  duplicates) §5.8.4, to avoid reader confusion.
- **Content:** (a) method (sweep, not tuning; re-anchored acceptance; LMIC demand is realistically
  inelastic ≈ −0.2…−0.5 while the sim sits ≈ −1.1…−1.4); (b) headline: **no elasticity lets any
  learner beat the best constant** (learner stays ~73–88 %); (c) the sharp nuance — at the
  realistic *inelastic* end the best constant **is** the oracle (100 %, no contextual structure
  exists), while at the *elastic* end contextual structure emerges (best-constant-vs-oracle gap
  0 %→7.4 %) and a fully-supervised linear model captures it (97–100 %) but the bandit still does
  not; (d) verdict — combined with §5.11/drift/HITL, no tested regime rescues the bandit.
- **Table (1):**
  - **Table 24** — 7-point sweep: elasticity (−0.24 … −1.32) × {best constant, LinUCB, LinTS,
    LogisticOracle, Oracle, best-constant÷oracle, learner>constant?}.
- **Key numbers to reproduce:** inelastic −0.24 → best-constant 365,385 = oracle (100 %); most
  elastic −1.32 → best-constant 311,532, LinTS 273,091, gap-to-oracle 7.4 %; "learner > constant?"
  = no at every row.

### 3.4 §5.13 Horizon Check
- **Title:** `\section{Horizon Check --- Is the Defeat Structural or Cold-Start Cost?}`
- **Source:** run `research/horizon_check.py` (N = 20,000 rounds, 5 seeds, ORIGINAL reward,
  policies Oracle/AlwaysRATED/LinUCB/LinTS). The script prints the table; capture its stdout.
- **Content:** (a) the discriminating question — the 5,000-round main results charge the bandit its
  full cold-start cost over a short horizon; does the **steady-state** (last 1,000 of 20,000)
  per-round reward reach the constant, and does cumulative reward ever cross AlwaysRATED?
  (b) answer: late-window bandit per-round reward stays **below** the constant and cumulative
  **never crosses** within 20,000 rounds ⇒ the defeat is **structural**, not a finite-horizon
  artifact; (c) ties back to §5.6 (EXP-013 validates the √T *rate* at which LinUCB learns its *own*
  optimum; §5.13 shows that optimum is itself below the constant, so the regret tail vs the best
  simple policy is ultimately linear).
- **Table (1):**
  - **Table 25** — per-round reward by window {0–1k, 4–5k, 9–10k, 19–20k} for the 4 policies, plus
    the steady-state verdict and the "never crosses" gap.
- **Numbers:** produced by the `horizon_check.py` run (implementation step). Note: 5 seeds (long
  horizon is expensive) — state the seed count explicitly in the caption, consistent with the
  chapter's "unless noted" multi-seed convention (§5.0).

### 3.5 Cross-reference resolution
After the three sections exist, all **22** §5.11/§5.12/§5.13 references resolve to real sections.
No ref rewriting is needed (they already use the correct target numbers). Implementation must grep
`5\.1[123]` post-edit and confirm every hit now has a matching `\section`.

### 3.6 Build r5 + verify
- New zip `thesis/Thesis_overleaf_2026-06-09_r5.zip` via a `zip_thesis_r5.py` that extends the r4
  asserts: (a) `\setcounter{section}{-1}` present in ch5; (b) no baked-in "5.6 " in the EXP-013
  title; (c) the three new `\section` titles present; (d) new manual "Table 22/23/24/25" present;
  (e) **every** §5.11/§5.12/§5.13 ref has a real section (0 dangling); (f) all r4 figure checks
  still pass (regression). Python `zipfile`, forward-slash arcnames.
- **r5 is "done" only when an Overleaf XeLaTeX log proves it**: 0 TeX errors; sections render
  5.0–5.13; the 22 refs point at the right numbers; tables 22–25 present; prior error classes 0.

## 4. Verification requirements
- Reproduce §5.11 + §5.12 key numbers **from the CSVs** before drafting (don't trust the findings
  docs blind); they must also be internally consistent with existing ch5 numbers (EXP-007 line,
  ladder, §5.8.4).
- Run `horizon_check.py`; use its actual output for §5.13 + Table 25.
- Maintain the honest reframe framing throughout — these sections *reinforce* the negative result
  (constant beats bandit robustly); no overclaim, no "bandit wins" language.
- Brace/`\section`/environment balance check on ch5 after edits; advisor review before the r5 build.

## 5. Out of scope / deferred
- **LoF double-number** — the `\fg`/`\caption` mechanism prints the auto chapter-figure number
  ("5.1") beside the manual "Figure N." A clean global fix is fragile (captions carry math/markup
  that must survive re-writing to `.lof`); purely cosmetic. Separate isolated micro-pass later.
- **New figures** for the re-added sections (stale reframe-era PNGs exist; regenerating to the
  `_style.py` vector standard + extending numbering is a separate figure-pass).
- **`.md` mirror** `chapter05_results.md` (docx path; only matters if docx is rebuilt).

## 6. Risks
- **Wide Table 22** (8×6) may overfull-hbox like the other wide ch4–5 tables — acceptable
  (pre-existing class of cosmetic residue); consider `\footnotesize`/`\resizebox` if egregious.
- **`\setcounter{section}{-1}` side effects** — must verify it does not leak past ch5 (ch6/appendix
  numbering unchanged) in the r5 Overleaf log.
- **Number drift** — the findings docs are dated 2026-06-03; if the CSVs have since changed,
  reproduce-from-CSV catches it. If `horizon_check.py` won't run cleanly, that's an implementation
  blocker to surface (the section's conclusion is known from existing refs, but the table needs the
  run).

## 7. Files touched
- `thesis/Thesis/Chapters/ch5-Results.tex` (setcounter + EXP-013 title + 3 appended sections).
- `%TEMP%\zip_thesis_r5.py` (new build script).
- Output: `thesis/Thesis_overleaf_2026-06-09_r5.zip`.
- No preamble (`Main_content.tex`) change (LoF deferred).
