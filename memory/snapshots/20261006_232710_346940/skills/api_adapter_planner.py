"""Przygotowanie bezpiecznego planu adaptera API."""
try:
    from future_agent_capabilities import execute
except ImportError:
    from agent.future_agent_capabilities import execute

def run(argument=None):
    """Run a local, read-only capability contract."""
    return execute("api_adapter_planner", argument)
