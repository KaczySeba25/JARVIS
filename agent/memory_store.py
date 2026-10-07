"""Private, local-first long-term memory with simple transparent retrieval."""
from __future__ import annotations

import re
import sqlite3
import time
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "memory" / "jarvis.sqlite3"
_SECRET = re.compile(r"(?i)(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|(?:password|passwd|api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"']?[^\s,;\"']+|bearer\s+[A-Za-z0-9._~+/-]+=*)")
_WORD = re.compile(r"[\w'-]{3,}", re.UNICODE)


def _connect():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_FILE, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS long_term_memory (
        id INTEGER PRIMARY KEY, content TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'fact',
        source TEXT NOT NULL DEFAULT 'user', confidence REAL NOT NULL DEFAULT 1.0,
        created REAL NOT NULL, accessed REAL NOT NULL
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memory_category ON long_term_memory(category)")
    return db


def remember(content: str, category: str = "fact", source: str = "user", confidence: float = 1.0) -> dict:
    """Store a useful memory locally; credentials are rejected rather than retained."""
    text = " ".join(str(content or "").split()).strip()
    if len(text) < 3:
        raise ValueError("Wspomnienie jest zbyt krótkie.")
    if _SECRET.search(text):
        return {"saved": False, "reason": "secret_detected"}
    category = re.sub(r"[^a-z0-9_-]", "", str(category).lower())[:40] or "fact"
    confidence = max(0.0, min(1.0, float(confidence)))
    now = time.time()
    with closing(_connect()) as db:
        row = db.execute("SELECT id FROM long_term_memory WHERE content=? COLLATE NOCASE AND category=?", (text, category)).fetchone()
        if row:
            db.execute("UPDATE long_term_memory SET source=?, confidence=?, accessed=? WHERE id=?", (source[:120], confidence, now, row[0]))
            memory_id, updated = row[0], True
        else:
            cur = db.execute("INSERT INTO long_term_memory(content,category,source,confidence,created,accessed) VALUES(?,?,?,?,?,?)", (text, category, source[:120], confidence, now, now))
            memory_id, updated = cur.lastrowid, False
        db.commit()
    return {"saved": True, "id": memory_id, "updated": updated, "category": category}


def recall(query: str, limit: int = 6, category: str | None = None) -> list[dict]:
    """Rank local memories by lexical overlap and confidence; no cloud service required."""
    terms = {word.casefold() for word in _WORD.findall(str(query or ""))}
    if not terms:
        return []
    with closing(_connect()) as db:
        sql = "SELECT id,content,category,source,confidence,created FROM long_term_memory"
        params: tuple = ()
        if category:
            sql += " WHERE category=?"
            params = (category,)
        rows = db.execute(sql, params).fetchall()
        ranked = []
        for row in rows:
            words = {word.casefold() for word in _WORD.findall(row[1])}
            overlap = len(terms & words) / max(1, len(terms))
            if overlap:
                ranked.append((overlap * 0.8 + row[4] * 0.2, row))
        ranked.sort(key=lambda item: (item[0], item[1][5]), reverse=True)
        selected = ranked[:max(1, min(int(limit), 20))]
        if selected:
            db.executemany("UPDATE long_term_memory SET accessed=? WHERE id=?", [(time.time(), row[1][0]) for row in selected])
            db.commit()
    return [{"id": row[0], "content": row[1], "category": row[2], "source": row[3], "confidence": row[4]} for _, row in selected]


def forget(memory_id: int) -> bool:
    with closing(_connect()) as db:
        cur = db.execute("DELETE FROM long_term_memory WHERE id=?", (int(memory_id),))
        db.commit()
        return cur.rowcount > 0


def list_memories(limit: int = 100, category: str | None = None) -> list[dict]:
    """List recent local memories so the user can review what Jarvis retained."""
    limit = max(1, min(int(limit), 500))
    with closing(_connect()) as db:
        if category:
            rows = db.execute("SELECT id,content,category,source,confidence,created,accessed FROM long_term_memory WHERE category=? ORDER BY accessed DESC LIMIT ?", (category, limit)).fetchall()
        else:
            rows = db.execute("SELECT id,content,category,source,confidence,created,accessed FROM long_term_memory ORDER BY accessed DESC LIMIT ?", (limit,)).fetchall()
    return [{"id": row[0], "content": row[1], "category": row[2], "source": row[3], "confidence": row[4], "created": row[5], "accessed": row[6]} for row in rows]


def update_memory(memory_id: int, content: str, category: str | None = None) -> bool:
    """Edit one local memory without creating a duplicate or retaining secrets."""
    text = " ".join(str(content or "").split()).strip()
    if len(text) < 3:
        raise ValueError("Wspomnienie jest zbyt krótkie.")
    if _SECRET.search(text):
        raise ValueError("Wspomnienie wygląda na sekret i nie zostało zapisane.")
    now = time.time()
    with closing(_connect()) as db:
        if category:
            safe_category = re.sub(r"[^a-z0-9_-]", "", str(category).lower())[:40] or "fact"
            cur = db.execute("UPDATE long_term_memory SET content=?,category=?,accessed=? WHERE id=?", (text, safe_category, now, int(memory_id)))
        else:
            cur = db.execute("UPDATE long_term_memory SET content=?,accessed=? WHERE id=?", (text, now, int(memory_id)))
        db.commit()
        return cur.rowcount > 0
