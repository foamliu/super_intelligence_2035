#!/usr/bin/env bash
# download_85m_retry.sh — Retry-loop wrapper for 85M dataset download
# Dataset: mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M (46.66TB, 12124 files, 8 subsets)
#
# Why retry-loop: Proxy 503 / CDN jitter causes `hf download` to crash after
# exhausting its internal 5-retry backoff. This wrapper re-launches it
# automatically (sleep 30 between attempts) so it self-heals without
# manual intervention.
#
# hf download is resumable: it checks existing parquet + .metadata and
# only downloads missing/incomplete files. Killing + restarting does NOT
# re-download completed files.
#
# Launch: setsid -f nohup bash download_85m_retry.sh > /tmp/85M_dl.log 2>&1 &
# ppid will be 1 (daemonized via setsid).

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=1

REPO="mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M"
LOCAL_DIR="/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 85M download retry-loop START ==="
echo "[$(date '+%H:%M:%S')] REPO=$REPO"
echo "[$(date '+%H:%M:%S')] LOCAL_DIR=$LOCAL_DIR"
echo "[$(date '+%H:%M:%S')] PID=$$ PPID=$PPID"

ATTEMPT=0
while true; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Attempt #${ATTEMPT} ---"

  # Clean stale .incomplete files before each attempt (hf_transfer leaves them on crash)
  INCOMPLETE_COUNT=$(find "$LOCAL_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
  if [ "$INCOMPLETE_COUNT" -gt 0 ]; then
    echo "[$(date '+%H:%M:%S')] Cleaning $INCOMPLETE_COUNT stale .incomplete files..."
    find "$LOCAL_DIR" -name '*.incomplete' -delete 2>/dev/null
  fi

  # Run hf download (resumable — skips already-downloaded files)
  if hf download --repo-type dataset "$REPO" \
    --local-dir "$LOCAL_DIR" \
    2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 85M download COMPLETE (attempt #${ATTEMPT}) ==="
    # Final verification
    FINAL_PARQUET=$(find "$LOCAL_DIR" -name '*.parquet' 2>/dev/null | wc -l)
    FINAL_SIZE=$(du -sh "$LOCAL_DIR" 2>/dev/null | cut -f1)
    echo "[$(date '+%H:%M:%S')] FINAL: ${FINAL_PARQUET} parquet files, ${FINAL_SIZE} total"
    break
  else
    EXIT_CODE=$?
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Attempt #${ATTEMPT} FAILED (exit=$EXIT_CODE) ---"
    echo "[$(date '+%H:%M:%S')] Retrying in 30s..."
    sleep 30
  fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 85M download retry-loop EXIT ==="
