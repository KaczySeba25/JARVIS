"""Import a Google OAuth client JSON file directly into the DPAPI vault.

The file contents and secret values are never printed.  The OAuth client id is
stored as the vault username and the client secret as the protected secret.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from secret_store import save


def import_client(path: str, service: str = "youtube.oauth") -> dict:
    source = Path(path).expanduser().resolve()
    if source.suffix.lower() != ".json":
        raise ValueError("oauth_json_required")
    data = json.loads(source.read_text(encoding="utf-8"))
    config = data.get("installed") or data.get("web")
    if not isinstance(config, dict):
        raise ValueError("oauth_client_config_missing")
    client_id = str(config.get("client_id") or "").strip()
    client_secret = str(config.get("client_secret") or "").strip()
    if not client_id or not client_secret:
        raise ValueError("oauth_client_fields_missing")
    result = save(
        service,
        client_secret,
        username=client_id,
        metadata={
            "provider": "google",
            "kind": "oauth_client",
            "service": "youtube",
            "source_name": source.name,
        },
    )
    return {"saved": True, "service": result["service"], "source_name": source.name}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python agent/import_oauth_json.py <oauth.json>")
    try:
        print(json.dumps(import_client(sys.argv[1]), ensure_ascii=False))
    except Exception as exc:
        raise SystemExit(f"oauth_import_failed:{type(exc).__name__}")
