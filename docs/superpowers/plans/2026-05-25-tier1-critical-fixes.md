# Tier-1 Critical Thesis Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the 7 critical findings (IMP-C1 through IMP-C7) from `docs/superpowers/audit/2026-05-25/05-improvements.md` so the thesis is submission-ready: consistent chapter structure, single statistical methodology, correct numerics across chapters, accurate citations, no internal contradictions.

**Architecture:** This is primarily a *thesis text editing* project, not a software change. The "tests" are content-verification commands (grep counts, build-renders, link checks) rather than pytest. Tasks are sequenced so structural changes (Task 1) land before content changes that reference structure (Tasks 2-6). Task 7 (Shadow Mode) is independent and can run in parallel with 4-6.

**Tech Stack:** Markdown editing; Python 3.11 (for verification scripts + docx build); python-docx (build_thesis_docx.py); git for atomic commits per fix.

**Inputs (read before starting):**
- `docs/superpowers/audit/2026-05-25/03-research-integrity.md` — full mismatch register
- `docs/superpowers/audit/2026-05-25/04-literature-validation.md` — per-citation findings
- `docs/superpowers/audit/2026-05-25/05-improvements.md` — Tier-1 list

**Estimated total effort:** 10-12 hours of focused editing.

---

## Pre-flight

### Task 0: Verify clean baseline

**Files:** None modified.

- [ ] **Step 0.1: Confirm git state is clean of in-progress edits relevant to this plan**

Run:
```bash
cd C:/DAC-UW-Thesis && git status --short | grep -E "thesis/health_rl/chapter|backend/|stress_testing/rl/experiments/exp_[0-9]+_.+\.py$"
```
Expected output: only the chapter files known to have uncommitted edits from prior work (`chapter1_introduction.md`, `chapter2_literature_review.md`, `chapter3_methodology.md`, `chapter4_results.md`, `chapter5_conclusion.md`). No `??` (untracked) chapter files should appear — those were removed in commit `30a4c21`.

If any unexpected modifications appear, stash or commit them before starting:
```bash
git stash push -m "pre-tier1-fixes-stash" -- <files>
```

- [ ] **Step 0.2: Read audit reports**

Read these three files in full before editing anything:
- `docs/superpowers/audit/2026-05-25/03-research-integrity.md`
- `docs/superpowers/audit/2026-05-25/04-literature-validation.md`
- `docs/superpowers/audit/2026-05-25/05-improvements.md`

- [ ] **Step 0.3: Snapshot the canonical numbers**

Save this reference card to scratchpad. **All chapters V & VI must use these exact numbers** (from `exp_005`/`007`/`008` 20-seed runs, per `chapter4_results.md`):

| Quantity | Value |
|---|---|
| Methodology | 20 independent seeds (1–20), bootstrap 95 % CI, paired Wilcoxon |
| LinUCB cumulative reward | $90,540 ± 5,382 [88,287, 92,886] |
| LinUCB late regret (last 500) | $2.20 ± 2.77/round |
| LinUCB reward lift over Static XGB | +18,248 (+25.2 %), p < 0.001, Cohen's d = 2.98 |
| LinTS cumulative reward | $93,572 ± 6,229 [90,980, 96,312] |
| LinTS cumulative regret | $21,149 ± 6,458 [18,285, 23,873] |
| LinUCB cumulative regret | $22,774 ± 6,627 [19,865, 25,559] |
| LinTS vs LinUCB (regret diff) | +1,626, p = 0.87, d = 0.26 (NOT significant) |
| Epsilon-Greedy regret | $38,281 ± 6,320 |
| Static XGB regret | $42,548 ± 4,970 |
| Region PSI (max 500-round sliding window) | 0.0821 ± 0.0213 |
| Occupation PSI (max 500-round sliding window) | 0.1225 ± 0.0793 |
| Region approval parity (min/max) | 85.72 % (PASS) |
| Occupation approval parity (min/max) | 90.12 % (PASS) |
| HITL c=0.7 cumulative reward | $102,100 (+6.5 % over math-REFER) |
| HITL human review rate | 75 / 5,000 = 1.5 % |
| Feature dimension (bandit) | d = 34 |
| Feature dimension (static XGB) | 21 |
| Epsilon (ε-greedy) | 0.15 |
| Hyperparameters | α = 1.0 (LinUCB), v² = 1.0 (LinTS), ε = 0.15 |

Any number not on this list (e.g., `$95,872`, `$101,266`, `27.7 %`, `34.8 %`, `d = 25`, `ε = 0.10`, region PSI `0.0050`) belongs to the obsolete single-seed=42 methodology and must be replaced or removed.

---

## Task 1 — IMP-C1: Reconcile chapter numbering and remove duplicates

**Goal:** Eliminate the 9-files-for-6-chapters confusion. Establish one canonical file per ITC chapter.

**Files:**
- Read: all of `thesis/health_rl/chapter*.md`
- Modify: `thesis/health_rl/chapter1_introduction.md` (strip Ch II content)
- Modify: `thesis/health_rl/chapter2_literature_review.md` (remove disclaimer note, fix Ch III heading)
- Move/decide: `thesis/health_rl/chapter3_methodology.md` (see Step 1.2)
- Rename: 3 chapter files to match their content's declared chapter number
- Modify: `thesis/health_rl/build_thesis_docx.py` (update glob/order to match renames)

### Decision required at Step 1.2: Methodology chapter placement

The 6-chapter ITC structure does not contain a "Methodology" slot. Two options:

- **Option A (Recommended): Fold `chapter3_methodology.md` content into Chapter IV (`chapter4_project_analysis.md`)** as new sections 4.5 "Dataset and Feature Engineering", 4.6 "Bandit Algorithms", 4.7 "Reward Design", 4.8 "PSI Guardrails", 4.9 "Experimental Design". Then delete `chapter3_methodology.md`. Preserves ITC 6-chapter structure. Result: 6 canonical chapter files.

- **Option B: Promote Methodology to its own chapter, breaking the 6-chapter pattern.** Rename `chapter3_methodology.md` to `chapter4_methodology.md` and re-heading "CHAPTER IV. METHODOLOGY". Push `chapter4_project_analysis.md` to V, `chapter4_results.md` to VI, `chapter5_conclusion.md` to VII. Result: 7 chapters.

**This plan executes Option A.** If Option B is preferred, stop and reissue the plan with a one-task amendment.

- [ ] **Step 1.1: Verify which chapter content is currently where**

Run:
```bash
cd C:/DAC-UW-Thesis && grep -nE "^# (CHAPTER |[IVX]+\. )" thesis/health_rl/chapter*.md
```

Expected output (confirms the audit finding):
```
chapter1_introduction.md:1:# I. INTRODUCTION
chapter1_introduction.md:51:# II. PRESENTATION OF THE PROJECT
chapter2_literature_review.md:1:# II. PRESENTATION OF THE PROJECT
chapter2_literature_review.md:7:# III. LITERATURE REVIEW
chapter2_presentation_of_project.md:1:# CHAPTER II. PRESENTATION OF THE PROJECT
chapter3_methodology.md:1:# CHAPTER III. METHODOLOGY
chapter4_project_analysis.md:1:# CHAPTER IV. PROJECT ANALYSIS AND CONCEPTS
chapter4_results.md:1:# CHAPTER V. RESULTS AND DISCUSSION
chapter5_conclusion.md:1:# CHAPTER VI. CONCLUSION
```

- [ ] **Step 1.2: Strip duplicate Chapter II content from `chapter1_introduction.md`**

`chapter1_introduction.md` currently contains both Ch I (lines 1–50) AND Ch II (lines 51–150). The Ch II content is duplicated by the dedicated `chapter2_presentation_of_project.md`. Decide which file owns Ch II; the audit recommends the dedicated `chapter2_presentation_of_project.md`.

Compare the two Ch II versions to ensure nothing unique is lost:
```bash
cd C:/DAC-UW-Thesis && diff <(sed -n '51,$p' thesis/health_rl/chapter1_introduction.md) thesis/health_rl/chapter2_presentation_of_project.md
```

If the diff shows content in `chapter1_introduction.md` that is NOT in `chapter2_presentation_of_project.md`, migrate the unique passages to `chapter2_presentation_of_project.md` first. Then edit `chapter1_introduction.md` to keep only lines 1–50 (Ch I content) plus the References section at the end (lines 154–166):

