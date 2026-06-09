# Chapter V Structural Pass — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans (inline) or
> superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox
> (`- [ ]`) syntax.
>
> **Adaptation note:** this is thesis LaTeX content + numeric verification, not code-with-unit-tests.
> The "test-first" gate is: **reproduce every number from its CSV / experiment output before writing
> it into the thesis.** Verification = reproduction scripts + r5 zip self-checks + the Overleaf
> XeLaTeX log (the only proof of compilation; there is no local TeX). **Commits are user-gated** —
> do not commit unless the user asks.

**Goal:** Re-add the three missing Chapter V sections (§5.11 Reward-Model Sensitivity, §5.12 EXP-016
Demand-Elasticity Sweep, §5.13 Horizon Check), fix the §5.0 section-numbering offset, and ship a
green r5 — resolving all 22 dangling §5.11/§5.12/§5.13 references.

**Architecture:** Append three table+prose sections after EXP-010 (§5.10) in `ch5-Results.tex`; a
one-line `\setcounter{section}{-1}` plus removing a baked-in "5.6 " makes the whole chapter
auto-number 5.0–5.13 so the new sections land exactly where the prose already points. No preamble
change, no new figures, no `.md` mirror edits (all deferred).

**Tech Stack:** XeLaTeX (Overleaf), Python (`zipfile`, `pandas`/`csv`, the `research/` harnesses),
the existing `\fg`/`\captionof{table}` + `labelformat=empty` manual-numbering idiom.

**Spec:** `docs/superpowers/specs/2026-06-09-ch5-structural-pass-design.md`

---

## File Structure

- **Modify** `thesis/Thesis/Chapters/ch5-Results.tex`
  - top of file: `\setcounter{section}{-1}`
  - EXP-013 `\section` title (~line 454): drop literal `5.6 `
  - end of file (after §5.10 Pass/Fail, ~line 884+): append §5.11, §5.12, §5.13
- **Create** `%TEMP%\verify_ch5_numbers.py` — reproduces §5.11/§5.12 numbers from CSVs; asserts.
- **Run** `research/horizon_check.py` — produces §5.13 numbers (capture stdout).
- **Create** `%TEMP%\zip_thesis_r5.py` — extends `zip_thesis_r4.py` asserts; builds the r5 zip.
- **Output** `thesis/Thesis_overleaf_2026-06-09_r5.zip`
- **No change:** `Main_content.tex` (LoF deferred), `chapter05_results.md` (docx mirror, deferred).

---

## Task 0: Establish ground-truth numbers (the "test-first" step)

**Files:** Create `%TEMP%\verify_ch5_numbers.py`; run `research/horizon_check.py`.

- [ ] **Step 1: Write the reproduction + assertion script**

```python
# %TEMP%\verify_ch5_numbers.py
import pandas as pd, json, pathlib
RES = pathlib.Path(r"C:\DAC-UW-Thesis\research\results")

# --- 5.11 reward sensitivity: ORIGINAL column must match ch5 EXP-007 / ladder ---
rs = pd.read_csv(RES / "reward_sensitivity_results.csv")
print("reward_sensitivity columns:", list(rs.columns))
print(rs.head(20).to_string())
# Expected ORIGINAL means (20 seeds): AlwaysRATED 122,287 | LinTS 93,723 | LinUCB 91,864
#   | StaticXGB 72,206 | Oracle 126,351  (cross-check against ch5 line ~317 + ladder Fig 6)

# --- 5.12 elasticity sweep: 7 rows, learner never > best constant ---
el = pd.read_csv(RES / "elasticity_sweep_results.csv")
print("\nelasticity columns:", list(el.columns))
print(el.to_string())
# Expected endpoints: -0.24 -> best constant 365,385 == oracle (100%);
#   -1.32 -> best constant 311,532, LinTS 273,091, gap-to-oracle ~7.4%; learner>constant = NO all rows
```

- [ ] **Step 2: Run it and record the exact reproduced values**

Run: `python "%TEMP%\verify_ch5_numbers.py"`
Expected: the printed tables; confirm the ORIGINAL reward-sensitivity means match ch5's existing
EXP-007 falsification line (AlwaysRATED 122,287 > LinTS 93,723 > LinUCB 91,864) and the elasticity
endpoints above. **If any number differs from the findings docs, use the CSV value (it is
authoritative) and note the drift.**

- [ ] **Step 3: Run the horizon experiment for §5.13**

