"""Read-only diagnostic snapshot of the autonomous execution layer."""
from pathlib import Path
import json
def run(argument=None):
    path=Path(__file__).resolve().parent.parent / "memory" / "autonomy_state.json"
    if not path.exists(): return {"queue":0,"checkpoints":0,"stop_requested":False}
    data=json.loads(path.read_text(encoding="utf-8")); return {"queue":len(data.get("queue",[])),"checkpoints":len(data.get("checkpoints",[])),"stop_requested":data.get("stop_requested",False)}
