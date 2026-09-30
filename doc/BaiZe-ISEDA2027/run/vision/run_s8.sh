#!/bin/bash
# S8 training-hparam ablation (P3): LR sweep on the winner (OpenVision2), then warmup档位.
# Single-variable vs anchor: lr=1e-3 -> {1e-3, 3e-3, 5e-3}; warmup=100 -> {50, 300} (optional).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

for lr in 1e-3 3e-3 5e-3; do
    OUT="$OUTROOT/S8_ov2_lr${lr}"
    echo "===== S8 openvision2 lr=$lr ====="
    bash run_train.sh openvision2 1000 "$OUT" --data "$DATA" --batch-size 32 \
        --log-every 25 --lr "$lr" \
        2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn'
    echo "===== S8 ov2 lr=$lr done (exit ${PIPESTATUS[0]}) ====="
done

# optional warmup档位 (uncomment / extend if GPU budget remains)
# for wp in 50 300; do
#     OUT="$OUTROOT/S8_ov2_wu${wp}"
#     echo "===== S8 openvision2 warmup=$wp ====="
#     bash run_train.sh openvision2 1000 "$OUT" --data "$DATA" --batch-size 32 \
#         --log-every 25 --warmup "$wp" \
#         2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn'
#     echo "===== S8 ov2 warmup=$wp done (exit ${PIPESTATUS[0]}) ====="
# done

echo "===== S8 ALL DONE ====="