#!/bin/bash
# baize_posttrain_sft_pretok.sh — SFT training with pre-tokenized data
# Uses PreTokenizedSFTDataset (custom_cls) to bypass slow MultiTurnSFTDataset
#
# Usage: bash baize_posttrain_sft_pretok.sh --gpus 6,7 --max-length 2048 --epochs 3
set -euo pipefail

# Defaults
GPUS="6,7"
MAX_LENGTH=2048
EPOCHS=3
LR=1e-5
TRAIN_BATCH=64
MICRO_BATCH=4
SAVE_FREQ=20
RUN_NAME="minicpm5_agentic_v39_pretok"
SEED=42

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gpus) GPUS="$2"; shift 2 ;;
    --max-length) MAX_LENGTH="$2"; shift 2 ;;
    --epochs) EPOCHS="$2"; shift 2 ;;
    --lr) LR="$2"; shift 2 ;;
    --train-batch) TRAIN_BATCH="$2"; shift 2 ;;
    --micro-batch) MICRO_BATCH="$2"; shift 2 ;;
    --save-freq) SAVE_FREQ="$2"; shift 2 ;;
    --run-name) RUN_NAME="$2"; shift 2 ;;
    --seed) SEED="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

NGPU=$(echo "$GPUS" | tr ',' '\n' | wc -l)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/sft_surrogate_data/minicpm5_agentic_v39_pretok"
OUTPUT_DIR="${SCRIPT_DIR}/sft_surrogate_runs/${RUN_NAME}"
HYDRA_DIR="/tmp/baize_sft_pretok_hydra"
LOG_FILE="/tmp/baize_sft_pretok_${RUN_NAME}.log"
DATASET_CLS="${SCRIPT_DIR}/baize_posttrain_pretokenized_dataset.py"
MODEL_PATH="/nas_data/app.e0031982/models/MiniCPM5-2B"

# Guard: check GPUs are free
for gi in $(echo "$GPUS" | tr ',' ' '); do
  MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$gi" 2>/dev/null | tr -d ' ')
  if [[ "$MEM" -gt 1000 ]]; then
    echo "[guard] GPU $gi has ${MEM} MiB used — aborting"
    exit 1
  fi
done
echo "[guard] GPUs $GPUS all free OK"

mkdir -p "$OUTPUT_DIR" "$HYDRA_DIR"

export CUDA_VISIBLE_DEVICES="$GPUS"
export HF_HOME="/tmp/hf_home"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
export TOKENIZERS_PARALLELISM=true
export WANDB_MODE=disabled
export HYDRA_FULL_ERROR=1

echo ""
echo "===== PreTokenized SFT START @ $(date '+%F %T') ====="
echo "  GPUs: $GPUS ($NGPU x A40)"
echo "  data: $DATA_DIR"
echo "  model: $MODEL_PATH"
echo "  max_length: $MAX_LENGTH, batch: $TRAIN_BATCH, micro: $MICRO_BATCH"
echo "  epochs: $EPOCHS, lr: $LR, save_freq: $SAVE_FREQ"
echo "  output: $OUTPUT_DIR"
echo "  log: $LOG_FILE"
echo ""

VERL_PYTHON="/home/app.e0031982/code/verl_cu124_venv/bin/python3"
VERL_TORCHRUN="/home/app.e0031982/code/verl_cu124_venv/bin/torchrun"

"$VERL_TORCHRUN" --nproc_per_node="$NGPU" --master_addr=127.0.0.1 --master_port=29832 \
  -m verl.trainer.fsdp_sft_trainer \
  --config-name sft_trainer \
  data.train_files="${DATA_DIR}/sft_surrogate_train.parquet" \
  data.val_files="${DATA_DIR}/sft_surrogate_val.parquet" \
  data.train_batch_size="$TRAIN_BATCH" \
  data.micro_batch_size_per_gpu="$MICRO_BATCH" \
  data.max_length="$MAX_LENGTH" \
  data.truncation=right \
  data.multiturn.enable=false \
  data.custom_cls.path="$DATASET_CLS" \
  data.custom_cls.name=PreTokenizedSFTDataset \
  model.partial_pretrain="$MODEL_PATH" \
  model.trust_remote_code=true \
  model.enable_gradient_checkpointing=True \
  model.fsdp_config.model_dtype=bf16 \
  model.strategy=fsdp2 \
  model.lora_rank=0 \
  optim.lr="$LR" \
  'optim.betas=[0.9,0.95]' \
  optim.weight_decay=0.01 \
  optim.warmup_steps_ratio=0.1 \
  optim.clip_grad=1.0 \
  optim.lr_scheduler=cosine \
  trainer.total_epochs="$EPOCHS" \
  trainer.save_freq="$SAVE_FREQ" \
  trainer.test_freq=-1 \
  trainer.n_gpus_per_node="$NGPU" \
  trainer.nnodes=1 \
  'trainer.logger=[console]' \
  trainer.project_name=baize_posttrain_sft_surrogate \
  trainer.experiment_name="$RUN_NAME" \
  trainer.default_local_dir="$OUTPUT_DIR" \
  trainer.seed="$SEED" \
  hydra.run.dir="$HYDRA_DIR" \
  hydra.output_subdir=null \
  2>&1 | tee "$LOG_FILE"

RC=${PIPESTATUS[0]}
echo "  rc=$RC"
echo "===== PreTokenized SFT END @ $(date '+%F %T') rc=$RC ====="
if [ $RC -eq 0 ]; then
  echo "SFT complete. Checkpoint: $OUTPUT_DIR/global_step_*"
fi
exit $RC
