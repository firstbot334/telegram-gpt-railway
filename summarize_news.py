
import argparse
from datetime import datetime, timedelta, timezone
from typing import List
from openai import OpenAI
from db import SessionLocal
from models import Article
from tg_util import tg_send
from config import OPENAI_API_KEY, SUMMARY_CHANNEL, INTEREST_KEYWORDS, STANCE_MODEL

KST = timezone(timedelta(hours=9))

def fetch_articles(session, start: datetime, end: datetime) -> List[Article]:
    return session.query(Article).filter(Article.created_at >= start, Article.created_at < end).order_by(Article.created_at.asc()).all()

def build_prompt(articles: List[Article], window_label: str) -> str:
    items = []
    for a in articles:
        t = (a.text or "").strip()
        if a.url:
            t += f"\nURL: {a.url}"
        items.append(t)

    keywords = ", ".join(INTEREST_KEYWORDS) if INTEREST_KEYWORDS else "(키워드 제한 없음)"
    header = f"[요약 윈도우: {window_label}]\n감시 키워드: {keywords}\n\n"
    body = "\n---\n".join(items) if items else "수집된 뉴스가 없습니다."
    return header + body

def summarize(window: str):
    session = SessionLocal()
    try:
        now = datetime.now(KST)
        if window == "day":
            start = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now < start:
                start = start - timedelta(days=1)
            end = start + timedelta(hours=11)  # 9:00~20:00
            window_label = f"{start:%Y-%m-%d} 09:00 ~ {end:%Y-%m-%d} 20:00"
        else:  # night
            end = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now < end:
                end = end - timedelta(days=1)
            start = end - timedelta(hours=13)  # 20:00~다음날 09:00
            window_label = f"{start:%Y-%m-%d} 20:00 ~ {end:%Y-%m-%d} 09:00"

        articles = fetch_articles(session, start, end)
        prompt = build_prompt(articles, window_label)

        if not articles:
            tg_send(SUMMARY_CHANNEL, f"<b>{window_label}</b>\n수집된 뉴스가 없습니다.", parse_mode="HTML")
            return

        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=STANCE_MODEL,
            messages=[
                {"role": "system", "content": "너는 재무·산업 이슈 요약가다. 핵심 포인트를 5~10줄 bullet로 한국어로 정리하고, 꼭 수치(톤수, 매출, 증설 규모 등)를 남겨라."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        text = completion.choices[0].message.content.strip()
        header = f"<b>{window_label} 요약</b>\n"
        tg_send(SUMMARY_CHANNEL, header + text, parse_mode="HTML")
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", choices=["day", "night"], default="day", help="요약 시간창 (기본: day)")
    args = parser.parse_args()
    summarize(args.window)

if __name__ == "__main__":
    main()
