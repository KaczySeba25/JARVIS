"""Scan and recall durable project structure without storing file contents."""
import json
try: from project_memory import scan,get
except ImportError: from agent.project_memory import scan,get
def run(argument=None):
    try:
        data=argument if isinstance(argument,dict) else json.loads(str(argument or "{}")); return {"ok":True,"project":scan(data.get("path"))} if data.get("action","scan")=="scan" else {"ok":True,"project":get(data.get("path"))}
    except Exception as exc:return {"ok":False,"error":type(exc).__name__}
