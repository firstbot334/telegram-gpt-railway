
# Telegram News Collector & Summarizer (Fixed)
## Quick Setup
1. **Env Vars (must)**  
   - `OPENAI_API_KEY`
   - `TELEGRAM_TOKEN` (or `TELEGRAM_BOT_TOKEN`)
   - `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELETHON_SESSION` (Telethon user session)
   - `DATABASE_URL` (Postgres; sslmode added automatically if missing)
   - `SUMMARY_CHANNEL` (e.g. -1001234 or @channel)
   - `NEWS_SOURCES` (comma-separated: @ch1,@ch2 or numeric IDs)
   - Optional: `INTEREST_KEYWORDS`, `STANCE_MODEL` (default: gpt-4o-mini), `BACKFILL_DAYS` (default: 2)

2. **Create tables (one time)**
   ```py
   from db import create_tables
   create_tables()
   ```

3. **Run**
   - Collector (continuous): `python collector_telethon.py`
   - Summary: `python summarize_news.py --window day` (or `night`)
   - Event pin update: `python event_updater.py`

## Notes
- HTML parse issues are auto-fallback to plaintext.
- Missing legacy env names are mapped to the new ones.
