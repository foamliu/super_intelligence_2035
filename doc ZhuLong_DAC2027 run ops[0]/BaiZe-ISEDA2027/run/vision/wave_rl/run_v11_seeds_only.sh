#!/bin/bash
# run_v11_seeds_only.sh - run only the 3 standard seeds (smoke already done).
set -u
cd /nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl
export CUDA_VISIBLE_DEVICES=5
export OMP_NUM_THREADS=16
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LOG=/tmp/v11_regen.log
MODEL_PATH=/nas_data/app.e0031982/models/Qwen3.5-2B
OUT_BASE=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl/v11_results
SEEDS=(20261114 20261115 20261116)

echo "=== v11 SEEDS-ONLY started at $(date) ===" >> "$LOG"
echo "  model=$MODEL_PATH  out_base=$OUT_BASE  seeds=${SEEDS[*]}  GPU=$CUDA_VISIBLE_DEVICES" >> "$LOG"

for s in "${SEEDS[@]}"; do
  echo "=== SEED $s START $(date) ===" >> "$LOG"
  python3 cpu_rl_v11_regen_experiment.py --mode standard \
    --model_path "$MODEL_PATH" --out_dir "${OUT_BASE}/cpu_rl_v11_std_s${s}" --seed $s \
    --n_base 400 --n_aug 400 --sft_epochs 5 --n_eval_per_cat 16 --batch_size 8 \
    >> "$LOG" 2>&1
  echo "  seed $s exit=$? at $(date)" >> "$LOG"
done
echo "=== v11 SEEDS-ONLY DONE at $(date) ===" >> "$LOG"
