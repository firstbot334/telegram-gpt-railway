#!/usr/bin/env bash
set -x
echo "PATH=$PATH"
which python || true
which python3 || true
python --version || true
python3 --version || true
ls -la /app || true
ls -la /app/.venv/bin || true
