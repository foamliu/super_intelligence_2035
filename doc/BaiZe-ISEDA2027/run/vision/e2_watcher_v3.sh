#!/bin/bash
# e2_watcher_v3.sh — waits for E1 resume to finish, then runs E2 smoke + full training + eval
# Created 2026-10-09 (v3: eliminates redundant eval_final from v2)
#   v2 had eval_final which re-evaluated BOTH arms — but resume_e1 already evals E1,
#   and e2 mode already evals E2. v3 skips that, saving ~2-4h GPU time.
#   Safety net: if E1 eval log doesn't show DONE, run E1 eval only (not both).
# Pipeline: E1 resume (130k→187k) + E1 eval → E2 smoke (30 steps) → E2 full (1 epoch) + E2 eval
#           → [if E1 eval missing] E1 eval only
set -uo pipefail
cd "$(dirname "$0")"

LOG=/tmp/e2_watcher_v3.log
E1_RESUME_PID="${1:-}"

if [ -z "$E1_RESUME_PID" ]; then
    echo "[$(date '+%F %T')] ERROR: must provide E1 resume PID as argument" | tee "$LOG"
    exit 1
fi

echo "[$(date '+%F %T')] E2 watcher v3 started — waiting for E1 resume (PID $E1_RESUME_PID) to finish..." | tee "$LOG"

# Wait for E1 resume process to exit (includes E1 training + E1 eval by resume_e1 mode)
while kill -0 "$E1_RESUME_PID" 2>/dev/null; do
    sleep 60
done
echo "[$(date '+%F %T')] E1 resume (PID $E1_RESUME_PID) has exited." | tee -a "$LOG"

# Small buffer for GPU memory to release
sleep 30
echo "[$(date '+%F %T')] GPU buffer wait done. Checking GPU state..." | tee -a "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv | tee -a "$LOG"

# Step 1: E2 smoke test (30 steps) to measure throughput
echo "[$(date '+%F %T')] Starting E2 smoke test (w768/d30, 30 steps)..." | tee -a "$LOG"
bash run_scaling_experiment.sh smoke_e2 2>&1 | tee -a "$LOG"
SMOKE_RC=${PIPESTATUS[0]}
echo "[$(date '+%F %T')] E2 smoke exit code: $SMOKE_RC" | tee -a "$LOG"

# Report smoke throughput
grep -E 'image/s|params' /tmp/scaling_e2.log | tail -5 | tee -a "$LOG"

# Step 2: E2 full training (1 epoch) — e2 mode auto-evals E2 after training (Protocol B 3 seeds + Protocol A)
echo "[$(date '+%F %T')] Starting E2 full training (w768/d30, 1 epoch)..." | tee -a "$LOG"
bash run_scaling_experiment.sh e2 2>&1 | tee -a "$LOG"
E2_RC=${PIPESTATUS[0]}
echo "[$(date '+%F %T')] E2 training exit code: $E2_RC" | tee -a "$LOG"

# Step 3: Safety net — check if E1 was evaluated by resume_e1; if not, eval E1 only
E1_EVAL_LOG=/tmp/scaling_e1_eval.log
if [ -f "$E1_EVAL_LOG" ] && grep -q 'DONE' "$E1_EVAL_LOG"; then
    echo "[$(date '+%F %T')] E1 eval already done (found DONE in $E1_EVAL_LOG). Skipping re-eval." | tee -a "$LOG"
else
    echo "[$(date '+%F %T')] E1 eval NOT found or incomplete. Running E1 eval only (Protocol B 3 seeds + Protocol A)..." | tee -a "$LOG"
    E1_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E1_ov2_w512_d30_p16_224
    /nas_train/app.e0031982/miniforge3/envs/py310/bin/python lp_protocol_bridge.py \
        --ckpts "$E1_OUT/vision.pt" --protocol B --probe-full-train 2>&1 | tee -a "$LOG"
    /nas_train/app.e0031982/miniforge3/envs/py310/bin/python lp_protocol_bridge.py \
        --ckpts "$E1_OUT/vision.pt" --protocol A 2>&1 | tee -a "$LOG"
    echo "[$(date '+%F %T')] E1 eval complete." | tee -a "$LOG"
fi

echo "[$(date '+%F %T')] E2 watcher v3 complete. Both arms trained + evaluated." | tee -a "$LOG"
echo "[$(date '+%F %T')] Next steps: check /tmp/scaling_e1_eval.log + /tmp/scaling_e2_eval.log for results." | tee -a "$LOG"
echo "[$(date '+%F %T')] Then: write HTML report (report_vision_aimv2_scaling.html) + update EXPERIMENTS_VISION.md." | tee -a "$LOG"