Run: `python research/horizon_check.py` (N=20,000 × 5 seeds × 4 policies; may take a few minutes —
use `run_in_background` if it exceeds the foreground timeout, then collect output).
Expected stdout: a per-window table; **LinUCB and LinTS steady-state (19k–20k) per-round reward
BELOW AlwaysRATED**, and **"NEVER crosses AlwaysRATED within 20,000 rounds"** for both. Record the
exact per-window values + the final cumulative gap — these populate Table 25.
**If the script errors (import/env), surface it as a blocker before drafting §5.13.**

- [ ] **Step 4: Freeze the numbers**

Paste the three reproduced result blocks into a scratch note (or this plan's margin) so Tasks 2–4
quote verified values, not findings-doc values. No commit.

---

## Task 1: Section-numbering fix

**Files:** Modify `thesis/Thesis/Chapters/ch5-Results.tex` (top of file + EXP-013 title).

- [ ] **Step 1: Read the current top of the file and the EXP-013 \section line**

Run: read `ch5-Results.tex` lines 1–4 and 454.

- [ ] **Step 2: Insert the section counter reset at the very top**

Add as the first line of the file (before the first `\section`):

```latex
% Chapter opens at §5.0 (Statistical Methodology); the \chapter reset to 0 is nudged to -1 so the
% first \section becomes 5.0, matching the prose scheme (ladder = §5.0.1, EXP-005 = §5.1, ...).
\setcounter{section}{-1}
```

- [ ] **Step 3: Remove the baked-in "5.6 " from the EXP-013 title**

Change (line ~454):
```latex
\section{\texorpdfstring{5.6 EXP-013: Empirical Validation of the \(\tilde O(d\sqrt{T})\) Regret Bound}{5.6 EXP-013: Empirical Validation of the \textbackslash tilde O(d\textbackslash sqrt\{T\}) Regret Bound}}\label{exp-013-empirical-validation-of-the-tilde-odsqrtt-regret-bound}
```
to (drop both `5.6 ` prefixes):
```latex
\section{\texorpdfstring{EXP-013: Empirical Validation of the \(\tilde O(d\sqrt{T})\) Regret Bound}{EXP-013: Empirical Validation of the \textbackslash tilde O(d\textbackslash sqrt\{T\}) Regret Bound}}\label{exp-013-empirical-validation-of-the-tilde-odsqrtt-regret-bound}
```

- [ ] **Step 4: Verify the edits are in place**

Run: grep `\\setcounter\{section\}\{-1\}` and `5\.6 EXP-013` in ch5.
Expected: setcounter present (1 hit); `5.6 EXP-013` now ABSENT (0 hits). (Compilation correctness is
proven later by the r5 Overleaf log: sections render 5.0–5.13.)

---

## Task 2: Draft §5.11 Reward-Model Sensitivity

**Files:** Modify `ch5-Results.tex` (append after §5.10 Pass/Fail, before any closing content).

- [ ] **Step 1: Append the section skeleton + Table 22 + Table 23**

Use the existing chapter idiom exactly: `\section{...}` (auto-numbers 5.11), prose paragraphs,
and `\captionof{table}{Table 22 --- ...}\label{tab:5.11.1}` inside the project's longtable/table
pattern (copy the structure of an existing ch5 table, e.g. Table 21). Content per spec §3.2:

Section title: `\section{Reward-Model Sensitivity --- Is the Negative Result an Artifact of the Reward Design?}`

Required prose beats (honest framing — reinforces the negative result):
1. Purpose: tests whether removing simulator asymmetries (A sym-adverse, B A+sym-cost, C swept
   fair-pricing loadings ℓ=.45/.60/.75) overturns constant > bandit. CRN, 20 seeds, 6 models.
2. Headline: ranking `Oracle > AlwaysRATED > LinTS ≈ LinUCB > StaticXGB > AlwaysSTANDARD > Random`
   is invariant across all six models (Table 22). Bandit holds 74–82 % of best constant everywhere.
3. Significance (Table 23): every learner < AlwaysRATED, p < 0.0001, |d| 3.5–7.5.
4. Honest nuance: AlwaysRATED's *share of oracle* IS sensitive (96.8 %→81.8 % once A1/A4 corrected
   — the old "97.6 % of oracle" overstated near-optimality) but the *ranking* never moves; and
   LogisticOracle ≈ Oracle in every model ⇒ the optimal policy is linearly representable, so the
   bandit's shortfall is a partial-feedback/exploration cost, not a representational limit.

