import subprocess
import sys
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent

def run(skill_name: str):
    """
    Próbuje uruchomić dany skill i przechwycić błędy.
    """
    try:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", skill_name or ""):
            return "BŁĄD: Nieprawidłowa nazwa skilla."
        file_path = (SKILLS_DIR / f"{skill_name}.py").resolve()
        if file_path.parent != SKILLS_DIR.resolve():
            return "BŁĄD: Ścieżka poza katalogiem skills."
        if not file_path.exists():
            return f"BŁĄD: Plik {skill_name}.py nie istnieje."
            
        # Uruchamia skill w oddzielnym procesie, aby nie zawiesić głównego agenta
        # Dodajemy mały skrypt, który importuje funkcję run i ją wywołuje
        probe = "import importlib.util,sys; p=sys.argv[1]; s=importlib.util.spec_from_file_location('tested_skill',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.run() if callable(getattr(m,'run',None)) else 'Brak funkcji run()')"
        
        result = subprocess.run([sys.executable, "-c", probe, str(file_path)], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return f"TEST SUKCES: {result.stdout}"
        else:
            return f"TEST NIEUDANY. BŁĄD KONSOLI:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "BŁĄD: Skill przekroczył limit czasu (Timeout)."
    except Exception as e:
        return f"BŁĄD TESTOWANIA: {str(e)}"
