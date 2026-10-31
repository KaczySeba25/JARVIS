"""Local Ollama model management for Jarvis.

All operations target the user's local Ollama instance or its local CLI. No
cloud account, API key or paid service is created by this module.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_URL = "http://127.0.0.1:11434"
MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
RECOMMENDED_MODELS = [
    ("qwen3.5:4b", "Dobry ogólny model, rozsądny dla CPU/GPU"),
    ("qwen3:4b", "Szybki model ogólny do codziennych zadań"),
    ("gemma3:4b", "Lekki model do rozmowy i tekstu"),
    ("qwen3-vl:2b", "Lekki model z obsługą obrazu, jeśli dostępny"),
    ("llama3.2:3b", "Lekki model ogólny"),
]


def base_url(value: str | None = None) -> str:
    return (value or os.getenv("JARVIS_OLLAMA_URL", DEFAULT_URL)).rstrip("/")


def validate_model(name: str) -> str:
    name = str(name or "").strip()
    if not name or not MODEL_RE.fullmatch(name):
        raise ValueError("Nieprawidłowa nazwa modelu Ollama.")
    return name


def _request(path: str, method: str = "GET", payload=None, url: str | None = None, timeout: float = 4.0):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(base_url(url) + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def status(url: str | None = None) -> dict:
    try:
        payload = _request("/api/tags", url=url, timeout=2.0)
        return {"available": True, "models": payload.get("models", [])}
    except Exception as exc:
        return {"available": False, "models": [], "error": type(exc).__name__}


def models(url: str | None = None) -> list[str]:
    payload = status(url)
    return [str(item.get("name")) for item in payload.get("models", []) if item.get("name")]


def delete(model: str, url: str | None = None) -> dict:
    model = validate_model(model)
    return _request("/api/delete", method="DELETE", payload={"name": model}, url=url, timeout=10.0)


def cli_path() -> str | None:
    return shutil.which("ollama")


def pull(model: str, on_line=None, cancel_event: threading.Event | None = None, url: str | None = None) -> dict:
    """Pull a model through the locally installed Ollama CLI.

    The caller owns the UI thread. Output is streamed line by line so the
    desktop app can display progress. The model name is validated first.
    """
    model = validate_model(model)
    executable = cli_path()
    if not executable:
        return {"ok": False, "error": "OLLAMA_NOT_FOUND", "message": "Nie znaleziono programu Ollama."}
    command = [executable, "pull", model]
    env = os.environ.copy()
    if url and base_url(url) != DEFAULT_URL:
        env["OLLAMA_HOST"] = base_url(url).replace("http://", "").replace("https://", "")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=env)
    except OSError as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}
    lines = []
    assert process.stdout is not None
    for line in process.stdout:
        line = line.rstrip()
        if line:
            lines.append(line)
            if on_line:
                on_line(line)
        if cancel_event and cancel_event.is_set():
            process.terminate()
            return {"ok": False, "cancelled": True, "message": "Pobieranie zatrzymane przez użytkownika.", "output": lines[-20:]}
    code = process.wait()
    return {"ok": code == 0, "returncode": code, "message": "Model zainstalowany." if code == 0 else "Ollama nie zainstalowała modelu.", "output": lines[-20:]}
