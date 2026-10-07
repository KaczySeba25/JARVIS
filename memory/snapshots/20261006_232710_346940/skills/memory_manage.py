"""Review, edit, and delete Jarvis's local long-term memories."""
from __future__ import annotations

import json

try:
    from memory_store import forget, list_memories, update_memory
except ImportError:
    from agent.memory_store import forget, list_memories, update_memory


def run(request):
    """JSON actions: list, edit {id,content,category?}, delete {id}."""
    try:
        data = json.loads(request) if isinstance(request, str) else request
        if not isinstance(data, dict):
            return {"ok": False, "error": "expected_json_object"}
        action = str(data.get("action", "list")).lower()
        if action == "list":
            return {"items": list_memories(data.get("limit", 100), data.get("category"))}
        if action == "edit":
            changed = update_memory(data.get("id"), data.get("content", ""), data.get("category"))
            return {"updated": changed, "id": data.get("id")}
        if action == "delete":
            removed = forget(data.get("id"))
            return {"deleted": removed, "id": data.get("id")}
        return {"ok": False, "error": "unsupported_action", "allowed": ["list", "edit", "delete"]}
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
