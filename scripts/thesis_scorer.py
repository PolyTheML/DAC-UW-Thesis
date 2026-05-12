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
