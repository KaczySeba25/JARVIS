"""Porównywanie planu z rezultatem i wykrywanie lekcji."""
try:
    from meta_capabilities import execute
except ImportError:
    from agent.meta_capabilities import execute

def run(argument=None):
    """Run a local, read-only meta-capability contract."""
    return execute("learning_loop", argument)
