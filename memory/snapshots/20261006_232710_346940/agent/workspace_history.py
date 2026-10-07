"""Version journal for files created or changed in Jarvis workspace."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
import uuid
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.resolve()
WORKSPACE = (ROOT / "workspace").resolve()
SNAPSHOTS = (ROOT / "memory" / "snapshots").resolve()
DB = ROOT / "memory" / "jarvis.sqlite3"


def _connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=10)
    db.execute("""CREATE TABLE IF NOT EXISTS workspace_versions (
        id TEXT PRIMARY KEY, path TEXT NOT NULL, before_exists INTEGER NOT NULL,
        backup_path TEXT, after_sha256 TEXT NOT NULL, created REAL NOT NULL, rolled_back REAL
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_workspace_versions_path ON workspace_versions(path, created DESC)")
    db.commit()
    return db


def _safe_path(relative):
    path = (WORKSPACE / str(relative)).resolve()
    if path == WORKSPACE or WORKSPACE not in path.parents:
        raise ValueError("Dozwolone są wyłącznie pliki wewnątrz workspace.")
    return path


def record_change(relative, before_exists, backup_path, content):
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    version_id = uuid.uuid4().hex[:12]
    with closing(_connect()) as db:
        db.execute("INSERT INTO workspace_versions(id,path,before_exists,backup_path,after_sha256,created) VALUES(?,?,?,?,?,?)",
                   (version_id, str(relative), int(bool(before_exists)), str(backup_path or ""), digest, time.time()))
        db.commit()
    return version_id


def list_versions(relative, limit=50):
    _safe_path(relative)
    limit = max(1, min(int(limit), 100))
    with closing(_connect()) as db:
        rows = db.execute("SELECT id,path,before_exists,backup_path,after_sha256,created,rolled_back FROM workspace_versions WHERE path=? ORDER BY created DESC LIMIT ?", (str(relative), limit)).fetchall()
    return [{"id": r[0], "path": r[1], "can_restore": bool(r[2]) or not r[6], "previous_version_exists": bool(r[2]), "created": r[5], "rolled_back": r[6] is not None} for r in rows]


def restore(version_id):
    with closing(_connect()) as db:
        row = db.execute("SELECT path,before_exists,backup_path,rolled_back FROM workspace_versions WHERE id=?", (str(version_id),)).fetchone()
    if not row:
        return {"restored": False, "reason": "version_not_found"}
    relative, before_exists, backup_path, rolled_back = row
    if rolled_back:
        return {"restored": False, "reason": "version_already_rolled_back"}
    target = _safe_path(relative)
    if before_exists:
        snapshot = Path(backup_path).resolve()
        if snapshot != SNAPSHOTS and SNAPSHOTS not in snapshot.parents:
            return {"restored": False, "reason": "backup_outside_snapshot_store"}
        source = (snapshot / Path(relative)).resolve()
        if snapshot not in source.parents or not source.is_file():
            return {"restored": False, "reason": "backup_missing"}
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".rollback")
        temporary.write_bytes(source.read_bytes())
        os.replace(temporary, target)
        result = "previous_file_restored"
    else:
        target.unlink(missing_ok=True)
        result = "new_file_removed"
    with closing(_connect()) as db:
        db.execute("UPDATE workspace_versions SET rolled_back=? WHERE id=?", (time.time(), str(version_id)))
        db.commit()
    return {"restored": True, "path": relative, "result": result, "version_id": version_id}
