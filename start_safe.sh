#!/usr/bin/env bash
set -euo pipefail

echo "[start_safe] Python: $(python -V)"
echo "[start_safe] PIP:     $(pip -V)"
echo "[start_safe] TZ:      ${TZ:-UTC}"

# Validate channels first to avoid Telethon entity errors
python -u src/utils.py --validate-sources || { echo "[start_safe] Invalid SRC_CHANNELS"; exit 1; }

# Auto-fix schema before run (idempotent)
python -u src/fix_schema.py || true

# Optional: validate Telegram session (won't fail the run)
python -u src/validate_session.py || true

exec python -u src/run_all.py
