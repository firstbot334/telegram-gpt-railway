import os
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session
from openai import OpenAI
from telegram import Bot

from db import SessionLocal, Base, engine
from models import Article
from sqlalchemy import Column, Integer, DateTime, String

# processed table
class ProcessedArticle(Base):
    __tablename__ = "processed_articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, nullable=False, unique=True)
    posted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    note = Column(String(200), nullable=True)

Base.metadata.create_all(engine)

KST = timezone(timedelta(hours=9))
SUMMARY_CHANNEL = os.getenv("SUMMARY_CHANNEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STANCE_MODEL = os.getenv("STANCE_MODEL", "gpt-4o-mini")
INTEREST_KEYWORDS = os.getenv("INTEREST_KEYWORDS", "")
BACKFILL_DAYS = int(os.getenv("BACKFILL_DAYS", "2"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not (SUMMARY_CHANNEL and OPENAI_API_KEY and TELEGRAM_TOKEN):
    raise RuntimeError("Missing env: SUMMARY_CHANNEL / OPENAI_API_KEY / TELEGRAM_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

def fetch_unsent(session: Session, limit: int = 30):
    cutoff = datetime.now(KST) - timedelta(days=BACKFILL_DAYS)
    sub = session.query(ProcessedArticle.article_id)
    q = (
        session.query(Article)
        .filter(Article.created_at >= cutoff)
        .filter(~Article.id.in_(sub))
        .order_by(Article.created_at.asc())
        .limit(limit)
    )
    return q.all()

def build_prompt(items: List[Article]) -> str:
    lines = []
    for i, a in enumerate(items, 1):
        ts = a.created_at.strftime("%Y-%m-%d %H:%M")
        lines.append(f"{i}. ({ts}) {a.text}")
    corpus = "\n".join(lines)
    interest = INTEREST_KEYWORDS.strip()
    interest_clause = f"관심 키워드 참조: {interest}" if interest else ""
    return f"""다음 포스트들을 한국어로 5~8줄 요약해줘. 겹치는 내용은 묶고 핵심 수치/정책/가격 변동을 강조해.
{interest_clause}

Posts:
{corpus}
"""

def summarize(items: List[Article]) -> str:
    if not items:
        return ""
    prompt = build_prompt(items)
    resp = client.chat.completions.create(
        model=STANCE_MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.3,
        max_tokens=800,
    )
    return resp.choices[0].message.content.strip()

def post(text: str):
    if text:
        bot.send_message(chat_id=int(SUMMARY_CHANNEL), text=text)

def mark(session: Session, items: List[Article]):
    from datetime import datetime as dt
    now = dt.utcnow()
    for a in items:
        session.add(ProcessedArticle(article_id=a.id, posted_at=now))
    session.commit()

def main_once():
    session = SessionLocal()
    try:
        items = fetch_unsent(session, limit=30)
        if not items:
            print("[summary] no new items")
            return
        text = summarize(items)
        post(text)
        mark(session, items)
        print("[summary] posted")
    finally:
        session.close()

if __name__ == "__main__":
    main_once()
