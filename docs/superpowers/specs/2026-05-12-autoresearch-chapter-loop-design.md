# Autoresearch-Style Chapter Writing Loop — Design Spec

**Date**: 2026-05-12  
**Status**: Approved  
**Scope**: All 5 thesis chapters in `thesis/health_rl/chapter*.md`

---

## 1. Motivation

Karpathy's autoresearch framework demonstrates that an autonomous agent loop — one editable file, one fixed goal file, one metric, iterate until passing — produces reliable improvement without human micro-management. This spec adapts that pattern to thesis chapter quality assurance:

| autoresearch | This system |
|---|---|
| `program.md` | `ITC_STYLE_GUIDE.md` — fixed, never modified |
| `train.py` | `chapterN_*.md` — the editable files |
| `val_bpb` metric | ITC style compliance score (0–100) |
| overnight GPU loop | score → rewrite → re-score → keep if improved |

---

## 2. Architecture

Three new files under `scripts/`:

```
scripts/
  thesis_scorer.py      # scores a chapter against the style guide
  thesis_rewriter.py    # rewrites a chapter to fix violations
  thesis_loop.py        # orchestrator — entry point
```

Input files (read-only):
- `thesis/health_rl/ITC_STYLE_GUIDE.md`

Editable files (may be overwritten when score improves):
- `thesis/health_rl/chapter1_introduction.md`
- `thesis/health_rl/chapter2_literature_review.md`
- `thesis/health_rl/chapter2_presentation_of_project.md`
- `thesis/health_rl/chapter3_methodology.md`
- `thesis/health_rl/chapter4_project_analysis.md`
- `thesis/health_rl/chapter4_results.md`
- `thesis/health_rl/chapter5_conclusion.md`

---

## 3. Data Structures

```python
@dataclass
class Violation:
    section: str      # e.g. "1.2 Problem Statement"
    rule: str         # e.g. "heading_hierarchy" | "citation_placeholder" |
                      #       "figure_placeholder" | "itc_structure" | "apa7_format"
    description: str  # human-readable explanation
    severity: str     # "error" | "warning"

@dataclass
class ComplianceReport:
    score: int                  # 0–100
    violations: list[Violation]
    pass_threshold: int = 85
```

---

## 4. Scoring Breakdown

| Rule | Points | What is checked |
|---|---|---|
| Heading hierarchy | 25 | `#` → `##` → `###` never skips a level |
| Citation placeholders | 25 | Factual/statistical claims have `[CITATION: Author Year]` |
| Figure/Table placeholders | 20 | `[FIGURE: caption]` / `[TABLE: caption]` where referenced |
| ITC section structure | 20 | Correct sections present per structure mapping table |
| APA 7 format | 10 | Reference list entries follow APA 7 format |
| **Total** | **100** | Pass threshold: **85** |

---

## 5. Loop Logic

```
PASS_THRESHOLD = 85
MAX_ITER = 3
MODEL = "claude-opus-4-7"
CHAPTERS = sorted(Path("thesis/health_rl").glob("chapter*.md"))

for chapter in CHAPTERS:
    report = score_chapter(chapter)
    if report.score >= PASS_THRESHOLD:
        mark PASS, skip to next chapter
    for iter in range(MAX_ITER):
        revised = rewrite_chapter(chapter_content, report.violations)
        new_report = score_chapter(revised)
        if new_report.score > report.score:
            overwrite chapter file with revised content
            report = new_report
        if report.score >= PASS_THRESHOLD:
            break

git commit all changed chapters in one commit
print summary table
```

---

## 6. Components

### `thesis_scorer.py`

- Reads `ITC_STYLE_GUIDE.md` once at import time
- `score_chapter(content: str) -> ComplianceReport`
- Calls Claude API (`claude-opus-4-7`) with a structured prompt requesting JSON output
- Parses response into `ComplianceReport`; falls back to score=0 on parse error

### `thesis_rewriter.py`

- `rewrite_chapter(content: str, violations: list[Violation]) -> str`
- Calls Claude API with the chapter content + serialized violations list
- Instructs the model to fix **only the listed violations** — no content changes
- Does not add new arguments, does not remove existing text
- `[CITATION: needed]` placeholders are added where claims are unsupported (never fabricated citations)

### `thesis_loop.py`

- Entry point: `python scripts/thesis_loop.py [--dry-run]`
- `--dry-run`: score and report violations without writing any files
- Prints a summary table on completion:

```
Chapter                            Before  After  Iter  Status
chapter1_introduction.md             62     91      2    PASS
chapter2_literature_review.md        78     91      1    PASS
chapter3_methodology.md              55     83      3    WARN
chapter4_project_analysis.md         70     88      2    PASS
chapter5_conclusion.md               80     91      1    PASS
```

---

## 7. Error Handling

| Condition | Behaviour |
|---|---|
| Revised content < 50% of original length | Discard revision, treat as failed iteration |
| API call fails | Retry once with 2s backoff; if still failing, log ERROR and skip chapter |
| Score does not improve | Keep existing file unchanged for that iteration |
| `--dry-run` flag | Score all chapters, print report, write nothing |

---

## 8. Constraints

- Does **not** change the substance of arguments — only fixes style rule violations
- Does **not** fabricate citations — only adds `[CITATION: needed]` placeholders
- Does **not** modify any file outside `thesis/health_rl/chapter*.md`
- Does **not** modify `ITC_STYLE_GUIDE.md`
- Requires `ANTHROPIC_API_KEY` environment variable

---

## 9. Dependencies

```
anthropic>=0.25.0   # Claude API client
python>=3.11
```

No other new dependencies.
