# weekly_digest.py — Monday digest: top 5 companies & 5 news (last 5 days), with raw source quotes
import os, asyncio, datetime, html, re, textwrap
from zoneinfo import ZoneInfo
from collections import Counter
from telethon import TelegramClient
from telethon.sessions import StringSession
from db import SessionLocal
from models import Article

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELETHON_SESSION"]
DEST = os.environ.get("DEST_CHANNEL")
KST = ZoneInfo("Asia/Seoul")

COMPANY_KEYS = os.environ.get("COMPANY_KEYWORDS") or os.environ.get("INTEREST_KEYWORDS","")
TOPN = int(os.environ.get("DIGEST_TOPN","5"))
DAYS = int(os.environ.get("DIGEST_DAYS","5"))
DIGEST_SILENT = os.environ.get("DIGEST_SILENT","false").lower() in ("1","true","yes","y")

def _norm_list(csv: str):
    items = []
    for t in csv.replace("，", ",").split(","):
        t = t.strip()
        if t:
            items.append(t)
    return items

COMPANY_LIST = _norm_list(COMPANY_KEYS)

def _top_companies(rows):
    if not COMPANY_LIST:
        return []
    c = Counter()
    for r in rows:
        txt = (r.text or "").lower()
        for k in COMPANY_LIST:
            if k:
                c[k] += txt.count(k.lower())
    return [k for k,_ in c.most_common(TOPN) if c[k] > 0]

def _highlight(text, keys):
    if not text:
        return ""
    safe = html.escape(text, quote=False)
    for k in keys:
        if not k:
            continue
        pat = re.compile(re.escape(k), re.IGNORECASE)
        safe = pat.sub(lambda m: f"<b>🔴{m.group(0)}</b>", safe)
    return safe

async def main():
    if not DEST:
        raise RuntimeError("DEST_CHANNEL not set")
    start = datetime.datetime.now(tz=KST) - datetime.timedelta(days=DAYS)
    s = SessionLocal()
    try:
        rows = s.query(Article).filter(Article.date >= start).order_by(Article.date.desc()).all()
        top_comp = _top_companies(rows)
        top_news = rows[:TOPN]  # 최근 뉴스 상위 N개

        date_str = datetime.datetime.now(tz=KST).strftime("%Y-%m-%d")
        header = f"📅 주간 리마인드 ({date_str}) — 지난 {DAYS}일"
        comp_html = "· " + "<br>· ".join(_highlight(x, top_comp) for x in top_comp) if top_comp else "· (회사 키워드 없음)"
        news_blocks = []
        for i, r in enumerate(top_news, 1):
            raw = textwrap.shorten(r.text or "", width=1500, placeholder="…")
            block = f"<b>{i}.</b> <i>{r.date}</i> — <code>{html.escape(r.source or 'unknown', quote=False)}</code><br>{_highlight(raw, COMPANY_LIST)}"
            news_blocks.append(block)
        news_html = "<br><br>".join(news_blocks) if news_blocks else "(최근 뉴스가 없습니다)"
        body = f"<b>▶ 자주 언급된 상위 {TOPN} 기업</b><br>{comp_html}<br><br><b>▶ 최근 {TOPN}개 뉴스 (원문 멘트 그대로)</b><br>{news_html}"
    finally:
        s.close()

    dest = int(DEST) if DEST.lstrip('-').isdigit() else DEST
    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        await client.send_message(dest, f"{header}<br><br>{body}", parse_mode="html", silent=DIGEST_SILENT)
        print("✅ weekly digest posted.")

if __name__ == "__main__":
    asyncio.run(main())
