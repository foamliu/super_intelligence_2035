# Deepread: 1794790395375_uyvi5 — STA run evaluation (analysis-Q&A)

## Trace source
- **session**: `1794790395375_uyvi5` (messages.json, 1.79MB, 271 msgs)
- **user**: `e0046913` @ `hfeg0pkn004` (10.129.2.13)
- **mc**: 164 (netlist:566; pt_shell:190; verilog:131; primetime:63; rtl:36; synopsys:20; synthesis:11)
- **model**: deepseek-v4-flash (interactive, completed)
- **session span**: 2026-11-16 00:53 → 11-18 01:28 (multi-turn, 13 user turns)

## User intent (turn 1, the case target)
> `<user_input mode="act">/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/cla_top_DS/sta/run 我正在调试sta flow，以cla_top作为database进行试跑。根据log和report评估本次STA运行结果</user_input>`

**Single-turn analysis-Q&A**: user gives STA run dir path, asks agent to evaluate the run result based on log and report. Agent explored dir, read logs/reports/SDC/netlist/proc tcl, produced a Chinese markdown evaluation report.

## Agent's tool chain (turn 1, msgs 0–32)
1. `list_allowed_files` run dir → saw Makefile, sta.tcl, sta_setup.tcl, proc/*.tcl (0_check_config…10_qa), lib_path/, etc.
2. `list_allowed_files` sta parent → saw `all_out/v1.0_Latest/`, `data/`
3. `read_files` Makefile, sta.tcl, sta_setup.tcl, CFG_VARS, CXDP_STA_CFG
4. `list_allowed_files` all_out/v1.0_Latest (depth 3) → saw QA/, report/, log/
5. `read_files` QA/sta_qa_result, cla_top_qa_summary_ssgnp_v0p675_0c.txt, link_report
6. `read_files` report_timing_setup/hold, wns_tns, wns_tns_hold, check_constraints, analysis_coverage, global_timing (all ssgnp_v0p675_0c)
7. `read_files` log/sta_pre_WL_ssgnp_v0p675_0c.log (lines 1–220, 220–520, 290–460, 520–760)
8. `read_files` data/cla_top.netlist.f, sta_override.tcl, log/run_vars_ssgnp_v0p675_0c.tcl
9. `read_files` data/cla_top.sdc
10. `read_files` run/proc/2_read_netlist…10_qa.tcl (8 proc files)
11. `read_files` report_drv_all, report_clock, report_constraints, check_timing, etm_netlist_interface_timing, lib_path/analysis_lib.f
12. `read_files` cla_top.mapped.v (head, lines 1–45)
13. `read_files` report_drv_all (lines 103–109, the max_fanout violation block)

## Ground-truth findings (agent's final report, msg 32)
1. **Flow**: CXDP STA proc-based, PrimeTime U-2022.12-SP5, `make common`/`make sta`, Pre netlist + WL, corner `ssgnp_v0p675_0c` (WCL/RCWORST)
2. **Inputs**: netlist `1103_clatop_syn/flow_cla_top/results/cla_top.mapped.v` (DC Ultra synth), SDC `data/cla_top.sdc`, 3 std libs `DBCP51H180L6W25T5_*_ssgnp...db`
3. **Run**: 18 seconds, peak RSS ~3.1 GB, all steps "OK", `_flow_status=0`
4. **QA gate**: `QA/sta_qa_result` + `qa_summary` report PASS (blackbox=0, setup/hold/DRV all 0, WNS=TNS=0) — **BUT not trustworthy**
5. **Design**: pure combinational 16-bit CLA, ports `a[15:0] b[15:0] cin -> sum[15:0] cout`, no registers, no clock pin (confirmed in cla_top.mapped.v head)
6. **link OK**: "Design 'cla_top' was successfully linked", LNK-045/046 info-only, blackbox=0
7. **Setup OK**: `report_timing -delay_type max` = "No paths with slack < 0"; ETM max_combo_delay slack all positive (0.002~0.64ns), WNS(feedthrough)=0
8. **🔴 P1 — QA漏报 max_fanout**: report_drv_all / report_constraints show **9 max_fanout violations** (slack -1.0~-2.0): `U36/ZN(-2), U40/CO(-2), U21/CO(-1), U26/CO(-1), U28/ZN(-1), U33/CO(-1), U42/CO(-1), U60/ZN(-1), intadd_0_U14/CO(-1)`, constraint `max_fanout=1.0`. QA `vio_max_fanout=0` because `10_qa.tcl count_constraint_violations` requires "check type keyword" + `violat` on **same line**, but report format has them on separate lines → count always 0. Also 13 `min_capacitance slack=0.000 (VIOLATED: increase significant digits)` boundary items not counted.
9. **🔴 P1 — current_design = _sel1**: after link, `current_design = _sel1` (PT-generated internal name), `3_link_design.tcl` warns `CXDP-WARN: current_design is generated name '_sel1'`. SDC lines 9-11 `set_max_fanout 8 / set_max_transition 0.2 / set_max_capacitance 0.05 [current_design]` apply to `_sel1`, **cla_top shows "--" (unset)** in report_design. cla_top effective max_fanout=1.0 (lib/WLM default) → caused the fanout violations.
10. **🔴 P1 — check_constraints (GCA) failed but hidden**: `cla_top_check_constraints_...report` contains `Error: Current design is not defined. (DES-001)` + `Error: Constraint checking in GCA failed.`. Hidden because sta.tcl Message Summary only scans `sta_*.log` for `Error:*` lines, so reports `Error(0)`, QA "SDC errors clean" is false negative.
11. **🟠 P2 — virtual clock only**: SDC only `create_clock -name vclk -period 2 -waveform {0 1}` (no source, UITE-121 "Creating virtual clock"). `report_clock` Sources={} empty. `report_analysis_coverage` only 17 out_setup + 17 out_hold, **no reg-to-reg, no clock paths**; **17 out_hold all Untested(100%)**. hold "PASS=0" is misleading (untested ≠ clean).
12. **🟠 P2 — ETM ILM-004**: `write_interface_timing` warns `No clocks have been defined on the current design` (ILM-004), 33 ports `a[15:0]/b/cin/sum/cout` all `Port xxx is unconstrained` (MV-001). ETM interface timing model usability doubtful.
13. **🟡 P3 — only 1 corner ran**: config `CXDP_STA_CORNERS = ssgnp_v0p675_0c tt_v0p75_25c` but all_out/v1.0_Latest has only ssgnp reports. Need `make sta_sweep` or `make sta CORNER=tt_v0p75_25c`.
14. **🟡 P3 — lib list duplicated**: `lib_path/analysis_lib.f` repeats same 3 libs 12 times (36 lines), target_library redundant.
15. **🟡 P3 — netlist path** is `1103_clatop_syn/flow_cla_top/results/cla_top.mapped.v` (old 11-03 synth result).

## Conclusion table (agent's)
| 项目 | 结果 | 可信度 |
|---|---|---|
| 流程跑通 / link 干净 | ✅ OK, blackbox=0 | 高 |
| 组合 setup | ✅ 全满足 (WNS=0) | 高 (feedthrough) |
| hold | ⚠️ 未分析 (Untested) | 低–不可直接 PASS |
| Design rules | ❌ SDC 丢失到 _sel1; 9 条 max_fanout violation | 真实 violation |
| check_constraints (GCA) | ❌ DES-001 / GCA failed (hidden) | 已失败 |
| ETM/接口时序 | ⚠️ ILM-004 + 33 端口 MV-001 | 存疑 |
| QA 总结 | ❌ 报 PASS, 计数漏报 fanout, hold untested 算 0 | 不可信 |

## Case design (plan)
- **task form**: single-turn analysis-Q&A (Chinese markdown STA evaluation report), faithful to user turn-1 intent
- **A assets** (SUT-visible): reconstructed sta/run + all_out/v1.0_Latest + data/ tree from trace tool_results (Makefile, sta.tcl, sta_setup.tcl, CFG_VARS, CXDP_STA_CFG, proc/*.tcl, lib_path/analysis_lib.f, data/cla_top.sdc, data/cla_top.netlist.f, data/sta_override.tcl, all_out/v1.0_Latest/{QA/sta_qa_result, report/*.report, report/*.txt, log/sta_pre_WL_ssgnp_v0p675_0c.log, log/run_vars_ssgnp_v0p675_0c.tcl}, cla_top.mapped.v head)
- **B hidden** (judge-only, specificity oracle): a SYNTHESIZED different STA run — `sta_pre_WL_tt_v0p75_25c.log` with DIFFERENT root cause (e.g., `link_design FAILED` / `unresolved references` / different corner, NO _sel1 issue, NO 9 max_fanout, different QA outcome). check.py asserts SUT report contains A-specific signatures (corner=ssgnp_v0p675_0c, _sel1, 9 max_fanout, DES-001/GCA, hold Untested, ILM-004) AND does NOT contain B-specific signatures (tt_v0p75_25c, link_design FAILED, etc.) — anti-hardcoding.
- **check()**: subprocess parses SUT's markdown report (no script to run — pure Q&A); ≥15 independent content assertions on A-ground-truth signatures + anti-B overlap + randomized subset selection.
- **negatives**: §4.9 a noop / b print-expected / c core-deleted + d hardcode-b (copy B signatures) + e wrong-rootcause (claim OOM/license).

## Distinctness from r765 StaInterruptCauseAnalyze-001
r765 case (0arn6, same user e0046913): "分析任务中断原因" → root cause `link_design FAILED / unresolved / CXDP_BLOCK_RUN` (run did NOT complete).
This case (uyvi5): "评估本次STA运行结果" → run COMPLETED (_flow_status=0, QA PASS) but evaluation reveals PASS is untrustworthy (hidden violations, _sel1, GCA DES-001, hold untested). **Different intent, different root cause, different deliverable shape.**
