"""Windows DPAPI-backed local secret store; plaintext is never written to disk."""
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
def save(service,secret,username="",metadata=None):
    if not service or not secret: raise ValueError("service and secret are required")
    data=_read(); data[service.strip().lower()]={"username":username,"secret":secret,"metadata":metadata or {}}; STORE.parent.mkdir(parents=True,exist_ok=True); STORE.write_bytes(base64.b64encode(_crypt(json.dumps(data,ensure_ascii=False).encode(),True))); return {"saved":True,"service":service.strip().lower()}
def get(service):
    item=_read().get(service.strip().lower())
    if not item: raise KeyError("secret_not_found")
    return item
def status(): return {"configured":STORE.exists(),"services":sorted(_read()) if STORE.exists() else []}
