#!/usr/bin/env bash
# baize_posttrain_sft_surrogate.sh - Phase 2: MiniCPM5-2B surrogate SFT wrapper
# ⚠️ SURROGATE experiment - gains NOT transferable to BaiZe.
# Uses GPU 6-7 (2x A40 48GB) for full fine-tuning.
# Usage:
#   bash baize_posttrain_sft_surrogate.sh --dry-run
#   bash baize_posttrain_sft_surrogate.sh --smoke
#   bash baize_posttrain_sft_surrogate.sh
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$(realpath "${BASH_SOURCE[0]}")")" && pwd)"
PY="$HOME/code/verl_cu124_venv/bin/python"
MODEL="/nas_data/app.e0031982/models/MiniCPM5-2B"
DATA="$SCRIPT_DIR/sft_pyaether_corpus_v2.jsonl"
OUTPUT="/nas_data/app.e0031982/models/MiniCPM5-2B-SFT-surrogate"
GPU_IDS="6,7"
MAX_LEN=1024
BATCH=1
GRAD_ACCUM=16
LR=2e-5
EPOCHS=3.0
WARMUP=50
SAVE_STEPS=200
DRY_RUN=0
SMOKE=0
CLEAN_GPU=0
GPU_WAIT_TIMEOUT=120
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --smoke) SMOKE=1 ;;
    --gpu) GPU_IDS="$2"; shift ;;
    --output) OUTPUT="$2"; shift ;;
    --epochs) EPOCHS="$2"; shift ;;
    --lr) LR="$2"; shift ;;
    --max-len) MAX_LEN="$2"; shift ;;
    --save-steps) SAVE_STEPS="$2"; shift ;;
    --clean-gpu) CLEAN_GPU=1 ;;
    --gpu-wait-timeout) GPU_WAIT_TIMEOUT="$2"; shift ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--smoke] [--gpu 6,7] [--output DIR] [--epochs N]"
      echo "          [--lr F] [--max-len N] [--save-steps N] [--clean-gpu] [--gpu-wait-timeout S]"
      echo "  --clean-gpu          Kill stale processes on target GPUs before training (fix 1)"
      echo "  --gpu-wait-timeout S Wait up to S seconds for GPU VRAM to free (default 120, fix 4)"
      exit 0 ;;
    *) echo "Unknown: $1" ;;
  esac
  shift
done
echo "===== Phase 2: MiniCPM5-2B SURROGATE SFT ====="
echo "  model      : $MODEL"
echo "  data       : $DATA"
echo "  output     : $OUTPUT"
echo "  GPUs       : $GPU_IDS"
echo "  max_len    : $MAX_LEN"
echo "  batch      : ${BATCH} x grad_accum ${GRAD_ACCUM}"
echo "  lr         : $LR (cosine, warmup ${WARMUP})"
echo "  save_steps : $SAVE_STEPS (crash-resilient: wake194 crash@step95 lost all w/ save_steps=500)"
echo "  epochs     : $EPOCHS"
echo "  clean_gpu  : $CLEAN_GPU (fix1: kill stale procs)"
echo "  gpu_wait   : ${GPU_WAIT_TIMEOUT}s (fix4: wait VRAM<1GB)"
echo "  NCCL       : P2P_DISABLE=1 IB_DISABLE=1 (fix2: A40 no-NVLink)"
echo "  mode       : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))"
echo "  ⚠️ SURROGATE: gains NOT transferable to BaiZe"
echo "===== END RECIPE ====="
[ $DRY_RUN = 1 ] && { echo "[dry-run] Recipe printed, not executing."; exit 0; }

