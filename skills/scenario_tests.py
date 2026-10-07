"""End-to-end smoke scenarios for core Jarvis safety and skills."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))
from jarvis_core import JarvisCore

def run(_: str = "all"):
    jarvis = JarvisCore(confirm=lambda _: False)
    checks = {
        "hello_skill": "dziala" in jarvis.run_skill("hello"),
        "unknown_skill_safe": "Błąd skilla" in jarvis.run_skill("missing_skill"),
        "risky_action_blocked": "anulowana" in jarvis.run_skill("system_cmd", "echo blocked"),
        "personality": "Jarvis" in jarvis.system_prompt(),
    }
    return "SCENARIOS " + ("PASS" if all(checks.values()) else "FAIL") + " " + str(checks)
