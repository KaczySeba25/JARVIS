"""Creates a safe request when a task needs a missing API key or login secret."""
def run(argument=None):
    service=str(argument or "requested_service").strip()
    return {"needs_user_input":True,"service":service,"instruction":"Podaj sekret tylko w bieżącej rozmowie; Jarvis zapisze go w DPAPI i nie umieści w logu."}
