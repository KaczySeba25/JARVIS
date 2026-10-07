"""Start, inspect, or stop an approved demo created in Jarvis workspace."""
from __future__ import annotations

import json

try:
    from workspace_process_manager import execute
except ImportError:
    from agent.workspace_process_manager import execute


def run(request):
    """JSON: start {project,entry}, status {run_id}, or stop {run_id}."""
    try:
        return execute(request)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
