#!/bin/bash
# stackv3_rerun_failed.sh — Rerun failed/missing shards from stack-v3-train tokenization.
# Usage: bash stackv3_rerun_failed.sh [workers]
#   workers: number of parallel workers (default: 4, reduced from 16 to avoid memory pressure)
#
# This script:
#   1. Finds all parquet shards that do NOT have a corresponding .json manifest
#      in the tokenized output directory (i.e., failed or not-yet-processed).
#   2. Runs the FIXED stackv3_tokenize.py on just those shards.
#
# The fix removes combine_chunks() (which caused ArrowNotImplementedError on
# nested columns) and uses iter_batches as fallback instead of pq.read_table.
set -euo pipefail

PY310=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
SCRIPT_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data
PARQUET_DIR=/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data
OUTPUT_DIR=/nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train
WORKERS=${1:-4}
FAILED_LIST=/tmp/stackv3_rerun_shards.txt

echo "=== stackv3 rerun failed shards ==="
echo "Workers: $WORKERS"
echo "Output:  $OUTPUT_DIR"

# Find all parquet shards, find all .json manifests, compute the difference
echo "Scanning for missing/failed shards..."
ALL_PARQUETS=($(ls "$PARQUET_DIR"/part-*.parquet | sort))
TOTAL=${#ALL_PARQUETS[@]}
echo "Total parquet shards: $TOTAL"

MISSING=()
for i in "${!ALL_PARQUETS[@]}"; do
    JSON_PATH="$OUTPUT_DIR/stackv3_s$(printf '%05d' $i).json"
    if [ ! -f "$JSON_PATH" ]; then
        MISSING+=("${ALL_PARQUETS[$i]}")
    fi
done

echo "Missing/failed shards: ${#MISSING[@]}"

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "All shards have .json manifests. Nothing to rerun."
    exit 0
fi

# Write the list
printf '%s\n' "${MISSING[@]}" > "$FAILED_LIST"
echo "Failed shard list: $FAILED_LIST"

# Run the fixed tokenizer on just the failed shards
cd "$SCRIPT_DIR"
export PYTHONPATH=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
echo "Starting rerun at $(date)..."
nice -n 19 ionice -c3 $PY310 stackv3_tokenize.py \
    --shard-list "$FAILED_LIST" \
    --workers "$WORKERS" \
    --output-dir "$OUTPUT_DIR" \
    2>&1 | tee /tmp/stackv3_rerun_$(date +%Y%m%d_%H%M%S).log

echo "Rerun complete at $(date)."
