#!/usr/bin/env bash
set -euo pipefail
python -u src/fix_schema.py || true
exec python -u src/run_all.py
