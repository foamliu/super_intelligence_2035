#!/usr/bin/env bash
# _retry_pull_tb_images.sh — Retry pulling all still-missing TB images.
#
# The first pull run (_pull_all_tb_images.sh) had 28 failures due to a
# transient auth.docker.io "Service Unavailable" outage.  This script
# retries all still-missing images with up to 3 attempts each, with a
# 30s delay between retries to let auth.docker.io recover.
#
# Usage:  setsid sg docker -c "bash _retry_pull_tb_images.sh" > /tmp/tb_retry_pull.log 2>&1 &
set -uo pipefail

LOG="/tmp/tb_retry_pull_images.log"
echo "[retry] started $(date '+%F %T')" | tee "$LOG"

MAX_RETRIES=3
RETRY_DELAY=30  # seconds between retries

pulled=0
failed=0
skipped=0
still_missing=0

for d in ~/terminal-bench/*/; do
    t=$(basename "$d")
    img="alexgshaw/${t}:20251031"

    # Skip if already present
    if docker image inspect "$img" >/dev/null 2>&1; then
        skipped=$((skipped + 1))
        continue
    fi

    success=false
    for attempt in $(seq 1 $MAX_RETRIES); do
        echo "[retry] ($attempt/$MAX_RETRIES) pulling $img ..." | tee -a "$LOG"
        if docker pull "$img" 2>&1 | tee -a "$LOG"; then
            success=true
            break
        fi
        echo "[retry] ($attempt/$MAX_RETRIES) FAIL $img" | tee -a "$LOG"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "[retry] waiting ${RETRY_DELAY}s before next attempt ..." | tee -a "$LOG"
            sleep $RETRY_DELAY
        fi
    done

    if $success; then
        pulled=$((pulled + 1))
        echo "[retry] OK  $img (pulled=$pulled failed=$failed skipped=$skipped)" | tee -a "$LOG"
    else
        failed=$((failed + 1))
        still_missing=$((still_missing + 1))
        echo "[retry] GIVEUP $img after $MAX_RETRIES attempts (pulled=$pulled failed=$failed skipped=$skipped)" | tee -a "$LOG"
    fi

    # Small pause between different images
    sleep 2
done

echo "[retry] DONE $(date '+%F %T')  pulled=$pulled failed=$failed skipped=$skipped" | tee -a "$LOG"

# Show total image count
total=$(docker images --filter "reference=alexgshaw/*" --format '{{.Repository}}' | sort -u | wc -l)
echo "[retry] Total alexgshaw/* images now: $total / 89" | tee -a "$LOG"

if [ $still_missing -gt 0 ]; then
    echo "[retry] ⚠️  $still_missing images still missing after retries" | tee -a "$LOG"
    echo "[retry] Still missing:" | tee -a "$LOG"
    for d in ~/terminal-bench/*/; do
        t=$(basename "$d")
        img="alexgshaw/${t}:20251031"
        if ! docker image inspect "$img" >/dev/null 2>&1; then
            echo "  - $img" | tee -a "$LOG"
        fi
    done
fi
