#!/usr/bin/env bash
# _pull_all_tb_images.sh — Pull all 89 Terminal-Bench task images via proxy.
#
# Docker daemon.json already has proxies configured (172.19.92.25:13128),
# verified working 2026-10-24.  This script pulls all missing alexgshaw/*
# images in batches of 5 to avoid disk I/O contention with running evals.
#
# Usage:  setsid sg docker -c "bash _pull_all_tb_images.sh" > /tmp/tb_pull_all.log 2>&1 &
set -uo pipefail

LOG="/tmp/tb_pull_all_images.log"
echo "[pull] started $(date '+%F %T')" | tee "$LOG"

BATCH=5
pulled=0
failed=0
skipped=0

for d in ~/terminal-bench/*/; do
    t=$(basename "$d")
    img="alexgshaw/${t}:20251031"

    # Skip if already present
    if docker image inspect "$img" >/dev/null 2>&1; then
        skipped=$((skipped + 1))
        continue
    fi

    echo "[pull] pulling $img ..." | tee -a "$LOG"
    if docker pull "$img" 2>&1 | tee -a "$LOG"; then
        pulled=$((pulled + 1))
        echo "[pull] OK  $img (pulled=$pulled failed=$failed skipped=$skipped)" | tee -a "$LOG"
    else
        failed=$((failed + 1))
        echo "[pull] FAIL $img (pulled=$pulled failed=$failed skipped=$skipped)" | tee -a "$LOG"
    fi

    # Throttle: every BATCH pulls, pause 2s to let disk settle
    if [ $(((pulled + failed) % BATCH)) -eq 0 ] && [ $((pulled + failed)) -gt 0 ]; then
        echo "[pull] batch pause 2s ..." | tee -a "$LOG"
        sleep 2
    fi
done

echo "[pull] DONE $(date '+%F %T')  pulled=$pulled failed=$failed skipped=$skipped" | tee -a "$LOG"

# Show total image count
total=$(docker images --filter "reference=alexgshaw/*" --format '{{.Repository}}' | sort -u | wc -l)
echo "[pull] Total alexgshaw/* images now: $total / 89" | tee -a "$LOG"
