"""Walidacja kontraktu endpointów bez wywołań produkcyjnych."""
try:
    from future_agent_capabilities import execute
except ImportError:
    from agent.future_agent_capabilities import execute

def run(argument=None):
    """Run a local, read-only capability contract."""
    return execute("api_contract_validator", argument)
