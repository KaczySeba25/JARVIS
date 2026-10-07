import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "agent"))
from loop_guard import LoopGuard
from structured_plan import Plan, Step

def test_plan_validation():
    assert Plan("goal", [Step("step", risk="low")]).validate()

def test_loop_guard_stops_repetition():
    guard = LoopGuard()
    assert guard.allow("same")
    assert guard.allow("same")
    assert guard.allow("same")
    assert not guard.allow("same")
