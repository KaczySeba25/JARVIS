"""Open the local secure credential intake form."""
import subprocess
import sys
from pathlib import Path
def run(argument=None):
    service=str(argument or "requested_service").strip()
    script = Path(__file__).resolve().parent.parent / "agent" / "secure_input.py"
    try:
        subprocess.Popen([sys.executable, str(script), service], close_fds=True)
        return {"needs_secure_input": True, "service": service, "form_opened": True, "instruction": "Wpisz dane w lokalnym oknie Jarvisa. Nie wklejaj hasła, tokenu ani klucza do czatu.", "secret_saved": False}
    except Exception as exc:
        return {"needs_secure_input": True, "service": service, "form_opened": False, "error": type(exc).__name__, "instruction": "Nie udało się otworzyć lokalnego formularza. Nie wysyłaj sekretu w czacie."}
