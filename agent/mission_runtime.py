"""Durable mission graph for Jarvis: steps, dependencies, evidence and recovery."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "memory" / "jarvis.sqlite3"


def _db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_FILE, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS missions (
        id TEXT PRIMARY KEY, goal TEXT NOT NULL, status TEXT NOT NULL,
        priority INTEGER NOT NULL DEFAULT 0, success_criteria TEXT NOT NULL DEFAULT '',
        metadata_json TEXT NOT NULL DEFAULT '{}', created REAL NOT NULL, updated REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS mission_steps (
        id TEXT PRIMARY KEY, mission_id TEXT NOT NULL, step_key TEXT NOT NULL,
        title TEXT NOT NULL, status TEXT NOT NULL, depends_json TEXT NOT NULL DEFAULT '[]',
        tool TEXT NOT NULL DEFAULT '', argument_json TEXT NOT NULL DEFAULT '{}',
        risk TEXT NOT NULL DEFAULT 'low', attempts INTEGER NOT NULL DEFAULT 0,
        max_attempts INTEGER NOT NULL DEFAULT 2, result_json TEXT NOT NULL DEFAULT '',
        error TEXT NOT NULL DEFAULT '', created REAL NOT NULL, updated REAL NOT NULL,
        UNIQUE(mission_id, step_key), FOREIGN KEY(mission_id) REFERENCES missions(id)
    );
    CREATE TABLE IF NOT EXISTS mission_evidence (
        id INTEGER PRIMARY KEY, mission_id TEXT NOT NULL, step_id TEXT NOT NULL DEFAULT '',
        kind TEXT NOT NULL, value TEXT NOT NULL, verified INTEGER NOT NULL DEFAULT 0,
        created REAL NOT NULL, FOREIGN KEY(mission_id) REFERENCES missions(id)
    );
    CREATE TABLE IF NOT EXISTS mission_events (
        id INTEGER PRIMARY KEY, mission_id TEXT NOT NULL, stage TEXT NOT NULL,
        message TEXT NOT NULL, details_json TEXT NOT NULL DEFAULT '{}', created REAL NOT NULL,
        FOREIGN KEY(mission_id) REFERENCES missions(id)
    );
    CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status, updated);
    CREATE INDEX IF NOT EXISTS idx_mission_steps_ready ON mission_steps(mission_id, status);
    """)
    db.commit()
    return db


def _json(value, default):
    if value in (None, ""):
        return default
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        return parsed if isinstance(parsed, type(default)) else default
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _mission(row):
    if not row:
        return None
    return {"id": row["id"], "goal": row["goal"], "status": row["status"], "priority": row["priority"],
            "success_criteria": row["success_criteria"], "metadata": _json(row["metadata_json"], {}),
            "created": row["created"], "updated": row["updated"]}


def _step(row):
    if not row:
        return None
    return {"id": row["id"], "mission_id": row["mission_id"], "step_key": row["step_key"],
            "title": row["title"], "status": row["status"], "depends_on": _json(row["depends_json"], []),
            "tool": row["tool"], "argument": _json(row["argument_json"], {}), "risk": row["risk"],
            "attempts": row["attempts"], "max_attempts": row["max_attempts"],
            "result": _json(row["result_json"], row["result_json"]), "error": row["error"],
            "created": row["created"], "updated": row["updated"]}


def event(mission_id, stage, message, details=None):
    with closing(_db()) as db:
        db.execute("INSERT INTO mission_events(mission_id,stage,message,details_json,created) VALUES(?,?,?,?,?)",
                   (mission_id, str(stage)[:80], str(message)[:1000], json.dumps(details or {}, ensure_ascii=False, default=str)[:6000], time.time()))
        db.execute("UPDATE missions SET updated=? WHERE id=?", (time.time(), mission_id))
        db.commit()


def create(goal, success_criteria="", priority=0, metadata=None, steps=None):
    mission_id = "m_" + uuid.uuid4().hex[:20]
    now = time.time()
    with closing(_db()) as db:
        db.execute("INSERT INTO missions(id,goal,status,priority,success_criteria,metadata_json,created,updated) VALUES(?,?,?,?,?,?,?,?)",
                   (mission_id, str(goal)[:2000], "planning", int(priority), str(success_criteria)[:2000], json.dumps(metadata or {}, ensure_ascii=False), now, now))
        db.commit()
    event(mission_id, "created", "Utworzono trwałą misję.", {"goal": str(goal)[:300]})
    for item in steps or []:
        add_step(mission_id, item)
    return get(mission_id)


