# Autoresearch Chapter Writing Loop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous loop that scores all thesis chapters against `ITC_STYLE_GUIDE.md`, rewrites each to fix violations, re-scores, keeps improvements, and commits — mirroring Karpathy's autoresearch pattern.

**Architecture:** Three scripts under `scripts/` — a scorer (Claude API → ComplianceReport), a rewriter (Claude API → fixed markdown), and an orchestrator that runs the score→rewrite→re-score→keep loop up to 3 iterations per chapter, stopping early when a chapter reaches score ≥ 85.

**Tech Stack:** Python 3.11, `anthropic>=0.25.0` (Claude API), `pytest`, existing project structure.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `scripts/thesis_scorer.py` | Create | `Violation`, `ComplianceReport` dataclasses + `score_chapter()` |
| `scripts/thesis_rewriter.py` | Create | `rewrite_chapter()` — fixes listed violations only |
| `scripts/thesis_loop.py` | Create | Orchestrator, CLI entry point, summary table, git commit |
| `tests/test_thesis_scorer.py` | Create | Unit tests for data structures, JSON parsing, API call |
| `tests/test_thesis_rewriter.py` | Create | Unit tests for rewriter API call and no-op behaviour |
| `tests/test_thesis_loop.py` | Create | Unit tests for loop logic, truncation guard, dry-run |
| `requirements.txt` | Modify | Add `anthropic>=0.25.0` |

---

## Task 1: Data structures + dependency

**Files:**
- Create: `scripts/__init__.py` (empty)
- Create: `scripts/thesis_scorer.py` (data structures only — no API yet)
- Create: `tests/test_thesis_scorer.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add `anthropic` to requirements.txt**

In `requirements.txt`, add after the last line:
```
anthropic>=0.25.0
```

- [ ] **Step 2: Install the dependency**

```bash
pip install anthropic>=0.25.0
```

Expected: `Successfully installed anthropic-...`

- [ ] **Step 3: Create empty `scripts/__init__.py`**

Create `scripts/__init__.py` with empty content (enables `from scripts.thesis_scorer import ...` in tests).

- [ ] **Step 4: Write failing tests for data structures**

Create `tests/test_thesis_scorer.py`:

```python
import pytest
from scripts.thesis_scorer import Violation, ComplianceReport


def test_violation_fields():
    v = Violation(
        section="1.1",
        rule="heading_hierarchy",
        description="### used before ##",
        severity="error",
    )
    assert v.section == "1.1"
    assert v.rule == "heading_hierarchy"
    assert v.severity == "error"


def test_compliance_report_passes_at_threshold():
    report = ComplianceReport(score=85)
    assert report.passed is True


def test_compliance_report_fails_below_threshold():
    report = ComplianceReport(score=84)
    assert report.passed is False


def test_compliance_report_custom_threshold():
    report = ComplianceReport(score=70, pass_threshold=70)
    assert report.passed is True


def test_compliance_report_violations_list():
    v = Violation("2.1", "citation_placeholder", "Missing citation", "warning")
    report = ComplianceReport(score=70, violations=[v])
    assert len(report.violations) == 1
    assert report.violations[0].rule == "citation_placeholder"
```

- [ ] **Step 5: Run tests — verify they FAIL**

```bash
python -m pytest tests/test_thesis_scorer.py -v
```

Expected: `ImportError` — `scripts.thesis_scorer` does not exist yet.

- [ ] **Step 6: Create `scripts/thesis_scorer.py` with data structures**

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Violation:
    section: str
    rule: str
    description: str
    severity: str  # "error" | "warning"


@dataclass
class ComplianceReport:
    score: int
    violations: list[Violation] = field(default_factory=list)
    pass_threshold: int = 85

    @property
    def passed(self) -> bool:
        return self.score >= self.pass_threshold
```

- [ ] **Step 7: Run tests — verify they PASS**

```bash
python -m pytest tests/test_thesis_scorer.py -v
```

Expected: `5 passed`

- [ ] **Step 8: Commit**

```bash
git add scripts/__init__.py scripts/thesis_scorer.py tests/test_thesis_scorer.py requirements.txt
git commit -m "feat: add Violation and ComplianceReport data structures"
```

---

## Task 2: Scorer — JSON parsing

The scorer calls Claude API and receives a JSON string. This task implements and tests the parsing logic in isolation (no API call yet).

**Files:**
- Modify: `scripts/thesis_scorer.py`
- Modify: `tests/test_thesis_scorer.py`

