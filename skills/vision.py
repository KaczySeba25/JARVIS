"""Real screen vision: screenshot capture, dimensions, hashes and optional OCR."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

RISK_LEVEL = "low"
ROOT = Path(__file__).resolve().parent.parent

def run(argument=None):
    data = argument if isinstance(argument, dict) else {}
    try:
        import pyautogui
        from PIL import Image
        screenshot_dir = ROOT / "logs" / "screens"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        path = screenshot_dir / f"screen_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.time()*1000)%1000:03d}.png"
        image = pyautogui.screenshot()
        image.save(path)
        result = {"ok": True, "path": str(path), "width": image.width, "height": image.height,
                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "captured_at": time.time()}
        if bool(data.get("ocr", True)):
            try:
                import pytesseract
                result["ocr_text"] = pytesseract.image_to_string(image, lang=str(data.get("language", "pol+eng")))[:12000]
                result["ocr_available"] = True
            except Exception as exc:
                result["ocr_available"] = False
                result["ocr_note"] = f"OCR niedostępny: {type(exc).__name__}. Obraz zapisany do analizy wizualnej."
        return result
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:500]}
