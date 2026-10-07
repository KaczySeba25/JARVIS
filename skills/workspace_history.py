"""Review changes made by Jarvis in workspace and restore a chosen version."""
from __future__ import annotations

import json

try:
    from workspace_history import list_versions, restore
except ImportError:
    from agent.workspace_history import list_versions, restore


def run(request):
    """JSON: {action:'list',path:'project/file.py'} or {action:'restore',version_id:'...'}"""
    try:
        data = json.loads(request) if isinstance(request, str) else request
        if not isinstance(data, dict):
            return {"ok": False, "error": "expected_json_object"}
        action = str(data.get("action", "list")).lower()
        if action == "list":
            return {"versions": list_versions(data.get("path", ""), data.get("limit", 50))}
        if action == "restore":
            return restore(data.get("version_id", ""))
        return {"ok": False, "error": "unsupported_action", "allowed": ["list", "restore"]}
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
