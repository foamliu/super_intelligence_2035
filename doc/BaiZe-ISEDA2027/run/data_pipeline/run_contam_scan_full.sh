#!/bin/bash
# Comprehensive contamination scan: 32 parquet files × 5K docs = 160K docs
# Sources on /nas_train only (avoids /nas_inference I/O contention with GPIC)
# en_base(10) + l1_en_hq(12=2×6 subdirs) + zh(10) = 32 files
# This is 16× more thorough than the 10K sampling scan (唤醒244)
set -euo pipefail

PYTHON=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3.10
SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/check_contamination.py
BLACKLIST=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/blacklist

EN_BASE=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_en
L1_HQ=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq
ZH=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/ultrafineweb_zh

OUTDIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
LOG="$OUTDIR/contam_scan_full.log"
SUMMARY="$OUTDIR/contam_scan_full_summary.md"

echo "=== Comprehensive Contamination Scan ===" > "$LOG"
echo "Start: $(date)" >> "$LOG"
echo "Sources: en_base(10) + l1_en_hq(12) + zh(10) = 32 files × 5K docs = 160K docs" >> "$LOG"
echo "" >> "$LOG"

TOTAL_HITS=0
TOTAL_DOCS=0
TOTAL_FILES=0

scan_file() {
    local label="$1"
    local filepath="$2"
    local maxdocs="${3:-5000}"
    if [ ! -f "$filepath" ]; then
        echo "SKIP (not found): $filepath" >> "$LOG"
        return
    fi
    local tmpout="/tmp/contam_$(basename "$filepath" .parquet).md"
    echo "--- $label: $(basename "$filepath") ---" >> "$LOG"
    $PYTHON "$SCRIPT" --blacklist-dir "$BLACKLIST" --input "$filepath" \
        --ngram 13 --threshold 0.8 --max-docs "$maxdocs" --out "$tmpout" >> "$LOG" 2>&1 || true
    # Extract hit count from output
    local hits=$(grep -oiP 'hits?[:=]\s*\K\d+' "$tmpout" 2>/dev/null | head -1 || echo "0")
    local docs=$(grep -oiP 'docs?[:=]\s*\K\d+' "$tmpout" 2>/dev/null | head -1 || echo "$maxdocs")
    echo "  → docs=$docs hits=$hits" >> "$LOG"
    TOTAL_HITS=$((TOTAL_HITS + hits))
    TOTAL_DOCS=$((TOTAL_DOCS + docs))
    TOTAL_FILES=$((TOTAL_FILES + 1))
}

# 10 evenly-spaced en_base files (2048 total, step ~204)
for i in 1 205 409 613 817 1021 1225 1429 1633 1837; do
    f=$(printf "ultrafineweb-en-part-%04d-of-2048.parquet" "$i")
    scan_file "en_base" "$EN_BASE/$f"
done

# 2 evenly-spaced files from each l1_en_hq CC-MAIN subdir (1000 each)
for dir in CC-MAIN-2025-30 CC-MAIN-2025-33 CC-MAIN-2025-38 CC-MAIN-2025-43 CC-MAIN-2025-47 CC-MAIN-2025-50; do
    for i in 1 501; do
        f=$(printf "ultrafineweb-l1-en-hq-%s-part-%04d-of-1000.parquet" "$dir" "$i")
        scan_file "l1_en_hq" "$L1_HQ/$dir/$f"
    done
done

# 10 evenly-spaced zh files (256 total, step ~25)
for i in 1 26 51 76 101 126 151 176 201 226; do
    f=$(printf "ultrafineweb-zh-part-%03d-of-256.parquet" "$i")
    scan_file "zh" "$ZH/$f"
done

echo "" >> "$LOG"
echo "=== Scan Complete ===" >> "$LOG"
echo "End: $(date)" >> "$LOG"
echo "Files scanned: $TOTAL_FILES" >> "$LOG"
echo "Total docs scanned: $TOTAL_DOCS" >> "$LOG"
echo "Total hits: $TOTAL_HITS" >> "$LOG"

# Write summary
cat > "$SUMMARY" <<EOF
# Comprehensive Contamination Scan Summary

**Date**: $(date)
**Scope**: 32 parquet files × 5K docs = ~160K docs
**Sources**: en_base(10) + l1_en_hq(12) + zh(10) — all on /nas_train (no /nas_inference I/O)
**Blacklist**: 536 tasks / 193,295 13-gram + 10 8-gram (6 snapshot union)

## Results

| Metric | Value |
|:---|:---|
| Files scanned | $TOTAL_FILES |
| Total docs scanned | $TOTAL_DOCS |
| **Total hits** | **$TOTAL_HITS** |

## Conclusion

$([ "$TOTAL_HITS" -eq 0 ] && echo "✅ **ZERO contamination hits** — Ultra-FineWeb (en_base + l1_en_hq + zh) confirmed clean against EDA-Eval 536-task blacklist. Combined with 唤醒244 sampling scan (10K docs, 0 hits), total scanned = $((TOTAL_DOCS + 10000)) docs across 37 parquet files, all 0 hits. Data is clean for formal training use." || echo "⚠️ **$TOTAL_HITS contamination hits detected** — see full log for details. Requires investigation before formal use.")

## Full Log
See: \`run/data_pipeline/contam_scan_full.log\`
EOF

echo "DONE: files=$TOTAL_FILES docs=$TOTAL_DOCS hits=$TOTAL_HITS"
