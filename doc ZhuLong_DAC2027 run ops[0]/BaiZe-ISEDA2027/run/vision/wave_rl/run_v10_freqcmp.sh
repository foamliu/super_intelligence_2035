#!/bin/bash
# run_v10_freqcmp.sh - v10 frequency comparison experiment on .17 (post-migration)
#
# WHY v10 (fixing v9's NO CHANGE with n_disc=0):
#   v9 seed0: A=0% B=49.5% C=49.5% p=1.0 n_disc=0 → NO CHANGE
#   Diagnosis: grpo_lr=1e-6 is too low → GRPO has reward signal (nz_std=75%)
#   but zero discordant cases (policy doesn't change predictions).
#   v10 FIXES:
#     1. grpo_lr: 1e-6 → 1e-5 (10x increase, key fix for n_disc=0)
#     2. n_grpo_steps: 30 → 50 (more policy updates)
#     3. Base model: qwen3vl_2b_text_extracted → Qwen3.5-2B (user-specified, available on .17)
#     4. Output: local directory on .17 (nas_train datasets not accessible post-migration)
#   Everything else identical to v9 (SFT 500ex×5ep, eval 96q, 3 seeds + control).
#
# PRE-REGISTERED JUDGMENT (written BEFORE running, 2026-11-13):
#   A (zero-shot, fresh LoRA):  ~0-50% (format-dependent, NOT a capability metric)
#   B (SFT on freq comparison):  >55% (500 examples × 5 epochs should push above chance)
#   C (GRPO on top of B):        >B (RL refines frequency discrimination)
#   D (GRPO with random reward):  <= B (control, random reward doesn't help)
#   DIAGNOSTIC: n_disc > 0 (GRPO must change at least some predictions — was 0 in v9)
#   SUCCESS: C > B (mean), McNemar p < 0.05, 3 seeds all C >= B, n_disc > 0
#   FAIL:    C <= B (mean) OR p >= 0.05 OR seeds not consistent OR n_disc = 0
#
# Infrastructure note: v9 ran on .12 (nas_train paths). .17 migration at 09:12 broke
# nas_train access (/nas_train → /H100_train empty symlink). v10 uses nas_data paths.
# Model change: Qwen3.5-2B (Qwen3_5ForConditionalGeneration, AutoModelForCausalLM
# confirmed working per s2_fallback_result.json: 1.88B params, LoRA 737K, 1.2s/step).
set -u
cd /nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export OMP_NUM_THREADS=16
# Use GPU 7 (only free A40 on .17; GPUs 0-6 occupied by posttrain).
# Qwen3.5-2B uses linear attention (gated delta rule) — without optimized
# kernels (causal_conv1d / flash-linear-attention) the CPU fallback is
# ~10x+ slower for training. GPU 7 has 46GB free, plenty for a 2B model.
# bf16 dtype halves memory vs fp32 (model ~4GB, activations ~18GB, total ~22GB).
export CUDA_VISIBLE_DEVICES=7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LOG=/tmp/v10_freqcmp.log
MODEL_PATH=/nas_data/app.e0031982/models/Qwen3.5-2B
OUT_BASE=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl/v10_results
GRPO_LR=1e-5
N_GRPO_STEPS=50

echo "=== v10 freqcmp started at $(date) ===" > "$LOG"
echo "  model=$MODEL_PATH  grpo_lr=$GRPO_LR  n_grpo_steps=$N_GRPO_STEPS" >> "$LOG"
echo "  out_base=$OUT_BASE" >> "$LOG"
SEEDS=(20261112 20261113 20261114)
SFT_CKPT=""

# ---- Phase 0: Smoke test ----
echo "=== SMOKE TEST at $(date) ===" >> "$LOG"
nice -n 19 python3 cpu_rl_v9_freqcmp_experiment.py \
  --mode smoke \
  --model_path "$MODEL_PATH" \
  --out_dir "${OUT_BASE}/cpu_rl_v10_smoke" \
  --seed 20261112 \
  --grpo_lr $GRPO_LR --n_grpo_steps 3 --group_size 4 --batch_prompts 2 \
  --n_train 12 --n_eval_per_cat 4 --n_sft 24 --sft_epochs 5 \
  >> "$LOG" 2>&1
SMOKE_RC=$?
echo "  -> smoke exit=$SMOKE_RC at $(date)" >> "$LOG"
if [ $SMOKE_RC -ne 0 ]; then
  echo "!!! SMOKE TEST FAILED (exit=$SMOKE_RC) — aborting full experiment" >> "$LOG"
  echo "=== v10 ABORTED (smoke failed) at $(date) ===" >> "$LOG"
  exit 1
fi
echo "  -> SMOKE PASSED, proceeding to full experiment" >> "$LOG"

# ---- Phase 1: Standard runs (3 seeds) ----
for i in 0 1 2; do
  SEED=${SEEDS[$i]}
  OUT_DIR="${OUT_BASE}/cpu_rl_v10_std_s${i}"
  echo "=== v10 standard seed=${SEED} run $((i+1))/3 at $(date) ===" >> "$LOG"
  EXTRA_ARGS=""
  if [ $i -gt 0 ]; then
    EXTRA_ARGS="--skip_baseline_eval"
  fi
  if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
    EXTRA_ARGS="$EXTRA_ARGS --sft_ckpt $SFT_CKPT --skip_sft"
  fi
  nice -n 19 python3 cpu_rl_v9_freqcmp_experiment.py \
    --mode standard \
    --model_path "$MODEL_PATH" \
    --out_dir "$OUT_DIR" \
    --seed $SEED \
    --grpo_lr $GRPO_LR --n_grpo_steps $N_GRPO_STEPS --group_size 4 --batch_prompts 2 \
    --n_train 100 --n_eval_per_cat 16 --n_sft 500 --sft_epochs 5 \
    $EXTRA_ARGS \
    >> "$LOG" 2>&1
  echo "  -> done at $(date)" >> "$LOG"
  if [ $i -eq 0 ] && [ -d "${OUT_DIR}/sft_adapter" ]; then
    SFT_CKPT="${OUT_DIR}/sft_adapter"
    echo "  -> SFT adapter saved at $SFT_CKPT" >> "$LOG"
  fi
done

# ---- Phase 2: Control run (random reward, 1 seed) ----
echo "=== v10 control (random reward) at $(date) ===" >> "$LOG"
CTRL_ARGS="--skip_baseline_eval"
if [ -n "$SFT_CKPT" ] && [ -d "$SFT_CKPT" ]; then
  CTRL_ARGS="$CTRL_ARGS --sft_ckpt $SFT_CKPT --skip_sft"
fi
nice -n 19 python3 cpu_rl_v9_freqcmp_experiment.py \
  --mode control \
  --model_path "$MODEL_PATH" \
  --out_dir "${OUT_BASE}/cpu_rl_v10_ctrl_s0" \
  --seed 20261112 \
  --grpo_lr $GRPO_LR --n_grpo_steps $N_GRPO_STEPS --group_size 4 --batch_prompts 2 \
  --n_train 100 --n_eval_per_cat 16 \
  $CTRL_ARGS \
  >> "$LOG" 2>&1
echo "  -> control done at $(date)" >> "$LOG"

echo "=== v10 freqcmp ALL DONE at $(date) ===" >> "$LOG"
