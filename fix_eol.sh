#!/usr/bin/env bash
set -euo pipefail
# Convert CRLF to LF for common file types
files=$(git ls-files | grep -E '\.(Dockerfile|sh|py|txt|toml|yml|yaml)$' || true)
if [ -z "$files" ]; then
  echo "No matching files. Exiting."
  exit 0
fi
# Use sed to strip CR on macOS/Linux without dos2unix
for f in $files; do
  printf 'Fixing EOL -> %s\n' "$f"
  sed -i 's/\r$//' "$f"
done
echo "Done. Commit the changes:"
echo "  git add -A && git commit -m 'Normalize LF line endings'"
