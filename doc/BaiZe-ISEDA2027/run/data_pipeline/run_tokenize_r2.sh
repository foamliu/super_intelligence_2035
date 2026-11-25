#!/bin/bash
# run_tokenize_r2.sh — 运维指令 2026-10-09② 全量分词（修正①）
# 新增：Code L2(561pq) + Math L2p(138pq) + Math L3(200pq) + L3 web(1764pq)
# 25 新进程，nice -n 10，setsid nohup
set -euo pipefail
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
OUT_DIR=/nas_train/app.e0031982/datasets/baize-data/text
LOG_DIR=/nas_train/app.e0031982/datasets/baize-data/text/logs
mkdir -p "$OUT_DIR" "$LOG_DIR"
ALL_PIDS=""
# === ① Code L2 (7 proc, text-column=content) ===
CODE_L2_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L2
launch_code_l2() {
  local lang="$1" sid="$2" logname="$3"
  echo "[code-l2] $lang → code_l2_s${sid}"
  nice -n 10 "$PY" "$SCRIPT" --input-dir "$CODE_L2_SRC/$lang" \
    --output-prefix "$OUT_DIR/code_l2_s${sid}" --tokenizer "$TOKENIZER" \
    --tokenizer-output-dir "$TOK_OUT" --mode content --text-column content --dtype int32 \
    > "$LOG_DIR/${logname}.log" 2>&1 &
  echo $!
}
launch_code_l2_seq() {
  local langs="$1" sids="$2" logname="$3"
  echo "[code-l2-seq] $langs → code_l2_s${sids}"
  ( local i=0; for lang in $langs; do
      local sid=$(echo "$sids" | cut -d' ' -f$((i+1)))
      echo "[code-l2-seq] === $lang → code_l2_s${sid} ==="
      nice -n 10 "$PY" "$SCRIPT" --input-dir "$CODE_L2_SRC/$lang" \
        --output-prefix "$OUT_DIR/code_l2_s${sid}" --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$TOK_OUT" --mode content --text-column content --dtype int32
      echo "[code-l2-seq] === $lang → code_l2_s${sid} DONE ==="
      i=$((i+1))
    done
  ) > "$LOG_DIR/${logname}.log" 2>&1 &
  echo $!
}
ALL_PIDS="$ALL_PIDS $(launch_code_l2 js   0 code_l2_js)"
ALL_PIDS="$ALL_PIDS $(launch_code_l2 py   1 code_l2_py)"
ALL_PIDS="$ALL_PIDS $(launch_code_l2 php  2 code_l2_php)"
ALL_PIDS="$ALL_PIDS $(launch_code_l2 java 3 code_l2_java)"
ALL_PIDS="$ALL_PIDS $(launch_code_l2 cs   4 code_l2_cs)"
ALL_PIDS="$ALL_PIDS $(launch_code_l2_seq 'cpp rust'   '5 6'      code_l2_cpp_rust)"
ALL_PIDS="$ALL_PIDS $(launch_code_l2_seq 'go rb r sh' '7 8 9 10' code_l2_small)"

