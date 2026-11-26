# u54d9 — signal→pattern/.inc/reg cross-reference (eason1z, digital, A-faithful produce)

- **trace**: 1794021023245_u54d9.messages.json (eason1z@hfeg0plg100, mc108, verilog:5163, 205 msgs)
- **claim**: r309 (DEBT:1 build → r310)
- **host**: 10.129.8.232 (hfeg0plg100), NFS-shared home → readable from any host
- **found via**: r309 trace_ledger.py **$6-column bug fix** (was missed by old $7 filter; u54d9 has verilog:5163 in $6 keywords but $7 tools empty → bug hid it)

## USER#0 (verbatim, A-faithful produce ✓ — states goal, no root cause)
> 给你一个文件/rundata/drgqx/V0/simdir/verilog/zhaoxin/verilog.ddr5.drgqx.1107/cmname_zx，里面有很多信号名，你帮我在路径/.../patterns/cmds_testmode/下的文件和文件夹中的文件里去找包含这些信号名的文件，然后去路径/.../Regressions/下以.inc结尾的文件中去找到有包含这些文件名的文件，并记录信号名和文件名的对应关系给我,同时在路径/.../Regressions下的文件里去找包含这些信号的文件，并记录信号名和文件名的对应关系给我.

## Task = 3-level signal cross-reference
1. **pattern match**: search files (recursive) under `patterns/cmds_testmode/` for each signal name → `signal → [pattern_files]`
2. **.inc reference**: search `.inc` files under `Regressions/` for those pattern *filenames* → `pattern_file → [.inc_files]` (so signal→.inc via pattern)
3. **reg direct**: search files under `Regressions/` for each signal name directly → `signal → [reg_files]`
- Output: structured report of signal→pattern_files / .inc_refs / reg_files mapping.

## Real data (ATEXT#40, accepted result, 12 signals after ` 1`-suffix cleanup)
Signal list (cmname_zx, 12): ts_FsStbGenDly_Int, ts_FsPgm_Int, fc_MrrFrpX16Adj, ag_AdjVfsrdxgt_Int, ag_AdjVfsrdb_Int, ag_AdjVfsrdfsgt_Int, fc_MR2OP4WindowEn_Int, fc_MRWPulseCtrl, fc_AlwaysLatMraOpEn, fc_MR4Op7Sel, fc_DisCstmRst_Int, fc_MR14OP6KeepDis
- 2 signals (ts_FsStbGenDly_Int, ts_FsPgm_Int) → no match anywhere
- 10 signals → pattern matches in cmds_fuse / cmds_priority3 / option_fuse_table subdirs (counts 1–33 files)
- .inc refs: tm_fuse_table_MultiBit_eye.inc→TM_BlownMultiBits.v (3 signals), tm_datapathtiming_eye.inc→TM_datapath_inc.v (fc_MRWPulseCtrl), temp_variation.inc→temp_variation.v (fc_MR4Op7Sel), tm_temp_sensor.inc→tm_temp_sensor.v (fc_MR4Op7Sel)
- reg direct: tm_datapathtiming_eye.run (fc_MRWPulseCtrl), 12 .run files (fc_MR4Op7Sel)
- Deliverable file: `/home/eason1z/signal_search_report.txt` (markdown table report)

## Case design (r310 build plan) — spec-driven-generator + static-verification (L1)
Matches RunTaskMapExtractor-001 (r307) / SpfCouplingParser-001 pattern but with the signal→pattern→.inc 3-level dimension.
- **deliverable**: `gen_signal_xref.py` + `spec_a.json`
  - generator (stdlib) emits `signal_xref.py` parameterized by spec: {signal_list_file, patterns_dir, regressions_dir, inc_suffix, reg_suffixes, output_file, output_format}
  - emitted `signal_xref.py` walks patterns_dir (recursive), greps each signal, builds signal→pattern_files; walks Regressions/*.inc, greps pattern filenames, builds pattern→inc; walks Regressions/*, greps signals, builds signal→reg; writes structured report (markdown table + TSV)
- **check.py** (hidden spec_b): synthetic isomorphic file tree — different signal names (e.g. sigA1..sigA12), different pattern/.inc/.run files, different match counts; verify:
  - a) zip contains gen + spec_a
  - b) gen py_compile OK
  - c) gen on spec_b emits signal_xref.py
  - d) signal_xref py_compile OK
  - e) run on hidden sample_b (signal_list_b.txt + patterns_b/ tree + Regressions_b/ tree) → produces report_b
  - f) report_b signal count == B signal count (independent recompute)
  - g) signal→pattern mapping correct (recompute by grep, compare)
  - h) pattern→.inc mapping correct
  - i) signal→reg direct mapping correct
  - j) unmatched signals (no-match) reported correctly
  - k) anti-hardcode-A: B-specific signals present, A-specific absent
  - l) anti-hardcode-A: emitted source doesn't contain A-specific signal names
  - m) 3-seed determinism (md5)
  - n) anti-trivial: re.compile/finditer + ≥3 functions + reads spec json + walks dirs
- **A assets** (faithful): real cmname_zx signal list (12 signals, masked paths ok per red-line #2), real subdir names (cmds_fuse/option_fuse_table/cmds_priority3), real .inc/.run filenames
- **hidden B**: synthetic signal_list_b (12 different sig names), synthetic patterns_b/ (mkdir tree with .v files containing chosen sigs), Regressions_b/ (.inc + .run files) — isomorphic, different counts/values
- **negatives**: noop, hardcode_a, fake_print, fake_output, stub, fake_core_deleted (all FAIL)
- **target k**: 14 (a–n), k_rationale==k_check≥8 ✓
- **domain**: digital; **track**: faithful; **level**: L1-static

## Why not built in r309
r309 budget consumed by the trace_ledger.py $6/$7 column-mapping **bug fix** (294→2381 dedup candidates, 8×; 581 digital-dominant) + pool reassessment — a major infrastructure deliverable ending 40 rounds (r268–r308) of "pool exhausted" misdiagnosis. u54d9 deepread complete; r310 builds (no further exploration needed).
