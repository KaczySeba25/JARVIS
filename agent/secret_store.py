"""Windows DPAPI-backed local secret store.

Plaintext is only returned to trusted in-process connectors. Skills expose
metadata and operation results, never the secret value to the language model.
"""
from __future__ import annotations
import base64, ctypes, json
from ctypes import wintypes
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; STORE=ROOT/"vault"/"secrets.dpapi"
class _Blob(ctypes.Structure): _fields_=[("cbData",wintypes.DWORD),("pbData",ctypes.POINTER(ctypes.c_byte))]
def _crypt(data, protect):
    source=ctypes.create_string_buffer(data); blob=_Blob(len(data),ctypes.cast(source,ctypes.POINTER(ctypes.c_byte))); out=_Blob(); fn=ctypes.windll.crypt32.CryptProtectData if protect else ctypes.windll.crypt32.CryptUnprotectData
    if not fn(ctypes.byref(blob),None,None,None,None,0,ctypes.byref(out)): raise ctypes.WinError()
    try: return ctypes.string_at(out.pbData,out.cbData)
    finally: ctypes.windll.kernel32.LocalFree(out.pbData)
def _read(): return json.loads(_crypt(base64.b64decode(STORE.read_bytes()),False).decode()) if STORE.exists() else {}
def _service(service):
    value = str(service or "").strip().lower()
    if not value or len(value) > 120 or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for ch in value):
        raise ValueError("invalid_service")
    return value
def save(service,secret,username="",metadata=None):
    service = _service(service)
    if not service or not secret: raise ValueError("service and secret are required")
    data=_read(); data[service.strip().lower()]={"username":username,"secret":secret,"metadata":metadata or {}}; STORE.parent.mkdir(parents=True,exist_ok=True); STORE.write_bytes(base64.b64encode(_crypt(json.dumps(data,ensure_ascii=False).encode(),True))); return {"saved":True,"service":service.strip().lower()}
def get(service):
    item=_read().get(_service(service))
    if not item: raise KeyError("secret_not_found")
    return item
def metadata(service):
    item = get(service)
    return {"service": _service(service), "username": item.get("username", ""), "metadata": item.get("metadata", {})}
def delete(service):
    service = _service(service); data = _read()
    existed = data.pop(service, None) is not None
    if existed:
        STORE.write_bytes(base64.b64encode(_crypt(json.dumps(data, ensure_ascii=False).encode(), True)))
    return {"deleted": existed, "service": service}
def status(): return {"configured":STORE.exists(),"services":sorted(_read()) if STORE.exists() else []}
