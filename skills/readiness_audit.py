"""Report whether Jarvis is ready; never reports green while .env exists."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))
from readiness import audit

def run(_: str = "status"):
    return str(audit())
