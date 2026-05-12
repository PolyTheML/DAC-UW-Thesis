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
