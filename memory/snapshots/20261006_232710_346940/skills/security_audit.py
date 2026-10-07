"""Check public website security headers without accessing local networks."""
try:
    from research_engine import _get_public
except ImportError:
    from agent.research_engine import _get_public

def run(url: str):
    """Inspect common HTTPS/browser security headers on a public web page."""
    url = str(url or "").strip()
    if not url.startswith(("https://", "http://")):
        url = "https://" + url
    try:
        response = _get_public(url, timeout=(3, 5))
        headers = response.headers
        required = ("Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security")
        findings = {header: header in headers for header in required}
        return {"url": response.url, "status_code": response.status_code, "headers": findings, "limitations": ["header_presence_only", "not_a_full_security_audit"]}
    except Exception as exc:
        return {"error": type(exc).__name__, "audited": False}
