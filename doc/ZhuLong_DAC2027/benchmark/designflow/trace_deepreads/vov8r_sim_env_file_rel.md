# Deepread: 1789882357975_vov8r — xrxiong@hfeg0plg74

- session_file: `1789882357975_vov8r`
- user: xrxiong  host: hfeg0plg74 (10.129.8.230)  agent: lead
- match_count: 23  domain: waveform (shard D)
- msgs: 573  .messages.json: 831695 B
- old verdict (2026-11-14): `parked` "sim env file relationship analysis Q&A non-produce"
- revival: 11-15 mandate (Q&A/analysis-only revival) — re-classified as造-able code-grounded file-relationship analysis Q&A
- case_id: **EDA-Eval-DesignFlow-SimEnvFileRelAnalysisQA-001** (r807, A-grade verbatim)

## User verbatim U#1
> 分析一下这个仿真环境各个文件之间的关系

附 8 个文件: rhr_driver.sv / rhr_interface.sv / rhr_monitor.sv / rhr_top.sv / top.sv / cyclic_xyz.sv / rhr_probe.tcl / rhr_netlist.sv (DRAM Row-Hammer-Refresh 仿真环境).

## Gold answer (assistant msg[10], 6 节结构化分析)
1. 文件依赖图: top.sv `include` rhr_parameter.pkg / rhr_interface.sv / rhr_driver.sv / simulation.pat; rhr_top 实例化 DUT + driver + monitor + interface; rhr_netlist = 643KB DUT 门级网表
2. 各文件职责:
   - rhr_driver.sv: 6 tasks (osc_gen / act_pre_cmd / ref_cmd_panic / act_pre_cmd_dummy / act_pre_cmd_nop / ref_cmd) — 发 ACT/PRE/REF 命令序列
   - rhr_interface.sv: interface `rhr_behaviorio` — top↔monitor 桥接
   - rhr_monitor.sv: module `rhr_monitor` + tasks performance_monitor / sort_array, $fopen hammer_count.rpt / hammer_ratio.rpt / refresh_pump_report.rpt
   - rhr_top.sv: module `rhr_top` testbench, 实例化 DUT+driver+monitor, $fopen flush_addr_ive.csv
   - top.sv: module `top` 顶层, `include` driver/interface/pattern, import rhr_parameter::*
   - cyclic_xyz.sv: task `rhr_pattern` — 攻击循环 (x/y/z 嵌套 for, act_pre_cmd_dummy + ref_cmd_panic)
   - rhr_probe.tcl: database/probe/run/drivers/process/exit — waveform 采集
   - rhr_netlist.sv: DUT 门级网表 (R_RHDLUTFull_TestBench_TRNG_PRACAddSub2_Verilog_TOP, 含 R_RHRaddsub1Unit / R_RHRaddsubUnit 等子模块, 643KB 仅取 9665B 摘录)
3. 数据流: interface rhr_behaviorio 桥接 top 信号到 monitor; driver tasks 通过 interface 驱动; monitor 追踪 hammer_queue/hammer_count/hammer_ratio
4. 关键概念: RHR (Row-Hammer-Refresh) / Pump / DLUT / PRAC / TRNG / CBR
5. 仿真启动流程: rhr_probe.tcl → database -open waves → probe -create top -all → run → drivers -active → exit
6. 缺失文件: rhr_parameter.pkg 未附 (被 import 但不在 8 文件中)

## Case 设计
- A-grade: prompt = verbatim U#1 + brief 交付接口说明 (task_brief.md 仅说明交付物, 不说明任务)
- A assets (10): 8 .sv/.tcl + question.txt + task_brief.md
- hidden B (identifier-renamed, 零 A 重叠):
  - RHR→RFM, rhr_*→rfm_*, R_RH*→R_RF*, TRNG→TNND, PRAC→PRAD, hammer→hammr
  - SrefOsc→SlpOsc, osc_gen→osc_generate, act_pre_cmd→act_preq_cmd, ref_cmd_panic→ref_cmd_burst
  - cyclic_xyz→cyclic_abc, simulation.pat→sim_pattern.pat, simlib_→stdlib_, dscqa→dscqb, xrxiong→xrxiong_b
  - 52 A_ONLY_TOKENS 词边界校验零泄漏
- candidate_ref.py: 通用 SV/Tcl sim-env 分析器 (filename-pattern role classification primary; header-cell parse for DUT top; module-decl submodules; no hardcoded identifiers)
- check.py: 14 conditions (a-n), k_check=14=k_rationale
- 自验: ref 14/14 PASS, 4 negs FAIL (NEG_RC=0), §4.9 4 degen FAIL, 3-run md5 deterministic

## 关键工程教训
- rhr_netlist.sv 在 trace 中仅是 9665B 摘录 (原 643KB) — file_role 不能靠 size>10000 判定 dut_netlist, 必须用 filename pattern (`*netlist*`) 作 primary signal
- DUT top cell name `R_RFDLUTFull_..._TOP` 仅出现在 `// Verilog file for cell "..."` 头注释, 不在 excerpt 的 module 声明里 — candidate 须 parse header comment 提取 top_cell
- 子模块 (R_RFR*) 用 module 声明列表 (excerpt 含 2 个), 不用 instance 列表 (excerpt 的 instance 全是标准门 inv/and/xor)
- classify_top 须选 role==top_module 且 module 字面名 == "top" 的文件 (top.sv), 不选 rfm_top.sv (module rfm_top)
