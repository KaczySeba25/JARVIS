import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "agent"))
from critic import critique_plan, critique_results
from structured_plan import Plan, Step

def test_critic_rejects_empty_plan():
    assert not critique_plan(Plan("x")).approved

def test_critic_accepts_completed_result():
    class R: status = "done"; result = "ok"
    assert critique_results([R()]).approved
