"""Reports resumable state after a restart without executing queued work."""
from pathlib import Path
import json
def run(argument=None):
    path=Path(__file__).resolve().parent.parent / "memory" / "autonomy_state.json"
    if not path.exists(): return {"resumable":False,"reason":"no_state"}
    data=json.loads(path.read_text(encoding="utf-8")); return {"resumable":bool(data.get("queue")),"pending":sum(x.get("status")=="pending" for x in data.get("queue",[]))}
