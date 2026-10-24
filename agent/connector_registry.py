"""Local registry for explicit service connectors and their scopes."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "memory" / "connectors.json"

# Catalogue is intentionally metadata-only. It does not contain credentials and
# registering an item never enables network access by itself.
CATALOG = [
    {"service": "youtube", "kind": "oauth", "scopes": ["youtube.readonly", "youtube.upload", "youtube.force-ssl"], "endpoint": "https://developers.google.com/youtube/v3"},
    {"service": "google", "kind": "oauth", "scopes": ["openid", "email", "profile"], "endpoint": "https://console.cloud.google.com/apis/credentials"},
    {"service": "github", "kind": "oauth", "scopes": ["repo", "read:org"], "endpoint": "https://docs.github.com/en/apps/oauth-apps"},
    {"service": "outlook", "kind": "oauth", "scopes": ["Mail.Read", "Mail.Send"], "endpoint": "https://learn.microsoft.com/graph/auth-register-app-v2"},
    {"service": "slack", "kind": "oauth", "scopes": ["chat:write", "channels:read"], "endpoint": "https://api.slack.com/authentication/oauth-v2"},
    {"service": "shopify", "kind": "oauth", "scopes": ["read_products", "write_products"], "endpoint": "https://shopify.dev/docs/apps/build/authentication-authorization"},
    {"service": "binance-testnet", "kind": "api", "scopes": ["market-data", "testnet-only"], "endpoint": "https://testnet.binance.vision/"},
]
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

def catalog(query=""):
    q = str(query or "").strip().lower()
    items = [item for item in CATALOG if not q or q in item["service"] or q in item["kind"] or any(q in scope.lower() for scope in item["scopes"])]
    registered = _read()
    return [{**item, "registered": item["service"] in registered, "enabled": bool(registered.get(item["service"], {}).get("enabled", False))} for item in items]

def add_custom(service, kind="api", scopes=None, endpoint=""):
    return save(service, kind, scopes, endpoint)
