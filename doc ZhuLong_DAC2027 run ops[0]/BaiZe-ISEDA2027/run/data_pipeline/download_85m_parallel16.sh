#!/usr/bin/env bash
# download_85m_parallel16.sh — Multi-file parallel download for 85M dataset
# Variant: hf_transfer DISABLED, HF_HUB_MAX_WORKERS=16 (16 files in parallel)
#
# Why: With hf_transfer=1, files download sequentially (1 at a time, multi-chunk).
#      Total throughput ~19 MB/s. Disabling hf_transfer + 16 workers may allow
#      16 simultaneous file downloads → potentially higher aggregate bandwidth.
#
# hf download is resumable: skips already-downloaded parquet + .metadata.
# Launch: setsid -f nohup bash download_85m_parallel16.sh > /tmp/85M_dl_parallel.log 2>&1 &

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_HUB_MAX_WORKERS=16

REPO="mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M"
LOCAL_DIR="/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 85M PARALLEL-16 download START ==="
echo "[$(date '+%H:%M:%S')] hf_transfer=0 max_workers=16"
echo "[$(date '+%H:%M:%S')] REPO=$REPO"
echo "[$(date '+%H:%M:%S')] LOCAL_DIR=$LOCAL_DIR"

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
    2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 85M download COMPLETE (attempt #${ATTEMPT}) ==="
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
