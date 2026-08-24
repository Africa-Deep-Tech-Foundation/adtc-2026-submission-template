#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$TARGET/vector_afya" "$TARGET/tests"
cp "$SCRIPT_DIR/vector_afya/"*.py "$TARGET/vector_afya/"
cp "$SCRIPT_DIR/tests/test_vector_afya.py" "$TARGET/tests/"
cp "$SCRIPT_DIR/ARCHITECTURE.md" "$TARGET/"
cp "$SCRIPT_DIR/README_VECTOR_AFYA.md" "$TARGET/"
cp "$SCRIPT_DIR/metadata.json" "$TARGET/"
cp "$SCRIPT_DIR/download_model.sh" "$TARGET/"
chmod +x "$TARGET/download_model.sh"
echo "VECTOR Afya MVP files applied to: $TARGET"
