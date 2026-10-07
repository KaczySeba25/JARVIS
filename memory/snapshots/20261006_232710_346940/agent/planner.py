"""Deterministic planning helpers used before model/tool execution."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PlanStep:
    goal: str
    tool: str | None
    risk: str = "low"
    requires_confirmation: bool = False

def classify_risk(tool: str | None) -> str:
    if tool in {"system_cmd", "code_writer", "vault_manager", "universal_login", "live_trading"}:
        return "high"
    if tool in {"paper_trading", "backtest", "file_manager"}:
        return "medium"
    return "low"

def build_plan(goal: str, tools: list[str]) -> list[PlanStep]:
    return [PlanStep(goal, tool, classify_risk(tool), classify_risk(tool) == "high") for tool in tools]
