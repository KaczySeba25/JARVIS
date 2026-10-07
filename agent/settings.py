"""Validated runtime limits and preferences from the local environment."""
import os
from dataclasses import dataclass


def _bounded_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


@dataclass(frozen=True)
class Settings:
    model: str = (os.getenv("JARVIS_MODEL", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b")
    max_retries: int = _bounded_int("JARVIS_MAX_RETRIES", 3, 1, 5)
    max_context_messages: int = _bounded_int("JARVIS_MAX_CONTEXT", 20, 2, 60)
    max_tool_steps: int = _bounded_int("JARVIS_MAX_TOOL_STEPS", 16, 1, 32)
    require_research_for_unknown: bool = os.getenv("JARVIS_REQUIRE_RESEARCH", "1").strip() == "1"


SETTINGS = Settings()
