#!/bin/bash
# stackv3_tokenize_new_launch.sh
# Step C: Wait for hf download to complete, then tokenize new shards (skip already-tokenized).
# Auto-skip: stackv3_tokenize.py checks if .json/.bin/.idx already exist → SKIP.
# Usage: setsid bash stackv3_tokenize_new_launch.sh > /tmp/tokenize_stackv3_new.log 2>&1 < /dev/null &

set -euo pipefail

PARQUET_DIR="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data"
OUTPUT_DIR="/nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train"
SCRIPT="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/stackv3_tokenize.py"
LOG="/tmp/tokenize_stackv3_new.log"
EXPECTED_FILES=8207   # total files in the HF repo (parquet + stats)
MAX_WAIT_HOURS=48

echo "=== stackv3_tokenize_new_launch.sh started $(date) ==="
echo "PARQUET_DIR=$PARQUET_DIR"
echo "OUTPUT_DIR=$OUTPUT_DIR"
echo "Waiting for hf download to complete (up to ${MAX_WAIT_HOURS}h)..."

wait_start=$(date +%s)
while true; do
    # Check if hf download process is still running
    if ! pgrep -f "hf download HuggingFaceCode/stack-v3-train" > /dev/null 2>&1; then
        echo "$(date): hf download process not found — checking file count..."
        n_parquet=$(find "$PARQUET_DIR" -name '*.parquet' 2>/dev/null | wc -l)
        n_incomplete=$(find "$PARQUET_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
        echo "$(date): parquet=$n_parquet incomplete=$n_incomplete"
        if [ "$n_incomplete" -eq 0 ]; then
            echo "$(date): Download appears complete (no incomplete files, process gone)."
            break
        fi
    fi

    n_parquet=$(find "$PARQUET_DIR" -name '*.parquet' 2>/dev/null | wc -l)
    n_incomplete=$(find "$PARQUET_DIR" -name '*.incomplete' 2>/dev/null | wc -l)
    echo "$(date): Waiting... parquet=$n_parquet/$EXPECTED_FILES incomplete=$n_incomplete"

    elapsed=$(( $(date +%s) - wait_start ))
    if [ $elapsed -gt $((MAX_WAIT_HOURS * 3600)) ]; then
        echo "$(date): ERROR: Max wait time exceeded. Aborting."
        exit 1
    fi
    sleep 300  # check every 5 minutes
done

echo ""
echo "=== Download complete. Starting tokenization at $(date) ==="
n_parquet=$(find "$PARQUET_DIR" -name '*.parquet' 2>/dev/null | wc -l)
echo "Total parquets: $n_parquet"

# Run tokenization: --shards all → script will auto-skip already-tokenized shards
nice -n 19 ionice -c3 python3 "$SCRIPT" \
    --parquet-dir "$PARQUET_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --shards all \
    --workers 16

echo "=== Tokenization complete at $(date) ==="

# Post-tokenization stats
echo ""
echo "=== Post-tokenization stats ==="
n_json=$(find "$OUTPUT_DIR" -name '*.json' ! -name 'MANIFEST.json' 2>/dev/null | wc -l)
n_bin=$(find "$OUTPUT_DIR" -name '*.bin' 2>/dev/null | wc -l)
n_idx=$(find "$OUTPUT_DIR" -name '*.idx' 2>/dev/null | wc -l)
total_bytes=$(du -sb "$OUTPUT_DIR" 2>/dev/null | cut -f1)
echo "JSON files: $n_json"
echo "BIN files: $n_bin"
echo "IDX files: $n_idx"
echo "Total bytes: $total_bytes"
echo "Failed shards:"
cat "$OUTPUT_DIR/failed_shards.txt" 2>/dev/null || echo "(none)"