- [ ] **Step 1: Write failing tests for `_parse_response`**

Add to `tests/test_thesis_scorer.py`:

```python
from scripts.thesis_scorer import _parse_response


def test_parse_valid_json():
    json_str = '{"score": 72, "violations": [{"section": "1.1", "rule": "heading_hierarchy", "description": "### before ##", "severity": "error"}]}'
    report = _parse_response(json_str)
    assert report.score == 72
    assert len(report.violations) == 1
    assert report.violations[0].rule == "heading_hierarchy"


def test_parse_empty_violations():
    report = _parse_response('{"score": 90, "violations": []}')
    assert report.score == 90
    assert report.violations == []


def test_parse_missing_violations_key():
    report = _parse_response('{"score": 90}')
    assert report.score == 90
    assert report.violations == []


def test_parse_malformed_json_returns_zero():
    report = _parse_response("not json at all")
    assert report.score == 0
    assert report.violations[0].rule == "parse_error"


def test_parse_missing_score_returns_zero():
    report = _parse_response('{"violations": []}')
    assert report.score == 0
```

- [ ] **Step 2: Run — verify they FAIL**

```bash
python -m pytest tests/test_thesis_scorer.py::test_parse_valid_json -v
```

Expected: `ImportError` — `_parse_response` not defined yet.

- [ ] **Step 3: Add `_parse_response` to `scripts/thesis_scorer.py`**

Add after the dataclasses:

```python
import json


def _parse_response(json_str: str) -> ComplianceReport:
    try:
        data = json.loads(json_str)
        score = int(data["score"])
        violations = [
            Violation(
                section=v["section"],
                rule=v["rule"],
                description=v["description"],
                severity=v["severity"],
            )
            for v in data.get("violations", [])
        ]
        return ComplianceReport(score=score, violations=violations)
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return ComplianceReport(
            score=0,
            violations=[
                Violation(
                    section="",
                    rule="parse_error",
                    description="Failed to parse scorer response",
                    severity="error",
                )
            ],
        )
```

- [ ] **Step 4: Run — verify all scorer tests PASS**

```bash
python -m pytest tests/test_thesis_scorer.py -v
```

Expected: `10 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/thesis_scorer.py tests/test_thesis_scorer.py
git commit -m "feat: add JSON response parsing for compliance scorer"
```

---

## Task 3: Scorer — Claude API integration

Wire up the actual `score_chapter()` API call. Tests mock the `anthropic.Anthropic` client.

**Files:**
- Modify: `scripts/thesis_scorer.py`
- Modify: `tests/test_thesis_scorer.py`

- [ ] **Step 1: Write failing tests for `score_chapter`**

Add to `tests/test_thesis_scorer.py`:

```python
import os
from unittest.mock import MagicMock, patch


@patch("scripts.thesis_scorer.anthropic.Anthropic")
def test_score_chapter_returns_report(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='{"score": 80, "violations": []}')]
    )
    from scripts.thesis_scorer import score_chapter
    report = score_chapter("# I. INTRODUCTION\n\nSome text.")
    assert report.score == 80
    assert mock_client.messages.create.called


@patch("scripts.thesis_scorer.anthropic.Anthropic")
def test_score_chapter_passes_style_guide_in_prompt(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='{"score": 70, "violations": []}')]
    )
    from scripts.thesis_scorer import score_chapter
    score_chapter("# Chapter")
    user_content = mock_client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "ITC Style Guide" in user_content


@patch("scripts.thesis_scorer.anthropic.Anthropic")
def test_score_chapter_uses_configured_model(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='{"score": 70, "violations": []}')]
    )
    from scripts.thesis_scorer import score_chapter
    score_chapter("# Chapter", model="claude-haiku-4-5-20251001")
    assert mock_client.messages.create.call_args.kwargs["model"] == "claude-haiku-4-5-20251001"
```

- [ ] **Step 2: Run — verify they FAIL**

```bash
python -m pytest tests/test_thesis_scorer.py::test_score_chapter_returns_report -v
```

Expected: `ImportError` — `score_chapter` not defined.

- [ ] **Step 3: Add imports and constants to `scripts/thesis_scorer.py`**

Add at the top of the file (after `from __future__ import annotations`):

