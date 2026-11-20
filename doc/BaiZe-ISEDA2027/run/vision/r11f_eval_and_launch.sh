#!/bin/bash
# Wrapper: run AIMv2 4-ckpt IN-1k eval, then launch R11-F data-source comparison.
# Created 2026-10-04 because r11f_auto_launch.sh died before detecting training completion.
# Launch with: setsid bash r11f_eval_and_launch.sh &
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
AIMV2_OUT=/nas_train/app.e0031982/datasets/baize-vision/out/R11L_aimv2_w512
AIMV2_LOG=/tmp/r11_aimv2_eval.log
R11F_LOG=/tmp/r11f_datasource.log

echo "===== AIMv2 eval + R11-F launch START $(date '+%F %T') =====" > /tmp/r11f_wrapper.log

# 1. Run AIMv2 4-ckpt IN-1k eval (single GPU)
echo "[$(date '+%T')] Running AIMv2 4-ckpt IN-1k eval..." >> /tmp/r11f_wrapper.log
CKPTS=()
for f in "$AIMV2_OUT"/vision_step10000.pt "$AIMV2_OUT"/vision_step20000.pt "$AIMV2_OUT"/vision_step30000.pt; do
    [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> /tmp/r11f_wrapper.log
done
FINAL="$AIMV2_OUT/vision.pt"; [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] final" >> /tmp/r11f_wrapper.log
echo "[$(date '+%T')] Eval on ${#CKPTS[@]} ckpts: ${CKPTS[*]}" >> /tmp/r11f_wrapper.log

if [ "${#CKPTS[@]}" -gt 0 ]; then
    CUDA_VISIBLE_DEVICES=0 "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" > "$AIMV2_LOG" 2>&1
    echo "[$(date '+%T')] AIMv2 eval done (exit $?) -> $AIMV2_LOG" >> /tmp/r11f_wrapper.log
else
    echo "[$(date '+%T')] No ckpts found, skipping eval" >> /tmp/r11f_wrapper.log
fi

# 2. Wait a moment for GPU to fully release
sleep 5

# 3. Verify GPU is free
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date '+%T')] GPU still has processes, waiting..." >> /tmp/r11f_wrapper.log
    sleep 10
done
echo "[$(date '+%T')] GPU free, launching R11-F..." >> /tmp/r11f_wrapper.log

# 4. Launch R11-F (5 arms serial: A→B→C→E→D)
bash r11_run_datasource.sh 30000 6 >> "$R11F_LOG" 2>&1
echo "===== R11-F DONE (exit $?) $(date '+%F %T') =====" >> /tmp/r11f_wrapper.log
