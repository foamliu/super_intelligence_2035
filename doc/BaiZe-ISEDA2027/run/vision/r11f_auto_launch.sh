#!/bin/bash
# R11-F auto-launcher: wait for AIMv2 training to finish, run its (orphaned) eval,
# then launch R11-F data-source comparison when GPU is free.
# Created 2026-10-04 because r11_run_aimv2.sh parent process died (workers orphaned,
# ppid=1) -> auto-eval would not run. This wrapper picks up that responsibility.
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/r11f_wait_launch.log
AIMV2_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/R11L_aimv2_w512
AIMV2_LOG=/tmp/r11_aimv2.log

echo "===== R11-F auto-launcher START $(date '+%F %T') =====" > "$LOG"

# 1. Wait for AIMv2 training (8 r9_train.py workers) to finish
while pgrep -f 'r9_train.*aimv2' > /dev/null 2>&1; do
    echo "[$(date '+%T')] AIMv2 training still running, waiting..." >> "$LOG"
    sleep 120
done
echo "[$(date '+%T')] AIMv2 training done." >> "$LOG"

# 2. Run AIMv2 4-ckpt IN-1k eval (parent script is gone, so do it manually)
#    Check if eval was already done (look for IN-1k results in log)
if grep -q 'IN-1k' "$AIMV2_LOG" 2>/dev/null && grep -q 'lp' "$AIMV2_LOG" 2>/dev/null; then
    echo "[$(date '+%T')] AIMv2 eval may already have results in log, skipping" >> "$LOG"
else
    CKPTS=()
    for f in "$AIMV2_OUT"/vision_step10000.pt "$AIMV2_OUT"/vision_step20000.pt "$AIMV2_OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$AIMV2_OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$AIMV2_OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] final ckpt" >> "$LOG"
    echo "[$(date '+%T')] Running AIMv2 IN-1k eval on ${#CKPTS[@]} ckpts" >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        CUDA_VISIBLE_DEVICES=0 "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$AIMV2_LOG" 2>&1
        echo "[$(date '+%T')] AIMv2 eval done (exit $?)" >> "$LOG"
    fi
fi

# 3. Wait for GPU to be fully free (no compute processes)
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date '+%T')] GPU still has processes, waiting..." >> "$LOG"
    sleep 30
done
echo "[$(date '+%T')] GPU free." >> "$LOG"

# 4. Launch R11-F (5 arms serial: A→B→C→E→D, 30k steps each + auto 4-ckpt eval)
echo "[$(date '+%T')] Launching R11-F data-source comparison (5 arms)" >> "$LOG"
bash r11_run_datasource.sh 30000 6 >> "$LOG" 2>&1
echo "===== R11-F auto-launcher DONE $(date '+%F %T') =====" >> "$LOG"
