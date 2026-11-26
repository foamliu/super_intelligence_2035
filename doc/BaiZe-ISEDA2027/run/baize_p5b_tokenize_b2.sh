#!/bin/bash
# BaiZe Stage(i) R2 P-5b 前置·数据分词 batch 2：补齐 20B token（batch 1 已产出 10.2B，缺口 ~10B）。
# 背景：batch 1（baize_p5b_tokenize.sh）处理前 24 个 parquet（part-00000..00023）实得 ~10.28B token
#    （每 parquet ~428M token，非初估 1.12B），距 P-5b 目标 20B 缺 ~10B。
# 本脚本：处理 **part-00024..00047**（再 24 片 ≈ +10.28B），产出 s8..s15 共 8 个新分片，
#   与 batch 1 的 s0..s7 合并 → 16 分片 1:1 等权 blend ≈ 20.6B token。
# 复用 baize_p5b_tokenize.sh 的 preprocess_data.py 与分词口径（纯 L3 `qa` content）。
# 起始：setsid bash baize_p5b_tokenize_b2.sh &
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa
OUTDIR="$BASE/data/p5b_l3"
WORK=/tmp/p5b_tok_work_b2
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=8
FILES_PER_SHARD=3
N_FILES=$((N_SHARDS * FILES_PER_SHARD))   # 24
OFFSET=24                                   # 从 part-00024 起
SHARD_START=8                               # 输出 s8..s15

SUM=/tmp/baize_p5b_tokenize_b2.log
mkdir -p "$OUTDIR" "$WORK"
echo "===== P-5b tokenize batch2 START @ $(date '+%F %T') (parquet ${OFFSET}..$((OFFSET+N_FILES-1)) -> shards s${SHARD_START}..s$((SHARD_START+N_SHARDS-1))) =====" > "$SUM"

mapfile -t ALL < <(ls "$SRC"/*.snappy.parquet | sort | tail -n +$((OFFSET+1)) | head -"$N_FILES")
if [ "${#ALL[@]}" -lt "$N_FILES" ]; then
    echo "❌ 仅找到 ${#ALL[@]} 个 parquet（自 offset ${OFFSET} 起），少于 ${N_FILES}" | tee -a "$SUM"; exit 1
fi
echo "  处理 parquet：$(basename "${ALL[0]}") ... $(basename "${ALL[$((N_FILES-1))]}")" >> "$SUM"

for s in $(seq 0 $((N_SHARDS-1))); do
    d="$WORK/s$s"
    mkdir -p "$d"
    for j in $(seq 0 $((FILES_PER_SHARD-1))); do
        idx=$((s*FILES_PER_SHARD + j))
        ln -sf "${ALL[$idx]}" "$d/part-$(printf '%03d' "$idx").snappy.parquet"
    done
done

pids=()
for s in $(seq 0 $((N_SHARDS-1))); do
    out_idx=$((SHARD_START + s))
    echo "  [shard $out_idx] 启动 @ $(date '+%F %T')" >> "$SUM"
    "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$WORK/s$s" \
        --output-prefix "$OUTDIR/p5b_l3_train_s$out_idx" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_s$out_idx" \
        --mode content --dtype int32 \
        > "/tmp/p5b_tok_b2_s$out_idx.log" 2>&1 &
    pids+=($!)
done

rc=0
for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
        echo "  ❌ shard s$((SHARD_START+i)) 失败，见 /tmp/p5b_tok_b2_s$((SHARD_START+i)).log" >> "$SUM"; rc=1
    else
        echo "  ✅ shard s$((SHARD_START+i)) 完成" >> "$SUM"
    fi
done

TOTAL=0
for s in $(seq "$SHARD_START" $((SHARD_START+N_SHARDS-1))); do
    tok=$(python -c "import json;print(json.load(open('$OUTDIR/p5b_l3_train_s$s.json'))['num_tokens'])" 2>/dev/null || echo 0)
    echo "  shard s$s tokens = $tok" >> "$SUM"
    TOTAL=$((TOTAL + tok))
done
echo "  batch2 TOTAL tokens = $TOTAL (≈$((TOTAL/1000000000)) B)" >> "$SUM"
echo "===== P-5b tokenize batch2 DONE @ $(date '+%F %T') rc=$rc ===== " >> "$SUM"
exit $rc