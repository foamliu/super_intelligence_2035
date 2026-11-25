#!/bin/bash
# run_lp_protocol_bridge.sh — Convenience wrapper for lp_protocol_bridge.py
#
# Runs the A/B protocol bridging evaluation on specified checkpoints.
# MUST be run AFTER R12b training finishes (GPU + heavy I/O for full-train mode).
#
# Usage:
#   bash run_lp_protocol_bridge.sh          # default: both protocols, 200/class
#   bash run_lp_protocol_bridge.sh full      # B group with full IN-1k train (1.28M)
#   bash run_lp_protocol_bridge.sh A_only    # only BaiZe protocol
#   bash run_lp_protocol_bridge.sh B_only    # only mainstream protocol
#
# Prerequisites:
#   conda activate py310
#   cd doc/BaiZe-ISEDA2027/run/vision
#   R12b training must be FINISHED (check: tail /tmp/r12b_fulldata_aimv2.log)

set -euo pipefail

OUT=/nas_train/app.e0031982/datasets/baize-vision/out
MODE="${1:-default}"

# Checkpoints for the bridge study (operator suggested: R12b final + R12 3-epoch + 臂⑥ AIMv2)
# R12b final will be available when training completes.
# R12 vision.pt = 120k step (1 epoch); the 3-epoch continue = lp 20.27%
R12B_FINAL="${OUT}/R12b_fulldata_aimv2_w512/vision.pt"
R12_1EPOCH="${OUT}/R12_fulldata_aimv2_w512/vision.pt"
R11G_AIMV2="${OUT}/R11G_aimv2_long_w512/vision.pt"    # 108k AIMv2 long run
R11L_AIMV2="${OUT}/R11L_aimv2_w512/vision.pt"          # 臂⑥ AIMv2

# Build ckpt list (only include files that exist)
CKPTS=()
for c in "$R12B_FINAL" "$R12_1EPOCH" "$R11G_AIMV2"; do
    if [ -f "$c" ]; then
        CKPTS+=("$c")
    else
        echo "[WARN] ckpt not found (skipping): $c"
    fi
done

if [ ${#CKPTS[@]} -eq 0 ]; then
    echo "[ERROR] No checkpoints found. R12b may still be training."
    echo "  Check: tail /tmp/r12b_fulldata_aimv2.log"
    exit 1
fi

echo "[run_bridge] ckpts: ${CKPTS[*]}"
echo "[run_bridge] mode: $MODE"

case "$MODE" in
    full)
        echo "[run_bridge] B group with FULL IN-1k train (1.28M) — heavy I/O!"
        PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
        python lp_protocol_bridge.py --ckpts "${CKPTS[@]}" --protocol both \
            --probe-full-train --repeats 3 --gpu 0 \
            2>&1 | tee /tmp/lp_bridge_full.log
        ;;
    A_only)
        echo "[run_bridge] Only Protocol A (BaiZe)"
        python lp_protocol_bridge.py --ckpts "${CKPTS[@]}" --protocol A \
            --gpu 0 2>&1 | tee /tmp/lp_bridge_A.log
        ;;
    B_only)
        echo "[run_bridge] Only Protocol B (mainstream, 200/class)"
        python lp_protocol_bridge.py --ckpts "${CKPTS[@]}" --protocol B \
            --probe-per-class 200 --repeats 3 --gpu 0 \
            2>&1 | tee /tmp/lp_bridge_B.log
        ;;
    default|*)
        echo "[run_bridge] Both protocols, B with 200/class subset"
        python lp_protocol_bridge.py --ckpts "${CKPTS[@]}" --protocol both \
            --probe-per-class 200 --repeats 3 --gpu 0 \
            2>&1 | tee /tmp/lp_bridge_default.log
        ;;
esac

echo "[run_bridge] DONE. Log saved to /tmp/lp_bridge_*.log"
