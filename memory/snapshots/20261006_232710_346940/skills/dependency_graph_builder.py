"""Budowanie grafu zależności zadań."""
try:
    from advanced_capabilities import execute
except ImportError:
    from agent.advanced_capabilities import execute

def run(argument=None):
    """Execute a deterministic, read-only primitive and return structured data."""
    return execute("dependency_graph_builder", argument)

