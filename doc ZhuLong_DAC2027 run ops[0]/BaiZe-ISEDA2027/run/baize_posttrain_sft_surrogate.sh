#!/usr/bin/env bash
# baize_posttrain_sft_surrogate.sh — Phase 2 surrogate SFT launch (verl FSDP)
#
# Purpose: End-to-end SFT validation on MiniCPM5-2B (2B, Llama-arch, Apache 2.0)
#          as a BaiZe surrogate, using the R152 unified PyAether SFT parquet
#          (1725 pairs, ~650K tok). Validates the SFT recipe before BaiZe ckpt.
#
# Framework: verl 0.4.0 FSDP SFT trainer (fsdp_sft_trainer.py, hydra config).
#   - MultiTurnSFTDataset reads `conversation` column (messages_key=conversation).
#   - Loss masked to assistant turns only.
#   - Checkpoint saved as HF format (safetensors) — directly vLLM-serveable.
#
# GPU: 2×A40 (indices 6,7 by default), FSDP2 across 2 GPUs.
#   Per 2026-11-10 13:40 user order: "GPU6-7 训练".
#   Per 2026-11-10 17:10 user order: GPU5-7 occupied by vLLM serve until
#   sandbox tunnel restored. GPU-busy guard prevents launching on occupied GPUs.
#
# Red lines: source parquet gate PASS (R150/R151, 0 hits); no new data added.
#   Report must label results "替身预演，收益不可迁移到 BaiZe".
#
# Usage:
#   bash baize_posttrain_sft_surrogate.sh --dry-run     # print recipe only
#   bash baize_posttrain_sft_surrogate.sh --prep-only   # create train/val split
#   bash baize_posttrain_sft_surrogate.sh --smoke       # tiny run (5 steps)
#   bash baize_posttrain_sft_surrogate.sh               # full SFT (v5v6v7 corpus)
#   GPUS="4,5" bash baize_posttrain_sft_surrogate.sh    # override GPU set
#
# R207: Retrain with v11-v35 merged corpus (943 pairs, 189 unique APIs, dual gate PASS):
#   bash baize_posttrain_sft_surrogate.sh --dry-run \
#     --src-parquet sft_pyaether_corpus_v11_v35_merged.parquet \
#     --run-name minicpm5_pyaether_v2_v11v35
#   bash baize_posttrain_sft_surrogate.sh --prep-only \
#     --src-parquet sft_pyaether_corpus_v11_v35_merged.parquet \
#     --run-name minicpm5_pyaether_v2_v11v35
#   bash baize_posttrain_sft_surrogate.sh \
#     --src-parquet sft_pyaether_corpus_v11_v35_merged.parquet \
#     --run-name minicpm5_pyaether_v2_v11v35 --epochs 5
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# ============ paths ============
VERL_PY="$HOME/code/verl_cu124_venv/bin/python"
VERL_TORCHRUN="$HOME/code/verl_cu124_venv/bin/torchrun"
MODEL_PATH="/nas_data/app.e0031982/models/MiniCPM5-2B"
SRC_PARQUET="$SCRIPT_DIR/sft_pyaether_corpus_unified_v5v6v7.parquet"
RUN_NAME="minicpm5_pyaether_v1"
TRAIN_PARQUET="$SCRIPT_DIR/sft_surrogate_train.parquet"
VAL_PARQUET="$SCRIPT_DIR/sft_surrogate_val.parquet"
OUTPUT_DIR="$SCRIPT_DIR/sft_surrogate_runs/${RUN_NAME}"
DATA_SUBDIR="$SCRIPT_DIR"
HYDRA_DIR="/tmp/baize_sft_surrogate_hydra"
LOG_FILE="/tmp/baize_posttrain_sft_surrogate.log"

# ============ GPU config ============
GPUS="${GPUS:-6,7}"
NGPU=$(echo "$GPUS" | tr ',' '\n' | wc -l)

# ============ training hyperparams ============
MAX_LENGTH=2048
TRAIN_BATCH=64
MICRO_BATCH=4
TOTAL_EPOCHS=3
LR=1e-5
WARMUP_RATIO=0.1
SAVE_FREQ=20
TEST_FREQ=-1
SEED=42
GRAD_CKPT=1
UPSAMPLE=1
FT_MODE=full
LORA_RANK=64
LORA_ALPHA=128

