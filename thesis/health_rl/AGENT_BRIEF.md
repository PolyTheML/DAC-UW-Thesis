# AI Agent Brief — Thesis Update & Demo Furnishing

> **Project**: Adaptive Health Insurance Underwriting via Contextual Bandits (Bachelor's Thesis, ITC Cambodia)
> **Author**: Chanpoly
> **Defense target**: ~2026-06-26
> **Repository root**: `C:\DAC-UW-Thesis`

---

## 1. THESIS REPORT — CURRENT STATE

### Chapters built into the DOCX
The DOCX builder (`thesis/health_rl/build_thesis_docx.py`) reads these files in order:

| File | Chapter | Words | Status |
|------|---------|-------|--------|
| `chapter1_introduction.md` | I. INTRODUCTION | ~1,900 | ✅ Complete draft |
| `chapter2_literature_review.md` | II. LITERATURE REVIEW | ~3,000 | ✅ Complete draft |
| `chapter3_methodology.md` | III. METHODOLOGY | ~4,400 | ✅ Complete draft |
| `chapter4_project_analysis.md` | IV. PROJECT ANALYSIS | ~1,500 | ✅ Complete draft |
| `chapter4_results.md` | V. RESULTS & DISCUSSION | ~3,600 | ✅ Complete draft |
| `chapter5_conclusion.md` | VI. CONCLUSION | ~1,600 | ✅ Complete draft |

**Total body text**: ~14,500 words.

### Known critical issues

#### Issue A: Conflicting results numbers across files
There are **three different sets of EXP-005 numbers** in the repo. You must reconcile them to one consistent set and update all downstream references.

| Source | LinUCB Reward | Static XGB Reward | Delta |
|--------|---------------|-------------------|-------|
| `chapter4_results.md` (used in DOCX) | $58,642 | $35,032 | +67% |
| `chapter5_results.md` (NOT in DOCX) | $95,872 | $75,067 | +27.7% |
| `AGENTS.md` quick reference | $99,706 | $72,540 | +37% |
| `build_presentation.py` (hardcoded) | $58,642 | $35,032 | +67% |
| **Actual experiment run (2026-05-21)** | ~$99,700 | ~$72,500 | +37% |

**Decision needed**: The hardcoded presentation figures and `chapter4_results.md` currently agree with each other but **disagree with the actual experiments**. The actual experiments (running `exp_005_underwriting_convergence.py`) produce ~$99,700 / ~$72,500.

**Recommended fix**:
1. Run EXP-005, EXP-006, EXP-007, EXP-008 on seed=42 with default `RewardConfig()`.
2. Update `chapter4_results.md` tables and prose to match the actual output.
3. Update `build_presentation.py` hardcoded scaling factors to match.
4. Regenerate all 6 core figures (`fig_reward_curves.png`, `fig_regret_curves.png`, etc.).
5. Delete `chapter5_results.md` and `chapter5_conclusion.md` duplicates to avoid confusion (the build uses `chapter4_results.md` and `chapter5_conclusion.md`).

#### Issue B: References are placeholders
The DOCX bibliography section contains placeholder APA citations marked `[CITATION: Author Year]`. These need to be replaced with real references.

**Action**: Convert all `[CITATION: ...]` markers in the markdown chapters to proper APA 7th edition inline citations, then update the References section in `build_thesis_docx.py`.

#### Issue C: Front matter personalization
The DOCX auto-generates title pages, abstracts, and acknowledgements with placeholder text like `[Khmer title here]`, `[Student Name]`, etc.

**Action**: Update `build_thesis_docx.py` front-matter functions (`add_title_page`, `add_acknowledgement`, `add_khmer_abstract`, `add_english_abstract`) with the real content.

### Files to ignore / not modify
- `chapter2_presentation_of_project.md` — NOT used in DOCX build; it's an older parallel draft.
- `chapter5_results.md` — NOT used in DOCX build; superseded by `chapter4_results.md`.
- `chapter6_conclusion.md` — NOT used in DOCX build.
- `DEMO_DEFENSE_REDEMPTION_PLAN.md` — planning doc, not thesis content.

---

## 2. SPECIFIC TASKS FOR AN AI AGENT

### High Priority (do first)

1. **Reconcile experiment numbers**
   - Run: `python stress_testing/rl/experiments/exp_005_underwriting_convergence.py`
   - Run: `python stress_testing/rl/experiments/exp_006_fairness_audit.py`
   - Run: `python stress_testing/rl/experiments/exp_007_benchmark_comparison.py`
   - Run: `python stress_testing/rl/experiments/exp_008_human_in_the_loop.py`
   - Note the seed=42 outputs.
   - Update all tables in `chapter4_results.md` to match seed=42 outputs.
   - Update scaling factors in `thesis/health_rl/build_presentation.py` to match.
   - Regenerate figures: `python thesis/health_rl/build_presentation.py`
   - Regenerate DOCX: `python thesis/health_rl/build_thesis_docx.py`

2. **Fix references**
   - Search for `[CITATION:` across all `thesis/health_rl/chapter*.md` files.
   - Replace with proper APA inline citations (e.g., `(Li et al., 2010)`).
   - Update the reference list in `build_thesis_docx.py` lines ~748–784.

3. **Personalize front matter**
   - Edit `build_thesis_docx.py`:
     - `add_title_page()`: Real Khmer/English title, student name "LUN CHANPOLY", advisor name.
     - `add_acknowledgement()`: Real acknowledgement text.
     - `add_khmer_abstract()`: Real Khmer abstract (~200 words).
     - `add_english_abstract()`: Real English abstract (~250 words).
   - Regenerate DOCX.

### Medium Priority

4. **Table of contents sanity check**
   - Verify that every section header in the markdown (`#`, `##`, `###`) renders correctly in the DOCX.
   - Check that figure/table numbering is sequential (no gaps, no duplicates).

5. **Clean up duplicate chapter files**
   - Move `chapter5_results.md`, `chapter6_conclusion.md`, `chapter2_presentation_of_project.md` to an `archive/` subfolder so they don't confuse future agents.

6. **Regenerate defense presentation**
   - `python thesis/health_rl/build_presentation.py` — already done after number reconciliation.
   - Verify 20 slides, presenter name "LUN CHANPOLY", key titles present.
   - Run `pytest tests/test_build_presentation.py -v` to validate.

### Low Priority (nice to have)

7. **Abstract consistency**
   - Ensure the English abstract in the DOCX matches the findings in Chapter 5 exactly (same numbers, same conclusions).

8. **Figure caption review**
   - Every `[FIGURE: path — Figure X.Y. Caption]` should have a matching PNG file.
   - Every table should have a caption bolded above it: `**Table X.Y — Caption**`

---

## 3. DEMO FURNISHING — HOW TO MAKE IT DEFENSE-READY

The current demo (`demo/main.py`) is a FastAPI backend with a single `index.html` frontend. It has these API capabilities:
- `POST /api/simulate` — compute expected rewards for 4 actions on a single applicant
- `POST /api/simulate/stochastic` — stochastic realisation of all 4 actions
- `POST /api/bandit/run` — run one algorithm for N rounds
- `POST /api/bandit/compare` — run all 4 algorithms head-to-head
- `POST /api/pricing/optimize` — find profit-maximising premium multiplier
- `POST /api/pricing/batch` — batch optimise 100 random applicants
- `GET/POST /api/hitl/*` — human-in-the-loop review queue

### Recommended demo improvements

#### A. Interactive dashboard (highest impact)
Replace the bare `index.html` with a tabbed dashboard:

| Tab | What it shows | Backend endpoint |
|-----|---------------|------------------|
| **Applicant Simulator** | Form to build an applicant, see 4-action expected rewards, optimal action highlighted | `/api/simulate` |
| **Bandit Arena** | Run LinUCB/LinTS/Epsilon/StaticXGB for N rounds; live Chart.js line chart of cumulative reward & regret | `/api/bandit/run` + `/api/bandit/compare` |
| **Fairness Monitor** | PSI traffic-light cards (GREEN/AMBER/RED) for region & occupation; bar chart of approval rates | Compute from `/api/bandit/run` actions |
| **Premium Optimiser** | Single-applicant profit curve + batch histogram | `/api/pricing/optimize` + `/api/pricing/batch` |
| **HITL Queue** | Underwriter review interface: bandit recommendation → human override → metrics update | `/api/hitl/*` |
| **Drift Simulator** | Slider to inject a synthetic outbreak (shift region/age/BMI distribution), re-run bandit, show PSI spike | New endpoint (see below) |

#### B. Drift simulation endpoint (impressive for defense)
Add a new endpoint `POST /api/drift/simulate` that:
1. Takes drift parameters (e.g., `shift_region='Preah Sihanouk'`, `age_bias=-5`, `bmi_increase=2`, `hepatitis_b_rate=0.15`).
2. Generates a modified dataset slice (e.g., 500 applicants) with shifted demographics.
3. Runs LinUCB on the shifted data.
4. Computes PSI between original approved pool and drift-approved pool.
5. Returns: reward trajectory, PSI time series, traffic-light status.

This directly supports the "non-stationary drift" discussion in Chapter 6 (Future Work) and makes the demo interactive and memorable.

#### C. Visual polish
- Add a Cambodia-themed color palette (blue/white from the national flag, with gold accents).
- Use Chart.js (already referenced in `chapter4_project_analysis.md`) for all charts.
- Add a "live ticker" showing total applications processed, cumulative profit, current PSI status.
- Mobile-responsive layout (the thesis mentions mobile distribution).

#### D. Shadow mode visualization
Add a `POST /api/shadow/run` endpoint that:
1. Processes one applicant through BOTH the static XGB baseline AND LinUCB simultaneously.
2. Shows both recommendations side-by-side.
3. Highlights disagreements (e.g., red border when XGB says DECLINE but LinUCB says STANDARD).
4. Tracks disagreement rate over time.

This visualises the "Phase 1 — Shadow Mode" deployment roadmap from Chapter 3.

#### E. Narrated walkthrough mode
Add a "Defense Demo Mode" button that auto-advances through 5 pre-scripted scenarios:
1. Low-risk applicant → STANDARD (obvious case).
2. Borderline applicant → RATED (bandit learns pricing).
3. High-risk applicant → DECLINE (protect portfolio).
4. Uncertain applicant → REFER → human override (HITL value).
5. Drifted population → PSI turns RED → alert triggered.

Each step pauses with explanatory text. This turns the demo into a story the student can tell during defense without clicking randomly.

### Implementation notes for demo
- The demo is pure Python + FastAPI + Jinja2 + vanilla JS. Keep it that way — no React, no build step.
- All new endpoints should follow the existing Pydantic model pattern.
- Add new templates to `demo/templates/` and static assets to `demo/static/`.
- Run with: `uvicorn demo.main:app --reload --port 8000`

---

## 4. STYLE & CONVENTIONS

- **Language**: British English (e.g., "behaviour", "colour", "centre").
- **Numbers**: Use `$` for USD, comma thousands separators (`$58,642`), percentages with `%` symbol.
- **Math**: Inline math in `$...$`, display math in `$$...$$`.
- **Tables**: Caption above table in bold: `**Table X.Y — Caption**`.
- **Figures**: Use `[FIGURE: thesis/health_rl/figures/fig_NAME.png — Figure X.Y. Caption]`.
- **Citations**: APA 7th edition. Replace `[CITATION: Author Year]` with `(Author, Year)` or `Author (Year)`.
- **File naming**: Lowercase with underscores. Figures: `fig_{NN}_{slug}.png`.

---

## 5. BUILD COMMANDS

```powershell
# Run experiments
python stress_testing/rl/experiments/exp_005_underwriting_convergence.py
python stress_testing/rl/experiments/exp_006_fairness_audit.py
python stress_testing/rl/experiments/exp_007_benchmark_comparison.py
python stress_testing/rl/experiments/exp_008_human_in_the_loop.py

# Generate figures + presentation
python thesis/health_rl/build_presentation.py

# Generate Word thesis
python thesis/health_rl/build_thesis_docx.py

# Run tests
pytest tests/ -v

# Run demo
uvicorn demo.main:app --reload --port 8000
```

---

## 6. QUESTIONS FOR THE STUDENT

Before an agent proceeds, clarify:
1. **Which number set is canonical?** The old hardcoded ones (~$58k / ~$35k) or the actual experiment output (~$99k / ~$72k)?
2. **Advisor name** for the title page?
3. **Khmer title** exact spelling?
4. **Should the demo be deployed live** (Render, as mentioned in NFR-4) for the defense, or run locally?
