"""Creates a safe request without asking for a secret in chat."""
def run(argument=None):
    service=str(argument or "requested_service").strip()
    return {"needs_secure_input": True, "service": service, "instruction": "Otwórz bezpieczny lokalny formularz Jarvisa i wpisz sekret bezpośrednio tam. Nie wklejaj hasła, tokenu ani klucza do czatu.", "secret_saved": False}