Use Edit tool to remove lines 51 through (References_section_start - 1). The exact line numbers will depend on the current state of the file; locate by searching for the literal string `# II. PRESENTATION OF THE PROJECT` and delete from that line through (but not including) `## REFERENCES`.

- [ ] **Step 1.3: Verify Step 1.2**

```bash
cd C:/DAC-UW-Thesis && grep -nE "^# " thesis/health_rl/chapter1_introduction.md
```

Expected: only `# I. INTRODUCTION` at line 1; no `# II.` heading anywhere.

- [ ] **Step 1.4: Remove the misleading disclaimer + Ch II heading from `chapter2_literature_review.md`**

The file currently starts with a Ch II header and a disclaimer note saying "I am actually Ch III". After renaming (Step 1.10) the disclaimer is unneeded. Edit the file: replace lines 1–9 (the `# II. PRESENTATION OF THE PROJECT`, the note paragraph, the `---`, and the `# III. LITERATURE REVIEW` line) with a single clean header:

Find:
```
# II. PRESENTATION OF THE PROJECT

*[Note: Per ITC thesis structure, Chapter II is reserved for "Presentation of the Project". The Literature Review content below has been re-numbered as Chapter III in accordance with ITC guidelines.]*

---

# III. LITERATURE REVIEW

---
```

Replace with:
```
# CHAPTER III. LITERATURE REVIEW

---
```

- [ ] **Step 1.5: Fold `chapter3_methodology.md` into Chapter IV (Option A)**

Read both files:
```bash
cd C:/DAC-UW-Thesis && wc -l thesis/health_rl/chapter3_methodology.md thesis/health_rl/chapter4_project_analysis.md
```

Open `chapter4_project_analysis.md`. After section 4.4 (the "Detail Concept — Contextual Bandits" section, ending at the `---` line before "*Word count*"), append the entire content of `chapter3_methodology.md` **except its top-level `# CHAPTER III. METHODOLOGY` heading line**. Renumber the appended sections from 3.1, 3.2, 3.3, 3.4, 3.5, 3.6 to 4.5, 4.6, 4.7, 4.8, 4.9, 4.10. Subsection numbering follows (e.g., `3.1.1` becomes `4.5.1`).

Use sed for the bulk renumber (PowerShell-safe alternative below):
```bash
# bash variant
cd C:/DAC-UW-Thesis/thesis/health_rl
sed -E 's/^(## )3\.([1-6])/\1 4.\2_TMP/g; s/^(### )3\.([1-6])\.([0-9]+)/\1 4.\2_TMP.\3/g' chapter3_methodology.md > /tmp/methodology_renumbered.md
# Then manually shift: 3.1→4.5, 3.2→4.6, ..., 3.6→4.10
```

Or, more reliably, do this with explicit Edit calls per section header. Map:
| Old | New |
|---|---|
| 3.1 → 4.5  | 3.1.1 → 4.5.1, 3.1.2 → 4.5.2, 3.1.3 → 4.5.3 |
| 3.2 → 4.6  | 3.2.1 → 4.6.1, ..., 3.2.4 → 4.6.4 |
| 3.3 → 4.7  | 3.3.1 → 4.7.1, 3.3.2 → 4.7.2, 3.3.3 → 4.7.3 |
| 3.4 → 4.8  | 3.4.1, 3.4.2, 3.4.3 → 4.8.1-3 |
| 3.5 → 4.9  | 3.5.1, 3.5.2, 3.5.3, 3.5.4 → 4.9.1-4 |
| 3.6 → 4.10 | 3.6.1-4 → 4.10.1-4 |

Update the chapter intro paragraph in `chapter4_project_analysis.md` to mention the new sections (4.5 dataset, 4.6 bandits, 4.7 reward, 4.8 PSI, 4.9 experiments, 4.10 deployment roadmap).

- [ ] **Step 1.6: Delete `chapter3_methodology.md`**

```bash
cd C:/DAC-UW-Thesis && git rm thesis/health_rl/chapter3_methodology.md
```

- [ ] **Step 1.7: Verify no chapter cross-references point to removed file**

```bash
cd C:/DAC-UW-Thesis && grep -rn "chapter3_methodology" thesis/ scripts/ docs/ --include="*.md" --include="*.py"
```

Expected: zero hits (or only hits in audit reports, which are historical and should not be edited).

If hits appear in `build_thesis_docx.py` or any active code, update them in this step.

- [ ] **Step 1.8: Verify in-chapter section references still resolve**

Some chapters cite specific sections (e.g., "see §3.4.1"). After renumber, these must point to the new section numbers.

```bash
cd C:/DAC-UW-Thesis && grep -nE "§|Section [0-9]+\.[0-9]+|see (Chapter |Ch\.? )?[0-9]+\.[0-9]" thesis/health_rl/chapter*.md
```

For each hit, check if the referenced section was renumbered (any 3.x reference to former Methodology should now be 4.(x+4)). Use Edit tool to update.

- [ ] **Step 1.9: Rename chapter files to match declared chapter numbers**

| Current name | Content's declared chapter | New name |
|---|---|---|
| chapter1_introduction.md | Ch I | (keep — already 1) |
| chapter2_presentation_of_project.md | Ch II | `chapter02_presentation.md` |
| chapter2_literature_review.md | Ch III | `chapter03_literature_review.md` |
| chapter4_project_analysis.md | Ch IV | `chapter04_project_analysis.md` |
| chapter4_results.md | Ch V | `chapter05_results.md` |
| chapter5_conclusion.md | Ch VI | `chapter06_conclusion.md` |

Rationale for the zero-padded `chapterNN_` prefix: alphabetical sort matches numerical order, so `ls` shows chapters in reading order. (Currently `chapter10_*` would sort between `chapter1_*` and `chapter2_*`.) Also rename `chapter1_introduction.md` to `chapter01_introduction.md` for consistency.

```bash
cd C:/DAC-UW-Thesis/thesis/health_rl
git mv chapter1_introduction.md chapter01_introduction.md
git mv chapter2_presentation_of_project.md chapter02_presentation.md
git mv chapter2_literature_review.md chapter03_literature_review.md
git mv chapter4_project_analysis.md chapter04_project_analysis.md
git mv chapter4_results.md chapter05_results.md
git mv chapter5_conclusion.md chapter06_conclusion.md
```

- [ ] **Step 1.10: Update `build_thesis_docx.py` chapter glob/order**

Open `thesis/health_rl/build_thesis_docx.py`. Find the section that enumerates chapter files (search for `chapter` or `glob`). Confirm the new filenames are picked up correctly. If the script uses a hardcoded list, update it.

Run:
```bash
cd C:/DAC-UW-Thesis && grep -nE "chapter[0-9_]+\.md|glob.*chapter" thesis/health_rl/build_thesis_docx.py scripts/thesis_*.py
```

Update any hardcoded references.

- [ ] **Step 1.11: Verify docx build still works**

```bash
cd C:/DAC-UW-Thesis && python thesis/health_rl/build_thesis_docx.py 2>&1 | tail -10
```

Expected: successful run with output `.docx` file created. Open the docx and visually confirm chapters appear in I → II → III → IV → V → VI order with no duplicate Ch II content.

- [ ] **Step 1.12: Commit IMP-C1**

```bash
cd C:/DAC-UW-Thesis && git add -A thesis/health_rl/ && git commit -m "fix(thesis): consolidate chapter structure (IMP-C1)

- strip duplicate Ch II content from chapter1_introduction.md
- fold methodology (former Ch III) into Ch IV §§ 4.5-4.10
- remove disclaimer + dual Ch headings from literature review file
- rename chapter files to zero-padded chapterNN_<slug>.md pattern
  matching declared chapter numbers
- update build_thesis_docx.py for new filenames
- delete superseded chapter3_methodology.md

Resolves audit finding RI-1 / IMP-C1."
```

---

## Task 2 — IMP-C3: Fix the d = 25 vs d = 34 contradiction

**Files:**
- Modify: `thesis/health_rl/chapter04_project_analysis.md` (formerly chapter4_project_analysis.md)
- Modify: `thesis/health_rl/chapter06_conclusion.md` (formerly chapter5_conclusion.md)

- [ ] **Step 2.1: Find every occurrence**

```bash
cd C:/DAC-UW-Thesis && grep -nE "d ?= ?25|25[- ]?dim|25 features|25-feature" thesis/health_rl/chapter*.md
```

