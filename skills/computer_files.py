"""Read and modify files in explicitly approved local folders."""
from __future__ import annotations
import json
import re
import shutil
from pathlib import Path

RISK_LEVEL = "high"
MAX_BYTES = 2_000_000
SECRET = re.compile(r"(?i)(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|(?:password|passwd|api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"']?[^\s,;\"']+|bearer\s+[A-Za-z0-9._~+/-]+=*)")

def _redact(value):
    return SECRET.sub("[REDACTED]", str(value))

def run(argument=None):
    try:
        from filesystem_policy import describe, resolve, roots
        data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
        action = str(data.get("action", "")).lower()
        if action == "permissions": return describe()
        path = resolve(data.get("path"))
        if action == "list":
            return {"ok": True, "path": str(path), "items": [{"name": p.name, "directory": p.is_dir(), "size": p.stat().st_size if p.is_file() else None} for p in list(path.iterdir())[:500]]}
        if action == "read":
            if not path.is_file(): return {"ok": False, "error": "file_not_found"}
            if path.stat().st_size > MAX_BYTES: return {"ok": False, "error": "file_too_large"}
            return {"ok": True, "path": str(path), "content": _redact(path.read_text(encoding="utf-8-sig", errors="replace"))}
        if action == "search":
            query = str(data.get("query", "")).strip().lower()
            if len(query) < 2: return {"ok": False, "error": "query_too_short"}
            matches = []
            for base in roots():
                for item in base.rglob("*"):
                    if len(matches) >= 200: break
                    if item.is_file() and query in item.name.lower(): matches.append(str(item))
            return {"ok": True, "query": query, "matches": matches}
        if action == "mkdir":
            path.mkdir(parents=True, exist_ok=True)
            return {"ok": True, "created": str(path)}
        if action == "write":
            content = str(data.get("content", ""))
            if len(content.encode("utf-8")) > MAX_BYTES: return {"ok": False, "error": "content_too_large"}
            backup = None
            if path.exists():
                backup = path.with_suffix(path.suffix + ".jarvis-backup")
                shutil.copy2(path, backup)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"ok": True, "written": str(path), "backup": str(backup) if backup else None}
        return {"ok": False, "error": "unsupported_action", "allowed": ["permissions", "list", "read", "search", "mkdir", "write"]}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:300]}
