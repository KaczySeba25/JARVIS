"""Report configured model without revealing credentials."""
import os
def run(_: str = "status"):
    return str({"provider": "Groq-compatible", "model": os.getenv("JARVIS_MODEL", "openai/gpt-oss-120b"), "key_configured": bool(os.getenv("GROQ_API_KEY")), "live_trading": False})
