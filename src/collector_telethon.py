import asyncio, logging, re, httpx, hashlib
from datetime import timedelta, timezone, datetime
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from sqlalchemy import insert, select, delete, func
from .config import settings
from .logging_setup import setup_logging
from .db import get_engine
from .models import messages
from .utils import split_sources, sha256_of

setup_logging()
log = logging.getLogger("collector")

# --- helpers ---
URL_RX = re.compile(r"(https?://\S+)", re.I)

async def fetch_url_text(url: str, timeout=10) -> Tuple[Optional[str], Optional[str]]:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent":"Mozilla/5.0 (bot)"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.title.text.strip() if soup.title else None
            # crude text extraction
            for tag in soup(["script","style","noscript"]):
                tag.decompose()
            text = " ".join(t.strip() for t in soup.get_text(" ").split())
            return title, text[:10000]  # truncate
    except Exception as e:
        log.warning("fetch_url_text failed for %s: %s", url, e)
        return None, None

async def collect_once():
    engine = get_engine()
    async with TelegramClient(StringSession(settings.TELETHON_SESSION), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        sources = split_sources(settings.SRC_CHANNELS)
        for src in sources:
            try:
                log.info("Reading from %s", src)
                async for m in client.iter_messages(src, limit=200):
                    text = (m.raw_text or "").strip()
                    url = None
                    murls = URL_RX.findall(text) if text else []
                    if murls:
                        url = murls[0]
                        title2, text2 = await fetch_url_text(url)
                        # prefer fetched article text if original text is too short
                        if (not text) or len(text) < 40:
                            text = (title2 or "") + "\n" + (text2 or text)
                    if not text:
                        continue
                    h = sha256_of(src, str(m.id), text[:500], url or "")
                    try:
                        with engine.begin() as conn:
                            # unique by hash; also keep (src,msg_id) uniqueness
                            conn.execute(insert(messages).prefix_with("OR IGNORE" if engine.url.get_backend_name()=="sqlite" else ""), {
                                "src": src, "msg_id": str(m.id), "url": url, "title": None, "content": text, "summary_html": None, "hash": h
                            })
                    except Exception as e:
                        # For Postgres, rely on unique index to ignore duplicates
                        log.debug("insert failed (likely duplicate): %s", e)
            except FloodWaitError as fw:
                log.warning("FloodWait %s seconds on %s", fw.seconds, src)
                await asyncio.sleep(fw.seconds + 1)
            except ValueError as ve:
                # entity not found or invalid peer
                log.error("Source invalid or not joined: %s (%s)", src, ve)
            except Exception as e:
                log.exception("iter_messages failed for %s: %s", src, e)

if __name__ == "__main__":
    asyncio.run(collect_once())
