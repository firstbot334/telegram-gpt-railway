import os
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import ChannelPrivateError, InviteHashExpiredError, FloodWaitError
from db import SessionLocal, create_tables
from models import Article
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELETHON_SESSION, NEWS_SOURCES, BACKFILL_DAYS

KST = timezone(timedelta(hours=9))

def _require_env():
    need = ["TELEGRAM_API_ID","TELEGRAM_API_HASH","TELETHON_SESSION","DATABASE_URL"]
    missing = [k for k in need if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env(s): {', '.join(missing)}")

async def collect():
    _require_env()
    api_id = int(TELEGRAM_API_ID)
    api_hash = TELEGRAM_API_HASH
    sess = (TELETHON_SESSION or "").strip()

    client = TelegramClient(StringSession(sess), api_id, api_hash)
    await client.connect()

    me = await client.get_me()
    if getattr(me, "bot", False):
        raise RuntimeError("TELETHON_SESSION is a BOT session. Create user session and update env.")
    if not await client.is_user_authorized():
        raise RuntimeError("TELETHON_SESSION not authorized. Recreate it and update env.")

    if not NEWS_SOURCES:
        print("NEWS_SOURCES is empty — nothing to collect.")
        await client.disconnect()
        return

    create_tables()
    session = SessionLocal()
    cutoff = datetime.now(KST) - timedelta(days=int(BACKFILL_DAYS or 1))

    try:
        for src in NEWS_SOURCES:
            try:
                entity = await client.get_input_entity(src)
                print(f"[info] reading from: {src}")
            except Exception as e:
                print(f"[warn] get_input_entity failed for {src}: {e}")
                continue

            async for msg in client.iter_messages(entity, reverse=False):
                if msg.date.replace(tzinfo=timezone.utc) < cutoff.astimezone(timezone.utc):
                    continue
                text = (getattr(msg, "message", None) or getattr(msg, "raw_text", None) or "").strip()
                if not text:
                    continue
                if session.query(Article).filter(Article.text == text).first():
                    continue
                session.add(Article(text=text, url=None, created_at=msg.date.astimezone(KST)))
                session.commit()
                print(f"[ok] saved: [{src}] {text[:100]}...")

    except FloodWaitError as e:
        print(f"[info] FloodWait: sleeping {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except (ChannelPrivateError, InviteHashExpiredError) as e:
        print(f"[warn] channel access error: {e}")
    finally:
        session.close()
        await client.disconnect()
        print("✅ collector done.")

if __name__ == "__main__":
    asyncio.run(collect())
