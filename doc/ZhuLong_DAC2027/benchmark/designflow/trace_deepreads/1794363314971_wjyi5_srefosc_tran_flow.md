# deepread: 1794363314971_wjyi5 (junweix @ hfeg0plg76, spice_sim, mc19)

## trace 概况
- 19 msgs, 531KB, agent=lead, 2 substantive user turns
- 旧判 parked (r704, 2026-11-17 05:05): "tran.sp analyze Q&A 8 tool_use too short" — 旧规则 Q&A=not-produce 误杀
- 11-15 令 reaudit 复活: analysis-Q&A → produce 合法 (trace 531KB/19msgs/agent 读 tran.sp 159 行 + netlist_org 1131 行, 交付两份结构化分析)

## 用户原话 (verbatim)
- [msg0] `/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/codywang/DDGOA/srefosc/tran.sp 分析一下整个仿真的流程以及查看的信号`
- [msg7] `继续`

## agent 探查路径
1. list_allowed_files /home/junweix/Desktop → 4 个 .py 脚本
2. read_files tran.sp (159 行) → msg6 仿真流程分析 (10 节)
3. list_allowed_files ALPS 目录 → netlist_org, netlistHeader/Footer/log, force_power.inc, idealcap.cell
4. read_files netlistHeader/Footer/log/netlist_org → netlist 结构
5. read_files netlist_org:109-380, 804-1128 (SUBCKT 定义: nor3, SrefOscPwrCtrlGut0ZQIP)
6. read_files netlist_org:381-744 (inven, invhiz, ffrqLx1, SrefAnlgOscDrvZQIP)
7. read_files netlist_org:450-620 (SrefAnlgOscDrvZQIP 主体: invLx1/invLx4/nand2/ffrqLx1)
→ msg18 完整结论 (6 节)

## agent 交付 (verbatim methodology → methodology.md asset)
### msg6 第一轮: 仿真流程+信号 (10 节)
1. 仿真类型: Finesim(spicead/ALPS), .tran 20p 30u, 被测 SrefOscAnlgIP
2. 精度选项: accurate=1/gmin=1e-16/runlvl=5/finesim_mode=spicead/PARHIER=LOCAL/PORT_VOLTAGE_SCALE_TO_2X=1
3. 全局节点: vss!/vdd1!/vcc!/vdleq!, 电源 vvss=0/vvcc=1.05/vvdleq=1.17/vvdd1=1.8 + PWL vPwrOnVdleq(1µs)/vvPwrUpRst(5µs)
4. 修调: 8-bit cm1_ro_AdjSrefOsc<7:0> = tm0..tm7, 分两段: data_res(tm7/6/5 3-bit 8行) + data_cap(tm4..0 5-bit 32行)
5. tran 扫描: .tran 20p 30u $sweep data=data1 (data1 未定义! 只有 data_res/data_cap — gap)
6. probe: v(srefosc) + v(*)/i(*)/isub(*) level=5
7. measure: t_srefosc=(rise21-rise11)/4 (rise=7/11 @0.5V, 4 周期平均) + ion/ioff (avg i(vvdleq) 8-14µs/2-4.9µs)
8. PVT: tt/25℃ + alter105 ff/130℃ (res_ff, 其余 tt)
9. 流程总结一句话
10. 注意点: data1 未定义 / pvdleq 后置定义 / level=5 波形大 / measfile=0

### msg18 第二轮: 节点+机制+修调 (6 节)
1. srefosc = SrefOscAnlgZQIP 的 SrefOsc 输出端口 (经 invLx4 缓冲的数字时钟, 非裸电容节点)
2. 振荡机制: RC 张弛 (SrefOscComp1ZQIP 比较器/充放电环 + 5-bit cap array 细调 + 3-bit resistor tap 粗调), f∝1/(R·C)
3. 修调映射: tm7/6/5→电阻译码 TrimLvlEn<7:0>, tm4..0→电容 TrimCap<4:0>
4. data1 坑: 需合并 data_res(3列)+data_cap(5列)→data1(8列256行)
5. 完整数据流一句话
6. 设计频率: 需跑完用 t_srefosc 算

## 合成
- case_id: EDA-Eval-DesignFlow-SrefOscTranFlowAnalyze-001
- task form: spice_sim analysis Q&A → produce (产 tran_sim_flow_analyzer.py 解析 tran.sp+netlist_snippet → analysis_report.json 8 sections)
- A档 trace-faithful: 真实 tran.sp (159 行 verbatim from trace tool_result) + netlist_snippet (代表性 SUBCKT) + methodology.md (msg6+msg18 verbatim)
- hidden B cross-input guard: RingOscClkAnlgIP 7-stage inverter ring / HSPICE / .tran 10p 20u / 3 domains vdd!/vss!/vcore! (0.9/0/0.65) / 6-bit current trim single block 64 rows / probe v(clk_out)+i(vvdd) / measure period 0.45V rise=3/7 / 3 PVT corners tt/27c+ss/-40c+ff/125c
- 16 断言 (a0-a15+a16): zip+compile+入口+A/B 结构 + cross-input guard(simulator/step/global/supply/trim/probe/measure/pvt/oscillator/dut) + A-leak report+source + 确定性 + B-grounding
- ref 16/16 PASS + 4 negs (empty/print_only/hardcode_a/deleted_core) 全 FAIL
