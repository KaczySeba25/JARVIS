"""Run a supervised research-to-draft-to-test improvement cycle."""
import json
try:
    from self_improvement import improve
except ImportError:
    from agent.self_improvement import improve

def run(command: str):
    parts = (command or "").split("|", 2)
    if len(parts) != 3:
        return "Użycie: nazwa_skilla|cel|kod_python"
    return json.dumps(improve(parts[0].strip(), parts[1].strip(), parts[2]), ensure_ascii=False, indent=2)
