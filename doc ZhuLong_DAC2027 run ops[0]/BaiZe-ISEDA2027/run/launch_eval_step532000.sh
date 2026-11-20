#!/usr/bin/env bash
# Launch step_532000 baseline eval on .29 — properly detached
set -u
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
MODEL=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_history/step_532000
OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/eval_step532000_baseline
LABEL=step532000_baseline
LOG=/tmp/eval_step532000_baseline.log

cd "$RUN_DIR"
nohup bash baize_xmodel_eval.sh "$MODEL" "$OUT" "$LABEL" 0,1,2,3,4,5,6,7 8 > "$LOG" 2>&1 &
echo "EVAL_PID=$!"
echo "LOG=$LOG"
