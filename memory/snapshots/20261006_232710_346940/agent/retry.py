"""Bounded retry helper; never retries destructive actions indefinitely."""
import time

def run(operation, attempts=3, delay=0.2):
    last = None
    for index in range(attempts):
        try: return operation()
        except Exception as exc:
            last = exc
            if index + 1 < attempts: time.sleep(delay * (index + 1))
    raise RuntimeError(f"Operacja nie powiodła się po {attempts} próbach: {last}")
