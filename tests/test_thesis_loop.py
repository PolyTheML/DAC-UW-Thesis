import io
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


def test_print_summary_shows_all_columns(capsys):
    from scripts.thesis_loop import ChapterResult, _print_summary
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
