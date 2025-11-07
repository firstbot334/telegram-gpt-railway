# 로컬에서 한 번 실행해 TELETHON_SESSION 문자열을 생성하는 도구입니다.
# 실행 후 나온 문자열을 Railway 환경변수 TELETHON_SESSION에 그대로 넣으세요.
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 39591049
API_HASH = "63051274cc060175aee8f62d636cfa6f"

async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        # 처음 실행 시 전화번호/인증코드 입력 프롬프트가 뜹니다.
        session_str = client.session.save()
        print("\n=== COPY THIS STRING ===\n")
        print(session_str)
        print("\nPut it into TELETHON_SESSION env var on Railway.")

if __name__ == "__main__":
    asyncio.run(main())
