"""Dependency-free smoke test runner for the Jarvis project."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "agent"))
sys.path.insert(0, str(Path(__file__).parents[1]))

def main():
    from jarvis_core import JarvisCore
    from structured_plan import Plan, Step
    from critic import critique_plan
    from loop_guard import LoopGuard
    from capability_audit import audit_skills
    j = JarvisCore(confirm=lambda _: False)
    j.run_skill("emergency_stop", "reset")
    assert "dziala" in j.run_skill("hello")
    assert "anulowana" in j.run_skill("system_cmd", "echo denied")
    assert not critique_plan(Plan("empty")).approved
    guard = LoopGuard()
    assert [guard.allow("x") for _ in range(4)] == [True, True, True, False]
    assert Plan("ok", [Step("one")]).validate()
    assert j.run_skill("autonomy_status") is not None
    assert j.run_skill("queue_worker") is not None
    assert j.run_skill("resume_manager") is not None
    assert "ready" in j.run_skill("integration_diagnostics")
    assert "review_required" in j.run_skill("runtime_cycle", "smoke")
    assert "diagnostics.html" in j.run_skill("diagnostics_panel")
    assert "build_all" in j.run_skill("skill_builder", "invalid")
    findings = audit_skills(Path(__file__).parents[1] / "skills")
    assert findings and all(item.score >= 60 for item in findings)
    print("JARVIS_SMOKE_TESTS: PASS")

if __name__ == "__main__":
    main()
