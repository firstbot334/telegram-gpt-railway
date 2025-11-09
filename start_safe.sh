#!/usr/bin/env bash
set -euo pipefail
echo "[start_safe] Python: $(python -V)"
echo "[start_safe] PIP:     $(pip -V)"
echo "[start_safe] TZ:      ${TZ:-UTC}"

# Check private channels access; allow numeric -100... if joined or invite available
python -u src/check_access.py

# Schema auto-fix (idempotent)
python -u src/fix_schema.py || true

# Validate Telethon session (non-fatal)
python -u src/validate_session.py || true

# Run orchestrator
exec python -u src/run_all.py
