"""Execute a simple validated plan: objective|tool|argument;..."""
import json
try:
    from plan_executor import PlanExecutor
    from structured_plan import Plan, Step
    from critic import critique_plan, critique_results
except ImportError:
    from agent.plan_executor import PlanExecutor
    from agent.structured_plan import Plan, Step
    from agent.critic import critique_plan, critique_results

def run(command: str):
    steps = []
    for raw in (command or "").split(";"):
        parts = raw.split("|", 2)
        if len(parts) < 2: continue
        steps.append(Step(parts[0], parts[1], parts[2] if len(parts) == 3 else None))
    plan = Plan("manual plan", steps)
    before = critique_plan(plan)
    if not before.approved: return json.dumps(before.__dict__, ensure_ascii=False, default=list)
    executor = PlanExecutor(lambda tool, arg: "tool execution delegated: " + str(tool), lambda _: False)
    results = executor.execute(plan)
    after = critique_results(results)
    return json.dumps({"before": before.__dict__, "results": [r.__dict__ for r in results], "after": after.__dict__}, ensure_ascii=False, default=list)
