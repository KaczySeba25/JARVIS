"""Generowanie testów kontraktowych dla przyszłych agentów."""
try:
    from future_agent_capabilities import execute
except ImportError:
    from agent.future_agent_capabilities import execute

def run(argument=None):
    """Run a local, read-only capability contract."""
    return execute("agent_test_harness", argument)
