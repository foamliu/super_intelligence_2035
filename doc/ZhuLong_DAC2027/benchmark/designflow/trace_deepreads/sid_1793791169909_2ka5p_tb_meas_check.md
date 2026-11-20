# Deepread: 2ka5p (e0030760@hfeg0pkn004) — testbench 测量指令诊断

## trace_source
- user: e0030760, host: hfeg0pkn004, ip: 10.129.2.13
- session_file: 1793791169909_2ka5p.messages.json
- match_count: 257, spice_count: 1345, tool_total: 1737, spice_ratio: 0.774
- tools: 1251 hspice, 319 netlist, 94 spectre, 70 schematic, 2 virtuoso, 1 pyAether
- NEW vs 10-28 快照（19:2x 重扫 ssh_eda_search_20261105_192825/spice_candidates_NEW.tsv）

## A-档目标轮（USER#1, ts=1793791170268）verbatim
`/home/e0030760/Documents/Solido/test_fix.sp 帮我检查一下这个testbench，里面测试WSNM、Iread、Iwrite、Ileak的指令是否存在问题`
- ✅ 提出需求：给文件 + 问测量指令是否有问题。无根因、无修复方案。clean A-档。

## test_fix.sp（A 输入，verbatim, 77 行）要点
- include option_hspice.sp / pwr.sp / switch.sp + bitcell netlist
- .PARAM VIN=VVDD；.NODESET 设 6 个测试单元（WNM×2/HSNM/RSNM/IREAD/IWRITE/ILEAK）初始态
- 电源：V_power VDD=VVDD, V_input VI=VIN, V_input1 VIN_1=VVDD-VIN（互补扫）, VIPRB_READ/WRITE/STANDBY 0V 安培计
- .tran 1p 10ns + .DC VIN 0.0 VVDD 10e-3
- .MEASURE DC Iread FIND I(VIPRB_READ) AT=VVDD/2
- .MEASURE DC Iwrite FIND I(VIPRB_WRITE) AT=VVDD/2
- .MEASURE DC Ileak FIND I(VIPRB_STANDBY) AT=VVDD/2
- .Measure DC WNM_1 find v(VIN_1) when par('v(S1_WNM)-v(SB1_WNM)')=0 cross=1
- .Measure DC WNM_2 find v(VIN_2) when par('v(S2_WNM)-v(SB2_WNM)')=0 cross=1
- corners: ttg_sram_fs + pre_sim_fs, .TEMP 25, VVDD=0.675

## 金标准诊断（assistant ASST#15, 用户接受）逐项
1. ❌ **Iwrite — 原理性错误**：写电流是瞬态量，DC 稳态 FIND 必测到 ~0（实测 -6.66pA vs MC 期望 -482nA）。AT=VVDD/2 指向 VIN（与 Iwrite 无关），只是随便取点。修复：用 .MEASURE TRAN（WL 脉冲+BL 驱动+0V 安培计+iwrite_peak/avg）或至少 .MEASURE DC Iwrite MAX par('abs(I(VIPRB_WRITE))')。
2. ✅ **Iread — 能出数（21.86µA）但口径**：AT=VVDD/2 指 VIN=0.3375（与 Iread 无关），取到的是任意点静态读电流。若要动态放电电流需改 testbench。
3. ✅ **Ileak — 正常（31.3pA）**：待机 WL 关、BL=BLB=VDD，漏电合理。保留。
4. ✅/⚠️ **WSNM(WNM_1/2=250.5mV)**：互补扫 VIN_1=VDD−VIN，cross=1 工作。需确认定义是「写翻转位线电压(0.25V)」还是「VDD−VIN_at_flip(0.425V)」。
5. 其他：.tran 10ns 无任何 .MEASURE TRAN（白跑）；option BEHAVIORAL=1 unknown warning；pwr.sp vgnd 重复致 job aborted；MC measure_failures 264/22/51 多来自 Iwrite/crossing。

## case 设计（TbMeasCheck-001, spice_sim A-faithful L2）
- 交付：`tb_meas_check.py <testbench.sp> <out.json>` 通用解析 hspice testbench，对 Iwrite/Iread/Ileak/WSNM 各给 status(error/warning/ok)+problems+root_cause+fix + other_issues。
- hidden B（test_fix_B.sp）：不同问题组合 — Iwrite=error(DC FIND transient, AT=0), Iread=ok(AVG range), Ileak=error(standby bias wrong S_ILEAK=VVDD), WSNM=error(crossing 引用不存在的 S9_WNM)。VVDD=0.9, 扫参 VS, 不同 corner。强制通用解析防硬编码 A。
- check.py k=15: zip 入口/py_compile/B exit0+JSON/顶层 keys/4 measures/字段+status枚举/Iwrite=error/Ileak=error/WSNM=error/Iread=ok/Iwrite root_cause 含 transient|瞬态|稳态|steady/Iwrite fix 含 TRAN|ammeter|安培计|peak/other_issues 非空/A cross-input guard ok/problems 非空。
