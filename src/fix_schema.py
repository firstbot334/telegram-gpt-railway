import logging
from .db import get_engine
from .models import metadata
from .logging_setup import setup_logging
setup_logging()
log = logging.getLogger("schema")
with get_engine().begin() as conn:
    metadata.create_all(conn)
    log.info("✅ schema ensured (news)")
