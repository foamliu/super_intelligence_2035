#!/bin/bash
# Tokenize ultrafineweb_zh (256 parquet, ~301GB) → .bin/.idx (2026-10-07 用户直令)
# I/O 纪律: nice -n 19 + 1 进程（先保守, 盯 BO 速率, BO 掉速则暂停）
# 输出: data/mix_base/mix_base_train_s4 (续 s0-s3 的 22.05B tok → 扩展至 ~100B)
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_zh
OUTDIR="$BASE/data/mix_base"
WORK=/tmp/mix_base_tok_zh_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

LOG=/tmp/baize_tokenize_zh.log
mkdir -p "$OUTDIR" "$WORK"

echo "===== tokenize zh START @ $(date '+%F %T') (256 parquet -> 1 shard s4) =====" > "$LOG"

# 1) 建 symlink 子目录（preprocess_data.py 只认 *.snappy.parquet）
d="$WORK/s4"
mkdir -p "$d"
for f in "$SRC"/ultrafineweb-zh-part-*.parquet; do
    b=$(basename "$f" .parquet)
    ln -sf "$f" "$d/${b}.snappy.parquet"
done
nfiles=$(ls "$d"/*.snappy.parquet 2>/dev/null | wc -l)
echo "  $nfiles parquet symlinked" >> "$LOG"

# 2) nice -n 19 单进程分词
echo "  [shard s4] 启动 @ $(date '+%F %T') (nice -n 19)" >> "$LOG"
nice -n 19 "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
    --input-dir "$d" \
    --output-prefix "$OUTDIR/mix_base_train_s4" \
    --tokenizer "$TOKENIZER" \
    --tokenizer-output-dir "$WORK/tok_eod_s4" \
    --mode content --dtype int32 \
    >> "/tmp/mix_base_tok_s4.log" 2>&1
rc=$?
echo "  [shard s4] done rc=$rc @ $(date '+%F %T')" >> "$LOG"

# 3) 报告 token 数
if [ -f "$OUTDIR/mix_base_train_s4.json" ]; then
    "$PY/python" -c "import json; d=json.load(open('$OUTDIR/mix_base_train_s4.json')); print(f'  s4 tokens: {d[\"num_tokens\"]:,}')" >> "$LOG" 2>&1
fi
echo "===== tokenize zh DONE @ $(date '+%F %T') =====" >> "$LOG"
