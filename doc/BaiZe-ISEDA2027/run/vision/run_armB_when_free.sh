#!/bin/bash
# ==============================================================================
# run_armB_when_free.sh — Poll .12 GPU until free, then launch ArmB training.
#
# Operator instruction 2026-10-17: ".29 不可用 => 写 run_armB_when_free.sh:
#   每 5min 轮询 .12 8 卡 (无 compute apps 且每卡显存 >70GB) -> 满足即起训"
#
# NOTE: As of 2026-10-17 12:2x, .12 is already free (pretrain migrated to .29).
#       This script is provided per instruction requirement; if GPUs are already
#       free it launches immediately.
#
# Usage:
#   setsid bash run_armB_when_free.sh > /tmp/armB_when_free.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

POLL_INTERVAL=300  # 5 minutes
MIN_FREE_MEM_MIB=70000  # 70 GB free per card

echo "[armB-wait] $(date '+%F %T') polling .12 8xH100 every ${POLL_INTERVAL}s"

while true; do
    # Check all 8 GPUs: no compute apps + sufficient free memory
    GPU_OK=true
    COMPUTE=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
    if [ "$COMPUTE" -gt 0 ]; then
        GPU_OK=false
    else
        # Check free memory on each GPU
        while IFS=, read -r idx mem_used mem_total; do
            free=$((mem_total - mem_used))
            if [ "$free" -lt "$MIN_FREE_MEM_MIB" ]; then
                GPU_OK=false
                break
            fi
        done < <(nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null)
    fi

    if [ "$GPU_OK" = "true" ]; then
        echo "[armB-wait] $(date '+%F %T') .12 8 cards free — launching ArmB"
        nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv
        exec bash run_armB_openclip.sh
    fi

    echo "[armB-wait] $(date '+%F %T') GPUs busy (compute_apps=$COMPUTE), sleeping ${POLL_INTERVAL}s"
    sleep "$POLL_INTERVAL"
done
