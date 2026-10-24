"""Create safe, reviewable lessons from a project inventory."""
import json
try:
    from project_memory import get
    from governance import save_lesson
except ImportError:
    from agent.project_memory import get
    from agent.governance import save_lesson
def run(argument=None):
    data=argument if isinstance(argument,dict) else json.loads(str(argument or "{}")); project=get(data.get("path"))
    if not project:return {"ok":False,"error":"project_not_scanned"}
    save_lesson(str(data.get("path")),"project_inventory","structure_scanned",f"Project contains {project['file_count']} files; inspect before changing.",0.6,"project_memory")
    return {"ok":True,"learned":True,"facts":["file_inventory","project_root","file_count"],"content_not_stored":True}
