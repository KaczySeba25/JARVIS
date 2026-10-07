"""Jarvis foundation skill: deployment_planner."""
def run(argument=None):
    """Deterministic local-only contract; no external side effects."""
    return {'deployment': 'supervised_local', 'live': False, 'rollback_required': True}
