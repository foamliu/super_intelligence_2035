#!/bin/bash
# stackv3_tokenize_new_launch.sh
# Step C: Wait for hf download to complete, then tokenize new shards (skip already-tokenized).
# Auto-skip: stackv3_tokenize.py checks if .json/.bin/.idx already exist → SKIP.
# Usage: setsid bash stackv3_tokenize_new_launch.sh > /tmp/tokenize_stackv3_new.log 2>&1 < /dev/null &
#
# ⚠️ Robustness fix (2026-11-14): removed `set -euo pipefail` from the monitoring
# loop — NFS transient errors on `find` were killing the wait process.  Only the
# tokenization command itself uses `set -e` so a genuine tokenize failure still
# surfaces.

PARQUET_DIR="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data"
REPO_ROOT="/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train"
OUTPUT_DIR="/nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train"
SCRIPT="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/stackv3_tokenize.py"
LOG="/tmp/tokenize_stackv3_new.log"
EXPECTED_PARQUET=8192   # authoritative parquet count from HfApi (2026-11-13 audit)
MAX_WAIT_HOURS=48

echo "=== stackv3_tokenize_new_launch.sh started $(date) ==="
echo "PARQUET_DIR=$PARQUET_DIR"
echo "OUTPUT_DIR=$OUTPUT_DIR"
echo "EXPECTED_PARQUET=$EXPECTED_PARQUET"
echo "Waiting for hf download to complete (up to ${MAX_WAIT_HOURS}h)..."

wait_start=$(date +%s)
while true; do
    # Count parquet files in data/ and incomplete files in entire repo (including .cache/)
    # `|| true` guards against NFS transient errors that previously killed the script
    n_parquet=$(find "$PARQUET_DIR" -maxdepth 1 -name '*.parquet' 2>/dev/null | wc -l || echo 0)
    n_incomplete=$(find "$REPO_ROOT" -name '*.incomplete' 2>/dev/null | wc -l || echo 0)

    # Check if hf download process is still running
    if ! pgrep -f "hf download HuggingFaceCode/stack-v3-train" > /dev/null 2>&1; then
        echo "$(date): hf download process not found — checking completion criteria..."
        echo "$(date): parquet=$n_parquet/$EXPECTED_PARQUET incomplete=$n_incomplete"
        # Guard: all three conditions must be met before starting tokenization
        if [ "$n_incomplete" -eq 0 ] && [ "$n_parquet" -eq "$EXPECTED_PARQUET" ]; then
            echo "$(date): Download verified complete (parquet=$n_parquet==$EXPECTED_PARQUET, incomplete=0, process gone)."
            break
        elif [ "$n_incomplete" -eq 0 ] && [ "$n_parquet" -lt "$EXPECTED_PARQUET" ]; then
            echo "$(date): WARNING: process gone but parquet=$n_parquet < expected=$EXPECTED_PARQUET and no incomplete files."
            echo "$(date): This may indicate a crashed download. NOT starting tokenization. Aborting."
            exit 1
        else
            echo "$(date): process gone but incomplete=$n_incomplete > 0. Waiting for incomplete files to clear..."
        fi
    else
        echo "$(date): Waiting... parquet=$n_parquet/$EXPECTED_PARQUET incomplete=$n_incomplete"
    fi

    elapsed=$(( $(date +%s) - wait_start ))
    if [ $elapsed -gt $((MAX_WAIT_HOURS * 3600)) ]; then
        echo "$(date): ERROR: Max wait time exceeded. Aborting."
        exit 1
    fi
    sleep 300  # check every 5 minutes
done

echo ""
echo "=== Download complete. Starting tokenization at $(date) ==="
n_parquet=$(find "$PARQUET_DIR" -name '*.parquet' 2>/dev/null | wc -l || echo 0)
echo "Total parquets: $n_parquet"

# Ensure tokenizer dependencies are on PATH
export PATH="/nas_train/app.e0031982/miniforge3/envs/py310/bin:$PATH"

# Re-enable strict mode for tokenization so genuine failures surface
set -e

# Run tokenization: --shards all → script will auto-skip already-tokenized shards
nice -n 19 ionice -c3 python3 "$SCRIPT" \
    --parquet-dir "$PARQUET_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --shards all \
    --workers 8

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