```python
import json
import os
from pathlib import Path

import anthropic

_STYLE_GUIDE_PATH = Path(__file__).parent.parent / "thesis" / "health_rl" / "ITC_STYLE_GUIDE.md"
_STYLE_GUIDE: str = _STYLE_GUIDE_PATH.read_text(encoding="utf-8")

_SCORER_SYSTEM = (
    "You are an ITC thesis style compliance checker.\n"
    "Score the chapter from 0 to 100 based on these rules:\n"
    "- Heading hierarchy (25 pts): markdown # → ## → ### never skips a level\n"
    "- Citation placeholders (25 pts): factual or statistical claims have [CITATION: Author Year]\n"
    "- Figure/Table placeholders (20 pts): [FIGURE: caption] where figures are referenced; "
    "[TABLE: caption] where tables are referenced\n"
    "- ITC section structure (20 pts): correct sections present per the ITC structure mapping\n"
    "- APA 7 format (10 pts): reference list entries follow APA 7th edition\n\n"
    "Return ONLY valid JSON, no prose, no markdown fences:\n"
    '{"score": <int 0-100>, "violations": [{"section": "<heading>", "rule": "<rule>", '
    '"description": "<what is wrong>", "severity": "<error|warning>"}]}'
)
```

- [ ] **Step 4: Add `score_chapter()` to `scripts/thesis_scorer.py`**

Add after `_parse_response`:

```python
def score_chapter(content: str, *, model: str = "claude-opus-4-7") -> ComplianceReport:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user_message = f"ITC Style Guide:\n\n{_STYLE_GUIDE}\n\n---\n\nChapter to score:\n\n{content}"
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=_SCORER_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )
    return _parse_response(response.content[0].text)
```

- [ ] **Step 5: Run — verify all scorer tests PASS**

```bash
python -m pytest tests/test_thesis_scorer.py -v
```

Expected: `13 passed`

- [ ] **Step 6: Commit**

```bash
git add scripts/thesis_scorer.py tests/test_thesis_scorer.py
git commit -m "feat: add score_chapter() with Claude API integration"
```

---

## Task 4: Rewriter

**Files:**
- Create: `scripts/thesis_rewriter.py`
- Create: `tests/test_thesis_rewriter.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_thesis_rewriter.py`:

```python
from unittest.mock import MagicMock, patch
from scripts.thesis_scorer import Violation


@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_calls_api_and_returns_string(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="# Fixed [CITATION: needed]")]
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("1.1", "citation_placeholder", "Missing citation", "warning")]
    result = rewrite_chapter("# Original", violations)
    assert result == "# Fixed [CITATION: needed]"
    assert mock_client.messages.create.called


def test_rewrite_returns_original_when_no_violations():
    from scripts.thesis_rewriter import rewrite_chapter
    content = "# Chapter\n\nSome text."
    result = rewrite_chapter(content, violations=[])
    assert result == content


@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_includes_violations_in_user_message(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="fixed")]
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("2.1", "heading_hierarchy", "### before ##", "error")]
    rewrite_chapter("content", violations)
    user_msg = mock_client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "heading_hierarchy" in user_msg
    assert "2.1" in user_msg
    assert "### before ##" in user_msg


@patch("scripts.thesis_rewriter.anthropic.Anthropic")
def test_rewrite_uses_configured_model(mock_class, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="fixed")]
    )
    from scripts.thesis_rewriter import rewrite_chapter
    violations = [Violation("1.1", "citation_placeholder", "Missing", "warning")]
    rewrite_chapter("content", violations, model="claude-haiku-4-5-20251001")
    assert mock_client.messages.create.call_args.kwargs["model"] == "claude-haiku-4-5-20251001"
```

- [ ] **Step 2: Run — verify they FAIL**

```bash
python -m pytest tests/test_thesis_rewriter.py -v
```

Expected: `ImportError` — `scripts.thesis_rewriter` not defined.

- [ ] **Step 3: Create `scripts/thesis_rewriter.py`**

```python
from __future__ import annotations

import os

import anthropic

from scripts.thesis_scorer import Violation

_REWRITER_SYSTEM = (
    "You are an ITC thesis style compliance editor.\n"
    "Fix ONLY the violations listed below. Do not change any other content — "
    "not arguments, not data, not conclusions.\n"
    "Rules per violation type:\n"
    "- heading_hierarchy: fix the heading level so no level is skipped\n"
    "- citation_placeholder: add [CITATION: needed] directly after the unsupported claim\n"
    "- figure_placeholder: add [FIGURE: description] on its own line where a figure is referenced\n"
    "- table_placeholder: add [TABLE: description] on its own line where a table is referenced\n"
    "- itc_structure: add the missing section heading in the correct position\n"
    "- apa7_format: fix the reference list entry to APA 7 format\n\n"
    "Do not fabricate citations. Do not remove existing text.\n"
    "Return the complete fixed markdown chapter and nothing else."
)


def rewrite_chapter(
    content: str, violations: list[Violation], *, model: str = "claude-opus-4-7"
) -> str:
    if not violations:
        return content
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    violations_text = "\n".join(
        f"- [{v.severity.upper()}] Section '{v.section}', Rule '{v.rule}': {v.description}"
        for v in violations
    )
    user_message = f"Violations to fix:\n{violations_text}\n\n---\n\nChapter:\n\n{content}"
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=_REWRITER_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
```

