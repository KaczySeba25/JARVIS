"""Create one researched Jarvis skill; refuses the retired hollow bulk builder."""
from __future__ import annotations

import json

try:
    from skill_builder import build_all, build_skill
except ImportError:
    from agent.skill_builder import build_all, build_skill


def run(argument=None):
    """JSON action create {name,goal,python_code}; build_all is intentionally disabled."""
    raw = str(argument or "").strip()
    if raw.lower() in {"build_all", "confirm_build_all"}:
        return build_all()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"promoted": False, "reason": "Podaj JSON: {action:create,name,goal,python_code}."}
    if not isinstance(data, dict) or data.get("action") != "create":
        return {"promoted": False, "reason": "Dozwolone działanie: create."}
    return build_skill(str(data.get("name", "")), str(data.get("goal", "")), str(data.get("python_code", "")))
