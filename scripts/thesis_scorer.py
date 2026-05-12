from __future__ import annotations

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
