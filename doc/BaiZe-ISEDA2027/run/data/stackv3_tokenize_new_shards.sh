#!/bin/bash
# stackv3_tokenize_new_shards.sh — Step C: Tokenize new stack-v3-train shards (part-04600+)
# Prerequisites:
#   1. rsync of 926GB tokenized data to /nas_user completed and verified
#   2. hf download of full stack-v3-train to /nas_user completed (0 .incomplete)
#   3. /nas_train source tokenized dir deleted
#
# Usage:
#   bash stackv3_tokenize_new_shards.sh test    # 3-shard test run
#   bash stackv3_tokenize_new_shards.sh full     # full run (all shards, skip first 4600)
#   bash stackv3_tokenize_new_shards.sh check    # just check prerequisites

set -euo pipefail

PARQUET_DIR="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data"
OUTPUT_DIR="/nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train"
SCRIPT="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/stackv3_tokenize.py"
LOG="/tmp/tokenize_stackv3_new.log"
MODE="${1:-check}"

echo "=== stackv3_tokenize_new_shards.sh ==="
echo "Mode: $MODE"
echo "Parquet dir: $PARQUET_DIR"
echo "Output dir:  $OUTPUT_DIR"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"

# --- Check prerequisites ---
check_prereqs() {
    echo "--- Checking prerequisites ---"

    # Check 1: rsync done (source should be deleted, MANIFEST at dest)
    if [ -f "$OUTPUT_DIR/MANIFEST.json" ]; then
        local dst_json=$(find "$OUTPUT_DIR" -name '*.json' ! -name 'MANIFEST.json' 2>/dev/null | wc -l)
        echo "  Tokenized .json at dest: $dst_json (expected ~4362)"
    else
        echo "  ERROR: MANIFEST.json not found at $OUTPUT_DIR — rsync may not be complete"
        return 1
    fi

    # Check 2: source deleted
    if [ -d "/nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train" ]; then
        echo "  WARNING: Source tokenized dir still exists at /nas_train (not yet deleted)"
    else
        echo "  OK: Source tokenized dir deleted from /nas_train"
    fi

    # Check 3: hf download complete (0 incomplete)
    local inc_count=$(find "$PARQUET_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
    local parquet_count=$(find "$PARQUET_DIR" -name '*.parquet' 2>/dev/null | wc -l)
    echo "  Parquet files: $parquet_count"
    echo "  Incomplete files: $inc_count"

    if [ "$inc_count" -gt 0 ]; then
        echo "  WARNING: Download still has $inc_count incomplete files"
        return 1
    fi

    # Check 4: disk space
    local user_avail=$(df -h /nas_user | tail -1 | awk '{print $4}')
    echo "  /nas_user available: $user_avail"

    echo "--- Prerequisites check done ---"
    return 0
}

# --- Test run (3 new shards) ---
run_test() {
    echo "--- Starting 3-shard test run ---"
    # Use --shard-start to get the first 3 NEW shards (after the 4600 already tokenized)
    # The script will load all parquets, but only process shards 4600-4602
    nice -n 19 ionice -c3 python "$SCRIPT" \
        --parquet-dir "$PARQUET_DIR" \
        --output-dir "$OUTPUT_DIR" \
        --shard-start 4600 \
        --shard-end 4603 \
        --workers 1 \
        2>&1 | tee "$LOG"
    echo "--- Test run complete ---"
    echo "Check $LOG for results. If PASS, run: bash $0 full"
}

# --- Full run (all shards, skip logic handles first 4600) ---
run_full() {
    echo "--- Starting full tokenization run ---"
    echo "  All shards will be processed; first 4600 will be SKIP (already tokenized)"
    echo "  New shards (4600+) will be tokenized"
    echo "  Workers: 16, nice: 19, ionice: -c3"

    setsid bash -c "
        nice -n 19 ionice -c3 python '$SCRIPT' \
            --parquet-dir '$PARQUET_DIR' \
            --output-dir '$OUTPUT_DIR' \
            --workers 16 \
            2>&1 | tee '$LOG'
        echo \"TOKENIZE_NEW_DONE_EXIT=\$?\" >> '$LOG'
    " < /dev/null > /dev/null 2>&1 &

    local pid=$!
    echo "  Started in background, PID: $pid"
    echo "  Log: $LOG"
    echo "  Monitor: tail -f $LOG"
}

# --- Main ---
case "$MODE" in
    check)
        check_prereqs
        ;;
    test)
        check_prereqs || { echo "Prerequisites not met, aborting."; exit 1; }
        run_test
        ;;
    full)
        check_prereqs || { echo "Prerequisites not met, aborting."; exit 1; }
        run_full
        ;;
    *)
        echo "Usage: $0 {check|test|full}"
        exit 1
        ;;
esac
