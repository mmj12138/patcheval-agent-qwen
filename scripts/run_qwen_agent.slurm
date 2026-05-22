#!/bin/bash
#SBATCH --job-name=qwen-patcheval-agent
#SBATCH --output=logs/qwen_agent_%j.out
#SBATCH --error=logs/qwen_agent_%j.err

#SBATCH --account=gratis
#SBATCH --partition=gpu
#SBATCH --qos=job_gratis
#SBATCH --gres=gpu:rtx4090:1

#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -e

echo "Job started on $(hostname)"
echo "Start time: $(date)"

# 进入你的工程目录
cd $HOME/patcheval-agent-qwen

# 创建日志目录
mkdir -p logs
mkdir -p outputs

# 加载 Python
module load Python/3.10.8

# 创建/激活虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

source venv/bin/activate

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 可选：设置 HuggingFace 缓存目录，避免占用 home
export HF_HOME=$SCRATCH/huggingface
export TRANSFORMERS_CACHE=$SCRATCH/huggingface
mkdir -p $HF_HOME

# 检查 GPU
python - <<'PY'
import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
PY

# 运行 agent 生成 patch
export MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
bash scripts/run.sh

echo "Output saved to outputs/patches.json"
echo "Job finished at $(date)"