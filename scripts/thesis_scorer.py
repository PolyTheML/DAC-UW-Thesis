from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Violation:
    section: str
    rule: str
    description: str
    severity: Literal["error", "warning"]


@dataclass
class ComplianceReport:
    score: int
    violations: list[Violation] = field(default_factory=list)
    pass_threshold: int = 85

    @property
    def passed(self) -> bool:
        return self.score >= self.pass_threshold


def _parse_response(json_str: str) -> ComplianceReport:
    """Parse JSON response from Claude API into a ComplianceReport.

    Args:
        json_str: JSON string containing score and violations list

    Returns:
        ComplianceReport with parsed data, or score=0 with parse_error on failure
    """
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
