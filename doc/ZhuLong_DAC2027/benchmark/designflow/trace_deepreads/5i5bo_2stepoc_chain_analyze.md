# trace deepread — 5i5bo (2StepOC chain analyze)

- session: 1793857124040_5i5bo.messages.json
- user: zqzhan · host: hfeg0pkn002 · mc=155 · domain: schematic_netlist/analog_context
- agent: lead · 134 msgs · 62 tool_use
- 私有资产 /proj/drcpa/V0/ 不可读 → B-grade synthesized

## 真实任务（用户原话要点）
1. 读飞书文档 + pyAether_API.md（pyAether 连接关系检查 API）
2. "你是不是可以检查电路的连接关系是否完整"
3. 学习仿真 pattern 文件 input.sp（2stepOC, Sim1103_HT101_LT010/TT_pvcc1p1_45C）
4. "先继续读 stimulus_2stepOC.sp / measure_2StepOC.sp，把这套 2stepOC 测试的激励和测量点也搞懂"
5. 最终目的："检查 2StepOc 功能，看看有没有什么优化的空间。2Step OC 功能就是 SA 的 OC 阶段，会分两步打开 NCS 和 PCS，对应 SanEn 和 SapEn 信号第一个 pulse 的上升沿是分步打开的"

## agent 过程
- fetch飞书doc(失败,需登录) → 读 pyAether_API.md（dbSeCheckDesign/emyNetGetPinFigs 等）
- 读 input.sp: .option finesim_mode=promd, .lib model, .temp 45, .param pvcc=1.1/pviso=1.389/ORG=8, .include BiasTrimAccuracy
- 读 stimulus_2stepOC.sp: Vcm1_ro_2StepOC cm1_ro_2StepOC 0 PULSE(pvcc pvss 0 tr tf 256*t0 512*t0)；Vcm1_ro_2StepOCNTDis PULSE(...128*t0 256*t0)；2StepOc temp trim 注释掉；SaNP HTLT trim
- 读 measure_2StepOC.sp: 大量 .meas tran OC_Rise_Dly_N / OC_Fall_Dly_N (N=1..~177)，trig v(xi147.xi_m768meg.sapenbusec35) val='pvpcsg/2' rise/fall=1 td='2*t0*N'，targ v(xi147.xi_m768meg.sanenbusec35) val='pvdleq/2'
- 找到 netlist.presim (21MB/59867行/805 subckts)，grep 2StepOc → 33 命中
- 抽 subckt: RasSim_2stepOcCtrl（trim/温度/PN 选择→cm1_ro_2StepOcDlyo<3:0>+TwoStepOcEn2AryNPre）、R_TwoStepOCtrimDly（可编程 RC 延迟，4-bit trim，PMOS 上拉+电容 cg3..cg16 二进制定权 1/2/4/8/16/32）、RasSim_NcCtrl_LPwr（两路 mxi2LVx1 复用器，TwoStepOc 选"直接 SecEnOn"与"延迟 SecEnOn_2stepOC"→SaOnNCS/SaOnPCS）、R_SaCtrol（SanEn/SapEn 驱动，SanEnN/SapEnN 经 invx2_xdec）

## 最终交付（msg#133，2843字）
"2StepOC 功能链路（已从 netlist 还原）"4 阶段：
① RasSim_2stepOcCtrl — 控制/trim 码选择（温度分区 HT/LT/NT + P/N switch + Dly/Dly2 两组码 → cm1_ro_2StepOcDlyo<3:0> + TwoStepOcEn2AryNPre）
② R_TwoStepOCtrimDly — 可编程延迟单元（4-bit trim，RC 梯+电容二进制定权，Out 同相跟随 In 延迟）
③ RasSim_NcCtrl_LPwr — NCS/PCS 控制（两路 mxi2LVx1 复用，TwoStepOc 在"直接 SecEnOn"与"延迟 SecEnOn_2stepOC"间选 → SaOnNCS/SaOnPCS）
④ R_SaCtrol — SA enable 驱动（SanEn/SapEn）
+ 可优化点（温度自适应延迟码、RC trim 分辨率、P/N 对称性等）

## B-grade 合成方案
真实 netlist 21MB/private 不可读 → 复刻"分析阶段"：给一个忠实迷你 SPICE netlist（4 阶段 2StepOC 链 + 可编程 RC trim + NCS/PCS mux + SanEn/SapEn drv）+ stimulus（PULSE）+ measure（.meas tran OC_Rise/Fall_Dly_N），让候选写 chain_analyze.py 解析网表还原链路结构 + 统计 trim bits / measure / stimulus，输出 chain_report.json。隐藏 B 换成 3 阶段/3-bit trim/不同信号名（SAE_NCS/SAE_PCS）/不同 measure 计数。
