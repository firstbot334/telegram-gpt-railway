from pydantic import BaseModel
import os

class Settings(BaseModel):
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID","0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH","")
    TELETHON_SESSION: str = os.getenv("TELETHON_SESSION","")
    SRC_CHANNELS: str = os.getenv("SRC_CHANNELS","")
    # Optional invite links (comma/space separated, e.g., https://t.me/+abcd...)
    SRC_INVITES: str = os.getenv("SRC_INVITES","")
    DEST_BOT_TOKEN: str = os.getenv("DEST_BOT_TOKEN","")
    DEST_CHAT_ID: str = os.getenv("DEST_CHAT_ID","")
    DATABASE_URL: str = os.getenv("DATABASE_URL","sqlite:///./newsbot.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY","")
    RUN_INTERVAL_MIN: int = int(os.getenv("RUN_INTERVAL_MIN","10"))
    MAX_DAYS_KEEP: int = int(os.getenv("MAX_DAYS_KEEP","60"))
    DIGEST_HOUR_KST: int = int(os.getenv("DIGEST_HOUR_KST","9"))
    INTEREST_KEYWORDS: str = os.getenv("INTEREST_KEYWORDS","NVDA,TSMC,AI,data center,EV")
    ALERT_KEYWORDS: str = os.getenv("ALERT_KEYWORDS","bankruptcy,SEC investigation,SEC probe,delisting")

settings = Settings()
