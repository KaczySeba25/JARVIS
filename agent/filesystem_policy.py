"""Allowlisted filesystem access for Jarvis computer work."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "memory" / "filesystem_permissions.json"
DEFAULT_ROOTS = [str(ROOT), r"D:\AI Trading Agent"]

def roots():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        values = data.get("roots", []) if isinstance(data, dict) else []
    except (OSError, ValueError, TypeError):
        values = []
    candidates = values or DEFAULT_ROOTS
    result = []
    for value in candidates:
        try:
            path = Path(value).expanduser().resolve()
            if path.exists() and path.is_dir() and path not in result:
                result.append(path)
        except (OSError, ValueError):
            pass
    return result

def resolve(relative_or_absolute):
    candidate = Path(str(relative_or_absolute or "")).expanduser()
    if not candidate.is_absolute():
        candidate = roots()[0] / candidate
    candidate = candidate.resolve()
    if not any(candidate == base or base in candidate.parents for base in roots()):
        raise PermissionError("path_outside_approved_roots")
    return candidate

def describe():
    return {"roots": [str(item) for item in roots()], "mode": "allowlist", "outside_roots": "blocked"}
