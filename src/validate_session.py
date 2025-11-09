import logging, asyncio, os
from telethon import TelegramClient
from telethon.sessions import StringSession
from .config import settings
from .logging_setup import setup_logging

setup_logging()
log = logging.getLogger("validate_session")

async def main():
    if not (settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH and settings.TELETHON_SESSION):
        log.warning("Telethon credentials not fully set; skipping.")
        return
    try:
        async with TelegramClient(StringSession(settings.TELETHON_SESSION), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
            me = await client.get_me()
            log.info("Telethon session OK: %s", me.username or me.id)
    except Exception as e:
        log.exception("Telethon session validation failed: %s", e)

if __name__ == "__main__":
    asyncio.run(main())
