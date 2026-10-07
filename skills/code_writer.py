"""Improve a Jarvis skill through research, validation and reversible promotion."""
try:
    from self_improvement import improve
except ImportError:
    from agent.self_improvement import improve

def run(action_data: str):
    """Input format: skill_name|goal|python_code (or skill_name|python_code)."""
    parts = str(action_data or "").split("|", 2)
    if len(parts) < 2:
        return {"promoted": False, "reason": "Użyj formatu nazwa|cel|kod albo nazwa|kod."}
    if len(parts) == 3:
        name, goal, code = (part.strip() for part in parts)
    else:
        name, code = (part.strip() for part in parts)
        goal = f"Sprawdź i ulepsz umiejętność Jarvisa {name}"
    return improve(name, goal, code)
