"""Human-like local memory manager: user, episodic, procedural and knowledge memories."""
from __future__ import annotations
import json
try:
    from agent.memory_store import remember, recall, list_memories, forget, update_memory
except ImportError:
    from memory_store import remember, recall, list_memories, forget, update_memory

RISK_LEVEL = "medium"
CATEGORIES = {"user", "episodic", "procedural", "knowledge", "fact", "research_lesson"}

def run(argument=None):
    data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
    action = str(data.get("action", "list")).lower()
    category = str(data.get("category", ""))
    if category == "user": category = "user_preference"
    if category == "episodic": category = "episode"
    if category == "procedural": category = "procedure"
    if category == "knowledge": category = "knowledge"
    if action in {"save", "remember"}:
        return remember(data.get("content", ""), category=category or "fact", source=str(data.get("source", "jarvis"))[:120], confidence=float(data.get("confidence", 0.7)))
    if action in {"search", "recall"}:
        return {"query": data.get("query", ""), "matches": recall(data.get("query", ""), limit=data.get("limit", 10), category=category or None)}
    if action == "list":
        return {"memories": list_memories(limit=data.get("limit", 50), category=category or None), "categories": sorted(CATEGORIES)}
    if action == "update":
        return {"updated": update_memory(int(data["id"]), data.get("content", ""), category or None)}
    if action == "forget":
        return {"forgotten": forget(int(data["id"]))}
    return {"ok": False, "error": "unsupported_action", "allowed": ["save", "search", "list", "update", "forget"]}
