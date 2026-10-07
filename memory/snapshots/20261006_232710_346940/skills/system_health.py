"""Read-only Jarvis health check."""
import importlib.util
import shutil
import sqlite3
from pathlib import Path

def run(_: str = "status"):
    root = Path(__file__).resolve().parent.parent
    db = root / "memory" / "jarvis.sqlite3"
    checks = {
        "python": True,
        "sqlite": db.exists(),
        "groq_key_present": bool(__import__("os").getenv("GROQ_API_KEY")),
        "disk_free_gb": round(shutil.disk_usage(root).free / (1024**3), 2),
        "core_importable": importlib.util.find_spec("jarvis_core") is not None,
    }
    return str(checks)
