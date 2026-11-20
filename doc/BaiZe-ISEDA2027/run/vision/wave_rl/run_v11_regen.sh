#!/bin/bash
# run_v11_regen.sh - v11 REGRESSION vs GENERATION three-arm comparison.
#
# WHY v11 (DIRECTION CHANGE after v6-v10 stalled; research-daily 2026-11-14 vision item):
#   Freqcmp direction saturated (v10 C=51.6% < B=54.9% NOT SIGNIFICANT). Per task guardrail
#   "连续 3 轮无提升必须换方向" (5 rounds v6-v10 no gain) + task-book rule "research-daily
#   相关条目 -> 纳入本轮计划", switch to PERIOD REGRESSION (original hard task, ~34% ceiling)
#   and test whether GENERATIVE approaches beat DIRECT regression.
#
# THREE ARMS (all SFT, fixed budget; NO GRPO since it failed in v2-v4/v6/v10):
#   Arm 1 "direct"    : SFT -> output period number directly.
#   Arm 2 "augment"   : Arm 1 + generative data augmentation (denser synthesized period grid).
#   Arm 3 "synthesis" : SFT -> output "type,freq"; period = 1/freq computed (analysis-by-synthesis).
#
# PRE-REGISTERED JUDGMENT (written BEFORE running, 2026-11-14 wake#1180):
#   Arm 1 (direct):    ~30-40%   (known SFT ceiling on period regression, per v2-v4)
#   Arm 2 (augment):   > Arm 1   IF generative augmentation supplies useful period coverage
#   Arm 3 (synthesis): > Arm 1   IF type+freq -> 1/freq is an easier representation
#   SUCCESS: >=1 generative arm beats Arm 1 by >=5pp, McNemar p<0.05, consistent across 3 seeds.
#   NEGATIVE (equally valuable): neither generative arm beats Arm 1 -> do not pursue generative
#            route this period; report why + next step.
#
# Model: Qwen3.5-2B (user-specified), LoRA r=16, GPU 5 (free A40 on .17; posttrain occupies 0-4,6,7).
# Generative component = PROGRAMMATIC waveform generator (full diffusion infeasible on budget;
#    documented as a principled lightweight proxy preserving the scientific question).
set -u
cd /nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export CUDA_VISIBLE_DEVICES=5
export OMP_NUM_THREADS=16
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LOG=/tmp/v11_regen.log
MODEL_PATH=/nas_data/app.e0031982/models/Qwen3.5-2B
OUT_BASE=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl/v11_results
SEEDS=(20261114 20261115 20261116)

echo "=== v11 regen started at $(date) ===" > "$LOG"
echo "  model=$MODEL_PATH  out_base=$OUT_BASE  seeds=${SEEDS[*]}" >> "$LOG"

# ---- Phase 0: Smoke test ----
echo "=== SMOKE TEST at $(date) ===" >> "$LOG"
python3 cpu_rl_v11_regen_experiment.py --mode smoke \
  --model_path "$MODEL_PATH" --out_dir "${OUT_BASE}/cpu_rl_v11_smoke" --seed 20261114 \
  >> "$LOG" 2>&1
echo "  smoke exit=$? at $(date)" >> "$LOG"

# ---- Phase 1: 3 seeds, standard ----
for s in "${SEEDS[@]}"; do
  echo "=== SEED $s at $(date) ===" >> "$LOG"
  python3 cpu_rl_v11_regen_experiment.py --mode standard \
    --model_path "$MODEL_PATH" --out_dir "${OUT_BASE}/cpu_rl_v11_std_s${s}" --seed $s \
    --n_base 400 --n_aug 400 --sft_epochs 5 --n_eval_per_cat 16 --batch_size 8 \
    >> "$LOG" 2>&1
  echo "  seed $s exit=$? at $(date)" >> "$LOG"
done

echo "=== v11 DONE at $(date) ===" >> "$LOG"
