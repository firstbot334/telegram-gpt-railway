# collector_telethon.py — save `source` and `sha256` (dedupe)
import os, asyncio, hashlib
from typing import List
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError
from db import SessionLocal
from models import Article

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELETHON_SESSION"]

SRC_CHANNELS = os.environ.get("SRC_CHANNELS") or os.environ.get("SRC_CHANNEL") or "@nje2e"
AUTO_JOIN = os.environ.get("AUTO_JOIN", "true").lower() in ("1","true","yes","y")
LIMIT = int(os.environ.get("SRC_LIMIT", "300"))
KST = ZoneInfo("Asia/Seoul")

def parse_sources(s: str) -> List[str]:
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

async def collect_from(client: TelegramClient, source: str, session):
    if AUTO_JOIN and source.startswith("@"):
        try:
            await client(JoinChannelRequest(source))
        except Exception:
            pass
    added = 0; skipped = 0
    async for msg in client.iter_messages(source, limit=LIMIT):
        txt = getattr(msg, "message", None) or getattr(msg, "text", None) or ""
        txt = (txt or "").strip()
        if not txt:
            continue
        h = hashlib.sha256(txt.encode("utf-8")).hexdigest()
        try:
            session.add(Article(
                text=txt,
                url=None,
                date=msg.date.astimezone(KST) if msg.date else None,
                source=source,
                sha256=h
            ))
            session.commit()
            added += 1
        except IntegrityError:
            session.rollback()
            skipped += 1
        except Exception:
            session.rollback()
    print(f"[collect] {source} -> stored {added} rows, skipped {skipped} dups.")

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
