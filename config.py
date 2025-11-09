import os
def _as_list(v):
    if v is None: return []
    if isinstance(v, (list, tuple)): return [str(x).strip() for x in v if str(x).strip()]
    return [s.strip() for s in str(v).split(',') if s.strip()]

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELETHON_SESSION = os.getenv('TELETHON_SESSION','')
DATABASE_URL = os.getenv('DATABASE_URL','')

NEWS_SOURCES = _as_list(os.getenv('NEWS_SOURCES',''))
BACKFILL_DAYS = int(os.getenv('BACKFILL_DAYS','2'))

SUMMARY_CHANNEL = os.getenv('SUMMARY_CHANNEL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
STANCE_MODEL = os.getenv('STANCE_MODEL','gpt-4o-mini')
INTEREST_KEYWORDS = os.getenv('INTEREST_KEYWORDS','')
TZ = os.getenv('TZ','Asia/Seoul')
