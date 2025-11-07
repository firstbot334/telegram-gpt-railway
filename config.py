
import os
from typing import List

def _get_env(*names: str, default: str | None = None) -> str | None:
    """
    Return the first non-empty environment variable among `names`.
    """
    for n in names:
        v = os.environ.get(n)
        if v is not None and str(v).strip() != "":
            return v
    return default

# --- Telegram / OpenAI / DB ---
OPENAI_API_KEY = _get_env("OPENAI_API_KEY", "OPENAI_APIKEY")

# Prefer TELEGRAM_TOKEN but allow TELEGRAM_BOT_TOKEN as a fallback
TELEGRAM_TOKEN = _get_env("TELEGRAM_TOKEN", "TELEGRAM_BOT_TOKEN")

# Telethon (user account) credentials for collector
TELEGRAM_API_ID = _get_env("TELEGRAM_API_ID", "API_ID")
TELEGRAM_API_HASH = _get_env("TELEGRAM_API_HASH", "API_HASH")
TELETHON_SESSION = _get_env("TELETHON_SESSION", "TELEGRAM_STRING_SESSION")

DATABASE_URL = _get_env("DATABASE_URL", "POSTGRES_DATABASE_URL")

# --- Channel / Source config ---
# Accept both modern and legacy names
SUMMARY_CHANNEL = _get_env("SUMMARY_CHANNEL", "TARGET_CHANNEL_ID")
# NEWS_SOURCES expects comma-separated usernames or IDs
NEWS_SOURCES_RAW = _get_env("NEWS_SOURCES", "SOURCE_CHANNEL_IDS", default="")
NEWS_SOURCES: List[str] = [s.strip() for s in NEWS_SOURCES_RAW.split(",") if s.strip()]

# Keywords (watched terms for summarization)
INTEREST_KEYWORDS_RAW = _get_env("INTEREST_KEYWORDS", "KEYWORDS", default="")
INTEREST_KEYWORDS: List[str] = [s.strip() for s in INTEREST_KEYWORDS_RAW.split(",") if s.strip()]

# Model defaults (use a currently-available chat model)
STANCE_MODEL = _get_env("STANCE_MODEL", default="gpt-4o-mini")

# Misc
BACKFILL_DAYS = int(_get_env("BACKFILL_DAYS", default="2") or "2")
TZ = _get_env("TZ", default="Asia/Seoul")

def require(name: str, value: str | None):
    if not value:
        raise RuntimeError(f"Required config '{name}' is missing. Please set it in your environment.")
    return value

def require_any(name: str, values: list[tuple[str,str|None]]):
    for key, val in values:
        if val:
            return val
    pretty = ", ".join(k for k,_ in values)
    raise RuntimeError(f"Required config '{name}' is missing. Please set one of: {pretty}")

# Quick validation helper (optional; call in entrypoints)
def validate_minimum_env():
    require("OPENAI_API_KEY", OPENAI_API_KEY)
    require("TELEGRAM_TOKEN", TELEGRAM_TOKEN)
    require("DATABASE_URL", DATABASE_URL)
    require("SUMMARY_CHANNEL", SUMMARY_CHANNEL)
    # NEWS_SOURCES can be empty for summarize-only flows, but collector requires it

