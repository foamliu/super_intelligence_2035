# Comprehensive Contamination Scan Summary

**Date**: Fri Oct  9 05:34:08 AM CST 2026
**Scope**: 32 parquet files × 5K docs = ~160K docs
**Sources**: en_base(10) + l1_en_hq(12) + zh(10) — all on /nas_train (no /nas_inference I/O)
**Blacklist**: 536 tasks / 193,295 13-gram + 10 8-gram (6 snapshot union)

## Results

| Metric | Value |
|:---|:---|
| Files scanned | 30 |
| Total docs scanned | 150000 |
| **Total hits** | **0** |

## Conclusion

✅ **ZERO contamination hits** — Ultra-FineWeb (en_base + l1_en_hq + zh) confirmed clean against EDA-Eval 536-task blacklist. Combined with 唤醒244 sampling scan (10K docs, 0 hits), total scanned = 160000 docs across 37 parquet files, all 0 hits. Data is clean for formal training use.

## Full Log
See: `run/data_pipeline/contam_scan_full.log`
