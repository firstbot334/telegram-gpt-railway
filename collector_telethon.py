import os
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import ChannelPrivateError, InviteHashExpiredError, FloodWaitError
from db import SessionLocal
from models import Article
from config import NEWS_SOURCES, BACKFILL_DAYS

KST = timezone(timedelta(hours=9))

def _parse_sources(sources):
    if isinstance(sources, (list, tuple)):
        return [s.strip() for s in sources if s and str(s).strip()]
    if isinstance(sources, str):
        return [s.strip() for s in sources.split(",") if s.strip()]
    return []

async def collect():
    # Read required envs
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    sess = os.getenv("TELETHON_SESSION", "").strip()

    if not (api_id and api_hash and sess):
        missing = [k for k in ["TELEGRAM_API_ID","TELEGRAM_API_HASH","TELETHON_SESSION"] if not os.getenv(k)]
        raise RuntimeError(f"Missing required env(s): {', '.join(missing)}")

    # Create client with the provided user session
    client = TelegramClient(StringSession(sess), int(api_id), api_hash)
    await client.connect()

    # Guard: must be a USER session (not a bot)
    me = await client.get_me()
    if getattr(me, "bot", False):
        raise RuntimeError("Current TELETHON_SESSION is a BOT session. Create a USER StringSession and update env.")

    if not await client.is_user_authorized():
        raise RuntimeError("TELETHON_SESSION not authorized. Recreate it locally and set env again.")

    sources = _parse_sources(NEWS_SOURCES)
    if not sources:
        print("NEWS_SOURCES is empty — nothing to collect.")
        await client.disconnect()
        return

    cutoff = datetime.now(KST) - timedelta(days=int(BACKFILL_DAYS or 1))
    session = SessionLocal()

    try:
        for src in sources:
            try:
                entity = await client.get_input_entity(src)
                print(f"[info] Reading from: {src}")
            except Exception as e:
                print(f"[warn] get_input_entity failed for {src}: {e}")
                continue

            async for msg in client.iter_messages(entity, reverse=False):
                # Time window filter
                if msg.date.replace(tzinfo=timezone.utc) < cutoff.astimezone(timezone.utc):
                    continue
                text = (getattr(msg, "message", None) or getattr(msg, "raw_text", None) or "").strip()
                if not text:
                    continue
                # De-duplicate by exact text
                if session.query(Article).filter(Article.text == text).first():
                    continue

                session.add(Article(text=text, url=None, created_at=msg.date.astimezone(KST)))
                session.commit()
                print(f"[ok] saved: [{src}] {text[:100]}...")

    except FloodWaitError as e:
        print(f"[info] FloodWait: sleeping for {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except (ChannelPrivateError, InviteHashExpiredError) as e:
        print(f"[warn] Channel access error for some sources: {e}")
    finally:
        session.close()
        await client.disconnect()
        print("✅ Done. Client disconnected.")

if __name__ == "__main__":
    asyncio.run(collect())
