#!/bin/bash
# ==============================================================================
# run_armD_r2_stage2_then_12bench.sh — auto-chain: wait for Stage-2 step3500
# checkpoint, then launch ④ 12-benchmark eval (operator instruction 2026-10-21 ④).
#
# Stage-2 (run_armD_r2_stage2_only.sh) writes step3500/projector.pt on success.
# This watcher polls for that file, then runs launch_12benchmarks_armD_r2_offline.sh
# (the /tmp-cache-fixed script that made ArmB 12/12 successful). After ④, ⑤ report
# is generated manually (report_vision_armD_r2_20261020_mllm_stage4_zh.html + §14).
#
# Launch (on .12):
#   setsid bash run_armD_r2_stage2_then_12bench.sh > /tmp/armD_r2_stage2_then_12bench.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
cd "$VISION_DIR"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

STAGE2_CKPT=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2_armD_r2_20261020/step3500/projector.pt
echo "============================================================"
echo "  ArmD-R2 auto-chain (Stage-2 -> ④12-set) started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Waiting for Stage-2 checkpoint: $STAGE2_CKPT"
echo "============================================================"

# Wait up to ~90 min for Stage-2 to finish (3500 steps @ ~2.35 steps/s ≈ 25 min; generous margin)
WAITED=0
while [ ! -f "$STAGE2_CKPT" ]; do
    if [ $WAITED -ge 5400 ]; then
        echo "[$(date '+%H:%M:%S')] ERROR: Stage-2 checkpoint not found after 90 min. ABORT auto-chain."
        echo "Last 20 lines of Stage-2 log:"
        tail -20 /tmp/armD_r2_stage2.log 2>&1
        exit 1
    fi
    # Abort early if Stage-2 process died and no checkpoint
    STAGE2_ALIVE=$(pgrep -f 'stage2_train_armD_r2.py' 2>/dev/null || true)
    if [ -z "$STAGE2_ALIVE" ] && [ ! -f "$STAGE2_CKPT" ]; then
        echo "[$(date '+%H:%M:%S')] ERROR: Stage-2 process exited but no checkpoint. ABORT."
        tail -30 /tmp/armD_r2_stage2.log 2>&1
        exit 1
    fi
    sleep 60
    WAITED=$((WAITED + 60))
    echo "[$(date '+%H:%M:%S')] Still waiting for Stage-2 (${WAITED}s elapsed)..."
done
echo "[$(date '+%H:%M:%S')] Stage-2 checkpoint found! Starting ④ 12-benchmark eval..."

# ============================================================
# PHASE ④: 12-benchmark eval (~1.5h)
# ============================================================
echo ""
echo "===== PHASE 4: 12-benchmark eval ($(date '+%H:%M:%S')) ====="
bash mllm_bridge/launch_12benchmarks_armD_r2_offline.sh
RC=$?
echo "[$(date '+%H:%M:%S')] 12-benchmark exit=$RC"
echo ""
echo "============================================================"
echo "  ArmD-R2 auto-chain ④ COMPLETE: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  12-set results: /nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armD_r2_20261020/"
echo "  Next (manual): ⑤ report_vision_armD_r2_20261020_mllm_stage4_zh.html + EXPERIMENTS_VISION.md §14"
echo "  CAVEAT: Stage-2 instruct data = original LLaVA-NeXT-780k quick-start subset"
echo "          (NOT opt47 738588) — report MUST annotate this data-version difference"
echo "          vs ArmB/ArmC. Encoder conclusions (ProtB) unaffected."
echo "============================================================"
exit $RC
