"""Independent deterministic verifier for mission claims and local evidence."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

RISK_LEVEL = "low"

def run(argument=None):
    data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
    kind = str(data.get("kind", "")).lower()
    if kind == "exact":
        verified = data.get("expected") == data.get("observed")
        return {"verified": verified, "kind": kind, "basis": "exact_value_comparison", "expected": data.get("expected"), "observed": data.get("observed")}
    if kind == "file_exists":
        path = Path(str(data.get("path", ""))).resolve()
        exists = path.exists() and (not data.get("file") or path.is_file())
        return {"verified": exists, "kind": kind, "path": str(path), "exists": exists, "size": path.stat().st_size if exists and path.is_file() else None}
    if kind == "text_contains":
        path = Path(str(data.get("path", ""))).resolve()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            needle = str(data.get("text", ""))
            return {"verified": needle in text, "kind": kind, "path": str(path), "found": needle in text}
        except Exception as exc:
            return {"verified": False, "kind": kind, "error": type(exc).__name__}
    if kind == "sha256":
        path = Path(str(data.get("path", ""))).resolve()
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            return {"verified": digest == str(data.get("expected_hash", "")), "kind": kind, "hash": digest}
        except Exception as exc:
            return {"verified": False, "kind": kind, "error": type(exc).__name__}
    return {"verified": False, "review_required": True, "error": "unsupported_verification_kind"}
