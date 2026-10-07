"""Local task list stored as JSON without external services."""
import json
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "memory" / "tasks.json"
def run(command: str = "list"):
    data = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else []
    parts = (command or "list").split("|", 1)
    if parts[0] == "add" and len(parts) == 2: data.append({"title": parts[1], "status": "open"})
    elif parts[0] == "done" and len(parts) == 2 and parts[1].isdigit() and int(parts[1]) < len(data): data[int(parts[1])]["status"] = "done"
    elif parts[0] != "list": return "Użycie: list | add|zadanie | done|numer"
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return "\n".join(f"{i}: [{item['status']}] {item['title']}" for i, item in enumerate(data)) or "Brak zadań."
