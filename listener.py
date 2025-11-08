# listener.py
import os, asyncio, re, hashlib
from typing import List
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

# ==== 환경변수 ====
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION  = os.getenv("TELETHON_SESSION")          # StringSession
DEST     = os.getenv("DEST_CHANNEL")              # @mychannel 또는 -100...
SRC      = os.getenv("SRC_CHANNELS", "")          # 콤마로 구분(@a,https://t.me/b,...)

USE_GPT  = os.getenv("USE_GPT", "0") == "1"       # 1 이면 GPT 요약 사용
OPENAI_KEY   = os.getenv("OPENAI_API_KEY")        # USE_GPT=1일 때 필요
OPENAI_MODEL = os.getenv("STANCE_MODEL", "gpt-4o-mini")

# ==== 유틸 ====
def normalize(x: str) -> str:
    x = x.strip().rstrip(",")
    if x.startswith("@"):
        return f"https://t.me/{x[1:]}"
    if x.startswith("t.me/"):
        return f"https://{x}"
    return x

SRC_LIST: List[str] = [normalize(s) for s in SRC.split(",") if s.strip()]

_seen = set()                         # 메모리 중복 필터
URL_RE = re.compile(r"https?://\S+")

def dedup_key(text: str) -> str:
    return hashlib.md5(text.encode("utf-8", "ignore")).hexdigest()

# ==== (선택) GPT 요약 ====
async def summarize_if_needed(text: str) -> str:
    if not USE_GPT or not OPENAI_KEY:
        return text
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        prompt = f"다음 텍스트를 한 줄로 아주 간결하게 요약해줘:\\n\\n{text[:4000]}"
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role":"system","content":"한국어로 짧고 정확하게 요약합니다."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2
        )
        summary = resp.choices[0].message.content.strip()
        urls = URL_RE.findall(text)
        if urls:
            summary += "\\n" + " ".join(urls[:3])   # URL 보존
        return summary
    except Exception as e:
        return f"{text}\\n(요약 실패: {e})"

# ==== Telethon 클라이언트 ====
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

async def ensure_joined_public(entity_like: str):
    \"\"\"공개 채널은 실행 시 자동 조인 시도(이미 조인돼 있으면 조용히 통과).\"\"\"
    ent = await client.get_entity(entity_like)
    try:
        await client(JoinChannelRequest(ent))
    except Exception:
        pass
    return ent

@client.on(events.NewMessage(chats=SRC_LIST))
async def on_new_message(ev: events.NewMessage.Event):
    text = (ev.raw_text or \"\").strip()

    # 링크만 있는 글도 통과 (완전 빈 메시지만 제외)
    if not text and not ev.message.media and not ev.message.entities:
        return

    urls = URL_RE.findall(text)
    base = text if not urls else \" \".join(sorted(set(urls)))
    k = dedup_key(f\"{ev.chat_id}:{base}\")
    if k in _seen:
        return
    _seen.add(k)

    out = await summarize_if_needed(text)

    try:
        dest_ent = await client.get_entity(DEST)
        await client.send_message(dest_ent, out)
    except Exception as e:
        print(\"send fail:\", e)

async def main():
    # 실행 시 소스 채널 resolve/조인(안전장치)
    for s in SRC_LIST:
        try:
            await ensure_joined_public(s)
        except Exception as e:
            print(\"join/resolve fail:\", s, e)

    await client.start()
    me = await client.get_me()
    print(\"listening as:\", me.username or me.phone)
    print(\"sources:\", SRC_LIST)
    print(\"dest:\", DEST)
    await client.run_until_disconnected()

if __name__ == \"__main__\":
    asyncio.run(main())
