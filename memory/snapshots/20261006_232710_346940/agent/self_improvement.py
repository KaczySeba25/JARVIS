"""Supervised self-improvement loop for Jarvis-created skills."""
from __future__ import annotations
import json
import re
import time
from pathlib import Path
from research_engine import deep_research
from skill_lifecycle import create_draft, validate, promote
from governance import save_decision, save_evidence

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "memory" / "improvement_runs.jsonl"

def improve(skill_name: str, goal: str, code: str) -> dict:
    started = time.time()
    record = {"skill": skill_name, "goal": goal, "stage": "research", "promoted": False}
    try:
        research = deep_research(goal)
        record["research_ok"] = research.startswith("RESEARCH RESULT - źródła") and "http" in research
        record["research_sources"] = list(dict.fromkeys(re.findall(r"https?://[^\s]+", research)))[:10]
        record["researched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not record["research_ok"]:
            record["stage"] = "blocked_research"
            record["error"] = "Brak potwierdzonych źródeł; draft nie został utworzony."
            raise RuntimeError(record["error"])
        record["stage"] = "draft"
        create_draft(skill_name, code)
        record["stage"] = "validation"
        validation = validate(skill_name)
        record["validation"] = validation
        record["stage"] = "validation"
        save_decision(goal, "draft_created", json.dumps(validation, ensure_ascii=False))
        save_evidence(__import__("governance").Evidence(goal, "research_engine", 0.7, bool(record["research_ok"])))
        if validation["syntax"] and validation["execution"]:
            # The user has explicitly authorized Jarvis to improve its own
            # skills. New code remains high-risk at runtime and is backed up.
            outcome = promote(skill_name, confirm=True, metadata={
                "goal": goal[:1000], "research_sources": record["research_sources"],
                "verified_at": record["researched_at"], "validation": validation,
                "limitations": ["Import and static checks do not prove real task quality.", "Runtime execution remains restricted and high-risk."],
            })
            record["promoted"] = "aktywow" in outcome
            record["promotion"] = outcome
            record["stage"] = "promoted" if record["promoted"] else "validation_blocked"
        else:
            record["review_required"] = True
            record["stage"] = "validation_blocked"
    except Exception as exc:
        record["stage"] = "blocked"
        record["error"] = str(exc)
    record["duration_s"] = round(time.time() - started, 3)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
