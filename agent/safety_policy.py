"""Central risk decisions for operator actions."""
def assess(action,path="",external=False,reversible=True):
    action=str(action).lower(); high=external or action in {"delete","publish","submit","send","create_account","write"}; return {"risk":"high" if high else "medium" if not reversible else "low","requires_plan":high or not reversible,"requires_human":action in {"captcha","2fa","sms","payment","identity"},"path":str(path)[:500]}
