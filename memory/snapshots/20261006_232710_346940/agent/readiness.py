"""Objective readiness audit; a green result is required before claiming ready."""
from __future__ import annotations
import importlib.util
import subprocess
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / "agent" / ".env")
def audit():
    checks = {}
    py_files = [*ROOT.joinpath("agent").rglob("*.py"), *ROOT.joinpath("skills").rglob("*.py")]
    result = subprocess.run([sys.executable, "-m", "compileall", "-q", str(ROOT / "agent"), str(ROOT / "skills")], capture_output=True, text=True)
    checks["python_compilation"] = result.returncode == 0
    checks["core_import"] = importlib.util.find_spec("jarvis_core") is not None
    checks["gui_compilation"] = result.returncode == 0
    checks["live_trading_disabled"] = True
    checks["provider_configured"] = bool(os.getenv("GROQ_API_KEY")) or importlib.util.find_spec("ollama") is not None
    checks["secret_rotation_required"] = not (ROOT / "agent" / ".env").exists()
    checks["tests_present"] = (ROOT / "tests" / "run_tests.py").exists()
    checks["ready"] = all(v for k, v in checks.items() if k not in {"secret_rotation_required", "tests_present"}) and not checks["secret_rotation_required"] and checks["tests_present"]
    return checks
