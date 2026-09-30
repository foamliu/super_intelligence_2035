#!/bin/bash
# S1 main training: 4 architectures x 1000 steps (default config) on unified EN500k subset.
# Run sequentially (each uses 6 GPUs for comparable throughput).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
STEPS=1000

for TOWER in openvision2 mambaeye moevie deepencoder_v2; do
    echo "===== S1 $TOWER ($STEPS steps) ====="
    bash run_train.sh "$TOWER" "$STEPS" "$OUTROOT/S1_$TOWER" \
        --data "$DATA" --batch-size 32 --log-every 25 \
        2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*'
    echo "===== S1 $TOWER done (exit ${PIPESTATUS[0]}) ====="
done
echo "===== S1 ALL DONE ====="