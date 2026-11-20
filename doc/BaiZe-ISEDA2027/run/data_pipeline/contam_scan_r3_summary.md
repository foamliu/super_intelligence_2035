# R3 Contamination Scan Summary
**Date**: Sat Oct 10 11:22:43 AM CST 2026
**Scope**: 30 parquet files x 2K docs = 60K docs
**Sources**: L3(10) + Code(10) + Math(10)
**Blacklist**: 536 tasks / 193,295 13-gram + 10 8-gram
## Results
| Metric | Value |
|:---|:---|
| Files scanned | 30 |
| Total docs scanned | 60,000 |
| **Total hits** | **0** |
## Per-source breakdown
| Source | Files | Docs | Hits |
|:---|---:|---:|---:|
| L3 (Ultra-FineWeb-L3) | 10 | 20,000 | 0 |
| Code (UltraData-Code) | 10 | 20,000 | 0 |
| Math (UltraData-Math) | 10 | 20,000 | 0 |
| **Total** | **30** | **60,000** | **0** |
## Conclusion
ZERO contamination. R3 sources clean. All training data ready.
Combined with previous base scan (160K docs, 0 hits):
Total scanned: 208000 docs across all 6 sources, 0 hits.
## Full Log
See: run/data_pipeline/contam_scan_r3.log
