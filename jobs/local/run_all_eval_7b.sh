#!/bin/bash
set -euo pipefail

echo "=================================="
echo "Start evaluation"
echo "Time: $(date)"
echo "=================================="

# ----------------------------
# Basic
# ----------------------------
echo "[1/4] Running basic_7b_eval"

python src/evaluation/run_evaluation.py \
  --patch_file outputs/basic_7b_patches.json \
  --input_file data/processed/input_real.json \
  --output basic_7b_eval \
  --max_workers 1 \
  --log_level INFO


# ----------------------------
# Feedback
# ----------------------------
echo "[2/4] Running feedback_7b_eval"

python src/evaluation/run_evaluation.py \
  --patch_file outputs/feedback_7b_patches.json \
  --input_file data/processed/input_real.json \
  --output feedback_7b_eval \
  --max_workers 1 \
  --log_level INFO


# ----------------------------
# Static Tool
# ----------------------------
echo "[3/4] Running static_tool_7b_eval"

python src/evaluation/run_evaluation.py \
  --patch_file outputs/static_tool_7b_patches.json \
  --input_file data/processed/input_real.json \
  --output static_tool_7b_eval \
  --max_workers 1 \
  --log_level INFO


# ----------------------------
# Dynamic Tool
# ----------------------------
echo "[4/4] Running dynamic_tool_7b_eval"

python src/evaluation/run_evaluation.py \
  --patch_file outputs/dynamic_tool_7b_patches.json \
  --input_file data/processed/input_real.json \
  --output dynamic_tool_7b_eval \
  --max_workers 1 \
  --log_level INFO


echo "=================================="
echo "Generating summary table"
echo "=================================="

python src/evaluation/summarize_eval_results.py \
  --methods \
  basic_7b_eval \
  feedback_7b_eval \
  static_tool_7b_eval \
  dynamic_tool_7b_eval \
  --output_csv outputs/eval_summary_7b.csv

echo "=================================="
echo "Finished!"
echo "Time: $(date)"
echo "=================================="