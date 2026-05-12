from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

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


def score_chapter(content: str, *, model: str = "claude-opus-4-7") -> ComplianceReport:
    """Score a chapter against ITC style guide. Requires ANTHROPIC_API_KEY env var."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user_message = f"ITC Style Guide:\n\n{_STYLE_GUIDE}\n\n---\n\nChapter to score:\n\n{content}"
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=_SCORER_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )
    return _parse_response(response.content[0].text)
