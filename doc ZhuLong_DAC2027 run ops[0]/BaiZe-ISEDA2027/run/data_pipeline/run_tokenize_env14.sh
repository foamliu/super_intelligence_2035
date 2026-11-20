#!/bin/bash
# run_tokenize_env14.sh — en_v1_4 分词（运维指令 2026-10-18② 令④）
# 对 Ultra-FineWeb en_v1_4 已完成的 CC-MAIN-* 快照逐 shard 分词，产出 .bin/.idx
#   每个 CC-MAIN-XXXX 目录含 512 个 *.parquet（text column = content）
# 并发: 8 进程, nice -n 19（最低优先级，不干扰 download / vision GPU）
# 产物前缀: env14_<CC-MAIN-XXXX>  → /nas_train/.../baize-data/text/env14_*.bin/.idx/.json
#
# 用法:
#   setsid -f nohup bash run_tokenize_env14.sh > /tmp/run_tokenize_env14.log 2>&1 &
set -uo pipefail   # no -e: background job failures shouldn't kill the launcher

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
EN_V14_DIR=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs
SHARDS_FILE=/tmp/env14_completed_shards.txt
MAX_CONCURRENT=8
NICE=19

mkdir -p "$OUT_DIR" "$LOG_DIR"

# Build completed shards list if not present or stale (>60min old)
need_rebuild=1
if [ -f "$SHARDS_FILE" ]; then
  age_min=$(( ($(date +%s) - $(stat -c %Y "$SHARDS_FILE")) / 60 ))
  [ "$age_min" -lt 60 ] && need_rebuild=0
fi
if [ "$need_rebuild" -eq 1 ]; then
  echo "[$(date '+%H:%M:%S')] Building completed shards list..."
  > "$SHARDS_FILE.tmp"
  for d in "$EN_V14_DIR"/CC-MAIN-*; do
    n=$(find "$d" -maxdepth 1 -name '*.parquet' 2>/dev/null | wc -l)
    if [ "$n" -eq 512 ]; then
      echo "$(basename "$d")" >> "$SHARDS_FILE.tmp"
    fi
  done
  mv "$SHARDS_FILE.tmp" "$SHARDS_FILE"
fi
TOTAL_SHARDS=$(wc -l < "$SHARDS_FILE")
echo "=== en_v1_4 tokenization START $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "Completed shards to tokenize: $TOTAL_SHARDS"
echo "Max concurrent: $MAX_CONCURRENT, nice: $NICE"

launch_one() {
  local shard="$1"
  local out_prefix="$OUT_DIR/env14_${shard}"
  # Skip if already done (.bin + .idx + .json all exist and .bin > 0)
  if [ -s "${out_prefix}.bin" ] && [ -s "${out_prefix}.idx" ] && [ -s "${out_prefix}.json" ]; then
    echo "[$(date '+%H:%M:%S')] SKIP $shard (already tokenized)"
    return 0
  fi
  nice -n "$NICE" "$PY" "$SCRIPT" \
    --input-dir "$EN_V14_DIR/$shard" \
    --output-prefix "$out_prefix" \
    --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
    --mode content --text-column content --dtype int32 \
    > "$LOG_DIR/env14_${shard}.log" 2>&1 &
  echo "[$(date '+%H:%M:%S')] LAUNCH $shard (PID=$!)"
}

launched=0
skipped=0
while IFS= read -r shard; do
  [ -z "$shard" ] && continue
  # Check if already done
  out_prefix="$OUT_DIR/env14_${shard}"
  if [ -s "${out_prefix}.bin" ] && [ -s "${out_prefix}.idx" ] && [ -s "${out_prefix}.json" ]; then
    skipped=$((skipped + 1))
    continue
  fi
  # Throttle: wait if too many running
  while [ "$(jobs -rp 2>/dev/null | wc -l)" -ge "$MAX_CONCURRENT" ]; do
    sleep 15
  done
  launch_one "$shard"
  launched=$((launched + 1))
done < "$SHARDS_FILE"

echo "[$(date '+%H:%M:%S')] Launched=$launched Skipped=$skipped, waiting for all to finish..."
wait

# Summary
echo "=== en_v1_4 tokenization END $(date '+%Y-%m-%d %H:%M:%S') ==="
BIN_COUNT=$(ls "$OUT_DIR"/env14_*.bin 2>/dev/null | wc -l)
echo "Output .bin files: $BIN_COUNT"
TOTAL_TOK=0
for jf in "$OUT_DIR"/env14_*.json; do
  [ -f "$jf" ] || continue
  t=$("$PY" -c "import json; print(json.load(open('$jf'))['num_tokens'])" 2>/dev/null || echo 0)
  TOTAL_TOK=$((TOTAL_TOK + t))
done
echo "Total tokens: $TOTAL_TOK"
echo "FINAL: $BIN_COUNT .bin files, $TOTAL_TOK tokens"