# ============ mode switches ============
DRY_RUN=0; SMOKE=0; PREP_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --smoke) SMOKE=1 ;;
    --prep-only) PREP_ONLY=1 ;;
    --gpus) GPUS="$2"; shift; NGPU=$(echo "$GPUS" | tr ',' '\n' | wc -l) ;;
    --epochs) TOTAL_EPOCHS="$2"; shift ;;
    --lr) LR="$2"; shift ;;
    --max-length) MAX_LENGTH="$2"; shift ;;
    --batch) TRAIN_BATCH="$2"; shift ;;
    --micro-batch) MICRO_BATCH="$2"; shift ;;
    --upsample) UPSAMPLE="$2"; shift ;;
    --ft-mode) FT_MODE="$2"; shift ;;
    --lora-rank) LORA_RANK="$2"; shift ;;
    --src-parquet) SRC_PARQUET="$2"; shift ;;
    --run-name)
      RUN_NAME="$2"; shift
      DATA_SUBDIR="$SCRIPT_DIR/sft_surrogate_data/${RUN_NAME}"
      TRAIN_PARQUET="$DATA_SUBDIR/sft_surrogate_train.parquet"
      VAL_PARQUET="$DATA_SUBDIR/sft_surrogate_val.parquet"
      OUTPUT_DIR="$SCRIPT_DIR/sft_surrogate_runs/${RUN_NAME}"
      ;;
    *) echo "unknown arg: $1" ;;
  esac
  shift
done

# ============ recipe print ============
print_recipe() {
  cat <<EOF
===== BaiZe Phase 2 Surrogate SFT — RECIPE @ $(date '+%F %T') =====
  mode            : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))
  surrogate note  : 替身预演，收益不可迁移到 BaiZe (MiniCPM5-2B Llama-arch != BaiZe Mamba2)
  model           : $MODEL_PATH (MiniCPM5-2B, 2B, LlamaForCausalLM)
  framework       : verl 0.4.0 FSDP2 SFT (fsdp_sft_trainer.py)
  GPUs            : $GPUS ($NGPU x A40)
  data.train      : $TRAIN_PARQUET
  data.val        : $VAL_PARQUET
  data.src        : $SRC_PARQUET
  data.upsample   : x$UPSAMPLE
  max_length      : $MAX_LENGTH
  batch           : global=$TRAIN_BATCH  micro/GPU=$MICRO_BATCH
  epochs          : $TOTAL_EPOCHS
  lr              : $LR (cosine, warmup_ratio=$WARMUP_RATIO)
  ft_mode         : $FT_MODE  (lora_rank=$LORA_RANK lora_alpha=$LORA_ALPHA)
  grad_checkpoint : $GRAD_CKPT
  save_freq       : $SAVE_FREQ steps
  output_dir      : $OUTPUT_DIR
  log             : $LOG_FILE
  red line        : source parquet gate PASS (R150/R151 0 hits); no new data added
===== END RECIPE =====
EOF
}

# ============ step 1: data prep ============
prep_data() {
  if [ -f "$TRAIN_PARQUET" ] && [ -f "$VAL_PARQUET" ]; then
    echo "[prep] train/val parquet already exist, skipping split."
    return 0
  fi
  if [ ! -f "$SRC_PARQUET" ]; then
    echo "ERROR: source parquet not found: $SRC_PARQUET"
    echo "       Run R152 merge first: baize_posttrain_merge_v5v6.py --parquet"
    exit 1
  fi
  echo "[prep] splitting $SRC_PARQUET -> train/val (90/10, seed=$SEED, upsample=x$UPSAMPLE)"
  mkdir -p "$DATA_SUBDIR"
  "$VERL_PY" "$SCRIPT_DIR/baize_posttrain_sft_surrogate_prep.py" \
    --src "$SRC_PARQUET" \
    --out-dir "$DATA_SUBDIR" \
    --val-ratio 0.1 \
    --upsample "$UPSAMPLE" \
    --seed "$SEED" || { echo "ERROR: data prep failed"; exit 1; }
}

# ============ dry-run ============
if [ $DRY_RUN = 1 ]; then
  print_recipe
  echo ""
  echo "[dry-run] checking prerequisites (no training launched)..."
  [ -x "$VERL_TORCHRUN" ] && echo "  torchrun: $VERL_TORCHRUN OK" || echo "  torchrun: NOT FOUND"
  [ -d "$MODEL_PATH" ] && echo "  model: $MODEL_PATH OK" || echo "  model: NOT FOUND"
  "$VERL_PY" -c 'import verl, flash_attn, peft; print("  verl+flash_attn+peft: OK")' 2>/dev/null || echo "  verl deps: MISSING"
  [ -f "$SRC_PARQUET" ] && echo "  src parquet: OK ($(wc -c < "$SRC_PARQUET") bytes)" || echo "  src parquet: NOT FOUND"
  echo "[dry-run] recipe printed. Run --prep-only to create train/val, or remove --dry-run to train."
  exit 0
fi

# ============ prep-only ============
if [ $PREP_ONLY = 1 ]; then
  prep_data
  echo "[prep-only] done. train=$TRAIN_PARQUET val=$VAL_PARQUET"
  exit 0
fi

