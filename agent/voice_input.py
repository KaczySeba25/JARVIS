"""Free Polish microphone input with device selection and diagnostics."""
from __future__ import annotations


def available() -> bool:
    try:
        import pyaudio  # noqa: F401
        import speech_recognition  # noqa: F401
        return True
    except ImportError:
        return False


def list_microphones() -> list[dict]:
    """Return input devices without opening or recording from them."""
    if not available():
        return []
    try:
        import speech_recognition as sr
        import pyaudio
        audio = pyaudio.PyAudio()
        names = sr.Microphone.list_microphone_names()
        result = []
        for index, name in enumerate(names):
            try:
                info = audio.get_device_info_by_index(index)
            except Exception:
                continue
            if int(info.get("maxInputChannels", 0)) > 0:
                result.append({"index": index, "name": str(name), "rate": int(info.get("defaultSampleRate", 44100))})
        audio.terminate()
        return result
    except Exception:
        return []


def preferred_microphone() -> dict | None:
    """Prefer the physical laptop microphone over Sound Mapper or Bluetooth hands-free."""
    devices = list_microphones()
    if not devices:
        return None
    def score(item):
        name = item["name"].casefold()
        value = 0
        if "conexant" in name:
            value += 100
        if "microphone (" in name:
            value += 40
        if "sound mapper" in name or "podstawowy sterownik" in name:
            value -= 50
        if "headset" in name or "bluetooth" in name:
            value -= 20
        return value
    return sorted(devices, key=lambda item: (score(item), -item["index"]), reverse=True)[0]


def listen(language: str = "pl-PL", timeout: int = 8, phrase_time_limit: int = 18, device_index: int | None = None) -> dict:
    if not available():
        return {"ok": False, "error": "brak_bibliotek_audio", "message": "Brak bibliotek mikrofonu w środowisku JARVISA."}
    device = None
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        recognizer.phrase_threshold = 0.2
        recognizer.non_speaking_duration = 0.35
        device = next((item for item in list_microphones() if item["index"] == device_index), None) if device_index is not None else preferred_microphone()
        microphone = sr.Microphone(device_index=device["index"] if device else None, sample_rate=device["rate"] if device else None, chunk_size=1024)
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.65)
            try:
                import winsound
                winsound.Beep(880, 120)
            except Exception:
                pass
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        text = recognizer.recognize_google(audio, language=language).strip()
        if not text:
            return {"ok": False, "error": "pusta_transkrypcja", "message": "Nie rozpoznałem żadnych słów.", "device": device}
        return {"ok": True, "text": text, "language": language, "provider": "Google Speech keyless", "device": device}
    except Exception as exc:
        name = type(exc).__name__
        messages = {
            "WaitTimeoutError": "Nie usłyszałem mowy po sygnale. Kliknij mikrofon i zacznij mówić dopiero po krótkim sygnale.",
            "UnknownValueError": "Nie zrozumiałem nagrania. Wybrany mikrofon: {}. Spróbuj mówić bliżej i wyraźniej.".format((device or {}).get("name", "domyślny")),
            "RequestError": "Nagranie powstało, ale bezpłatna transkrypcja nie odpowiedziała. Sprawdź internet.",
            "OSError": "Nie mogę otworzyć wybranego mikrofonu. Sprawdź uprawnienia Windows i urządzenie: {}.".format((device or {}).get("name", "domyślne")),
        }
        return {"ok": False, "error": name, "message": messages.get(name, f"Mikrofon zgłosił błąd ({name})."), "device": device}
