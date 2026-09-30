#!/bin/bash
# S4 multi-seed: top-2 architectures x 3 seeds x 1000 steps (reproducibility / tie-break).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

TOWERS=(openvision2 deepencoder_v2)
SEEDS=(1234 42 7)

for TOWER in "${TOWERS[@]}"; do
    for SEED in "${SEEDS[@]}"; do
        OUT="$OUTROOT/S4_${TOWER}_s${SEED}"
        echo "===== S4 $TOWER seed=$SEED ====="
        bash run_train.sh "$TOWER" 1000 "$OUT" --data "$DATA" --batch-size 32 \
            --log-every 25 --seed "$SEED" \
            2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn'
        echo "===== S4 $TOWER seed=$SEED done (exit ${PIPESTATUS[0]}) ====="
    done
done
echo "===== S4 ALL DONE ====="