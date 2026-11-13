#!/usr/bin/env bash
# stackv3_full_download.sh — HuggingFaceCode/stack-v3-train 全量 train split 下载到 /nas_user
# 用户令 2026-11-13: 全量 ~15.9TB，已下载的 2TB(4600 parquet) 已 rsync 到 /nas_user，hf download 自动跳过
# 纪律: nice -n 19, --max-workers 2, 不挤 S1, 走代理, /nas_user 余量红线 >=5T
set -uo pipefail

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export HTTPS_PROXY="http://172.19.92.25:13128"
export https_proxy="$HTTPS_PROXY"
export HTTP_PROXY="$HTTPS_PROXY"
export http_proxy="$HTTPS_PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0

REPO="HuggingFaceCode/stack-v3-train"
BASE="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
LOG="/tmp/stackv3_full_download.log"
PROGRESS_LOG="/tmp/stackv3_full_download_progress.log"

echo "==== stack-v3-train FULL download start $(date '+%Y%m%d_%H%M%S') ====" | tee "$LOG"
echo "  target: $BASE" | tee -a "$LOG"
echo "  repo: $REPO (dataset, train split only)" | tee -a "$LOG"
echo "  nice=19, max-workers=2, proxy=172.19.92.25:13128" | tee -a "$LOG"

# Record pre-download state
echo "" | tee -a "$LOG"
echo "Pre-download state:" | tee -a "$LOG"
EXISTING_PARQUETS=$(find "$BASE/data" -name '*.parquet' -type f 2>/dev/null | wc -l)
echo "  existing parquet files: $EXISTING_PARQUETS" | tee -a "$LOG"
EXISTING_BYTES=$(du -sb "$BASE" 2>/dev/null | cut -f1)
echo "  existing bytes: $EXISTING_BYTES" | tee -a "$LOG"
df -h /nas_user | tee -a "$LOG"

# Start the full download (hf download will skip already-existing files)
echo "" | tee -a "$LOG"
echo "Starting hf download..." | tee -a "$LOG"

nice -n 19 hf download "$REPO" \
    --repo-type dataset \
    --local-dir "$BASE" \
    --max-workers 2 \
    >> "$LOG" 2>&1

RC=$?
echo "" | tee -a "$LOG"
echo "==== FULL download FINISH $(date '+%Y%m%d_%H%M%S') rc=$RC ====" | tee -a "$LOG"

# Post-download state
TOTAL_PARQUETS=$(find "$BASE/data" -name '*.parquet' -type f 2>/dev/null | wc -l)
TOTAL_BYTES=$(du -sb "$BASE" 2>/dev/null | cut -f1)
TOTAL_INCS=$(find "$BASE" -name '*.incomplete' 2>/dev/null | wc -l)
echo "  total parquet files: $TOTAL_PARQUETS" | tee -a "$LOG"
echo "  total bytes: $TOTAL_BYTES" | tee -a "$LOG"
echo "  incomplete files: $TOTAL_INCS" | tee -a "$LOG"
df -h /nas_user | tee -a "$LOG"
