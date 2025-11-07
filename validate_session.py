import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    sess = os.getenv("TELETHON_SESSION", "").strip()
    if not (api_id and api_hash and sess):
        print("Missing env(s). Provide TELEGRAM_API_ID/TELEGRAM_API_HASH/TELETHON_SESSION.")
        return
    client = TelegramClient(StringSession(sess), int(api_id), api_hash)
    await client.connect()
    me = await client.get_me()
    print("Session user:", getattr(me, "username", None) or me.id)
    print("Is bot?:", bool(getattr(me, "bot", False)))
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
