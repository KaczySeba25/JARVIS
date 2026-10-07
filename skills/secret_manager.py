"""Jarvis foundation skill: secret_manager."""
def run(argument=None):
    """Deterministic local-only contract; no external side effects."""
    return {'delegated_to': 'agent.secret_store', 'plaintext_output': False}
