#!/usr/bin/env bash
# Xmodel-2/2.5 history checkpoint evaluation: Common sense 8 (zero-shot) + Complex 6
# Uses trust_remote_code=True for custom XmodelForCausalLM
# Usage: bash baize_xmodel_eval.sh <hf_model_path> <output_dir> <label> [gpu_ids] [batch_size]
set -uo pipefail

MODEL="${1:?Usage: bash baize_xmodel_eval.sh <hf_model_path> <output_dir> <label> [gpu_ids] [batch_size]}"
OUT="${2:?output_dir required}"
LABEL="${3:?label required e.g. xmodel25_step2000}"
GPU_IDS="${4:-0,1,2,3,4,5,6,7}"
BATCH="${5:-8}"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

# NOTE: Do NOT include p6_tf5 in PYTHONPATH — it has transformers 5.17.0 which
# lacks is_torch_fx_available needed by modeling_xmodel2.py. System transformers 4.56.1 works.
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
echo "===== Xmodel eval START @ $(date '+%F %T') =====" >> "$SUM"
echo "  MODEL=$MODEL" >> "$SUM"
echo "  LABEL=$LABEL" >> "$SUM"
echo "  OUT=$OUT" >> "$SUM"
echo "  GPU_IDS=$GPU_IDS" >> "$SUM"
echo "  BATCH=$BATCH" >> "$SUM"

# Parse GPU IDs
IFS=',' read -ra GPUS <<< "$GPU_IDS"
NUM_GPUS=${#GPUS[@]}

# ── Phase 1: Common sense 8 (zero-shot, parallel across GPUs) ──
CS_TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)
echo "" >> "$SUM"
echo "===== Phase 1: Common sense 8 (zero-shot, ${NUM_GPUS} GPU parallel) @ $(date '+%T') =====" >> "$SUM"

CS_PIDS=()
for i in "${!CS_TASKS[@]}"; do
  TASK="${CS_TASKS[$i]}"
  GPU="${GPUS[$((i % NUM_GPUS))]}"
  SUBDIR="cs_${TASK}"
  echo "  launched GPU${GPU} -> ${TASK} (pid $$)" >> "$SUM"
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

# ── Phase 2: Complex 6 (default n-shot, 6 GPUs parallel) ──
# gsm8k: 5-shot, hendrycks_math500: 4-shot, mmlu: 5-shot
# bbh_zeroshot: 0-shot, humaneval: 0-shot, mbpp: 3-shot
CX_DEFS=(
  "gsm8k:5:8"
  "hendrycks_math500:4:4"
  "mmlu:5:8"
  "bbh_zeroshot:0:4"
  "humaneval:0:4"
  "mbpp:3:4"
)
echo "" >> "$SUM"
echo "===== Phase 2: Complex 6 (default n-shot, 6 GPU parallel) @ $(date '+%T') =====" >> "$SUM"

CX_PIDS=()
for i in "${!CX_DEFS[@]}"; do
  IFS=':' read -r TASK SHOT BS <<< "${CX_DEFS[$i]}"
  GPU="${GPUS[$((i % NUM_GPUS))]}"
  SUBDIR="cx_${TASK}"
  echo "  launched GPU${GPU} -> ${TASK} (shot=${SHOT}, batch=${BS})" >> "$SUM"
  CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=True,attn_implementation=sdpa" \
    --tasks "$TASK" \
    --num_fewshot "$SHOT" \
    --batch_size "$BS" \
    --output_path "${OUT}/${SUBDIR}" \
    > "${OUT}/${SUBDIR}.log" 2>&1 &
  CX_PIDS+=($!)
done

echo "  Waiting for Phase 2 (complex 6)..." >> "$SUM"
for pid in "${CX_PIDS[@]}"; do wait "$pid"; done
echo "  Phase 2 DONE @ $(date '+%T')" >> "$SUM"

# ── Phase 3: Collect results ──
echo "" >> "$SUM"
echo "===== Phase 3: Collecting results @ $(date '+%T') =====" >> "$SUM"
"$PY" "$RUN_DIR/baize_p8_eval_collect.py" --out "$OUT" >> "$SUM" 2>&1

echo "" >> "$SUM"
echo "===== Xmodel eval COMPLETE @ $(date '+%T') =====" >> "$SUM"
echo "DONE: $LABEL" >> "$SUM"
