#!/bin/bash
# Tokenize ultrafineweb_l1_en_hq (6000 parquet, ~446GB, 6 CC-MAIN snapshots) → 12 parallel shards s12..s23
# 2026-10-08: 继 zh 分词(s4-s11)后启动, 续 s0-s3(en base 22.05B) + s4-s11(zh) → 扩展至 ~100B tok
# 护栏: nice -n 10 · setsid nohup · 盯GPIC速率 · 别打满NFS
# 输出: data/mix_base/mix_base_train_s{12..23}
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq
OUTDIR="$BASE/data/mix_base"
WORK=/tmp/mix_base_tok_l1_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=12
SHARD_OFFSET=12   # s12, s13, ..., s23

LOGDIR=/tmp/baize_tokenize_l1_par
mkdir -p "$OUTDIR" "$WORK" "$LOGDIR"

# 1) 收集所有 parquet 文件路径 (已排序)
mapfile -t ALL_FILES < <(find "$SRC" -name '*.parquet' | sort)
TOTAL_FILES=${#ALL_FILES[@]}
PER_SHARD=$((TOTAL_FILES / N_SHARDS))
REMAINDER=$((TOTAL_FILES % N_SHARDS))

MAIN_LOG="$LOGDIR/main.log"
echo "===== tokenize l1_en_hq PARALLEL START @ $(date '+%F %T') (N=$N_SHARDS, $TOTAL_FILES files, ~$PER_SHARD files/shard) =====" > "$MAIN_LOG"

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

    # 3) 启动分词进程 (nice -n 10)
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
echo "  TOTAL l1_en_hq tokens: ${TOTAL_TOK}" >> "$MAIN_LOG"
echo "  Failed shards: $FAIL" >> "$MAIN_LOG"
echo "===== tokenize l1_en_hq PARALLEL DONE @ $(date '+%F %T') =====" >> "$MAIN_LOG"
