"""Jarvis foundation skill: auto_recovery_handler."""
def run(argument=None):
    """Deterministic local-only contract; no external side effects."""
    return {'actions': ['capture_error', 'bounded_retry', 'checkpoint_review']}
