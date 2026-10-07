"""Single supervised runtime cycle joining Jarvis quality layers."""
from __future__ import annotations
import json, time
from pathlib import Path
try:
    from .autonomy_layers import execute as autonomy
    from .meta_capabilities import execute as meta
except ImportError:
    from autonomy_layers import execute as autonomy
    from meta_capabilities import execute as meta

ROOT=Path(__file__).resolve().parent.parent; REPORT=ROOT/"memory"/"runtime_report.json"
def cycle(goal: str) -> dict:
    goal=str(goal or "").strip()
    result={"goal":goal,"started":time.time(),"stages":[]}
    result["stages"].append({"name":"checkpoint","result":autonomy("checkpoint_manager","runtime_cycle")})
    result["stages"].append({"name":"plan","result":meta("advanced_planner",goal)})
    result["stages"].append({"name":"sandbox","result":meta("sandbox_runner",goal)})
    result["stages"].append({"name":"regression","result":meta("regression_runner",goal)})
    result["stages"].append({"name":"verification","result":meta("self_verifier",goal)})
    result["status"]="review_required"
    result["finished"]=time.time()
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

def dashboard() -> str:
    data=REPORT.read_text(encoding="utf-8") if REPORT.exists() else json.dumps({"status":"no_cycle"},ensure_ascii=False)
    html="""<!doctype html><meta charset='utf-8'><title>Jarvis diagnostics</title><style>body{font:16px system-ui;max-width:900px;margin:40px auto;background:#101318;color:#eee}pre{padding:20px;background:#1b212b;border-radius:8px;white-space:pre-wrap}</style><h1>Jarvis diagnostics</h1><pre>"""+data+"</pre>"
    path=ROOT/"memory"/"diagnostics.html"; path.write_text(html,encoding="utf-8"); return str(path)
