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
    "appearance": "dark",        # dark/light/system; desktop UI preference
    "accent_color": "blue",      # blue/cyan/purple/green
    "font_scale": "normal",      # small/normal/large
    "voice_input": "off",        # off/on; enabled only when local speech tools work
    "voice_output": "off",       # off/on; enabled only when local TTS works
    "notifications": "on",       # local progress notifications
    "compact_mode": "off",       # denser desktop layout
    "language": "pl",            # pl/en response preference
    "user_name": "Sebastian",    # name used by the local persona
}


def _clean(data: dict) -> dict:
    result = dict(DEFAULTS)
    if isinstance(data, dict):
        for key in DEFAULTS:
            value = data.get(key, DEFAULTS[key])
            result[key] = value.strip()[:200] if isinstance(value, str) else DEFAULTS[key]
    if result["provider"] not in PROVIDERS:
        result["provider"] = "auto"
    if result["appearance"] not in {"dark", "light", "system"}:
        result["appearance"] = "dark"
    if result["accent_color"] not in {"blue", "cyan", "purple", "green"}:
        result["accent_color"] = "blue"
    if result["font_scale"] not in {"small", "normal", "large"}:
        result["font_scale"] = "normal"
    for key in ("voice_input", "voice_output", "notifications", "compact_mode"):
        if result[key] not in {"on", "off"}:
            result[key] = "off" if key != "notifications" else "on"
    if result["language"] not in {"pl", "en"}:
        result["language"] = "pl"
    result["user_name"] = result["user_name"][:80]
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
