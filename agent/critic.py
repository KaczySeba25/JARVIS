"""Deterministic pre/post execution critic."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Critique:
    approved: bool
    reasons: tuple[str, ...]
    score: float

def critique_plan(plan):
    reasons = []
    if not plan.goal.strip(): reasons.append("Brak celu.")
    if not plan.steps: reasons.append("Plan nie ma kroków.")
    if len(plan.steps) > 20: reasons.append("Plan jest zbyt długi.")
    return Critique(not reasons, tuple(reasons), 1.0 if not reasons else 0.2)

def critique_results(results):
    reasons = [r.result for r in results if r.status in {"failed", "blocked"}]
    completed = sum(r.status == "done" for r in results)
    score = completed / len(results) if results else 0.0
    return Critique(not reasons and score == 1.0, tuple(reasons), score)
