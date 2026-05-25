# Repository Audit & Safe Cleanup — Design

**Date**: 2026-05-25
**Mode**: Audit + safe cleanup (no source refactoring)
**Thesis**: *Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia*

---

## Goal

Produce a rigorous, evidence-based audit of `C:\DAC-UW-Thesis` covering: dead code, structure, thesis↔code consistency, literature integrity, and research-quality improvements. Execute only safe, pre-approved deletions in this pass. Source refactoring becomes a follow-up implementation plan.

## Non-goals (out of scope this session)

- Source refactoring (folder moves, renames, modularization, config centralization).
- Chapter rewrites or content edits.
- Re-running any experiment (verify reproducibility by inspection, not execution).
- Touching the DAC platform repo at `C:\DAC-UW-Agent`.

## Scope decisions (user-confirmed)

- **Operating mode**: audit + safe cleanup; destructive ops gated on per-list approval.
- **Literature validation depth**: full web verification of all references in chapter 2 (17 confirmed).
- **Code↔thesis check depth**: full audit of all 9 chapter files including duplicate-variant resolution.

## Deliverables

All written to `docs/superpowers/audit/2026-05-25/`:

| # | File | Purpose |
|---|------|---------|
| 1 | `01-cleanup-report.md` | Per-file deletion/refactor proposals with rationale. Gate for safe-delete phase. |
| 2 | `02-structure-overview.md` | Current annotated tree + proposed clean tree + naming/config recommendations. |
| 3 | `03-research-integrity.md` | Code↔thesis mismatch register; resolves duplicate chapters. |
| 4 | `04-literature-validation.md` | Per-reference verification table with web evidence. |
| 5 | `05-improvements.md` | Critical / important / optional improvements across methodology, baselines, ablations, stats, reproducibility, evaluation, novelty. |
| 6 | `06-final-assessment.md` | Thesis-ready / publication-ready / production-ready verdict with reasoning. |

## Process (7 steps, sequential)

1. **Enumerate & classify** every file in the repo. Label: thesis-critical / supporting / cruft / ambiguous. Feeds reports 1 & 2.
2. **Read all 9 chapter files**; build claims/methods/experiments/figures inventory.
3. **Read all RL source** (`stress_testing/rl/`, `backend/`, `demo/`, `case-study/`, `scripts/`). Map source↔chapter.
4. **Cross-check** chapter claims against code; build mismatch register → report 3.
5. **Verify all references** via WebSearch (one per ref; second on conflict) → report 4.
6. **Write reports 1, 2, 5, 6** — synthesizing 1–5.
7. **Present cleanup list for approval**, execute approved deletions only. Safe candidates known a priori:
   - `__pycache__/` dirs throughout
   - `stress_testing/rl/experiments/exp_*_output*.txt` (generated artifacts)
   - Duplicate `thesis/I5_*BACKUP*.docx` variants
   - Stale root scripts: `analyze2.py` … `analyze6.py`, `analyze_build*.py`, `analyze_template.py`, `_fix_theta.py`
   - `shadow_mode.db` (if not referenced)
   - Other items surfaced by step 1 that you approve

## Constraints

- No deletion without per-item documentation in report 1.
- Preserve reproducibility (no removal of dataset files, experiment scripts, model artifacts referenced by thesis).
- Maintain git history (use `git rm` not `rm`).
- Treat repo as future open-source candidate.

## Estimated cost

~17 WebSearches, ~30 file reads, 6 doc writes, a few targeted greps. Mid-sized session.

## Open questions

None at design time. All scope and depth questions answered during brainstorming.

## Follow-up (not this session)

- A `writing-plans` implementation plan for source refactoring (steps + diffs).
- A second audit pass post-refactor to confirm the new structure preserves all reports' findings.
