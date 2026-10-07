"""Jarvis foundation skill: rate_limit_manager."""
def run(argument=None):
    """Deterministic local-only contract; no external side effects."""
    return {'allowed': True, 'mode': 'local_policy', 'calls': 0}
