# 로컬에서 한 번 실행해 사용자 StringSession을 발급하세요.
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(input("API_ID: ").strip())
API_HASH = input("API_HASH: ").strip()

async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        print("\n=== TELETHON_SESSION (USER) ===")
        print(client.session.save())

if __name__ == "__main__":
    asyncio.run(main())
