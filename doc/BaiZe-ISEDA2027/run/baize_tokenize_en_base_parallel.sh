#!/bin/bash
# Tokenize ultrafineweb_en base 子样本 → 10 parallel shards s24..s33
# 2026-10-08: en base 主体子样本。s0-s3 已分前 48 parquet(part-0001..0048, 22.05B tok)
#   本次取后续 450 parquet(part-0049..0498, ~202B tok 留余量) → 10 进程并行续 s24
# 护栏: nice -n 10 · setsid nohup · 盯GPIC速率 · 别打满NFS
# 输出: data/mix_base/mix_base_train_s{24..33}
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en
OUTDIR="$BASE/data/mix_base"
WORK=/tmp/mix_base_tok_en_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=10
SHARD_OFFSET=24   # s24..s33
START_FILE=49     # 跳过已分的 part-0001..0048
N_FILES=450       # part-0049..0498, ~202B tok
PER_SHARD=$((N_FILES / N_SHARDS))   # 45
REMAINDER=$((N_FILES % N_SHARDS))

LOGDIR=/tmp/baize_tokenize_en_par
mkdir -p "$OUTDIR" "$WORK" "$LOGDIR"

MAIN_LOG="$LOGDIR/main.log"
echo "===== tokenize en_base PARALLEL START @ $(date '+%F %T') (N=$N_SHARDS, $N_FILES files, ~$PER_SHARD files/shard) =====" > "$MAIN_LOG"

PIDS=()

for ((i=0; i<N_SHARDS; i++)); do
    SHARD=$((i + SHARD_OFFSET))
    # 最后一个 shard 吃 remainder
    if (( i == N_SHARDS - 1 )); then
        COUNT=$((PER_SHARD + REMAINDER))
    else
        COUNT=$PER_SHARD
    fi
    FSTART=$((START_FILE + i*PER_SHARD))

    # 1) 建 symlink 子目录
    D="$WORK/s${SHARD}"
    mkdir -p "$D"
    rm -f "$D"/*.snappy.parquet 2>/dev/null

    for ((j=0; j<COUNT; j++)); do
        FN=$((FSTART + j))
        PADDED=$(printf "%04d" "$FN")
        SRC_FILE="$SRC/ultrafineweb-en-part-${PADDED}-of-2048.parquet"
        if [ -f "$SRC_FILE" ]; then
            ln -sf "$SRC_FILE" "$D/ultrafineweb-en-part-${PADDED}-of-2048.snappy.parquet"
        else
            echo "  [shard s${SHARD}] ❌ MISSING $SRC_FILE" >> "$MAIN_LOG"
        fi
    done
    NFLINKS=$(ls "$D"/*.snappy.parquet 2>/dev/null | wc -l)
    echo "  [shard s${SHARD}] files ${FSTART}-$((FSTART+COUNT-1)) → ${NFLINKS} symlinks" >> "$MAIN_LOG"

    # 2) 启动分词进程 (nice -n 10)
    SHARD_LOG="$LOGDIR/s${SHARD}.log"
    nice -n 10 "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$D" \
        --output-prefix "$OUTDIR/mix_base_train_s${SHARD}" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_s${SHARD}" \
        --mode content --dtype int32 \
        >> "$SHARD_LOG" 2>&1 &
    PID=$!
    PIDS+=($PID)
    echo "  [shard s${SHARD}] PID=$PID 启动 @ $(date '+%F %T') (nice -n 10, $COUNT files)" >> "$MAIN_LOG"
done

echo "  All $N_SHARDS processes launched: ${PIDS[*]}" >> "$MAIN_LOG"
echo "  PIDs: ${PIDS[*]}"

# 3) 等待所有完成
FAIL=0
for ((i=0; i<N_SHARDS; i++)); do
    SHARD=$((i + SHARD_OFFSET))
    if wait "${PIDS[$i]}"; then
        echo "  [shard s${SHARD}] DONE OK @ $(date '+%F %T')" >> "$MAIN_LOG"
    else
        echo "  [shard s${SHARD}] FAILED rc=$? @ $(date '+%F %T')" >> "$MAIN_LOG"
        FAIL=$((FAIL + 1))
    fi
done

# 4) 报告 token 数
echo "  --- Summary ---" >> "$MAIN_LOG"
TOTAL_TOK=0
for ((i=0; i<N_SHARDS; i++)); do
    SHARD=$((i + SHARD_OFFSET))
    JF="$OUTDIR/mix_base_train_s${SHARD}.json"
    if [ -f "$JF" ]; then
        TOK="$("$PY/python" -c "import json; print(json.load(open('$JF'))['num_tokens'])" 2>/dev/null)"
        echo "  s${SHARD}: ${TOK} tokens" >> "$MAIN_LOG"
        TOTAL_TOK=$((TOTAL_TOK + TOK))
    else
        echo "  s${SHARD}: .json MISSING" >> "$MAIN_LOG"
    fi
done
echo "  TOTAL en_base tokens: ${TOTAL_TOK}" >> "$MAIN_LOG"
echo "  Failed shards: $FAIL" >> "$MAIN_LOG"
echo "===== tokenize en_base PARALLEL DONE @ $(date '+%F %T') ===== " >> "$MAIN_LOG"