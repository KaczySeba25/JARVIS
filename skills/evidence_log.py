"""Record redacted task evidence in local governance."""
import json
try: import governance
except ImportError: from agent import governance
def run(argument=None):
    try:
        data=argument if isinstance(argument,dict) else json.loads(str(argument or "{}"))
        item=governance.Evidence(str(data.get("claim",""))[:500],str(data.get("source","runtime"))[:200],max(0,min(float(data.get("confidence",.5)),1)),bool(data.get("verified",False)))
        governance.save_evidence(item); return {"ok":True,"recorded":True,"verified":item.verified}
    except Exception as exc:return {"ok":False,"error":type(exc).__name__}
