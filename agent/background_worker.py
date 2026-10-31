"""Bounded background worker for approved tasks stored by background_tasks."""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "memory" / "jarvis.sqlite3"


class BackgroundWorker:
    def __init__(self, run_goal, interval=5.0, progress=None):
        self.run_goal = run_goal
        self.interval = max(1.0, float(interval))
        self.progress = progress or (lambda *_: None)
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._loop, name="jarvis-background-worker", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _loop(self):
        while not self.stop_event.is_set():
            try:
                self.run_once()
            except Exception as exc:
                self.progress({"stage": "background_error", "message": type(exc).__name__})
            self.stop_event.wait(self.interval)

    def run_once(self):
        DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB, timeout=15) as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(background_tasks)")}
            if "approved" not in columns:
                db.execute("ALTER TABLE background_tasks ADD COLUMN approved INTEGER NOT NULL DEFAULT 0")
            row = db.execute("SELECT id,goal,max_runs,runs,schedule FROM background_tasks WHERE status='scheduled' AND approved=1 AND next_run<=? ORDER BY next_run LIMIT 1", (time.time(),)).fetchone()
            if not row:
                db.commit()
                return {"processed": 0}
            task_id, goal, max_runs, runs, schedule = row
            db.execute("UPDATE background_tasks SET status='running',updated=? WHERE id=?", (time.time(), task_id))
            db.commit()
        self.progress({"stage": "background_started", "task_id": task_id, "goal": goal[:200]})
        try:
            result = self.run_goal(goal)
            runs += 1
            repeat = str(schedule).lower().startswith(("every", "interval")) and runs < max_runs
            with sqlite3.connect(DB, timeout=15) as db:
                db.execute("UPDATE background_tasks SET status=?,runs=?,next_run=?,updated=? WHERE id=?", ("scheduled" if repeat else "done", runs, time.time() + self._interval_seconds(schedule) if repeat else time.time(), time.time(), task_id))
                db.commit()
            self.progress({"stage": "background_done", "task_id": task_id, "result": str(result)[:1000]})
            return {"processed": 1, "task_id": task_id, "status": "scheduled" if repeat else "done"}
        except Exception as exc:
            with sqlite3.connect(DB, timeout=15) as db:
                db.execute("UPDATE background_tasks SET status='blocked',updated=? WHERE id=?", (time.time(), task_id))
                db.commit()
            self.progress({"stage": "background_blocked", "task_id": task_id, "error": type(exc).__name__})
            return {"processed": 1, "task_id": task_id, "status": "blocked"}

    @staticmethod
    def _interval_seconds(schedule):
        text = str(schedule).lower()
        for token, seconds in (("hour", 3600), ("day", 86400), ("minute", 60)):
            if token in text:
                return seconds
        return 3600
