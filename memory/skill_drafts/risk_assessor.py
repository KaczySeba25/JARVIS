"""Jarvis foundation skill: risk_assessor."""
def run(argument=None):
    """Deterministic local-only contract; no external side effects."""
    return {'risk': 'review_required', 'categories': ['technical', 'privacy', 'operational']}
