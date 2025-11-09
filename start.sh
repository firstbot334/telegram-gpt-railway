#!/usr/bin/env bash
set -euo pipefail
echo "[start.sh] Python: $(python -V)"
echo "[start.sh] TZ: ${TZ:-UTC}"
echo "[start.sh] Running schema check/auto-fix"
python -u src/fix_schema.py || true
echo "[start.sh] Launching collector loop..."
exec python -u src/run_loop.py
