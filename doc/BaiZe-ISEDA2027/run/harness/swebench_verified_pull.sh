#!/bin/bash
# SWE-bench Verified -- Batch Docker image puller with rate limiting
# Pulls 500 swebench/sweb.eval.x86_64.* images in batches of 50.
# Idempotent: docker pull is naturally resumable.
# Progress: doc/BaiZe-ISEDA2027/run/harness/swebench_verified_pull_progress.txt
#
# Usage:  bash swebench_verified_pull.sh
# The script uses 'sg docker' for docker access and the daemon.json proxy.

set -euo pipefail

HARNESS_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness"
IMAGES_FILE="/tmp/swebench_verified_images.json"
PROGRESS_FILE="$HARNESS_DIR/swebench_verified_pull_progress.txt"
BATCH_SIZE=50
MAX_RETRIES=2
DOCKER_ROOT="/data/docker"

# Read image list (JSON array)
mapfile -t ALL_IMAGES < <(python3 -c "import json; [print(i) for i in json.load(open('$IMAGES_FILE'))]")
TOTAL=${#ALL_IMAGES[@]}

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SWE-bench Verified image pull started. Total=$TOTAL" | tee "$PROGRESS_FILE"
echo "Batch size=$BATCH_SIZE, Max retries=$MAX_RETRIES" | tee -a "$PROGRESS_FILE"

PULLED=0
FAILED_LIST=()
CUMULATIVE_GB=0
BATCH_NUM=0

for ((i=0; i<TOTAL; i+=BATCH_SIZE)); do
    BATCH_NUM=$((BATCH_NUM + 1))
    END=$((i + BATCH_SIZE))
    [ $END -gt $TOTAL ] && END=$TOTAL
    
    echo "" | tee -a "$PROGRESS_FILE"
    echo "[$(date '+%H:%M:%S')] Batch $BATCH_NUM: images $((i+1))-$END / $TOTAL" | tee -a "$PROGRESS_FILE"
    
    for ((j=i; j<END; j++)); do
        IMG="${ALL_IMAGES[$j]}"
        SUCCESS=false
        
        for attempt in $(seq 1 $((MAX_RETRIES + 1))); do
            if sg docker -c "docker pull '$IMG' > /tmp/_pull_output.txt 2>&1"; then
                SUCCESS=true
                # Get image size
                SIZE=$(sg docker -c "docker image inspect '$IMG' --format '{{.Size}}' 2>/dev/null" || echo "0")
                SIZE_GB=$(python3 -c "print(f'{$SIZE / 1e9:.2f}')" 2>/dev/null || echo "?")
                CUMULATIVE_GB=$(python3 -c "print($CUMULATIVE_GB + $SIZE / 1e9)" 2>/dev/null || echo "$CUMULATIVE_GB")
                PULLED=$((PULLED + 1))
                echo "  [OK] $IMG (${SIZE_GB}GB) - attempt $attempt" | tee -a "$PROGRESS_FILE"
                break
            else
                ERR=$(tail -3 /tmp/_pull_output.txt 2>/dev/null | tr '\n' ' ' | head -c 200)
                echo "  [FAIL attempt $attempt] $IMG: $ERR" | tee -a "$PROGRESS_FILE"
                sleep 5
            fi
        done
        
        if [ "$SUCCESS" = false ]; then
            FAILED_LIST+=("$IMG")
            echo "  [GIVE UP] $IMG after $((MAX_RETRIES + 1)) attempts" | tee -a "$PROGRESS_FILE"
        fi
    done
    
    # Batch checkpoint: disk check
    DISK_FREE=$(df -BG /data | tail -1 | awk '{print $4}' | tr -d 'G')
    echo "[$(date '+%H:%M:%S')] Batch $BATCH_NUM done. Pulled=$PULLED/$TOTAL, Failed=${#FAILED_LIST[@]}, Disk free=${DISK_FREE}G, Cumulative=${CUMULATIVE_GB}GB" | tee -a "$PROGRESS_FILE"
    
    # Safety: stop if disk < 100GB
    if [ "$DISK_FREE" -lt 100 ]; then
        echo "[WARNING] Disk below 100GB, stopping!" | tee -a "$PROGRESS_FILE"
        break
    fi
    
    # Brief pause between batches to let TB breathe
    sleep 10
done

echo "" | tee -a "$PROGRESS_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PULL COMPLETE" | tee -a "$PROGRESS_FILE"
echo "  Pulled: $PULLED / $TOTAL" | tee -a "$PROGRESS_FILE"
echo "  Failed: ${#FAILED_LIST[@]}" | tee -a "$PROGRESS_FILE"
if [ ${#FAILED_LIST[@]} -gt 0 ]; then
    echo "  Failed images:" | tee -a "$PROGRESS_FILE"
    for f in "${FAILED_LIST[@]}"; do
        echo "    $f" | tee -a "$PROGRESS_FILE"
    done
fi
echo "  Cumulative pulled: ${CUMULATIVE_GB}GB" | tee -a "$PROGRESS_FILE"
