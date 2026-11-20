#!/usr/bin/env bash
# BaiZe Stage(i) R2 · A v2 FIX: humaneval + mbpp only (HF_ALLOW_CODE_EVAL=1)
# v2 main script (baize_complex6_eval_v2.sh) forgot to export HF_ALLOW_CODE_EVAL=1
# → humaneval/mbpp crashed at code_eval metric stage. This fix re-runs ONLY those
#   2 tasks on GPU1 (parallel with main v2 on GPU0), writing to same lm_eval_complex/ dirs.
# 6 milestone ckpts: iter_0156~4771 (655M~20B token)
set -uo pipefail

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_HUB_ENABLE_HF_TRANSFER=0
# ONLINE with proxy
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
# ⭐ THE FIX: allow code_eval metric to execute model-generated code
export HF_ALLOW_CODE_EVAL=1

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b
OUT_BASE=$BASE/lm_eval_complex
SUM="/tmp/baize_complex6_humaneval_mbpp_fix.sum"; : > "$SUM"

echo "===== A v2 FIX: humaneval + mbpp (HF_ALLOW_CODE_EVAL=1) START @ $(date '+%F %T') =====" >> "$SUM"
echo "  GPU1 only, HF_ALLOW_CODE_EVAL=1, online proxy" >> "$SUM"

# Only the 2 code-eval tasks that failed
TASKS=(
  "humaneval:100"
  "mbpp:100"
)
ITERS=(0156 0312 0624 1248 2496 4771)
BATCH=4

mkdir -p "$OUT_BASE"

for iter in "${ITERS[@]}"; do
  MODEL="$BASE/hf_iter_${iter}"
  if [ ! -f "$MODEL/model.safetensors" ]; then
    echo "SKIP iter_${iter}: HF model not found at $MODEL" >> "$SUM"
    continue
  fi
  OUT="$OUT_BASE/iter_${iter}"; mkdir -p "$OUT"
  echo "========== iter_${iter} @ $(date '+%T') ==========" >> "$SUM"

  for task_spec in "${TASKS[@]}"; do
    task="${task_spec%%:*}"
    limit="${task_spec##*:}"
    LOG="/tmp/baize_c6fix_${iter}_${task}.log"

    echo "  [$iter] $task (limit=$limit) @ $(date '+%T')" >> "$SUM"

    CUDA_VISIBLE_DEVICES=1 $PY -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
      --tasks "$task" \
      --num_fewshot 0 \
      --batch_size "$BATCH" \
      --limit "$limit" \
      --output_path "$OUT" \
      --confirm_run_unsafe_code \
      > "$LOG" 2>&1
    rc=$?

    if [ $rc -ne 0 ]; then
      echo "    rc=$rc  ❌ FAILED — last 3 lines:" >> "$SUM"
      tail -3 "$LOG" | sed 's/^/    /' >> "$SUM"
    else
      echo "    rc=0  ✅ done" >> "$SUM"
    fi
  done
done

echo "  FIX COMPLETE @ $(date '+%T')" >> "$SUM"
