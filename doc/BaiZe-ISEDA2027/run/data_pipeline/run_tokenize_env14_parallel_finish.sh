#!/bin/bash
# run_tokenize_env14_parallel_finish.sh
# Parallel finisher for the 5 remaining en_v1_4 shards (105/110 done).
# Kills serial fullsource processes, deletes partial .bin, relaunches
# with preprocess_data_cm_parallel.py using N workers per shard.
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm_parallel.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
EN_V14_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs

WORKERS_PER_SHARD=${WORKERS_PER_SHARD:-13}
BATCH_SIZE=${BATCH_SIZE:-256}
NICE=10

mkdir -p "$OUT_DIR" "$LOG_DIR"

echo "=== en_v1_4 PARALLEL FINISHER START $(date '+%F %T') ==="
echo "workers_per_shard=$WORKERS_PER_SHARD batch=$BATCH_SIZE nice=$NICE"

# Step 1: Kill serial fullsource + all preprocess_data_cm.py
echo "[step1] killing serial processes ..."
pkill -f 'env14_fullsource run_tokenize_env14_fullsource' 2>/dev/null || true
sleep 2
pkill -f 'run_tokenize_env14_fullsource.sh' 2>/dev/null || true
sleep 1
pkill -f 'preprocess_data_cm[.]py' 2>/dev/null || true
sleep 3
remaining=$(pgrep -cf 'preprocess_data_cm[.]py' 2>/dev/null || echo 0)
echo "[step1] remaining: $remaining"
if [ "$remaining" -gt 0 ]; then
  pkill -9 -f 'preprocess_data_cm[.]py' 2>/dev/null || true
  sleep 2
fi
echo "[step1] done at $(date '+%F %T')"

# Step 2: Find WIP shards (has .bin but no .idx), delete partial .bin
echo "[step2] finding WIP shards ..."
WIP_SHARDS=""
for binf in "$OUT_DIR"/env14_CC-MAIN-*.bin; do
  [ -f "$binf" ] || continue
  base="${binf%.bin}"
  if [ ! -s "${base}.idx" ]; then
    shard=$(basename "$base" | sed 's/^env14_//')
    WIP_SHARDS="$WIP_SHARDS $shard"
    sz=$(ls -lh "$binf" 2>/dev/null | awk '{print $5}')
    echo "[step2] WIP: $shard (partial .bin=$sz) — deleting"
    rm -f "$binf" "${base}.idx" "${base}.json"
  fi
done

if [ -z "$WIP_SHARDS" ]; then
  echo "[step2] no WIP shards found"
  done_n=0
  for binf in "$OUT_DIR"/env14_CC-MAIN-*.bin; do
    [ -f "$binf" ] || continue
    b="${binf%.bin}"
    [ -s "${b}.idx" ] && [ -s "${b}.json" ] && done_n=$((done_n + 1))
  done
  echo "[step2] done=$done_n/110"
  [ "$done_n" -ge 110 ] && echo "ALL 110 DONE" && exit 0
  exit 1
fi
echo "[step2] WIP shards:$WIP_SHARDS"

# Step 3: Launch parallel processes
echo "[step3] launching at $(date '+%F %T') ..."
PIDS=""
for shard in $WIP_SHARDS; do
  input_dir="$EN_V14_DIR/$shard"
  out_prefix="$OUT_DIR/env14_${shard}"
  log_file="$LOG_DIR/env14_${shard}_parallel.log"
  [ -d "$input_dir" ] || { echo "[step3] SKIP $shard (no input dir)"; continue; }
  echo "[step3] LAUNCH $shard workers=$WORKERS_PER_SHARD"
  nice -n "$NICE" "$PY" "$SCRIPT" \
    --input-dir "$input_dir" \
    --output-prefix "$out_prefix" \
    --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
    --mode content --text-column content --dtype int32 \
    --max-chars 50000 \
    --num-workers "$WORKERS_PER_SHARD" --batch-size "$BATCH_SIZE" \
    > "$log_file" 2>&1 &
  pid=$!
  PIDS="$PIDS $pid"
  echo "[step3] $shard PID=$pid"
  sleep 3
done
echo "[step3] all launched PIDs:$PIDS"

# Step 4: Wait
echo "[step4] waiting ..."
fail=0
for pid in $PIDS; do
  wait "$pid" 2>/dev/null
  rc=$?
  [ "$rc" -ne 0 ] && { echo "[step4] PID=$pid FAILED rc=$rc"; fail=$((fail + 1)); } || echo "[step4] PID=$pid OK"
done
echo "[step4] finished at $(date '+%F %T') failures=$fail"

# Step 5: Verify
echo "[step5] verifying ..."
done_n=0
total_tokens=0
for shard in $WIP_SHARDS; do
  base="$OUT_DIR/env14_${shard}"
  if [ -s "${base}.bin" ] && [ -s "${base}.idx" ] && [ -s "${base}.json" ]; then
    tok=$("$PY" -c "import json; print(json.load(open('${base}.json'))['num_tokens'])" 2>/dev/null || echo 0)
    done_n=$((done_n + 1))
    total_tokens=$((total_tokens + tok))
    echo "[step5] OK $shard tokens=$tok"
  else
    echo "[step5] FAIL $shard"
  fi
done

all_done=0
for binf in "$OUT_DIR"/env14_CC-MAIN-*.bin; do
  [ -f "$binf" ] || continue
  b="${binf%.bin}"
  [ -s "${b}.idx" ] && [ -s "${b}.json" ] && all_done=$((all_done + 1))
done
echo "=== COMPLETE $(date '+%F %T') WIP_done=$done_n total=$all_done/110 new_tokens=$total_tokens fail=$fail ==="
