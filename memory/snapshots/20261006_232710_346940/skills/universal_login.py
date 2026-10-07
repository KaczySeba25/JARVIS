"""Open a service for a user-controlled sign-in handoff without handling passwords."""
from __future__ import annotations

import ipaddress
import socket
import webbrowser
from urllib.parse import urlparse


def _safe_https_url(value):
    parsed = urlparse(str(value or "").strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Podaj publiczny adres https:// bez danych logowania.")
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".local"):
        raise ValueError("Adres lokalny nie jest obsługiwany.")
    try:
        addresses = [ipaddress.ip_address(host)] if all(ch in "0123456789abcdef:." for ch in host) else [ipaddress.ip_address(row[4][0]) for row in socket.getaddrinfo(host, 443)]
    except (ValueError, OSError) as exc:
        raise ValueError("Nie udało się potwierdzić publicznego adresu usługi.") from exc
    if not addresses or not all(item.is_global for item in addresses):
        raise ValueError("Usługa musi mieć publiczny adres internetowy.")
    return parsed.geturl()


def run(service_data: str):
    """Input is a URL only. Never accept a username, password, or pasted token."""
    try:
        raw = str(service_data or "").strip()
        if "|" in raw:
            return {"opened": False, "connected": False, "reason": "credential_format_removed", "message": "Nie podawaj hasła Jarvisowi. Wklej sam adres usługi; zaloguj się w przeglądarce."}
        url = _safe_https_url(raw)
        opened = webbrowser.open(url, new=2, autoraise=True)
        return {"opened": bool(opened), "connected": False, "url": url,
                "next_step": "Zaloguj się samodzielnie w otwartej przeglądarce. Jarvis nie otrzymał hasła ani tokenu. Potem napisz, że logowanie jest zakończone; dostęp do danych wymaga właściwego, bezpiecznego połączenia z usługą."}
    except ValueError as exc:
        return {"opened": False, "connected": False, "reason": str(exc)}
    except Exception as exc:
        return {"opened": False, "connected": False, "reason": f"browser_unavailable:{type(exc).__name__}"}
