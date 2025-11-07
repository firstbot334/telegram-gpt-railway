import os

def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in str(value).split(",") if v.strip()]

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELETHON_SESSION = os.getenv("TELETHON_SESSION", "")

NEWS_SOURCES = _as_list(os.getenv("NEWS_SOURCES", ""))
BACKFILL_DAYS = int(os.getenv("BACKFILL_DAYS", "2"))
DATABASE_URL = os.getenv("DATABASE_URL", "")

SUMMARY_CHANNEL = os.getenv("SUMMARY_CHANNEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STANCE_MODEL = os.getenv("STANCE_MODEL", "gpt-4o-mini")
INTEREST_KEYWORDS = os.getenv("INTEREST_KEYWORDS", "")
TZ = os.getenv("TZ", "Asia/Seoul")
