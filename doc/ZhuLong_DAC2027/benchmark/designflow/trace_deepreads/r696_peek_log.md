# r696 peek log — candidates peeked & disposition (so r697 doesn't re-peek)

## VIABLE → BUILD queue
- **3hwld** (ellawu mc46, pg_layout): U#0 "整理一下flow详细一点" + attached G4C_AA_PG_dummy_fill_for_Logic.rule (3169-line TVF deck). **CLAIMED r696, deepread done, build deferred r697**. → deepread: trace_deepreads/3hwld_pg_dummy_fill_flow.md

## TAKEN (case already exists in C jsonl — DO NOT rebuild)
- wg5u2 (zjqiao mc738): LibCellList-001 exists (2026-11-02). netlist→lib_cell.list.
- x4b0p (xinqiaoz mc1508): PDKQA-001 exists. PDK QA migration SOP.
- ukkn7 (e0031668 mc1627): ERCFlowAether-001 exists. ERC_AI_CHECK pipeline.

## OFF-C domain (B/D — skip for shard C)
- 9knot (vincelu mc986): PEX/CDL/SPF + hspice/siliconsmart **characterization** (B-domain).
- as67p/okq91/t0aom/dek1i (easont mc654/654/654/592): waveview/netlist **spice sim** (B/D).
- bqgpm (gracew mc132): verilog sim waveform debug compress/dq (D-domain).
- cpvbl (e0039602 mc90): verilog sim (vsim/ddr5_tb) command+result debug (D-domain).
- xm22u/xh3mj/lc81i/b460k/atgt9 (jason17w mc515/511/500/497/497): verilog sim regression VPS skill (D).
- wiglh (jason17w mc141): "[run-regression] run_step2_2 with uvs" verilog sim (D).
- 68gc9 (kli mc431): PrimeSim si.out memory comparison (B-domain spice sim).
- p64wo (tongfanl mc403): Verilog testbench MRR delay / pattern check (D-domain verification).
- my769 (e0017906 mc620): analog circuit analysis Q&A + finesim capability (B/Q&A weak).

## OVERLAP with existing C cases (skip)
- rn6pm (yohannw mc355): SKILL source analysis → docs (IMCutRscalcFlow.il etc.) — overlaps RscalcFlowDocGen-001.
- sk6cg (joelchen mc274) + sr1fw (miccao mc346): "# Calibre/Argus DRC Log 拆解报告" template — overlaps DrcLogPerfAnalysis-001 / DrcLog4ModTruncOpt-001.
- agzjb/nud8i/a15un/jr97m/m14th/pksze (xinqiaoz cluster, drc/pdk/calibre): PDK_QA DrcQa/DummyQa/DrcPatternCheck code review/refactor — overlaps PDKQA-001 cluster.

## WEAK checkability (Q&A / env-config / debug — park)
- gg2j6 (e0027537 mc86): "分析test mode作用 cm1_io_DLLDivSel" circuit Q&A.
- wn9jo (t0002965 mc206): PDK .db file location for synthesis — env-config/Q&A.
- 3h21t (e0047527 mc447): eda bridge connection debug, aether GUI startup — env/debug Q&A.
- bf4yc/tckme/wyrs2 (e0014566 mc730/691/683): "read prompt_flow.md/prompt_powerfill.md and do the job" — same flow-driving cluster as r695's 8du7m (RsCalcFlowCompare-001); redundant.

## Pool status
- A 换池: summary_stats.mc_matrix.src = ssh_eda_search_20261115_081559 (11-15 快照, 自 r681 生效, 未再换)
- mc-matrix(C-keyword, src=summary_1115_081559.tsv): mc>=10 fresh = **221** (非零, 池非枯竭, 按 11-11 令不得下「池耗尽」)
- strong C-dominant fresh candidates (csum>=150, mc>=30): 601 条 — 选料面充足
