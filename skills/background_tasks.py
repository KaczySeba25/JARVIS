"""Durable background task definitions with bounded schedules and explicit status."""
from __future__ import annotations
import json
import sqlite3
import time
import uuid
from pathlib import Path

RISK_LEVEL = "medium"
DB = Path(__file__).resolve().parent.parent / "memory" / "jarvis.sqlite3"

def _db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=15)
    db.execute("CREATE TABLE IF NOT EXISTS background_tasks(id TEXT PRIMARY KEY, goal TEXT, schedule TEXT, status TEXT, max_runs INTEGER, runs INTEGER, next_run REAL, created REAL, updated REAL, metadata_json TEXT, approved INTEGER NOT NULL DEFAULT 0)")
    columns = {row[1] for row in db.execute("PRAGMA table_info(background_tasks)")}
    if "approved" not in columns:
        db.execute("ALTER TABLE background_tasks ADD COLUMN approved INTEGER NOT NULL DEFAULT 0")
    db.commit()
    return db

def run(argument=None):
    data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
    action = str(data.get("action", "list")).lower()
    with _db() as db:
        if action == "create":
            task_id = "bg_" + uuid.uuid4().hex[:18]
            now = time.time()
            db.execute("INSERT INTO background_tasks VALUES(?,?,?,?,?,?,?,?,?,?,?)", (task_id, str(data.get("goal", ""))[:1000], str(data.get("schedule", "once"))[:120], "scheduled", max(1, min(1000, int(data.get("max_runs", 1)))), 0, float(data.get("next_run", now)), now, now, json.dumps(data.get("metadata", {}), ensure_ascii=False), 1 if data.get("approved") else 0))
            db.commit()
            return {"created": True, "id": task_id, "status": "scheduled", "approved": bool(data.get("approved")), "next_run": now}
        if action == "approve":
            db.execute("UPDATE background_tasks SET approved=1,status='scheduled',updated=? WHERE id=?", (time.time(), data.get("id")))
            db.commit()
            return {"updated": True, "id": data.get("id"), "approved": True}
        if action in {"pause", "resume", "cancel"}:
            status = {"pause": "paused", "resume": "scheduled", "cancel": "cancelled"}[action]
            db.execute("UPDATE background_tasks SET status=?,updated=? WHERE id=?", (status, time.time(), data.get("id")))
            db.commit()
            return {"updated": True, "id": data.get("id"), "status": status}
        rows = db.execute("SELECT id,goal,schedule,status,max_runs,runs,next_run,created,updated,approved FROM background_tasks ORDER BY updated DESC LIMIT 100").fetchall()
        return {"tasks": [dict(zip(("id","goal","schedule","status","max_runs","runs","next_run","created","updated","approved"), row)) for row in rows]}
