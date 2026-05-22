#!/bin/bash
#python src/pipeline.py
#python3 -m venv venv
#source venv/bin/activate
#
#pip install -r requirements.txt
#pip install torch

python scripts/prepare_data.py \
  --input data/raw/PatchEval/patcheval/datasets/input.json \
  --output data/processed/input_real.json \
  --num 1000 \
  --language Python
#
#python -m scripts.filter_input_by_images \
#  --input data/raw/PatchEval/patcheval/datasets/input.json \
#  --images images.txt \
#  --output data/processed/input_docker.json \
#  --num 10
#
#python -m src.pipeline --agent basic
#
#python -m scripts.evaluate_light \
#  --input data/processed/input_real.json \
#  --pred outputs/basic_patches.json
#
#python -m scripts.evaluate_light \
#  --input data/processed/input_real.json \
#  --pred outputs/feedback_patches.json
#
#python -m scripts.evaluate_light \
#  --input data/processed/input_real.json \
#  --pred outputs/cwe_tool_patches.json
#
#python -m scripts.evaluate_light \
#  --input data/processed/input_real.json \
#  --pred outputs/dynamic_tool_patches.json
#
#python src/evaluation/run_evaluation.py \
#  --output feedback_eval \
#  --patch_file outputs/basic_docker_patches.json \
#  --input_file data/processed/input_real.json \
#  --log_level DEBUG