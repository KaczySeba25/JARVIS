"""Query locally stored research knowledge."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "memory" / "jarvis.sqlite3"
def run(query: str = ""):
    if not DB.exists(): return "Brak lokalnej bazy wiedzy."
    with sqlite3.connect(DB) as db:
        rows = db.execute("SELECT topic,title,url,confidence FROM knowledge WHERE topic LIKE ? OR conclusion LIKE ? ORDER BY confidence DESC LIMIT 10", (f"%{query}%", f"%{query}%")).fetchall()
    return "\n".join(f"{topic} | {title} | {confidence:.2f} | {url}" for topic,title,url,confidence in rows) or "Nie znaleziono wiedzy."
