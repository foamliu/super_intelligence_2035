#!/usr/bin/env bash
# Re-evaluate Xmodel-2 s1 checkpoints (step 10000-40000) with trust_remote_code=True
# The previous eval used trust_remote_code=False → wrong results (hellaswag 0.296 vs correct 0.630)
# Usage: bash xmodel2_s1_reeval.sh
# Runs 4 checkpoints sequentially, each using 8 GPUs (CS8 parallel + Complex6 parallel)
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_ALLOW_CODE_EVAL=1

EVAL_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel2_history
MODEL_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/xmodel_eval

# Checkpoints: (model_dir, output_dir, label, tokens_B)
CHECKPOINTS=(
  "xmodel2_s1_10000|eval_s1_10000|Xmodel-2 s1/10K (39.3B)|39.3"
  "xmodel2_s1_20000|eval_s1_20000|Xmodel-2 s1/20K (78.6B)|78.6"
  "xmodel2_s1_30000|eval_s1_30000|Xmodel-2 s1/30K (117.9B)|117.9"
  "xmodel2_s1_40000|eval_s1_40000|Xmodel-2 s1/40K (157.2B)|157.2"
)

CS_TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)
CX_DEFS=(
  "gsm8k:5:8"
  "hendrycks_math500:4:4"
  "mmlu:5:8"
  "bbh_zeroshot:0:4"
  "humaneval:0:4"
  "mbpp:3:4"
)

for ckpt in "${CHECKPOINTS[@]}"; do
  IFS='|' read -r MODEL_DIR OUT_DIR LABEL TOKENS <<< "$ckpt"
  MODEL_PATH="$MODEL_BASE/$MODEL_DIR"
  OUT="$EVAL_BASE/$OUT_DIR"

  if [ -f "$OUT/p8_eval_summary.json" ]; then
    echo "[$(date '+%T')] SKIP $LABEL — already has summary"
    continue
  fi

  mkdir -p "$OUT"
  echo "================================================================"
  echo "[$(date '+%T')] Evaluating $LABEL ($MODEL_PATH)"
  echo "  Output: $OUT"
  echo "================================================================"

  # Phase 1: Common sense 8 (zero-shot, 8 GPU parallel)
  echo "[$(date '+%T')] Phase 1: Common8 (8 GPU parallel)"
  CS_PIDS=()
  for i in "${!CS_TASKS[@]}"; do
    TASK="${CS_TASKS[$i]}"
    GPU=$i
    CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL_PATH},dtype=bfloat16,trust_remote_code=True" \
      --tasks "$TASK" \
      --num_fewshot 0 \
      --batch_size 8 \
      --output_path "${OUT}/cs_${TASK}" \
      > "${OUT}/cs_${TASK}.log" 2>&1 &
    CS_PIDS+=($!)
  done
  for pid in "${CS_PIDS[@]}"; do wait "$pid"; done
  echo "[$(date '+%T')] Phase 1 DONE"

  # Phase 2: Complex 6 (default n-shot, 6 GPU parallel)
  echo "[$(date '+%T')] Phase 2: Complex6 (6 GPU parallel)"
  CX_PIDS=()
  for i in "${!CX_DEFS[@]}"; do
    IFS=':' read -r TASK SHOT BATCH <<< "${CX_DEFS[$i]}"
    GPU=$i
    CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL_PATH},dtype=bfloat16,trust_remote_code=True" \
      --tasks "$TASK" \
      --num_fewshot "$SHOT" \
      --batch_size "$BATCH" \
      --output_path "${OUT}/cx_${TASK}" \
      > "${OUT}/cx_${TASK}.log" 2>&1 &
    CX_PIDS+=($!)
  done
  for pid in "${CX_PIDS[@]}"; do wait "$pid"; done
  echo "[$(date '+%T')] Phase 2 DONE"

  # Collect results
  echo "[$(date '+%T')] Collecting results..."
  "$PY" "$RUN_DIR/collect_eval_summary.py" "$OUT" "$LABEL" "$TOKENS" 2>&1 || true
  echo "[$(date '+%T')] $LABEL COMPLETE"
done

echo "================================================================"
echo "[$(date '+%T')] ALL Xmodel-2 s1 re-evaluations COMPLETE"
echo "================================================================"
