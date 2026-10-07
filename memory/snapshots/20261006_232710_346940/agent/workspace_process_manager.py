"""Launch and supervise user-approved Python demos built in the workspace."""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import time
import uuid
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / "workspace"
DB = ROOT / "memory" / "jarvis.sqlite3"
_PROCESSES: dict[str, subprocess.Popen] = {}


def _connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=10)
    db.execute("CREATE TABLE IF NOT EXISTS workspace_runs (id TEXT PRIMARY KEY, project TEXT NOT NULL, entry TEXT NOT NULL, pid INTEGER NOT NULL, log_path TEXT NOT NULL, started REAL NOT NULL, stopped REAL)")
    db.commit()
    return db


def _entry(project, entry):
    project_path = (WORKSPACE / str(project)).resolve()
    entry_path = (project_path / str(entry)).resolve()
    if WORKSPACE.resolve() not in project_path.parents or project_path == WORKSPACE.resolve():
        raise ValueError("Projekt musi znajdować się w workspace.")
    if project_path not in entry_path.parents or not entry_path.is_file() or entry_path.suffix.lower() != ".py":
        raise ValueError("Punkt startowy musi być istniejącym plikiem Python w folderze projektu.")
    return project_path, entry_path


def execute(request):
    data = json.loads(request) if isinstance(request, str) else request
    if not isinstance(data, dict):
        raise ValueError("Oczekuję obiektu JSON.")
    action = str(data.get("action", "")).lower()
    if action == "start":
        project, entry = _entry(data.get("project", ""), data.get("entry", ""))
        run_id = uuid.uuid4().hex[:12]
        flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0) if os.name == "nt" else 0
        process = subprocess.Popen([sys.executable, "-u", str(entry)], cwd=str(project), stdin=subprocess.DEVNULL,
                                   shell=False, creationflags=flags)
        log_path = ""
        _PROCESSES[run_id] = process
        with closing(_connect()) as db:
            db.execute("INSERT INTO workspace_runs(id,project,entry,pid,log_path,started) VALUES(?,?,?,?,?,?)",
                       (run_id, str(project.relative_to(WORKSPACE)), str(entry.relative_to(project)), process.pid, str(log_path), time.time()))
            db.commit()
        return {"started": True, "run_id": run_id, "pid": process.pid, "project": str(project.relative_to(WORKSPACE)),
                "entry": str(entry.relative_to(project)), "visible_console_requested": os.name == "nt", "output": "inherited_visible_console" if os.name == "nt" else "inherited_terminal"}
    run_id = str(data.get("run_id", ""))
    with closing(_connect()) as db:
        row = db.execute("SELECT id,project,entry,pid,log_path,started,stopped FROM workspace_runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        return {"found": False, "run_id": run_id}
    process = _PROCESSES.get(run_id)
    if action == "status":
        code = process.poll() if process else None
        state = "running" if process and code is None else ("exited" if process else "state_unknown_after_restart")
        return {"found": True, "run_id": run_id, "state": state, "return_code": code, "pid": row[3], "output": "visible console; output is not captured"}
    if action == "stop":
        if not process or process.poll() is not None:
            return {"stopped": False, "reason": "process_handle_unavailable_or_already_exited", "run_id": run_id}
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"], capture_output=True, text=True, timeout=10, shell=False)
            else:
                process.kill()
        _PROCESSES.pop(run_id, None)
        with closing(_connect()) as db:
            db.execute("UPDATE workspace_runs SET stopped=? WHERE id=?", (time.time(), run_id))
            db.commit()
        return {"stopped": True, "run_id": run_id}
    return {"ok": False, "error": "unsupported_action", "allowed": ["start", "status", "stop"]}
