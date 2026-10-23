"""User-editable model preferences stored locally; never stores API keys or passwords."""
from __future__ import annotations

import json
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "memory" / "user_settings.json"
_LOCK = threading.RLock()

PROVIDERS = ("auto", "local", "hosted")
DEFAULTS = {
    "provider": "auto",          # auto: hosted if an API key exists, otherwise local Ollama
    "local_model": "",           # empty: first installed Ollama model
    "hosted_model": "",          # empty: JARVIS_MODEL from .env
    "ollama_url": "",            # empty: JARVIS_OLLAMA_URL or http://127.0.0.1:11434
}


def _clean(data: dict) -> dict:
    result = dict(DEFAULTS)
    if isinstance(data, dict):
        for key in DEFAULTS:
            value = data.get(key, DEFAULTS[key])
            result[key] = value.strip()[:200] if isinstance(value, str) else DEFAULTS[key]
    if result["provider"] not in PROVIDERS:
        result["provider"] = "auto"
    if result["ollama_url"] and not result["ollama_url"].startswith(("http://127.0.0.1", "http://localhost")):
        result["ollama_url"] = ""   # keep prompts and files on this computer
    return result


def load() -> dict:
    with _LOCK:
        try:
            return _clean(json.loads(FILE.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return dict(DEFAULTS)


def save(**changes) -> dict:
    with _LOCK:
        data = load()
        data.update({key: value for key, value in changes.items() if key in DEFAULTS})
        data = _clean(data)
        FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary = FILE.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(FILE)
        return data
