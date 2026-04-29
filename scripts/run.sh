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
  --num 5 \
  --language Python

python -m src.pipeline