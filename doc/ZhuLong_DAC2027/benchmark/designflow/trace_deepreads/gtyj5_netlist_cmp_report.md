# Deepread: 1793070934364_gtyj5 — netlist comparison report (easont, eda_other)

**Trace**: `1793070934364_gtyj5.messages.json` (easont@hfeg0pkn004, mc592, 393 msgs, 2.06MB)
**Claimed**: r253 (2026-11-09). DEBT:1 → r254 must synthesize first.
**Domain**: eda_other (SPICE netlist structural comparison + markdown report generation)

## Why deepread-only this round
Trace file = 2.06MB > 2MB threshold (§3 单轮闭环 exception). netlist_AI (802 lines) no longer on
disk — must be stitched from 4 overlapping in-session read_files tool_results. netlist_pro_clean
(431 lines, 24951 B) still on .75 at `/home/easont/netlist_pro_clean`. Full synthesis (stitch +
comparison script + check.py + hidden B + negatives + self-verify) needs a full round.

## Session arc (10 real user turns)
- U#0 `can you read <cosim/tt0.94v45c.vdd2h/finesim.fsdb>` — goal
- U#8 `有fsdb相关的MCP server吗` — question
- U#17 `使用上面的skill读取<fsdb>；根据波形说明signal的功能` — goal ★A-eligible
- U#63 `读取netlist_AI,结合上面的fsdb分析，说明模块功能` — goal ★A-eligible
- U#97 `分析当前netlist是最简逻辑吗，是否有优化方案，直接输出优化后的网表到...命名为netlist_pro` — goal (gives output direction)
- U#204 `仿真波形有问题，自己分析后迭代netlist` — points to root cause (NOT A-eligible)
- U#234 `结构参考这个来，你生成的都是错的` — root cause (NOT A-eligible)
- U#278 `你理解下这个网表，然后分析是否有可优化的点，然后直接在netlist上修改` — fix direction
- **U#383 `对比修改后的网表和原先的网表，生成markdown形式的报告`** — pure goal ★★ SELECTED
- U#392 `分析文件夹...说明整体仿真流程` — goal (next request ⇒ U#383 gold accepted)

## Selected A-档 turn: U#383 (pure goal, no root-cause/fix given)
**Verbatim task**: `对比修改后的网表和原先的网表，生成markdown形式的报告`
**Gold**: assistant A#391 — markdown comparison report `netlist_AI` (original) vs
`netlist_pro_clean` (optimized). User moved on to U#392 ⇒ accepted.

