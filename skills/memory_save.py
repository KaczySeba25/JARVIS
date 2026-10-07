"""Save private Jarvis memories to the local SQLite database."""
try:
    from memory_store import remember
except ImportError:
    from agent.memory_store import remember

def run(data_string: str):
    """Save content locally; optional format: category|content."""
    raw = str(data_string or "").strip()
    category, separator, content = raw.partition("|")
    if not separator:
        category, content = "fact", raw
    if not content.strip():
        return {"saved": False, "reason": "empty_memory"}
    return remember(content, category=category.strip() or "fact")
