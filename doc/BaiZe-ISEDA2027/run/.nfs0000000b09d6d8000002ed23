#!/bin/bash
# BaiZe 数据配比实验（§0.6-B）前置：分词打包 SFT-2605 全量（12 parquet → 4 shards .bin/.idx）。
# 供 Decay 段配比实验的 SFT 主体（Xmodel-2 最优 SFT 占比 64%）。
# ✅ 复用 pretrain 的 preprocess_data.py（已证实可用）；SFT parquet 有 content 列（convert_sft_to_parquet.py 产出）。
#
# 策略：12 个 SFT parquet（合计 ~30GB）按大小分 4 组，4 进程并行分词（降低 I/O 压力，避让 P-9.9 训练）。
#   分组（按大小平衡）：
#     shard 0: no_think_Math (13.2GB)              ← 最大，单独一组
#     shard 1: think_Code (7.0G) + no_think_Code (3.6G) = 10.6GB
#     shard 2: Multi-lang-Kn (2.9G) + think_Math (1.3G) + no_think_Kn (762M) + think_Kn (758M) + ML-Math (865M) = 6.6GB
#     shard 3: no_think_CG (390M) + no_think_IF (250M) + think_CG (355M) + think_IF (197M) = 1.2GB
#
# 启动：ssh 10.239.2.29 'setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_tokenize_sft.sh &'
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC="$BASE/data/mix_sft"
OUTDIR="$BASE/data/mix_sft_tok"
WORK=/tmp/mix_sft_tok_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

SUM=/tmp/baize_mix_tokenize_sft.log
mkdir -p "$OUTDIR" "$WORK"
echo "===== mix_sft_tok tokenize START @ $(date '+%F %T') (12 SFT-2605 parquet -> 4 shards) =====" > "$SUM"

# 分组定义（文件名不含路径，在 $SRC 下找）
# shard 0: no_think_Math (13.2GB)
SHARD0=("sft_no_think_Math.parquet")
# shard 1: think_Code (7.0G) + no_think_Code (3.6G) = 10.6GB
SHARD1=("sft_think_Code.parquet" "sft_no_think_Code.parquet")
# shard 2: Multi-lang-Kn (2.9G) + think_Math (1.3G) + no_think_Kn (762M) + think_Kn (758M) + ML-Math (865M) = 6.6GB
SHARD2=("sft_no_think_Multi-lang-Knowledge.parquet" "sft_think_Math.parquet" "sft_no_think_Knowledge.parquet" "sft_think_Knowledge.parquet" "sft_no_think_Multi-lang-Math.parquet")
# shard 3: no_think_CG (390M) + no_think_IF (250M) + think_CG (355M) + think_IF (197M) = 1.2GB
SHARD3=("sft_no_think_Chinese-general.parquet" "sft_no_think_IF.parquet" "sft_think_Chinese-general.parquet" "sft_think_IF.parquet")

declare -n SHARDS
SHARDS=(SHARD0 SHARD1 SHARD2 SHARD3)

rc=0
pids=()
for s in 0 1 2 3; do
    d="$WORK/s$s"
    mkdir -p "$d"
    # 清理旧软链
    rm -f "$d"/*.snappy.parquet 2>/dev/null
    nameref="SHARD$s"
    files="${nameref}[@]"
    for f in "${!files}"; do
        src_path="$SRC/$f"
        if [ ! -f "$src_path" ]; then
            echo "  ⚠️ shard $s: $f 不存在，跳过" >> "$SUM"
            continue
        fi
        # preprocess_data.py 只认 *.snappy.parquet → 加 .snappy 后缀做软链
        ln -sf "$src_path" "$d/${f%.parquet}.snappy.parquet"
    done
    n_files=$(ls "$d"/*.snappy.parquet 2>/dev/null | wc -l)
    echo "  [shard $s] $n_files files, 启动 @ $(date '+%F %T')" >> "$SUM"
    "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$d" \
        --output-prefix "$OUTDIR/mix_sft_train_s$s" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_sft_s$s" \
        --mode content --dtype int32 \
        > "/tmp/mix_sft_tok_s$s.log" 2>&1 &
    pids+=($!)
done

for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
        echo "  ❌ shard $i 失败，见 /tmp/mix_sft_tok_s$i.log" >> "$SUM"; rc=1
    else
        echo "  ✅ shard $i 完成" >> "$SUM"
    fi
done

# 汇总 token 数
TOTAL=0
for s in 0 1 2 3; do
    tok=$("$PY/python" -c "import json;print(json.load(open('$OUTDIR/mix_sft_train_s$s.json'))['num_tokens'])" 2>/dev/null || echo 0)
    echo "  shard $s tokens = $tok" >> "$SUM"
    TOTAL=$((TOTAL + tok))
done
echo "  TOTAL tokens = $TOTAL (≈$((TOTAL/1000000000)).$((TOTAL%1000000000/100000000)) B)" >> "$SUM"
echo "===== mix_sft_tok tokenize ALL DONE @ $(date '+%F %T') rc=$rc =====" >> "$SUM"
exit $rc