Known hits (from audit):
- `chapter04_project_analysis.md` §4.4.2: "where d = 25 in this implementation"
- `chapter04_project_analysis.md` §4.4.4 item 6: "Linear bandits with d = 25 features achieve…"
- `chapter06_conclusion.md` §6.3.2 (former Future Work): "For a 25-feature dataset"
- Possibly `chapter06_conclusion.md` Limitation 4: "the 25-feature space used here"

- [ ] **Step 2.2: Replace each `25` with `34`**

Use Edit tool with `replace_all=False` so each change is targeted. For each hit, replace the surrounding clause:

Find: `d = 25 in this implementation` → Replace: `d = 34 in this implementation`

Find: `Linear bandits with d = 25 features` → Replace: `Linear bandits with d = 34 features`

Find: `For a 25-feature dataset` → Replace: `For a 34-feature dataset`

Find: `the 25-feature space used here` → Replace: `the 34-feature space used here`

- [ ] **Step 2.3: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -nE "d ?= ?25|25[- ]?dim|25 features|25-feature" thesis/health_rl/chapter*.md
```

Expected: zero hits.

Also verify the correct number is used:
```bash
cd C:/DAC-UW-Thesis && grep -cnE "d ?= ?34|34[- ]?dim|34 features|34-feature" thesis/health_rl/chapter*.md
```

Expected: ≥ 5 hits across chapters.

- [ ] **Step 2.4: Sanity-check against code**

```bash
cd C:/DAC-UW-Thesis && python -c "from stress_testing.rl.underwriting_bandit import preprocess_cambodia_data; X, _, features = preprocess_cambodia_data(); print(f'd = {X.shape[1]}'); assert X.shape[1] == 34, 'Feature count mismatch!'"
```

Expected output: `d = 34` and no AssertionError.

- [ ] **Step 2.5: Commit IMP-C3**

```bash
cd C:/DAC-UW-Thesis && git add thesis/health_rl/ && git commit -m "fix(thesis): correct feature dimensionality from d=25 to d=34 (IMP-C3)

Bandit context vector is 34-dim after one-hot encoding of region (8) and
occupation (7), verified by stress_testing/rl/underwriting_bandit.py
preprocess_cambodia_data(). Static XGB baseline uses 21 features
(label-encoded region+occupation), unchanged.

Resolves audit finding RI-3 / IMP-C3."
```

---

## Task 3 — IMP-C4: Fix the ε = 0.10 vs ε = 0.15 contradiction

**Files:**
- Modify: `thesis/health_rl/chapter05_results.md` (formerly chapter4_results.md), §5.3.2

- [ ] **Step 3.1: Find the wrong epsilon**

```bash
cd C:/DAC-UW-Thesis && grep -nE "varepsilon ?= ?0\.10|epsilon ?= ?0\.10|ε ?= ?0\.10|10 ?% of decisions" thesis/health_rl/chapter*.md
```

Known hit: `chapter05_results.md` §5.3.2 paragraph for "Epsilon-Greedy (rank 3)" contains "With \varepsilon = 0.10, the algorithm wastes 10% of decisions on uniform random exploration".

- [ ] **Step 3.2: Replace**

Find: `With \varepsilon = 0.10, the algorithm wastes 10% of decisions on uniform random exploration`

Replace: `With \varepsilon = 0.15, the algorithm wastes 15% of decisions on uniform random exploration`

- [ ] **Step 3.3: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -nE "varepsilon ?= ?0\.10|epsilon ?= ?0\.10|ε ?= ?0\.10|10 ?% of decisions on uniform" thesis/health_rl/chapter*.md
```

Expected: zero hits.

```bash
cd C:/DAC-UW-Thesis && grep -nE "varepsilon ?= ?0\.15|15 ?% of decisions" thesis/health_rl/chapter*.md
```

Expected: at least one hit (the replacement) plus the existing chapter3-now-§4.6.3 occurrence.

- [ ] **Step 3.4: Sanity-check against code**

```bash
cd C:/DAC-UW-Thesis && grep -nE "epsilon ?= ?0\.1[05]" stress_testing/rl/experiments/exp_007*.py
```

Expected: `EpsilonGreedy(..., epsilon=0.15, ...)`.

- [ ] **Step 3.5: Commit IMP-C4**

```bash
cd C:/DAC-UW-Thesis && git add thesis/health_rl/ && git commit -m "fix(thesis): correct epsilon from 0.10 to 0.15 in ch V §5.3.2 (IMP-C4)

EXP-007 instantiates EpsilonGreedy with epsilon=0.15 (exp_007_*.py:64),
matching methodology §4.6.3 (former §3.2.3) declaration. Ch V §5.3.2
previously said 0.10 in error.

Resolves audit finding RI-4 / IMP-C4."
```

---

## Task 4 — IMP-C2: Standardize on the 20-seed multi-run methodology

**Goal:** Every headline statistic in Chapters V and VI must come from the 20-seed methodology (with mean ± std and 95 % bootstrap CI). Single-seed=42 numbers are removed or relegated to a "Reproducibility note" sidebar.

This is the largest task. Estimated 4 hours.

**Files:**
- Modify: `thesis/health_rl/chapter05_results.md`
- Modify: `thesis/health_rl/chapter06_conclusion.md`

**Reference card:** see Step 0.3 above. Any number not on that list must be replaced.

- [ ] **Step 4.1: Inventory all numeric claims in chapters V and VI**

```bash
cd C:/DAC-UW-Thesis && grep -nE "\\\$[0-9]+,?[0-9]*" thesis/health_rl/chapter05_results.md thesis/health_rl/chapter06_conclusion.md
```

For each dollar value, classify as either:
- **Canonical** (matches the Step 0.3 reference card) → keep as-is
- **Obsolete single-seed** (matches the "obsolete" list in Step 0.3, e.g. `$95,872`, `$101,266`, `$75,067`, `$13,944`, `$19,289`, `$76,282`, `$38,888`, `$38,964`) → replace with the canonical 20-seed value
- **Derived stat** (e.g., `+25.2%` improvement; `+18,248` mean diff) → confirm it's derived from canonical, otherwise replace
- **Unknown** → flag, do not auto-edit

Save the inventory to a scratchpad table before editing.

- [ ] **Step 4.2: Locate the canonical 20-seed source**

`chapter05_results.md` (the canonical Ch V) already contains the 20-seed numbers in sections 5.1, 5.2, 5.3, 5.4. Use these as the source of truth. Cross-check against:

```bash
cd C:/DAC-UW-Thesis && grep -n "20 seeds" thesis/health_rl/chapter05_results.md | head -20
```

Confirm Tables 5.1.1, 5.2.1, 5.3.1, 5.4.1 are present and use the canonical numbers.

- [ ] **Step 4.3: Fix Ch VI Finding 4 — the mixed-methodology contradiction**

Open `chapter06_conclusion.md` (formerly `chapter5_conclusion.md`).

The audit identified (RI-2) that Finding 4 cites `$102,100 vs $95,872 mathematical-REFER baseline` — but `$95,872` is the single-seed=42 LinUCB cumulative reward, NOT the math-REFER baseline from EXP-008. EXP-008 uses its own baseline.

Inspect `chapter06_conclusion.md` Finding 4 carefully. Re-read `chapter05_results.md` §5.4 to find the correct 20-seed numbers for the HITL experiment, including the math-REFER baseline.

Then in `chapter06_conclusion.md`:

Find the entire "**Finding 4 — Human-in-the-loop underwriting improves reward at low cost (EXP-008).**" paragraph and rewrite using only canonical numbers from §5.4 (e.g., `$102,100 vs $95,872 mathematical-REFER baseline (+6.5%); review cost $2,625 (2.6% of reward); 75 of 5,000 rounds (1.5%) routed to human`).

- [ ] **Step 4.4: Scrub remaining single-seed numbers from `chapter06_conclusion.md`**

Search for the obsolete numbers explicitly:

```bash
cd C:/DAC-UW-Thesis && grep -nE "95,?872|101,?266|75,?067|13,?944|19,?289|76,?282|38,?888|38,?964|27\.7 ?%|34\.8 ?%|0\.005|0\.010|1\.320|1\.053" thesis/health_rl/chapter06_conclusion.md
```

For each hit, replace with the canonical 20-seed value or remove the surrounding clause if the claim no longer holds at 20-seed scale.

