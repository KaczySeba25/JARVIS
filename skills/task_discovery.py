"""Discover unknowns and research questions for any new domain task."""
import json
try:
    from task_discovery import discover
except ImportError:
    from agent.task_discovery import discover

def run(goal: str):
    return json.dumps(discover(goal).__dict__, ensure_ascii=False, indent=2)
