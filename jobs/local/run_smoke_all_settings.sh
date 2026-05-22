#!/bin/bash
set -euo pipefail

mkdir -p outputs
mkdir -p outputs/logs

export MODEL_NAME="${MODEL_NAME:-Qwen/Qwen2.5-Coder-7B-Instruct}"
export MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-1024}"

INPUT_FILE="${INPUT_FILE:-data/processed/input_real.json}"

echo "MODEL_NAME=${MODEL_NAME}"
echo "MAX_NEW_TOKENS=${MAX_NEW_TOKENS}"
echo "INPUT_FILE=${INPUT_FILE}"

echo "===== BASIC ====="
python -m src.pipeline \
  --agent basic \
  --input "${INPUT_FILE}" \
  --output outputs/basic_7b_patches.json

echo "===== FEEDBACK ====="
python -m src.pipeline \
  --agent feedback \
  --input "${INPUT_FILE}" \
  --output outputs/feedback_7b_patches.json

echo "===== STATIC TOOL ====="
python -m src.pipeline \
  --agent static_tool \
  --input "${INPUT_FILE}" \
  --output outputs/static_tool_7b_patches.json

echo "===== DYNAMIC TOOL ====="
python -m src.pipeline \
  --agent dynamic_tool \
  --input "${INPUT_FILE}" \
  --output outputs/dynamic_tool_7b_patches.json

echo "All experiments finished."