Specific known fixes for `chapter06_conclusion.md`:
- "27.7 % improvement" / "27.7%" → "25.2 %" or "+18,248 (+25.2 %)"
- "34.8 %" → "30.4 %" (LinTS lift over StaticXGB at 20 seeds, recompute from $93,572/$72,292)
- "$95,872" → "$90,540"
- "$101,266" → "$93,572"
- "$75,067" → "$72,292"
- "$13,944" → "$21,149"
- "$19,289" → "$22,774"
- region PSI "0.0050" / "0.005" → "0.082 max sliding-window" (and **disambiguate**: "max 500-round sliding-window PSI", not "final-state PSI")
- occupation PSI "0.0100" / "0.01" → "0.123 max sliding-window"

For PSI specifically: the audit (RI-5) notes that the 0.005 / 0.01 numbers are end-of-run final-state PSI (single seed), while the 0.082 / 0.123 numbers are max sliding-window across 20 seeds. **These are different metrics, not contradictions.** Decide which to report; recommend the more conservative max-sliding-window because that's what production monitoring would use. Always label clearly.

- [ ] **Step 4.5: Scrub remaining single-seed numbers from `chapter05_results.md`**

Even though §§5.1-5.4 use 20-seed numbers, the chapter intro paragraph and §5.5 "Implications" subsections may still reference single-seed lift percentages. Search:

```bash
cd C:/DAC-UW-Thesis && grep -nE "27\.7|34\.8|95,?872|101,?266|75,?067" thesis/health_rl/chapter05_results.md
```

Replace each with the canonical 20-seed values.

- [ ] **Step 4.6: Add a Reproducibility sidebar**

In `chapter05_results.md` after the chapter intro (before §5.1), add a short statistical-methodology block so readers understand the convention:

```markdown
## 5.0 Statistical Methodology and Reproducibility

All headline statistics in this chapter are computed across **20 independent seeds (1–20)** with the actuarial simulator run for **N = 5,000 rounds** per seed. Tables report **mean ± standard deviation** with **95 % bootstrap confidence intervals** in brackets. Pairwise comparisons between algorithms use the **paired Wilcoxon signed-rank test** with **Bonferroni correction** for multiple comparisons; effect sizes are reported as **Cohen's d**. The primary illustrative seed (used for trajectory figures) is SEED = 42; figures are produced from this seed unless noted.

A reviewer can reproduce any reported number by running `python stress_testing/rl/experiments/exp_005_underwriting_convergence.py` (or the corresponding `exp_006`, `exp_007`, `exp_008`) on Python 3.11 with the pinned dependencies in `requirements.txt`. Each script exits with code 0 if the pre-registered pass criteria are satisfied.
```

- [ ] **Step 4.7: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -cnE "\\\$95,?872|\\\$101,?266|\\\$75,?067|27\.7 ?%|34\.8 ?%" thesis/health_rl/chapter0[56]*.md
```

Expected: 0 (all obsolete single-seed numbers gone).

```bash
cd C:/DAC-UW-Thesis && grep -cnE "\\\$90,?540|\\\$93,?572|\\\$72,?292|25\.2 ?%|20 seeds|Bonferroni" thesis/health_rl/chapter0[56]*.md
```

Expected: each pattern hits ≥ 1 (canonical numbers present).

- [ ] **Step 4.8: Re-read Ch V and Ch VI end-to-end**

This is a content-review step. Read both chapters fresh. Look for:
- Any remaining "27.7 %" / "+25.2 %" inconsistency in adjacent sentences
- Any unlabeled PSI value (always say "max sliding-window" or "end-of-run")
- Any "single seed" / "SEED = 42" claim other than in the Reproducibility sidebar or figure captions
- Any "FAILED" assertion (the obsolete §5.1.3 in the old `chapter5_results.md` had a FAILED criterion 2; the 20-seed version in canonical §5.1.4 passes all five — verify this)

Fix any drift inline.

- [ ] **Step 4.9: Commit IMP-C2**

```bash
cd C:/DAC-UW-Thesis && git add thesis/health_rl/ && git commit -m "fix(thesis): standardize chs V & VI on 20-seed methodology (IMP-C2)

All headline statistics now use 20-seed mean ± std with 95% bootstrap CI
and paired Wilcoxon tests. Single-seed numbers removed; PSI metrics
disambiguated as max-500-round-sliding-window vs end-of-run. Added §5.0
Statistical Methodology sidebar. Fixed Ch VI Finding 4 which mixed
single-seed LinUCB reward with EXP-008 math-REFER baseline.

Resolves audit findings RI-2 and RI-5 / IMP-C2."
```

---

## Task 5 — IMP-C5: Resolve the Bastani et al. (2021) citation misapplication

**Goal:** The paper Bastani, H., Bayati, M., & Khosravi, K. (2021) is about **covariate-diversity-driven exploration-free greedy**, NOT "hidden-context discovery". The thesis cites it 3 times to support a claim it does not make.

**Files:**
- Modify: 3 occurrences across `chapter04_project_analysis.md` (formerly chapter3_methodology.md content, now folded as §4.9.1), `chapter05_results.md` (§5.1.3), and `chapter06_conclusion.md` if present
- Modify: `stress_testing/rl/experiments/exp_005_underwriting_convergence.py:183` (the comment cites Bastani too)

- [ ] **Step 5.1: Find all occurrences**

```bash
cd C:/DAC-UW-Thesis && grep -nE "Bastani" thesis/health_rl/ stress_testing/ -r
```

- [ ] **Step 5.2: Rewrite each citation to accurately describe Bastani et al. (2021)**

The correct one-sentence summary of the paper: *Bastani, Bayati & Khosravi (2021) prove that under sufficient covariate diversity in the context distribution, a purely greedy (no-exploration) policy can be rate-optimal for contextual bandits; their result helps explain why simple methods often suffice in practice when contexts are heterogeneous.*

For each occurrence, replace the misuse with one of two patterns:

**Pattern A** (when the surrounding text discusses why the bandit's policy diverges from the oracle): drop Bastani and instead acknowledge the observation as your own empirical finding. Example rewrite in `chapter05_results.md` §5.1.3:

Find:
```
This pattern is consistent with the hidden-context phenomenon described by Bastani et al. (2021): the linear reward model lacks features that the Oracle uses internally, so the bandit finds an alternative action mapping that is near-optimal under the available feature set without ever matching the Oracle's action choices case-by-case.
```

Replace with:
```
This pattern reflects a limited-feature regime: because the linear reward model in `expected_rewards()` uses the same 34-feature context that the bandit observes — while the Oracle has access to the per-sample stochastic noise realisation — the bandit cannot match the Oracle's action choices case-by-case. Instead it learns an alternative policy that is near-optimal *within the available feature subspace*. From an actuarial perspective, this is the deployment-relevant property: the bandit maximises observable reward given observable features.
```

**Pattern B** (when the surrounding text discusses why a simple method works): keep Bastani but use the correct framing. Example for §4.9.1 (former §3.5.1) pass criterion 4:

Find:
```
the bandit is expected to discover a *different* but profitable policy, not to converge to the oracle exactly; see Bastani et al., 2021
```

Replace with:
```
the bandit is expected to learn a profitable policy within its feature subspace rather than converge to the oracle exactly. Theoretical support for the broader claim that simple bandit methods can be rate-optimal under heterogeneous contexts is provided by Bastani, Bayati & Khosravi (2021), who prove that covariate diversity alone can make exploration-free greedy near-optimal.
```

- [ ] **Step 5.3: Update the source code comment**

`exp_005_underwriting_convergence.py:183` currently prints:
```python
print(f"       Interpretation: Bandit discovers a *different* but profitable policy,")
print(f"       not oracle convergence. See Bastani et al. (2021) on hidden-context discovery.")
```

Edit to:
```python
print(f"       Interpretation: Bandit learns a profitable policy within its")
print(f"       feature subspace; the Oracle has access to the per-sample noise")
print(f"       realisation that the bandit cannot observe. See Bastani et al. (2021)")
print(f"       for theory on rate-optimal greedy under covariate diversity.")
```

- [ ] **Step 5.4: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -nE "hidden[- ]context|hidden-context discovery" thesis/health_rl/ stress_testing/ -r
```

Expected: zero hits.

- [ ] **Step 5.5: Commit IMP-C5**

