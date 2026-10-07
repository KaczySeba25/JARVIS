"""Validated plan representation independent of model wording."""
from dataclasses import dataclass, field

@dataclass
class Step:
    objective: str
    tool: str | None = None
    argument: str | None = None
    risk: str = "low"
    status: str = "pending"

@dataclass
class Plan:
    goal: str
    steps: list[Step] = field(default_factory=list)
    confidence: float = 0.0

    def validate(self):
        if not self.goal.strip(): raise ValueError("Plan musi mieć cel.")
        if len(self.steps) > 20: raise ValueError("Plan ma zbyt wiele kroków.")
        for step in self.steps:
            if step.risk not in {"low", "medium", "high", "critical"}: raise ValueError("Nieznany poziom ryzyka.")
        return True
