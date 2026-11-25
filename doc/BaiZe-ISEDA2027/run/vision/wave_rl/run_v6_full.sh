#!/bin/bash
# run_v6_full.sh - Launch v6 GRPO full experiment in background
# Full run: 40 GRPO steps, group_size=8, batch_prompts=2, 200 train Qs, 100 eval Qs
# Estimated time: ~1.5-2 hours on CPU
set -e
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export OMP_NUM_THREADS=16
LOG=/tmp/v6_full.log
OUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v6_grpo

echo "=== v6 FULL experiment started at $(date) ===" > "$LOG"
echo "Output dir: $OUT_DIR" >> "$LOG"
echo "Params: 40 steps, group_size=8, batch_prompts=2, 200 train, 100 eval" >> "$LOG"

nice -n 19 python3 cpu_rl_v6_grpo_experiment.py \
    --out_dir "$OUT_DIR" \
    --n_grpo_steps 40 \
    --group_size 8 \
    --batch_prompts 2 \
    --n_train 200 \
    --n_eval_per_type 25 \
    --lr 1e-6 \
    --temperature 0.8 \
    --clip_eps 0.2 \
    --seed 20261109 \
    >> "$LOG" 2>&1

echo "=== v6 FULL experiment finished at $(date) ===" >> "$LOG"
