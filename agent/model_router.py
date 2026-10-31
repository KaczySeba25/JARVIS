"""Choose the best configured model with bounded, automatic fallbacks.

Only providers explicitly configured by the user are considered. The router never
discovers random free APIs or sends data to an unknown service.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
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
        self._candidates = []
        self.warning = ""
        mode = self.prefs["provider"]
        key = os.getenv("JARVIS_API_KEY") or os.getenv("GROQ_API_KEY")
        custom_url = os.getenv("JARVIS_BASE_URL")
        self.local_url = (self.prefs["ollama_url"] or os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.installed = []

        if mode in ("auto", "hosted"):
            hosted = self._configured_hosted()
            if hosted:
                self._activate(*hosted[0])
                self._candidates = hosted[1:]
                return
        if mode == "hosted":
            self.warning = "Wybrano model online, ale w pliku .env nie ma klucza API."
            return

        self.installed = local_models(self.local_url)
        if not self.installed:
            self.warning = "Ollama nie odpowiada albo nie ma zainstalowanych modeli. Uruchom Ollama."
            return
        local = self._local_candidates()
        if not local:
            self.warning = "Nie znaleziono pasującego modelu lokalnego."
            return
        self._activate(*local[0])
        self._candidates = local[1:]

    def _use_local_fallback(self):
        installed = local_models(self.local_url)
        if not installed:
            return False
        self.installed = installed
        local = self._local_candidates()
        if not local:
            return False
        self._activate(*local[0])
        self._candidates = local[1:]
        self.warning = "Usługa online nie odpowiedziała; przełączono na skonfigurowany model lokalny Ollama."
        return True

    def _activate(self, provider, model, key, base_url):
        self.provider, self.model = provider, model
        self.client = OpenAI(api_key=key, base_url=base_url, timeout=float(os.getenv("JARVIS_MODEL_TIMEOUT", "8")))

    def _configured_hosted(self):
        requested = self.prefs["hosted_model"] or os.getenv("JARVIS_MODEL", "")
        result = []
        groq = os.getenv("GROQ_API_KEY") or os.getenv("JARVIS_API_KEY")
        if groq:
            base = os.getenv("JARVIS_BASE_URL") or "https://api.groq.com/openai/v1"
            requested = self._live_model_or_fallback(groq, base, requested, ("openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"))
            if requested:
                result.append(("hosted:groq", requested, groq, base))
        gemini = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini:
            result.append(("hosted:gemini", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), gemini, "https://generativelanguage.googleapis.com/v1beta/openai/"))
        nvidia = os.getenv("NVIDIA_API_KEY")
        if nvidia:
            result.append(("hosted:nvidia", os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct"), nvidia, "https://integrate.api.nvidia.com/v1"))
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            result.append(("hosted:openai", requested or "gpt-4o-mini", openai_key, "https://api.openai.com/v1"))
        return result

    @staticmethod
    def _live_model_or_fallback(key, base_url, requested, preferred):
        """Avoid stale model names while keeping provider discovery bounded."""
        try:
            client = OpenAI(api_key=key, base_url=base_url, timeout=5)
            available = {str(item.id) for item in client.models.list().data}
            if requested in available:
                return requested
            return next((name for name in preferred if name in available), next(iter(available), ""))
        except Exception:
            # A provider outage is handled later by complete(); do not block
            # startup just because model discovery is unavailable.
            return requested or preferred[0]

    def _local_candidates(self):
        explicit = self.prefs["local_model"] or os.getenv("JARVIS_LOCAL_MODEL", "")
        if explicit:
            if explicit not in self.installed:
                self.warning = f"Model '{explicit}' nie jest zainstalowany w Ollama."
                return []
            ordered = [explicit] + [name for name in self.installed if name != explicit]
        else:
            # Prefer small, instruction-capable models. The old API order was
            # arbitrary and often selected a 27B model on CPU.
            priority = ("qwen3.5:4b", "qwen3:4b", "openhermes:latest", "qwen3-vl:2b", "gemma4:26b", "qwen3.8:27b")
            rank = {name: index for index, name in enumerate(priority)}
            ordered = sorted(self.installed, key=lambda name: (rank.get(name, 100), self._size_hint(name), name))
        return [("local", name, "local", self.local_url + "/v1") for name in ordered]

    @staticmethod
    def _size_hint(name):
        match = re.search(r":(\d+(?:\.\d+)?)b", name.lower())
        return float(match.group(1)) if match else 10.0

    def available(self):
        return [self.model] if self.client else []

    def failover(self):
        """Select the next safe configured model without losing conversation state."""
        if self.provider.startswith("hosted"):
            self.installed = local_models(self.local_url)
            local = self._local_candidates()
            if local:
                self._activate(*local[0])
                self._candidates = local[1:]
                self.warning = "Provider online nie odpowiedział; kontynuuję na Ollama."
                return True
        if self._candidates:
            provider, model, key, base = self._candidates.pop(0)
            self._activate(provider, model, key, base)
            return True
        return False

    def describe(self) -> dict:
        return {"provider": self.provider, "model": self.model, "warning": self.warning,
                "installed_local": self.installed, "profiles": ["general", "fast", "code", "vision", "private"],
                "preferences": dict(self.prefs)}

    def select_profile(self, profile: str):
        """Select among already configured models; never discovers or creates a provider."""
        profile = str(profile or "general").lower()
        if profile in {"private", "local"}:
            local = self._local_candidates()
            if local:
                self._activate(*local[0])
                self._candidates = local[1:]
                return {"selected": self.provider, "model": self.model, "profile": profile}
        if self.provider.startswith("hosted") and profile == "general":
            return {"selected": self.provider, "model": self.model, "profile": profile}
        candidates = self._local_candidates()
        if candidates:
            names = [item[1].lower() for item in candidates]
            needles = {"code": ("coder", "qwen"), "vision": ("vl", "vision", "llava"), "fast": ("1.5b", "2b", "3b", "4b")}.get(profile, ())
            chosen = next((item for item in candidates if any(needle in item[1].lower() for needle in needles)), candidates[0])
            self._activate(*chosen)
            self._candidates = [item for item in candidates if item[1] != chosen[1]]
            return {"selected": self.provider, "model": self.model, "profile": profile}
        return {"selected": self.provider, "model": self.model, "profile": profile, "fallback": True}

    def complete(self, messages, **kwargs):
        profile = kwargs.pop("profile", "general")
        self.select_profile(profile)
        if not self.client:
            raise RuntimeError(self.warning or "Nie skonfigurowano modelu online ani nie znaleziono uruchomionego modelu lokalnego.")
        if self.provider.startswith("hosted:groq") and "reasoning_effort" not in kwargs and "gpt-oss" in self.model:
            # Groq GPT-OSS can spend the whole small completion budget on hidden
            # reasoning and return an empty message. Keep a useful answer budget.
            kwargs["reasoning_effort"] = "low"
            kwargs["max_tokens"] = max(int(kwargs.get("max_tokens", 2048)), 8192)
        errors = []
        deadline = time.monotonic() + max(5.0, float(os.getenv("JARVIS_MAX_MODEL_SECONDS", "25")))
        candidates = [(self.provider, self.model, self.client)] + [
            (provider, model, OpenAI(api_key=key, base_url=base, timeout=float(os.getenv("JARVIS_MODEL_TIMEOUT", "20"))))
            for provider, model, key, base in self._candidates
        ]
        # Add local candidates after an online failure, preserving context.
        if self.provider.startswith("hosted"):
            for provider, model, key, base in self._local_candidates():
                candidates.append((provider, model, OpenAI(api_key=key, base_url=base, timeout=float(os.getenv("JARVIS_MODEL_TIMEOUT", "20")))))
        for provider, model, client in candidates:
            if time.monotonic() >= deadline:
                break
            try:
                response = client.chat.completions.create(model=model, messages=messages, **kwargs)
                if (provider, model) != (self.provider, self.model):
                    self.provider, self.model, self.client = provider, model, client
                    self.warning = f"Automatycznie przełączono na {provider}/{model} po nieudanej próbie poprzedniego modelu."
                return response
            except Exception as exc:
                errors.append(f"{provider}/{model}:{type(exc).__name__}")
        raise RuntimeError("Żaden skonfigurowany model nie odpowiedział: " + ", ".join(errors[-6:]))
