#!/usr/bin/env bash
# pull_all_images.sh — Download SWE-bench Multimodal evaluation containers
# User order 2026-11-18: download SWE-bench Multimodal eval containers in parallel
# with continuing SWE-bench Verified evaluation.
# Constraint: nice19/ionice3, don't compete with pretrain on .29 CPU.
# Strategy: pull images SEQUENTIALLY (1 at a time) to minimize CPU/IO pressure.
#           dockerd does the decompression; sequential pulls limit concurrent CPU use.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
IMAGE_LIST="$HERE/swebench_mm_image_list.txt"
LOG_FILE="$HERE/pull_progress.log"
STATE_FILE="$HERE/pull_state.txt"   # tracks current index for resume
MAX_RETRIES=3
RETRY_DELAY=10

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

total=$(wc -l < "$IMAGE_LIST")
log "=== SWE-bench Multimodal container download START ==="
log "Total images to pull: $total"
log "Strategy: sequential (1 at a time), nice19/ionice3"

# Resume from state file if present
start_idx=1
if [[ -f "$STATE_FILE" ]]; then
    last_done=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
    if [[ "$last_done" =~ ^[0-9]+$ ]] && [[ "$last_done" -gt 0 ]]; then
        start_idx=$((last_done + 1))
        log "Resuming from index $start_idx (last completed: $last_done)"
    fi
fi

success_count=0
skip_count=0
fail_count=0
fail_list=()

idx=0
while IFS=$'\t' read -r instance_id repo image; do
    idx=$((idx + 1))
    if [[ "$idx" -lt "$start_idx" ]]; then
        continue
    fi

    # Check if already pulled
    if docker image inspect "$image" >/dev/null 2>&1; then
        skip_count=$((skip_count + 1))
        log "[$idx/$total] SKIP (already present): $instance_id"
        echo "$idx" > "$STATE_FILE"
        continue
    fi

    log "[$idx/$total] PULL: $instance_id -> $image"

    pulled=false
    for attempt in $(seq 1 $MAX_RETRIES); do
        # nice19 + ionice3 on the docker pull client; sequential = low CPU pressure
        if nice -n 19 ionice -c 3 docker pull "$image" >>"$LOG_FILE" 2>&1; then
            pulled=true
            break
        fi
        log "  attempt $attempt failed, retrying in ${RETRY_DELAY}s..."
        sleep "$RETRY_DELAY"
    done

    if $pulled; then
        success_count=$((success_count + 1))
        log "[$idx/$total] OK: $instance_id (pulled)"
    else
        fail_count=$((fail_count + 1))
        fail_list+=("$instance_id")
        log "[$idx/$total] FAILED after $MAX_RETRIES attempts: $instance_id"
    fi

    echo "$idx" > "$STATE_FILE"

    # Progress summary every 20 images
    if [[ $((idx % 20)) -eq 0 ]]; then
        log "  --- progress: $idx/$total | ok=$success_count skip=$skip_count fail=$fail_count ---"
    fi
done < "$IMAGE_LIST"

log "=== DOWNLOAD COMPLETE ==="
log "Total: $total | Pulled: $success_count | Skipped: $skip_count | Failed: $fail_count"
if [[ ${#fail_list[@]} -gt 0 ]]; then
    log "Failed images:"
    for f in "${fail_list[@]}"; do
        log "  - $f"
    done
fi
log "=== END ==="
