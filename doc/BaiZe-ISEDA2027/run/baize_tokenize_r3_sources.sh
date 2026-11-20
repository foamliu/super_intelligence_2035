#!/bin/bash
# BaiZe R3 数据配比 BO 搜索 — 小样本分词前置：6 源 × 2 parquet → 6 个 .bin/.idx
#
# 按 BAIZE_DATA_R3_TASK.md §3.2 规格：
#   - ultrafineweb_en      (content)          2 parquet
#   - ultrafineweb_zh      (content)          1 parquet (256 total, 取 2)
#   - ultrafineweb_l1_en_hq(content)          2 parquet
#   - ultrax_preview       (cleaned_content)  2 parquet
#   - ultradata_code       (content)          2 parquet (跨语言 py+cpp)
#   - ultradata_math       (content)          2 parquet
#
# 6 进程并行，输出到 {BASE}/data/r3_sources/r3_{source_name}.bin/.idx/.json
# 预计 ~30 min（I/O bound, 6 进程不线性加速但 30 min 足够）
#
# 启动：bash baize_tokenize_r3_sources.sh
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
OUTDIR="$BASE/data/r3_sources"
WORK=/tmp/r3_tok_work
TOKENIZER=/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:${PYTHONPATH:-}

SUM=/tmp/baize_tokenize_r3_sources.log
mkdir -p "$OUTDIR" "$WORK"
echo "===== R3 tokenize START @ $(date '+%F %T') (6 sources × 2 parquet → r3_sources/) =====" > "$SUM"

# ── helper: symlink 2 parquets into a work dir with .snappy.parquet suffix ──
setup_source() {
    local name="$1" col="$2"; shift 2
    local d="$WORK/r3_${name}"
    mkdir -p "$d"
    local i=0
    for src in "$@"; do
        local base=$(basename "$src" .parquet)
        ln -sf "$src" "$d/${base}.snappy.parquet"
        i=$((i+1))
    done
    echo "  [$name] $i parquet → $d (col=$col)" >> "$SUM"
}

# ── 6 sources ──
UFW=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data
ULTRAX=/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/data/UltraX-FineWeb
UDCODE=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3
UDMATH=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L1

setup_source ultrafineweb_en content \
    "$UFW/ultrafineweb_en/ultrafineweb-en-part-0001-of-2048.parquet" \
    "$UFW/ultrafineweb_en/ultrafineweb-en-part-0002-of-2048.parquet"

setup_source ultrafineweb_zh content \
    "$UFW/ultrafineweb_zh/ultrafineweb-zh-part-001-of-256.parquet" \
    "$UFW/ultrafineweb_zh/ultrafineweb-zh-part-002-of-256.parquet"

setup_source ultrafineweb_l1_en_hq content \
    "$UFW/ultrafineweb_l1_en_hq/CC-MAIN-2025-30/ultrafineweb-l1-en-hq-CC-MAIN-2025-30-part-0001-of-1000.parquet" \
    "$UFW/ultrafineweb_l1_en_hq/CC-MAIN-2025-30/ultrafineweb-l1-en-hq-CC-MAIN-2025-30-part-0002-of-1000.parquet"

setup_source ultrax_preview cleaned_content \
    "$ULTRAX/UltraX-FineWeb-en-part-0001-of-0104.parquet" \
    "$ULTRAX/UltraX-FineWeb-en-part-0002-of-0104.parquet"

setup_source ultradata_code content \
    "$UDCODE/py/UltraData-Code-L3-py-part-00001-of-00147.parquet" \
    "$UDCODE/cpp/UltraData-Code-L3-cpp-part-00001-of-00167.parquet"

setup_source ultradata_math content \
    "$UDMATH/CC-MAIN-2014-15/UltraData-Math-L1-CC-MAIN-2014-15-part-0001-of-15.parquet" \
    "$UDMATH/CC-MAIN-2014-15/UltraData-Math-L1-CC-MAIN-2014-15-part-0002-of-15.parquet"

# ── 6 processes in parallel ──
pids=()
names=(ultrafineweb_en ultrafineweb_zh ultrafineweb_l1_en_hq ultrax_preview ultradata_code ultradata_math)
cols=(content content content cleaned_content content content)

for idx in "${!names[@]}"; do
    nm="${names[$idx]}"
    cl="${cols[$idx]}"
    echo "  [$nm] tokenize START @ $(date '+%F %T') (col=$cl)" >> "$SUM"
    "$PY/python" "$BASE/mamba2_hybrid_2b/preprocess_data.py" \
        --input-dir "$WORK/r3_${nm}" \
        --output-prefix "$OUTDIR/r3_${nm}" \
        --tokenizer "$TOKENIZER" \
        --tokenizer-output-dir "$WORK/r3_tok_${nm}" \
        --mode content --text-column "$cl" --dtype int32 \
        > "/tmp/r3_tok_${nm}.log" 2>&1 &
    pids+=($!)
done

# ── wait all ──
rc=0
for i in "${!pids[@]}"; do
    if ! wait "${pids[$i]}"; then
        echo "  ❌ ${names[$i]} 失败，见 /tmp/r3_tok_${names[$i]}.log" >> "$SUM"; rc=1
    else
        echo "  ✅ ${names[$i]} 完成" >> "$SUM"
    fi
done

# ── summary ──
TOTAL=0
for nm in "${names[@]}"; do
    tok=$("$PY/python" -c "import json;print(json.load(open('$OUTDIR/r3_${nm}.json'))['num_tokens'])" 2>/dev/null || echo 0)
    echo "  $nm tokens = $tok" >> "$SUM"
    TOTAL=$((TOTAL + tok))
done
echo "  TOTAL tokens = $TOTAL (≈$((TOTAL/1000000000)).$((TOTAL%1000000000/100000000)) B)" >> "$SUM"
echo "===== R3 tokenize ALL DONE @ $(date '+%F %T') rc=$rc =====" >> "$SUM"
exit $rc
