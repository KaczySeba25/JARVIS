"""Bounded Windows computer operator. External actions require an approved mission plan."""
from __future__ import annotations
import json
import time

RISK_LEVEL = "high"

def run(argument=None):
    data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
    action = str(data.get("action", "")).lower()
    if action in {"screenshot", "screen"}:
        from vision import run as vision_run
        return vision_run(data)
    if action in {"click", "type", "hotkey", "press", "scroll", "move"} and not bool(data.get("approved", False)):
        return {"ok": False, "blocked": True, "reason": "approved_mission_required", "message": "Sterowanie komputerem wymaga zatwierdzonej misji."}
    try:
        import pyautogui
        pyautogui.PAUSE = 0.12
        if action == "click":
            x, y = int(data["x"]), int(data["y"])
            if not (0 <= x <= 10000 and 0 <= y <= 10000):
                return {"ok": False, "error": "coordinates_out_of_range"}
            pyautogui.click(x=x, y=y, clicks=max(1, min(2, int(data.get("clicks", 1)))))
            return {"ok": True, "action": action, "x": x, "y": y}
        if action == "move":
            pyautogui.moveTo(int(data["x"]), int(data["y"]), duration=0.2)
            return {"ok": True, "action": action}
        if action == "type":
            text = str(data.get("text", ""))[:5000]
            if any(token in text.casefold() for token in ("password", "api_key", "token", "secret")):
                return {"ok": False, "blocked": True, "reason": "possible_secret_in_plain_text"}
            pyautogui.write(text, interval=0.01)
            return {"ok": True, "action": action, "characters": len(text)}
        if action == "hotkey":
            keys = [str(k).lower() for k in data.get("keys", [])][:5]
            pyautogui.hotkey(*keys)
            return {"ok": True, "action": action, "keys": keys}
        if action == "press":
            key = str(data.get("key", ""))[:30].lower()
            pyautogui.press(key)
            return {"ok": True, "action": action, "key": key}
        if action == "scroll":
            amount = max(-20, min(20, int(data.get("amount", 0))))
            pyautogui.scroll(amount)
            return {"ok": True, "action": action, "amount": amount}
        if action == "wait":
            time.sleep(max(0.05, min(10, float(data.get("seconds", 0.5)))))
            return {"ok": True, "action": action}
        return {"ok": False, "error": "unsupported_action", "allowed": ["screenshot", "click", "move", "type", "hotkey", "press", "scroll", "wait"]}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:500]}
