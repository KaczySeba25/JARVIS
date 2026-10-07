"""Wersjonowanie, migracje i kompatybilność skillów."""
try:
    from future_agent_capabilities import execute
except ImportError:
    from agent.future_agent_capabilities import execute

def run(argument=None):
    """Run a local, read-only capability contract."""
    return execute("skill_version_manager", argument)
