"""Expert mission manager backed by a durable SQLite dependency graph."""
from __future__ import annotations
import json
try:
    from agent import mission_runtime
except ImportError:
    import mission_runtime

RISK_LEVEL = "low"

def _data(argument):
    if isinstance(argument, dict):
        return argument
    raw = str(argument or "").strip()
    try:
        return json.loads(raw) if raw else {"action": "list"}
    except json.JSONDecodeError:
        action, _, value = raw.partition("|")
        return {"action": action or "list", "goal": value}

def run(argument=None):
    data = _data(argument)
    action = str(data.get("action", "list")).lower()
    if action == "create":
        return mission_runtime.create(data.get("goal", ""), data.get("success_criteria", ""), data.get("priority", 0), data.get("metadata", {}), data.get("steps", []))
    if action == "add_step":
        return mission_runtime.add_step(data["mission_id"], data)
    if action in {"status", "get"}:
        return mission_runtime.get(data.get("mission_id"), include_steps=True)
    if action == "list":
        return mission_runtime.list_missions(data.get("status"), data.get("limit", 30))
    if action == "ready":
        return mission_runtime.ready_steps(data["mission_id"])
    if action == "update_step":
        return mission_runtime.update_step(data["mission_id"], data["step_key"], data.get("status", "done"), data.get("result"), data.get("error", ""), bool(data.get("increment_attempt", False)))
    if action == "evidence":
        return mission_runtime.add_evidence(data["mission_id"], data.get("kind", "result"), data.get("value", ""), bool(data.get("verified", False)), data.get("step_id", ""))
    if action in {"pause", "resume", "stop", "cancel"}:
        return mission_runtime.set_status(data["mission_id"], {"pause": "paused", "resume": "executing", "stop": "cancelled", "cancel": "cancelled"}[action])
    return {"ok": False, "error": "unsupported_action", "allowed": ["create", "add_step", "status", "list", "ready", "update_step", "evidence", "pause", "resume", "stop"]}