# --- Fix 1: Force-clean stale processes on target GPUs ---
if [ $CLEAN_GPU = 1 ]; then
  echo "[fix1] --clean-gpu: scanning target GPU(s) [$GPU_IDS] for stale processes..."
  I_OLD="$IFS"; IFS=','; read -ra GPU_ARR <<< "$GPU_IDS"; IFS="$I_OLD"
  STALE_FOUND=0
  for gi in "${GPU_ARR[@]}"; do
    PIDS=$(nvidia-smi --query-compute-apps=pid,gpu_uuid --format=csv,noheader 2>/dev/null)
    TARGET_UUID=$(nvidia-smi --query-gpu=index,uuid --format=csv,noheader 2>/dev/null | awk -F', ' -v g="$gi" '$1==g{print $2}')
    [ -z "$TARGET_UUID" ] && continue
    for line in $PIDS; do
      p=$(echo "$line" | awk -F',' '{print $1}' | xargs)
      u=$(echo "$line" | awk -F',' '{print $2}' | xargs)
      [ "$u" = "$TARGET_UUID" ] && {
        pname=$(ps -p "$p" -o args= 2>/dev/null | head -c 80)
        echo "  GPU $gi PID $p: $pname"
        echo "  -> kill -9 $p"
        kill -9 "$p" 2>/dev/null
        STALE_FOUND=1
      }
    done
  done
  [ $STALE_FOUND = 0 ] && echo "  No stale processes found." || echo "  Stale processes killed. Waiting for VRAM release..."
fi

# --- Fix 4: GPU idle wait loop (wait for VRAM <1GB on all target GPUs) ---
echo "[fix4] Waiting for GPU(s) [$GPU_IDS] VRAM <1GB (timeout=${GPU_WAIT_TIMEOUT}s)..."
WAITED=0
while [ $WAITED -lt $GPU_WAIT_TIMEOUT ]; do
  GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | \
    awk -F', ' -v gpus="$GPU_IDS" 'BEGIN{split(gpus,a,","); for(i in a) want[a[i]]=1} {gsub(/[^0-9]/,"",$2); if($2+0>1000 && want[$1]) print $1}' | tr '\n' ',' | sed 's/,$//')
  [ -z "$GPU_BUSY" ] && break
  [ $((WAITED % 10)) = 0 ] && echo "  ...GPU $GPU_BUSY still busy (waited ${WAITED}s)"
  sleep 5
  WAITED=$((WAITED + 5))
done
if [ -n "$GPU_BUSY" ]; then
  echo "ERROR: GPU $GPU_BUSY still busy (>1GB) after ${GPU_WAIT_TIMEOUT}s. Aborting."
  echo "  Hint: pass --clean-gpu to kill stale processes, or --gpu-wait-timeout to extend wait."
  exit 1
fi
echo "  GPU(s) [$GPU_IDS] idle (<1GB VRAM). Proceeding."

[ -f "$MODEL/config.json" ] || { echo "ERROR: Model not found: $MODEL"; exit 1; }
[ -f "$DATA" ] || { echo "ERROR: Data not found: $DATA"; exit 1; }

# --- Environment (fix 2: NCCL for A40 no-NVLink DDP) ---
export HF_HOME="/tmp/hf_home"
export HF_MODULES_CACHE="/tmp/hf_home/modules"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TOKENIZERS_PARALLELISM=false
export NCCL_P2P_DISABLE=1        # fix2: A40 has no NVLink, P2P can hang DDP init
export NCCL_IB_DISABLE=1         # A40 consumer GPUs: no IB, avoid NET fallback
export NCCL_DEBUG=WARN
SMOKE_FLAG=""
[ $SMOKE = 1 ] && SMOKE_FLAG="--smoke"
export CUDA_VISIBLE_DEVICES="$GPU_IDS"
echo "Launching with accelerate (num_processes=$(echo $GPU_IDS | tr ',' '\n' | wc -l))..."
"$PY" -m accelerate.commands.launch \
    --num_processes "$(echo $GPU_IDS | tr ',' '\n' | wc -l)" \
    "$SCRIPT_DIR/baize_posttrain_sft_surrogate.py" \
    --model_path "$MODEL" \
    --data_path "$DATA" \
    --output_dir "$OUTPUT" \
    --max_len "$MAX_LEN" \
    --per_device_batch_size "$BATCH" \
    --grad_accum "$GRAD_ACCUM" \
    --lr "$LR" \
    --warmup_steps "$WARMUP" \
    --num_epochs "$EPOCHS" \
    --save_steps "$SAVE_STEPS" \
    $SMOKE_FLAG
RC=$?
echo "===== SFT COMPLETE rc=$RC ====="
exit $RC
