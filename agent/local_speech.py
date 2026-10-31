"""Optional free local speech for the Jarvis desktop cockpit.

No cloud service or API key is used. Windows SAPI is the fallback when
pyttsx3 is unavailable. Voice names depend on voices installed on Windows.
"""
from __future__ import annotations

import base64
import os
import subprocess
import threading

_LOCK = threading.Lock()


def available() -> bool:
    try:
        import pyttsx3  # noqa: F401
        return True
    except ImportError:
        return os.name == "nt"


def _pyttsx3_speak(text: str) -> bool:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty("voices") or []
        preferred = ("jarvis", "david", "mark", "george", "male")
        for voice in voices:
            label = f"{getattr(voice, 'name', '')} {getattr(voice, 'id', '')}".lower()
            if any(item in label for item in preferred):
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 0.9)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        return True
    except Exception:
        return False


def _sapi_speak(text: str) -> bool:
    if os.name != "nt":
        return False
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    script = (
        "$b=[Convert]::FromBase64String('" + encoded + "');"
        "$t=[Text.Encoding]::UTF8.GetString($b);"
        "Add-Type -AssemblyName System.Speech;"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$s.Rate=0; $s.Volume=90; $s.Speak($t);"
    )
    try:
        result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], timeout=90, capture_output=True)
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def speak(text: str) -> bool:
    """Speak locally; return whether a local engine completed successfully."""
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return False
    with _LOCK:
        return _pyttsx3_speak(clean) or _sapi_speak(clean)
