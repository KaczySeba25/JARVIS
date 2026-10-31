"""Bounded mission recovery: classify failures and return a safe next action."""
from __future__ import annotations
import json

RISK_LEVEL = "low"

def run(argument=None):
    data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
    error = str(data.get("error", argument or ""))
    text = error.casefold()
    if any(x in text for x in ("captcha", "2fa", "sms", "verification", "kod")):
        category, action = "human_required", "wait_for_user"
    elif any(x in text for x in ("timeout", "connection", "429", "503")):
        category, action = "transient", "retry_once_after_research"
    elif any(x in text for x in ("permission", "access denied", "uprawn")):
        category, action = "permission", "request_or_explain_permission"
    elif any(x in text for x in ("selector", "not found", "nie znalezion")):
        category, action = "environment_changed", "take_screenshot_and_reinspect"
    else:
        category, action = "unknown", "stop_and_review"
    return {"classified": category, "recommended_action": action, "retry_allowed": category == "transient", "human_required": category == "human_required", "error": error[:500]}
