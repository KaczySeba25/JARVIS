"""Store reusable symptom/cause/fix records."""
try:
    from governance import save_error
except ImportError:
    from agent.governance import save_error

def run(data: str):
    parts = (data or "").split("|", 2)
    if len(parts) != 3: return "Użycie: symptom|cause|fix"
    save_error(*parts)
    return "Błąd i rozwiązanie zapisane w pamięci Jarvisa."
