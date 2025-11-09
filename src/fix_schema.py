from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.exc import ProgrammingError, OperationalError
from .config import settings
from .models import metadata, messages
from .db import get_engine
import logging
from .logging_setup import setup_logging

setup_logging()
log = logging.getLogger("fix_schema")

def ensure_tables():
    engine = get_engine()
    with engine.begin() as conn:
        try:
            metadata.create_all(conn)
            log.info("Schema ensured/created.")
        except (ProgrammingError, OperationalError) as e:
            log.exception("Schema creation failed: %s", e)
            raise

if __name__ == "__main__":
    ensure_tables()
