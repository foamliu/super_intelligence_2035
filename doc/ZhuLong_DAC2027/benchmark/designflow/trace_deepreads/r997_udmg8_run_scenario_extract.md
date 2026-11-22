# r997 deepread — 1794446541461_udmg8 (lein@hfeg0pkn005, mc396)

## Session
- user: lein, host: hfeg0pkn005 (10.129.32.75), mc=396
- keywords: verilog:2675; drc:564; netlist:194; cmos:42; rtl:22; analog:20
- A-pure (a=2697 > c=606 > bd=232), verification domain
- trace: 479 msgs, 18 user text msgs (act mode)
- scp via e0031982@hfeg0pkn005, file in subdir <sid>/<sid>.messages.json

## User intents (18 turns)
- U#0/U#4: refresh_parc.run 场景分析 ("此用例验证的场景有哪些？") ← **本case U#0**
- U#1: PRAC 语义纠正 (Per-Row Activation Count, RowHammer) — 用户先误导后澄清 PARC=Partial Array Refresh Control
- U#3: CS_CHECK/WL_CHECK/PRAC_CHECK 三宏在 Regressions 下哪些用例使用 ← **已有 case RegrCheckMacroMap-001 (r663)**
- U#6-U#8: project_pump_monitor.sv 加代码/注释/修正 perl bank→all+dual bank
- U#10-U#11: 为 lpddr6 平台写 pump_monitor SV 文件 (参照 ddr6 dscqa + ddr5 drcoa)
- U#13-U#14: TYPE_REF 定义位置 / refmonitors 实例化 / cbr_real[16:0] 采样
- U#15-U#17: ddr5 drcoa project_pump_monitor.sv 分析 / bind 机制 / TYPE_REF 结构体字段

## 本case (U#0): refresh_parc.run 场景提取
用户原话: "/rundata/decqa/V0/simdir/verilog/lein/1103_lp6tb/Regressions/proj_function/refresh_parc.run 路径下 此用例验证的场景有哪些？"

trace gold (A#1/A#4): refresh_parc.run 是 LPDDR6 PARC(Partial Array Refresh Control)+PASR 联动验证用例
- regression_name="refresh_parc", Config_Timing TS_1600/T_MIN/duty50
- 17条温度 ifdef 阶梯 (TEMPN→-40 ... TEMP130→110)
- randcase rhr_rate 3:00/0:01/0:10/0:11
- pasr_bits_start=8'b0000_0001 左移遍历
- case(mode) PARC_EN/PARC_DIS, pattern_name "PARC_EN&PASR--%0b"
- 操作: Refab/Refdb/SRE_T×3/Force_CBR/Deselectn, loop_nums case(trfc) 2→2/5→8/25→8/default→4

本case提炼为通用 extract_scenarios.py: .run→JSON结构化报告
- A=真实 refresh_parc.run (200行, 从trace tool_result恢复, 文件本身permission denied)
- hidden B=selfref_pdsr.run (TS_2400/T_MAX/duty45, 5条TEMP阶梯, rhr 01=5/10=2, pasr 8'b1000_0000右移, PowerDown+SelfRef无Force_CBR, loop_nums 4→3/9→6/default→2)
- check.py 20断言: B反硬编码A值 + 结构字段 + 确定性 + §4.9三假FAIL
- ref PASS 20/20 + 3neg全FAIL ✅

## 与已有case的关系
- RegrCheckMacroMap-001 (r663, U#3): CS_CHECK/WL_CHECK/PRAC_CHECK 宏→用例映射扫描
- 本case RunScenarioExtractProduce-001 (r997, U#0): 单个.run文件场景结构提取
- 不同子任务 (宏映射 vs 场景提取), 不同I/O (目录扫描 vs 单文件解析), 无intent-dup