# === ② Math L2-preview (2 proc, 138 parquet) ===
MATH_L2P_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L2-preview
for g in 0 1; do
  STAGE_DIR="$OUT_DIR/math_l2_stage_${g}"; mkdir -p "$STAGE_DIR"
  ALL_FILES=$(ls "$MATH_L2P_SRC"/*.parquet | sort)
  TOTAL=$(echo "$ALL_FILES" | wc -l); HALF=$(( (TOTAL + 1) / 2 ))
  if [ $g -eq 0 ]; then SELECTED=$(echo "$ALL_FILES" | head -$HALF); else SELECTED=$(echo "$ALL_FILES" | tail -n +$((HALF + 1))); fi
  for pf in $SELECTED; do ln -sf "$pf" "$STAGE_DIR/$(basename "$pf")"; done
  COUNT=$(ls "$STAGE_DIR"/*.parquet 2>/dev/null | wc -l)
  echo "[math-l2p] Group $g: $COUNT parquet → math_l2_s${g}"
  nice -n 10 "$PY" "$SCRIPT" --input-dir "$STAGE_DIR" \
    --output-prefix "$OUT_DIR/math_l2_s${g}" --tokenizer "$TOKENIZER" \
    --tokenizer-output-dir "$TOK_OUT" --mode content --text-column content --dtype int32 \
    > "$LOG_DIR/math_l2_s${g}.log" 2>&1 &
  ALL_PIDS="$ALL_PIDS $!"
done
# === ③ Math L3 (4 proc, 4 subdirs × 50 parquet) ===
MATH_L3_SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L3
MATH_L3_SUBDIRS=("Conversation-Synthetic" "Multi-Style-Synthetic" "QA-Synthetic" "Textbook-Exercise-Synthetic")
for g in 0 1 2 3; do
  subdir="${MATH_L3_SUBDIRS[$g]}"
  echo "[math-l3] $subdir → math_l3_s${g}"
  nice -n 10 "$PY" "$SCRIPT" --input-dir "$MATH_L3_SRC/$subdir" \
    --output-prefix "$OUT_DIR/math_l3_s${g}" --tokenizer "$TOKENIZER" \
    --tokenizer-output-dir "$TOK_OUT" --mode content --text-column content --dtype int32 \
    > "$LOG_DIR/math_l3_s${g}.log" 2>&1 &
  ALL_PIDS="$ALL_PIDS $!"
done
# === ④ L3 web (12 proc, 4 configs split) ===
L3_WEB_SRC=/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data
launch_l3_web_split() {
  local src_dir="$1" prefix="$2" n_groups="$3"
  local ALL_FILES=$(ls "$src_dir"/*.parquet | sort)
  local TOTAL=$(echo "$ALL_FILES" | wc -l)
  local GROUP_SIZE=$(( (TOTAL + n_groups - 1) / n_groups ))
  echo "[l3-web] $prefix: $TOTAL parquet → $n_groups groups"
  for g in $(seq 0 $((n_groups - 1))); do
    local STAGE_DIR="$OUT_DIR/${prefix}_stage_${g}"; mkdir -p "$STAGE_DIR"
    local START=$(( g * GROUP_SIZE )); local END=$(( START + GROUP_SIZE ))
    if [ $END -gt $TOTAL ]; then END=$TOTAL; fi
    local idx=0
    for pf in $ALL_FILES; do
      if [ $idx -ge $START ] && [ $idx -lt $END ]; then ln -sf "$pf" "$STAGE_DIR/$(basename "$pf")"; fi
      idx=$((idx+1))
    done
    local COUNT=$(ls "$STAGE_DIR"/*.parquet 2>/dev/null | wc -l)
    echo "[l3-web] $prefix s${g}: $COUNT parquet → ${prefix}_s${g}"
    nice -n 10 "$PY" "$SCRIPT" --input-dir "$STAGE_DIR" \
      --output-prefix "$OUT_DIR/${prefix}_s${g}" --tokenizer "$TOKENIZER" \
      --tokenizer-output-dir "$TOK_OUT" --mode content --text-column content --dtype int32 \
      > "$LOG_DIR/${prefix}_s${g}.log" 2>&1 &
    ALL_PIDS="$ALL_PIDS $!"
  done
}
launch_l3_web_split "$L3_WEB_SRC/ultrafineweb_en_l3/qa"          "l3_en_qa"    4
launch_l3_web_split "$L3_WEB_SRC/ultrafineweb_en_l3/multi_style" "l3_en_multi" 4
launch_l3_web_split "$L3_WEB_SRC/ultrafineweb_zh_l3/qa"          "l3_zh_qa"    2
launch_l3_web_split "$L3_WEB_SRC/ultrafineweb_zh_l3/multi_style" "l3_zh_multi" 2
# === 汇总 ===
echo "R2_PIDS: $ALL_PIDS"
echo "START_TIME: $(date '+%Y-%m-%d %H:%M:%S')"
echo "$ALL_PIDS" > "$LOG_DIR/r2_tokenize_pids.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_DIR/r2_tokenize_pids.txt"
echo "=== R2 全量分词已启动 ==="
echo "Code L2:  7 proc | Math L2p: 2 proc | Math L3: 4 proc | L3 web: 12 proc = 25 total"