"""Wyszukiwanie i ocena publicznej dokumentacji API."""
try:
    from future_agent_capabilities import execute
except ImportError:
    from agent.future_agent_capabilities import execute
try:
    from research_engine import search
except ImportError:
    from agent.research_engine import search

def run(argument=None):
    """Run a local, read-only capability contract."""
    query=str(argument or "").strip()
    return {**execute("api_discovery", query), "sources": search(query + " official API documentation", 5) if query else []}
