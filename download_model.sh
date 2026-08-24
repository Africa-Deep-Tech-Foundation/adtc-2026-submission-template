#!/usr/bin/env bash
# Download the exact public Qwen2.5-3B-Instruct Q4_K_M model used by VECTOR Afya.
# The script is idempotent and verifies the expected SHA-256 before replacing the file.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HERE/model"
MODEL_FILE="$MODEL_DIR/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
EXPECTED_SHA256="626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"

mkdir -p "$MODEL_DIR"

if [[ -f "$MODEL_FILE" ]]; then
  ACTUAL="$(sha256sum "$MODEL_FILE" | awk '{print $1}')"
  if [[ "$ACTUAL" == "$EXPECTED_SHA256" ]]; then
    echo "model already present and checksum verified: $MODEL_FILE"
    exit 0
  fi
  echo "existing model checksum mismatch; downloading a fresh copy" >&2
fi

PARTIAL="$MODEL_FILE.partial"
echo "downloading Qwen2.5-3B-Instruct Q4_K_M (~2.1 GB)…"
if command -v curl >/dev/null 2>&1; then
  curl -L --fail --progress-bar -o "$PARTIAL" "$MODEL_URL"
elif command -v wget >/dev/null 2>&1; then
  wget --show-progress -O "$PARTIAL" "$MODEL_URL"
else
  echo "error: neither curl nor wget found" >&2
  exit 1
fi

ACTUAL="$(sha256sum "$PARTIAL" | awk '{print $1}')"
if [[ "$ACTUAL" != "$EXPECTED_SHA256" ]]; then
  rm -f "$PARTIAL"
  echo "error: SHA-256 mismatch" >&2
  echo "expected: $EXPECTED_SHA256" >&2
  echo "actual:   $ACTUAL" >&2
  exit 1
fi

mv "$PARTIAL" "$MODEL_FILE"
echo "done: $MODEL_FILE"
