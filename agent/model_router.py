"""Choose a hosted model or an already-running free local model, as set by the user."""
from __future__ import annotations

import os
from openai import OpenAI

try:
    from .local_provider import models as local_models
    from . import user_settings
except ImportError:
    from local_provider import models as local_models
    import user_settings


class ModelRouter:
    def __init__(self):
        self.prefs = user_settings.load()
        self.model = ""
        self.provider = "unavailable"
        self.client = None
        self.warning = ""
        mode = self.prefs["provider"]
        key = os.getenv("JARVIS_API_KEY") or os.getenv("GROQ_API_KEY")
        custom_url = os.getenv("JARVIS_BASE_URL")
        self.local_url = (self.prefs["ollama_url"] or os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.installed = []

        if mode in ("auto", "hosted") and key:
            self.model = self.prefs["hosted_model"] or os.getenv("JARVIS_MODEL", "openai/gpt-oss-120b")
            self.client = OpenAI(api_key=key, base_url=custom_url or "https://api.groq.com/openai/v1")
            self.provider = "hosted"
            self._hosted_client = self.client
            return
        if mode == "hosted":
            self.warning = "Wybrano model online, ale w pliku .env nie ma klucza API."
            return

        self.installed = local_models(self.local_url)
        if not self.installed:
            self.warning = "Ollama nie odpowiada albo nie ma zainstalowanych modeli. Uruchom Ollama."
            return
        explicit = self.prefs["local_model"]
        requested = explicit or os.getenv("JARVIS_LOCAL_MODEL", "")
        if requested in self.installed:
            self.model = requested
        elif explicit:
            self.warning = f"Model '{explicit}' nie jest zainstalowany w Ollama. Dostępne: {', '.join(self.installed)}."
            return
        else:
            self.model = self.installed[0]
        self.client = OpenAI(api_key="local", base_url=self.local_url + "/v1")
        self.provider = "local"

    def _use_local_fallback(self):
        if self.provider == "local":
            return False
        installed = local_models(self.local_url)
        if not installed:
            return False
        requested = self.prefs["local_model"] or os.getenv("JARVIS_LOCAL_MODEL", "")
        self.installed = installed
        self.model = requested if requested in installed else installed[0]
        self.client = OpenAI(api_key="local", base_url=self.local_url + "/v1")
        self.provider = "local"
        self.warning = "Usługa online chwilowo nie odpowiada; przełączono na lokalny model Ollama."
        return True

    def available(self):
        return [self.model] if self.client else []

    def describe(self) -> dict:
        return {"provider": self.provider, "model": self.model, "warning": self.warning,
                "installed_local": self.installed, "preferences": dict(self.prefs)}

    def complete(self, messages, **kwargs):
        if not self.client:
            raise RuntimeError(self.warning or "Nie skonfigurowano modelu online ani nie znaleziono uruchomionego modelu lokalnego.")
        try:
            return self.client.chat.completions.create(model=self.model, messages=messages, **kwargs)
        except Exception as first_error:
            if self._use_local_fallback():
                try:
                    return self.client.chat.completions.create(model=self.model, messages=messages, **kwargs)
                except Exception as fallback_error:
                    raise RuntimeError(f"Online i lokalny model nie odpowiedziały: {type(fallback_error).__name__}") from fallback_error
            raise first_error
