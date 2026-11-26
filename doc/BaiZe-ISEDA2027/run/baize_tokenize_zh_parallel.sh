#!/bin/bash
# Tokenize ultrafineweb_zh (256 parquet, ~301GB) → 8 parallel shards s4..s11
# 2026-10-07 用户直令: 分词加大并发 (单进程 ETA ~2.5d → 8 进程目标 ≤12h)
# 护栏: nice -n 10 (BO已结束, 不必再19) · setsid nohup · 盯GPIC速率
# 输出: data/mix_base/mix_base_train_s{4..11} (续 s0-s3 的 22.05B tok → 扩展至 ~100B)
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_zh
OUTDIR="$BASE/data/mix_base"
WORK=/tmp/mix_base_tok_zh_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=8
TOTAL_FILES=256
PER_SHARD=$((TOTAL_FILES / N_SHARDS))  # 32

LOGDIR=/tmp/baize_tokenize_zh_par
mkdir -p "$OUTDIR" "$WORK" "$LOGDIR"

MAIN_LOG="$LOGDIR/main.log"
echo "===== tokenize zh PARALLEL START @ $(date '+%F %T') (N=$N_SHARDS, $PER_SHARD files/shard) =====" > "$MAIN_LOG"

PIDS=()

for ((i=0; i<N_SHARDS; i++)); do
    SHARD=$((i + 4))   # s4, s5, ..., s11
    START=$((i * PER_SHARD + 1))
    END=$(((i + 1) * PER_SHARD))

    # 1) 建 symlink 子目录
    D="$WORK/s${SHARD}"
    mkdir -p "$D"
    rm -f "$D"/*.snappy.parquet 2>/dev/null
    for ((f=START; f<=END; f++)); do
        PADDED=$(printf "%03d" "$f")
        SRC_FILE="$SRC/ultrafineweb-zh-part-${PADDED}-of-256.parquet"
        ln -sf "$SRC_FILE" "$D/ultrafineweb-zh-part-${PADDED}-of-256.snappy.parquet"
    done
    NFLINKS=$(ls "$D"/*.snappy.parquet 2>/dev/null | wc -l)
    echo "  [shard s${SHARD}] files ${START}-${END} → ${NFLINKS} symlinks" >> "$MAIN_LOG"

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
    echo "  [shard s${SHARD}] PID=$PID 启动 @ $(date '+%F %T') (nice -n 10)" >> "$MAIN_LOG"
done

echo "  All $N_SHARDS processes launched: ${PIDS[*]}" >> "$MAIN_LOG"
echo "  PIDs: ${PIDS[*]}"

# 3) 等待所有完成
FAIL=0
for ((i=0; i<N_SHARDS; i++)); do
    SHARD=$((i + 4))
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
    SHARD=$((i + 4))
    JF="$OUTDIR/mix_base_train_s${SHARD}.json"
    if [ -f "$JF" ]; then
        TOK=$("$PY/python" -c "import json; print(json.load(open('$JF'))['num_tokens'])" 2>/dev/null)
        echo "  s${SHARD}: ${TOK} tokens" >> "$MAIN_LOG"
        TOTAL_TOK=$((TOTAL_TOK + TOK))
    else
        echo "  s${SHARD}: .json MISSING" >> "$MAIN_LOG"
    fi
done
echo "  TOTAL zh tokens: ${TOTAL_TOK}" >> "$MAIN_LOG"
echo "  Failed shards: $FAIL" >> "$MAIN_LOG"
echo "===== tokenize zh PARALLEL DONE @ $(date '+%F %T') =====" >> "$MAIN_LOG"
