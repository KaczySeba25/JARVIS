"""Choose a configured hosted model or an already-running free local model."""
from __future__ import annotations

import os
from openai import OpenAI

try:
    from .local_provider import models as local_models
except ImportError:
    from local_provider import models as local_models


class ModelRouter:
    def __init__(self):
        self.model = os.getenv("JARVIS_MODEL", "openai/gpt-oss-120b")
        self.provider = "unavailable"
        self.client = None
        key = os.getenv("JARVIS_API_KEY") or os.getenv("GROQ_API_KEY")
        custom_url = os.getenv("JARVIS_BASE_URL")
        if key:
            self.client = OpenAI(api_key=key, base_url=custom_url or "https://api.groq.com/openai/v1")
            self.provider = "hosted"
            return

        local_url = os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        installed = local_models(local_url)
        if installed:
            requested = os.getenv("JARVIS_LOCAL_MODEL")
            self.model = requested if requested in installed else installed[0]
            self.client = OpenAI(api_key="local", base_url=local_url + "/v1")
            self.provider = "local"

    def available(self):
        return [self.model] if self.client else []

    def complete(self, messages, **kwargs):
        if not self.client:
            raise RuntimeError("Nie skonfigurowano modelu online ani nie znaleziono uruchomionego modelu lokalnego.")
        return self.client.chat.completions.create(model=self.model, messages=messages, **kwargs)
