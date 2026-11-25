#!/bin/bash
# run_v7_sweep.sh - Run v7 process reward lambda sweep + v7b LoRA probe
# Total: 18 runs (9 process_reward + 9 lora_probe)
# Estimated: ~6-7 hours on CPU
set -u
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/wave_rl

export OMP_NUM_THREADS=16
LOG=/tmp/v7_sweep.log
OUT_BASE=/nas_train/app.e0031982/datasets/baize-vision/out

echo "=== v7 sweep started at $(date) ===" > "$LOG"
SEEDS=(20261111 20261112 20261113)

# ---- v7: Process Reward lambda sweep (9 runs) ----
LAMBDAS=(0.03 0.1 0.2)
for LAMBDA in "${LAMBDAS[@]}"; do
  for i in 0 1 2; do
    SEED=${SEEDS[$i]}
    OUT_DIR="${OUT_BASE}/cpu_rl_v7_proc_lam${LAMBDA}_s${i}"
    echo "\n=== v7 process lambda=${LAMBDA} seed=${SEED} run $((i+1))/3 at $(date) ===" >> "$LOG"
    if [ $i -eq 0 ]; then
      # First seed: eval B for McNemar
      nice -n 19 python3 cpu_rl_v7_experiment.py \
        --mode process_reward \
        --out_dir "$OUT_DIR" \
        --lambda_process $LAMBDA \
        --seed $SEED \
        --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
        --n_train 100 --n_eval_per_type 12 \
        >> "$LOG" 2>&1
    else
      # Subsequent seeds: skip B eval
      nice -n 19 python3 cpu_rl_v7_experiment.py \
        --mode process_reward \
        --out_dir "$OUT_DIR" \
        --lambda_process $LAMBDA \
        --seed $SEED \
        --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
        --n_train 100 --n_eval_per_type 12 \
        --skip_baseline_eval \
        >> "$LOG" 2>&1
    fi
    echo "  -> done at $(date)" >> "$LOG"
  done
done

# ---- v7b: LoRA Capacity Probe (9 runs) ----
LORA_RS=(8 16 32)
for R in "${LORA_RS[@]}"; do
  for i in 0 1 2; do
    SEED=${SEEDS[$i]}
    OUT_DIR="${OUT_BASE}/cpu_rl_v7b_lora_r${R}_s${i}"
    echo "\n=== v7b lora_probe r=${R} seed=${SEED} run $((i+1))/3 at $(date) ===" >> "$LOG"
    if [ $i -eq 0 ]; then
      nice -n 19 python3 cpu_rl_v7_experiment.py \
        --mode lora_probe \
        --out_dir "$OUT_DIR" \
        --lora_r $R \
        --seed $SEED \
        --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
        --n_train 100 --n_eval_per_type 12 \
        >> "$LOG" 2>&1
    else
      nice -n 19 python3 cpu_rl_v7_experiment.py \
        --mode lora_probe \
        --out_dir "$OUT_DIR" \
        --lora_r $R \
        --seed $SEED \
        --n_grpo_steps 15 --group_size 4 --batch_prompts 2 \
        --n_train 100 --n_eval_per_type 12 \
        --skip_baseline_eval \
        >> "$LOG" 2>&1
    fi
    echo "  -> done at $(date)" >> "$LOG"
  done
done

echo "\n=== v7 sweep ALL DONE at $(date) ===" >> "$LOG"
