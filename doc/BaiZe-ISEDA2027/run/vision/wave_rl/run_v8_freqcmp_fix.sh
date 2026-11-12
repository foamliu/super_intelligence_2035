#!/bin/bash
# run_v8_freqcmp_fix.sh - Re-run v8 frequency comparison experiment with fixed code
# Fixes: 1) scipy.stats.binom_test→binomtest  2) gc import scoping
# Reuses existing SFT adapter from seed 0 (saves ~20min/seed)
# Phases: seed 0 (A/B/C) → seeds 1-2 (C only) → control
set -u
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export OMP_NUM_THREADS=16
LOG=/tmp/v8_freqcmp_fix.log
OUT_BASE=/nas_train/app.e0031982/datasets/baize-vision/out
SFT_CKPT="${OUT_BASE}/cpu_rl_v8_std_s0/sft_adapter"

echo "=== v8 freqcmp FIX started at $(date) ===" > "$LOG"
echo "  Using SFT adapter: $SFT_CKPT" >> "$LOG"

SEEDS=(20261112 20261113 20261114)

# ---- Phase 1: Standard runs (3 seeds) ----
# Seed 0: full A/B/C (reuse SFT adapter, but evaluate A+B)
# Seeds 1-2: C only (reuse SFT adapter, skip A+B)
for i in 0 1 2; do
  SEED=${SEEDS[$i]}
  OUT_DIR="${OUT_BASE}/cpu_rl_v8_std_s${i}"
  echo "\n=== v8 FIX standard seed=${SEED} run $((i+1))/3 at $(date) ===" >> "$LOG"
  EXTRA_ARGS=""
  if [ $i -gt 0 ]; then
    EXTRA_ARGS="--skip_baseline_eval"
  fi
  nice -n 19 python3 cpu_rl_v8_freqcmp_experiment.py \
    --mode standard \
    --out_dir "$OUT_DIR" \
    --seed $SEED \
    --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
    --n_train 100 --n_eval 48 --n_sft 200 --sft_epochs 3 \
    --sft_ckpt "$SFT_CKPT" --skip_sft \
    $EXTRA_ARGS \
    >> "$LOG" 2>&1
  echo "  -> done at $(date)" >> "$LOG"
done

# ---- Phase 2: Control run (random reward, 1 seed) ----
echo "\n=== v8 FIX control (random reward) at $(date) ===" >> "$LOG"
nice -n 19 python3 cpu_rl_v8_freqcmp_experiment.py \
  --mode control \
  --out_dir "${OUT_BASE}/cpu_rl_v8_ctrl_s0" \
  --seed 20261112 \
  --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
  --n_train 100 --n_eval 48 \
  --sft_ckpt "$SFT_CKPT" --skip_sft \
  --skip_baseline_eval \
  >> "$LOG" 2>&1
echo "  -> control done at $(date)" >> "$LOG"

# ---- Phase 3: Analysis ----
echo "\n=== v8 FIX analysis at $(date) ===" >> "$LOG"
python3 analyze_v8_freqcmp.py >> "$LOG" 2>&1

echo "\n=== v8 freqcmp FIX ALL DONE at $(date) ===" >> "$LOG"
