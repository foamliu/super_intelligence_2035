#!/usr/bin/env bash
# _pull_tb4_images.sh — Pull all 132 Terminal-Bench 4.0 task images (66 tasks × 2: env + verifier)
#
# Images are from harborframework/terminal-bench on Docker Hub.
# Docker daemon.json already has proxies configured (172.19.92.25:13128).
# Docker Hub anonymous rate limit: 100 manifests/hour → batch with sleep.
#
# Usage:  setsid sg docker -c "bash _pull_tb4_images.sh" > /tmp/tb4_pull_all.log 2>&1 &
set -uo pipefail

LOG="/tmp/tb4_pull_all_images.log"
echo "[pull-tb4] started $(date '+%F %T')" | tee "$LOG"

BATCH=5
pulled=0
failed=0
skipped=0
count=0
total=132

# Extract all unique docker_image references from TB 4.0 task.toml files
mapfile -t IMAGES < <(grep -h 'docker_image' ~/terminal-bench-4.0/*/task.toml 2>/dev/null \
  | sed 's/.*= "//' | sed 's/"//' | sort -u)

echo "[pull-tb4] ${#IMAGES[@]} unique images to pull" | tee -a "$LOG"

for img in "${IMAGES[@]}"; do
  count=$((count + 1))

  # Skip if already present
  if docker image inspect "$img" >/dev/null 2>&1; then
    skipped=$((skipped + 1))
    echo "[pull-tb4] [$count/$total] SKIP (already present): $img" | tee -a "$LOG"
    continue
  fi

  echo "[pull-tb4] [$count/$total] pulling: $img" | tee -a "$LOG"
  if docker pull "$img" >>"$LOG" 2>&1; then
    pulled=$((pulled + 1))
    echo "[pull-tb4] [$count/$total] OK: $img" | tee -a "$LOG"
  else
    failed=$((failed + 1))
    echo "[pull-tb4] [$count/$total] FAIL: $img" | tee -a "$LOG"
  fi

  # Batch pause every BATCH images to respect Docker Hub rate limits
  if [ $((count % BATCH)) -eq 0 ]; then
    echo "[pull-tb4] batch pause 30s (rate limit caution)..." | tee -a "$LOG"
    sleep 30
  fi
done

echo "[pull-tb4] DONE $(date '+%F %T') | pulled=$pulled failed=$failed skipped=$skipped total=$total" | tee -a "$LOG"
