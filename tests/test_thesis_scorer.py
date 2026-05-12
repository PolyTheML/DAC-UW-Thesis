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
