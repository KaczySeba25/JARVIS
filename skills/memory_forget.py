"""Delete one local Jarvis memory by its numeric id."""
try:
    from memory_store import forget
except ImportError:
    from agent.memory_store import forget

def run(memory_id):
    """Remove the memory with the supplied id; no cloud data is touched."""
    try:
        removed = forget(int(memory_id))
        return {"deleted": removed, "id": int(memory_id)}
    except (TypeError, ValueError):
        return {"deleted": False, "reason": "Podaj numer wspomnienia."}
