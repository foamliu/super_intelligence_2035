#!/usr/bin/env bash
# Parallel eval for Xmodel-2 s1 checkpoints (20K, 30K, 40K) on idle GPUs
# s1/10K BBH continues as orphan on GPU 3 (PID from prior script)
# Strategy:
#   - GPUs 0,1,2: BBH for s1/20K, 30K, 40K in parallel (~3h each)
#   - GPUs 4-7: CS8 (8 tasks, 2 batches of 4) + Complex5 (5 tasks, 2 batches)
#     for s1/20K, then 30K, then 40K (~20 min each, ~60 min total)
#   - GPU 3: s1/10K BBH orphan (wait for it at the end)
# After all done, collect results with collect_eval_summary.py
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

LOG=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/xmodel2_s1_parallel_eval.log
exec > "$LOG" 2>&1

echo "================================================================"
echo "[$(date '+%Y-%m-%d %T')] START parallel s1 eval"
echo "================================================================"

CS_TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)
CX5_TASKS=("gsm8k:5:8" "hendrycks_math500:4:4" "mmlu:5:8" "humaneval:0:4" "mbpp:3:4")

# Checkpoints for parallel BBH (GPU 0,1,2)
PARALLEL_CKPTS=(
  "xmodel2_s1_20000|eval_s1_20000|s1/20K|78.6|0"
  "xmodel2_s1_30000|eval_s1_30000|s1/30K|117.9|1"
  "xmodel2_s1_40000|eval_s1_40000|s1/40K|157.2|2"
)

# === Phase 1: Launch 3 BBHs in parallel on GPUs 0, 1, 2 ===
echo "[$(date '+%T')] Phase 1: Launching 3 BBHs in parallel on GPUs 0,1,2"
declare -A BBH_PIDS
for ckpt in "${PARALLEL_CKPTS[@]}"; do
  IFS='|' read -r MODEL_DIR OUT_DIR LABEL TOKENS GPU <<< "$ckpt"
  MODEL_PATH="$MODEL_BASE/$MODEL_DIR"
  OUT="$EVAL_BASE/$OUT_DIR"
  mkdir -p "$OUT/cx_bbh_zeroshot"
  CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
    --model hf \
    --model_args "pretrained=${MODEL_PATH},dtype=bfloat16,trust_remote_code=True" \
    --tasks bbh_zeroshot \
    --num_fewshot 0 \
    --batch_size 4 \
    --output_path "${OUT}/cx_bbh_zeroshot" \
    > "${OUT}/cx_bbh_zeroshot.log" 2>&1 &
  BBH_PIDS[$GPU]=$!
  echo "[$(date '+%T')] Launched BBH for $LABEL on GPU $GPU (PID ${BBH_PIDS[$GPU]})"
done

# === Phase 2: CS8 + Complex5 for each checkpoint on GPUs 4-7 ===
for ckpt in "${PARALLEL_CKPTS[@]}"; do
  IFS='|' read -r MODEL_DIR OUT_DIR LABEL TOKENS BBH_GPU <<< "$ckpt"
  MODEL_PATH="$MODEL_BASE/$MODEL_DIR"
  OUT="$EVAL_BASE/$OUT_DIR"
  mkdir -p "$OUT"

  echo "[$(date '+%T')] --- CS8 for $LABEL on GPUs 4-7 ---"
  for batch in 0 1; do
    PIDS=()
    for j in 0 1 2 3; do
      task_idx=$((batch * 4 + j))
      if [ $task_idx -ge 8 ]; then break; fi
      TASK="${CS_TASKS[$task_idx]}"
      GPU=$((4 + j))
      mkdir -p "$OUT/cs_${TASK}"
      CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
        --model hf \
        --model_args "pretrained=${MODEL_PATH},dtype=bfloat16,trust_remote_code=True" \
        --tasks "$TASK" \
        --num_fewshot 0 \
        --batch_size 8 \
        --output_path "${OUT}/cs_${TASK}" \
        > "${OUT}/cs_${TASK}.log" 2>&1 &
      PIDS+=($!)
    done
    for pid in "${PIDS[@]}"; do wait "$pid"; done
  done
  echo "[$(date '+%T')] CS8 DONE for $LABEL"

  echo "[$(date '+%T')] --- Complex5 for $LABEL on GPUs 4-7 ---"
  for batch in 0 1; do
    PIDS=()
    for j in 0 1 2 3; do
      task_idx=$((batch * 4 + j))
      if [ $task_idx -ge 5 ]; then break; fi
      IFS=':' read -r TASK SHOT BATCH <<< "${CX5_TASKS[$task_idx]}"
      GPU=$((4 + j))
      mkdir -p "$OUT/cx_${TASK}"
      CUDA_VISIBLE_DEVICES="$GPU" "$PY" -m lm_eval \
        --model hf \
        --model_args "pretrained=${MODEL_PATH},dtype=bfloat16,trust_remote_code=True" \
        --tasks "$TASK" \
        --num_fewshot "$SHOT" \
        --batch_size "$BATCH" \
        --output_path "${OUT}/cx_${TASK}" \
        > "${OUT}/cx_${TASK}.log" 2>&1 &
      PIDS+=($!)
    done
    for pid in "${PIDS[@]}"; do wait "$pid"; done
  done
  echo "[$(date '+%T')] Complex5 DONE for $LABEL"
done

echo "[$(date '+%T')] All CS8+Complex5 done. Waiting for BBHs..."

# === Phase 3: Wait for all 3 parallel BBHs ===
for GPU in 0 1 2; do
  wait "${BBH_PIDS[$GPU]}" 2>/dev/null
  echo "[$(date '+%T')] BBH on GPU $GPU DONE (exit=$?)"
done

# === Phase 4: Wait for s1/10K BBH orphan (PID 681295) ===
S1_10K_BBH_PID=681295
echo "[$(date '+%T')] Checking s1/10K BBH (PID $S1_10K_BBH_PID)..."
while kill -0 "$S1_10K_BBH_PID" 2>/dev/null; do
  echo "[$(date '+%T')] s1/10K BBH still running, waiting 60s..."
  sleep 60
done
echo "[$(date '+%T')] s1/10K BBH done"

# === Phase 5: Collect all results ===
echo "[$(date '+%T')] Phase 5: Collecting all results"
ALL_CKPTS=(
  "eval_s1_10000|Xmodel-2 s1/10K (39.3B)|39.3"
  "eval_s1_20000|Xmodel-2 s1/20K (78.6B)|78.6"
  "eval_s1_30000|Xmodel-2 s1/30K (117.9B)|117.9"
  "eval_s1_40000|Xmodel-2 s1/40K (157.2B)|157.2"
)
for ckpt in "${ALL_CKPTS[@]}"; do
  IFS='|' read -r OUT_DIR LABEL TOKENS <<< "$ckpt"
  OUT="$EVAL_BASE/$OUT_DIR"
  echo "[$(date '+%T')] Collecting $LABEL..."
  "$PY" "$RUN_DIR/collect_eval_summary.py" "$OUT" "$LABEL" "$TOKENS" || \
    echo "[$(date '+%T')] WARN: collect failed for $LABEL"
done

echo "================================================================"
echo "[$(date '+%Y-%m-%d %T')] ALL DONE — 4 checkpoints evaluated"
echo "================================================================"
