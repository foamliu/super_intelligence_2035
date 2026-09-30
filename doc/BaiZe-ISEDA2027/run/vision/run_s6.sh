#!/bin/bash
# S6 resolution/patch ablation on the winner (OpenVision2), single-variable vs anchor 224/16.
# Each 1000 steps. NOTE: 448/14 attention is ~5.2x seq len -> may OOM at batch32 on 80GB;
# if OOM, retry that combo with --batch-size 16 (record as non-comparable throughput).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

for cfg in "336 16" "448 16" "224 14" "336 14" "448 14"; do
    set -- $cfg
    RES="$1"; PATCH="$2"
    OUT="$OUTROOT/S6_ov2_r${RES}_p${PATCH}"
    echo "===== S6 openvision2 res=$RES patch=$PATCH ====="
    bash run_train.sh openvision2 3000 "$OUT" --data "$DATA" --batch-size 32 \
        --log-every 50 --resolution "$RES" --patch "$PATCH" \
        2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn'
    echo "===== S6 ov2 r${RES} p${PATCH} done (exit ${PIPESTATUS[0]}) ====="
done
echo "===== S6 ALL DONE ====="