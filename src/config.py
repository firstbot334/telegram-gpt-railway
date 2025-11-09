from pydantic import BaseModel
import os

class Settings(BaseModel):
    # Telegram (Telethon reader)
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID","0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH","")
    TELETHON_SESSION: str = os.getenv("TELETHON_SESSION","")  # string session

    # Sources (comma/space separated: @name or https://t.me/name)
    SRC_CHANNELS: str = os.getenv("SRC_CHANNELS","")

    # Destination (Bot API poster)
    DEST_BOT_TOKEN: str = os.getenv("DEST_BOT_TOKEN","")
    DEST_CHAT_ID: str = os.getenv("DEST_CHAT_ID","")

    # DB
    DATABASE_URL: str = os.getenv("DATABASE_URL","sqlite:///./newsbot.db")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY","")

    # Behavior
    RUN_INTERVAL_MIN: int = int(os.getenv("RUN_INTERVAL_MIN","10"))
    MAX_DAYS_KEEP: int = int(os.getenv("MAX_DAYS_KEEP","60"))
    DIGEST_HOUR_KST: int = int(os.getenv("DIGEST_HOUR_KST","9"))

    INTEREST_KEYWORDS: str = os.getenv("INTEREST_KEYWORDS","NVDA,TSMC,AI,data center,EV")
    ALERT_KEYWORDS: str = os.getenv("ALERT_KEYWORDS","bankruptcy,SEC investigation,SEC probe,delisting")

settings = Settings()
