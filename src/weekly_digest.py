import logging, html, re
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from telegram import Bot
from .db import get_engine
from .models import messages
from .config import settings
from .logging_setup import setup_logging

setup_logging()
log = logging.getLogger("weekly_digest")

def make_digest_html(items):
    # naive frequency of capitalized tokens as "entities"
    freq = {}
    for title, content, sm in items:
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

def run_digest(bot: Bot):
    tz = timezone(timedelta(hours=9))  # KST
    now = datetime.now(tz)
    # Monday 09:00 trigger should be handled by run loop; here we just compute range
    start = now - timedelta(days=7)
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(select(messages.c.title, messages.c.content, messages.c.summary_html).where(messages.c.created_at>=start)).all()
    digest = make_digest_html(rows)
    bot.send_message(chat_id=settings.DEST_CHAT_ID, text=digest, parse_mode="HTML")

if __name__ == "__main__":
    from telegram import Bot
    bot = Bot(token=settings.DEST_BOT_TOKEN) if settings.DEST_BOT_TOKEN else None
    if bot:
        run_digest(bot)
