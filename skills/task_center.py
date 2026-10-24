"""Task center: durable task status, timeline and resumable work."""
from __future__ import annotations
import json
try:
    import task_runtime
except ImportError:
    from agent import task_runtime

def run(argument=None):
    try:
        data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
        task_id = data.get("task_id")
        if data.get("action", "status") == "timeline":
            return {"ok": True, "events": task_runtime.recent(int(data.get("limit", 50)), task_id)}
        if task_id:
            return {"ok": True, "task": task_runtime.get(task_id), "events": task_runtime.recent(50, task_id)}
        return {"ok": True, "pending_approval": task_runtime.latest_pending(), "waiting_user": task_runtime.latest_waiting_user(), "events": task_runtime.recent(30)}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}
