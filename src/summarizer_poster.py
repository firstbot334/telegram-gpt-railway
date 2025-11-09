import logging, html
from sqlalchemy import select, update
from .db import get_engine
from .models import messages
from .config import settings
from .logging_setup import setup_logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

setup_logging()
log = logging.getLogger("summarizer")
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

PROMPT = ("다음 기사를 다음 형식으로 요약해줘:\n"
"- 한 줄 핵심 요약\n"
"- 쉬운 해석\n"
"- 투자 관점 (기회/위험)\n"
"한국어로, 60~120자/항목 내로 간결하게.\n"
)

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=20), reraise=True)
def summarize_text(txt: str) -> str:
    if not client:
        return html.escape((txt[:300] + "...") if len(txt) > 300 else txt)
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":"You are a concise financial news summarizer."},
                  {"role":"user","content":PROMPT + "\n\n---\n\n" + txt}],
        temperature=0.2,
        max_tokens=300
    )
    return r.choices[0].message.content.strip()

def apply_highlights(s: str) -> str:
    # interest keywords -> 🔴bold; alert keywords -> [ALERT] prefix
    interest = [w.strip() for w in settings.INTEREST_KEYWORDS.split(",") if w.strip()]
    alert = [w.strip() for w in settings.ALERT_KEYWORDS.split(",") if w.strip()]
    out = s
    for w in interest:
        out = out.replace(w, f"<b>🔴{html.escape(w)}</b>")
    for w in alert:
        out = out.replace(w, f"<b>[ALERT] {html.escape(w)}</b>")
    return out

def run_summarize(limit=100):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(select(messages.c.id, messages.c.content, messages.c.url).where(messages.c.summary_html==None).limit(limit)).all()
        for rid, content, url in rows:
            try:
                sm = summarize_text(content)
                sm = apply_highlights(sm)
                if url:
                    sm = f"{sm}<br/><a href='{html.escape(url)}'>원문</a>"
                conn.execute(messages.update().where(messages.c.id==rid).values(summary_html=sm))
            except Exception as e:
                log.exception("summarize failed id=%s: %s", rid, e)

if __name__ == "__main__":
    run_summarize()
