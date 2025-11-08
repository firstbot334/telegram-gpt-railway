# summary_poster.py â ìì½+ì¬ê² í´ì+í¬ì í´ì + ìë¦¼ + ê´ì¬í¤ìë íì´ë¼ì´í¸
import os, asyncio, textwrap, html, re
from typing import List
from telethon import TelegramClient
from telethon.sessions import StringSession
from db import SessionLocal
from models import Article

API_ID = int(os.environ["TELEGRAM_API_ID"]) 
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELETHON_SESSION"]

DEST = os.environ.get("DEST_CHANNEL")                  # íì: ìì½ ì¬ë¦¬ë¥¼ ì±ë
ALERT_CHANNEL = os.environ.get("ALERT_CHANNEL", "")    # ì í: ìë¦¼ ì ì© ì±ë
INTEREST = os.environ.get("INTEREST_KEYWORDS", "")     # ì í: ê´ì¬ í¤ìë
ALERT_KEYS = os.environ.get("ALERT_KEYWORDS", "")      # ì í: ìë¦¼ í¸ë¦¬ê±° í¤ìë
BATCH = int(os.environ.get("SUMMARY_BATCH", "30"))     # ë°°ì¹ 크ê¸°
DEFAULT_SILENT = os.environ.get("SILENT", "true").lower() in ("1","true","yes","y")

def _norm_list(csv: str) -> List[str]:
    items = []
    for t in csv.replace("ï¼", ",").split(","):
        t = t.strip()
        if t:
            items.append(t)
    return items

INTEREST_LIST = _norm_list(INTEREST)
ALERT_LIST = [s.lower() for s in _norm_list(ALERT_KEYS)]

def _has_alert_keyword(text: str) -> bool:
    base = (text or "").lower()
    return any(k in base for k in ALERT_LIST) if ALERT_LIST else False

