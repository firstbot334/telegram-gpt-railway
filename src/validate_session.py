import logging, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from .config import settings
from .logging_setup import setup_logging
setup_logging()
log = logging.getLogger("validate")
async def main():
    if not (settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH and settings.TELETHON_SESSION):
        log.warning("Missing Telethon credentials; skipping validate.")
        return
    try:
        async with TelegramClient(StringSession(settings.TELETHON_SESSION), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
            me = await client.get_me()
            log.info("Telethon OK: id=%s bot=%s", me.id, bool(me.bot))
    except Exception as e:
        log.exception("validate failed: %s", e)
if __name__ == "__main__":
    asyncio.run(main())
