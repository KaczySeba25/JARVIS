"""Secure credential vault using Windows DPAPI; values are never written as plaintext."""
try:
    from secret_store import get, save, status
except ImportError:
    from agent.secret_store import get, save, status
def run(action_data=None):
    """Use save|service|url|user|secret, get|service or status."""
    try:
        parts=(action_data or "").split("|",4); action=parts[0].lower()
        if action=="save":
            service=parts[1].lower(); url,user,secret=parts[2],parts[3],parts[4]; save(service,secret,user,{"url":url}); return {"saved":True,"service":service}
        if action=="get":
            item=get(parts[1]); return {"url":item.get("metadata",{}).get("url",""),"username":item["username"],"secret":item["secret"]}
        if action=="status": return status()
        return {"error":"use save|get|status"}
    except Exception as exc: return {"error":type(exc).__name__}