- [ ] **Step 4: Run — verify all rewriter tests PASS**

```bash
python -m pytest tests/test_thesis_rewriter.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/thesis_rewriter.py tests/test_thesis_rewriter.py
git commit -m "feat: add rewrite_chapter() with Claude API integration"
```

---

## Task 5: Loop — core logic

**Files:**
- Create: `scripts/thesis_loop.py`
- Create: `tests/test_thesis_loop.py`

- [ ] **Step 1: Write failing tests for `_run_chapter`**

Create `tests/test_thesis_loop.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock, patch
from scripts.thesis_scorer import ComplianceReport, Violation


def _report(score: int, violations=None) -> ComplianceReport:
    return ComplianceReport(score=score, violations=violations or [])


def _violation() -> Violation:
    return Violation("1.1", "citation_placeholder", "Missing citation", "warning")


@patch("scripts.thesis_loop.rewrite_chapter")
@patch("scripts.thesis_loop.score_chapter")
def test_chapter_already_passing_is_skipped(mock_score, mock_rewrite, tmp_path):
    chapter = tmp_path / "chapter1.md"
    chapter.write_text("# Content", encoding="utf-8")
    mock_score.return_value = _report(90)
    from scripts.thesis_loop import _run_chapter
    result = _run_chapter(chapter)
    assert result.status == "SKIP"
    mock_rewrite.assert_not_called()


@patch("scripts.thesis_loop.rewrite_chapter")
@patch("scripts.thesis_loop.score_chapter")
def test_chapter_improves_to_pass_and_file_overwritten(mock_score, mock_rewrite, tmp_path):
    chapter = tmp_path / "chapter1.md"
    chapter.write_text("# Content", encoding="utf-8")
    mock_score.side_effect = [
        _report(60, [_violation()]),
        _report(90),
    ]
    mock_rewrite.return_value = "# Fixed [CITATION: needed]"
    from scripts.thesis_loop import _run_chapter
    result = _run_chapter(chapter)
    assert result.status == "PASS"
    assert result.score_after == 90
    assert chapter.read_text(encoding="utf-8") == "# Fixed [CITATION: needed]"


@patch("scripts.thesis_loop.rewrite_chapter")
@patch("scripts.thesis_loop.score_chapter")
def test_no_regression_when_score_does_not_improve(mock_score, mock_rewrite, tmp_path):
    chapter = tmp_path / "chapter1.md"
    original = "# Content"
    chapter.write_text(original, encoding="utf-8")
    mock_score.side_effect = [
        _report(60, [_violation()]),
        _report(55),   # worse than original
        _report(55),
        _report(55),
    ]
    mock_rewrite.return_value = "# Worse rewrite"
    from scripts.thesis_loop import _run_chapter
    result = _run_chapter(chapter)
    assert chapter.read_text(encoding="utf-8") == original


@patch("scripts.thesis_loop.rewrite_chapter")
@patch("scripts.thesis_loop.score_chapter")
def test_dry_run_does_not_write_file(mock_score, mock_rewrite, tmp_path):
    chapter = tmp_path / "chapter1.md"
    original = "# Content"
    chapter.write_text(original, encoding="utf-8")
    mock_score.side_effect = [_report(60, [_violation()]), _report(90)]
    mock_rewrite.return_value = "# Fixed"
    from scripts.thesis_loop import _run_chapter
    _run_chapter(chapter, dry_run=True)
    assert chapter.read_text(encoding="utf-8") == original


@patch("scripts.thesis_loop.rewrite_chapter")
@patch("scripts.thesis_loop.score_chapter")
def test_truncated_revision_is_discarded(mock_score, mock_rewrite, tmp_path):
    chapter = tmp_path / "chapter1.md"
    original = "# Content " * 100   # ~1000 chars
    chapter.write_text(original, encoding="utf-8")
    mock_score.side_effect = [
        _report(60, [_violation()]),
        _report(90),
        _report(90),
        _report(90),
    ]
    mock_rewrite.return_value = "# Tiny"  # << 50% of 1000 chars
    from scripts.thesis_loop import _run_chapter
    result = _run_chapter(chapter)
    assert chapter.read_text(encoding="utf-8") == original


@patch("scripts.thesis_loop.rewrite_chapter")
@patch("scripts.thesis_loop.score_chapter")
def test_warn_status_when_max_iter_exhausted(mock_score, mock_rewrite, tmp_path):
    chapter = tmp_path / "chapter1.md"
    chapter.write_text("# Content", encoding="utf-8")
    mock_score.return_value = _report(60, [_violation()])
    mock_rewrite.return_value = "# Slightly better " * 20  # longer than original, above 50%
    from scripts.thesis_loop import _run_chapter
    result = _run_chapter(chapter)
    assert result.status == "WARN"
```

