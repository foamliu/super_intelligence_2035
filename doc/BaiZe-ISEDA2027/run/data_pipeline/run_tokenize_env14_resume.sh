#!/bin/bash
# run_tokenize_env14_resume.sh — SAFE resume of en_v1_4 tokenization (wake 526)
#
# Problem: the original run_tokenize_env14.sh wrapper (PID 2446251) died at ~12:53,
# leaving 8 orphan preprocess_data_cm.py children (PIDs 2446297-2446395) still
# running.  Restarting the original wrapper would CONFLICT because its SKIP check
# (.bin + .idx + .json) does not see .idx/.json for in-progress shards → it would
# re-launch the 8 running shards.
#
# This resume script is SAFE because it:
#   1. Counts ALL running preprocess_data_cm.py processes (including orphans) via
#      pgrep — so the throttle respects the 8 orphans already consuming slots.
#   2. Skips a shard if it is DONE (.bin + .idx + .json all non-empty) OR if a
#      preprocess_data_cm.py process with that shard name is currently running.
#   3. Only launches shards that are neither done nor in-progress.
#
# Launch:
#   setsid -f nohup bash run_tokenize_env14_resume.sh > /tmp/run_tokenize_env14_resume.log 2>&1 &
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
EN_V14_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs
MAX_CONCURRENT=8
NICE=19
POLL_INTERVAL=30   # seconds between throttle checks

mkdir -p "$OUT_DIR" "$LOG_DIR"

# Count ALL running preprocess_data_cm.py processes (own children + orphans)
count_running() {
  pgrep -cf 'preprocess_data_cm\.py.*env14' 2>/dev/null || echo 0
}

# Check if a specific shard is currently being tokenized (process args contain shard name)
is_shard_running() {
  local shard="$1"
  pgrep -af 'preprocess_data_cm\.py' 2>/dev/null | grep -qF "$shard" && echo 1 || echo 0
}

# Check if a shard is fully done (.bin + .idx + .json all non-empty)
is_shard_done() {
  local shard="$1"
  local prefix="$OUT_DIR/env14_${shard}"
  [ -s "${prefix}.bin" ] && [ -s "${prefix}.idx" ] && [ -s "${prefix}.json" ]
}

echo "=== en_v1_4 tokenization RESUME $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "Max concurrent: $MAX_CONCURRENT, nice: $NICE, poll: ${POLL_INTERVAL}s"

# Build the full shard list from completed download dirs (>= 512 parquet)
SHARDS_FILE=/tmp/env14_all_shards.txt
> "$SHARDS_FILE.tmp"
for d in "$EN_V14_DIR"/CC-MAIN-*; do
  [ -d "$d" ] || continue
  n=$(find "$d" -maxdepth 1 -name '*.parquet' 2>/dev/null | wc -l)
  if [ "$n" -ge 512 ]; then
    echo "$(basename "$d")" >> "$SHARDS_FILE.tmp"
  fi
done
mv "$SHARDS_FILE.tmp" "$SHARDS_FILE"
TOTAL_SHARDS=$(wc -l < "$SHARDS_FILE")
echo "Downloaded shards (>=512 parquet): $TOTAL_SHARDS"

launched=0
skipped_done=0
skipped_running=0
waited=0

while IFS= read -r shard; do
  [ -z "$shard" ] && continue

  # Skip if fully done
  if is_shard_done "$shard"; then
    skipped_done=$((skipped_done + 1))
    continue
  fi

  # Skip if currently being tokenized (orphan or own child)
  if [ "$(is_shard_running "$shard")" = "1" ]; then
    skipped_running=$((skipped_running + 1))
    continue
  fi

  # Throttle: wait until a slot is free (count ALL running, including orphans)
  while [ "$(count_running)" -ge "$MAX_CONCURRENT" ]; do
    sleep "$POLL_INTERVAL"
    waited=$((waited + 1))
  done

  # Launch this shard
  out_prefix="$OUT_DIR/env14_${shard}"
  echo "[$(date '+%H:%M:%S')] LAUNCH $shard (running=$(count_running))"
  nice -n "$NICE" "$PY" "$SCRIPT" \
    --input-dir "$EN_V14_DIR/$shard" \
    --output-prefix "$out_prefix" \
    --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
    --mode content --text-column content --dtype int32 \
    > "$LOG_DIR/env14_${shard}.log" 2>&1 &
  launched=$((launched + 1))
  # Small stagger to avoid thundering herd on tokenizer load
  sleep 5
done < "$SHARDS_FILE"

echo "[$(date '+%H:%M:%S')] Launch phase done: launched=$launched skipped_done=$skipped_done skipped_running=$skipped_running"
echo "[$(date '+%H:%M:%S')] Waiting for all children to finish..."
wait

# Summary
echo "=== en_v1_4 tokenization RESUME END $(date '+%Y-%m-%d %H:%M:%S') ==="
BIN_COUNT=$(ls "$OUT_DIR"/env14_*.bin 2>/dev/null | wc -l)
echo "Output .bin files: $BIN_COUNT"
