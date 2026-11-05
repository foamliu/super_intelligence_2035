#!/usr/bin/env bash
# Launch script for Stage-1W SFT training (Phase 1 wave RL).
# Waits for GPU to be free (all GPUs < 10% util) before starting.
#
# Usage:
#   bash run_sft_wave.sh [n_gpus]
#   bash run_sft_wave.sh 8        # 8 GPUs (default)
#   bash run_sft_wave.sh 1        # 1 GPU (slower but works)

set -euo pipefail

N_GPUS="${1:-8}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VISION_DIR="$(dirname "$$SCRIPT_DIR")"
LOG_DIR="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sft_train_$(date +%Y%m%d_%H%M%S).log"

echo "=== Stage-1W SFT Launch ==="
echo "  GPUs: $N_GPUS"
echo "  Script: $SCRIPT_DIR/sft_train_wave.py"
echo "  Log: $LOG_FILE"
echo "  Started: $(date)"

# Wait for GPU to be free (all GPUs < 10% util)
wait_gpu() {
  echo "[$(date +%H:%M:%S)] Waiting for GPU to be free..."
  while true; do
    BUSY=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | \
           awk -v n="$N_GPUS" 'NR<=n {if ($1 > 10) print "busy"}' | head -1)
    if [ -z "$$BUSY" ]; then
      echo "[$(date +%H:%M:%S)] GPU is free! Starting training."
      break
    fi
    echo "[$(date +%H:%M:%S)] GPU busy (some GPU > 10% util). Waiting 300s..."
    sleep 300
  done
}

wait_gpu

cd "$VISION_DIR"
if [ "$N_GPUS" -gt 1 ]; then
  torchrun --nproc_per_node="$N_GPUS" wave_rl/sft_train_wave.py 2>&1 | tee "$LOG_FILE"
else
  CUDA_VISIBLE_DEVICES=0 python wave_rl/sft_train_wave.py 2>&1 | tee "$LOG_FILE"
fi

echo "=== Training finished: $(date) ==="
echo "  Log: $LOG_FILE"
