# Deepread: r00t7 — SPF/DSPF Sa_BLa↔PreEq Coupling Sort (qinqinl)

- **Trace**: qinqinl @ hfeg0pkn003, session `1792499259030_r00t7`, mc=35, 245 msgs, 5.6MB (>2MB → deepread-only exception)
- **Domain**: eda_other (SPF/DSPF parasitic extraction post-processing)
- **Tool chain**: python-runner (no EDA tool; pure Python DSPF parsing) — L1-static + subprocess
- **Real input (A)**: `msaq_E.spf_CC` — DSPF 1.3, StarRC R-2020.09-SP5-4, design `msaq`, 98°C TYP, 20818 nets. **STATUS: ephemeral sandbox (/ai_sandbox/drgqx/V0/agentdir/qinqinl/) — GONE.** Partial real excerpt recovered from msg m19 (header lines 1-100) + m23 (lines 100-2100, cn09bla/cn09blb column-decoder bitline couplings — NO Sa_BLa/PreEq in this range).
- **Gold outputs (RECOVERABLE on host)**: `/home/qinqinl/.cline/data/sessions/1792499259030_r00t7/uploads/`:
  - `sa_bla_preeq_coupling_sorted.csv` (520424 B, 4495 rows) ← PRIMARY GOLD
  - `sa_blb_preeq_coupling_sorted.csv` (515871 B)
  - `cn_bl_preeq_coupling_sorted.csv` (930540 B)
  - `sa_bla_blb_total_loading_sorted.csv` (844212 B)

## User turns (25 total; A-faithful eligible marked ★)
- U#3 "可以帮我分析spf数据吗" — vague (analyze); not checkable without synthesized spec
- U#55 ★ "所有Sa_BLa与PreEq的coupling 帮我sorting出来" — pure goal (extract+sort Sa_BLa↔PreEq couplings)
- U#69 ★ "所有Sa_BLa需要排序，例如 C17487_4,XI_msax256_cp00.XI_CXSA_1x4_0<48>.Sa_BLa<0> 首先按照 cp00-cp* *；然后每个cp里<48>这个需要排序，最后<0>这个需要排序；Sa_BLa按照顺序分别与PreEq coupling帮我sorting出来" — concrete 3-level sort spec (block cp00→cp*, cxsa <48>, bit <0>); NOT root-cause/fix → A-eligible
- U#95 "pracL cp07 后边；pracR在cp08前边" — block-order refinement (placement spec)
- U#111 "把Sa_BLb和preEq的也按同样的方式sorting一下" — extend to Sa_BLb
- U#143 "可以作曲线图处理下这个数据吗...横轴sa_bla 纵轴coupling值" — plot
- U#167 ★ "Sabla是不是应该有4496个 帮忙check 下" — pure CHECK question (count=4496?); user does NOT give root cause → A-eligible. **Asset = the CSV itself (recoverable).**
- U#179 "帮忙修正这个，把缺失的那一个加进去，相当于preeq CC为0" — FIX (gives fix) → NOT A-eligible (root-cause/fix turn)
- U#190 "Sabla/Sablb 的total loading 按照order sorting 出来"
- U#204 "cn*bl*<*>和preEq的coupling sorting"
- U#235 "整理成excel 分成四个sheet"

## Assistant flow (gold methodology)
1. m21: `spf_analyze.py` — streaming DSPF parser; per-net `*|NET <name> <cap>PF` header + `C<id> n1 n2 val` (coupling) + `Cg<id> n 0 val` (ground cap); unit fix pF→F; output `spf_summary.json` (design, program, n_nets=20818, n_ports, cap stats, top-coupled nets)
2. m62 `spf_bla_preeq.py` → m70/m76 `spf_bla_preeq_sorted.py` → m78-99 `spf_bla_preeq_sorted2.py`: extract Sa_BLa↔PreEq couplings (4495 elements, ALL → PreEq0; PreEqIn_0/R/L have 0). 3-level natural sort: block (cp00→cp15→pracL→pracR), cxsa_idx (<0>~<63> numeric), sa_bla_idx (<0>~<3>). Output CSV cols: `order,element,block,type,cxsa_idx,sa_bla_idx,net_Sa_BLa,net_PreEq,cap_fF,cap_F`
3. m112 `spf_blb_preeq_sorted.py` (Sa_BLb, same structure)
4. m122 `spf_ab_merge.py` → `sa_bla_blb_preeq_merged.csv` (A/B side-by-side, a−b diff)
5. m144 `plot_sa_bla_coupling.py` (matplotlib curve)
6. m168 `spf_check_sabla.py` — count check: 4495 found, 1 missing (cp09 dummy CXSA gap)
7. m191 `spf_ab_total_loading.py` → total loading sorted
8. m205-223 `spf_cnbl_preeq_sorted.py` → cn*bl*↔PreEq couplings
9. m236 `make_excel.py` → 4-sheet xlsx

## Gold CSV structure (sa_bla_preeq_coupling_sorted.csv)
```
order,element,block,type,cxsa_idx,sa_bla_idx,net_Sa_BLa,net_PreEq,cap_fF,cap_F
1,C17055_4,msax256_cp00,std,,0,XI_msax256_cp00.XI_CXSA_1x4_0<0>.Sa_BLa<0>,PreEq0,2.35e-17,2.35e-29
...
4495 rows; all net_PreEq == PreEq0; cap_fF in ~1e-17 range (aF-scale)
```
- block values: msax256_cp00..cp15, msax260_cp07, msax196_pracL, pracR (16 cp + pracL + pracR, with msax256/msax260/msax196 variants)
- 4495 = expected 4496 minus 1 missing (cp09)

