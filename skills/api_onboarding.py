"""Open an official service page for API/OAuth setup without handling secrets."""
from __future__ import annotations
import json
import webbrowser
from urllib.parse import urlparse

RISK_LEVEL = "high"

def run(argument=None):
    try:
        if isinstance(argument, dict):
            data = argument
        else:
            raw = str(argument or "").strip()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # Accept a plain official URL emitted by a model. URL validation
                # below remains mandatory and prevents arbitrary schemes/credentials.
                import re
                match = re.search(r"https://[^\s\"']+", raw)
                data = {"url": match.group(0).rstrip(".,)") if match else raw}
        url = str(data.get("url", "")).strip()
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return {"opened": False, "human_required": False, "error": "official_https_url_required"}
        opened = webbrowser.open(url, new=2, autoraise=True)
        return {"opened": bool(opened), "url": url, "human_required": True,
                "instruction": "Wykonaj rejestrację aplikacji lub nadaj zakresy OAuth na oficjalnej stronie. Nie wklejaj sekretu do czatu. Po uzyskaniu danych użyj bezpiecznego formularza Jarvisa i napisz gotowe."}
    except Exception as exc:
        return {"opened": False, "human_required": False, "error": type(exc).__name__}
