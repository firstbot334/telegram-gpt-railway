import os
from pydantic import BaseModel

def _get_keywords():
    k1 = os.getenv("KEYWORDS", "")
    if k1.strip():
        return k1
    return os.getenv("INTEREST_KEYWORDS", "")

class Settings(BaseModel):
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID","0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH","")
    TELETHON_SESSION: str = os.getenv("TELETHON_SESSION","")
    SRC_CHANNELS: str = os.getenv("SRC_CHANNELS","")  # t.me URLs only
    KEYWORDS: str = _get_keywords()
    DATABASE_URL: str = os.getenv("DATABASE_URL","sqlite:///./newsbot.db")
    RUN_INTERVAL_MIN: int = int(os.getenv("RUN_INTERVAL_MIN","30"))
    MAX_DAYS_KEEP: int = int(os.getenv("MAX_DAYS_KEEP","60"))
settings = Settings()
