"""Quality score and stop conditions for Jarvis results."""
try:
    from governance import evaluate
except ImportError:
    from agent.governance import evaluate

def run(data: str):
    parts = (data or "").split("|", 2)
    if len(parts) < 2: return "Użycie: task|result|confidence"
    confidence = float(parts[2]) if len(parts) == 3 else 0.7
    quality = evaluate(parts[0], parts[1], confidence)
    return f"correctness={quality.correctness:.2f}; completeness={quality.completeness:.2f}; confidence={quality.confidence:.2f}; risk={quality.risk}; review={quality.needs_review}"
