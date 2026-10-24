"""Describe and enforce bounded operator mode for a task."""
import json
try: from safety_policy import assess
except ImportError: from agent.safety_policy import assess
def run(argument=None):
    data=argument if isinstance(argument,dict) else json.loads(str(argument or "{}")); action=data.get("action","status")
    if action=="status": return {"mode":"supervised_operator","requires_plan":True,"allowed_external":False,"human_steps":["CAPTCHA","SMS","2FA","payment","identity"]}
    return {"mode":"supervised_operator","decision":assess(data.get("operation"),data.get("path"),data.get("external",False),data.get("reversible",True))}
