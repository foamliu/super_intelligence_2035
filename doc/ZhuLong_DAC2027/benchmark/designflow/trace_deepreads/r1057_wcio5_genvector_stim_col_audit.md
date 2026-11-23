# r1057 deepread: wcio5 — ericw DDR5 genvector stimulus column-consistency audit

## trace_source
- session: 1794828827130_wcio5.messages.json
- user: ericw
- host: hfhds206 (10.129.32.80) / hfeg0pkn002
- match_count: 125
- keywords: verilog:476;analog:168;netlist:94;aether:59;systemverilog:12;cmos:11;floorplan:10;mixed-signal:9
- tools: 75 netlist, 7 pyAether, 1 hspice, 1 calibre
- 67 msgs, 664KB

## domain judgment
verilog:476 dominant (>> analog:168). Per 16:4x §三.3: virtuoso/skill/layout/gds/calibre/drc/lvs 主导 ⇒ C; hspice/netlist/spice/schematic 主导 ⇒ B/D; **digital/verification 主导 ⇒ A**. verilog:476 is A-domain (verification/stimulus-gen). r1021 bulk-park "mixed C/BD" was a keyword-inference error (analog:168 is secondary, the task itself is SV stimulus-list signal audit). **Corrected: A-domain (digital/verification).**

## user intent (2-turn)
### Q1 (msg 0): signal provenance + missing-signal diagnosis
- ericw ran `vecgen_drex` → extracted `stimulus.list` from log dir `Perbank001_ActWrRdPre_WPre_2_tCH_50_BL16_4b8g_B0_100_TT`
- stimulus.list defines 9 signals: CK, ACS_N, DCS_N, MCS_N, ACT_W, WR, RD, ConfigIN, GResetN
- Q: where are these defined? why is CACS_N missing?
- agent (msg 40): found 9 signals hardcoded in `ddr5_genvector.sv` task `analogvec_gen` signal_name[0..8]; CACS_N exists in ddr5_interface.sv (wire) + top.sv (port) but was never added to genvector. To add: modify 6 places (signal_name array, mask, vih/vil, slope, radix/io, $fmonitor).

### Q2 (msg 41): modification-bug diagnosis
- ericw added CACS_N to ddr5_genvector.sv but generated stimulus "文件不完整" (incomplete)
- agent (msg 44): diagnosed — radix/io lines in fd_vec (vec.text) and fd_stimu (stimulus.list) blocks still had 9 columns (not updated to 10), only fd_sim (stimulus.vec) was correct. Column mismatch → stimulus parser rejects file.
- fix: update radix/io in fd_vec + fd_stimu from 9→10 columns.

## case reframe (check-able produce task)
- **task_id**: EDA-Eval-DesignFlow-GenvectorStimColConsistencyAuditProduce-001
- **archetype**: L1 offline Python reframe (like r1050 ProbeTclSignalHierarchyExtractProduce-001)
- **intent preserved**: diagnose which of the 3 output blocks (fd_sim/fd_vec/fd_stimu) in a modified genvector.sv have section/column inconsistencies after a new signal was added
- **deliverable**: `genvector_audit.py` — parses a genvector.sv file, extracts signal_name array, for each of 3 blocks checks 6 sections (signal-list, mask, vih, vil, slope, radix-cols, io-cols, fmonitor) against signal_count, outputs structured JSON inconsistency report
- **input A**: synthesized genvector_modified.sv (10 signals incl CACS_N; fd_sim consistent; fd_vec radix/io=9 cols; fd_stimu radix/io=9 + fmonitor=9) — mirrors real trace bug
- **hidden B**: different signals (8: CLK,RST_N,EN,ADDR,DATA,WR_EN,RD_EN,IRQ), different mismatch pattern (fd_vec io=7+mask=7; fd_stimu radix=7+io=7+vil=7)
- **check()**: subprocess run on B, parse JSON, ≥10 assertions (signal_count, per-block radix/io/mask/vih/vil/slope/fmonitor cols, consistent flags, total_inconsistencies)
- **3 fakes**: empty / print-only-A (hardcoded A JSON) / core-deleted (parse signal names but skip column check)

## 三闸门 (sister-turn distinctness)
- (a') structure orthogonal: this = audit-script (detect column mismatches across 3 SV output blocks); r1056 MsieMmchExplainQA = mechanism-explain doc+verify (msie build/run flow). Different object (genvector.sv stimulus format vs msie package/snapshot), different verb (audit/detect vs explain/verify).
- (b') ≥4 non-reusable assertions: 10+ assertions on B-specific radix/io/mask/vih/vil/slope/fmonitor counts — not reusable from any existing case.
- (c') A/B token-disjoint: A uses 10 signals (DDR5 CK/ACS_N/.../CACS_N), B uses 8 signals (CLK/RST_N/.../IRQ) — different names, different counts, different mismatch patterns.

## verdict
VIABLE. A-domain (verilog dominant). Real trace (ericw wcio5 mc125). Check-able produce reframe. Proceed to合成.
