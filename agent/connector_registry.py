"""Local registry for explicit service connectors and their scopes."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "memory" / "connectors.json"
def _read():
    try: return json.loads(FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError): return {}
def save(service, kind, scopes=None, endpoint=""):
    service = str(service or "").strip().lower()
    if not service or len(service) > 120: raise ValueError("invalid_service")
    data = _read(); data[service] = {"kind": str(kind)[:40], "scopes": [str(x)[:120] for x in (scopes or [])[:30]], "endpoint": str(endpoint)[:500], "enabled": False}
    FILE.parent.mkdir(parents=True, exist_ok=True); FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"service": service, "enabled": False, "requires_test": True}
def list_all(): return {"services": sorted(_read())}
