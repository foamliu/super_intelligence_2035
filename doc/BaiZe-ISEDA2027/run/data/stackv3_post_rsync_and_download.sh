#!/usr/bin/env bash
# stackv3_post_rsync_and_download.sh
# Waits for rsync to finish, verifies byte match, deletes source, starts full download
# 用户令 2026-11-13: 全量 stack-v3-train 下载到 /nas_user
set -uo pipefail

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export HTTPS_PROXY="http://172.19.92.25:13128"
export https_proxy="$HTTPS_PROXY"
export HTTP_PROXY="$HTTPS_PROXY"
export http_proxy="$HTTPS_PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0

SRC="/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
DST="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
RYSNC_PID=3750248
LOG="/tmp/stackv3_post_rsync.log"

echo "==== post-rsync automation start $(date '+%Y-%m-%d %H:%M:%S') ====" | tee "$LOG"

# Step 1: Wait for rsync to finish
echo "[1/5] Waiting for rsync PID $RYSNC_PID to finish..." | tee -a "$LOG"
while kill -0 "$RYSNC_PID" 2>/dev/null; do
    sleep 30
done
echo "    rsync process exited at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"

# Give NFS a moment to settle
sleep 5

# Step 2: Verify byte-level match
echo "[2/5] Verifying byte-level match..." | tee -a "$LOG"
SRC_BYTES=$(du -sb "$SRC" 2>/dev/null | cut -f1)
DST_BYTES=$(du -sb "$DST" 2>/dev/null | cut -f1)
SRC_PARQUETS=$(find "$SRC/data" -name '*.parquet' -type f 2>/dev/null | wc -l)
DST_PARQUETS=$(find "$DST/data" -name '*.parquet' -type f 2>/dev/null | wc -l)

echo "  source: $SRC_PARQUETS parquet / $SRC_BYTES bytes" | tee -a "$LOG"
echo "  dest:   $DST_PARQUETS parquet / $DST_BYTES bytes" | tee -a "$LOG"

if [ "$SRC_PARQUETS" -ne 4600 ] || [ "$DST_PARQUETS" -ne 4600 ]; then
    echo "⚠️ parquet count mismatch! src=$SRC_PARQUETS dst=$DST_PARQUETS (expected 4600)" | tee -a "$LOG"
    echo "    NOT deleting source. Manual intervention required." | tee -a "$LOG"
    exit 1
fi

if [ "$SRC_BYTES" != "$DST_BYTES" ]; then
    DELTA=$((SRC_BYTES - DST_BYTES))
    echo "⚠️ byte mismatch! delta=$DELTA (src=$SRC_BYTES dst=$DST_BYTES)" | tee -a "$LOG"
    if [ "$DELTA" -gt 1073741824 ] || [ "$DELTA" -lt -1073741824 ]; then
        echo "    delta > 1GB, NOT deleting source." | tee -a "$LOG"
        exit 1
    else
        echo "    delta < 1GB, acceptable (NFS metadata). Proceeding." | tee -a "$LOG"
    fi
else
    echo "  ✅ byte-level match confirmed!" | tee -a "$LOG"
fi

# Step 3: Delete source (tokenization is done, safe to delete)
echo "[3/5] Deleting source at $SRC ..." | tee -a "$LOG"
# Double-check no tokenization is reading from source
if pgrep -f 'tokenize.*stackv3' >/dev/null 2>&1; then
    echo "  ⚠️ tokenization still running! NOT deleting source." | tee -a "$LOG"
else
    rm -rf "$SRC"
    echo "  ✅ source deleted at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
    # Verify deletion
    if [ -d "$SRC" ]; then
        echo "  ⚠️ source directory still exists after rm -rf!" | tee -a "$LOG"
    else
        echo "  ✅ source directory confirmed removed" | tee -a "$LOG"
    fi
fi

# Step 4: Start full download
echo "[4/5] Starting full hf download to $DST ..." | tee -a "$LOG"

PRE_FILES=$(find "$DST/data" -name '*.parquet' -type f 2>/dev/null | wc -l)
PRE_BYTES=$(du -sb "$DST" 2>/dev/null | cut -f1)
echo "  pre-download: $PRE_FILES parquet / $PRE_BYTES bytes" | tee -a "$LOG"
df -h /nas_user | tee -a "$LOG"

nice -n 19 hf download "HuggingFaceCode/stack-v3-train" \
    --repo-type dataset \
    --local-dir "$DST" \
    --max-workers 2 \
    >> "$LOG" 2>&1

RC=$?

# Step 5: Post-download verification
echo "[5/5] Post-download verification at $(date '+%Y-%m-%d %H:%M:%S') ..." | tee -a "$LOG"
POST_FILES=$(find "$DST/data" -name '*.parquet' -type f 2>/dev/null | wc -l)
POST_BYTES=$(du -sb "$DST" 2>/dev/null | cut -f1)
POST_INCS=$(find "$DST" -name '*.incomplete' -type f 2>/dev/null | wc -l)
echo "  total parquet: $POST_FILES" | tee -a "$LOG"
echo "  total bytes:   $POST_BYTES" | tee -a "$LOG"
echo "  incomplete:    $POST_INCS" | tee -a "$LOG"
echo "  download rc:   $RC" | tee -a "$LOG"
df -h /nas_user | tee -a "$LOG"

if [ "$RC" -eq 0 ] && [ "$POST_INCS" -eq 0 ]; then
    echo "✅ FULL DOWNLOAD COMPLETE: $POST_FILES parquet / $POST_BYTES bytes" | tee -a "$LOG"
else
    echo "⚠️ DOWNLOAD ISSUES: rc=$RC, incomplete=$POST_INCS" | tee -a "$LOG"
fi
echo "==== post-rsync automation end $(date '+%Y-%m-%d %H:%M:%S') ====" | tee -a "$LOG"
