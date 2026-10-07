"""Audytuje jakość i kompletność wszystkich dostępnych skillów Jarvisa."""
from pathlib import Path

try:
    from capability_audit import report
except ImportError:
    from agent.capability_audit import report


def run(argument=None):
    """Return a structured, read-only capability quality report."""
    root = Path(__file__).resolve().parent
    data = report(root)
    if argument and str(argument).lower() == "summary":
        return {key: data[key] for key in ("total", "passed", "review")}
    return data
