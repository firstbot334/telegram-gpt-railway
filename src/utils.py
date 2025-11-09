import hashlib
def sha256_of(*parts: str) -> str:
    h=hashlib.sha256()
    for p in parts:
        if p:
            h.update(p.encode('utf-8','ignore')); h.update(b'\0')
    return h.hexdigest()
