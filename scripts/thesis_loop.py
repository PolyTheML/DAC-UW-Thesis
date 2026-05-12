from __future__ import annotations

import argparse
import subprocess
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


def _print_summary(results: list[ChapterResult]) -> None:
    header = f"{'Chapter':<45} {'Before':>6} {'After':>5} {'Iter':>4} {'Status':>6}"
    print(f"\n{header}")
    print("-" * len(header))
    for r in results:
        print(
            f"{r.path.name:<45} {r.score_before:>6} {r.score_after:>5} "
            f"{r.iterations:>4} {r.status:>6}"
        )


def _commit_changes(changed: list[Path]) -> None:
    if not changed:
        return
    for p in changed:
        subprocess.run(["git", "add", str(p)], check=True)
    subprocess.run(
        [
            "git", "commit", "-m",
            "style: auto-fix ITC compliance violations\n\n"
            "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>",
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ITC thesis style compliance loop — autoresearch-style chapter rewriter"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Score and report violations without writing any files",
    )
    args = parser.parse_args()

    results: list[ChapterResult] = []
    changed: list[Path] = []

    for chapter in CHAPTERS:
        print(f"Processing {chapter.name}...")
        result = _run_chapter(chapter, dry_run=args.dry_run)
        results.append(result)
        if not args.dry_run and result.score_after > result.score_before:
            changed.append(chapter)

    _print_summary(results)

    if not args.dry_run:
        _commit_changes(changed)


if __name__ == "__main__":
    main()
