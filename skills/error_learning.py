"""Uczenie się na błędach bez sekretów."""
try:
    from autonomy_layers import execute
except ImportError:
    from agent.autonomy_layers import execute

def run(argument=None):
    """Run the local deterministic autonomy primitive."""
    return execute("error_learning", argument)
