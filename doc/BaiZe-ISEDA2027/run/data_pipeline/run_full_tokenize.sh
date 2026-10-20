#!/bin/bash
# run_full_tokenize.sh — Full tokenization of UltraData-Code/Math/UFW-L3 sources
# Operator instruction 2026-10-21 04:0x: "完整分词" with 224 cores
#
# Priority: Code L3 → Math L3 → Code L2 → UFW-L3 → Math L1
# Output: Megatron .bin/.idx/.json (int32) to data/full_*/ directories
# Tokenizer: DeepSeek-V4.1-Flash (vocab 129280) + EOD <|im_end|> → 129281
#
# Usage:
#   MAX_CONCURRENT=64 setsid -f nohup bash run_full_tokenize.sh \
#     > /tmp/run_full_tokenize.log 2>&1 &
#
# nice -n 10 (don't interfere with en_v1_4 download/tokenization)

set -uo pipefail

# ─── Configuration ───
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
DATA_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data
STAGING_BASE=/nas_train/app.e0031982/datasets/baize-data/text/staging_full
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs/full_tokenize
MANIFEST="$LOG_DIR/full_tokenize_manifest.tsv"

MAX_CONCURRENT=${MAX_CONCURRENT:-64}
NICE=10
INF_BASE=/nas_inference/app.e0031982/datasets/openbmb

mkdir -p "$LOG_DIR" "$STAGING_BASE"

# ─── Source definitions (priority order) ───
# Format: name|input_dir|output_dir|prefix|text_column|mode
SOURCES=(
  "code_l3|${INF_BASE}/UltraData-Code/data/UltraData-Code-L3|${DATA_BASE}/full_ultradata_code_l3|code_l3_train_s|full_content|content"
  "math_l3|${INF_BASE}/UltraData-Math/data/UltraData-Math-L3|${DATA_BASE}/full_ultradata_math_l3|math_l3_train_s|content|content"
  "code_l2|${INF_BASE}/UltraData-Code/data/UltraData-Code-L2|${DATA_BASE}/full_ultradata_code_l2|code_l2_train_s|content|content"
  "ufw_l3|${INF_BASE}/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa|${DATA_BASE}/full_ufw_l3|ufw_l3_train_s|content|content"
  "math_l1|${INF_BASE}/UltraData-Math/data/UltraData-Math-L1|${DATA_BASE}/full_ultradata_math_l1|math_l1_train_s|content|content"
)
# ─── Helper functions ───

# Count ONLY our workers (output paths contain full_ultradata or full_ufw)
count_my_running() {
  pgrep -af 'miniforge3/envs/py310/bin/python3.10.*preprocess_data_cm' 2>/dev/null \
    | grep 'full_ultradata\|full_ufw' | wc -l
}

# Count ALL preprocess_data_cm workers (ours + en_v1_4's)
count_all_running() {
  pgrep -f 'miniforge3/envs/py310/bin/python3.10.*preprocess_data_cm' 2>/dev/null | wc -l
}

is_done() {
  local prefix="$1"
  [ -s "${prefix}.bin" ] && [ -s "${prefix}.idx" ] && [ -s "${prefix}.json" ]
}

shard_tokens() {
  local jf="$1"
  [ -s "$jf" ] || { echo 0; return; }
  "$PY" -c "import json; print(int(json.load(open('$jf')).get('num_tokens',0)))" 2>/dev/null || echo 0
}


