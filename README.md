# Railway Full Replacement (URL-only Collector)
- Only t.me URLs in `SRC_CHANNELS` (no numeric -100 IDs)
- Collector-only loop; no summary/stats
- Keyword-filtered text + URL saved
- Auto-prunes old rows

## Env (Railway)
```
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELETHON_SESSION=...
SRC_CHANNELS="https://t.me/nje2e https://t.me/bbbbbworld https://t.me/repeatandrepeat https://t.me/SmallCap https://t.me/anna7673 https://t.me/EvAtZchuno"
KEYWORDS="배터리,전해액,NVDA,TSMC"
DATABASE_URL="sqlite:///./newsbot.db"
RUN_INTERVAL_MIN=30
MAX_DAYS_KEEP=60
```

## Logs should look like
```
[start.sh] Running schema check/auto-fix
[start.sh] Launching collector loop...
=== RUN: collector ===
reading https://t.me/...
=== RUN: prune ===
sleep 30 min
```

Generated: 2025-11-09 10:48 UTC
