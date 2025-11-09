import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    api_id = os.getenv('TELEGRAM_API_ID'); api_hash = os.getenv('TELEGRAM_API_HASH'); sess = os.getenv('TELETHON_SESSION','').strip()
    if not (api_id and api_hash and sess): print('[validate] missing api/session envs'); return
    client = TelegramClient(StringSession(sess), int(api_id), api_hash); await client.connect()
    me = await client.get_me()
    print('[validate] user:', getattr(me,'username',None) or me.id); print('[validate] is_bot?:', bool(getattr(me,'bot',False)))
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
