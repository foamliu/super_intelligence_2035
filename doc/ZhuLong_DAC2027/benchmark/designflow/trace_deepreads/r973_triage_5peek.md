# r973 triage — 5 fresh B-pure peek, 3 dup walls, 0 case (质量闸门·dedup gate)

**Date**: 2026-11-21 17:0x (shard B, r973)
**Snapshot**: `summary_1120_reconstructed.tsv` (mc≥10 pool=2072, touched=1796, fresh=276)
**Outcome**: 0 case. 5 candidates peeked via .75 SSH; 3 turned out to be dups (cross-host / cross-shard / near-dup of existing case), 2 thin/skill-use. NOT pool exhaustion — dedup quality gate.

## Root cause of dedup miss (fix for next round)
My freshness filter built `touched` from **only** `trace_ledger_B.tsv`. But the trace_ledger.py `--shard B claim` checks the **4-shard merged ledger** for cross-shard dedup. So sessions cased by shard A/C/D (same sid, waveform/veriloga tasks cross the B/D boundary) appeared "fresh" to my filter but were REFUSED on claim. **Fix**: build `touched` from all 4 ledgers (`trace_ledger_{A,B,C,D}.tsv`) + normalize suffix (strip `.messages.json`/`.messages.archive`). Confirmed working: `grep -l <sid> designflow/trace_ledger_*.tsv`.

## 5 peeked candidates

| sid | user@host | mc | task (U0) | verdict |
|---|---|---|---|---|
| 1794398362877_7prw8 | qiang3xu@hfeg0pgn094 | 159 | "veriloga理想SP2T开关，在20ns实现切换输入，并仿真验证" | **DUP** — `Sp2tVerilogaSwitch-001` already in B.jsonl (cased on hfeg0pkn005, mc=881; same sid cross-host NFS-synced home). Ledger had it; my filter missed (suffix). Real files grabbed: `sp2t_switch.va` (COM/OUT1/OUT2/CTRL, $abstime<t_switch Ron/Roff), `test_sp2t.scs` (Vcom=1V, Rout=1k, tran stop=50ns), spectre ran OK (0 err). |
| 1793582130511_ju0g4 | e0047722@hfeg0plg75 | 166 | "使用tcl代码，帮我画一个正弦波并计算过零点、估算频率与峰值" | **DUP (cross-shard)** — `WvSineWaveAnalyze-001` cased in shard D (ledger_A + ledger_D have it; B.jsonl count=0). claim REFUSED. Real file: `sine_wave_analysis.tcl` (generate_sine_wave/scan_zero_crossings/estimate_freq_from_crossings/analyze_sine_wave, default A=1V f=1MHz T=10us N=500). |
| 1795051874981_6wqk0 | alexcui@hfeg0plg09 | 83 | "wirte a verilogA code for clock signal phi2 160ns period phi1 80ns period phi0 80ns period all non-overlap" + U20 phi2E/phi0E <7:0> rotating bus | **NEAR-DUP of r962** `VlogaNonoverlapClkGen-001` (same user alexcui, identical task: 3-phase non-overlap clk phi2=160ns/phi1=80ns/phi0=80ns + phi2E[7:0]/phi0E[7:0] rotating bus). r962 source session=qcuvw but same content. **Parked** with note. |
| 1794290015438_49vj4 | mengzh@hfeg0plg07 | 214 | "能不能读取我rundata/SIPI/E0044949/test/里面的文件" | **thin** — file-reading/setup, no clear checkable deliverable. 207 msgs. Skip. |
| 1794402601515_cs3x5 / 1794376691015_9ms8b | deniss@hfeahpc501 / yuhang1f@hfeahpc504 | 163/22 | WaveView skill_instructions (FSDB reader V2-2) / "bang wo da kai v(blafarsec25<0>)" | **skill-use / thin** — interactive WaveView GUI, near-dup of r917 WvCurPwlStimGen / r954 WvTrtfDutySummarizer form. Skip. |

## Truly-fresh candidates confirmed NOT in any of 4 ledgers (next-round queue)
Cross-checked `grep -l <sid> designflow/trace_ledger_{A,B,C,D}.tsv`:
- `1795154624230_10atu` jeoteanl@hfeg0plg57 (mc=81, hspice:138) — U0 "找出mt0_parser.py文件copy到..." (file-copy, thin; needs deeper read of follow-up turns)
- `1794905183946_8b4hl` guangmingz@hfeg0pfn048 (mc=30, hspice:127) — U0 "/home/guangmingz/DSIM/codeDSIM/dsim_block 抽激励的步骤，用的什么脚本，如何获得cell的端口类型" (analysis-Q&A, explain DSIM stimulus extraction; needs dsim_block codebase read)
- `1795074929427_gpya9` t0002607@hfeahpc505 (mc=163, hspice:145) — U0 sim ERROR "no reference ckt rm2cb_fs for xi_cds_thru_0 (.netlist:1226) of hcsp_leaf_tiehl_corner" (debug-Q&A, missing-ref subckt diagnosis; **strongest checkable candidate** — reframe as netlist missing-ref diagnostic Python, self-contained A/B crafted netlists, no /proj/lacaa fetch needed)
- `1795144377582_6niih` yfguo@hfeg0plg101 (mc=149, waveview:380) — U0 "你有哪些技能" then waveview-fsdb-readerV2-2 on FSDB current analysis (skill-use, near-dup r917; 898KB/271 msgs huge)

## Next-round plan
1. Lead with **gpya9** (missing-ref diagnostic) — concrete, checkable, self-contained reframe.
2. If gpya9 unsuitable after deep-read, fall back to **8b4hl** (DSIM stimulus extraction analysis-Q&A) — needs dsim_block codebase read for "teeth".
3. Use the **fixed** 4-shard-ledger freshness filter to avoid repeat dup walls.
