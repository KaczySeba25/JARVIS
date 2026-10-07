"""Safe maintenance checks that do not mutate credentials or trading state."""
from pathlib import Path
import compileall
import shutil
from readiness import audit

def run(_: str = "status"):
    result = audit()
    result["disk_free_gb"] = round(shutil.disk_usage(Path(__file__).resolve().parent.parent).free / (1024**3), 2)
    return str(result)
