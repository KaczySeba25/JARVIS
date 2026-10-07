"""Deterministic critic for tool results before Jarvis reports success."""
def run(result: str):
    text = result or ""
    warnings = []
    if "Błąd" in text or "error" in text.lower(): warnings.append("wynik zawiera błąd")
    if "PAPER ONLY" not in text and any(word in text.lower() for word in ("order", "kup", "sprzed")):
        warnings.append("nie potwierdzono, że operacja jest paper-only")
    if not text.strip(): warnings.append("pusty wynik")
    return "CRITIC: " + ("OK" if not warnings else "UWAGA: " + "; ".join(warnings))
