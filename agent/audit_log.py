"""Append-only audit events for traceability."""
import json
import time
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "memory" / "audit.jsonl"
def write(event: str, **data):
    FILE.parent.mkdir(parents=True, exist_ok=True)
    with FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": time.time(), "event": event, **data}, ensure_ascii=False) + "\n")
