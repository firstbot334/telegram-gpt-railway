#!/usr/bin/env bash
set -euo pipefail
echo "[start] Python: $(python -V)"
echo "[start] TZ: ${TZ:-UTC}"
python -u src/fix_schema.py || true
exec python -u src/run_loop.py
