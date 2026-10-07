"""Safe skill drafting, validation and explicitly gated promotion."""
import json
try:
    from skill_lifecycle import create_draft, validate, promote
except ImportError:
    from agent.skill_lifecycle import create_draft, validate, promote

def run(command: str):
    parts = (command or "list").split("|", 2)
    action = parts[0].lower()
    if action == "draft" and len(parts) == 3:
        return f"Draft zapisany: {create_draft(parts[1], parts[2])}"
    if action == "validate" and len(parts) >= 2:
        return json.dumps(validate(parts[1]), ensure_ascii=False, indent=2)
    if action == "promote" and len(parts) >= 2:
        return promote(parts[1], confirm=len(parts) == 3 and parts[2].lower() == "confirm")
    return "Użycie: draft|nazwa|kod lub validate|nazwa lub promote|nazwa|confirm"
