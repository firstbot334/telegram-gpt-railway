
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import (ChannelPrivateError, InviteHashExpiredError, FloodWaitError)
from db import SessionLocal
from models import Article
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELETHON_SESSION, NEWS_SOURCES, BACKFILL_DAYS

KST = timezone(timedelta(hours=9))

async def collect():
    if not NEWS_SOURCES:
        print("NEWS_SOURCES is empty — nothing to collect.")
        return

    client = TelegramClient(StringSession(TELETHON_SESSION), int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    await client.start()

    for src in NEWS_SOURCES:
        try:
            await client(JoinChannelRequest(src))
        except Exception as e:
            print(f"Join failed for {src}: {e}")

    cutoff = datetime.now(KST) - timedelta(days=BACKFILL_DAYS)
    session = SessionLocal()

    try:
        async for msg in client.iter_messages(NEWS_SOURCES, offset_date=None, reverse=False):
            if msg.date.replace(tzinfo=timezone.utc) < cutoff.astimezone(timezone.utc):
                continue
            text = (msg.message or msg.raw_text or "").strip()
            url = None
            # Avoid storing empty messages
            if not text:
                continue
            exists = session.query(Article).filter(Article.text == text).first()
            if exists:
                continue
            session.add(Article(text=text, url=url, created_at=msg.date.astimezone(KST)))
            session.commit()
    finally:
        session.close()
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(collect())
