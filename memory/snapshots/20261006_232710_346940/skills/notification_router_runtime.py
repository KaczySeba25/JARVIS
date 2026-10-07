"""Creates local notification events without sending data externally."""
from pathlib import Path
import json,time
def run(argument=None):
    path=Path(__file__).resolve().parent.parent / "memory" / "notifications.jsonl"; path.parent.mkdir(exist_ok=True)
    event={"ts":time.time(),"message":str(argument or "Jarvis event"),"channel":"local"}
    with path.open("a",encoding="utf-8") as handle: handle.write(json.dumps(event,ensure_ascii=False)+"\n")
    return {"queued":True,"channel":"local"}
