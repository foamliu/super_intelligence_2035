#!/usr/bin/env bash
# Launch script for Stage-1W SFT training (Phase 1 wave RL).
# SAFELY waits for GPU to be truly free before starting.
#
# Safety guard (vision wake#612): a running job may briefly dip GPU util
# during checkpointing while still holding VRAM.  We require BOTH:
#   (a) utilization.gpu  < 10  for all first-N GPUs, AND
#   (b) memory.used      < 5000 MiB for all first-N GPUs (job released VRAM)
# sustained for CONSECUTIVE_IDLE consecutive checks (60s apart) before we
# start.  This prevents grabbing GPUs during a checkpoint pause and OOM-ing
# the healthy pretrain/vision training that must not be killed.
#
# Usage:
#   bash run_sft_wave.sh [n_gpus]
#   bash run_sft_wave.sh 8        # 8 GPUs (default)
#   bash run_sft_wave.sh 1        # 1 GPU (slower but works)

set -euo pipefail

N_GPUS="${1:-8}"
CONSECUTIVE_IDLE=3
IDLE_POLL_INTERVAL=60
UTIL_THRESHOLD=10
MEM_THRESHOLD=5000

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VISION_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sft_train_$(date +%Y%m%d_%H%M%S).log"
POLL_LOG="$LOG_DIR/sft_poll_$(date +%Y%m%d_%H%M%S).log"

echo "=== Stage-1W SFT Launch (safe GPU-wait) ===" | tee "$POLL_LOG"
echo "  GPUs: $N_GPUS" | tee -a "$POLL_LOG"
echo "  Script: $SCRIPT_DIR/sft_train_wave.py" | tee -a "$POLL_LOG"
echo "  Train log: $LOG_FILE" | tee -a "$POLL_LOG"
echo "  Poll log: $POLL_LOG" | tee -a "$POLL_LOG"
echo "  Guard: util<${UTIL_THRESHOLD}% AND mem<${MEM_THRESHOLD}MiB, ${CONSECUTIVE_IDLE}x consecutive @ ${IDLE_POLL_INTERVAL}s" | tee -a "$POLL_LOG"
echo "  Started polling: $(date)" | tee -a "$POLL_LOG"

gpu_is_idle() {
  # Disable pipefail locally: when awk exits early, nvidia-smi may get
  # SIGPIPE (exit 141), which under `set -o pipefail` would kill the script.
  set +o pipefail
  local out
  out=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits 2>/dev/null | \
    awk -v n="$N_GPUS" -v ut="$UTIL_THRESHOLD" -v mt="$MEM_THRESHOLD" '
      BEGIN { idle=1 }
      NR<=n {
        if ($1+0 >= ut) { idle=0; print "busy_util"; exit }
        if ($2+0 >= mt) { idle=0; print "busy_mem"; exit }
      }
      END { if (idle) print "idle" }
    ' 2>/dev/null) || true
  set -o pipefail
  printf '%s' "$out"
}

idle_count=0
while true; do
  status="$(gpu_is_idle)"
  ts="$(date +%H:%M:%S)"
  if [ "$status" = "idle" ]; then
    idle_count=$((idle_count + 1))
    echo "[$ts] idle ($idle_count/$CONSECUTIVE_IDLE)" | tee -a "$POLL_LOG"
    if [ "$idle_count" -ge "$CONSECUTIVE_IDLE" ]; then
      echo "[$ts] GPU confirmed free (sustained ${CONSECUTIVE_IDLE}x). Starting training." | tee -a "$POLL_LOG"
      break
    fi
  else
    if [ "$idle_count" -gt 0 ]; then
      echo "[$ts] $status -- resetting idle counter (was $idle_count)" | tee -a "$POLL_LOG"
    else
      echo "[$ts] $status -- waiting" | tee -a "$POLL_LOG"
    fi
    idle_count=0
  fi
  sleep "$IDLE_POLL_INTERVAL"
done

cd "$VISION_DIR"
echo "[$(date +%H:%M:%S)] Launching SFT training now." | tee -a "$POLL_LOG"
if [ "$N_GPUS" -gt 1 ]; then
  torchrun --nproc_per_node="$N_GPUS" wave_rl/sft_train_wave.py 2>&1 | tee "$LOG_FILE"
else
  CUDA_VISIBLE_DEVICES=0 python wave_rl/sft_train_wave.py 2>&1 | tee "$LOG_FILE"
fi

echo "=== Training finished: $(date) ===" | tee -a "$POLL_LOG"
echo "  Train log: $LOG_FILE" | tee -a "$POLL_LOG"
