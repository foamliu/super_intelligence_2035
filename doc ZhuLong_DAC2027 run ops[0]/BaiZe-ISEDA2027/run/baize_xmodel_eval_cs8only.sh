#!/usr/bin/env bash
# Xmodel-2/2.5 ckpt eval: Common Sense 8 ONLY (zero-shot) + collect (no Complex 6)
# For short-decay variants L1/L2/L3: quick judge via CS8 (≥55% threshold).
# Same CS8 task list & model_args as baize_xmodel_eval.sh Phase 1 (baseline step_532000=61.03%).
# Usage: bash baize_xmodel_eval_cs8only.sh <hf_model_path> <output_dir> <label> [gpu_ids] [batch_size]
set -uo pipefail

MODEL="${1:?Usage: bash baize_xmodel_eval_cs8only.sh <hf_model_path> <output_dir> <label> [gpu_ids] [batch_size]}"
OUT="${2:?output_dir required}"
LABEL="${3:?label required e.g. L1_final}"
GPU_IDS="${4:-0,1,2,3,4,5,6,7}"
BATCH="${5:-8}"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

# NOTE: Do NOT include p6_tf5 in PYTHONPATH (transformers 5.17 lacks is_torch_fx_available).
# System transformers 4.56.1 works with modeling_xmodel2.py.
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_ALLOW_CODE_EVAL=1

mkdir -p "$OUT"
SUM="$OUT/eval_summary.txt"
: > "$SUM"
echo "===== Xmodel CS8-only eval START @ $(date '+%F %T') =====" >> "$SUM"
echo "  MODEL=$MODEL" >> "$SUM"
echo "  LABEL=$LABEL" >> "$SUM"
echo "  OUT=$OUT" >> "$SUM"
echo "  GPU_IDS=$GPU_IDS" >> "$SUM"
echo "  BATCH=$BATCH" >> "$SUM"

IFS=',' read -ra GPUS <<< "$GPU_IDS"
NUM_GPUS=${#GPUS[@]}

CS_TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)
echo "" >> "$SUM"
echo "===== Phase 1: Common sense 8 (zero-shot, ${NUM_GPUS} GPU parallel) @ $(date '+%T') =====" >> "$SUM"

CS_PIDS=()
for i in "${!CS_TASKS[@]}"; do
  TASK="${CS_TASKS[$i]}"
  GPU="${GPUS[$((i % NUM_GPUS))]}"
  SUBDIR="cs_${TASK}"
  echo "  launched GPU${GPU} -> ${TASK}" >> "$SUM"
  CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=True" \
    --tasks "$TASK" \
    --num_fewshot 0 \
    --batch_size "$BATCH" \
    --output_path "${OUT}/${SUBDIR}" \
    > "${OUT}/${SUBDIR}.log" 2>&1 &
  CS_PIDS+=($!)
done

echo "  Waiting for Phase 1 (common sense 8)..." >> "$SUM"
for pid in "${CS_PIDS[@]}"; do wait "$pid"; done
echo "  Phase 1 DONE @ $(date '+%T')" >> "$SUM"

# ── Collect results (CS8 mean, acc_norm priority) ──
echo "" >> "$SUM"
echo "===== Collecting results @ $(date '+%T') =====" >> "$SUM"
"$PY" "$RUN_DIR/baize_p8_eval_collect.py" --out "$OUT" >> "$SUM" 2>&1

echo "" >> "$SUM"
echo "===== Xmodel CS8-only eval COMPLETE @ $(date '+%T') =====" >> "$SUM"
echo "DONE: $LABEL" >> "$SUM"