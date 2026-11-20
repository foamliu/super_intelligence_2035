#!/usr/bin/env bash
# stackv3_batch_download.sh — HuggingFaceCode/stack-v3-train 分批下载
# 运维令 2026-11-07 10:10: 2TB 上限, 每批 <=300GB, nice -n 10, --max-workers 2
# 落盘: /nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/
# 用法: bash stackv3_batch_download.sh <batch_num> <start_hundred_3digit> <end_hundred_3digit_inclusive>
#   例: bash stackv3_batch_download.sh 1 000 006  → 下载 part-000* ~ part-006* (700 shard ≈ 289GB)
#   每个 "hundred" = 100 shard ≈ 41 GB; 一批 7 hundred ≈ 289 GB
set -uo pipefail   # 不用 -e：单个 hundred 失败不应中断整批

export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"
export HTTPS_PROXY="http://172.19.92.25:13128"
export https_proxy="$HTTPS_PROXY"
export HTTP_PROXY="$HTTPS_PROXY"
export http_proxy="$HTTPS_PROXY"
export HF_HUB_ENABLE_HF_TRANSFER=0

REPO="HuggingFaceCode/stack-v3-train"
BASE="/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
BATCH="${1:-1}"
START="${2:-000}"
END="${3:-006}"
LOG="/tmp/stackv3_batch${BATCH}_$(date '+%Y%m%d_%H%M%S').log"
STATUS="/tmp/stackv3_batch${BATCH}_status.tsv"

echo "==== stack-v3-train batch $BATCH start $(date '+%Y%m%d_%H%M%S') ====" | tee "$LOG"
echo "  shard hundreds: part-${START}* ~ part-${END}* (each=100 shards ≈41GB)" | tee -a "$LOG"
echo -e "batch\thundred\tstatus\tfiles\tbytes\tincomplete" > "$STATUS"

mkdir -p "$BASE"

# Download each 100-shard group separately (proven to work with single --include)
FAIL=0
for h in $(seq -w "$START" "$END"); do
    PATTERN="data/part-${h}*"
    echo "[hundred $h] downloading $PATTERN ..." | tee -a "$LOG"
    if nice -n 10 hf download "$REPO" \
        --repo-type dataset \
        --local-dir "$BASE" \
        --max-workers 2 \
        --include "$PATTERN" \
        >> "$LOG" 2>&1 ; then
        NFILES=$(find "$BASE/data" -name "part-${h}*.parquet" -type f | wc -l)
        NINCS=$(find "$BASE" -name '*.incomplete' | wc -l)
        BYTES=$(du -sb "$BASE/data" 2>/dev/null | cut -f1)
        echo -e "BATCH${BATCH}\t${h}\tOK\t${NFILES}\t${BYTES}\t${NINCS}" >> "$STATUS"
        echo "[hundred $h] OK files=$NFILES bytes=$BYTES incs=$NINCS" | tee -a "$LOG"
    else
        RC=$?
        NFILES=$(find "$BASE/data" -name "part-${h}*.parquet" -type f 2>/dev/null | wc -l)
        NINCS=$(find "$BASE" -name '*.incomplete' 2>/dev/null | wc -l)
        BYTES=$(du -sb "$BASE/data" 2>/dev/null | cut -f1)
        echo -e "BATCH${BATCH}\t${h}\tFAIL(rc=$RC)\t${NFILES}\t${BYTES}\t${NINCS}" >> "$STATUS"
        echo "[hundred $h] FAIL rc=$RC files=$NFILES bytes=$BYTES incs=$NINCS" | tee -a "$LOG"
        FAIL=$((FAIL+1))
    fi
    # Check disk space between hundreds
    AVAIL_KB=$(df --output=avail -k /nas_inference | tail -1 | tr -d ' ')
    AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
    echo "  disk check: /nas_inference avail=${AVAIL_GB}GB" | tee -a "$LOG"
    if [ "$AVAIL_GB" -lt 5120 ]; then
        echo "⚠️ /nas_inference <5T free (${AVAIL_GB}GB), stopping batch per operator cmd" | tee -a "$LOG"
        break
    fi
done

# Final summary
TOTAL_FILES=$(find "$BASE/data" -name '*.parquet' -type f | wc -l)
TOTAL_BYTES=$(du -sb "$BASE/data" 2>/dev/null | cut -f1)
TOTAL_INCS=$(find "$BASE" -name '*.incomplete' | wc -l)
echo "==== batch $BATCH FINISH $(date '+%Y%m%d_%H%M%S') ====" | tee -a "$LOG"
echo "  total files=$TOTAL_FILES bytes=$TOTAL_BYTES incomplete=$TOTAL_INCS failed_hundreds=$FAIL" | tee -a "$LOG"
echo "  status: $STATUS" | tee -a "$LOG"
