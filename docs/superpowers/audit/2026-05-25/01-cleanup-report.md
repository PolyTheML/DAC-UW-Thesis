# Cleanup Report — Proposed File-Level Changes

**Date**: 2026-05-25
**Mode**: Per-file proposals. Nothing has been deleted; this is the gate for the safe-cleanup execution phase.

---

## Classification key

- 🟥 **DELETE-SAFE** — generated artifact, deprecated, or untracked junk. Low risk.
- 🟧 **DELETE-AFTER-CONFIRM** — likely cruft but may have a use I cannot infer. User must confirm.
- 🟨 **REFACTOR-LATER** — keep, but earmark for the follow-up refactoring plan (folder move, rename, modularize).
- 🟩 **KEEP** — load-bearing for thesis or demo.

---

## Section A — Safe deletions (untracked cruft & generated outputs)

These are all **untracked or .gitignored** files. Removing them does not touch git history. The deletions can be executed with simple `rm` / `Remove-Item`; no `git rm` needed because git already doesn't know about them.

| File | Size | Reason | Class |
|---|---|---|---|
| `analyze2.py` … `analyze6.py` (5 files) | ~10 KB each | One-shot docx-inspection scripts with hardcoded paths to a file that no longer exists (`I5_ITC_Thesis_Template_Guideline-AMS (1).docx` is deleted per `git status`). Already gitignored (`analyze*.py`). | 🟥 |
| `analyze_build.py`, `analyze_build2.py`, `analyze_build3.py`, `analyze_template.py` (4 files) | ~5 KB total | Same — throwaway docx debugging scripts. | 🟥 |
| `_fix_theta.py` (under `thesis/health_rl/`) | <1 KB | One-shot script that already fixed a `\theta`-encoding bug in `chapter2_literature_review.md`. The fix is committed; the script has no future use. Untracked. | 🟥 |
| `shadow_mode.db` (40 KB, root) | 40 KB | SQLite runtime database for the deprecated `backend/` shadow mode. Already gitignored (`*.db`). | 🟥 |
| `demo/hitl.db` | small | Same — runtime database for the demo HITL feature, regenerable. Gitignored (`*.db`). | 🟥 |
| `stress_testing/rl/experiments/exp_005_output.txt`, `exp_005_output_utf8.txt`, `exp_006_output*.txt`, `exp_007_output*.txt`, `exp_008_output*.txt`, `exp_009_output*.txt`, `exp_010_output.txt` (≈11 files) | ~50–500 KB each | Saved stdout from past experiment runs. Regenerable. Untracked. Each `_utf8` variant is a Windows console-encoding artifact. | 🟥 |
| `.pytest_cache/` | small | Tooling cache. Gitignored. | 🟥 |
| `**/__pycache__/` | varies | Python bytecode caches. Gitignored. | 🟥 |
| `thesis/docx_structure.txt`, `thesis/docx_structure_full.txt` | 4–20 KB | Throwaway dumps of a docx structure used during template debugging. Untracked. | 🟥 |
| `thesis/template_extract.txt`, `thesis/template_tables.txt` | small | Same. | 🟥 |
| `thesis/health_rl/template_extract_full.txt` | small | Same. | 🟥 |
| `thesis/health_rl/slide_content.txt` | small | Plain-text dump of presentation slides. Untracked. | 🟥 |
| `thesis/I5_ITC_POLY_BACKUP.docx` | large | Backup of a docx that itself is also in the tree (`thesis/I5_ITC_POLY.docx`). Untracked. The pattern "X_BACKUP" is duplicated-state risk. | 🟥 |
| `thesis/I5_ITC_Thesis_Template_Guideline-AMS_BACKUP_CLEAN.docx` | large | Another backup variant. Tracked but `git status` shows it as modified — it was either modified or the working copy diverged. If you don't need to keep both variants, pick one and `git rm` the other. | 🟧 |

**Recommend**: execute all 🟥 deletions in one batch after your OK; nothing tracked is touched.

---

## Section B — Tracked files proposed for deletion after confirmation

These are in git history and require `git rm` + commit.