- [ ] **Step 2: Run — verify they FAIL**

```bash
python -m pytest tests/test_thesis_loop.py -v
```

Expected: `ImportError` — `scripts.thesis_loop` not defined.

- [ ] **Step 3: Create `scripts/thesis_loop.py`**

```python
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
```

- [ ] **Step 4: Run — verify all loop tests PASS**

```bash
python -m pytest tests/test_thesis_loop.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/thesis_loop.py tests/test_thesis_loop.py
git commit -m "feat: add chapter loop orchestrator with truncation guard and dry-run"
```

---

## Task 6: CLI, summary table, and git commit

**Files:**
- Modify: `scripts/thesis_loop.py`
- Modify: `tests/test_thesis_loop.py`

- [ ] **Step 1: Write failing test for summary table**

Add to `tests/test_thesis_loop.py`:

```python
import io
from scripts.thesis_loop import ChapterResult, _print_summary


def test_print_summary_shows_all_columns(capsys):
    results = [
        ChapterResult(Path("thesis/health_rl/chapter1_introduction.md"), 62, 91, 2, "PASS"),
        ChapterResult(Path("thesis/health_rl/chapter3_methodology.md"), 55, 83, 3, "WARN"),
    ]
    _print_summary(results)
    captured = capsys.readouterr().out
    assert "chapter1_introduction.md" in captured
    assert "PASS" in captured
    assert "WARN" in captured
    assert "62" in captured
    assert "91" in captured
```

- [ ] **Step 2: Run — verify it FAILS**

```bash
python -m pytest tests/test_thesis_loop.py::test_print_summary_shows_all_columns -v
```

Expected: `ImportError` — `_print_summary` not defined.

- [ ] **Step 3: Add `_print_summary`, `_commit_changes`, and `main` to `scripts/thesis_loop.py`**

Add after `_run_chapter`:

```python
import argparse
import subprocess


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
```

- [ ] **Step 4: Run — verify all tests PASS**

```bash
python -m pytest tests/test_thesis_loop.py tests/test_thesis_scorer.py tests/test_thesis_rewriter.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/thesis_loop.py tests/test_thesis_loop.py
git commit -m "feat: add CLI entry point, summary table, and git commit step"
```

---

## Task 7: API retry on failure

**Files:**
- Modify: `scripts/thesis_scorer.py`
- Modify: `scripts/thesis_rewriter.py`
- Modify: `tests/test_thesis_scorer.py`
- Modify: `tests/test_thesis_rewriter.py`

- [ ] **Step 1: Write failing test for scorer retry**

Add to `tests/test_thesis_scorer.py`:

```python
import time
from unittest.mock import MagicMock, patch, call
import anthropic as anthropic_lib


@patch("scripts.thesis_scorer.time.sleep")
@patch("scripts.thesis_scorer.anthropic.Anthropic")
def test_score_chapter_retries_once_on_api_error(mock_class, mock_sleep, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.side_effect = [
        anthropic_lib.APIError("rate limit", response=MagicMock(), body={}),
        MagicMock(content=[MagicMock(text='{"score": 75, "violations": []}')]),
    ]
    from scripts.thesis_scorer import score_chapter
    report = score_chapter("# Chapter")
    assert report.score == 75
    assert mock_client.messages.create.call_count == 2
    mock_sleep.assert_called_once_with(2)


@patch("scripts.thesis_scorer.time.sleep")
@patch("scripts.thesis_scorer.anthropic.Anthropic")
def test_score_chapter_returns_zero_after_two_failures(mock_class, mock_sleep, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.side_effect = anthropic_lib.APIError(
        "error", response=MagicMock(), body={}
    )
    from scripts.thesis_scorer import score_chapter
    report = score_chapter("# Chapter")
    assert report.score == 0
    assert report.violations[0].rule == "parse_error"
```

