#!/usr/bin/env bash
# run_p2_eval_chain.sh — P2 evaluation chain (wake#827, 2026-11-06).
#
# Waits for P1 GRPO pilot to finish, then runs:
#   1. post-SFT WaveQA-RL eval (SFT step3000 ckpt, 50 questions, CPU)
#   2. post-GRPO WaveQA-RL eval (GRPO step50 ckpt, 50 questions, CPU)
#
# Pre-SFT eval (base model, no LoRA) runs separately/in-parallel.
# Oracle ceiling already done (300 questions, 100%).
#
# Usage: setsid bash run_p2_eval_chain.sh > /tmp/p2_eval_chain.log 2>&1 < /dev/null &
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VISION_DIR="$(dirname "$SCRIPT_DIR")"
PILOT_OUT="/nas_train/app.e0031982/datasets/baize-vision/out/wave_grpo_cpu_pilot"
SFT_OUT="/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
LLM_2B="$SFT_OUT/qwen3vl_2b_text_extracted"
SFT_CKPT="$SFT_OUT/step3000"
NQ=50  # CPU reduced config (noted as "CPU 缩水配置")

echo "=== P2 Eval Chain (wake#827) ==="
echo "  Started: $(date)"
echo "  Pilot output: $PILOT_OUT"

# STEP 1: Wait for P1 GRPO pilot to finish (training_log.json appears)
echo ""
echo "[Step 1] Waiting for P1 GRPO pilot to finish (training_log.json)..."
MAX_WAIT=14400  # 4h cap
WAITED=0
while true; do
  if [ -f "$PILOT_OUT/training_log.json" ]; then
    echo "[$(date +%H:%M:%S)] training_log.json found! P1 DONE."
    break
  fi
  if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    echo "[$(date +%H:%M:%S)] TIMEOUT: P1 did not finish within ${MAX_WAIT}s."
    exit 1
  fi
  echo "[$(date +%H:%M:%S)] P1 not done yet (waited ${WAITED}s)..."
  sleep 60
  WAITED=$((WAITED + 60))
done

# Find latest GRPO checkpoint
GRPO_CKPT=$(python3 -c "
import os, glob
dirs = []
for d in glob.glob(os.path.join('$PILOT_OUT', 'step*')):
    num = os.path.basename(d).replace('step', '')
    if num.isdigit() and os.path.exists(os.path.join(d, 'adapter_config.json')):
        dirs.append((int(num), d))
dirs.sort(reverse=True)
print(dirs[0][1] if dirs else '')
" 2>/dev/null)

if [ -z "$GRPO_CKPT" ]; then
  echo "WARNING: No GRPO checkpoint found. Skipping post-GRPO eval."
else
  echo "  Latest GRPO checkpoint: $GRPO_CKPT"
fi

cd "$VISION_DIR"

# STEP 2: post-SFT eval
echo ""
echo "[Step 2] Running post-SFT WaveQA-RL eval ($NQ questions, CPU)..."
OMP_NUM_THREADS=8 nice -n 19 python3 wave_rl/waveqa_eval.py \
  --device cpu --ckpt_dir "$SFT_CKPT" --model_path "$LLM_2B" \
  --n_questions "$NQ" \
  --output "$PILOT_OUT/waveqa_post_sft_${NQ}.json" \
  2>&1 | tee /tmp/waveqa_post_sft_eval.log
echo "  post-SFT eval done."

# STEP 3: post-GRPO eval
if [ -n "$GRPO_CKPT" ]; then
  echo ""
  echo "[Step 3] Running post-GRPO WaveQA-RL eval ($NQ questions, CPU)..."
  OMP_NUM_THREADS=8 nice -n 19 python3 wave_rl/waveqa_eval.py \
    --device cpu --ckpt_dir "$GRPO_CKPT" --model_path "$LLM_2B" \
    --n_questions "$NQ" \
    --output "$PILOT_OUT/waveqa_post_grpo_${NQ}.json" \
    2>&1 | tee /tmp/waveqa_post_grpo_eval.log
  echo "  post-GRPO eval done."
fi

echo ""
echo "=== P2 Eval Chain complete: $(date) ==="
echo "  Oracle ceiling: $PILOT_OUT/waveqa_oracle_300.json (300q)"
echo "  pre-SFT:        $PILOT_OUT/waveqa_pre_sft_${NQ}.json"
echo "  post-SFT:       $PILOT_OUT/waveqa_post_sft_${NQ}.json"
echo "  post-GRPO:      $PILOT_OUT/waveqa_post_grpo_${NQ}.json"
