"""Free microphone input for Jarvis.

Uses the installed microphone stack and the keyless Google speech endpoint from
SpeechRecognition when available. Audio is sent only for transcription; the UI
shows a clear listening state and errors are returned instead of being hidden.
"""
from __future__ import annotations


def available() -> bool:
    try:
        import pyaudio  # noqa: F401
        import speech_recognition  # noqa: F401
        return True
    except ImportError:
        return False


def listen(language: str = "pl-PL", timeout: int = 6, phrase_time_limit: int = 16) -> dict:
    if not available():
        return {"ok": False, "error": "brak_bibliotek_audio", "message": "Brak bibliotek mikrofonu w środowisku JARVISA."}
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.45)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        text = recognizer.recognize_google(audio, language=language).strip()
        if not text:
            return {"ok": False, "error": "pusta_transkrypcja", "message": "Nie rozpoznałem żadnych słów."}
        return {"ok": True, "text": text, "language": language, "provider": "Google Speech keyless"}
    except Exception as exc:
        name = type(exc).__name__
        messages = {
            "WaitTimeoutError": "Nie usłyszałem mowy w wyznaczonym czasie.",
            "UnknownValueError": "Nie zrozumiałem nagrania. Spróbuj mówić bliżej mikrofonu.",
            "RequestError": "Usługa transkrypcji nie odpowiedziała. Sprawdź internet.",
            "OSError": "Nie mogę otworzyć mikrofonu. Sprawdź uprawnienia Windows i urządzenie domyślne.",
        }
        return {"ok": False, "error": name, "message": messages.get(name, f"Mikrofon zgłosił błąd ({name}).")}
