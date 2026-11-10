#!/usr/bin/env bash
# baize_posttrain_tokenize_anneal_corpus.sh — Tokenize PyAether anneal corpus
#   JSONL -> parquet -> mcore .bin/.idx (data-line task, R160)
#
# 用途：将 R153 构建的 PyAether 领域退火源语料 (pyAether_api_anneal_corpus.jsonl,
#   400 API-ref docs, ~696K tok, 污染闸门 PASS) 分词为 mcore .bin/.idx 格式,
#   供 baize_posttrain_anneal.sh domain blend (domain30:web50:code12:math8) 投料。
#
# ⚠️ 运行环境：必须在 .29 或 .12 上执行（preprocess_data.py + tokenizer_eod 仅在
#   /nas_train 上）。.17 上 /nas_train 不可达，仅能做 JSONL->parquet 转换。
#
# 红线（§5.1）：corpus = API 参考文档 ONLY; 158 eval-task 绝不入。R153 已过闸门。
#
# 用法（在 .29 或 .12 上）：
#   bash baize_posttrain_tokenize_anneal_corpus.sh --dry-run    # 仅打印配方
#   bash baize_posttrain_tokenize_anneal_corpus.sh              # 正式分词
#   bash baize_posttrain_tokenize_anneal_corpus.sh --help
set -uo pipefail

# ============ 路径（与 data 线脚本同口径） ============
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SCRIPT_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash

# 源 JSONL（在共享 git 仓库内，所有机器可读）
SRC_JSONL="$SCRIPT_DIR/pyAether_api_anneal_corpus.jsonl"

# 中间产物
PARQUET_OUT="$BASE/data/pyAether_api_anneal_parquet"
PARQUET_FILE="$PARQUET_OUT/pyAether_api_anneal.parquet"
WORK=/tmp/pt_anneal_tok_work

# 最终产物（baize_posttrain_anneal.sh DOMAIN_DATA 指向此前缀）
BIN_OUT="$BASE/data/pyAether_api_anneal"
BIN_PREFIX="$BIN_OUT/pyAether_api_anneal_train_s0"

export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

# ============ 模式开关 ============
DRY_RUN=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --help)
      echo "Usage: bash baize_posttrain_tokenize_anneal_corpus.sh [--dry-run] [--help]"
      echo "  Tokenize PyAether domain anneal corpus (R153) into mcore .bin/.idx."
      echo "  Must run on .29 or .12 (tokenizer + preprocess_data.py on /nas_train)."
      echo "  Output: $BIN_OUT/pyAether_api_anneal_train_s0.{bin,idx,json}"
      exit 0 ;;
  esac
done

# ============ 配方打印 ============
cat <<EOF
===== PyAether Anneal Corpus Tokenization — RECIPE @ $(date '+%F %T') =====
  mode        : $([ $DRY_RUN = 1 ] && echo DRY-RUN || echo TOKENIZE)
  src_jsonl   : $SRC_JSONL
  parquet_out : $PARQUET_FILE
  bin_out     : $BIN_PREFIX.{bin,idx,json}
  tokenizer   : $TOKENIZER (DeepSeek-V4.1-Flash, vocab 129281)
  preprocess  : $BASE/mamba2_hybrid_2b/preprocess_data.py --mode content --dtype int32
  red_line    : R153 contamination gate PASS (400 docs / 0 hits / 158-task blacklist)
  note        : Small corpus (~696K tok); domain30 blend upsamples ~3600x (WSD)
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行分词。"; exit 0; }

# ============ 前置检查 ============
[ -f "$SRC_JSONL" ] || { echo "ERROR: src JSONL not found: $SRC_JSONL"; exit 1; }
[ -d "$BASE/mamba2_hybrid_2b" ] || { echo "ERROR: mamba2_hybrid_2b not found (not on .29/.12?)"; exit 1; }
[ -f "$BASE/mamba2_hybrid_2b/preprocess_data.py" ] || { echo "ERROR: preprocess_data.py not found"; exit 1; }
[ -d "$TOKENIZER" ] || { echo "ERROR: tokenizer not found: $TOKENIZER"; exit 1; }
[ -f "$PY/python" ] || { echo "ERROR: miniforge py310 not found: $PY/python"; exit 1; }

SUM=/tmp/baize_posttrain_anneal_tokenize.log
mkdir -p "$PARQUET_OUT" "$BIN_OUT" "$WORK"
echo "===== Anneal Corpus Tokenize START @ $(date '+%F %T') =====" > "$SUM"

# ============ Step 1: JSONL -> parquet ============
echo "  [step1] JSONL -> parquet @ $(date '+%F %T')" >> "$SUM"
"$PY/python" "$SCRIPT_DIR/baize_posttrain_anneal_to_parquet.py" \
    --input "$SRC_JSONL" --output "$PARQUET_FILE" >> "$SUM" 2>&1
if [ $? -ne 0 ]; then
    echo "  ERROR: step1 (JSONL->parquet) failed" >> "$SUM"; cat "$SUM"; exit 1
fi
[ -f "$PARQUET_FILE" ] || { echo "  ERROR: parquet not created" >> "$SUM"; exit 1; }
echo "  parquet: $PARQUET_FILE" >> "$SUM"

# ============ Step 2: parquet -> .bin/.idx ============
echo "  [step2] parquet -> .bin/.idx @ $(date '+%F %T')" >> "$SUM"
WORK_SHARD="$WORK/s0"
mkdir -p "$WORK_SHARD"
rm -f "$WORK_SHARD"/*.snappy.parquet 2>/dev/null
ln -sf "$PARQUET_FILE" "$WORK_SHARD/pyAether_api_anneal.snappy.parquet"
"$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
    --input-dir "$WORK_SHARD" --output-prefix "$BIN_PREFIX" \
    --tokenizer "$TOKENIZER" --tokenizer-output-dir "$WORK/tok_eod_anneal" \
    --mode content --dtype int32 >> "$SUM" 2>&1
if [ $? -ne 0 ]; then
    echo "  ERROR: step2 (tokenize) failed" >> "$SUM"; tail -20 "$SUM"; exit 1
fi

# ============ Step 3: 验证产物 ============
echo "  [step3] verify @ $(date '+%F %T')" >> "$SUM"
for ext in bin idx json; do
    [ -f "${BIN_PREFIX}.${ext}" ] || { echo "  ERROR: missing ${BIN_PREFIX}.${ext}" >> "$SUM"; exit 1; }
    echo "  ${ext}: $(($(stat -c%s "${BIN_PREFIX}.${ext}" 2>/dev/null || echo 0)/1024)) KB" >> "$SUM"
done
TOK=$("$PY/python" -c "import json;print(json.load(open('${BIN_PREFIX}.json'))['num_tokens'])" 2>/dev/null || echo 0)
echo "  num_tokens = $TOK (~$((TOK/1000))K)" >> "$SUM"
echo "===== ALL DONE @ $(date '+%F %T') =====" >> "$SUM"
echo ""
cat "$SUM"
echo ""
echo "产物: $BIN_OUT/  |  anneal.sh DOMAIN_DATA -> $BIN_OUT"
echo "下一步: 在 DATA_LEDGER.md 登记此产物"
exit 0
