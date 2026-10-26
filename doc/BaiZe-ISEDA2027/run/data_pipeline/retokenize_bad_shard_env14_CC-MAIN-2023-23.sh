#!/bin/bash
# retokenize_bad_shard_env14_CC-MAIN-2023-23.sh
# 运维令 2026-10-26 22:0x：修复坏 shard env14_CC-MAIN-2023-23（.bin 被截断到 40%）。
# 从源 parquet（512 个）重新分词，写到临时前缀 RETOK_，验证后再原子替换原件。
# 参数与 run_tokenize_env14_parallel_finish.sh 完全一致（确定性可复现 ~30.62B token / ~122.5GB .bin）。
set -uo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/preprocess_data_cm_parallel.py
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
TOK_OUT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod
INPUT=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4/CC-MAIN-2023-23
OUT_PREFIX=/nas_train/app.e0031982/datasets/baize-data/text/RETOK_env14_CC-MAIN-2023-23
LOG=/nas_train/app.e0031982/datasets/baize-data/text/logs/env14_CC-MAIN-2023-23_retok.log

WORKERS=${WORKERS:-48}
BATCH=${BATCH:-256}

echo "=== RETOK START $(date '+%F %T') workers=$WORKERS batch=$BATCH ==="
echo "input=$INPUT"
echo "out_prefix=$OUT_PREFIX"

nice -n 10 "$PY" "$SCRIPT" \
  --input-dir "$INPUT" \
  --output-prefix "$OUT_PREFIX" \
  --tokenizer "$TOKENIZER" --tokenizer-output-dir "$TOK_OUT" \
  --mode content --text-column content --dtype int32 \
  --max-chars 50000 \
  --num-workers "$WORKERS" --batch-size "$BATCH"

rc=$?
echo "=== RETOK END $(date '+%F %T') rc=$rc ==="
# 验证产物
if [ -s "${OUT_PREFIX}.bin" ] && [ -s "${OUT_PREFIX}.idx" ] && [ -s "${OUT_PREFIX}.json" ]; then
  BS=$(stat -c%s "${OUT_PREFIX}.bin")
  echo "retok bin_size=$BS idx_size=$(stat -c%s "${OUT_PREFIX}.idx") json_size=$(stat -c%s "${OUT_PREFIX}.json")"
  echo "expected bin ~= 122496098780 (30.62B token * 4)"
fi
