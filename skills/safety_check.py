"""Explain the safety gate before an operator action."""
import json
try: from safety_policy import assess
except ImportError: from agent.safety_policy import assess
def run(argument=None):
    data=argument if isinstance(argument,dict) else json.loads(str(argument or "{}")); return {"ok":True,**assess(data.get("action"),data.get("path"),data.get("external",False),data.get("reversible",True))}
