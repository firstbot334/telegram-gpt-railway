# collector_telethon.py — multi-source collector (comma/space separated channels)
import os, asyncio
from typing import List
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from zoneinfo import ZoneInfo
from db import SessionLocal
from models import Article

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELETHON_SESSION"]

# Comma/space separated list of channels, e.g. "@nje2e,@bbbbbworld @repeatandrepeat"
SRC_CHANNELS = os.environ.get("SRC_CHANNELS") or os.environ.get("SRC_CHANNEL") or "@nje2e"
AUTO_JOIN = os.environ.get("AUTO_JOIN", "true").lower() in ("1","true","yes","y")
LIMIT = int(os.environ.get("SRC_LIMIT", "300"))  # per source
KST = ZoneInfo("Asia/Seoul")

def parse_sources(s: str) -> List[str]:
    parts = []
    for tok in s.replace(",", " ").split():
        t = tok.strip()
        if not t:
            continue
        parts.append(t)
    # de-duplicate while preserving order
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            out.append(p); seen.add(p)
    return out

async def collect_from(client: TelegramClient, source: str, session):
    # auto-join public channels if allowed
    if AUTO_JOIN and source.startswith("@"):
        try:
            await client(JoinChannelRequest(source))
        except Exception:
            pass
    count = 0
    async for msg in client.iter_messages(source, limit=LIMIT):
        text = None
        # Telethon uses .message for text in Channels; .text is for generic entities
        if getattr(msg, "message", None):
            text = (msg.message or "").strip()
        elif getattr(msg, "text", None):
            text = (msg.text or "").strip()
        if not text:
            continue
        try:
            session.add(Article(
                text=text,
                url=None,
                date=msg.date.astimezone(KST) if msg.date else None
            ))
            session.commit()
            count += 1
        except Exception:
            session.rollback()
    print(f"[collect] {source} -> stored {count} rows.")

async def main():
    sources = parse_sources(SRC_CHANNELS)
    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        dbs = SessionLocal()
        try:
            for src in sources:
                await collect_from(client, src, dbs)
            print("✅ collector done.")
        finally:
            dbs.close()

if __name__ == "__main__":
    asyncio.run(main())
