import time, logging, asyncio
from datetime import datetime
from dateutil.tz import gettz
from telegram import Bot
from .config import settings
from .logging_setup import setup_logging
from .collector_telethon import collect_once
from .summarizer_poster import run as run_summary
from .weekly_digest import run as run_digest
setup_logging(); log = logging.getLogger('run_all')

def should_send_digest(now):
    kst=gettz('Asia/Seoul'); t=now.astimezone(kst); return t.weekday()==0 and t.hour==settings.DIGEST_HOUR_KST

def main_loop():
    bot = Bot(token=settings.DEST_BOT_TOKEN) if settings.DEST_BOT_TOKEN else None
    interval=max(0, settings.RUN_INTERVAL_MIN)
    while True:
        log.info('=== RUN: collector_telethon ===')
        try: asyncio.run(collect_once())
        except Exception as e: log.exception('collector error: %s', e)
        log.info('=== RUN: summarizer ===')
        try: run_summary()
        except Exception as e: log.exception('summary error: %s', e)
        now=datetime.utcnow()
        if bot and should_send_digest(now):
            log.info('=== RUN: weekly_digest ===')
            try: run_digest(bot)
            except Exception as e: log.exception('digest error: %s', e)
        if interval==0:
            log.info('RUN_INTERVAL_MIN=0 -> exit'); break
        log.info('sleep %s min', interval); time.sleep(interval*60)

if __name__=='__main__': main_loop()
