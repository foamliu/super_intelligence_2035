#!/bin/bash
# S3 long-horizon training: extend the winner (OpenVision2) + runner-up (DeepEncoderV2)
# to 5k-10k steps, plus MambaEye/MoE-ViE at 5000 for loss-rank stability check.
# Same default config as S1 (en500k, batch32x6, seed1234, SigLIP), only steps differ.
# Run ON 10.239.2.12 (GPU 0-5 free).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/s3_main.log

echo "===== S3 long-horizon START $(date '+%F %T') =====" | tee "$LOG"

# tower -> steps (winner gets longest horizon)
run_one () {
    local TOWER="$1"; local STEPS="$2"
    echo "===== S3 $TOWER ($STEPS steps) =====" | tee -a "$LOG"
    bash run_train.sh "$TOWER" "$STEPS" "$OUTROOT/S3_$TOWER" \
        --data "$DATA" --batch-size 32 --log-every 50 --seed 1234 \
        2>&1 | grep -vE 'warning|Warning|import pynvml|OMP_NUM_THREADS|\*\*\*\*|FutureWarning|warnings\.warn' \
        | tee -a "$LOG"
    echo "===== S3 $TOWER done (exit ${PIPESTATUS[0]}) =====" | tee -a "$LOG"
}

run_one openvision2 10000
run_one deepencoder_v2 5000
run_one mambaeye 5000
run_one moevie 5000

echo "===== S3 ALL DONE =====" | tee -a "$LOG"