## Synthesis plan (NEXT ROUND — must deliver, no second deepread-only)
**Chosen task: U#167 "Sabla是不是应该有4496个 帮忙check 下"** (asset = recoverable CSV; cleanest A-faithful + checkable in one round)

### task_id: `EDA-Eval-DesignFlow-SpfsablaCountCheck-001` (domain eda_other, L1-static+subprocess)
- **Task statement (verbatim U#167)**: `Sabla是不是应该有4496个 帮忙check 下` (task_brief.md ≤3 lines: deliverable=outputs/submit.zip containing check_sabla_count.py + report.json; interface only)
- **Asset A (real)**: `sa_bla_preeq_coupling_sorted.csv` — scp from `/home/qinqinl/.cline/data/sessions/1792499259030_r00t7/uploads/sa_bla_preeq_coupling_sorted.csv` on hfeg0pkn003 (520KB, 4495 rows). Real, faithful.
- **Hidden B**: programmatic edit of A — (1) inject a DIFFERENT missing entry (remove row at e.g. cp05/CXSA<12>/Sa_BLa<2> → 4494 rows, expected 4496, missing 2); (2) relabel blocks (msax256_cp00→msax512_cp00 etc.) so candidate can't hardcode cp09. B in assets/.../hidden/, NOT in SUT sandbox.
- **B' cross-input guard variant**: a "complete" CSV (4496 rows, no gap) → candidate must report count_ok=true, missing=[].
- **Gold** (`check_sabla_count.py`, config-driven): parse CSV → count rows → reconstruct the cp×cxsa×bit grid from `block,cxsa_idx,sa_bla_idx` → enumerate expected combos → find absent ones → output `report.json` {csv_rows, expected_total, found_total, missing_count, missing:[{block,cxsa_idx,sa_bla_idx}], count_ok:bool, block_set, cxsa_range, bit_range}. NO hardcoded cp09/4496 — derive expected from observed block×cxsa×bit space (cross-product minus gaps).
- **check.py ≥8 conditions (a-n)**:
  - a zip contains check_sabla_count.py + report.json
  - b py_compile check_sabla_count.py
  - c [B] subprocess exit 0 + report.json valid JSON
  - d [B] report.csv_rows == B actual row count (4494)
  - e [B] report.found_total == 4494
  - f [B] report.expected_total == 4496 (derived from block×cxsa×bit cross-product, NOT hardcoded)
  - g [B] report.missing_count == 2 (B's injected gaps)
  - h [B] report.missing entries == B's removed (block,cxsa_idx,sa_bla_idx) tuples (anti-hardcode: must match B's specific gaps, not A's cp09)
  - i [B] report.count_ok == false
  - j [B] report.block_set contains the relabeled B blocks (msax512_*) and NOT A's msax256_* (cross-input guard)
  - k [B] report.cxsa_range covers <0>~<63> numeric span
  - l [B] report.bit_range covers <0>~<3>
  - m anti-hardcode: source contains no literal "cp09"/"4496"/"msax256_cp09" (generic grid derivation)
  - n [B'] cross-input guard: on complete-B' CSV, report.count_ok==true and missing==[] (defeats always-report-missing stub)
- **Negatives (≥3 §4.9 fakes + naive)**:
  - naive_noop: prints `{"count_ok":true}` always → fails (d,h,i on B; n on B')
  - print_expected: hardcodes A's cp09 missing → fails (h on B — wrong gaps; j — wrong blocks)
  - core_deleted: strip grid-enumeration logic → fails (f,g,h)
  - naive_count_only: only counts rows, no missing detection → fails (g,h,n)
- **Self-verify**: REF PASS 14/14 a-n on B + B'; 3 fakes FAIL distinct; §4.9 (a空壳/b只print期望/c删核心) all FAIL; negative_selftest PASS distinct≥3.
- **test_rationale**: `14 条断言：①zip含check_sabla_count.py+report.json ②py_compile通过 ③[B]子进程exit0+合法JSON ④[B]csv_rows=B实际行数 ⑤[B]found_total=4494 ⑥[B]expected_total=4496(网格导出非硬编码) ⑦[B]missing_count=2 ⑧[B]missing条目=B注入缺口(block,cxsa_idx,sa_bla_idx) ⑨[B]count_ok=false ⑩[B]block_set含B重标签msax512_*不含A的msax256_* ⑪[B]cxsa_range覆盖<0>~<63> ⑫[B]bit_range覆盖<0>~<3> ⑬反硬编码源码无cp09/4496/msax256_cp09字面量 ⑭[B']交叉输入守卫完整CSV报告count_ok=true且missing为空`

### Alternative task (if U#167 too narrow): U#69 Sa_BLa↔PreEq sort
- Asset A would need real Sa_BLa SPF excerpt — NOT recoverable (SPF gone). Would require reconstructing a synthetic-but-faithful DSPF from m23's cn09bl structure relabeled to Sa_BLa/PreEq → B-档, not A-faithful. **Prefer U#167 (real CSV asset available).**

## A-faithful eligibility verdict
- U#55 / U#69 / U#167 all A-eligible (goals/specs/checks, no root-cause/fix).
- U#167 chosen: real asset recoverable, checkable in one round, clean hidden-B construction.
- U#179 NOT eligible (gives fix).

## DEBT
- DEBT:1 (r245 deepread-only; r246 MUST synthesize SpfsablaCountCheck-001 — no second deepread-only)