| File | Reason | Class |
|---|---|---|
| `thesis/health_rl/chapter5_results.md` (untracked actually — confirmed) | Old single-seed version of Ch V. Superseded by `chapter4_results.md`. Keeps the inconsistent numbers alive. | 🟥 (already untracked, safe to rm) |
| `thesis/health_rl/chapter6_conclusion.md` (untracked) | Alternate conclusion that **mixes single-seed and 20-seed numbers in the same paragraph**. Internally inconsistent (see RI-2). Superseded by `chapter5_conclusion.md`. | 🟥 (already untracked) |
| `backend/` (entire directory: 8 files) | Marked deprecated in `.gitignore` line 73 ("Old backend API (superseded by demo/)") yet still tracked. Code path: only `tests/test_shadow_mode.py` imports it. **However**: chapter 3 §3.6.1 describes Shadow Mode as a deployment design. **Decision required**: either (a) revive `backend/` (remove gitignore line, write deployment-test), or (b) `git rm -r backend/ tests/test_shadow_mode.py` and rewrite ch3 §3.6.1 to mark Shadow Mode as design-only future work. | 🟧 |
| `tests/test_shadow_mode.py` (untracked) | Imports from the deprecated `backend/shadow/`. Orphaned. | 🟥 |
| `thesis/health_rl/build_presentation.py` + `build_presentation_sothea_format.py` + `build_burgundy_presentation.py` | 3 different presentation builders for the same defense. Only one is canonical for the live deck. Pick one (likely `build_burgundy_presentation.py` based on file names matching the live `.pptx`), delete the others. | 🟧 |
| `thesis/health_rl/burgundy_defense_presentation.pptx` vs `burgundy_defense_presentation_filled.pptx` vs `health_rl_defense_presentation.pptx` | Three deck variants. Decide which is canonical. The "_filled" suffix suggests it's the populated version of the template; the unsuffixed could be the template. Recommend keeping the "_filled" version and the build script that produced it; archive or delete the rest. | 🟧 |
| `thesis/AMS.png`, `thesis/DAC.jpg`, `thesis/ITC.jpg` | Logos. Keep if used by `build_thesis_docx.py` (verify with grep). | 🟩 if used, 🟥 if not |
| `thesis/I5_ITC_POLY.docx`, `thesis/I5_ITC_POLY_BACKUP.docx` | ITC poly thesis template variants. Used as input templates for the docx builder? Probably keep one. | 🟧 |
| `thesis/health_rl/ITC_Thesis_Draft.docx` | Probably the build output. Regenerable from `build_thesis_docx.py`. | 🟧 keep tracked or regenerate on demand |

---

## Section C — Refactor candidates (out of scope this session)

These are kept but should be cleaned up in a follow-up `writing-plans` plan.

| Item | Refactor proposed |
|---|---|
| **Chapter filename ↔ chapter-number mismatch** (chapter2_literature_review.md is actually Ch III; chapter4_results.md is actually Ch V; chapter5_conclusion.md is actually Ch VI) | Rename canonical chapter files to match their declared chapter numbers. Update build_thesis_docx.py glob if needed. |
| **Duplicate Ch II content** in `chapter1_introduction.md` lines 51-150 vs `chapter2_presentation_of_project.md` | Decide which file owns Ch II; remove from the other. |
| **Orphan EDA figures** — `figures/fig_eda_01..14.png` and `figures/eda_summary_statistics.csv` are generated by `generate_eda_figures.py` but not embedded in any chapter | Either embed in Ch III (dataset section) or move to `thesis/health_rl/figures/_appendix/`. |
| **Five undocumented experiments** (EXP-009/010/011/012/013) | Either promote results into Ch V/VI, or move source to `stress_testing/rl/experiments/_unused/` with a README explaining why. |
| **Multiple presentation builders** (3 variants) | Consolidate into a single `build_presentation.py` with config-driven theme selection (burgundy / sothea / default). |
| **No central config** — reward parameters live in `RewardConfig` dataclass; experiment hyperparameters (`alpha=1.0`, `v2=1.0`, `epsilon=0.15`, `n_seeds=20`, `N_ROUNDS=5000`) are scattered as constants across each `exp_*.py` | Create `stress_testing/rl/config.py` (or `experiments/_config.yaml`) holding all hyperparameters; each experiment imports from it. Currently changing N_ROUNDS requires editing 9 files. |
| **`scripts/` (thesis_loop, thesis_rewriter, thesis_scorer)** | Tested and tracked, but unclear if currently used. If used: keep. If not: archive. |
| **`wiki/sources/` and `wiki/topics/`** | Reference templates for ITC formatting. Useful as writing aids. Consider moving to `docs/templates/` for clarity. |
| **`case-study/` directory name** | The dataset is the **primary** dataset, not a "case study". Rename to `data/cambodia/`. |
| **`stress_testing/rl/`** | The "stress_testing" naming is a holdover from the previous (auto insurance) thesis. Rename to `experiments/` or `health_rl/` to reflect the actual content. |
| **`requirements.txt`** | Switch from `>=` to `==` pins for true reproducibility. Add a `requirements-dev.txt` for matplotlib + pytest + statsmodels separated from the runtime stack. |

