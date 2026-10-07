"""Discover already installed local Ollama models without downloading anything."""
from __future__ import annotations

import json
import os
from urllib.request import urlopen


def models(base_url: str | None = None) -> list[str]:
    url = (base_url or os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
    try:
        with urlopen(url + "/api/tags", timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [item["name"] for item in payload.get("models", []) if item.get("name")]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def available() -> bool:
    return bool(models())
