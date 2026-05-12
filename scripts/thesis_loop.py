from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.thesis_scorer import ComplianceReport, score_chapter
from scripts.thesis_rewriter import rewrite_chapter

PASS_THRESHOLD = 85
MAX_ITER = 3
MODEL = "claude-opus-4-7"
CHAPTERS = sorted((ROOT / "thesis" / "health_rl").glob("chapter*.md"))


@dataclass
class ChapterResult:
    path: Path
    score_before: int
    score_after: int
    iterations: int
    status: str  # "PASS" | "WARN" | "SKIP"


def _run_chapter(
    path: Path, *, dry_run: bool = False, model: str = MODEL
) -> ChapterResult:
    content = path.read_text(encoding="utf-8")
    report = score_chapter(content, model=model)
    score_before = report.score

    if report.passed:
        return ChapterResult(path, score_before, score_before, 0, "SKIP")

    best_content = content
    best_report = report
    iterations_used = 0

    for iteration in range(1, MAX_ITER + 1):
        iterations_used = iteration
        revised = rewrite_chapter(best_content, best_report.violations, model=model)

        # Truncation guard: discard if revised is < 50% of current content length
        if len(revised) < len(best_content) * 0.5:
            continue

        new_report = score_chapter(revised, model=model)
        if new_report.score > best_report.score:
            best_content = revised
            best_report = new_report

        if best_report.passed:
            break

    if not dry_run and best_content != content:
        path.write_text(best_content, encoding="utf-8")

    status = "PASS" if best_report.passed else "WARN"
    return ChapterResult(path, score_before, best_report.score, iterations_used, status)
