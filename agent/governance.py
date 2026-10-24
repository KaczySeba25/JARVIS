"""Local governance, evidence, quality and error memory for Jarvis."""
from __future__ import annotations
import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "memory" / "jarvis.sqlite3"

@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    confidence: float
    verified: bool = False

@dataclass(frozen=True)
class Quality:
    correctness: float
    completeness: float
    confidence: float
    risk: str
    needs_review: bool

def init():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY, claim TEXT, source TEXT, confidence REAL, verified INTEGER, created REAL);
        CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, goal TEXT, decision TEXT, reason TEXT, created REAL);
        CREATE TABLE IF NOT EXISTS errors (id INTEGER PRIMARY KEY, symptom TEXT, cause TEXT, fix TEXT, created REAL);
        CREATE TABLE IF NOT EXISTS evaluations (id INTEGER PRIMARY KEY, task TEXT, result TEXT, quality TEXT, created REAL);
        CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY, topic TEXT, symptom TEXT, cause TEXT, remedy TEXT, confidence REAL, source TEXT, created REAL);
        """)

def save_evidence(item: Evidence):
    init()
    with sqlite3.connect(DB_FILE) as db:
        db.execute("INSERT INTO evidence(claim,source,confidence,verified,created) VALUES(?,?,?,?,?)", (item.claim,item.source,item.confidence,int(item.verified),time.time()))
        db.commit()

def save_decision(goal, decision, reason):
    init()
    with sqlite3.connect(DB_FILE) as db:
        db.execute("INSERT INTO decisions(goal,decision,reason,created) VALUES(?,?,?,?)", (goal,decision,reason,time.time()))
        db.commit()

def save_error(symptom, cause, fix):
    init()
    with sqlite3.connect(DB_FILE) as db:
        db.execute("INSERT INTO errors(symptom,cause,fix,created) VALUES(?,?,?,?)", (symptom,cause,fix,time.time()))
        db.commit()

def save_lesson(topic, symptom, cause, remedy, confidence=0.5, source="runtime"):
    init()
    with sqlite3.connect(DB_FILE) as db:
        db.execute("INSERT INTO lessons(topic,symptom,cause,remedy,confidence,source,created) VALUES(?,?,?,?,?,?,?)",
                   (str(topic)[:300], str(symptom)[:500], str(cause)[:500], str(remedy)[:1000], max(0.0, min(float(confidence), 1.0)), str(source)[:200], time.time()))
        db.commit()

def recent_lessons(topic="", limit=8):
    init(); limit = max(1, min(int(limit), 50))
    with sqlite3.connect(DB_FILE) as db:
        if topic:
            rows = db.execute("SELECT topic,symptom,cause,remedy,confidence,source,created FROM lessons WHERE topic LIKE ? ORDER BY id DESC LIMIT ?", (f"%{topic}%", limit)).fetchall()
        else:
            rows = db.execute("SELECT topic,symptom,cause,remedy,confidence,source,created FROM lessons ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(zip(("topic","symptom","cause","remedy","confidence","source","created"), row)) for row in rows]

def evaluate(task, result, confidence=0.7, risk="low") -> Quality:
    text = result or ""
    bad = any(word in text.lower() for word in ("błąd", "error", "nie udało", "anulowana"))
    quality = Quality(0.3 if bad else 0.8, 0.4 if bad else 0.75, confidence, risk, bad or confidence < 0.75 or risk in {"high", "critical"})
    init()
    with sqlite3.connect(DB_FILE) as db:
        db.execute("INSERT INTO evaluations(task,result,quality,created) VALUES(?,?,?,?)", (task,text,json.dumps(asdict(quality),ensure_ascii=False),time.time()))
        db.commit()
    return quality
