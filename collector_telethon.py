import os
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (ChannelPrivateError, InviteHashExpiredError, FloodWaitError)
from db import SessionLocal
from models import Article
from config import NEWS_SOURCES, BACKFILL_DAYS

# 고정된 내 계정 API (요청하신 값)
API_ID = 39591049
API_HASH = "63051274cc060175aee8f62d636cfa6f"

KST = timezone(timedelta(hours=9))

async def collect():
    if not NEWS_SOURCES:
        print("⚠️  NEWS_SOURCES is empty — nothing to collect.")
        return

    sess = os.getenv("TELETHON_SESSION", "").strip()
    if not sess:
        raise RuntimeError("TELETHON_SESSION env var is missing — create one with make_session.py and set it in Railway.")

    client = TelegramClient(StringSession(sess), API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("Provided TELETHON_SESSION is not authorized. Recreate it with make_session.py.")

    cutoff = datetime.now(KST) - timedelta(days=BACKFILL_DAYS)
    session = SessionLocal()

    try:
        sources = NEWS_SOURCES if isinstance(NEWS_SOURCES, (list, tuple)) else [NEWS_SOURCES]
        for src in sources:
            try:
                entity = await client.get_input_entity(src)
            except Exception as e:
                print(f"[warn] get_input_entity failed for {src}: {e}")
                continue

            async for msg in client.iter_messages(entity, reverse=False):
                if msg.date.replace(tzinfo=timezone.utc) < cutoff.astimezone(timezone.utc):
                    continue
                text = (msg.message or msg.raw_text or "").strip()
                if not text:
                    continue
                exists = session.query(Article).filter(Article.text == text).first()
                if exists:
                    continue
                session.add(Article(text=text, url=None, created_at=msg.date.astimezone(KST)))
                session.commit()
                print(f"[ok] saved from {src}: {text[:60]}...")

    except FloodWaitError as e:
        print(f"⏱️ FloodWaitError: sleeping for {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except (ChannelPrivateError, InviteHashExpiredError) as e:
        print(f"⚠️ Channel access error: {e}")
    finally:
        session.close()
        await client.disconnect()
        print("✅ Done. Client disconnected.")

if __name__ == "__main__":
    asyncio.run(collect())
