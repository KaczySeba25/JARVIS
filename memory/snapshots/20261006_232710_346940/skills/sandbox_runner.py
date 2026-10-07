"""Planowanie izolowanego testu kodu bez aktywacji."""
try:
    from meta_capabilities import execute
except ImportError:
    from agent.meta_capabilities import execute

def run(argument=None):
    """Run a local, read-only meta-capability contract."""
    return execute("sandbox_runner", argument)
