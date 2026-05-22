#!/bin/bash
#SBATCH --job-name=smoke_all_settings
#SBATCH --output=outputs/logs/%x_%j.out
#SBATCH --error=outputs/logs/%x_%j.err

#SBATCH --account=gratis
#SBATCH --partition=gpu
#SBATCH --qos=job_gratis
#SBATCH --gres=gpu:rtx4090:1

#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

set -euo pipefail

cd "$HOME/patcheval-agent-qwen"

mkdir -p outputs/logs

module purge
module load Python/3.10

source "$HOME/venvs/myddlenv/bin/activate"

echo "Running on node: $(hostname)"
echo "Python: $(which python)"
echo "Start time: $(date)"

export MODEL_NAME="Qwen/Qwen2.5-Coder-7B-Instruct"
export MAX_NEW_TOKENS=1024
export INPUT_FILE="data/processed/input_real.json"

bash jobs/local/run_smoke_all_settings.sh

echo "Finished time: $(date)"