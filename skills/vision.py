import pyautogui
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run():
    """Robi zrzut ekranu i zapisuje go, aby Jarvis mógł go analizować."""
    try:
        screenshot_path = ROOT / "logs" / "screen.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        pyautogui.screenshot(screenshot_path)
        return f"Zrobiłem zrzut ekranu i zapisałem go w: {screenshot_path}. Teraz mogę przeanalizować, co jest na ekranie."
    except Exception as e:
        return f"Błąd widzenia: {str(e)}"
