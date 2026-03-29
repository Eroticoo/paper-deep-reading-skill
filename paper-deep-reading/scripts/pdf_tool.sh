#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_ROOT="${TMPDIR:-/tmp}"
CACHE_DIR="${CACHE_ROOT%/}/codex-swift-cache"

mkdir -p "$CACHE_DIR"
exec swift -module-cache-path "$CACHE_DIR" "$SCRIPT_DIR/pdf_snapshot.swift" "$@"
