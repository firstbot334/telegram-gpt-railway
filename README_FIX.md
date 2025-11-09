# Debian-slim Dockerfile Fix Pack

This pack fixes Railway build failures such as `Unable to locate package` that are
caused by CRLF line endings and broken `apt-get install` formatting.

## What's inside
- **Dockerfile** — corrected (LF endings, clean apt install block)
- **.gitattributes** — enforces LF for Dockerfile / .sh / .py
- **.editorconfig** — optional, helps editors keep LF
- **fix_eol.sh** — normalizes CRLF→LF for tracked files (no extra deps)

## How to use
1. Drop these files into the **repo root** (replace existing `Dockerfile`).
2. Run once locally:
   ```bash
   chmod +x fix_eol.sh && ./fix_eol.sh
   git add -A && git commit -m "Apply Debian-slim Dockerfile fix + LF"
   git push
   ```
3. Railway → **Settings → Build**: ensure **Builder = Dockerfile**.
4. **Deploy**.

> Tip: Use `psycopg2-binary` (not `psycopg2`) in `requirements.txt` to avoid native builds.

Generated: 2025-11-09 07:37 UTC