tokenize_source() {
  local name="$1" input_dir="$2" output_dir="$3" prefix="$4" text_column="$5" mode="$6"
  mkdir -p "$output_dir"

  # Collect all parquet files recursively
  local all_parquet
  all_parquet=$(find "$input_dir" -type f -name '*.parquet' 2>/dev/null | sort)
  local total_parquet
  total_parquet=$(echo "$all_parquet" | grep -c '.' || echo 0)
  if [ "$total_parquet" -eq 0 ] || [ "$all_parquet" = "" ]; then
    echo "[$(date '+%F %T')] [$name] ERROR: no parquet in $input_dir"
    return 1
  fi
  echo "[$(date '+%F %T')] [$name] START: $total_parquet parquet → $output_dir"

  # Shards: aim ≥3 parquet/shard, cap at MAX_CONCURRENT
  local num_shards ideal per_shard
  ideal=$(( (total_parquet + 2) / 3 ))
  if [ "$ideal" -gt "$MAX_CONCURRENT" ]; then num_shards=$MAX_CONCURRENT
  elif [ "$ideal" -lt 1 ]; then num_shards=1
  else num_shards=$ideal; fi
  per_shard=$(( (total_parquet + num_shards - 1) / num_shards ))
  echo "[$(date '+%F %T')] [$name] $num_shards shards × ~$per_shard parquet (max=$MAX_CONCURRENT)"

  local files=()
  mapfile -t files <<< "$all_parquet"

  local shard
  for ((shard=0; shard<num_shards; shard++)); do
    local shard_start=$((shard * per_shard))
    local shard_end=$((shard_start + per_shard))
    [ "$shard_end" -gt "$total_parquet" ] && shard_end=$total_parquet
    local out_prefix="${output_dir}/${prefix}${shard}"

    # Skip empty shards (off-by-one guard: last shard may have 0 files)
    if [ "$shard_start" -ge "$total_parquet" ]; then
      echo "[$(date '+%F %T')] [$name] shard $shard: SKIP (start=$shard_start >= total=$total_parquet)"
      continue
    fi

    if is_done "$out_prefix"; then
      echo "[$(date '+%F %T')] [$name] shard $shard: SKIP (done)"
      continue
    fi

    while [ "$(count_my_running)" -ge "$MAX_CONCURRENT" ]; do sleep 10; done

    local stage_dir="${STAGING_BASE}/${name}_stage_${shard}"
    rm -rf "$stage_dir"; mkdir -p "$stage_dir"
    local i
    for ((i=shard_start; i<shard_end; i++)); do
      ln -sf "${files[$i]}" "$stage_dir/$(basename "${files[$i]}")"
    done

    local num_files=$((shard_end - shard_start))
    echo "[$(date '+%F %T')] [$name] LAUNCH s$shard: $num_files parquet → ${prefix}${shard} (my=$(count_my_running) all=$(count_all_running))"
    nice -n "$NICE" "$PY" "$SCRIPT" \
      --input-dir "$stage_dir" \
      --output-prefix "$out_prefix" \
      --tokenizer "$TOKENIZER" \
      --tokenizer-output-dir "$TOK_OUT" \
      --mode "$mode" --text-column "$text_column" --dtype int32 \
      > "$LOG_DIR/${name}_s${shard}.log" 2>&1 &
    sleep 2
  done

  echo "[$(date '+%F %T')] [$name] All shards launched, waiting..."
  wait

  local done_count=0 total_tokens=0 total_bin_bytes=0
  for ((shard=0; shard<num_shards; shard++)); do
    local out_prefix="${output_dir}/${prefix}${shard}"
    if is_done "$out_prefix"; then
      done_count=$((done_count + 1))
      local tok bin_bytes
      tok=$(shard_tokens "${out_prefix}.json")
      bin_bytes=$(stat -c %s "${out_prefix}.bin" 2>/dev/null || echo 0)
      total_tokens=$((total_tokens + tok))
      total_bin_bytes=$((total_bin_bytes + bin_bytes))
      printf '%s\t%s\t%d\t%d\n' "$name" "${prefix}${shard}" "$tok" "$bin_bytes" >> "$MANIFEST"
    fi
  done
  echo "[$(date '+%F %T')] [$name] DONE: $done_count/$num_shards shards, $total_tokens tokens"
  rm -rf "${STAGING_BASE}/${name}_stage_"*
  return 0
}

# ─── Main: process all sources in priority order ───
echo "=== FULL TOKENIZATION START $(date '+%F %T') ==="
echo "max_concurrent=$MAX_CONCURRENT nice=$NICE nproc=$(nproc)"
echo "tokenizer=$TOKENIZER (vocab 129280 + EOD → 129281)"
echo ""

printf '#source\tshard\ttokens\tbin_bytes\n' > "$MANIFEST"

for src in "${SOURCES[@]}"; do
  IFS='|' read -r name input_dir output_dir prefix text_column mode <<< "$src"
  echo "--- Processing: $name ---"
  tokenize_source "$name" "$input_dir" "$output_dir" "$prefix" "$text_column" "$mode"
  echo ""
done

echo "=== FULL TOKENIZATION COMPLETE $(date '+%F %T') ==="
echo "=== Manifest ==="
cat "$MANIFEST"
echo "Manifest: $MANIFEST"
echo "Logs: $LOG_DIR/"
