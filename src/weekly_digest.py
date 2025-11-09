import logging, re, html
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from telegram import Bot
from .db import get_engine
from .models import messages
from .config import settings
from .logging_setup import setup_logging

setup_logging()
log = logging.getLogger("digest")

def make_digest_html(items):
    freq = {}
    for _, content, sm in items:
        text = (content or "") + " " + (sm or "")
        for m in re.findall(r"[A-Z][A-Za-z0-9_]{2,}", text):
            freq[m] = freq.get(m,0)+1
    top = sorted(freq.items(), key=lambda x:x[1], reverse=True)[:10]
    lines = ["<b>TOP 키워드</b>"]
    if not top:
        lines.append("- (없음)")
    else:
        for k,c in top:
            lines.append(f"- {html.escape(k)} ({c})")
    return "<br/>".join(lines)

def run(bot: Bot):
    tz = timezone(timedelta(hours=9))
    start = datetime.now(tz) - timedelta(days=7)
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(select(messages.c.title, messages.c.content, messages.c.summary_html).where(messages.c.created_at>=start)).all()
    digest = make_digest_html(rows)
    bot.send_message(chat_id=settings.DEST_CHAT_ID, text=digest, parse_mode="HTML")
    log.info("digest sent")

if __name__ == "__main__":
    if settings.DEST_BOT_TOKEN:
        run(Bot(token=settings.DEST_BOT_TOKEN))
