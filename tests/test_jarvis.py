import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "agent"))
from jarvis_core import JarvisCore
from planner import build_plan

def test_plan_marks_system_actions_high_risk():
    assert build_plan("x", ["system_cmd"])[0].requires_confirmation

def test_hello_skill_is_callable():
    assert "dziala" in JarvisCore().run_skill("hello")

def test_unknown_skill_is_safe():
    assert "Błąd skilla" in JarvisCore().run_skill("does_not_exist")
