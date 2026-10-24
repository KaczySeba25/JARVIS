"""Bounded Playwright browser operator for approved workflows.

The model never receives passwords. Secret fields are filled from the local
DPAPI vault by service reference. Final submits require an approved plan.
"""
from __future__ import annotations
import json
from urllib.parse import urlparse

RISK_LEVEL = "high"
_playwright = None
_browser = None
_page = None

def _load_page():
    global _playwright, _browser, _page
    if _page is not None and not _page.is_closed():
        return _page
    from playwright.sync_api import sync_playwright
    if _playwright is None:
        _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=False)
    _page = _browser.new_page()
    return _page

def _url(value):
    parsed = urlparse(str(value or "").strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("browser_operator wymaga publicznego adresu https bez danych logowania")
    return parsed.geturl()

def run(argument=None):
    try:
        data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
        action = str(data.get("action", "")).lower()
        if action == "navigate":
            url = _url(data.get("url"))
            page = _load_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return {"ok": True, "action": action, "url": page.url, "title": page.title()}
        page = _load_page()
        if action == "inspect":
            return {"ok": True, "url": page.url, "title": page.title(), "text": page.locator("body").inner_text(timeout=10000)[:12000]}
        selector = str(data.get("selector", "")).strip()
        if not selector or len(selector) > 500:
            raise ValueError("selector_required")
        if action == "fill":
            page.locator(selector).fill(str(data.get("value", ""))[:5000])
            return {"ok": True, "action": action, "selector": selector, "value_sent": True}
        if action == "fill_secret":
            from secret_store import get
            item = get(data.get("service"))
            field = str(data.get("field", "secret")).lower()
            value = item.get("username", "") if field in {"username", "login", "email"} else item.get("secret", "")
            page.locator(selector).fill(value)
            return {"ok": True, "action": action, "selector": selector, "service": str(data.get("service")), "secret_sent": True}
        if action == "click":
            if not bool(data.get("approved")):
                return {"ok": False, "blocked": True, "reason": "approved_plan_required"}
            page.locator(selector).click(timeout=15000)
            return {"ok": True, "action": action, "selector": selector, "submitted": bool(data.get("submit", False))}
        if action == "wait":
            page.wait_for_timeout(min(max(int(data.get("milliseconds", 500)), 50), 10000))
            return {"ok": True, "action": action, "url": page.url}
        return {"ok": False, "error": "unsupported_action", "allowed": ["navigate", "inspect", "fill", "fill_secret", "click", "wait"]}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:300]}
