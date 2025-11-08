# collector_telethon.py (fixed: Article(date=...), safe commit/rollback)
import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from zoneinfo import ZoneInfo
from db import SessionLocal
from models import Article

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELETHON_SESSION"]

SRC_CHANNEL = os.environ.get("SRC_CHANNEL", "@nje2e")  # default as per logs
KST = ZoneInfo("Asia/Seoul")

async def main():
    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        session = SessionLocal()
        try:
            async for msg in client.iter_messages(SRC_CHANNEL, limit=200):
                text = None
                if msg.message:
                    text = msg.message.strip()
                elif msg.text:
                    text = msg.text.strip()
                if not text:
                    continue

                try:
                    session.add(Article(
                        text=text,
                        url=None,
                        date=msg.date.astimezone(KST) if msg.date else None  # FIX: 'date=' instead of 'created_at='
                    ))
                    session.commit()
                except Exception:
                    session.rollback()
            print("✅ collector done.")
        finally:
            session.close()

if __name__ == "__main__":
    asyncio.run(main())
