"""Bounded queue inspection; execution stays supervised and never runs indefinitely."""
from pathlib import Path
import json
def run(argument=None):
    path=Path(__file__).resolve().parent.parent / "memory" / "autonomy_state.json"
    if not path.exists(): return {"processed":0,"pending":0}
    data=json.loads(path.read_text(encoding="utf-8")); pending=[x for x in data.get("queue",[]) if x.get("status")=="pending"]
    return {"processed":0,"pending":len(pending),"mode":"bounded_supervised"}
