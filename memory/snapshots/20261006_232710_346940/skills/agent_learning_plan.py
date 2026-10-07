"""Planowanie nauki i luk kompetencyjnych agenta."""
try:
    from future_agent_capabilities import execute
except ImportError:
    from agent.future_agent_capabilities import execute

def run(argument=None):
    """Run a local, read-only capability contract."""
    return execute("agent_learning_plan", argument)
