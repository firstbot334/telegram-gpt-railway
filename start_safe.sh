#!/usr/bin/env bash
set -euo pipefail
echo "[start_safe] Python: $(python -V)"
echo "[start_safe] TZ: ${TZ:-UTC}"
python -u src/fix_schema.py || true
python -u src/validate_session.py || true
exec python -u src/run_all.py
