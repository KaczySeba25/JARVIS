"""Search Jarvis private local memories."""
try:
    from memory_store import recall
except ImportError:
    from agent.memory_store import recall

def run(query_string: str):
    """Search by topic; optional format: category|query."""
    raw = str(query_string or "").strip()
    category, separator, query = raw.partition("|")
    if not separator:
        category, query = None, raw
    matches = recall(query, category=category or None)
    return {"query": query, "matches": matches, "count": len(matches)}
