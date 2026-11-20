#!/usr/bin/env bash
# BaiZe Stage(i) R2 · A v2: 复杂推理 6 集 (FIXED — online proxy, correct repos)
# 运维 2026-10-06 批准 A：GPU0 · 1 卡 · ≤6h
# v1 failed: offline mode + wrong dataset repos (EleutherAI/hendrycks_math, lukaemon/bbh)
#            + missing code_eval metric. v2 runs ONLINE with proxy (huggingface.co direct).
# gsm8k already succeeded in v1 (results saved) → reused; only 5 failed tasks re-run.
# Tasks: hendrycks_math500(100) / mmlu(200) / bbh_zeroshot(100) / humaneval(100) / mbpp(100)
# 6 milestone ckpts: iter_0156~4771 (655M~20B token)
set -uo pipefail

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_HUB_ENABLE_HF_TRANSFER=0
# ONLINE with proxy (NOT offline — v1 offline caused wrong-repo / missing-metric failures)
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b
OUT_BASE=$BASE/lm_eval_complex
SUM="/tmp/baize_complex6_v2.sum"; : > "$SUM"
COLLECTOR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_complex6_collect.py

echo "===== A v2: 复杂推理 6 集 (online, 5 tasks re-run, gsm8k reused) START @ $(date '+%F %T') =====" >> "$SUM"
echo "  GPU0 only, online proxy=172.19.92.25:13128, NO offline mode" >> "$SUM"

# 5 tasks to re-run (gsm8k reused from v1 — already has all 6 iters saved)
TASKS=(
  "hendrycks_math500:100"
  "mmlu:200"
  "bbh_zeroshot:100"
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
    LOG="/tmp/baize_c6v2_${iter}_${task}.log"

    echo "  [$iter] $task (limit=$limit) @ $(date '+%T')" >> "$SUM"

    CUDA_VISIBLE_DEVICES=0 $PY -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
      --tasks "$task" \
      --num_fewshot 0 \
      --batch_size "$BATCH" \
      --limit "$limit" \
      --output_path "$OUT" \
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

# ============ Collect all results (gsm8k v1 + 5 new) ============
echo "  Collecting results @ $(date '+%T')" >> "$SUM"
$PY "$COLLECTOR" >> "$SUM" 2>&1

echo "===== A v2 END @ $(date '+%F %T') =====" >> "$SUM"
