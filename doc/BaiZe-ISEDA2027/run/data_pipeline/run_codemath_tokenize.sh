#!/bin/bash
# run_codemath_tokenize.sh — UltraData-Code / UltraData-MATH 全量分词并行化
# 运维指令 2026-10-09①：Code/Math 全量分词 = P-8 数据层唯一阻塞
#
# Code: 7 进程（11 语言子目录，大语言各 1 进程，小语言顺序合并）
# Math: 4 进程（99 CC-MAIN shards 分 4 组，symlink staging dir）
# 合计 11 进程，nice -n 10，setsid nohup
#
# 产出：/nas_train/app.e0031982/datasets/baize-data/text/code_s{0..10}.bin/.idx/.json
#       /nas_train/app.e0031982/datasets/baize-data/text/math_s{0..3}.bin/.idx/.json
# 格式：Megatron-LM .bin/.idx（int32），tokenizer = tokenizer_eod（DeepSeek-V4.1-Flash + EOD）
# 不入 git（.bin/.idx/.json 产物不入库）

set -euo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs

CODE_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3
MATH_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L1

mkdir -p "$OUT_DIR" "$LOG_DIR"

# ─── Code 分词（7 进程，11 语言 → 11 .bin）──────────────────────────
# text-column = full_content（含 task+analysis+solution+test，最完整）
launch_code() {
  local lang="$1" shard_id="$2" logname="$3"
  echo "[code] 启动 $lang → code_s${shard_id} (log=$LOG_DIR/${logname}.log)"
  nice -n 10 "$PY" "$SCRIPT" \
    --input-dir "$CODE_SRC/$lang" \
    --output-prefix "$OUT_DIR/code_s${shard_id}" \
    --tokenizer "$TOKENIZER" \
    --tokenizer-output-dir "$TOK_OUT" \
    --mode content \
    --text-column full_content \
    --dtype int32 \
    > "$LOG_DIR/${logname}.log" 2>&1 &
  echo $!
}

launch_code_seq() {
  # 顺序处理多个语言，每个产出独立 .bin
  local langs="$1" shard_ids="$2" logname="$3"
  echo "[code-seq] 启动 $langs → code_s${shard_ids} (log=$LOG_DIR/${logname}.log)"
  (
    local i=0
    for lang in $langs; do
      local sid=$(echo "$shard_ids" | cut -d' ' -f$((i+1)))
      echo "[code-seq] === $lang → code_s${sid} ==="
      nice -n 10 "$PY" "$SCRIPT" \
        --input-dir "$CODE_SRC/$lang" \
        --output-prefix "$OUT_DIR/code_s${sid}" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$TOK_OUT" \
        --mode content \
        --text-column full_content \
        --dtype int32
      echo "[code-seq] === $lang → code_s${sid} DONE ==="
      i=$((i+1))
    done
  ) > "$LOG_DIR/${logname}.log" 2>&1 &
  echo $!
}

# Process 0: cpp (167 parquet) → code_s0
CODE_PIDS=""
CODE_PIDS="$CODE_PIDS $(launch_code cpp 0 code_cpp)"

# Process 1: py (147) → code_s1
CODE_PIDS="$CODE_PIDS $(launch_code py 1 code_py)"

# Process 2: java (137) → code_s2
CODE_PIDS="$CODE_PIDS $(launch_code java 2 code_java)"

# Process 3: cs(28) → code_s3, js(29) → code_s4
CODE_PIDS="$CODE_PIDS $(launch_code_seq 'cs js' '3 4' code_cs_js)"

# Process 4: php(24) → code_s5, go(12) → code_s6
CODE_PIDS="$CODE_PIDS $(launch_code_seq 'php go' '5 6' code_php_go)"

# Process 5: rs(7) → code_s7, r(3) → code_s8
CODE_PIDS="$CODE_PIDS $(launch_code_seq 'rs r' '7 8' code_rs_r)"

# Process 6: rb(4) → code_s9, sh(2) → code_s10
CODE_PIDS="$CODE_PIDS $(launch_code_seq 'rb sh' '9 10' code_rb_sh)"

echo "CODE_PIDS: $CODE_PIDS"

# ─── Math 分词（4 进程，99 shards 分 4 组 staging）──────────────────
# text-column = content（Math 只有 content + meta 列）

MATH_SHARDS=$(ls -d "$MATH_SRC"/CC-MAIN-* | sort)
MATH_TOTAL=$(echo "$MATH_SHARDS" | wc -l)
echo "[math] 共 $MATH_TOTAL 个 CC-MAIN shards"

# 分 4 组
GROUP_SIZE=$(( (MATH_TOTAL + 3) / 4 ))  # 向上取整
MATH_PIDS=""
for g in 0 1 2 3; do
  START=$(( g * GROUP_SIZE ))
  END=$(( START + GROUP_SIZE ))
  if [ $END -gt $MATH_TOTAL ]; then END=$MATH_TOTAL; fi

  STAGE_DIR="$OUT_DIR/math_stage_${g}"
  mkdir -p "$STAGE_DIR"

  # 创建 symlinks
  idx=0
  for shard in $MATH_SHARDS; do
    if [ $idx -ge $START ] && [ $idx -lt $END ]; then
      for pf in "$shard"/*.parquet; do
        bn=$(basename "$pf")
        ln -sf "$pf" "$STAGE_DIR/$bn"
      done
    fi
    idx=$((idx+1))
  done

  COUNT=$(ls "$STAGE_DIR"/*.parquet 2>/dev/null | wc -l)
  echo "[math] Group $g: shards[$START..$((END-1))] → $COUNT parquet symlinks → math_s${g}"

  nice -n 10 "$PY" "$SCRIPT" \
    --input-dir "$STAGE_DIR" \
    --output-prefix "$OUT_DIR/math_s${g}" \
    --tokenizer "$TOKENIZER" \
    --tokenizer-output-dir "$TOK_OUT" \
    --mode content \
    --text-column content \
    --dtype int32 \
    > "$LOG_DIR/math_s${g}.log" 2>&1 &
  MATH_PIDS="$MATH_PIDS $!"
done

echo "MATH_PIDS: $MATH_PIDS"
echo "ALL_PIDS: $CODE_PIDS $MATH_PIDS"
echo "START_TIME: $(date '+%Y-%m-%d %H:%M:%S')"

# 写 PID 文件供巡检
echo "$CODE_PIDS $MATH_PIDS" > "$LOG_DIR/codemath_pids.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_DIR/codemath_pids.txt"

echo "=== 分词已启动 ==="
echo "Code: 7 进程 → code_s0..code_s10 (11 .bin)"
echo "Math: 4 进程 → math_s0..math_s3 (4 .bin)"
echo "日志: $LOG_DIR/"
echo "PID 文件: $LOG_DIR/codemath_pids.txt"
