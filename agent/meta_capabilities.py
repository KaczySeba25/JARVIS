"""Small, honest diagnostics and planning helpers for Jarvis."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "memory" / "jarvis.sqlite3"


def execute(name, argument=None):
    value = str(argument or "").strip()
    if name == "memory_manager":
        try:
            from memory_store import recall
            matches = recall(value, limit=6) if value else []
            return {"query": value, "matches": matches, "local_database": str(DB)}
        except Exception as exc:
            return {"query": value, "matches": [], "error": type(exc).__name__}
    if name == "learning_loop":
        try:
            with sqlite3.connect(DB) as db:
                rows = db.execute("SELECT symptom,cause,fix,created FROM errors ORDER BY id DESC LIMIT 5").fetchall()
            return {"input": value, "recent_lessons": [{"symptom": r[0], "cause": r[1], "fix": r[2], "created": r[3]} for r in rows], "skill_updated": False}
        except sqlite3.Error as exc:
            return {"input": value, "recent_lessons": [], "error": type(exc).__name__}
    if name == "advanced_planner":
        return {"goal": value, "plan": None, "reason": "Requires task-specific reasoning; this helper does not invent an empty plan."}
    if name == "self_verifier":
        try:
            data = json.loads(value)
            if isinstance(data, dict) and "expected" in data and "observed" in data:
                verified = data["expected"] == data["observed"]
                return {"verified": verified, "reason": "exact_value_comparison", "review_required": not verified}
        except json.JSONDecodeError:
            pass
        return {"verified": False, "reason": "independent_evidence_required", "review_required": True, "goal": value}
    if name == "sandbox_runner":
        return {"isolated": False, "executed": False, "reason": "No operating-system sandbox is configured.", "target": value}
    if name == "regression_runner":
        return {"target": value, "tests": ["compile", "contract", "smoke", "security"], "regression_free": None, "executed": False}
    if name == "uncertainty_manager":
        return {"statement": value, "classification": "unverified", "confidence": 0.0, "needs_source": True}
    if name == "version_manager":
        name = Path(value).stem
        manifest = ROOT / "memory" / "skill_versions" / f"{name}.json"
        return {"target": name, "managed_revision": manifest.exists(), "rollback_available": manifest.exists(), "action_performed": False}
    if name == "project_manager":
        return {"project": value, "stages": ["understand_goal", "research", "plan", "work", "verify", "report"], "workflow_started": False}
    if name == "diagnostic_dashboard":
        try:
            with sqlite3.connect(DB) as db:
                tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                counts = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("messages", "long_term_memory", "errors", "evaluations") if table in tables}
        except sqlite3.Error:
            counts = {}
        return {"system": value or "Jarvis", "skill_files": len(list((ROOT / "skills").glob("*.py"))), "local_records": counts, "database_readable": bool(counts)}
    raise ValueError(name)
