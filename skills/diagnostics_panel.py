"""Generates a local diagnostics panel without network access."""
try:
    from runtime_integration import dashboard
except ImportError:
    from agent.runtime_integration import dashboard
def run(argument=None): return {"path":dashboard(),"network":False}
