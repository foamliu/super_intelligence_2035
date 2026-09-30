#!/bin/bash
# S2 inference benchmark: single-GPU forward, batch=1 (inference), bf16.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export CUDA_VISIBLE_DEVICES=0

echo "##### S2 inference benchmark (batch=1, bf16) #####"
for RES in 224 448; do
    echo "---- resolution=$RES ----"
    for TOWER in openvision2 mambaeye moevie deepencoder_v2; do
        python bench.py --tower "$TOWER" --resolution "$RES" --patch 16 --batch 1 2>/dev/null
    done
done
echo "##### S2 DONE #####"