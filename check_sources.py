# check_sources.py — verify access to sources and show latest message info
import os, asyncio
from datetime import timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELETHON_SESSION"]
SRC_CHANNELS = os.environ.get("SRC_CHANNELS") or os.environ.get("SRC_CHANNEL") or "@nje2e"
AUTO_JOIN = os.environ.get("AUTO_JOIN", "true").lower() in ("1","true","yes","y")

def parse_sources(s: str):
    parts = []
    for tok in s.replace(",", " ").split():
        t = tok.strip()
        if t:
            parts.append(t)
    seen = set(); out = []
    for p in parts:
        if p not in seen:
            out.append(p); seen.add(p)
    return out

async def probe(client, name: str):
    ok = True; info = {}
    try:
        if AUTO_JOIN and name.startswith("@"):
            try:
                await client(JoinChannelRequest(name))
            except Exception:
                pass
        msg = await client.get_messages(name, limit=1)
        if msg and len(msg)>0 and msg[0]:
            m = msg[0]
            info = {
                "id": getattr(m, "id", None),
                "date": getattr(m, "date", None),
                "preview": (getattr(m, "message", None) or getattr(m, "text", "") or "")[:120].replace("\n"," ")
            }
        else:
            ok=False
    except Exception as e:
        ok=False; info={"error": str(e)}
    return ok, info

async def main():
    sources = parse_sources(SRC_CHANNELS)
    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        for s in sources:
            ok, info = await probe(client, s)
            if ok:
                print(f"[OK] {s}  last_id={info.get('id')}  date={info.get('date')}  text='{info.get('preview')}'")
            else:
                print(f"[FAIL] {s}  reason={info.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
