#!/bin/bash
# Tokenize UltraX-Preview (104 FineWeb + 61 AICC parquet, ~166GB, cleaned_content) → 10 parallel shards s34..s43
# 2026-10-08: UltraX-Preview 偏退火/筛选数据，列名 cleaned_content（异于 content）
# 护栏: nice -n 10 · setsid nohup · 盯GPIC速率 · 别打满NFS
# 输出: data/mix_base/mix_base_train_s{34..43}
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC_FW=/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/data/UltraX-FineWeb
SRC_AICC=/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/data/UltraX-AICC
OUTDIR="$BASE/data/mix_base"
WORK=/tmp/mix_base_tok_ultrax_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=10
SHARD_OFFSET=34   # s34..s43

LOGDIR=/tmp/baize_tokenize_ultrax_par
mkdir -p "$OUTDIR" "$WORK" "$LOGDIR"

MAIN_LOG="$LOGDIR/main.log"
echo "===== tokenize UltraX-Preview PARALLEL START @ $(date '+%F %T') (N=$N_SHARDS, 104+61=165 files) =====" > "$MAIN_LOG"

# 1) 收集所有 parquet 文件路径（FineWeb + AICC，已排序）
mapfile -t ALL_FW < <(ls "$SRC_FW"/UltraX-FineWeb-en-part-*.parquet | sort)
mapfile -t ALL_AICC < <(ls "$SRC_AICC"/UltraX-AICC-en-part-*.parquet | sort)
ALL_FILES=("${ALL_FW[@]}" "${ALL_AICC[@]}")
TOTAL_FILES=${#ALL_FILES[@]}
PER_SHARD=$((TOTAL_FILES / N_SHARDS))
REMAINDER=$((TOTAL_FILES % N_SHARDS))

echo "  FineWeb: ${#ALL_FW[@]} files, AICC: ${#ALL_AICC[@]} files, TOTAL: $TOTAL_FILES" >> "$MAIN_LOG"

PIDS=()
IDX=0

for ((i=0; i<N_SHARDS; i++)); do
    SHARD=$((i + SHARD_OFFSET))
    # 最后一个 shard 吃 remainder
    if (( i == N_SHARDS - 1 )); then
        COUNT=$((PER_SHARD + REMAINDER))
    else
        COUNT=$PER_SHARD
    fi

    # 2) 建 symlink 子目录
    D="$WORK/s${SHARD}"
    mkdir -p "$D"
    rm -f "$D"/*.snappy.parquet 2>/dev/null

    for ((j=0; j<COUNT; j++)); do
        SRC_FILE="${ALL_FILES[$IDX]}"
        BASENAME=$(basename "$SRC_FILE")
        ln -sf "$SRC_FILE" "$D/${BASENAME}.snappy.parquet"
        IDX=$((IDX + 1))
    done
    NFLINKS=$(ls "$D"/*.snappy.parquet 2>/dev/null | wc -l)
    echo "  [shard s${SHARD}] ${NFLINKS} symlinks (count=$COUNT)" >> "$MAIN_LOG"

    # 3) 启动分词进程 (nice -n 10, --text-column cleaned_content)
    SHARD_LOG="$LOGDIR/s${SHARD}.log"
    nice -n 10 "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$D" \
        --output-prefix "$OUTDIR/mix_base_train_s${SHARD}" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_s${SHARD}" \
        --text-column cleaned_content \
        --mode content --dtype int32 \
        >> "$SHARD_LOG" 2>&1 &
    PID=$!
    PIDS+=($PID)
    echo "  [shard s${SHARD}] PID=$PID 启动 @ $(date '+%F %T') (nice -n 10, $COUNT files, cleaned_content)" >> "$MAIN_LOG"
done

echo "  All $N_SHARDS processes launched: ${PIDS[*]}" >> "$MAIN_LOG"
echo "  PIDs: ${PIDS[*]}"

# 4) 等待所有完成
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

# 5) 报告 token 数
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
echo "  TOTAL UltraX tokens: ${TOTAL_TOK}" >> "$MAIN_LOG"
echo "  Failed shards: $FAIL" >> "$MAIN_LOG"
echo "===== tokenize UltraX-Preview PARALLEL DONE @ $(date '+%F %T') ===== " >> "$MAIN_LOG"