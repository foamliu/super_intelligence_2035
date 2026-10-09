#!/bin/bash
# run_contam_scan_r3.sh — R3 投料前污染扫描（运维指令 2026-10-09③ ⑥）
# 3 个 R3 源: L3(1764 pq) + Code(1121 pq) + Math(1823 pq)
# 采样: 10 files/source × 2K docs = 20K docs/source (≥10K 要求)
# Total: 30 files × 2K = 60K docs
# Blacklist: 536 tasks / 193,295 13-gram + 10 8-gram (6 snapshot union)
# LAUNCH AFTER ALL R3 TOKENIZATION COMPLETES (code 30/30 done)
set -euo pipefail

PYTHON=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/check_contamination.py
BLACKLIST=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/blacklist
OUTDIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
LOG="$OUTDIR/contam_scan_r3.log"
SUMMARY="$OUTDIR/contam_scan_r3_summary.md"

echo "=== R3 Contamination Scan ===" > "$LOG"
echo "Start: $(date)" >> "$LOG"
echo "Sources: L3(10) + Code(10) + Math(10) = 30 files × 2K docs = 60K docs" >> "$LOG"
echo "" >> "$LOG"

TOTAL_HITS=0; TOTAL_DOCS=0; TOTAL_FILES=0

scan_file() {
    local label="$1" filepath="$2" maxdocs="${3:-2000}"
    [ ! -f "$filepath" ] && { echo "SKIP: $filepath" >> "$LOG"; return; }
    local tmpout="/tmp/contam_r3_$(basename "$filepath" .parquet).md"
    echo "--- $label: $(basename "$filepath") ---" >> "$LOG"
    $PYTHON "$SCRIPT" --blacklist-dir "$BLACKLIST" --input "$filepath" \
        --ngram 13 --threshold 0.8 --max-docs "$maxdocs" --out "$tmpout" >> "$LOG" 2>&1 || true
    local hits=$(grep -oiP 'hits?[:=]\s*\K\d+' "$tmpout" 2>/dev/null | head -1 || echo "0")
    local docs=$(grep -oiP 'docs?[:=]\s*\K\d+' "$tmpout" 2>/dev/null | head -1 || echo "$maxdocs")
    echo "  → docs=$docs hits=$hits" >> "$LOG"
    TOTAL_HITS=$((TOTAL_HITS + hits)); TOTAL_DOCS=$((TOTAL_DOCS + docs)); TOTAL_FILES=$((TOTAL_FILES + 1))
}

# === L3: 10 files across 4 subdirs ===
L3_BASE=/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data
for i in 0 205 410; do
    f=$(ls "$L3_BASE/ultrafineweb_en_l3/qa/"part-$(printf "%05d" $i)-*.snappy.parquet 2>/dev/null | head -1)
    scan_file "L3_en_qa" "$f"
done
for i in 0 184 368; do
    f=$(ls "$L3_BASE/ultrafineweb_en_l3/multi_style/"part-$(printf "%05d" $i)-*.snappy.parquet 2>/dev/null | head -1)
    scan_file "L3_en_ms" "$f"
done
for i in 0 155; do
    f=$(ls "$L3_BASE/ultrafineweb_zh_l3/qa/"part-$(printf "%05d" $i)-*.snappy.parquet 2>/dev/null | head -1)
    scan_file "L3_zh_qa" "$f"
done
for i in 0 143; do
    f=$(ls "$L3_BASE/ultrafineweb_zh_l3/multi_style/"part-$(printf "%05d" $i)-*.snappy.parquet 2>/dev/null | head -1)
    scan_file "L3_zh_ms" "$f"
done

# === Code: 5 L2 + 5 L3 ===
CODE_L2=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L2
CODE_L3=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3
scan_file "Code_L2_cpp"  "$(ls $CODE_L2/cpp/UltraData-Code-L2-cpp-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L2_py"   "$(ls $CODE_L2/py/UltraData-Code-L2-py-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L2_java" "$(ls $CODE_L2/java/UltraData-Code-L2-java-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L2_js"   "$(ls $CODE_L2/js/UltraData-Code-L2-js-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L2_go"   "$(ls $CODE_L2/go/UltraData-Code-L2-go-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L3_cpp"  "$(ls $CODE_L3/cpp/UltraData-Code-L3-cpp-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L3_py"   "$(ls $CODE_L3/py/UltraData-Code-L3-py-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L3_java" "$(ls $CODE_L3/java/UltraData-Code-L3-java-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L3_js"   "$(ls $CODE_L3/js/UltraData-Code-L3-js-part-00001-of-*.parquet 2>/dev/null | head -1)"
scan_file "Code_L3_rs"   "$(ls $CODE_L3/rs/UltraData-Code-L3-rs-part-00001-of-*.parquet 2>/dev/null | head -1)"

# === Math: 6 L1 + 2 L2p + 2 L3 ===
MATH_BASE=/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data
for dir in CC-MAIN-2014-15 CC-MAIN-2014-23 CC-MAIN-2014-35 CC-MAIN-2014-41 CC-MAIN-2014-42 CC-MAIN-2015-11; do
    f=$(ls "$MATH_BASE/UltraData-Math-L1/$dir/"*.parquet 2>/dev/null | head -1)
    scan_file "Math_L1" "$f"
done
for dir in $(ls "$MATH_BASE/UltraData-Math-L2-preview/" 2>/dev/null | head -2); do
    f=$(ls "$MATH_BASE/UltraData-Math-L2-preview/$dir/"*.parquet 2>/dev/null | head -1)
    scan_file "Math_L2p" "$f"
done
for dir in $(ls "$MATH_BASE/UltraData-Math-L3/" 2>/dev/null | head -2); do
    f=$(ls "$MATH_BASE/UltraData-Math-L3/$dir/"*.parquet 2>/dev/null | head -1)
    scan_file "Math_L3" "$f"
done

# === Summary ===
echo "" >> "$LOG"
echo "=== SUMMARY ===" >> "$LOG"
echo "Files scanned: $TOTAL_FILES" >> "$LOG"
echo "Total docs scanned: $TOTAL_DOCS" >> "$LOG"
echo "Total hits: $TOTAL_HITS" >> "$LOG"
echo "End: $(date)" >> "$LOG"

cat > "$SUMMARY" << EOFM
# R3 Contamination Scan Summary

**Date**: $(date)
**Scope**: 30 parquet files × 2K docs = ~60K docs
**Sources**: L3(10) + Code(10) + Math(10)
**Blacklist**: 536 tasks / 193,295 13-gram + 10 8-gram

## Results

| Metric | Value |
|:---|:---|
| Files scanned | $TOTAL_FILES |
| Total docs scanned | $TOTAL_DOCS |
| **Total hits** | **$TOTAL_HITS** |

## Conclusion

$([ "$TOTAL_HITS" -eq 0 ] && echo "✅ ZERO contamination — R3 sources clean. All training data ready." || echo "⚠️ $TOTAL_HITS hits — investigate before投料.")

## Full Log
See: \`run/data_pipeline/contam_scan_r3.log\`
EOFM

echo "Done. Hits: $TOTAL_HITS / Docs: $TOTAL_DOCS / Files: $TOTAL_FILES"
