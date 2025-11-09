import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from .db import get_engine
from .models import news
from .config import settings
from .logging_setup import setup_logging
setup_logging()
log = logging.getLogger("prune")
def prune():
    with get_engine().begin() as conn:
        cutoff = datetime.now(timezone(timedelta(hours=9))) - timedelta(days=settings.MAX_DAYS_KEEP)
        res = conn.execute(delete(news).where(news.c.created_at < cutoff))
        log.info("pruned %s rows older than %s", res.rowcount, cutoff.isoformat())
if __name__ == "__main__":
    prune()
