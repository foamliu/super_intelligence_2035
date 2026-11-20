#!/bin/bash
# S4 multi-seed: top-2 architectures x 3 seeds x 3000 steps (reproducibility / tie-break).
# NOTE: 3000 steps (not 1000) to stay out of the cosine-LR collapse artifact discovered in S3
# (1000-step cosine collapsed LR ~step700 -> all towers frozen at 6.7342). 3000 steps keeps
# lr ~7.7e-4 through step1000, reaching meaningful ~4.5-4.6 loss for cross-seed comparison.
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
        bash run_train.sh "$TOWER" 3000 "$OUT" --data "$DATA" --batch-size 32 \
            --log-every 50 --seed "$SEED" \
            2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn'
        echo "===== S4 $TOWER seed=$SEED done (exit ${PIPESTATUS[0]}) ====="
    done
done
echo "===== S4 ALL DONE ====="