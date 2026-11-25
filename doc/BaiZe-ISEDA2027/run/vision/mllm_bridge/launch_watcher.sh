#!/bin/bash
# Simple launcher for wait_precache_then_eval.sh — avoids tee broken pipe
# Usage: nohup bash mllm_bridge/launch_watcher.sh &
set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

LOG=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results/watcher.log

echo "============================================================" > "$LOG"
echo "  Watcher started: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG"
echo "============================================================" >> "$LOG"

# Source the watcher script but redirect all tee output
# The watcher script uses tee, so we just run it with output to the log
bash mllm_bridge/wait_precache_then_eval.sh >> "$LOG" 2>&1
echo "[launcher] Watcher exited with code $?" >> "$LOG"