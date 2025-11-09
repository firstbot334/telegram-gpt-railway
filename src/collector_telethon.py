import asyncio, logging, re, httpx
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from sqlalchemy import insert
from .config import settings
from .logging_setup import setup_logging
from .db import get_engine
from .models import messages
from .utils import sha256_of

setup_logging()
log = logging.getLogger("collector")
URL_RX = re.compile(r"(https?://\S+)", re.I)

async def fetch_url_text(url: str, timeout=10):
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent":"Mozilla/5.0 (bot)"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.title.text.strip() if soup.title else None
            for tag in soup(["script","style","noscript"]):
                tag.decompose()
            text = " ".join(t.strip() for t in soup.get_text(" ").split())
            return title, text[:10000]
    except Exception as e:
        log.warning("fetch_url_text failed for %s: %s", url, e)
        return None, None

async def collect_once():
    engine = get_engine()
    async with TelegramClient(StringSession(settings.TELETHON_SESSION), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        # Build dialog id map for private numeric channels
        idmap = {}
        async for d in client.iter_dialogs():
            ent = d.entity
            try:
                idmap[abs(getattr(ent, 'id', 0))] = ent
            except Exception:
                pass

        sources = [s.strip() for s in re.split(r"[\s,]+", settings.SRC_CHANNELS) if s.strip()]
        for src in sources:
            entity = src
            m = re.fullmatch(r"-?\d{6,}", src)
            if m:
                pos = abs(int(src))
                entity = idmap.get(pos, None)
                if entity is None:
                    log.error("Skip: private numeric channel not in dialogs (join first): %s", src)
                    continue

            try:
                log.info("Reading from %s", src)
                async for m in client.iter_messages(entity, limit=200):
                    text = (m.raw_text or "").strip()
                    url = None
                    murls = URL_RX.findall(text) if text else []
                    if murls:
                        url = murls[0]
                        t2, x2 = await fetch_url_text(url)
                        if (not text) or len(text) < 40:
                            text = ((t2 or "") + "\n" + (x2 or text)).strip()
                    if not text:
                        continue
                    h = sha256_of(str(src), str(m.id), text[:500], url or "")
                    with engine.begin() as conn:
                        try:
                            conn.execute(insert(messages).values(src=str(src), msg_id=str(m.id), url=url, title=None, content=text, summary_html=None, hash=h))
                        except Exception:
                            pass  # duplicate
            except FloodWaitError as fw:
                log.warning("FloodWait %s seconds on %s", fw.seconds, src)
                await asyncio.sleep(fw.seconds + 1)
            except Exception as e:
                log.exception("iter_messages failed for %s: %s", src, e)

if __name__ == "__main__":
    asyncio.run(collect_once())
