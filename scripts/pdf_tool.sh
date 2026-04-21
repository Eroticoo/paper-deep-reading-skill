#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/pdf_tool.py" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT_DIR/pdf_tool.py" "$@"
fi

if command -v swift >/dev/null 2>&1; then
  CACHE_ROOT="${TMPDIR:-/tmp}"
  CACHE_DIR="${CACHE_ROOT%/}/codex-swift-cache"
  mkdir -p "$CACHE_DIR"
  exec swift -module-cache-path "$CACHE_DIR" "$SCRIPT_DIR/pdf_snapshot.swift" "$@"
fi

echo "missing_runtime=python_or_swift" >&2
exit 1
