"""Read-only regression checks for approved local projects."""
from __future__ import annotations
import subprocess, sys, time, os
from pathlib import Path
def run(root: str, timeout: int = 60):
    path=Path(root).expanduser().resolve()
    if not path.is_dir(): return {"ok":False,"error":"project_not_found"}
    started=time.time(); result={"target":str(path),"checks":[]}
    try:
        ignored={".git","venv",".venv","node_modules","__pycache__","models","checkpoints","artifacts","WARTOSCIOWE_Z_INNYCH_PROJEKTOW"}
        files=[]
        for current, dirs, names in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored]
            files.extend(str(Path(current)/name) for name in names if name.endswith(".py"))
        compile_result=subprocess.run([sys.executable,"-m","py_compile",*files],capture_output=True,text=True,timeout=timeout,cwd=str(path))
        result["checks"].append({"name":"python_compile","passed":compile_result.returncode==0,"output":(compile_result.stderr or compile_result.stdout)[-2000:]})
    except subprocess.TimeoutExpired: result["checks"].append({"name":"python_compile","passed":False,"output":"timeout"})
    test_files=list(path.rglob("test_*.py"))+list(path.rglob("*_test.py"))
    result["test_files"]=len({p.resolve() for p in test_files if ".venv" not in p.parts and "venv" not in p.parts})
    result["passed"]=all(item["passed"] for item in result["checks"]); result["duration_s"]=round(time.time()-started,2); return result
