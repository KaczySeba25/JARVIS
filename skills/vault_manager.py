"""Secure credential vault using Windows DPAPI; values are never written as plaintext."""
import json
try:
    from secret_store import get, save, status, metadata, delete, rotate
except ImportError:
    from agent.secret_store import get, save, status, metadata, delete, rotate
def run(action_data=None):
    """Use JSON actions save/get_metadata/status/delete.

    Secret values are intentionally never returned. Trusted connector code may
    call agent.secret_store.get() directly inside the same process.
    """
    try:
        if isinstance(action_data, dict): data = action_data
        else:
            raw = str(action_data or "").strip()
            data = json.loads(raw) if raw.startswith("{") else {"action": raw}
        action = str(data.get("action", "")).lower()
        if action == "save":
            result = save(data.get("service"), data.get("secret"), data.get("username", ""), data.get("metadata", {}))
            return {"saved": True, "service": result["service"], "secret_returned": False}
        if action == "rotate":
            return rotate(data.get("service"), data.get("secret"), data.get("username"), data.get("metadata"))
        if action in {"get", "get_metadata"}:
            return metadata(data.get("service"))
        if action == "delete": return delete(data.get("service"))
        if action == "status": return status()
        return {"error":"use JSON action save|rotate|get_metadata|status|delete"}
    except Exception as exc: return {"error":type(exc).__name__, "secret_returned": False}
