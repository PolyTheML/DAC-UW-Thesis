from unittest.mock import MagicMock, patch
import anthropic as anthropic_lib

import pytest

from scripts.thesis_scorer import Violation, ComplianceReport, _parse_response


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
    assert report.violations[0].rule == "parse_error"


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


@patch("scripts.thesis_scorer.time.sleep")
@patch("scripts.thesis_scorer.anthropic.Anthropic")
def test_score_chapter_retries_once_on_api_error(mock_class, mock_sleep, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_class.return_value = mock_client
    mock_client.messages.create.side_effect = [
        anthropic_lib.APIError("rate limit", request=MagicMock(), body={}),
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
        "error", request=MagicMock(), body={}
    )
    from scripts.thesis_scorer import score_chapter
    report = score_chapter("# Chapter")
    assert mock_client.messages.create.call_count == 2
    assert report.score == 0
    assert report.violations[0].rule == "parse_error"
