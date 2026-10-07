"""Persistent, local primitives for supervised task management and recovery."""
from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "memory" / "autonomy_state.json"
_LOCK = threading.RLock()


def _read():
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write(data):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(STATE)


def execute(name, argument=None):
    value = "" if argument is None else str(argument).strip()
    with _LOCK:
        state = _read()
        if name == "task_queue":
            queue = state.setdefault("queue", [])
            existing = next((item for item in queue if item.get("task") == value and item.get("status") == "pending"), None)
            if existing:
                return {"queued": False, "duplicate": True, "size": len(queue)}
            queue.append({"task": value, "priority": 0, "status": "pending", "created": time.time()})
            _write(state)
            return {"queued": True, "size": len(queue)}
        if name == "checkpoint_manager":
            try:
                from backup import snapshot
                path = snapshot()
                checkpoint = {"label": value or "manual", "created": time.time(), "snapshot": path, "available": True}
            except Exception as exc:
                checkpoint = {"label": value or "manual", "created": time.time(), "available": False, "error": type(exc).__name__}
            state.setdefault("checkpoints", []).append(checkpoint)
            state["checkpoints"] = state["checkpoints"][-50:]
            _write(state)
            return checkpoint
        if name == "rollback_manager":
            checkpoints = state.get("checkpoints", [])
            return {"available": any(item.get("available") for item in checkpoints), "last_checkpoint": next((item for item in reversed(checkpoints) if item.get("available")), None), "automatic_file_restore": False}
        if name == "resource_monitor":
            import shutil
            return {"disk_free_gb": round(shutil.disk_usage(ROOT).free / 1024**3, 2), "timestamp": time.time()}
        if name == "emergency_stop":
            if value.lower() == "status":
                return {"stop_requested": state.get("stop_requested", False)}
            if value.lower() == "reset":
                state["stop_requested"] = False
                _write(state)
                return {"stop_requested": False}
            state["stop_requested"] = True
            _write(state)
            return {"stop_requested": True}
        if name == "result_verifier":
            try:
                data = json.loads(value)
            except json.JSONDecodeError:
                data = None
            if isinstance(data, dict) and data.get("expected") is not None and data.get("observed") is not None:
                verified = data["expected"] == data["observed"]
                return {"verified": verified, "review_required": not verified, "basis": "exact_value_comparison"}
            failed = bool(re.search(r"(?i)\b(error|failed|błąd|nie udało się|anulowano)\b", value))
            return {"verified": False, "review_required": True, "failure_marker_found": failed, "basis": "no_independent_evidence"}
        if name == "semantic_memory":
            try:
                from memory_store import recall
                return {"query": value, "matches": recall(value, limit=6)}
            except Exception as exc:
                return {"query": value, "matches": [], "error": type(exc).__name__}
        if name == "error_learning":
            safe = re.sub(r"(?i)(?:gsk_|sk-[A-Za-z0-9_-]{12,}|(?:password|token|api[_-]?key|secret)\s*[:=]\s*\S+)", "[REDACTED]", value)
            parts = safe.split("|", 2)
            try:
                from governance import save_error
                save_error(parts[0][:300], parts[1][:300] if len(parts) > 1 else "cause_not_provided", parts[2][:500] if len(parts) > 2 else "fix_not_provided")
                return {"recorded": True, "error": parts[0]}
            except Exception as exc:
                return {"recorded": False, "error": type(exc).__name__}
        if name == "permission_manager":
            blocked = any(word in value.lower() for word in ("delete", "publish", "payment", "buy", "send"))
            return {"operation": value, "allowed": not blocked, "requires_confirmation": blocked}
        if name == "execution_report":
            return {"task": value, "status": "reported_not_verified", "timestamp": time.time()}
        if name == "knowledge_freshness":
            return {"freshness": "unknown", "requires_research": True, "subject": value}
        if name == "autonomy_test":
            return {"checks": ["state persistence", "bounded retries", "emergency stop", "checkpoint availability"], "status": "not_run"}
    raise ValueError(name)
