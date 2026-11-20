#!/bin/bash
# BaiZe 数据配比实验（§0.6-B）前置：转换+分词 SFT-Agent-2609（4 子目录 jsonl → 4 parquet → 4 shards .bin/.idx）。
# 供 Decay 段配比实验的 SFT-Agent 主体。
# ✅ 复用 convert_sft_to_parquet.py（jsonl messages→parquet content 列）+ preprocess_data.py（parquet→.bin/.idx）。
#
# SFT-Agent-2609 结构：data/{Code_Agent,General_Agent,Search_Agent,Tool_Use}/*.jsonl (50 files, 51G)
# 策略：4 子目录 → 4 parquet → 4 shard 分词，并行（CPU-only，不占 GPU）。
#
# 启动：ssh 10.239.2.29 'setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_tokenize_agent.sh &'
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SCRIPT_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
SRC=/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609/data
PARQUET_OUT="$BASE/data/mix_sft_agent"
BIN_OUT="$BASE/data/mix_sft_agent_tok"
WORK=/tmp/mix_sft_agent_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

SUM=/tmp/baize_mix_tokenize_agent.log
mkdir -p "$PARQUET_OUT" "$BIN_OUT" "$WORK"
echo "===== mix_sft_agent tokenize START @ $(date '+%F %T') (50 jsonl -> 4 parquet -> 4 shards) =====" > "$SUM"

# Step 1: Convert each subdir to parquet (sequential — I/O bound, parallelism won't help on NFS)
SUBDIRS=(Code_Agent General_Agent Search_Agent Tool_Use)
for sub in "${SUBDIRS[@]}"; do
    echo "  [convert] $sub @ $(date '+%F %T')" >> "$SUM"
    "$PY/python" "$SCRIPT_DIR/convert_sft_to_parquet.py" \
        --input-dir "$SRC/$sub" \
        --output-dir "$PARQUET_OUT" \
        >> "$SUM" 2>&1
    if [ $? -ne 0 ]; then
        echo "  ❌ convert $sub failed" >> "$SUM"
    fi
done

# Step 2: Tokenize each parquet to .bin/.idx (4 shards in parallel)
echo "  [tokenize] Starting 4-shard parallel tokenization @ $(date '+%F %T')" >> "$SUM"

pids=()
for s in 0 1 2 3; do
    sub="${SUBDIRS[$s]}"
    parquet="$PARQUET_OUT/sft_${sub}.parquet"
    if [ ! -f "$parquet" ]; then
        echo "  ⚠️ shard $s ($sub): parquet missing, skip" >> "$SUM"
        continue
    fi
    d="$WORK/s$s"
    mkdir -p "$d"
    rm -f "$d"/*.snappy.parquet 2>/dev/null
    ln -sf "$parquet" "$d/sft_${sub}.snappy.parquet"

    echo "  [shard $s=$sub] tokenize @ $(date '+%F %T')" >> "$SUM"
    "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$d" \
        --output-prefix "$BIN_OUT/mix_sft_agent_train_s$s" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_agent_s$s" \
        --mode content --dtype int32 \
        > "/tmp/mix_sft_agent_s$s.log" 2>&1 &
    pids+=($!)
done

rc=0
for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
        echo "  ❌ shard $i failed, see /tmp/mix_sft_agent_s$i.log" >> "$SUM"; rc=1
    else
        echo "  ✅ shard $i done" >> "$SUM"
    fi
done

# Step 3: Summarize token counts
TOTAL=0
for s in 0 1 2 3; do
    tok=$("$PY/python" -c "import json;print(json.load(open('$BIN_OUT/mix_sft_agent_train_s$s.json'))['num_tokens'])" 2>/dev/null || echo 0)
    echo "  shard $s tokens = $tok" >> "$SUM"
    TOTAL=$((TOTAL + tok))
done
echo "  TOTAL Agent tokens = $TOTAL (≈$((TOTAL/1000000000)).$((TOTAL%1000000000/100000000)) B)" >> "$SUM"
echo "===== mix_sft_agent tokenize ALL DONE @ $(date '+%F %T') rc=$rc =====" >> "$SUM"
exit $rc
