#!/bin/bash
# run_v9_freqcmp.sh - Run v9 frequency comparison experiment (scaled-up)
# v9 changes from v8: SFT 500ex×5ep (was 200×3), eval 96q (was 48), GRPO 30 steps (was 15)
# Phases: smoke test → seed 0 (train SFT 500ex + A/B/C eval) → seeds 1-2 (reuse SFT, C only) → control
# Estimated: ~6min smoke + ~90min seed0 + ~45min/seed × 2 + ~45min control ≈ 4.5 hours on CPU
set -u
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export OMP_NUM_THREADS=16
LOG=/tmp/v9_freqcmp.log
OUT_BASE=/nas_train/app.e0031982/datasets/baize-vision/out

echo "=== v9 freqcmp started at $(date) ===" > "$LOG"
SEEDS=(20261112 20261113 20261114)
SFT_CKPT=""

# ---- Phase 0: Smoke test (ALREADY PASSED — skipped) ----
# Smoke test completed successfully at 2026-11-13 04:40-04:51
# All phases ran end-to-end, results saved to cpu_rl_v9_smoke/
echo "\n=== SMOKE TEST SKIPPED (already passed at 2026-11-13 04:51) ===" >> "$LOG"

# ---- Phase 1: Standard runs (3 seeds) ----
# Seed 0: trains SFT (500 examples, 5 epochs) + evaluates A/B/C
# Seeds 1-2: reuse seed 0's SFT adapter, only evaluate C (skip A/B)
for i in 0 1 2; do
  SEED=${SEEDS[$i]}
  OUT_DIR="${OUT_BASE}/cpu_rl_v9_std_s${i}"
  echo "\n=== v9 standard seed=${SEED} run $((i+1))/3 at $(date) ===" >> "$LOG"
  EXTRA_ARGS=""
  if [ $i -gt 0 ]; then
    EXTRA_ARGS="--skip_baseline_eval"
  fi
  if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
    EXTRA_ARGS="$EXTRA_ARGS --sft_ckpt $SFT_CKPT --skip_sft"
  fi
  nice -n 19 python3 cpu_rl_v9_freqcmp_experiment.py \
    --mode standard \
    --out_dir "$OUT_DIR" \
    --seed $SEED \
    --n_grpo_steps 30 --group_size 4 --batch_prompts 2 \
    --n_train 100 --n_eval_per_cat 16 --n_sft 500 --sft_epochs 5 \
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
echo "\n=== v9 control (random reward) at $(date) ===" >> "$LOG"
CTRL_ARGS="--skip_baseline_eval"
if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
  CTRL_ARGS="$CTRL_ARGS --sft_ckpt $SFT_CKPT --skip_sft"
fi
nice -n 19 python3 cpu_rl_v9_freqcmp_experiment.py \
  --mode control \
  --out_dir "${OUT_BASE}/cpu_rl_v9_ctrl_s0" \
  --seed 20261112 \
  --n_grpo_steps 30 --group_size 4 --batch_prompts 2 \
  --n_train 100 --n_eval_per_cat 16 \
  $CTRL_ARGS \
  >> "$LOG" 2>&1
echo "  -> control done at $(date)" >> "$LOG"

echo "\n=== v9 freqcmp ALL DONE at $(date) ===" >> "$LOG"
