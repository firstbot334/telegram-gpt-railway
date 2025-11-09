import logging
from .db import get_engine
from .models import metadata
from .logging_setup import setup_logging
setup_logging()
log = logging.getLogger("fix_schema")
def main():
    engine = get_engine()
    with engine.begin() as conn:
        metadata.create_all(conn)
        log.info("✅ schema ensured")
if __name__ == "__main__":
    main()
