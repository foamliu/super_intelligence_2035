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
OUTPUT="/tmp/sft_surrogate_out"
GPU_IDS="6,7"
MAX_LEN=2048
BATCH=1
GRAD_ACCUM=16
LR=2e-5
EPOCHS=3.0
WARMUP=50
SAVE_STEPS=500
DRY_RUN=0
SMOKE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --smoke) SMOKE=1 ;;
    --gpu) GPU_IDS="$2"; shift ;;
    --output) OUTPUT="$2"; shift ;;
    --epochs) EPOCHS="$2"; shift ;;
    --lr) LR="$2"; shift ;;
    --max-len) MAX_LEN="$2"; shift ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--smoke] [--gpu 6,7] [--output DIR] [--epochs N] [--lr F] [--max-len N]"
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
echo "  epochs     : $EPOCHS"
echo "  mode       : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))"
echo "  ⚠️ SURROGATE: gains NOT transferable to BaiZe"
echo "===== END RECIPE ====="
[ $DRY_RUN = 1 ] && { echo "[dry-run] Recipe printed, not executing."; exit 0; }
# Check GPU availability
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' -v gpus="$GPU_IDS" 'BEGIN{split(gpus,a,","); for(i in a) want[a[i]]=1} {gsub(/[^0-9]/,"",$2); if($2+0>1000 && want[$1]) print $1}')
[ -n "$GPU_BUSY" ] && { echo "ERROR: GPU $GPU_BUSY busy (>1GB used). Aborting."; exit 1; }
[ -f "$MODEL/config.json" ] || { echo "ERROR: Model not found: $MODEL"; exit 1; }
[ -f "$DATA" ] || { echo "ERROR: Data not found: $DATA"; exit 1; }
export HF_HOME="/tmp/hf_home"
export HF_MODULES_CACHE="/tmp/hf_home/modules"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TOKENIZERS_PARALLELISM=false
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
