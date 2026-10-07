"""Manage explicit local user preferences."""
try:
    from user_profile import load, update
except ImportError:
    from agent.user_profile import load, update

def run(command: str = "show"):
    parts = (command or "show").split("|", 1)
    if parts[0] == "show": return str(load())
    if parts[0] == "set" and len(parts) == 2 and "=" in parts[1]:
        key, value = parts[1].split("=", 1)
        return update(key, value)
    return "Użycie: show lub set|pole=wartość"
