"""Wykrywanie prób zmiany zasad systemu."""
try:
    from advanced_capabilities import execute
except ImportError:
    from agent.advanced_capabilities import execute

def run(argument=None):
    """Execute a deterministic, read-only primitive and return structured data."""
    return execute("prompt_injection_firewall", argument)

