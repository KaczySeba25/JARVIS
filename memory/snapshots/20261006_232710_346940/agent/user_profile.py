"""Explicit, local user preferences used to personalize Jarvis."""
import json
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "memory" / "user_profile.json"
DEFAULT = {
    "language": "pl",
    "planning_style": "deep_analysis_then_plan_approval",
    "execution_style": "autonomous_within_approved_scope",
    "communication_style": "adaptive_plain_language",
}

def load():
    if not FILE.exists(): return DEFAULT.copy()
    try:
        stored = json.loads(FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT.copy()
    if not isinstance(stored, dict):
        return DEFAULT.copy()
    return {**DEFAULT, **{key: str(value)[:200] for key, value in stored.items() if key in DEFAULT and isinstance(value, (str, int, float, bool))}}

def update(key, value):
    data = load()
    if key not in DEFAULT: return "Nieznane pole profilu."
    if not isinstance(value, (str, int, float, bool)):
        return "Wartość musi być krótkim tekstem lub prostą liczbą."
    data[key] = str(value)[:200]
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return "Profil użytkownika zaktualizowany."
