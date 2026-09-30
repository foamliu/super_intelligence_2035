#!/bin/bash
# S7 objective-function ablation (P2): SigLIP vs CLIP InfoNCE on the winner (OpenVision2).
# Single-variable vs anchor (224/16, SigLIP, en500k, batch32x6, seed1234, 1000 steps).
# GPIC caption granularity / dataset scale / ZH-EN ratio are follow-ups (deferred if budget tight).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

for loss in siglip clip; do
    OUT="$OUTROOT/S7_ov2_${loss}"
    echo "===== S7 openvision2 loss=$loss ====="
    bash run_train.sh openvision2 1000 "$OUT" --data "$DATA" --batch-size 32 \
        --log-every 25 --loss "$loss" \
        2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn'
    echo "===== S7 ov2 loss=$loss done (exit ${PIPESTATUS[0]}) ====="
done
echo "===== S7 ALL DONE ====="