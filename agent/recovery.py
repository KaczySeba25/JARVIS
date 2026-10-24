"""Bounded recovery records for Jarvis operations."""
from __future__ import annotations
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "memory" / "recovery.jsonl"
SAFE_RETRY_SKILLS = {"hello", "model_status", "integration_diagnostics", "system_health", "autonomy_status"}

def classify(error: str, skill: str = "") -> str:
    text = f"{skill} {error}".lower()
    if any(word in text for word in ("timeout", "connection", "tempor", "429", "503")):
        return "transient"
    if any(word in text for word in ("permission", "credential", "secret", "unauthorized", "captcha", "2fa")):
        return "access_or_human"
    if any(word in text for word in ("syntax", "import", "attribute", "typeerror")):
        return "code_or_dependency"
    return "unknown"

def record(skill: str, error: str, action: str, attempt: int = 1, outcome: str = "recorded") -> dict:
    item = {"ts": time.time(), "skill": str(skill)[:120], "error": str(error)[:500], "class": classify(error, skill), "action": str(action)[:300], "attempt": int(attempt), "outcome": outcome}
    FILE.parent.mkdir(parents=True, exist_ok=True)
    with FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return {"recorded": True, "class": item["class"], "action": item["action"], "attempt": item["attempt"], "outcome": item["outcome"]}

def can_retry(skill: str, attempt: int = 1) -> bool:
    return skill in SAFE_RETRY_SKILLS and attempt < 2