**Table 22** (mean cumulative reward, 20 seeds; columns = ORIGINAL, A, B, C ℓ=.45, C ℓ=.60,
C ℓ=.75; rows = Oracle, LogisticOracle‡, AlwaysRATED, LinTS, LinUCB, StaticXGB†, AlwaysSTANDARD,
Random). Use the Task-0 reproduced values. ORIGINAL column anchor:
122,287 / 93,723 / 91,864 / 72,206 / 126,351 (RATED/LinTS/LinUCB/Static/Oracle).

**Table 23** (learner vs AlwaysRATED): rows = 6 models; cols = LinUCB p, LinTS p, Cohen's d
(LinUCB/LinTS). All p < 0.0001; d from the CSV (ORIGINAL −5.14 / −4.51, etc.).

- [ ] **Step 2: Verify the numbers written match Task 0**

Run: grep the key figures (122,287 ; 93,723 ; 91,864) in the new §5.11 block; eyeball Table 22/23
against the Task-0 output. Expected: exact match.

- [ ] **Step 3: Brace/environment balance spot-check** (full check in Task 5).

---

## Task 3: Draft §5.12 EXP-016 Demand-Elasticity Sweep

**Files:** Modify `ch5-Results.tex` (append after §5.11).

- [ ] **Step 1: Append section + Table 24**

Section title: `\section{EXP-016: Demand-Elasticity Sweep --- Does Any Demand Regime Rescue the Bandit?}`
(auto-numbers 5.12).

Required prose beats (per spec §3.3):
1. **Opening sentence MUST distinguish from §5.8.4**: EXP-012's §5.8.4 is a 3-point LinUCB-vs-Static
   robustness check; this is the dedicated 7-point learner-vs-best-constant sweep.
2. Method: vary `acceptance_slope`, re-anchor intercept so mean acceptance ≈ 0.5 at every slope
   (a sweep, not tuning). Note realistic LMIC demand is inelastic ≈ −0.2…−0.5; sim sits ≈ −1.1…−1.4.
3. Headline: no elasticity lets any learner beat the best constant (learner ~73–88 %; Table 24).
4. Sharp nuance: at the realistic *inelastic* end the best constant **is** the oracle (100 %, no
   contextual structure); at the *elastic* end structure emerges (best-constant-vs-oracle gap
   0 %→7.4 %) and LogisticOracle captures it (97–100 %) but the bandit still does not.
5. Verdict: with §5.11 + drift (§5.9.5) + HITL, no tested regime rescues the bandit.

**Table 24** (7 rows, from Task 0): elasticity (−0.24 … −1.32) × {best constant, LinUCB, LinTS,
LogisticOracle, Oracle, best constant ÷ oracle, learner > constant?}. Endpoints:
−0.24 → 365,385 = oracle (100 %, no); −1.32 → constant 311,532 / LinTS 273,091 / gap 7.4 % (no).

- [ ] **Step 2: Verify Table 24 against Task 0 CSV output.** Expected: exact match; "no" every row.

---

## Task 4: Draft §5.13 Horizon Check

**Files:** Modify `ch5-Results.tex` (append after §5.12).

- [ ] **Step 1: Append section + Table 25 from the Task-0 horizon run**

Section title: `\section{Horizon Check --- Is the Defeat Structural or Cold-Start Cost?}`
(auto-numbers 5.13).

Required prose beats (per spec §3.4):
1. The discriminating question: the 5,000-round main results charge full cold-start over a short
   horizon; at 20,000 rounds, does steady-state per-round reward reach the constant, and does
   cumulative ever cross AlwaysRATED?
2. Answer (Table 25): late-window bandit per-round reward stays BELOW the constant; cumulative
   NEVER crosses within 20,000 rounds ⇒ the defeat is **structural**, not finite-horizon.
3. Tie to §5.6: EXP-013 validates the √T rate at which LinUCB learns its *own* optimum; §5.13 shows
   that optimum is itself below the constant, so the regret tail vs the best simple policy is
   ultimately linear, not √T.
4. **Caption MUST state "5 seeds"** (long horizon) per the §5.0 "unless noted" convention.

**Table 25** (from `horizon_check.py` stdout): rows = Oracle, AlwaysRATED, LinUCB, LinTS; cols =
per-round reward in windows [0–1k, 4–5k, 9–10k, 19–20k]; plus a one-line steady-state verdict and
the final cumulative gap. Use the exact captured values.

