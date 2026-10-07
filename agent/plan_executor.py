"""Validated multi-step plan executor with explicit stop conditions."""
from __future__ import annotations
from dataclasses import dataclass
try:
    from .structured_plan import Plan, Step
except ImportError:
    from structured_plan import Plan, Step

@dataclass
class StepResult:
    objective: str
    status: str
    result: str

class PlanExecutor:
    def __init__(self, run_tool, confirm):
        self.run_tool = run_tool
        self.confirm = confirm

    def execute(self, plan: Plan):
        plan.validate()
        results = []
        for step in plan.steps:
            if step.risk in {"high", "critical"} and not self.confirm(step):
                step.status = "blocked"
                results.append(StepResult(step.objective, "blocked", "Brak potwierdzenia."))
                break
            try:
                value = self.run_tool(step.tool, step.argument) if step.tool else "Krok analityczny wymaga modelu."
                step.status = "done"
                results.append(StepResult(step.objective, "done", str(value)))
            except Exception as exc:
                step.status = "failed"
                results.append(StepResult(step.objective, "failed", str(exc)))
                break
        return results
