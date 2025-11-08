import os, asyncio, re, datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from openai import OpenAI

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION  = os.getenv("TELETHON_SESSION_SUMMARY")
DEST     = os.getenv("DEST_CHANNEL")
SRC      = os.getenv("SRC_CHANNELS", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("STANCE_MODEL", "gpt-4o-mini")
DAYS_BACK = int(os.getenv("SUMMARY_DAYS", "1"))
URL_RE = re.compile(r"https?://\S+")

gpt = OpenAI(api_key=OPENAI_KEY)
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

async def summarize_texts(texts):
    joined = "\n\n".join(texts[:50])[:8000]
    prompt = f"""
다음은 지난 {DAYS_BACK}일간 여러 텔레그램 채널에서 수집된 뉴스/게시글입니다.
내용을 중복 없이 간결하게 정리하고, 핵심 주제별로 묶어 10줄 이내 요약을 만들어주세요.
중요한 숫자, 회사명, 날짜는 그대로 유지하세요.
-----------------------
{joined}
-----------------------
"""
    try:
        resp = gpt.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "한국어로 분석 보고서를 간결하게 요약합니다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"요약 실패: {e}"

async def main():
    await client.start()
    me = await client.get_me()
    print("summarizing as:", me.username or me.phone)

    now = datetime.datetime.utcnow()
    since = now - datetime.timedelta(days=DAYS_BACK)

    channels = [s.strip() for s in SRC.split(",") if s.strip()]
    all_texts = []

    for ch in channels:
        try:
            entity = await client.get_entity(ch)
            async for msg in client.iter_messages(entity, offset_date=now, reverse=True):
                if msg.date < since:
                    break
                if msg.raw_text:
                    all_texts.append(msg.raw_text.strip())
        except Exception as e:
            print("채널 접근 실패:", ch, e)

    if not all_texts:
        print("새 메시지가 없습니다.")
        return

    print(f"{len(all_texts)}개 메시지 수집 완료.")
    summary = await summarize_texts(all_texts)

    dest_ent = await client.get_entity(DEST)
    header = f"📅 {now.strftime('%Y-%m-%d')} 요약 보고서 ({len(all_texts)}개 메시지 기반)\n\n"
    await client.send_message(dest_ent, header + summary)
    print("요약 전송 완료.")

if __name__ == "__main__":
    asyncio.run(main())
