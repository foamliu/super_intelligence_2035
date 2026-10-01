#!/bin/bash
# BaiZe Stage(i) R2 P-5b 前置：分词打包 ~25B token 的 L3 en 主体（供 loss-vs-tokens scaling 曲线 20B token）。
# 背景：P-5b（loss-vs-tokens 曲线，决定 P-8 的 token 预算）需从零训到 20B token，
#   但现有 .bin/.idx 仅 ~1.26B token（L3 700m 742M + code 90M + math2 430M），远不够。
#   完整 L3 en（690B token / 616 parquet @ /nas_inference）早已下全，data agent 的 phase2 分词
#   仍在等 base 下载完成，故本任务自行分词 ~25B token 的 L3 切片（P-5b 专属，非 P-8 全量 body）。
#   ✅ 复用 Round 1 的 preprocess_data.py（已证实可用）；纯 L3 `qa` content 列，与 P-5a/P-1 同源同口径。
#
# 策略：前 24 个 parquet（part-00000..00023，排序=数字序，每片 ~1.12B token）≈26.9B token，
#   均分 8 组 × 3 片，8 进程并行分词 → 8 个 .bin/.idx 分片；训练时用 1:1 等权 blend 合并。
#   （单进程分词 ~450K tok/s，25B 需 ~15h；8 进程并行 ~2h。）
# 起始：setsid bash baize_p5b_tokenize.sh &   （PPID=1 真后台，勿裸 nohup &）
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
SRC=/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa
OUTDIR="$BASE/data/p5b_l3"
WORK=/tmp/p5b_tok_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

N_SHARDS=8
FILES_PER_SHARD=3
N_FILES=$((N_SHARDS * FILES_PER_SHARD))   # 24

SUM=/tmp/baize_p5b_tokenize.log
mkdir -p "$OUTDIR" "$WORK"
echo "===== P-5b tokenize START @ $(date '+%F %T') (L3 en first ${N_FILES} parquet -> ${N_SHARDS} shards) =====" > "$SUM"

# 1) 取排序后前 N_FILES 个 parquet（零填充故字母序=数字序）
mapfile -t ALL < <(ls "$SRC"/*.snappy.parquet | sort | head -"$N_FILES")
if [ "${#ALL[@]}" -lt "$N_FILES" ]; then
    echo "❌ 仅找到 ${#ALL[@]} 个 parquet，少于 ${N_FILES}" | tee -a "$SUM"; exit 1
fi
echo "  前 ${N_FILES} 个 parquet：$(basename "${ALL[0]}") ... $(basename "${ALL[$((N_FILES-1))]}")" >> "$SUM"

# 2) 建 8 个符号链接子目录（每目录 3 片）
for s in $(seq 0 $((N_SHARDS-1))); do
    d="$WORK/s$s"
    mkdir -p "$d"
    for j in $(seq 0 $((FILES_PER_SHARD-1))); do
        idx=$((s*FILES_PER_SHARD + j))
        ln -sf "${ALL[$idx]}" "$d/part-$(printf '%03d' "$idx").snappy.parquet"
    done
done

# 3) 8 进程并行分词
pids=()
for s in $(seq 0 $((N_SHARDS-1))); do
    echo "  [shard $s] 启动 @ $(date '+%F %T')" >> "$SUM"
    "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$WORK/s$s" \
        --output-prefix "$OUTDIR/p5b_l3_train_s$s" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/tok_eod_s$s" \
        --mode content --dtype int32 \
        > "/tmp/p5b_tok_s$s.log" 2>&1 &
    pids+=($!)
done

rc=0
for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
        echo "  ❌ shard $i 失败，见 /tmp/p5b_tok_s$i.log" >> "$SUM"; rc=1
    else
        echo "  ✅ shard $i 完成" >> "$SUM"
    fi
done

# 4) 汇总 token 数
TOTAL=0
for s in $(seq 0 $((N_SHARDS-1))); do
    tok=$(python -c "import json;print(json.load(open('$OUTDIR/p5b_l3_train_s$s.json'))['num_tokens'])" 2>/dev/null || echo 0)
    echo "  shard $s tokens = $tok" >> "$SUM"
    TOTAL=$((TOTAL + tok))
done
echo "  TOTAL tokens = $TOTAL (≈$((TOTAL/1000000000)).$((TOTAL%1000000000/100000000)) B)" >> "$SUM"
echo "===== P-5b tokenize ALL DONE @ $(date '+%F %T') rc=$rc =====" >> "$SUM"
exit $rc