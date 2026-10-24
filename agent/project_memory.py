"""Project inventory and durable local project memory."""
from pathlib import Path
import os
import json, time
FILE=Path(__file__).resolve().parent.parent/"memory"/"projects.json"
def _read():
    try:return json.loads(FILE.read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError):return {}
def scan(path):
    root=Path(path).expanduser().resolve()
    if not root.is_dir():raise ValueError("project_not_found")
    skipped={".git","venv",".venv","node_modules","__pycache__","models","checkpoints","artifacts"}
    large={".keras",".h5",".pt",".pth",".onnx",".bin",".safetensors",".zip",".tar",".gz"}
    files=[]
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skipped]
        for name in names:
            x = Path(current) / name
            if len(files)>=2000: break
            if x.suffix.lower() in large: continue
            try:
                if x.stat().st_size > 5_000_000: continue
            except OSError: continue
            files.append(str(x.relative_to(root)))
        if len(files)>=2000: break
    data=_read(); data[str(root)]={"root":str(root),"files":files,"file_count":len(files),"updated":time.time()}; FILE.parent.mkdir(parents=True,exist_ok=True); FILE.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8"); return data[str(root)]
def get(path):return _read().get(str(Path(path).expanduser().resolve()))