def add_step(mission_id, item):
    item = item if isinstance(item, dict) else {"title": str(item)}
    title = str(item.get("title") or item.get("objective") or item.get("step") or "Krok")[:500]
    key = str(item.get("step_key") or item.get("key") or uuid.uuid4().hex[:10])[:100]
    now = time.time()
    with closing(_db()) as db:
        db.execute("INSERT OR REPLACE INTO mission_steps(id,mission_id,step_key,title,status,depends_json,tool,argument_json,risk,attempts,max_attempts,result_json,error,created,updated) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   ("s_" + uuid.uuid4().hex[:18], mission_id, key, title, "pending", json.dumps(item.get("depends_on", item.get("depends", [])) or []),
                    str(item.get("tool") or "")[:120], json.dumps(item.get("argument", {}) or {}, ensure_ascii=False), str(item.get("risk") or "low")[:20],
                    0, max(1, min(5, int(item.get("max_attempts", 2)))), "", "", now, now))
        db.execute("UPDATE missions SET status='ready',updated=? WHERE id=? AND status='planning'", (now, mission_id))
        db.commit()
    event(mission_id, "step_added", f"Dodano krok: {title}", {"step_key": key})
    return get(mission_id)


def get(mission_id, include_steps=True):
    with closing(_db()) as db:
        mission = db.execute("SELECT * FROM missions WHERE id=?", (mission_id,)).fetchone()
        if not mission:
            return None
        result = _mission(mission)
        if include_steps:
            rows = db.execute("SELECT * FROM mission_steps WHERE mission_id=? ORDER BY created", (mission_id,)).fetchall()
            result["steps"] = [_step(row) for row in rows]
            result["ready_steps"] = [item["step_key"] for item in result["steps"] if item["status"] == "ready"]
            result["evidence"] = [dict(row) for row in db.execute("SELECT id,step_id,kind,value,verified,created FROM mission_evidence WHERE mission_id=? ORDER BY id", (mission_id,)).fetchall()]
        return result


def list_missions(status=None, limit=30):
    limit = max(1, min(int(limit), 100))
    with closing(_db()) as db:
        if status:
            rows = db.execute("SELECT * FROM missions WHERE status=? ORDER BY priority DESC,updated DESC LIMIT ?", (status, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM missions ORDER BY priority DESC,updated DESC LIMIT ?", (limit,)).fetchall()
    return [_mission(row) for row in rows]


def ready_steps(mission_id):
    mission = get(mission_id)
    if not mission:
        return []
    done = {item["step_key"] for item in mission["steps"] if item["status"] == "done"}
    return [item for item in mission["steps"] if item["status"] in {"pending", "ready", "failed"} and item["attempts"] < item["max_attempts"] and set(item["depends_on"]).issubset(done)]


def update_step(mission_id, step_key, status, result=None, error="", increment_attempt=False):
    now = time.time()
    allowed = {"pending", "ready", "running", "done", "failed", "blocked", "waiting_user", "skipped"}
    status = status if status in allowed else "failed"
    with closing(_db()) as db:
        row = db.execute("SELECT id,attempts FROM mission_steps WHERE mission_id=? AND step_key=?", (mission_id, step_key)).fetchone()
        if not row:
            return None
        attempts = int(row["attempts"]) + (1 if increment_attempt else 0)
        db.execute("UPDATE mission_steps SET status=?,attempts=?,result_json=?,error=?,updated=? WHERE id=?",
                   (status, attempts, json.dumps(result, ensure_ascii=False, default=str) if result is not None else "", str(error)[:1000], now, row["id"]))
        if status == "done" and not db.execute("SELECT 1 FROM mission_steps WHERE mission_id=? AND status NOT IN ('done','skipped')", (mission_id,)).fetchone():
            db.execute("UPDATE missions SET status='done',updated=? WHERE id=?", (now, mission_id))
        elif status in {"failed", "blocked", "waiting_user"}:
            db.execute("UPDATE missions SET status=?,updated=? WHERE id=?", ("waiting_user" if status == "waiting_user" else status, now, mission_id))
        else:
            db.execute("UPDATE missions SET status='executing',updated=? WHERE id=?", (now, mission_id))
        db.commit()
    event(mission_id, status, f"Krok {step_key}: {status}", {"error": str(error)[:300]} if error else {"result": str(result)[:500]})
    return get(mission_id)


def add_evidence(mission_id, kind, value, verified=False, step_id=""):
    with closing(_db()) as db:
        db.execute("INSERT INTO mission_evidence(mission_id,step_id,kind,value,verified,created) VALUES(?,?,?,?,?,?)",
                   (mission_id, str(step_id)[:100], str(kind)[:80], str(value)[:4000], 1 if verified else 0, time.time()))
        db.commit()
    event(mission_id, "evidence", "Dodano dowód rezultatu.", {"kind": kind, "verified": bool(verified)})
    return get(mission_id)


def set_status(mission_id, status):
    if status not in {"planning", "ready", "executing", "paused", "waiting_user", "blocked", "done", "cancelled"}:
        raise ValueError("unsupported_mission_status")
    with closing(_db()) as db:
        db.execute("UPDATE missions SET status=?,updated=? WHERE id=?", (status, time.time(), mission_id))
        db.commit()
    event(mission_id, status, f"Misja ma status: {status}.")
    return get(mission_id)
