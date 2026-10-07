"""Przygotowanie kontekstu przekazania człowiekowi."""
try:
    from advanced_capabilities import execute
except ImportError:
    from agent.advanced_capabilities import execute

def run(argument=None):
    """Execute a deterministic, read-only primitive and return structured data."""
    return execute("human_handoff_manager", argument)