def _openai_summarize_invest(text: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        head = textwrap.shorten(text or "", width=500, placeholder="\xe2\x80\xa6")
        return (
            "\xf0\x9f\x93\x8c \xed\\x9c\xec\x8b\xac \xec\x9a\x94\xec\x95\xbd\n"
            f"{head}\n\n"
            "\xf0\x9f\xa7\xbe \xec\x89\xac\xea\xb2\x8c \xed\x95\xb4\xec\x84\x9d\n"
            "\xed\x95\xb5\xec\x8b\xac\xeb\xa7\x8c \xea\xb0\x84\xeb\x8b\xa8\xed\x9e\x88 \xec\xa0\x95\xeb\xa6\xac\xed\x96\x88\xec\x8a\xb5\xeb\x8b\x88\xeb\x8b\xa4.\n\n"
            "\xf0\x9f\x93\x88 \xed\x88\xac\xec\x9e\x90 \xea\xb4\x80\xec\xa0\x90\n"
            "\xec\xa4\x91\xeb\xa6\xbd: \xec\xb6\x94\xea\xb0\x80 \xec\xa0\x95\xeb\xb3\xb4 \xeb\x8c\x80\xea\xb8\xb0.\n"
        )

    prompt = (
        "\xed\x95\x9c\xea\xb5\xad\xec\96\xb4\xeb\xa1\x9c \xeb\x8b\xa4\xec\x9d\x8c \xed\x98\xb9\ec\x8b\xac\xc2\xb7\xed\x95\xb5\xec\x8b\xac \xeb\x82\xb4\xec\x9a\xa9\xec\9d\x84 \xea\xb0\x84\xea\xb2\bd\xed\95\x98\xea\xb2\x8c \xec\xa0\x95\xeb\xa6\xac\xed\95\xb4\xec\xa3\xbc\xec\x84\xb8\xec\x9a\x94.\n"
        "1) \xf0\x9f\x93\x8c \xed\x95\x9c\xec\x8b\xac \xec\x9a\x94\xec\x95\xbd: 2\xe2\x80\x933\xec\xa4\x84\n"
        "2) \xf0\x9f\xa7\xbe \xec\x89\xac\xea\xb2\x8c \xed\x95\xb4\xec\x84\x9d: 2\xe2\x80\x933\xec\xa4\x84\n"
        "3) \xf0\x9f\x93\x88 \xed\x88\xac\xec\x9e\x90 \xea\xb4\x80\xec\xa0\x90: (\xea\¸\xb0\xec\xa0\x95/\xeb\xb6\x80\xec\a0\x95/\xec\xa4\x91\xeb\xa6\xbd) + \xec\x9d\xb4\xec\x9c\xa0 1\xe2\x80\x932\xec\xa4\x84\n"
        "4) \xf0\x9f\x94\x96 \xed\x95´\xec\xed\xea·¸: 3\xe2\x80\x936\xea\xb0\x9c (\xeb\x9c\x80\xec\96\x80\xec\x93\xb0\xea\xb8\xb0 \xec\x86\xec\x8c)\n\n"
        f"\xea\xb4\x80\xec\x8b\xac \xed\x82\xa4\xec\x9b\x8c\xeb\x93\x9c: {', '.join(INTEREST_LIST) if INTEREST_LIST else '없음'}\n\n"
        f"\xec\x9b\x90\xeb\xac\xbc:\n{text[:7000]}\n"
    )

    try:
        import openai
        openai.api_key = key
        resp = openai.ChatCompletion.create(
            model=os.environ.get("OPENAI_MODEL","gpt-4o-mini"),
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message["content"].strip()
    except Exception:
        pass
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL","gpt-4o-mini"),
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
        )
        content = resp.choices[0].message.content
        if isinstance(content, list) and content and hasattr(content[0], "text"):
            return content[0].text.strip()
        return str(content).strip()
    except Exception:
        head = textwrap.shorten(text or "", width=500, placeholder="\xe2\x80\xa6")
        return (
            "\xf0\x9f\x93\x8c \xed\x95\x9c\xec\x8b\xac \xec\x9a\x94\xec\x95\xbd\n"
            f"{head}\n\n"
            "\xf0\x9f\xa7\xbe \xec\x89\xac\xea\xb2\x8c \xed\x95\xb4\xec\x84\x9d\n"
            "\xed\x95\xb5\xec\x8b\xac\xeb\xa7\x8c \xea\xb0\x84\xeb\x8b\xa8\xed\x9e\x88 \xec\xa0\x95\xeb\xa6\xac\xed\x96\x88\xec\x8a\xb5\xeb\x8b\x88\xeb\x8b\xa4.\n\n"
            "\xf0\x9f\x93\x88 \xed\x88\xac\xec\x9e\x90 \xea\xb4\x80\xec\xa0\x90\n"
            "\xec\xa4\x91\xeb\xa6\xbd: \xec\xb6\x94\xea\xb0\x80 \xec\xa0\x95\xeb\xb3\xb4 \xeb\x8c\x80\xea\xb8\xb0.\n"
        )

def _parse_dest(val: str):
    if not val:
        raise RuntimeError("DEST_CHANNEL env var is not set")
    v = val.strip()
    if v.startswith("-") or v.isdigit():
        try:
            return int(v)
        except ValueError:
            return v
    return v

def _highlight_interests(text: str) -> str:
    # Telegram은 색상을 지원하지 않음 -> HTML <b> + 빨간 점(\xF0\x9F\x94\xB4) 이모지로 강조
    if not text:
        return ""
    safe = html.escape(text, quote=False)
    if not INTEREST_LIST:
        return safe
    for kw in INTEREST_LIST:
        if not kw:
            continue
        pat = re.compile(re.escape(kw), flags=re.IGNORECASE)
        safe = pat.sub(lambda m: f"<b>\xf0\x9f\x94\xb4{m.group(0)}</b>", safe)
    return safe

async def main():
    dest = _parse_dest(DEST)
    alert_dest = _parse_dest(ALERT_CHANNEL) if ALERT_CHANNEL else dest

    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        s = SessionLocal()
        try:
            rows = s.query(Article)\
                    .filter((Article.summary==None) | (Article.summary==""))\
                    .order_by(Article.id.asc())\
                    .limit(BATCH).all()
            if not rows:
                print("[summary] nothing to do"); return

            for r in rows:
                try:
                    text = r.text or ""
                    result = _openai_summarize_invest(text)
                    r.summary = result
                    s.commit()

                    is_alert = _has_alert_keyword(text) or ("\xf0\x9f\x93\x88" in result and ("\xeb\xb6\x80\xec\ \x95" in result or "\xea\¸\xb0\xec\xa0\x95" in result))
                    silent = False if is_alert or os.environ.get("ALWAYS_NOTIFY","false").lower() in ("1","true","yes","y") else DEFAULT_SILENT

                    header = f"\xf0\x9f\x93\xb0 ({r.date})"  # 📰
                    body_html = _highlight_interests(result)
                    msg_html = f"{header}<br><br>{body_html}"

                    await client.send_message(alert_dest if is_alert else dest, msg_html, parse_mode="html", silent=silent)
                    print(f"[summary] posted id={r.id} alert={is_alert} silent={silent}")
                except Exception as e:
                    s.rollback()
                    print("[summary] error on id", r.id, e)

            print("\xe2\x9c\x85 summary done.")
        finally:
            s.close()

if __name__ == "__main__":
    asyncio.run(main())