- [ ] **Step 2: Run — verify they FAIL**

```bash
python -m pytest tests/test_thesis_scorer.py::test_score_chapter_retries_once_on_api_error -v
```

Expected: FAIL — `score_chapter` does not retry yet.

- [ ] **Step 3: Add retry to `score_chapter` in `scripts/thesis_scorer.py`**

Add `import time` at the top. Replace the `score_chapter` function with:

```python
import time


def score_chapter(content: str, *, model: str = "claude-opus-4-7") -> ComplianceReport:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user_message = f"ITC Style Guide:\n\n{_STYLE_GUIDE}\n\n---\n\nChapter to score:\n\n{content}"
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                system=_SCORER_SYSTEM,
                messages=[{"role": "user", "content": user_message}],
            )
            return _parse_response(response.content[0].text)
        except anthropic.APIError:
            if attempt == 0:
                time.sleep(2)
    return ComplianceReport(
        score=0,
        violations=[
            Violation(
                section="",
                rule="parse_error",
                description="API call failed after retry",
                severity="error",
            )
        ],
    )
```

- [ ] **Step 4: Add retry to `rewrite_chapter` in `scripts/thesis_rewriter.py`**

Add `import time` at the top. Replace `rewrite_chapter` with:

```python
import time


def rewrite_chapter(
    content: str, violations: list[Violation], *, model: str = "claude-opus-4-7"
) -> str:
    if not violations:
        return content
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    violations_text = "\n".join(
        f"- [{v.severity.upper()}] Section '{v.section}', Rule '{v.rule}': {v.description}"
        for v in violations
    )
    user_message = f"Violations to fix:\n{violations_text}\n\n---\n\nChapter:\n\n{content}"
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=8192,
                system=_REWRITER_SYSTEM,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except anthropic.APIError:
            if attempt == 0:
                time.sleep(2)
    return content  # fall back to original on repeated failure
```

- [ ] **Step 5: Run full test suite — verify all PASS**

```bash
python -m pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/thesis_scorer.py scripts/thesis_rewriter.py tests/test_thesis_scorer.py
git commit -m "feat: add API retry with 2s backoff to scorer and rewriter"
```

---

## Task 8: End-to-end dry run validation

No new code — verify the full pipeline works against real chapter files.

**Prerequisite:** `ANTHROPIC_API_KEY` must be set in your environment.

- [ ] **Step 1: Set API key**

```bash
export ANTHROPIC_API_KEY=<your-key>
```

- [ ] **Step 2: Run dry-run against all chapters**

```bash
python scripts/thesis_loop.py --dry-run
```

Expected output (approximate):
```
Processing chapter1_introduction.md...
Processing chapter2_literature_review.md...
Processing chapter2_presentation_of_project.md...
Processing chapter3_methodology.md...
Processing chapter4_project_analysis.md...
Processing chapter4_results.md...
Processing chapter5_conclusion.md...

Chapter                                        Before After Iter Status
-----------------------------------------------------------------------
chapter1_introduction.md                           72    72    0   SKIP
chapter2_literature_review.md                      58    58    0   SKIP
...
```

- [ ] **Step 3: Confirm no files were modified**

```bash
git diff --stat
```

Expected: no output (dry run writes nothing).

- [ ] **Step 4: Run for real (writes files)**

```bash
python scripts/thesis_loop.py
```

Expected: chapters scoring below 85 are rewritten and committed automatically.

- [ ] **Step 5: Inspect the git log**

```bash
git log --oneline -5
```

Expected: a commit with message `style: auto-fix ITC compliance violations` appears if any chapter was improved.

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| `Violation` + `ComplianceReport` dataclasses | Task 1 |
| `_parse_response` JSON parsing | Task 2 |
| `score_chapter()` Claude API call | Task 3 |
| `rewrite_chapter()` Claude API call | Task 4 |
| Loop: score → rewrite → re-score → keep if improved | Task 5 |
| Truncation guard (< 50% length) | Task 5 |
| Dry-run flag | Task 5 + Task 6 |
| Summary table | Task 6 |
| Git commit of changed chapters | Task 6 |
| API retry with 2s backoff | Task 7 |
| End-to-end validation | Task 8 |

All spec requirements covered. No gaps.