```bash
cd C:/DAC-UW-Thesis && git add thesis/health_rl/ stress_testing/rl/experiments/exp_005_underwriting_convergence.py && git commit -m "fix(thesis): rewrite Bastani 2021 citations with accurate framing (IMP-C5)

The cited paper proves covariate-diversity → rate-optimal greedy, NOT
'hidden-context discovery' as previously claimed. Three thesis citations
and one source-code comment rewritten to either drop the citation in
favour of an empirical observation about the limited-feature regime, or
keep it with an accurate one-sentence summary.

Resolves audit findings RI-6 / IMP-C5."
```

---

## Task 6 — IMP-C6: Add the two missing references to the bibliography

**Files:**
- Modify: `thesis/health_rl/chapter03_literature_review.md` (References section at end)

- [ ] **Step 6.1: Locate the References section**

```bash
cd C:/DAC-UW-Thesis && grep -n "^## REFERENCES" thesis/health_rl/chapter03_literature_review.md
```

- [ ] **Step 6.2: Verify the current alphabetical order**

The existing references are alphabetised by first author surname (Agrawal, Ban, Barocas, Ensign, Lattimore, Lewis, Li, Lin, NIS, Robbins, Russo, Siddiqi, Sutton, Thomas, Yurdakul, Zhang, Zhou). Insertions must maintain this order.

- [ ] **Step 6.3: Add Bastani entry (between Ban and Barocas)**

Insert this entry after the existing Ban (2022) entry and before the Barocas (2019) entry:

```
Bastani, H., Bayati, M., & Khosravi, K. (2021). Mostly exploration-free algorithms for contextual bandits. *Management Science*, *67*(3), 1329–1349. https://doi.org/10.1287/mnsc.2020.3605
```

- [ ] **Step 6.4: Add Shadish entry (between Russo and Siddiqi)**

If the thesis is using the four-threats framework (internal/external/construct/statistical-conclusion validity), the canonical citation is actually Shadish, Cook & **Campbell** (2002), not Shadish, Cook & Leviton (1991). The 1991 book surveys evaluation theorists; the 2002 book is the validity-threats canon.

Per the lit-validation report recommendation, **replace** the in-body citation in `chapter05_results.md` §5.5.4 with Shadish, Cook & Campbell (2002), and add THAT entry to the bibliography:

Find in `chapter05_results.md` §5.5.4:
```
Threats to validity are classified following the framework of Shadish, Cook, and Leviton (1991).
```

Replace:
```
Threats to validity are classified following the four-threats framework of Shadish, Cook, and Campbell (2002).
```

Then insert the bibliography entry between Russo and Siddiqi:

```
Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). *Experimental and quasi-experimental designs for generalized causal inference*. Houghton Mifflin.
```

(If the executor confirms by reading §5.5.4 that the *theory survey* of Shadish/Cook/Leviton 1991 was intended rather than the validity canon, use the 1991 entry instead — but the validity-threats wording in §5.5.4 strongly indicates the 2002 book.)

- [ ] **Step 6.5: Verify alphabetical order**

```bash
cd C:/DAC-UW-Thesis && grep -E "^[A-Z][a-z]" thesis/health_rl/chapter03_literature_review.md | sed -n '/^## REFERENCES/,$ p' | head -30
```

Read the output and confirm A → Z order is preserved across the two insertions.

- [ ] **Step 6.6: Commit IMP-C6**

```bash
cd C:/DAC-UW-Thesis && git add thesis/health_rl/ && git commit -m "fix(thesis): add Bastani 2021 and Shadish/Cook/Campbell 2002 to references (IMP-C6)

Both works were cited in chapter bodies but missing from the bibliography.
Also corrects the Shadish citation from Shadish/Cook/Leviton (1991) to
Shadish/Cook/Campbell (2002), which is the canonical reference for the
four-threats validity framework actually used in Ch V §5.5.4.

Resolves audit findings RI-7 / IMP-C6."
```

---

## Task 7 — IMP-C7: Resolve the Shadow Mode contradiction

**Decision required:** Chapter 3 (now Ch IV §4.10.1) describes Shadow Mode as a Phase-1 deployment with a real implementation. But `backend/` (which implements Shadow Mode) is marked deprecated in `.gitignore` line 73 ("Old backend API (superseded by demo/)"). Pick:

- **Option A: Revive `backend/`** — remove the gitignore line, confirm `tests/test_shadow_mode.py` still passes (note: it was deleted in commit `30a4c21` — recover from history), add a `backend/README.md` describing the relationship to `demo/`. **~2 hours.**
- **Option B (Recommended): Demote Shadow Mode to design-only** — `git rm -r backend/`, leave `tests/test_shadow_mode.py` deleted, rewrite §4.10.1 to frame Shadow Mode as a proposed future deployment phase rather than an implemented one. **~30 minutes.**

**This plan executes Option B.** If Option A is preferred, run the alternative steps in Step 7.0.

### Option B steps (Recommended):

- [ ] **Step 7.B.1: Confirm `demo/` is the live platform with no Shadow Mode dependency**

```bash
cd C:/DAC-UW-Thesis && grep -rn "from backend\|import backend" demo/ stress_testing/ scripts/ case-study/ 2>&1
```

Expected: zero hits (demo/ does not import backend/).

- [ ] **Step 7.B.2: Remove `backend/` from tracking**

```bash
cd C:/DAC-UW-Thesis && git rm -r backend/
```

- [ ] **Step 7.B.3: Remove the now-obsolete .gitignore line**

Open `.gitignore`. Find and delete the two lines:
```
# Old backend API (superseded by demo/)
backend/
```

- [ ] **Step 7.B.4: Rewrite §4.10.1 to frame Shadow Mode as design-only**

Open `chapter04_project_analysis.md`. Locate §4.10.1 (formerly §3.6.1 in `chapter3_methodology.md`, now folded into Ch IV per Task 1).

Find the existing §4.10.1 opening:
```
### 4.10.1 Phase 1 — Shadow Mode (Months 1–3)

In shadow mode, the contextual bandit runs alongside the existing static rule engine without making live decisions.
```

Replace with:
```
### 4.10.1 Phase 1 — Shadow Mode (Months 1–3, design proposal)

This subsection describes the recommended first phase of a production deployment. The architecture below is a *design proposal* validated against the bandit core implemented in `stress_testing/rl/underwriting_bandit.py`; the production wrapper (PAS API, persistent state layer, audit logging) has not been implemented as part of this thesis and is recommended future work (Ch VI §6.4).

In shadow mode, the contextual bandit runs alongside the existing static rule engine without making live decisions.
```

(Rest of §4.10.1 content remains.)

- [ ] **Step 7.B.5: Verify the rest of §4.10 still reads coherently**

Read §§4.10.1 through 4.10.4 end-to-end. Make sure no later paragraph claims the shadow-mode implementation exists. Particularly check §4.10.4 "Technical Infrastructure for Production" — its language should be consistently future-tense.

- [ ] **Step 7.B.6: Verify the docx build still works**

```bash
cd C:/DAC-UW-Thesis && python thesis/health_rl/build_thesis_docx.py 2>&1 | tail -5
```

Expected: successful run.

- [ ] **Step 7.B.7: Commit IMP-C7 (Option B)**

```bash
cd C:/DAC-UW-Thesis && git add -A && git commit -m "fix(thesis): demote Shadow Mode to design-only; remove deprecated backend/ (IMP-C7, Option B)

Resolves the contradiction between ch IV §4.10.1 (which described Shadow
Mode as live) and .gitignore line 73 (which marked backend/ as deprecated).
Decision: backend/ removed, §4.10.1 reframed as design proposal. The live
production platform is demo/ (per render.yaml), which does not implement
shadow-mode logging.

Resolves audit finding RI-8 / IMP-C7."
```

### Option A steps (Alternative — only if backend/ should be revived):

- [ ] **Step 7.A.1**: `git checkout 30a4c21~1 -- backend/ tests/test_shadow_mode.py` to restore.
- [ ] **Step 7.A.2**: Edit `.gitignore` to remove the `backend/` line and its comment.
- [ ] **Step 7.A.3**: Run `pytest tests/test_shadow_mode.py -v` to confirm tests pass. If they fail, fix root cause.
- [ ] **Step 7.A.4**: Create `backend/README.md` explaining that backend/ implements Shadow Mode logging as described in Ch IV §4.10.1, while demo/ is the live actuarial dashboard. Both are independent FastAPI apps.
- [ ] **Step 7.A.5**: Commit with message `feat: revive backend/ shadow-mode implementation to match thesis ch IV §4.10.1 (IMP-C7, Option A)`.

