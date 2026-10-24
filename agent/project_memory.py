"""Project inventory and durable local project memory."""
from pathlib import Path
import json, time
FILE=Path(__file__).resolve().parent.parent/"memory"/"projects.json"
def _read():
    try:return json.loads(FILE.read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError):return {}
def scan(path):
    root=Path(path).expanduser().resolve()
    if not root.is_dir():raise ValueError("project_not_found")
    files=[str(x.relative_to(root)) for x in root.rglob("*") if x.is_file() and not any(p in {".git","venv",".venv","node_modules","__pycache__"} for p in x.parts)][:2000]
    data=_read(); data[str(root)]={"root":str(root),"files":files,"file_count":len(files),"updated":time.time()}; FILE.parent.mkdir(parents=True,exist_ok=True); FILE.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8"); return data[str(root)]
def get(path):return _read().get(str(Path(path).expanduser().resolve()))
