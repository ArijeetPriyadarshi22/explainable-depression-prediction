#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_DIR="$SCRIPT_DIR/exports"
mkdir -p "$EXPORT_DIR"

if command -v mmdc >/dev/null 2>&1; then
  MMDC=(mmdc)
elif command -v npm >/dev/null 2>&1; then
  MMDC=(npm exec --package @mermaid-js/mermaid-cli -- mmdc)
elif command -v npx >/dev/null 2>&1; then
  MMDC=(npx --package @mermaid-js/mermaid-cli mmdc)
else
  echo "Mermaid CLI not found. Install mmdc, npm, or npx." >&2
  exit 1
fi

for file in "$SCRIPT_DIR"/*.mmd; do
  base="$(basename "$file" .mmd)"
  "${MMDC[@]}" -i "$file" -o "$EXPORT_DIR/$base.svg" -b white
  echo "wrote $EXPORT_DIR/$base.svg"
done
