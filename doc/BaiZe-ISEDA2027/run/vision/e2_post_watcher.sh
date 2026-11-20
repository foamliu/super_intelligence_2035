#!/bin/bash
# e2_post_watcher.sh — waits for E2 full training to finish, then re-runs E1 Protocol A eval
# (which failed earlier due to sympy 1.5.1 incompatibility, now fixed with sympy 1.14.0)
# Created 2026-10-09
set -uo pipefail
cd "$(dirname "$0")"

LOG=/tmp/e2_post_watcher.log
E2_PID="${1:-}"

if [ -z "$E2_PID" ]; then
    echo "[$(date '+%F %T')] ERROR: must provide E2 training PID as argument" | tee "$LOG"
    exit 1
fi

echo "[$(date '+%F %T')] Post-E2 watcher started — waiting for E2 training (PID $E2_PID) to finish..." | tee "$LOG"

while kill -0 "$E2_PID" 2>/dev/null; do
    sleep 60
done
echo "[$(date '+%F %T')] E2 training (PID $E2_PID) has exited." | tee -a "$LOG"

sleep 30
echo "[$(date '+%F %T')] GPU buffer wait done." | tee -a "$LOG"

# Re-run E1 Protocol A eval (failed earlier due to sympy issue)
E1_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E1_ov2_w512_d30_p16_224
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

echo "[$(date '+%F %T')] Re-running E1 Protocol A eval (was failed by sympy 1.5.1, now fixed)..." | tee -a "$LOG"
"$PY" lp_protocol_bridge.py --ckpts "$E1_OUT/vision.pt" --protocol A 2>&1 | tee -a "$LOG"
echo "[$(date '+%F %T')] E1 Protocol A eval complete." | tee -a "$LOG"

# Check E2 eval results
E2_EVAL_LOG=/tmp/scaling_e2_eval.log
if [ -f "$E2_EVAL_LOG" ] && grep -q 'DONE' "$E2_EVAL_LOG"; then
    echo "[$(date '+%F %T')] E2 eval already done (found DONE in $E2_EVAL_LOG)." | tee -a "$LOG"
    grep -E 'lp_top1|SUMMARY|DONE' "$E2_EVAL_LOG" | tee -a "$LOG"
else
    echo "[$(date '+%F %T')] E2 eval NOT found. Running E2 eval..." | tee -a "$LOG"
    E2_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E2_ov2_w768_d30_p16_224
    "$PY" lp_protocol_bridge.py --ckpts "$E2_OUT/vision.pt" --protocol B --probe-full-train 2>&1 | tee -a "$LOG"
    "$PY" lp_protocol_bridge.py --ckpts "$E2_OUT/vision.pt" --protocol A 2>&1 | tee -a "$LOG"
fi

echo "[$(date '+%F %T')] Post-E2 watcher complete. All evals done." | tee -a "$LOG"
echo "[$(date '+%F %T')] Next: write HTML report + update EXPERIMENTS_VISION.md." | tee -a "$LOG"