# ============ real run prerequisites ============
print_recipe
echo ""
[ -x "$VERL_TORCHRUN" ] || { echo "ERROR: torchrun not found: $VERL_TORCHRUN"; exit 1; }
[ -d "$MODEL_PATH" ] || { echo "ERROR: model not found: $MODEL_PATH"; exit 1; }
prep_data
[ -f "$TRAIN_PARQUET" ] || { echo "ERROR: train parquet missing after prep"; exit 1; }
[ -f "$VAL_PARQUET" ] || { echo "ERROR: val parquet missing after prep"; exit 1; }

# GPU busy guard
echo "[guard] checking GPU $GPUS are free..."
GPU_LIST=$(echo "$GPUS" | tr ',' ' ')
BUSY=""
for gi in $GPU_LIST; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$gi" 2>/dev/null | tr -d ' ')
  if [ "${used:-0}" -gt 1000 ]; then BUSY="$BUSY $gi(${used}MiB)"; fi
done
if [ -n "$BUSY" ]; then
  echo "ERROR: GPU$BUSY is occupied (used > 1GB)."
  echo "       Per 2026-11-10 17:10 user order, GPU5-7 may hold vLLM serve."
  echo "       Wait for sandbox restore, stop serve, re-run. Or: GPUS=\"<free>\" bash $0"
  exit 1
fi
echo "[guard] GPU $GPUS all free OK"

if [ $SMOKE = 1 ]; then
  TOTAL_EPOCHS=1; SAVE_FREQ=5; OUTPUT_DIR="${OUTPUT_DIR}_smoke"
  echo "[smoke] epochs=1 save_freq=5 output=$OUTPUT_DIR"
fi

LORA_CFG="model.lora_rank=0"
if [ "$FT_MODE" = "lora" ]; then
  LORA_CFG="model.lora_rank=$LORA_RANK model.lora_alpha=$LORA_ALPHA"
  echo "[config] LoRA enabled: rank=$LORA_RANK alpha=$LORA_ALPHA"
fi
GC_CFG="model.enable_gradient_checkpointing=$([ $GRAD_CKPT = 1 ] && echo True || echo False)"

# ============ launch verl FSDP SFT ============
mkdir -p "$OUTPUT_DIR" "$HYDRA_DIR"
export CUDA_VISIBLE_DEVICES="$GPUS"
export HF_HOME="/tmp/hf_home"
export HF_MODULES_CACHE="/tmp/hf_home/modules"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
export TOKENIZERS_PARALLELISM=true
export WANDB_MODE=disabled

echo ""
echo "===== Surrogate SFT START @ $(date '+%F %T') =====" | tee "$LOG_FILE"

"$VERL_TORCHRUN" --nproc_per_node="$NGPU" --master_addr=127.0.0.1 --master_port=29830 \
  -m verl.trainer.fsdp_sft_trainer \
  --config-name sft_trainer \
  data.train_files="$TRAIN_PARQUET" \
  data.val_files="$VAL_PARQUET" \
  data.train_batch_size="$TRAIN_BATCH" \
  data.micro_batch_size_per_gpu="$MICRO_BATCH" \
  data.max_length="$MAX_LENGTH" \
  data.truncation=right \
  data.multiturn.enable=true \
  data.multiturn.messages_key=conversation \
  data.multiturn.tools_key=null \
  model.partial_pretrain="$MODEL_PATH" \
  model.trust_remote_code=true \
  $GC_CFG \
  model.fsdp_config.model_dtype=bf16 \
  model.strategy=fsdp2 \
  $LORA_CFG \
  optim.lr="$LR" \
  optim.betas='[0.9,0.95]' \
  optim.weight_decay=0.01 \
  optim.warmup_steps_ratio="$WARMUP_RATIO" \
  optim.clip_grad=1.0 \
  optim.lr_scheduler=cosine \
  trainer.total_epochs="$TOTAL_EPOCHS" \
  trainer.save_freq="$SAVE_FREQ" \
  trainer.test_freq="$TEST_FREQ" \
  trainer.n_gpus_per_node="$NGPU" \
  trainer.nnodes=1 \
  trainer.logger='[console]' \
  trainer.project_name=baize_posttrain_sft_surrogate \
  trainer.experiment_name=minicpm5_pyaether_v1 \
  trainer.default_local_dir="$OUTPUT_DIR" \
  trainer.seed="$SEED" \
  hydra.run.dir="$HYDRA_DIR" \
  hydra.output_subdir=null \
  2>&1 | tee -a "$LOG_FILE"

RC=${PIPESTATUS[0]}
echo "  rc=$RC" | tee -a "$LOG_FILE"
echo "===== Surrogate SFT END @ $(date '+%F %T') rc=$RC =====" | tee -a "$LOG_FILE"
if [ $RC -eq 0 ]; then
  echo ""
  echo "SFT complete. Checkpoint: $OUTPUT_DIR/global_step_*"
  echo "   Next: serve SFT ckpt with vLLM, then run EDA-Eval (baize_posttrain_eval.sh)."
  echo "   Report results as: 替身预演，收益不可迁移到 BaiZe"
fi
exit $RC
