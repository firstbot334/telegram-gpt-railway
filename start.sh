#!/usr/bin/env bash
set -euo pipefail

echo "[start.sh] Python: $(python -V)"
echo "[start.sh] PIP:     $(pip -V)"
echo "[start.sh] TZ:       ${TZ:-UTC}"

# Optional: set timezone inside container (if present)
if [ -n "${TZ:-}" ] && [ -f "/usr/share/zoneinfo/$TZ" ]; then
  ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime || true
fi

echo "[start.sh] Running schema check/auto-fix (idempotent)"
python -u fix_schema.py || python -u check_schema.py || true

echo "[start.sh] Validating Telegram session (idempotent)"
# This only checks credentials; won't block if not interactive
python -u validate_session.py || true

echo "[start.sh] Launching main loop"
exec python -u run_all.py
