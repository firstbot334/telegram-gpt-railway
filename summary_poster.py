import os
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from openai import OpenAI
from telegram import Bot
from db import SessionLocal, Base, engine
from models import Article
from sqlalchemy import Column, Integer, DateTime, String

class ProcessedArticle(Base):
    __tablename__ = 'processed_articles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, nullable=False, unique=True)
    posted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    note = Column(String(200), nullable=True)

Base.metadata.create_all(engine)

KST = timezone(timedelta(hours=9))
SUMMARY_CHANNEL = os.getenv('SUMMARY_CHANNEL'); OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
STANCE_MODEL = os.getenv('STANCE_MODEL','gpt-4o-mini'); INTEREST_KEYWORDS = os.getenv('INTEREST_KEYWORDS','')
BACKFILL_DAYS = int(os.getenv('BACKFILL_DAYS','2')); TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not (SUMMARY_CHANNEL and OPENAI_API_KEY and TELEGRAM_TOKEN): raise RuntimeError('Missing SUMMARY_CHANNEL/OPENAI_API_KEY/TELEGRAM_TOKEN')
client = OpenAI(api_key=OPENAI_API_KEY); bot = Bot(token=TELEGRAM_TOKEN)

def fetch_unsent(session: Session, limit:int=30):
    cutoff = datetime.now(KST) - timedelta(days=BACKFILL_DAYS)
    sub = session.query(ProcessedArticle.article_id)
    return (session.query(Article).filter(Article.created_at >= cutoff).filter(~Article.id.in_(sub)).order_by(Article.created_at.asc()).limit(limit).all())

def build_prompt(items: List[Article]) -> str:
    lines = [f"{i}. ({a.created_at:%Y-%m-%d %H:%M}) {a.text}" for i,a in enumerate(items,1)]
    interest = INTEREST_KEYWORDS.strip()
    return f"한국어로 5~8줄 요약. 중복은 합치고 핵심 수치/정책/가격 강조.\n관심키워드: {interest}\n\n" + "\n".join(lines)

def summarize(items: List[Article]) -> str:
    if not items: return ''
    resp = client.chat.completions.create(model=STANCE_MODEL, messages=[{'role':'user','content':build_prompt(items)}], temperature=0.3, max_tokens=800)
    return resp.choices[0].message.content.strip()

def post(text:str):
    if text: bot.send_message(chat_id=int(SUMMARY_CHANNEL), text=text)

def mark(session: Session, items: List[Article]):
    from datetime import datetime as dt
    now = dt.utcnow()
    for a in items: session.add(ProcessedArticle(article_id=a.id, posted_at=now))
    session.commit()

def main_once():
    s = SessionLocal()
    try:
        items = fetch_unsent(s, 30)
        if not items: print('[summary] no new items'); return
        text = summarize(items); post(text); mark(s, items); print('[summary] posted')
    finally:
        s.close()

if __name__ == '__main__':
    main_once()
