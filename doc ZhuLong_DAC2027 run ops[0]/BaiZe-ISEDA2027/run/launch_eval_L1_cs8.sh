#!/usr/bin/env bash
# Launch L1 final ckpt CS8-only eval on .29 (8×H100, all 8 GPUs) — properly detached.
# Usage: bash launch_eval_L1_cs8.sh  (run from run/ dir)
set -u
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
MODEL=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_L1_20b/final
OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/eval_L1_20b_cs8
LABEL=L1_20b_final_cs8
LOG=/tmp/eval_L1_20b_cs8.log

cd "$RUN_DIR"
nohup bash baize_xmodel_eval_cs8only.sh "$MODEL" "$OUT" "$LABEL" 0,1,2,3,4,5,6,7 8 > "$LOG" 2>&1 &
echo "EVAL_PID=$!"
echo "LOG=$LOG"
echo "OUT=$OUT"