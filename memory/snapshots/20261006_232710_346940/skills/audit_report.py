"""Summarize the local audit log."""
from pathlib import Path
from collections import Counter
import json

FILE = Path(__file__).resolve().parent.parent / "memory" / "audit.jsonl"
def run(_: str = "summary"):
    if not FILE.exists(): return "Brak zdarzeń audytowych."
    events = []
    for line in FILE.read_text(encoding="utf-8").splitlines()[-100:]:
        try: events.append(json.loads(line))
        except json.JSONDecodeError: pass
    return f"Zdarzenia: {len(events)}; typy: {dict(Counter(item.get('event') for item in events))}"