- [ ] **Step 2: Verify Table 25 equals the captured stdout.** Expected: exact match.

---

## Task 5: Cross-reference resolution + structural balance + advisor

**Files:** read-only checks on `ch5-Results.tex`.

- [ ] **Step 1: Confirm every phantom ref now resolves**

Run: scan `5\.1[123]` refs (the Task-0-era scanner) AND list `\section` numbers.
Expected: §5.11/§5.12/§5.13 each now have a real `\section`; 0 dangling. Count unchanged at 22 refs.

- [ ] **Step 2: Brace / `\section` / environment balance**

Run a balance check (braces net 0; `\begin`/`\end` paired; every new `\captionof{table}` has a
matching `\label`; tables 22–25 present exactly once each).
Expected: balanced; 14 `\section` total; Tables 22,23,24,25 present.

- [ ] **Step 3: Advisor review of the drafted sections**

Call `advisor` before the build — verify honest framing (no overclaim), number fidelity, and that
§5.12 does not contradict §5.8.4. Address any findings.

---

## Task 6: Build r5

**Files:** Create `%TEMP%\zip_thesis_r5.py` (extends `%TEMP%\zip_thesis_r4.py`).

- [ ] **Step 1: Write zip_thesis_r5.py**

Copy `zip_thesis_r4.py`; change `zippath` to `Thesis_overleaf_2026-06-09_r5.zip`; KEEP all r4
checks (regression); ADD:
```python
("ch5 opens at section 5.0", r"\setcounter{section}{-1}" in c5),
("EXP-013 baked '5.6 ' removed", "5.6 EXP-013" not in c5),
("§5.11 section present", "Reward-Model Sensitivity" in c5),
("§5.12 section present", "Demand-Elasticity Sweep" in c5),
("§5.13 section present", "Horizon Check" in c5),
("Table 22 present", "Table 22" in c5),
("Table 23 present", "Table 23" in c5),
("Table 24 present", "Table 24" in c5),
("Table 25 present", "Table 25" in c5),
("14 sections in ch5", c5.count("\\section{") == 14),
# every 5.11/5.12/5.13 ref still has a home (no dangling): all three section titles exist (above)
```

- [ ] **Step 2: Run it**

Run: `python "%TEMP%\zip_thesis_r5.py"`
Expected: `ALL CHECKS PASS — r5 ready for Overleaf upload`, exit 0, ~50+ checks, all PASS.

---

## Task 7: Overleaf verification gate

**Files:** none (user action + log analysis).

- [ ] **Step 1: User uploads r5 → XeLaTeX → pastes the output zip/log.**

- [ ] **Step 2: Analyze the log** (reuse/extend `%TEMP%\analyze_r4_log.py`).

Expected: 0 TeX errors; PDF written (≥ 99 pp, likely a few more for the 3 sections); sections
render **5.0–5.13** (no "5.7 5.6" double); the 22 refs now point at real numbers; Tables 22–25
appear in the LoT; prior error classes (No counter / mathbb / longtable / tightlist / Missing $) all
0; `\setcounter{section}{-1}` did NOT leak into ch6/appendix (spot-check ch6 first section = 6.1).
**r5 is "done" only when this log is green.**

- [ ] **Step 3: Update memory** (`figure-overhaul-status` / `latex-migration-status` / `MEMORY.md`):
structural pass complete; LoF + figures + `.md` mirror remain deferred.

- [ ] **Step 4 (user-gated): commit.** Only if the user asks — propose a scoped commit then.

---

## Self-Review (against the spec)

- **Spec coverage:** numbering fix (Task 1) ✓; §5.11 (Task 2) ✓; §5.12 (Task 3) ✓; §5.13 (Task 4) ✓;
  cross-ref resolution (Task 5) ✓; verify-from-source (Task 0) ✓; r5 build + Overleaf gate
  (Tasks 6–7) ✓; deferred items untouched ✓.
- **Placeholder scan:** §5.13 numbers are produced by a defined run (Task 0 Step 3), not a TBD; all
  tables have a concrete source + anchor values. No "add error handling"-class vagueness (n/a).
- **Type/name consistency:** table numbers 22→23→24→25 consistent across Tasks 2–6; section titles
  identical in the draft tasks and the r5 asserts ("Reward-Model Sensitivity",
  "Demand-Elasticity Sweep", "Horizon Check"); `\setcounter{section}{-1}` string identical in
  Task 1 and Task 6 assert.
