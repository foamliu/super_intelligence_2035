#!/usr/bin/env bash
# download_ultradata_rl2609_retry.sh — Retry-loop wrapper for openbmb/UltraData-RL-2609 download
# Dataset: openbmb/UltraData-RL-2609 (26 files: 20 jsonl + 4 metadata + 2 assets, gated=False)
#   - data/Code/ (12 jsonl), data/Knowledge/ (2 jsonl), data/Long_Context/ (2 jsonl), data/Math/ (4 jsonl)
# Landing: /nas_env/app.e0031982/datasets/openbmb/UltraData-RL-2609/
# User direct order 2026-10-15: verify SFT-2605 (already present) + download RL-2609 (missing)
#
# Launch: setsid -f nohup bash download_ultradata_rl2609_retry.sh > /tmp/ultradata_rl2609_dl.log 2>&1 &

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=1

REPO="openbmb/UltraData-RL-2609"
LOCAL_DIR="/nas_env/app.e0031982/datasets/openbmb/UltraData-RL-2609"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === UltraData-RL-2609 download retry-loop START ==="
echo "[$(date '+%H:%M:%S')] REPO=$REPO"
echo "[$(date '+%H:%M:%S')] LOCAL_DIR=$LOCAL_DIR"
echo "[$(date '+%H:%M:%S')] PID=$$ PPID=$PPID"

ATTEMPT=0
while true; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Attempt #${ATTEMPT} ---"

  INCOMPLETE_COUNT=$(find "$LOCAL_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
  if [ "$INCOMPLETE_COUNT" -gt 0 ]; then
    echo "[$(date '+%H:%M:%S')] Cleaning $INCOMPLETE_COUNT stale .incomplete files..."
    find "$LOCAL_DIR" -name '*.incomplete' -delete 2>/dev/null
  fi

  if hf download --repo-type dataset "$REPO" \
    --local-dir "$LOCAL_DIR" \
    --max-workers 4 \
    2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === UltraData-RL-2609 download COMPLETE (attempt #${ATTEMPT}) ==="
    FINAL_JSONL=$(find "$LOCAL_DIR" -name '*.jsonl' 2>/dev/null | wc -l)
    FINAL_SIZE=$(du -sh "$LOCAL_DIR" 2>/dev/null | cut -f1)
    echo "[$(date '+%H:%M:%S')] FINAL: ${FINAL_JSONL} jsonl files, ${FINAL_SIZE} total"
    break
  else
    EXIT_CODE=$?
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Attempt #${ATTEMPT} FAILED (exit=$EXIT_CODE) ---"
    echo "[$(date '+%H:%M:%S')] Retrying in 30s..."
    sleep 30
  fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === UltraData-RL-2609 download retry-loop EXIT ==="
