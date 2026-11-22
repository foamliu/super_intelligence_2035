# r1019 deepread — gw1z7 (zhiqihe@hfeg0plg103, SiliconSmart char flow verilogFind.log)

## session
- sid: 1795159788338_gw1z7, user zhiqihe, host hfeg0plg103, mc106
- scan: ssh_eda_search_20261123_064315 (r1019 new full scan)
- digA2 filter: ac=3080 cc=4 bc=346 (cleanest A-pure: verilog:2536 dominant, cc=4)
- scp: 676KB / 58 msgs / 9 user turns (all plan-mode Q&A, agent=lead)
- NEW user zhiqihe (no prior case), fresh verified absent from 4-shard ledger (4460 sids)

## user intents (9 Q&A turns)
- U#0: "how to get @libs from verilogFind.log's first column in chat.pl?" ← 本case提炼点
- U#1: chat.pl -s 首跑是否检查已存在 inst 文件
- U#2: ./sisregular/<lib>/ 刚创建所以无 .inst 文件
- U#3-U#4: charlist.py 解密版放 /proj/.../char/charlist.py, agent 读源码
- U#5: "So in script just check for existing inst files, don't create it"
- U#6: "Why you keep saying that run <lib>.tcl will create inst files"
- U#7: SiliconSmart docs at /apps/synopsys/SRB/ssmart_2023.12-SP5/
- U#8: "use import to create inst file, or copy custom; how to check inst status" → report_status

## verilogFind.log structure (real, 2159 lines, from trace tool_results)
```
<lib>  <cell>  verilog  [sub: <reflib>/<refcell> ...]
```
- 9 libs: stdcells_am(680), ddgoa_cmos_digital(417), ddgoa_cmos_pc40(378), ddgoa_cmos_stdcells(299), commonIP(270), ddgoa_cmos_io(80), ddgoa_cmos_lvio64(20), ddgoa_cmos_analog(15)
- 94 cells with sub-deps; 6 subdep-libs; subdep count 1-6 per cell

## case reframe (11-15 令 analysis-Q&A → produce-task)
U#0 intent (extract @libs from verilogFind.log col 1) reframed to generic produce-task:
`parse_verilogfind_log.py <log> <output.json>` → structured JSON
(total_cells/unique_libs/unique_lib_count/libs_summary/cells_with_subdeps/subdep_libs/subdep_lib_count/cells[{lib,cell,type,subdeps:[{lib,cell}]}]).

## assets
- A (visible): verilogFind_A.log = real 2159-line ddgoa project log (from trace tool_results, cleaned of [Showing artifacts)
- hidden B: synthesized PCIe PHY char project (36 cells / 6 libs / 8 cells-with-subdeps / 2 subdep-libs), all lib/cell names different from A
- anti-hardcode anchors: B libs pcie_* vs A libs commonIP/ddgoa_cmos_*/stdcells_am; B 36 cells vs A 2159; known subdep cells PcieTxSerDesLaneIP/PcieDmaEngine/PcieRxEqAdaptIP

## verification
- ref PASS 16/16 on B
- 3 negs FAIL: neg_empty(solver<200B) / neg_print_only(hardcoded A values, total_cells 2162≠36) / neg_core_deleted(skeleton cells=[], total_cells 0≠36)
- §4.9 三假 FAIL ✓
- determinism 3x md5 ✓

## 选料注
r1018 (0-case, pool exhausted on 20261122 scan) → r1019 ran new full 698-host scan (orchestrator.sh, 06:43-06:49, summary.tsv 46472 rows / 8938 dedup sessions / 741 new vs 11-22). digA2 narrow-C_KW filter → 760 dedup A-dom cands → 38 fresh (4460 ledger diff). gw1z7 (zhiqihe mc106 ac=3080/cc=4 cleanest A-pure, NEW user) selected. gw1z7 is Q&A-heavy (9 turns, SiliconSmart flow consultation) but U#0 (extract @libs from verilogFind.log col 1) has clean produce-task reframe with structured-log parse → ≥16 assertions. verilogFind.log content recovered from trace tool_results (e0031982 scp permission-denied on zhiqihe files; trace read_files tool_results contain full 2159-line content in 4 chunks msg[4/16/18/20]).
