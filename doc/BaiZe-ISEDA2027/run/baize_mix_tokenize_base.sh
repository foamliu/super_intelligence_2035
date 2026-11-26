#!/bin/bash
# BaiZe 数据配比实验（§0.6-B）前置：分词打包 ~21B token 的 Ultra-FineWeb base (ultrafineweb_en) 子集。
# 供 Stable 段配比实验的 web 主体（与 L3 并列，用于 S1 轴：base vs L3 占比）。
# ✅ 复用 pretrain 的 preprocess_data.py（已证实可用）；base parquet 有 content 列，与 L3 同格式。
#
# 策略：前 48 个 parquet（part-0001..0048-of-2048，每片 ~1.3GB ≈ ~450M token）
#   均分 4 组 × 12 片，4 进程并行分词（降低 I/O 压力，避让 P-9.9 训练）→ 4 个 .bin/.idx 分片。
#   合计 ~21B token，够 5000 步 × GBS=1024 × seq=4094 = ~21B token 的 Stable 段实验。
#
# 启动：ssh 10.239.2.29 'setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_tokenize_base.sh &'
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en
OUTDIR="$BASE/data/mix_base"
WORK=/tmp/mix_base_tok_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=4
FILES_PER_SHARD=12
N_FILES=$((N_SHARDS * FILES_PER_SHARD))   # 48

SUM=/tmp/baize_mix_tokenize_base.log
mkdir -p "$OUTDIR" "$WORK"
echo "===== mix_base tokenize START @ $(date '+%F %T') (ultrafineweb_en first ${N_FILES} parquet -> ${N_SHARDS} shards) =====" > "$SUM"

# 1) 取排序后前 N_FILES 个 parquet
mapfile -t ALL < <(ls "$SRC"/ultrafineweb-en-part-*.parquet | sort | head -"$N_FILES")
if [ "${#ALL[@]}" -lt "$N_FILES" ]; then
    echo "❌ 仅找到 ${#ALL[@]} 个 parquet，少于 ${N_FILES}" | tee -a "$SUM"; exit 1
fi
echo "  前 ${N_FILES} 个 parquet：$(basename "${ALL[0]}") ... $(basename "${ALL[$((N_FILES-1))]}")" >> "$SUM"

# 2) 建 N_SHARDS 个符号链接子目录
for s in $(seq 0 $((N_SHARDS-1))); do
    d="$WORK/s$s"
    mkdir -p "$d"
    for j in $(seq 0 $((FILES_PER_SHARD-1))); do
        idx=$((s*FILES_PER_SHARD + j))
        # preprocess_data.py 只认 *.snappy.parquet，base 文件名是 *.parquet → 加 .snappy 后缀做软链
        ln -sf "${ALL[$idx]}" "$d/$(basename "${ALL[$idx]}" .parquet).snappy.parquet"
    done
done

# 3) N_SHARDS 进程并行分词（4 进程，降低 I/O 压力）
pids=()
for s in $(seq 0 $((N_SHARDS-1))); do
    echo "  [shard $s] 启动 @ $(date '+%F %T')" >> "$SUM"
    "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$WORK/s$s" \
        --output-prefix "$OUTDIR/mix_base_train_s$s" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_s$s" \
        --mode content --dtype int32 \
        > "/tmp/mix_base_tok_s$s.log" 2>&1 &
    pids+=($!)
done

rc=0
for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
        echo "  ❌ shard $i 失败，见 /tmp/mix_base_tok_s$i.log" >> "$SUM"; rc=1
    else
        echo "  ✅ shard $i 完成" >> "$SUM"
    fi
done

# 4) 汇总 token 数
TOTAL=0
for s in $(seq 0 $((N_SHARDS-1))); do
    tok=$("$PY/python" -c "import json;print(json.load(open('$OUTDIR/mix_base_train_s$s.json'))['num_tokens'])" 2>/dev/null || echo 0)
    echo "  shard $s tokens = $tok" >> "$SUM"
    TOTAL=$((TOTAL + tok))
done
echo "  TOTAL tokens = $TOTAL (≈$((TOTAL/1000000000)).$((TOTAL%1000000000/100000000)) B)" >> "$SUM"
echo "===== mix_base tokenize ALL DONE @ $(date '+%F %T') rc=$rc =====" >> "$SUM"
exit $rc
