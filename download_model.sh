#!/usr/bin/env bash
# Download your model weight file.
#
# Rules:
#   - Must be idempotent (safe to run multiple times).
#   - Must download without any credentials (public URL only).
#   - The output path must match `_runtime.model_path` in metadata.json.
#   - MODEL_URL must point to an exact, immutable file — pin it to a specific
#     commit/release, never a mutable branch like "main". On Hugging Face,
#     replace "main" in the URL with the exact commit SHA from your repo's
#     file history so the file you submitted can never silently change.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HERE/model"

# ⚠️ Edit ONLY the two values below (MODEL_FILE, MODEL_URL). Do not change
# anything else in this file — see "download_model.sh" in README.md for what
# the evaluator requires.
MODEL_FILE="$MODEL_DIR/[YOUR_MODEL_FILE_NAME].gguf"
MODEL_URL="[YOUR_MODEL_URL]"

mkdir -p "$MODEL_DIR"

if [[ -f "$MODEL_FILE" ]]; then
  echo "model already present at $MODEL_FILE — skipping download"
  exit 0
fi

echo "downloading $MODEL_URL → ${MODEL_FILE}…"

if command -v curl > /dev/null 2>&1; then
  curl -L --fail --progress-bar -o "$MODEL_FILE.partial" "$MODEL_URL"
elif command -v wget > /dev/null 2>&1; then
  wget --show-progress -O "$MODEL_FILE.partial" "$MODEL_URL"
else
  echo "error: neither curl nor wget found" >&2
  exit 1
fi

mv "$MODEL_FILE.partial" "$MODEL_FILE"
echo "done: $MODEL_FILE"
