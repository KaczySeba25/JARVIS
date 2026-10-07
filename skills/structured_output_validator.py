"""Walidacja danych względem prostego schematu."""
try:
    from advanced_capabilities import execute
except ImportError:
    from agent.advanced_capabilities import execute

def run(argument=None):
    """Execute a deterministic, read-only primitive and return structured data."""
    return execute("structured_output_validator", argument)

