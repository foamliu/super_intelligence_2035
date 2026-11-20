#!/usr/bin/env bash
# BaiZe Stage(i) R2 · A: 复杂推理 6 集（GSM8K/MATH/BBH/MMLU/HumanEval/MBPP）
# 运维 2026-10-06 批准 A：GPU0 · 1 卡 · ≤6h
# 用 P-5b 的 6 个里程碑 HF ckpt（655M~20B token）做 zero-shot eval
# Env: py310 + p6_tf5 (transformers 5.x with nemotron_h support)
# 下载：用 huggingface.co 直连 + proxy（不用 hf-mirror，mirror 会 308 重定向导致 Python 库失败）
# 两阶段：Phase 1 预下载所有数据集 → Phase 2 offline eval
set -uo pipefail

# === 环境 ===
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_HUB_ENABLE_HF_TRANSFER=0

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b
OUT_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_complex
SUM="/tmp/baize_complex6_eval.sum"; : > "$SUM"

echo "===== A: 复杂推理 6 集 START @ $(date '+%F %T') =====" >> "$SUM"
echo "  GPU0 only, 6 tasks × 6 ckpts, --limit 100 for generative tasks" >> "$SUM"

# ============ Phase 1: 预下载所有数据集 ============
echo "  Phase 1: Pre-downloading datasets @ $(date '+%T')" >> "$SUM"
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"

$PY -c "
import os
os.environ.pop('HF_HUB_OFFLINE',None)
os.environ.pop('HF_DATASETS_OFFLINE',None)
from datasets import load_dataset

datasets_to_dl = [
    ('openai/gsm8k','main'),
    ('EleutherAI/hendrycks_math','algebra'),
    ('EleutherAI/hendrycks_math','counting_and_probability'),
    ('EleutherAI/hendrycks_math','geometry'),
    ('EleutherAI/hendrycks_math','intermediate_algebra'),
    ('EleutherAI/hendrycks_math','number_theory'),
    ('EleutherAI/hendrycks_math','prealgebra'),
    ('EleutherAI/hendrycks_math','precalculus'),
    ('cais/mmlu','all'),
    ('lukaemon/bbh','boolean_expressions'),
    ('lukaemon/bbh','date_understanding'),
    ('lukaemon/bbh','disambiguation_qa'),
    ('lukaemon/bbh','formal_fallacies'),
    ('lukaemon/bbh','geometric_shapes'),
    ('lukaemon/bbh','hyperbaton'),
    ('lukaemon/bbh','logical_deduction_five_objects'),
    ('lukaemon/bbh','logical_deduction_seven_objects'),
    ('lukaemon/bbh','logical_deduction_three_objects'),
    ('lukaemon/bbh','movie_recommendation'),
    ('lukaemon/bbh','multistep_arithmetic_two'),
    ('lukaemon/bbh','navigate'),
    ('lukaemon/bbh','object_counting'),
    ('lukaemon/bbh','penguins_in_a_table'),
    ('lukaemon/bbh','reasoning_about_colored_objects'),
    ('lukaemon/bbh','ruin_names'),
    ('lukaemon/bbh','salient_translation_error_detection'),
    ('lukaemon/bbh','snarks'),
    ('lukaemon/bbh','sports_understanding'),
    ('lukaemon/bbh','temporal_sequences'),
    ('lukaemon/bbh','tracking_shuffled_objects_five_objects'),
    ('lukaemon/bbh','tracking_shuffled_objects_seven_objects'),
    ('lukaemon/bbh','tracking_shuffled_objects_three_objects'),
    ('lukaemon/bbh','web_of_lies'),
    ('lukaemon/bbh','word_sorting'),
    ('openai/openai_humaneval',None),
    ('google-research-datasets/mbpp','full'),
]

ok=0; fail=0
for repo, config in datasets_to_dl:
    try:
        if config:
            ds = load_dataset(repo, config, split='test[:1]')
        else:
            ds = load_dataset(repo, split='test[:1]')
        print(f'OK: {repo}:{config}')
        ok += 1
    except Exception as e:
        print(f'FAIL: {repo}:{config}: {str(e)[:80]}')
        fail += 1
print(f'Done: {ok} OK, {fail} FAIL')
" >> /tmp/baize_complex6_download.log 2>&1

DL_RESULT=$(tail -1 /tmp/baize_complex6_download.log 2>/dev/null)
echo "  Phase 1 done: $DL_RESULT @ $(date '+%T')" >> "$SUM"

# ============ Phase 2: Offline eval ============
echo "  Phase 2: Offline eval @ $(date '+%T')" >> "$SUM"
unset http_proxy https_proxy
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1

# 6 tasks (generative use --limit 100, multiple_choice use --limit 200)
TASKS=(
  "gsm8k:100"
  "hendrycks_math500:100"
  "mmlu:200"
  "bbh_zeroshot:100"
  "humaneval:0"
  "mbpp:100"
)

# 6 milestone checkpoints
ITERS=(0156 0312 0624 1248 2496 4771)
BATCH=4

mkdir -p "$OUT_BASE"

for iter in "${ITERS[@]}"; do
  MODEL="$BASE/hf_iter_${iter}"
  if [ ! -f "$MODEL/model.safetensors" ]; then
    echo "SKIP iter_${iter}: HF model not found at $MODEL" >> "$SUM"
    continue
  fi
  OUT="$OUT_BASE/iter_${iter}"
  mkdir -p "$OUT"
  echo "========== Evaluating iter_${iter} @ $(date '+%T') ==========" >> "$SUM"

  for task_spec in "${TASKS[@]}"; do
    task="${task_spec%%:*}"
    limit="${task_spec##*:}"
    LOG="/tmp/baize_complex6_${iter}_${task}.log"
    
    echo "  [$iter] $task (limit=$limit) @ $(date '+%T')" >> "$SUM"
    
    LIMIT_ARG=""
    if [ "$limit" != "0" ]; then
      LIMIT_ARG="--limit $limit"
    fi

    CUDA_VISIBLE_DEVICES=0 $PY -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
      --tasks "$task" \
      --num_fewshot 0 \
      --batch_size "$BATCH" \
      $LIMIT_ARG \
      --output_path "$OUT" \
      > "$LOG" 2>&1
    rc=$?
    
    # 提取结果
    acc=$(grep -oP '(?:acc|acc_norm|exact_match|pass@1):\s*\K[0-9.]+' "$LOG" 2>/dev/null | head -1)
    echo "    rc=$rc  ${task}=${acc:-N/A}" >> "$SUM"
    
    if [ $rc -ne 0 ]; then
      echo "    ❌ FAILED — last 3 lines:" >> "$SUM"
      tail -3 "$LOG" | sed 's/^/    /' >> "$SUM"
    fi
  done
done

echo "===== A: 复杂推理 6 集 END @ $(date '+%F %T') =====" >> "$SUM"