---

## Task 8 — Final verification

**Files:** none modified.

- [ ] **Step 8.1: Re-run all integrity-check greps**

```bash
cd C:/DAC-UW-Thesis && set -e && \
echo "--- d=25 should be 0 ---" && grep -cnE "d ?= ?25|25[- ]?dim|25 features|25-feature" thesis/health_rl/chapter*.md && \
echo "--- epsilon=0.10 should be 0 ---" && grep -cnE "varepsilon ?= ?0\.10|epsilon ?= ?0\.10|ε ?= ?0\.10|10 ?% of decisions on uniform" thesis/health_rl/chapter*.md && \
echo "--- obsolete single-seed numbers should be 0 ---" && grep -cnE "\\\$95,?872|\\\$101,?266|\\\$75,?067|27\.7 ?%|34\.8 ?%" thesis/health_rl/chapter*.md && \
echo "--- hidden-context citation should be 0 ---" && grep -cnE "hidden[- ]context" thesis/health_rl/ stress_testing/ -r && \
echo "--- Bastani in body but absent from refs should be 0 ---" && (! grep -L "Bastani.*2021.*Mostly exploration-free" thesis/health_rl/chapter03_literature_review.md) && \
echo "--- chapter3_methodology.md should not exist ---" && (! test -f thesis/health_rl/chapter3_methodology.md)
```

All `cnE` lines should show `0` for every chapter file (no hits). The two negation checks should succeed silently.

- [ ] **Step 8.2: Build the docx and inspect**

```bash
cd C:/DAC-UW-Thesis && python thesis/health_rl/build_thesis_docx.py 2>&1 | tail -10
```

Open the produced `thesis/health_rl/ITC_Thesis_Draft.docx` in Word. Visually verify:
- Chapters appear in order I → II → III → IV → V → VI
- No duplicate Ch II content
- All `[FIGURE: …]` placeholders resolve to embedded images (not broken links)
- References list contains both Bastani (2021) and Shadish/Cook/Campbell (2002)
- Ch V tables use ± and CI notation consistent with the Reproducibility sidebar

- [ ] **Step 8.3: Run the experiment scripts to confirm they still pass**

This is a regression check on the bandit core (in case any commits accidentally touched code):

```bash
cd C:/DAC-UW-Thesis && python stress_testing/rl/experiments/exp_005_underwriting_convergence.py 2>&1 | tail -3
```
Expected last line: `EXP-005: PASS`.

```bash
cd C:/DAC-UW-Thesis && python stress_testing/rl/experiments/exp_007_benchmark_comparison.py 2>&1 | tail -3
```
Expected last line: `EXP-007: PASS`.

(Each takes ~2-5 minutes per seed × 20 seeds — budget ~30 minutes for EXP-007.)

- [ ] **Step 8.4: Cross-check no audit-report findings remain open in Tier 1**

Open `docs/superpowers/audit/2026-05-25/03-research-integrity.md`. Review the "Summary table of integrity issues" at the bottom. For each row marked 🔴 (RI-1 through RI-7):
- Confirm the underlying issue has been fixed by this plan's commits
- If any remain (e.g., a 🔴 introduced by a partial fix), open a new follow-up plan or amend this plan and re-run

- [ ] **Step 8.5: Final commit and review log**

If any small consistency fixes turned up during Step 8.2 visual inspection:

```bash
cd C:/DAC-UW-Thesis && git add -A && git commit -m "fix(thesis): final consistency pass after Tier-1 critical fixes"
```

Then summarise:

```bash
cd C:/DAC-UW-Thesis && git log --oneline 30a4c21..HEAD
```

Expected: ≤ 8 commits, each tagged with the IMP-C* identifier it resolves.

---

---

## Task 9 — Structural rename: `case-study/` → `data/cambodia/`

**Goal:** Bring directory naming in line with the project's content (it's the primary Cambodia dataset, not a "case study"). Update all 17 Python files + 4 markdown files that reference the old path.

**Files:**
- Move: `case-study/` → `data/cambodia/` (everything inside preserved)
- Modify (Python, 17 files): `demo/main.py`, `demo/pricing_engine.py`, `thesis/health_rl/build_thesis_docx.py`, `thesis/health_rl/generate_eda_figures.py`, all 9 files under `stress_testing/rl/` (experiments + bandit), `case-study/generate_cambodia_dataset.py`, `case-study/train_cambodia_models.py`, `case-study/train_cambodia_rl.py`
- Modify (markdown): `thesis/health_rl/chapter01_introduction.md`, `thesis/health_rl/AGENT_BRIEF.md`, `thesis/health_rl/DEMO_DEFENSE_REDEMPTION_PLAN.md` (the `chapter3_methodology.md` reference was eliminated when that file was folded into Ch IV in Task 1)
- Modify: `CLAUDE.md` (project instructions reference `case-study/`)
- Modify: `.gitignore` (line 59: `case-study/phnom_penh_pings.csv` — though this file no longer exists, the path pattern matters)

- [ ] **Step 9.1: Inventory all references**

```bash
cd C:/DAC-UW-Thesis && grep -rnE "case[-_]study" --include="*.py" --include="*.md" --include="*.yaml" --include=".gitignore" 2>&1 | tee /tmp/case-study-refs.txt | wc -l
```

Save the output. Expect ~30-50 hits.

- [ ] **Step 9.2: Move the directory**

```bash
cd C:/DAC-UW-Thesis && mkdir -p data && git mv case-study data/cambodia
```

- [ ] **Step 9.3: Mass-update Python imports and path constants**

Two patterns to replace:

Pattern A (string literals containing the path):
- `"case-study/...` → `"data/cambodia/...`
- `'case-study/...` → `'data/cambodia/...`
- `case-study\\` → `data/cambodia\\` (Windows paths if any)
- `case-study/models` → `data/cambodia/models`

Pattern B (Path objects with `case-study` segment):
- `ROOT / "case-study"` → `ROOT / "data" / "cambodia"`
- `Path("case-study")` → `Path("data/cambodia")`

For each file in the inventory:
```bash
# Use Edit tool per file with replace_all=True for unambiguous string matches.
# Key files to check first:
#   stress_testing/rl/underwriting_bandit.py:28  DATA_PATH = ROOT / "case-study" / "cambodia_dataset.csv"
#   stress_testing/rl/underwriting_bandit.py:29  MODELS_DIR = ROOT / "case-study" / "models"
#   demo/main.py, demo/pricing_engine.py, thesis/health_rl/build_thesis_docx.py
```

- [ ] **Step 9.4: Update markdown references**

In `chapter01_introduction.md`, `AGENT_BRIEF.md`, `DEMO_DEFENSE_REDEMPTION_PLAN.md`, and `CLAUDE.md`: search for `case-study` and replace with `data/cambodia` (or `data/cambodia/` for directory references).

- [ ] **Step 9.5: Update `.gitignore`**

Open `.gitignore`. Find line 59 `case-study/phnom_penh_pings.csv` and change to `data/cambodia/phnom_penh_pings.csv` (preserves the historical ignore even if the file no longer exists).

- [ ] **Step 9.6: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -rnE "case[-_]study" --include="*.py" --include="*.md" --include="*.yaml" --include=".gitignore" 2>&1 | grep -v "docs/superpowers/audit/" | grep -v "docs/superpowers/plans/" | grep -v "docs/superpowers/specs/"
```

Expected: zero hits (excluding the historical audit/plan/spec docs which legitimately reference the old name).

- [ ] **Step 9.7: Smoke-test code paths**

```bash
cd C:/DAC-UW-Thesis && python -c "from stress_testing.rl.underwriting_bandit import preprocess_cambodia_data; X, df, _ = preprocess_cambodia_data(); print(f'Loaded {len(df)} rows, d={X.shape[1]}')"
```

Expected: `Loaded 2000 rows, d=34`.

- [ ] **Step 9.8: Commit IMP-S1**

```bash
cd C:/DAC-UW-Thesis && git add -A && git commit -m "refactor: rename case-study/ to data/cambodia/ (IMP-S1)

