import time, logging
from datetime import datetime
from dateutil.tz import gettz
from telegram import Bot
from .config import settings
from .logging_setup import setup_logging
from .collector_telethon import collect_once
from .summarizer_poster import run_summarize
from .weekly_digest import run_digest

setup_logging()
log = logging.getLogger("run_all")

def should_send_digest(now):
    # Monday 09:00 KST +- 5 minutes window; run once per hour safely.
    kst = gettz("Asia/Seoul")
    now_kst = now.astimezone(kst)
    return now_kst.weekday()==0 and now_kst.hour==settings.DIGEST_HOUR_KST

def main_loop():
    bot = Bot(token=settings.DEST_BOT_TOKEN) if settings.DEST_BOT_TOKEN else None
    interval = max(0, settings.RUN_INTERVAL_MIN)
    while True:
        log.info("Cycle start")
        try:
            import asyncio
            asyncio.run(collect_once())
        except Exception as e:
            log.exception("collector error: %s", e)

        try:
            run_summarize()
        except Exception as e:
            log.exception("summarizer error: %s", e)

        now = datetime.utcnow()
        if bot and should_send_digest(now):
            try:
                run_digest(bot)
                log.info("Weekly digest sent.")
            except Exception as e:
                log.exception("digest error: %s", e)

        if interval == 0:
            log.info("RUN_INTERVAL_MIN=0 → single run mode. exiting.")
            break
        log.info("Sleep %s min", interval)
        time.sleep(interval*60)

if __name__ == "__main__":
    main_loop()
