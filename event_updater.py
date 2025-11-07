from datetime import datetime, timedelta, timezone
import os
from openai import OpenAI
from db import SessionLocal
from models import Event, Article
from tg_util import tg_send_or_edit
from config import STANCE_MODEL, OPENAI_API_KEY, SUMMARY_CHANNEL

KST = timezone(timedelta(hours=9))

def _render_events(session) -> str:
    today = datetime.now(KST).date()
    events = session.query(Event).order_by(Event.event_date.asc()).all()
    lines = ["<b>📌 이벤트 캘린더(업데이트)</b>"]
    for ev in events:
        mark = "✅" if ev.event_date and ev.event_date <= today else "🗓️"
        title = (ev.headline or "").strip()
        date_str = ev.event_date.strftime("%Y-%m-%d") if ev.event_date else "TBD"
        lines.append(f"{mark} <b>{date_str}</b> — {title}")
        if ev.note:
            lines.append(f" └ {ev.note}")
    return "\n".join(lines)

def main():
    session = SessionLocal()
    try:
        text = _render_events(session)
        # Keep HTML but let tg_util handle fallback on parse errors
        msg = tg_send_or_edit(SUMMARY_CHANNEL, None, text, pin=True, parse_mode="HTML")
    finally:
        session.close()

if __name__ == "__main__":
    main()