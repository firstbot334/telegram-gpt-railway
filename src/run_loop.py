import time, logging, asyncio
from .config import settings
from .collector import collect_once
from .prune import prune

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("loop")

def main():
    interval = max(1, settings.RUN_INTERVAL_MIN)
    while True:
        log.info("=== RUN: collector ===")
        try:
            asyncio.run(collect_once())
        except Exception as e:
            log.exception("collector error: %s", e)

        log.info("=== RUN: prune ===")
        try:
            prune()
        except Exception as e:
            log.exception("prune error: %s", e)

        log.info("sleep %s min", interval)
        time.sleep(interval * 60)

if __name__ == "__main__":
    main()
