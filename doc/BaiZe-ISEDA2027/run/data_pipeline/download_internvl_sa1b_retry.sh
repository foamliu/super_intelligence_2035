#!/usr/bin/env bash
# download_internvl_sa1b_retry.sh — Retry-loop for hanlincs/InternVL-SA1B-Caption-WebDataset
# Dataset: hanlincs/InternVL-SA1B-Caption-WebDataset (2000 tar, ~1-1.5 TB, ~22.4M pairs, webdataset)
# Landing: /nas_user/app.e0031982/datasets/hanlincs/InternVL-SA1B-Caption-WebDataset/
#
# Launch: setsid -f nohup bash download_internvl_sa1b_retry.sh > /tmp/internvl_sa1b_dl.log 2>&1 &

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=1

REPO="hanlincs/InternVL-SA1B-Caption-WebDataset"
LOCAL_DIR="/nas_user/app.e0031982/datasets/hanlincs/InternVL-SA1B-Caption-WebDataset"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === InternVL-SA1B-Caption-WebDataset download retry-loop START ==="
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
    2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === InternVL-SA1B download COMPLETE (attempt #${ATTEMPT}) ==="
    FINAL_TAR=$(find "$LOCAL_DIR" -name '*.tar' 2>/dev/null | wc -l)
    FINAL_SIZE=$(du -sh "$LOCAL_DIR" 2>/dev/null | cut -f1)
    echo "[$(date '+%H:%M:%S')] FINAL: ${FINAL_TAR} tar files, ${FINAL_SIZE} total"
    break
  else
    EXIT_CODE=$?
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Attempt #${ATTEMPT} FAILED (exit=$EXIT_CODE) ---"
    echo "[$(date '+%H:%M:%S')] Retrying in 30s..."
    sleep 30
  fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === InternVL-SA1B download retry-loop EXIT ==="
