#!/bin/bash
# run_v8_freqcmp.sh - Run v8 frequency comparison experiment
# Phases: smoke test → seed 0 (train SFT 200ex + A/B/C eval) → seeds 1-2 (reuse SFT, C only) → control
# Estimated: ~30min smoke + ~60min seed0 + ~30min/seed × 2 + ~30min control ≈ 3 hours on CPU
set -u
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export OMP_NUM_THREADS=16
LOG=/tmp/v8_freqcmp.log
OUT_BASE=/nas_train/app.e0031982/datasets/baize-vision/out

echo "=== v8 freqcmp started at $(date) ===" > "$LOG"
SEEDS=(20261112 20261113 20261114)
SFT_CKPT=""

# ---- Phase 0: Smoke test (does NOT save reusable SFT) ----
echo "\n=== SMOKE TEST at $(date) ===" >> "$LOG"
nice -n 19 python3 cpu_rl_v8_freqcmp_experiment.py \
  --mode smoke \
  --out_dir "${OUT_BASE}/cpu_rl_v8_smoke" \
  --seed 20261112 \
  >> "$LOG" 2>&1
echo "  -> smoke done at $(date)" >> "$LOG"

# ---- Phase 1: Standard runs (3 seeds) ----
# Seed 0: trains SFT (200 examples, 3 epochs) + evaluates A/B/C
# Seeds 1-2: reuse seed 0's SFT adapter, only evaluate C (skip A/B)
for i in 0 1 2; do
  SEED=${SEEDS[$i]}
  OUT_DIR="${OUT_BASE}/cpu_rl_v8_std_s${i}"
  echo "\n=== v8 standard seed=${SEED} run $((i+1))/3 at $(date) ===" >> "$LOG"
  EXTRA_ARGS=""
  if [ $i -gt 0 ]; then
    EXTRA_ARGS="--skip_baseline_eval"
  fi
  if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
    EXTRA_ARGS="$EXTRA_ARGS --sft_ckpt $SFT_CKPT --skip_sft"
  fi
  nice -n 19 python3 cpu_rl_v8_freqcmp_experiment.py \
    --mode standard \
    --out_dir "$OUT_DIR" \
    --seed $SEED \
    --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
    --n_train 100 --n_eval 48 --n_sft 200 --sft_epochs 3 \
    $EXTRA_ARGS \
    >> "$LOG" 2>&1
  echo "  -> done at $(date)" >> "$LOG"
  # Save SFT adapter from first run for later seeds
  if [ $i -eq 0 ] && [ -d "${OUT_DIR}/sft_adapter" ]; then
    SFT_CKPT="${OUT_DIR}/sft_adapter"
    echo "  -> SFT adapter saved at $SFT_CKPT" >> "$LOG"
  fi
done

# ---- Phase 2: Control run (random reward, 1 seed) ----
echo "\n=== v8 control (random reward) at $(date) ===" >> "$LOG"
CTRL_ARGS="--skip_baseline_eval"
if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
  CTRL_ARGS="$CTRL_ARGS --sft_ckpt $SFT_CKPT --skip_sft"
fi
nice -n 19 python3 cpu_rl_v8_freqcmp_experiment.py \
  --mode control \
  --out_dir "${OUT_BASE}/cpu_rl_v8_ctrl_s0" \
  --seed 20261112 \
  --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
  --n_train 100 --n_eval 48 \
  $CTRL_ARGS \
  >> "$LOG" 2>&1
echo "  -> control done at $(date)" >> "$LOG"

echo "\n=== v8 freqcmp ALL DONE at $(date) ===" >> "$LOG"
