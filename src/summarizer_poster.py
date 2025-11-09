import logging, html
from sqlalchemy import select
from .db import get_engine
from .models import messages
from .config import settings
from .logging_setup import setup_logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
setup_logging(); log = logging.getLogger('summary')
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
PROMPT = "다음 기사를 '한줄핵심/쉬운해석/투자관점'(각 60~120자, 한국어) 형식으로 요약하라."
@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1,min=1,max=20), reraise=True)
def summarize_text(txt:str)->str:
    if not client: return html.escape((txt[:300]+'...') if len(txt)>300 else txt)
    r = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role':'system','content':'You are a concise financial news summarizer.'},{'role':'user','content':PROMPT+'\n\n---\n\n'+txt}], temperature=0.2, max_tokens=320)
    return r.choices[0].message.content.strip()

def run(limit=120):
    engine=get_engine()
    with engine.begin() as conn:
        rows = conn.execute(select(messages.c.id, messages.c.content, messages.c.url).where(messages.c.summary_html==None).limit(limit)).all()
        for rid, content, url in rows:
            try:
                sm = summarize_text(content or '')
                if url: sm = f"{sm}<br/><a href='{html.escape(url)}'>원문</a>"
                conn.execute(messages.update().where(messages.c.id==rid).values(summary_html=sm)); log.info('[summary] id=%s', rid)
            except Exception as e:
                log.exception('summarize failed id=%s: %s', rid, e)
if __name__=='__main__': run()
