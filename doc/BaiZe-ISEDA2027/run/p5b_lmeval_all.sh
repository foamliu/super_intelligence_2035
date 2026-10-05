#!/usr/bin/env bash
# P-5b ②③: Run lm_eval 8-set zero-shot on all 6 milestone HF checkpoints
# Uses GPU0-1 only (2 GPUs), runs 2 tasks in parallel per checkpoint
# Env: py310 + p6_tf5 (transformers 5.x with nemotron_h support)
#
# Milestone checkpoints (tokens = iter * GBS(1024) * seq(4094) / 1e9):
#   iter_0156 = 655M  iter_0312 = 1.3B  iter_0624 = 2.6B
#   iter_1248 = 5.2B  iter_2496 = 10.5B iter_4771 = 20B

export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b
OUT_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_results
BATCH=8

# 8 tasks (order: heaviest first for better parallelism)
TASKS=(hellaswag arc_easy boolq arc_challenge sciq piqa winogrande openbookqa)

# 6 milestone checkpoints
ITERS=(0156 0312 0624 1248 2496 4771)

mkdir -p "$OUT_BASE"

for iter in "${ITERS[@]}"; do
  MODEL="$BASE/hf_iter_${iter}"
  if [ ! -f "$MODEL/model.safetensors" ]; then
    echo "SKIP iter_${iter}: HF model not found at $MODEL"
    continue
  fi
  OUT="$OUT_BASE/iter_${iter}"
  mkdir -p "$OUT"
  echo "========== Evaluating iter_${iter} =========="

  # Run 2 tasks at a time on GPU0 and GPU1
  for ((i=0; i<${#TASKS[@]}; i+=2)); do
    task0="${TASKS[$i]}"
    task1="${TASKS[$((i+1))]}"

    log0="/tmp/p5b_lmeval_${iter}_${task0}.log"
    log1="/tmp/p5b_lmeval_${iter}_${task1}.log"

    echo "  GPU0 -> $task0 | GPU1 -> $task1"

    CUDA_VISIBLE_DEVICES=0 $PY -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
      --tasks "$task0" \
      --num_fewshot 0 \
      --batch_size "$BATCH" \
      --output_path "$OUT" \
      > "$log0" 2>&1 &
    pid0=$!

    CUDA_VISIBLE_DEVICES=1 $PY -m lm_eval \
      --model hf \
      --model_args "pretrained=${MODEL},dtype=bfloat16,trust_remote_code=False" \
      --tasks "$task1" \
      --num_fewshot 0 \
      --batch_size "$BATCH" \
      --output_path "$OUT" \
      > "$log1" 2>&1 &
    pid1=$!

    wait $pid0 $pid1
    echo "  done: $task0 (exit $?) $task1"
  done

  echo "========== iter_${iter} complete =========="
done

echo "ALL_EVAL_DONE"
