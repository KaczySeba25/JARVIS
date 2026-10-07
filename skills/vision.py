import pyautogui
import os

def run():
    """Robi zrzut ekranu i zapisuje go, aby Jarvis mógł go analizować."""
    try:
        screenshot_path = r"C:\Jarvis\logs\screen.png"
        pyautogui.screenshot(screenshot_path)
        return f"Zrobiłem zrzut ekranu i zapisałem go w: {screenshot_path}. Teraz mogę przeanalizować, co jest na ekranie."
    except Exception as e:
        return f"Błąd widzenia: {str(e)}"
