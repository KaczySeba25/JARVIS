"""Report available model providers without exposing secrets."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))
from local_provider import available

def run(_: str = "status"):
    return str({"groq_configured": bool(os.getenv("GROQ_API_KEY")), "ollama_local": available(), "live_trading": False})
