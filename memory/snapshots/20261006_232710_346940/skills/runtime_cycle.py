"""Runs the integrated supervised quality cycle for a Jarvis task."""
try:
    from runtime_integration import cycle
except ImportError:
    from agent.runtime_integration import cycle
def run(argument=None): return cycle(argument)
