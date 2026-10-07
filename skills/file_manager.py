"""Inspect and create project files inside Jarvis's workspace."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.resolve()
WORKSPACE = ROOT / "workspace"
MAX_BYTES = 1_000_000
_SECRET = re.compile(r"(?i)(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|((?:password|passwd|api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"']?)[^\s,;\"']+|bearer\s+[A-Za-z0-9._~+/-]+=*)")


def _redact(value):
    return _SECRET.sub(lambda match: (match.group(1) or "") + "[REDACTED]", value)


def _path(raw):
    path = (WORKSPACE / str(raw or ".")).resolve()
    if path != WORKSPACE and WORKSPACE not in path.parents:
        raise ValueError("Pliki tworzone przez Generator muszą pozostać w folderze workspace.")
    return path


def _backup(path):
    if path.exists() and path.is_file():
        try:
            from backup import snapshot
        except ImportError:
            from agent.backup import snapshot
        return snapshot([str(path.relative_to(ROOT))])
    return None


def run(command):
    """Use JSON {action,path,content/query}; legacy list|path/read|path remain supported."""
    raw = str(command or "").strip()
    try:
        request = json.loads(raw)
        if not isinstance(request, dict):
            raise ValueError("Polecenie JSON musi być obiektem.")
    except json.JSONDecodeError:
        action, _, value = raw.partition("|")
        request = {"action": action or "list", "path": value or "."}
    action = str(request.get("action", "list")).lower()
    path = _path(request.get("path", "."))
    if action == "list":
        if not path.is_dir():
            return {"ok": False, "error": "folder_not_found"}
        entries = sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.casefold()))[:500]
        return {"path": str(path.relative_to(WORKSPACE)), "items": [{"name": item.name, "type": "folder" if item.is_dir() else "file"} for item in entries]}
    if action == "read":
        if not path.is_file():
            return {"ok": False, "error": "file_not_found"}
        if path.stat().st_size > MAX_BYTES:
            return {"ok": False, "error": "file_too_large", "max_bytes": MAX_BYTES}
        return {"path": str(path.relative_to(WORKSPACE)), "content": _redact(path.read_text(encoding="utf-8-sig", errors="replace"))}
    if action == "search":
        if not path.is_dir():
            return {"ok": False, "error": "folder_not_found"}
        needle = str(request.get("query", "")).casefold()
        if len(needle) < 2:
            return {"ok": False, "error": "query_too_short"}
        matches = []
        for item in path.rglob("*"):
            if not item.is_file() or item.stat().st_size > 250_000:
                continue
            try:
                for number, line in enumerate(item.read_text(encoding="utf-8-sig").splitlines(), 1):
                    if needle in line.casefold():
                        matches.append({"path": str(item.relative_to(WORKSPACE)), "line": number, "text": _redact(line[:500])})
                        if len(matches) >= 100:
                            return {"matches": matches, "truncated": True}
            except (OSError, UnicodeError):
                continue
        return {"matches": matches, "truncated": False}
    if action == "mkdir":
        path.mkdir(parents=True, exist_ok=True)
        return {"created": True, "path": str(path.relative_to(WORKSPACE))}
    if action == "write":
        content = request.get("content")
        if not isinstance(content, str):
            return {"ok": False, "error": "content_must_be_text"}
        if len(content.encode("utf-8")) > MAX_BYTES:
            return {"ok": False, "error": "content_too_large", "max_bytes": MAX_BYTES}
        path.parent.mkdir(parents=True, exist_ok=True)
        before_exists = path.is_file()
        backup_path = _backup(path)
        temporary = path.with_suffix(path.suffix + ".jarvis-tmp")
        temporary.write_text(content, encoding="utf-8", newline="")
        os.replace(temporary, path)
        try:
            from workspace_history import record_change
        except ImportError:
            from agent.workspace_history import record_change
        version_id = record_change(str(path.relative_to(WORKSPACE)), before_exists, backup_path, content)
        return {"written": True, "path": str(path.relative_to(WORKSPACE)), "bytes": path.stat().st_size, "version_id": version_id, "backup_path": backup_path}
    return {"ok": False, "error": "unsupported_action", "allowed": ["list", "read", "search", "mkdir", "write"]}
