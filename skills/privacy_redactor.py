"""Redacts common personal data before it enters logs or reports."""
import re
def run(argument=None):
    """Return redacted text without external side effects."""
    value = str(argument or "")
    value = re.sub(r"[\w.+-]+@[\w.-]+\.\w+", "[EMAIL]", value)
    value = re.sub(r"\b\d{9,}\b", "[NUMBER]", value)
    value = re.sub(r"(?:gsk_|sk-|api[_-]?key|password|token)\s*[=:]?\s*[^\s,;]+", "[SECRET]", value, flags=re.I)
    return {"text": value, "changed": value != str(argument or "")}
