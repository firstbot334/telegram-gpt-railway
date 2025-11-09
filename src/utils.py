import os, re, sys, hashlib, html
from typing import Iterable, List, Tuple
from .config import settings

def sha256_of(*parts: Iterable[str]) -> str:
    h = hashlib.sha256()
    for p in parts:
        if p:
            h.update(p.encode("utf-8", errors="ignore"))
    return h.hexdigest()

def html_safe(s: str) -> str:
    return html.escape(s or "", quote=True)

def split_sources(raw: str) -> List[str]:
    items = [s.strip() for s in re.split(r"[\s,]+", raw) if s.strip()]
    out = []
    for s in items:
        if s.startswith("@"):
            out.append(s)
        elif s.startswith("http"):
            out.append(s)
        elif s.startswith("t.me/"):
            out.append("https://" + s)
        elif re.fullmatch(r"[A-Za-z0-9_]{5,}", s):
            out.append("@"+s)
        else:
            out.append(s)  # keep as-is (might be -100... -> will be rejected later)
    return out

def validate_sources(raw: str) -> Tuple[bool, List[str], List[str]]:
    ok, bad = [], []
    for s in split_sources(raw):
        if s.startswith("@") or s.startswith("http"):
            ok.append(s)
        else:
            bad.append(s)
    return (len(bad)==0, ok, bad)

if __name__ == "__main__":
    if "--validate-sources" in sys.argv:
        valid, ok, bad = validate_sources(settings.SRC_CHANNELS)
        print("[utils] SRC_CHANNELS(raw) =", settings.SRC_CHANNELS)
        print("[utils] normalized(ok)    =", " ".join(ok) if ok else "(none)")
        if bad:
            print("[utils] invalid items    =", " ".join(bad))
            print("ERROR: replace numeric IDs like -100... with @username or https://t.me/... (or join the channel first).")
            sys.exit(1)
        sys.exit(0)