---

## Section D — Files that **must stay** (load-bearing)

| Category | Files |
|---|---|
| Core algorithm | `stress_testing/rl/underwriting_bandit.py`, `stress_testing/rl/__init__.py` |
| Experiment scripts | `stress_testing/rl/experiments/exp_{005..013}.py` + `experiment_utils.py` + `statistical_utils.py` |
| Dataset & training | `case-study/generate_cambodia_dataset.py`, `case-study/train_cambodia_models.py`, `case-study/train_cambodia_rl.py`, `case-study/cambodia_dataset.csv`, `case-study/cambodia_dataset.parquet`, `case-study/models/*.pkl + *.json + *.csv + *.parquet` |
| Demo platform | `demo/main.py`, `demo/pricing_engine.py`, `demo/hitl_db.py`, `demo/static/*`, `demo/templates/index.html`, `render.yaml`, `requirements.txt` |
| Chapter sources (canonical set) | `thesis/health_rl/chapter{1,2_presentation_of_project,2_literature_review,3_methodology,4_project_analysis,4_results,5_conclusion}.md` |
| Chapter figures (referenced) | `thesis/health_rl/figures/fig_*.png/svg` for figures cited in chapters |
| Build scripts | `thesis/health_rl/build_thesis_docx.py`, `thesis/health_rl/scripts/build_fig_ch4_*.py`, `thesis/health_rl/generate_eda_figures.py`, `thesis/health_rl/latex_render.py` |
| Writing aids | `thesis/health_rl/ITC_STYLE_GUIDE.md`, `thesis/health_rl/AGENT_BRIEF.md`, `wiki/sources/*.md`, `wiki/topics/*.md` |
| Top-level docs | `CLAUDE.md`, `AGENTS.md`, `COLLAB.md`, `.gitignore`, `docs/superpowers/` |
| Auto-research loop | `scripts/thesis_loop.py`, `thesis_rewriter.py`, `thesis_scorer.py` (tested by `tests/test_thesis_*.py`) — keep if still used |
| Tests | `tests/test_build_presentation.py`, `tests/test_thesis_*.py` (3 files) |

---

## Proposed safe-cleanup batch (Section A only)

For your one-click approval — these 30+ items are **untracked or gitignored**, so no git history is affected:

```text
# Throwaway docx scripts
analyze2.py
analyze3.py
analyze4.py
analyze5.py
analyze6.py
analyze_build.py
analyze_build2.py
analyze_build3.py
analyze_template.py
thesis/health_rl/_fix_theta.py

# Runtime SQLite databases (regenerable)
shadow_mode.db
demo/hitl.db

# Generated experiment outputs (regenerable)
stress_testing/rl/experiments/exp_005_output.txt
stress_testing/rl/experiments/exp_005_output_utf8.txt
stress_testing/rl/experiments/exp_006_output.txt
stress_testing/rl/experiments/exp_006_output_utf8.txt
stress_testing/rl/experiments/exp_007_output.txt
stress_testing/rl/experiments/exp_007_output_utf8.txt
stress_testing/rl/experiments/exp_008_output.txt
stress_testing/rl/experiments/exp_008_output_utf8.txt
stress_testing/rl/experiments/exp_009_output.txt
stress_testing/rl/experiments/exp_010_output.txt

# Throwaway template-debug dumps
thesis/docx_structure.txt
thesis/docx_structure_full.txt
thesis/template_extract.txt
thesis/template_tables.txt
thesis/health_rl/template_extract_full.txt
thesis/health_rl/slide_content.txt

# Superseded duplicate docx backups
thesis/I5_ITC_POLY_BACKUP.docx

# Superseded chapter drafts (internally inconsistent)
thesis/health_rl/chapter5_results.md
thesis/health_rl/chapter6_conclusion.md

# Orphan test (its target backend/ is deprecated)
tests/test_shadow_mode.py

# Pytest cache + bytecode
.pytest_cache/
**/__pycache__/
```

After your approval, Section B (tracked deletions) can be addressed in a follow-up.
