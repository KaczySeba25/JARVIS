"""Durable task progress and plan-approval contracts for Jarvis."""
from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "memory" / "jarvis.sqlite3"
APPROVAL_TTL_SECONDS = 7 * 24 * 60 * 60
_SECRET = re.compile(r"(?i)(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|(?:password|passwd|api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"']?[^\s,;\"']+|bearer\s+[A-Za-z0-9._~+/-]+=*)")


def _connect():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_FILE, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS task_runs (
        id TEXT PRIMARY KEY, goal TEXT NOT NULL, status TEXT NOT NULL,
        plan_json TEXT, allowed_tools_json TEXT NOT NULL DEFAULT '[]',
        approval_scope TEXT NOT NULL DEFAULT '', created REAL NOT NULL, updated REAL NOT NULL
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_task_runs_status ON task_runs(status, updated)")
    db.execute("""CREATE TABLE IF NOT EXISTS task_events (
        id INTEGER PRIMARY KEY, task_id TEXT NOT NULL, ts REAL NOT NULL,
        stage TEXT NOT NULL, message TEXT NOT NULL, details_json TEXT NOT NULL DEFAULT '{}',
        FOREIGN KEY(task_id) REFERENCES task_runs(id)
    )""")
    db.commit()
    return db


def _safe(value, limit=4000):
    return _SECRET.sub("[REDACTED]", str(value or ""))[:limit]


def _clean_details(value, depth=0):
    if depth > 5:
        return "[DEPTH_LIMIT]"
    if isinstance(value, dict):
        return {str(key)[:80]: _clean_details(item, depth + 1) for key, item in list(value.items())[:50]}
    if isinstance(value, (list, tuple)):
        return [_clean_details(item, depth + 1) for item in value[:50]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _safe(value, 2000)


def create(goal: str) -> str:
    task_id, now = uuid.uuid4().hex, time.time()
    with closing(_connect()) as db:
        db.execute("INSERT INTO task_runs(id,goal,status,created,updated) VALUES(?,?,?,?,?)", (task_id, _safe(goal, 2000), "planning", now, now))
        db.commit()
    event(task_id, "planning", "Rozpoczynam analizę zadania.")
    return task_id


def get(task_id: str):
    with closing(_connect()) as db:
        row = db.execute("SELECT id,goal,status,plan_json,allowed_tools_json,approval_scope,created,updated FROM task_runs WHERE id=?", (task_id,)).fetchone()
    if not row:
        return None
    return {"id": row[0], "goal": row[1], "status": row[2], "plan": json.loads(row[3]) if row[3] else None,
            "allowed_tools": json.loads(row[4] or "[]"), "approval_scope": row[5], "created": row[6], "updated": row[7]}


def latest_pending():
    with closing(_connect()) as db:
        db.execute("UPDATE task_runs SET status='expired',updated=? WHERE status='waiting_approval' AND updated<?", (time.time(), time.time() - APPROVAL_TTL_SECONDS))
        db.commit()
        row = db.execute("SELECT id FROM task_runs WHERE status='waiting_approval' ORDER BY updated DESC LIMIT 1").fetchone()
    return get(row[0]) if row else None


def latest_waiting_user():
    with closing(_connect()) as db:
        row = db.execute("SELECT id FROM task_runs WHERE status='waiting_user' ORDER BY updated DESC LIMIT 1").fetchone()
    return get(row[0]) if row else None


def save_plan(task_id: str, plan, allowed_tools: list[str], scope: str):
    tools = sorted(set(str(name) for name in allowed_tools if str(name).isidentifier()))
    now = time.time()
    with closing(_connect()) as db:
        db.execute("UPDATE task_runs SET status='superseded',updated=? WHERE status='waiting_approval' AND id<>?", (now, task_id))
        db.execute("UPDATE task_runs SET status='waiting_approval',plan_json=?,allowed_tools_json=?,approval_scope=?,updated=? WHERE id=?",
                   (json.dumps(plan, ensure_ascii=False), json.dumps(tools), _safe(scope, 2000), now, task_id))
        db.commit()
    event(task_id, "waiting_approval", "Plan gotowy — oczekuje na decyzję Sebastiana.", {"allowed_tools": tools})


def approve(task_id: str):
    now = time.time()
    with closing(_connect()) as db:
        cur = db.execute("UPDATE task_runs SET status='approved',updated=? WHERE id=? AND status='waiting_approval'", (now, task_id))
        db.commit()
    if cur.rowcount:
        event(task_id, "approved", "Plan zaakceptowany.")
    return bool(cur.rowcount)


def reject(task_id: str):
    now = time.time()
    with closing(_connect()) as db:
        cur = db.execute("UPDATE task_runs SET status='rejected',updated=? WHERE id=? AND status='waiting_approval'", (now, task_id))
        db.commit()
    if cur.rowcount:
        event(task_id, "rejected", "Plan odrzucony.")
    return bool(cur.rowcount)


def authorize_tool(task_id: str | None, tool: str) -> bool:
    item = get(task_id) if task_id else None
    return bool(item and item["status"] in {"approved", "executing"} and tool in item["allowed_tools"])


def set_status(task_id: str, status: str):
    now = time.time()
    with closing(_connect()) as db:
        db.execute("UPDATE task_runs SET status=?,updated=? WHERE id=?", (status, now, task_id))
        db.commit()


def event(task_id: str, stage: str, message: str, details=None):
    safe_details = _clean_details(details or {})
    with closing(_connect()) as db:
        db.execute("INSERT INTO task_events(task_id,ts,stage,message,details_json) VALUES(?,?,?,?,?)",
                   (task_id, time.time(), _safe(stage, 80), _safe(message), json.dumps(safe_details, ensure_ascii=False, default=str)))
        db.commit()
        db.execute("UPDATE task_runs SET updated=? WHERE id=?", (time.time(), task_id))
        db.commit()


def recent(limit=100, task_id: str | None = None):
    limit = max(1, min(int(limit), 500))
    with closing(_connect()) as db:
        if task_id:
            rows = db.execute("SELECT task_id,ts,stage,message,details_json FROM task_events WHERE task_id=? ORDER BY id DESC LIMIT ?", (task_id, limit)).fetchall()
        else:
            rows = db.execute("SELECT task_id,ts,stage,message,details_json FROM task_events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [{"task_id": r[0], "timestamp": r[1], "stage": r[2], "message": r[3], "details": json.loads(r[4])} for r in reversed(rows)]
