# Deepread · nn0xl · maggiew @ hfeg0pkn002 · IddCellFilter

- **sid**: 1794302134942_nn0xl · user maggiew @ hfeg0pkn002 (10.129.x) · mc14 · kw cmos:277;analog:37;synthesis:2
- **domain**: analog_context (sim idd leakage post-processing)
- **nmsgs**: 48 · user turns: 6
- **scan src**: ssh_eda_search_20261113_131349 · D-shard fresh (not in ledger)

## User intent (verbatim, trace-faithful)

- U0 (msg0): `/rundata/.../ext_vdd1!.csv 把这个csv 中第一列大于5的cellname 统计出来 把数值也带上`
- U6 (msg6): `不用全部读完，参考前面几行然后处理就行` (don't read whole file, sample first rows)
- U18 (msg18): `把这个表格路径给我` (save to file)
- U26 (msg26): `这个没有完全显示 搜索的不对` (output truncated; wants raw detail not aggregation)
- U40 (msg40): `我要找的是5以上的，scmosvdlyzin这个怎么也被搜索出来了 他小于5` (gotcha: user thinks scmosvdlyzin <5 but it has 2 rows ~44.9 >5)

= **clean produce-task**: CLI script to filter CSV rows where first-column idd > 5, output idd + cellName detail. Spec-by-iteration (U26 refines aggregation→detail, U40 reveals numeric-vs-per-cell subtlety).

## Assistant tool chain

list_allowed_files (path is file not dir) → read_files (ext_vdd1!.csv) → editor filter_csv.py (agg: count/min/max/avg by cell) → run python-runner → 536 rows idd>5, 147 unique cells → editor add file output → U26 wants detail → editor filter_detail.py (raw rows idd,cellName) → run → 536 rows → U40 scmosvdlyzin complaint → editor check_cell.py (dump all scmosvdlyz* rows) → run → reveals 2 rows ~44.9 (>5, correctly included) + 60+ rows ~0.05 (<5, excluded) → assistant explains per-row filter is correct.

## Real artifacts (fetched from .75 hfeg0pkn002)

### filter_detail.py (the gold-equivalent, real)
```python
import csv
filepath = "/rundata/.../ext_vdd1!.csv"
outpath = "/home/maggiew/idd_gt5_detail.csv"
count = 0
with open(filepath,'r') as fin, open(outpath,'w',newline='') as fout:
    reader = csv.reader(fin); writer = csv.writer(fout)
    header = next(reader); writer.writerow(["idd","cellName"])
    for row in reader:
        if not row: continue
        idd_val = float(row[0]); cell = row[4]
        if idd_val > 5:
            count += 1; writer.writerow([idd_val, cell])
print(f"Total rows with idd > 5: {count}")
```

### Real input format
- CSV comma-separated, **5 columns**: `row[0]`=idd (float), `row[4]`=cellName (string). Middle cols (1-3) are sim metadata (pattern/corner/temp). Header row present, skipped.
- Real input inaccessible (Permission denied on /rundata), but output `idd_gt5_detail.csv` (2-col idd,cellName, 536 rows) fetched — gives real cellnames + value ranges.

### Real cellnames (from idd_gt5_detail.csv head 40)
array2gd_sc0, array0d5g_topl, array8g_sc1, array2ga_sc1, array0d5g_topr, xdecgap_48r, sactrol, sactrol_sub, eqio_sactrol_drv_inv, ptn, iso_sactrol_inv, sapena_sactrol_drv, ptk, sapenb_sactrol_drv, sapenc_sactrol_drv, scmosvdleq2vcc, ntk, ntn_lv, scmosvdleq2vccfs, scmosviso2vcc, scmosvdlyzin.

### Real value ranges
- Large leakers: array8g_sc1=2124.6, scmosvdleq2vcc=109.9, scmosviso2vcc=45.1
- scmosvdlyzin: 2 rows ~44.9 (>5) + 60+ rows ~0.05 (<5) — the U40 gotcha
- Boundary: iso_sactrol_inv=5.14, ptn=5.14 (just above 5)
- Small: ptn=9.98, eqio_sactrol_drv_inv=13.6

## Synthesis plan (B档 synthesized)

- **case_id**: EDA-Eval-DesignFlow-IddCellFilter-001
- **domain**: analog_context
- **SUT produces**: `idd_filter.py` (pure stdlib CLI `python3 idd_filter.py <in.csv> <out.csv> [--threshold 5]`)
  - parse CSV (5-col header `idd,pattern,corner,temp,cellName`), filter rows where float(row[0]) > threshold, write output CSV `idd,cellName` + matching rows
- **visible A**: sample_A.csv (5-col, ~50 rows, real-like cellnames, mix >5/<5). Gotchas:
  1. scmosvdlyzin: 2 rows ~44.9 (>5 ✓) + 4 rows ~0.05 (<5 ✗) — per-row not per-cell
  2. cellname `buf5x` with idd=3.2 (<5) — anti string-match on cellname digit "5"
  3. boundary: idd=5.0 (excluded strict >), idd=5.0001 (included), idd=4.9999 (excluded)
  4. idd=10 cellname `inv_a` — string compare "10"<"5" would EXCLUDE wrongly; numeric INCLUDES (anti string-compare on idd)
  5. idd=100 cellname `inv_b` — same trap, "100"<"5" lexically
- **hidden B**: sample_B.csv (5-col, different cellnames dft_clk/pll_vco/ldo_out/..., same 5 gotchas, different scale)
- **hidden C**: sample_C.csv (5-col, disjoint cellnames, anti-hardcode A)
- **check.py**: ~15 cond (zip valid / py_compile / generic no-hardcode / B exit0 / B valid CSV header / B rowcount=oracle / B multiset=oracle / B boundary 5.0 excluded / B idd=10,100 included anti-string-compare / B scmosvdlyzin per-row / B buf5x-digit excluded / C cross-input rowcount=oracle / C multiset=oracle / empty robust / idd numeric). 4 negatives (empty/print_only/hardcode_a/core_removed-string-compare).
- **test_rationale**: 15 条断言 (k=15, k_check=15 ≥8 ✓)

## Gotchas for check (key subtleties)

1. **numeric vs string compare** (anti-naive): idd=10/100 must be INCLUDED (string "10"<"5" lexically → naive excludes wrongly). This is the core trap — a `row[0] > "5"` string comparison fails on multi-digit values.
2. **per-row not per-cell** (scmosvdlyzin): a cell with mostly <5 values still has its >5 rows included. A per-cell aggregation/summary that excludes cells whose majority <5 would fail.
3. **boundary strict >**: idd=5.0 excluded (not >=).
4. **cellname digit trap**: cellname containing "5" (buf5x) with idd<5 must be excluded — catches string-match on the whole row.