The 2000-record Cambodia dataset is the primary corpus, not a 'case study'.
New layout: data/cambodia/{cambodia_dataset.csv, generate_cambodia_dataset.py,
train_cambodia_*.py, models/*.pkl}. Updated all 17 Python files and 4 markdown
files that referenced the old path. .gitignore updated for the new location.

Per docs/superpowers/audit/2026-05-25/02-structure-overview.md."
```

---

## Task 10 — Structural rename: `stress_testing/rl/` → `healthrl/`

**Goal:** Replace the holdover name from the predecessor (auto-insurance / PSI) thesis with a name that reflects the current thesis content. `healthrl/` is concise, accurate, and importable as a Python package.

**Files:**
- Move: `stress_testing/rl/` → `healthrl/`
- Delete: `stress_testing/` (now empty)
- Modify: all files that have `from stress_testing.rl…` or `import stress_testing.rl…` (≈12 files: demo/, thesis builders, the 9 experiment scripts internally if any cross-reference)
- Modify: `CLAUDE.md`, audit reports referenced by future docs

- [ ] **Step 10.1: Inventory all references**

```bash
cd C:/DAC-UW-Thesis && grep -rnE "stress_testing" --include="*.py" --include="*.md" --include="*.yaml" 2>&1 | tee /tmp/stress-refs.txt | wc -l
```

- [ ] **Step 10.2: Move the directory**

```bash
cd C:/DAC-UW-Thesis && git mv stress_testing/rl healthrl && rmdir stress_testing 2>&1 || rm -rf stress_testing
```

- [ ] **Step 10.3: Mass-update Python imports**

Patterns:
- `from stress_testing.rl.` → `from healthrl.`
- `from stress_testing.rl ` → `from healthrl `
- `import stress_testing.rl` → `import healthrl`
- `from stress_testing.rl.underwriting_bandit import` → `from healthrl.underwriting_bandit import`

For each file. Use `Grep` to find, `Edit` per file with `replace_all=True`.

Key files: `demo/main.py:31`, `demo/pricing_engine.py:19`, `thesis/health_rl/build_thesis_docx.py` (if applicable), each `healthrl/experiments/exp_*.py` (they internally `from stress_testing.rl.underwriting_bandit import …` — fix all 9).

- [ ] **Step 10.4: Update path-string references in docs**

In `CLAUDE.md`, `thesis/health_rl/AGENT_BRIEF.md`, `chapter01_introduction.md` (if applicable): search for `stress_testing` and replace with `healthrl`. For chapter texts mentioning experiment paths (e.g., `stress_testing/rl/experiments/`), update to `healthrl/experiments/`.

- [ ] **Step 10.5: Update sys.path injections**

Several experiment scripts have:
```python
ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
```

After the move, the `parent.parent.parent.parent` depth may change (was `experiments/ → rl/ → stress_testing/ → repo_root`, now `experiments/ → healthrl/ → repo_root`). Count carefully:
- Old: `exp_*.py` at depth 4 → 4 parents to reach ROOT
- New: `exp_*.py` at depth 3 → 3 parents to reach ROOT

Update each `exp_*.py` to use `parent.parent.parent` (3 levels).

- [ ] **Step 10.6: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -rnE "stress_testing" --include="*.py" --include="*.md" --include="*.yaml" 2>&1 | grep -v "docs/superpowers/audit/" | grep -v "docs/superpowers/plans/" | grep -v "docs/superpowers/specs/"
```

Expected: zero hits.

- [ ] **Step 10.7: Smoke-test the package**

```bash
cd C:/DAC-UW-Thesis && python -c "from healthrl.underwriting_bandit import LinUCB, LinTS, EpsilonGreedy, StaticXGBBaseline, OraclePolicy, preprocess_cambodia_data, RewardConfig; print('All imports OK')"
```

Expected: `All imports OK`.

```bash
cd C:/DAC-UW-Thesis && python healthrl/experiments/exp_005_underwriting_convergence.py 2>&1 | tail -3
```

Expected: `EXP-005: PASS` (last line). May take ~5 minutes.

- [ ] **Step 10.8: Commit IMP-S2**

```bash
cd C:/DAC-UW-Thesis && git add -A && git commit -m "refactor: rename stress_testing/rl/ to healthrl/ (IMP-S2)

'stress_testing' was a holdover from the predecessor PSI/telematics thesis;
this thesis is health-RL. Renamed top-level package, updated all imports
in demo/, healthrl/experiments/, thesis builders. Adjusted sys.path depth
in experiment scripts (now 3 parents to ROOT, was 4).

Per docs/superpowers/audit/2026-05-25/02-structure-overview.md."
```

---

## Task 11 — Centralize hyperparameters: create `healthrl/config.py`

**Goal:** Eliminate hyperparameter drift (the kind of drift that produced the IMP-C4 ε=0.10 vs 0.15 bug). Constants currently duplicated across 9 experiment files become a single import.

**Files:**
- Create: `healthrl/config.py`
- Modify: all 9 files in `healthrl/experiments/exp_*.py`

- [ ] **Step 11.1: Create `healthrl/config.py`**

Write this exact content to `healthrl/config.py`:

```python
"""Central configuration for healthrl experiments.

All experiment-wide constants live here so that:
1. Methodology changes (e.g., N_ROUNDS, n_seeds) require editing one file.
2. Cross-chapter consistency is mechanical: chapters quote these constants
   by name and the actual numbers stay synchronized with code.

Add new constants here rather than introducing module-level constants in
individual exp_*.py scripts.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    """Common settings for every multi-seed experiment."""
    n_rounds: int = 5000
    n_seeds: int = 20
    primary_seed: int = 42
    psi_window: int = 500
    drift_shock_round: int = 2500


@dataclass(frozen=True)
class BanditConfig:
    """Default bandit hyperparameters.

    These match the methodology declarations in thesis Ch IV §§4.6.1-4.6.3.
    Override per-experiment if the experiment is intentionally exploring
    a different setting (e.g., exp_012 sensitivity sweep over alpha).
    """
    linucb_alpha: float = 1.0
    lints_v2: float = 1.0
    epsilon: float = 0.15


EXPERIMENT = ExperimentConfig()
BANDIT = BanditConfig()
```

- [ ] **Step 11.2: Update each `exp_*.py` to import and use the config**

For each of `exp_005`, `exp_006`, `exp_007`, `exp_008`, `exp_009`, `exp_010`, `exp_011`, `exp_012`, `exp_013`:

1. Add import after the existing healthrl imports:
   ```python
   from healthrl.config import EXPERIMENT, BANDIT
   ```

2. Replace `N_ROUNDS = 5000` with `N_ROUNDS = EXPERIMENT.n_rounds`.

3. Replace `n_seeds=20` (or `n_seeds=10` in exp_010 — see note below) in the `run_experiment_seeds_*` call sites with `n_seeds=EXPERIMENT.n_seeds`. Exception: exp_010 currently uses 10; if you want to keep the deliberate divergence, leave `n_seeds=10` as a literal with a comment `# n_seeds=10 by design — cold-start sweep is expensive` (this also addresses IMP-I2 from the improvements report).

4. Replace bandit hyperparameter literals in instantiation calls:
   - `LinUCB(..., alpha=1.0)` → `LinUCB(..., alpha=BANDIT.linucb_alpha)`
   - `LinTS(..., v2=1.0, ...)` → `LinTS(..., v2=BANDIT.lints_v2, ...)`
   - `EpsilonGreedy(..., epsilon=0.15, ...)` → `EpsilonGreedy(..., epsilon=BANDIT.epsilon, ...)`

   EXCEPTION: in `exp_012_sensitivity_analysis.py`, the alpha values are swept intentionally — leave those literals alone but add the import for use elsewhere if any.

   EXCEPTION: in `exp_011_ablation_study.py:84`, `alpha=0.0` is the greedy-only ablation — leave that literal alone.

5. Replace `WINDOW = 500` in exp_006 with `WINDOW = EXPERIMENT.psi_window`.

6. Replace `SHOCK_ROUND = 2500` in exp_009 with `SHOCK_ROUND = EXPERIMENT.drift_shock_round`.

- [ ] **Step 11.3: Verify**

```bash
cd C:/DAC-UW-Thesis && grep -nE "^N_ROUNDS ?= ?5000|^WINDOW ?= ?500|^SHOCK_ROUND ?= ?2500" healthrl/experiments/exp_*.py
```

Expected: zero hits (all replaced by `EXPERIMENT.*`).

```bash
cd C:/DAC-UW-Thesis && grep -nE "epsilon ?= ?0\.15" healthrl/experiments/exp_*.py
```

Expected: zero hits (replaced by `BANDIT.epsilon`).

```bash
cd C:/DAC-UW-Thesis && python -c "from healthrl.config import EXPERIMENT, BANDIT; assert EXPERIMENT.n_rounds == 5000; assert BANDIT.epsilon == 0.15; print('Config OK')"
```

Expected: `Config OK`.

- [ ] **Step 11.4: Re-run EXP-005 to confirm no behavior change**

```bash
cd C:/DAC-UW-Thesis && python healthrl/experiments/exp_005_underwriting_convergence.py 2>&1 | tail -3
```

Expected: `EXP-005: PASS` with identical numbers to before (refactor must be behavior-preserving).

- [ ] **Step 11.5: Commit IMP-S3**

```bash
cd C:/DAC-UW-Thesis && git add -A && git commit -m "refactor: centralize hyperparameters in healthrl/config.py (IMP-S3)

EXPERIMENT (n_rounds, n_seeds, primary_seed, psi_window, drift_shock_round)
and BANDIT (linucb_alpha, lints_v2, epsilon) are now defined once and
imported by all exp_*.py scripts. Prevents the kind of drift that produced
the chapter ε=0.10 vs code ε=0.15 contradiction (IMP-C4). Eliminates 9
duplicated constant definitions.

Sweep-based experiments (exp_011 greedy ablation, exp_012 alpha sensitivity)
retain literal hyperparameter values where the sweep is the point. exp_010
keeps n_seeds=10 with a comment justifying the divergence.

Per docs/superpowers/audit/2026-05-25/02-structure-overview.md."
```

---

## Task 12 — Update top-level docs to reflect new structure

**Files:**
- Modify: `CLAUDE.md` (project root)
- Create: `README.md` (project root)

- [ ] **Step 12.1: Update `CLAUDE.md`**

Open `CLAUDE.md`. Find the "Repo Structure" section. Replace the directory tree with the new layout:

Find (or similar):
```
C:\DAC-UW-Thesis\
  thesis/
    archive-life-insurance-2026-04-19/
    ...
  stress_testing/
    auto_insurance/
    experiments/
  case-study/
    phnom_penh_pings.csv
    ...
```

Replace with the actual current tree:
```
C:\DAC-UW-Thesis\
  CLAUDE.md
  README.md
  requirements.txt
  render.yaml
  healthrl/                       # core bandit package (LinUCB, LinTS, ε-Greedy, StaticXGB, Oracle)
    underwriting_bandit.py
    config.py                     # central hyperparameters (EXPERIMENT, BANDIT)
    experiments/
      exp_005_underwriting_convergence.py
      exp_006_fairness_audit.py
      exp_007_benchmark_comparison.py
      exp_008_human_in_the_loop.py
      exp_009_drift_adaptation.py
      exp_010_cold_start_analysis.py
      exp_011_ablation_study.py
      exp_012_sensitivity_analysis.py
      exp_013_loglog_regret_validation.py
      experiment_utils.py
      statistical_utils.py
  data/
    cambodia/
      cambodia_dataset.csv
      cambodia_dataset.parquet
      generate_cambodia_dataset.py
      train_cambodia_models.py
      train_cambodia_rl.py
      models/                    # GLM + XGBoost + bandit pickles
  demo/                          # Render-deployed FastAPI dashboard
  scripts/                       # thesis_loop / scorer / rewriter
  tests/
  thesis/
    health_rl/
      chapter01_introduction.md
      chapter02_presentation.md
      chapter03_literature_review.md
      chapter04_project_analysis.md   # includes methodology §§4.5-4.10
      chapter05_results.md
      chapter06_conclusion.md
      figures/                   # chapter figures + math_cache
      build_thesis_docx.py
      build_presentation.py
  wiki/                          # writing templates + topic guides
  docs/superpowers/              # specs, plans, audits
```

Also update the section "What this repo is" and any text mentioning `auto insurance / PSI` — the thesis topic is RL health insurance.

Also remove the "Vietnam case study" mention if present; that was for the old project.

- [ ] **Step 12.2: Create `README.md`**

Write to `README.md`:

```markdown
# DAC-UW-Thesis — Adaptive Health Insurance Underwriting via Contextual Bandits

Master's thesis at ITC (Institut de Technologie du Cambodge): a contextual bandit framework for health insurance underwriting in Cambodia, with PSI-based fairness guardrails and a human-in-the-loop extension.

## Quick start

```bash
# Install
pip install -r requirements.txt

# Regenerate the synthetic dataset (deterministic, SEED=42)
python data/cambodia/generate_cambodia_dataset.py

# Train baseline models (XGBoost + GLM)
python data/cambodia/train_cambodia_models.py

# Run the headline experiment (LinUCB convergence vs Static XGB, 20 seeds)
python healthrl/experiments/exp_005_underwriting_convergence.py

# Launch the live demo dashboard locally
uvicorn demo.main:app --reload --port 8000
```

## Repository layout

| Path | Purpose |
|---|---|
| `healthrl/` | Core bandit package: LinUCB, LinTS, ε-Greedy, StaticXGB, Oracle, reward simulator, preprocessor |
| `healthrl/config.py` | Central hyperparameters (`EXPERIMENT`, `BANDIT`) — change in one place |
| `healthrl/experiments/` | 9 experiments (EXP-005 to EXP-013) with pre-registered pass criteria + exit codes |
| `data/cambodia/` | Synthetic CDHS-anchored applicant dataset (2,000 records) + trained baseline models |
| `demo/` | FastAPI actuarial dashboard (Render-deployed) |
| `thesis/health_rl/` | Chapter sources + figures + docx/pptx builders |
| `docs/superpowers/` | Specs, plans, audits |

## Reproducibility

All experiments use fixed seeds, multi-seed analysis (20 seeds for headline statistics, 10 for the cold-start sweep in EXP-010), bootstrap 95 % confidence intervals, and paired Wilcoxon tests with Bonferroni correction. Each `exp_*.py` exits 0 on PASS, 1 on FAIL, suitable for CI.

Primary seed: 42. Multi-seed range: 1–20.

## Thesis structure

| Chapter | File |
|---|---|
| I. Introduction | `thesis/health_rl/chapter01_introduction.md` |
| II. Presentation of the Project | `thesis/health_rl/chapter02_presentation.md` |
| III. Literature Review | `thesis/health_rl/chapter03_literature_review.md` |
| IV. Project Analysis (includes methodology §§4.5-4.10) | `thesis/health_rl/chapter04_project_analysis.md` |
| V. Results and Discussion | `thesis/health_rl/chapter05_results.md` |
| VI. Conclusion | `thesis/health_rl/chapter06_conclusion.md` |

## License

[TBD by candidate]
```

- [ ] **Step 12.3: Verify**

```bash
cd C:/DAC-UW-Thesis && test -f README.md && grep -q "healthrl/" README.md && grep -q "data/cambodia/" README.md && echo "README OK"
cd C:/DAC-UW-Thesis && grep -q "healthrl/" CLAUDE.md && grep -q "data/cambodia/" CLAUDE.md && echo "CLAUDE.md OK"
```

- [ ] **Step 12.4: Commit IMP-S4**

```bash
cd C:/DAC-UW-Thesis && git add CLAUDE.md README.md && git commit -m "docs: update CLAUDE.md and add README.md for new structure (IMP-S4)

Reflects: healthrl/ package, data/cambodia/ dataset path, chapter01_..06_
naming, and consolidated 6-chapter structure with methodology folded into
Ch IV. README gives the 60-second orientation for new readers.

Per docs/superpowers/audit/2026-05-25/02-structure-overview.md."
```

---

## Out of scope for this plan (deferred to follow-up)

The following items from `05-improvements.md` are explicitly **not** addressed here:
- IMP-I1: writing up EXP-009/010/011/012/013 results into Ch V
- IMP-I7: bandit-core unit tests
- Extracting reward/preprocessor modules from `underwriting_bandit.py`
- Renaming `wiki/` → `docs/templates/` (pure cosmetic; defer)
- Three-into-one consolidation of presentation builders
- All Tier-3 publication-quality improvements (NeuralLinear baseline, heavy-tailed claims, pre-registration)

When this combined plan is complete, the thesis is **submission-ready** and the repo structure is **research-publication-presentable**. Tier-2 content work (especially IMP-I1) raises the work toward publication-ready.