## Gold report structure (A#391, 2696 chars)
```
# 网表对比报告：netlist_AI → netlist_pro_clean
## 1. 文件大小
| 指标 | netlist_AI（原始） | netlist_pro_clean（优化） | 变化 |
| 字节 | 39,840 | 24,951 | -14,889 (-37.4%) |
| 行数 | 802 | 431 | -371 (-46.3%) |
## 2. 单元格定义  (.SUBCKT definitions diff — added/removed/preserved)
## 3+. 实例统计 (X-instance counts by cell type) ...
```
Assistant produced this by writing a python script (run_approved_command, msg#384→388→390)
that read both netlists and computed the metrics. **That script = the reference solution.**

## Assets (real, recoverable)
- **netlist_AI** (original, 802 lines, 39840 B): STITCH from in-session reads:
  - msg#282: `netlist_AI:1-235` (11157 B content)
  - msg#280: `netlist_AI:233-400` (8429 B)
  - msg#74:  `netlist_AI:400-762` (24309 B)
  - msg#284: `netlist_AI:762-810` (2668 B)
  - Overlaps at 233-235, 400 — dedup by line number prefix ` N | `.
  - Cross-check: total 802 lines, 39840 bytes per gold report.
- **netlist_pro_clean** (optimized, 431 lines, 24951 B): STILL ON DISK
  `/home/easont/netlist_pro_clean` — `cat` directly on .75, no stitching needed.
- Both are SPICE netlists for `TempHalfWL` (temperature half-wordline sensor circuit,
  ddgoa_cmos_digital). Top-level `.SUBCKT TempHalfWL Temp<7>...Temp<0> ...`. Library cells:
  invLx1/invLx2/invLx4, nand2Lx1/nor2Lx1, xnor2Lx1, nand4, oai21, bufLx4, etc. Instances
  named `XI<cmp>_...` (comparators for temp thresholds sel32/sel35/sel40/sel43/sel50/sel61/
  sel68/sel76). netlist_pro_clean removed 18 unused cells + simplified output stage
  (per its header comment: "Removed 18 unused cell ...").

## Synthesis plan (r254 — DO THIS FIRST)
1. **Recover netlist_AI**: on .75, run python to extract the 4 read_results from
   gtyj5.messages.json, parse `result` string (format `' N | <line>'`), stitch by line number,
   write to workdir `netlist_AI`. Verify == 802 lines / 39840 bytes.
2. **Copy netlist_pro_clean** from `/home/easont/netlist_pro_clean` (431 lines / 24951 B).
3. **Case**: `EDA-Eval-DesignFlow-NetlistCmpReport-001` (eda_other, L1-static+subprocess).
   - **Deliverable**: `compare_netlist.py` — config-driven (`config.json{netlist_a, netlist_b,
     report_out}`), parses two SPICE netlists → emits a markdown comparison report with
     structured sections (size metrics, .SUBCKT definitions added/removed/preserved,
     X-instance counts by cell type, top-level port diff).
   - **A (visible)**: real `netlist_AI` + `netlist_pro_clean` + `config_a.json`.
   - **Hidden B**: synthesized netlist pair structurally different from A — e.g.
     `netlist_orig_B.sp` (5 .SUBCKT, ~40 X-inst, 8 ports) vs `netlist_opt_B.sp` (3 .SUBCKT
     after removing 2, ~22 X-inst, same ports) — different byte/line deltas, different
     removed cells, so check values differ from A. Cross-guard: B's removed-cell set and
     size delta must differ from A's (-37.4% bytes / -46.3% lines / 18 removed cells).
   - **check.py** (≥14 conds a-n): a zip-has-compare_netlist.py; b py_compile;
     c [B] run 3× deterministic exit0 + writes report_b.md; d [B] report has `# ` title +
     `## ` size section; e [B] netlist_a bytes count correct; f [B] netlist_b bytes correct;
     g [B] byte-delta % correct (within 0.1%); h [B] line counts correct; i [B] .SUBCKT
     list per netlist correct; j [B] removed .SUBCKT set correct; k [B] preserved .SUBCKT
     set correct; l [B] X-instance count by cell type for netlist_a; m [B] X-instance count
     by cell type for netlist_b; n anti-hardcode: source has no A-specific literals
     (TempHalfWL/sel76/invLx1/netlist_AI/netlist_pro_clean/easont/ddgoa) — gold uses generic
     .SUBCKT/X regex parsing.
   - **negatives** (≥2 + §4.9 three fakes): naive_noop (empty → c), print_expected (hardcode
     A's report → n), core_deleted (strip .SUBCKT parsing → i/j), naive_count_lines_only
     (no cell-type breakdown → l/m).
   - **test_rationale** (k=14, `14 条断言：①…⑭` mapped 1:1 to a-n).
4. Self-verify: REF PASS 14/14, 3 §4.9 fakes FAIL distinct, negatives NEG_RC=0, k-gate PASS.
5. Append `EDA-Eval-DesignFlow_A.jsonl`, `mark gtyj5→case`, daily report line, DEBT→0.

## Distinctness guard vs existing cases
- `CosimFlowAnalyze-001` (as67p, easont) = cosim FLOW structure (VCS+FineSimPro orchestration).
- This case = NETLIST structural DIFF (cell/instance deltas between two netlist versions).
  Different deliverable (comparison report vs flow description), different check dimensions.
  Both are easont/ddgoa but distinct task angle. Acceptable.
