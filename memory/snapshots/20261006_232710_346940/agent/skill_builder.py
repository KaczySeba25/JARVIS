"""Research-backed builder for one useful, reviewable Jarvis skill at a time."""
from __future__ import annotations


def build_all() -> dict:
    """The old bulk builder created hollow placeholders; it is deliberately disabled."""
    return {"created": 0, "status": "disabled", "reason": "Bulk placeholder generation is retired. Describe one real capability so it can be researched, validated, and versioned."}


def build_skill(name: str, goal: str, code: str) -> dict:
    """Build a single managed skill through the researched self-improvement lifecycle."""
    try:
        from self_improvement import improve
    except ImportError:
        from agent.self_improvement import improve
    if not goal or not code:
        return {"promoted": False, "reason": "goal_and_python_code_required"}
    return improve(name, goal, code)
