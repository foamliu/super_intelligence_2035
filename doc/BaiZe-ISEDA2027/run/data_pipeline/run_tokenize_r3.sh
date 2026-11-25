#!/bin/bash
# run_tokenize_r3.sh — 运维指令 2026-10-09③ 全量分词（停②重头来）
# 3 个原始目录，每个目录所有文件全切，不挑不漏
#   Ultra-FineWeb-L3  1,764 parquet → l3_s{i}   (40 shards, col=content)
#   UltraData-Code    1,121 parquet → code_s{i} (30 shards: L2=content s0-s14, L3=full_content s15-s29)
#   UltraData-Math    1,823 parquet → math_s{i} (40 shards, col=content)
# 并发: 110 进程, nice -n 10
set -euo pipefail
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs
STAGE_BASE=/nas_train/app.e0031982/datasets/baize-data/text/staging_r3
mkdir -p "$OUT_DIR" "$LOG_DIR" "$STAGE_BASE"
ALL_PIDS=""

launch_shard() {
  local src_prefix="$1" shard_idx="$2" text_col="$3" files_file="$4"
  local stage_dir="$STAGE_BASE/${src_prefix}_s${shard_idx}"
  mkdir -p "$stage_dir"
  while IFS= read -r pf; do
    ln -sf "$pf" "$stage_dir/$(basename "$pf")"
  done < "$files_file"
  local count=$(ls "$stage_dir"/*.parquet 2>/dev/null | wc -l)
  echo "[${src_prefix}] s${shard_idx}: ${count} parquet, col=${text_col}"
  nice -n 10 "$PY" "$SCRIPT" \
    --input-dir "$stage_dir" \
    --output-prefix "$OUT_DIR/${src_prefix}_s${shard_idx}" \
    --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
    --mode content --text-column "$text_col" --dtype int32 \
    > "$LOG_DIR/${src_prefix}_s${shard_idx}.log" 2>&1 &
  ALL_PIDS="$ALL_PIDS $!"
}

split_into_groups() {
  local input_file="$1" n_groups="$2" output_prefix="$3"
  local total=$(wc -l < "$input_file")
  local group_size=$(( (total + n_groups - 1) / n_groups ))
  split -l "$group_size" -d -a 3 "$input_file" "${output_prefix}_"
}

echo "=== R3 全量分词启动 $(date '+%Y-%m-%d %H:%M:%S') ==="

# 1. Ultra-FineWeb-L3 (1,764 parquet, all content)
echo "=== [1/3] Ultra-FineWeb-L3: 1,764 parquet → 40 shards ==="
L3_SRC=/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data
find "$L3_SRC" -name '*.parquet' -type f | sort > "$STAGE_BASE/l3_all.txt"
L3_TOTAL=$(wc -l < "$STAGE_BASE/l3_all.txt")
L3_SHARDS=40
split_into_groups "$STAGE_BASE/l3_all.txt" "$L3_SHARDS" "$STAGE_BASE/l3_g"
for i in $(seq 0 $((L3_SHARDS - 1))); do
  launch_shard "l3" "$i" "content" "$STAGE_BASE/l3_g_$(printf '%03d' "$i")"
done

# 2. UltraData-Code (1,121 parquet, L2=content, L3=full_content)
echo "=== [2/3] UltraData-Code: 1,121 parquet → 30 shards ==="
CODE_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data
find "$CODE_SRC/UltraData-Code-L2" -name '*.parquet' -type f | sort > "$STAGE_BASE/code_l2.txt"
CODE_L2_TOTAL=$(wc -l < "$STAGE_BASE/code_l2.txt")
find "$CODE_SRC/UltraData-Code-L3" -name '*.parquet' -type f | sort > "$STAGE_BASE/code_l3.txt"
CODE_L3_TOTAL=$(wc -l < "$STAGE_BASE/code_l3.txt")
echo "Code L2: $CODE_L2_TOTAL (content), L3: $CODE_L3_TOTAL (full_content)"
CODE_L2_SHARDS=15
CODE_L3_SHARDS=15
split_into_groups "$STAGE_BASE/code_l2.txt" "$CODE_L2_SHARDS" "$STAGE_BASE/code_l2_g"
for i in $(seq 0 $((CODE_L2_SHARDS - 1))); do
  launch_shard "code" "$i" "content" "$STAGE_BASE/code_l2_g_$(printf '%03d' "$i")"
done
split_into_groups "$STAGE_BASE/code_l3.txt" "$CODE_L3_SHARDS" "$STAGE_BASE/code_l3_g"
for i in $(seq 0 $((CODE_L3_SHARDS - 1))); do
  launch_shard "code" "$((i + CODE_L2_SHARDS))" "full_content" "$STAGE_BASE/code_l3_g_$(printf '%03d' "$i")"
done

# 3. UltraData-Math (1,823 parquet, all content)
echo "=== [3/3] UltraData-Math: 1,823 parquet → 40 shards ==="
MATH_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data
find "$MATH_SRC" -name '*.parquet' -type f | sort > "$STAGE_BASE/math_all.txt"
MATH_TOTAL=$(wc -l < "$STAGE_BASE/math_all.txt")
MATH_SHARDS=40
split_into_groups "$STAGE_BASE/math_all.txt" "$MATH_SHARDS" "$STAGE_BASE/math_g"
for i in $(seq 0 $((MATH_SHARDS - 1))); do
  launch_shard "math" "$i" "content" "$STAGE_BASE/math_g_$(printf '%03d' "$i")"
done

echo "=== R3 启动完成 $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "L3: $L3_SHARDS shards ($L3_TOTAL pq) | Code: $((CODE_L2_SHARDS+CODE_L3_SHARDS)) shards ($((CODE_L2_TOTAL+CODE_L3_TOTAL)) pq) | Math: $MATH_SHARDS shards ($MATH_TOTAL pq)"
echo "Total: $((L3_SHARDS+CODE_L2_SHARDS+CODE_L3_SHARDS+MATH_SHARDS)) processes"
echo "PIDS:$ALL_PIDS"
echo "$ALL_PIDS" > "$LOG_DIR/r3_tokenize_pids.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_DIR/r3_tokenize_pids.txt"
