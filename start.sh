#!/usr/bin/env bash
set -euo pipefail
echo "[start.sh] Python: $(python -V)"
echo "[start.sh] TZ: ${TZ:-UTC}"
python -u src/fix_schema.py || true
echo "[start.sh] Launching collector loop..."
exec python -u src/run_loop.py
