"""Register and inspect explicit API/OAuth/browser connectors."""
from __future__ import annotations
import json
try:
    from connector_registry import save, list_all, catalog, add_custom, ensure
except ImportError:
    from agent.connector_registry import save, list_all, catalog, add_custom, ensure
def run(argument=None):
    try:
        data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
        action = data.get("action", "list")
        if action == "list": return {"ok": True, **list_all()}
        if action == "catalog": return {"ok": True, "items": catalog(data.get("query", ""))}
        if action == "ensure": return {"ok": True, **ensure(data.get("service"), data.get("kind", "api"), data.get("scopes", []), data.get("endpoint", ""))}
        if action == "register": return {"ok": True, **save(data.get("service"), data.get("kind", "browser"), data.get("scopes", []), data.get("endpoint", ""))}
        if action == "create": return {"ok": True, **add_custom(data.get("service"), data.get("kind", "api"), data.get("scopes", []), data.get("endpoint", ""))}
        return {"ok": False, "error": "unsupported_action", "allowed": ["list", "catalog", "ensure", "register", "create"]}
    except Exception as exc: return {"ok": False, "error": type(exc).__name__}
