# Deepread: sid_1793935018992_a75vy — GrDecPwr ACT/PRE 验证 testbench

## Trace 来源
- session: 1793935018992_a75vy (dsgao@hfeg0pkn002, 231 msgs, 793KB)
- 11-06 11:0x 经 .75 run_commands 定向重扫（threshold 11-05 19:28）发现 NEW session
- mtime 11-06，**不在 11-05 19:28 快照中**（genuinely NEW trace，证 pool 未枯竭）
- ledger claim 11:2x, domain=spice_sim

## 用户意图（A-档 verbatim）
- **U#11（提出需求轮，纯需求 ✓）**：「现在我有一个secHV激励 上升沿是act,下降沿是pre,怎么做逻辑可以仿真看到 GrDecPwr 的上拉和下拉的过程中的电位变化」
- U#0: 「这个电路有什么」（探索）
- U#18: 「用nand将 SecHv 和 cm1_sw_total / cm1sw 做 逻辑 来 模仿 ACT 和 pre 时候 GrDecPWR 的变化」（需求延伸，非根因/修复）
- U#26: 「cm1_sw_total / cm1sw 在开关有效窗口内是高电平，且是恒定的」（补充约束）
- U#32: 「写一个验证tb」（需求）
- U#184: 「为什么下拉基本不工作」（诊断，不用作 A-档）
- U#186: 「减小 GrDecPwr 负载电容 cgr（200f→20f）」（调参）
- U#196: 「vwlp 电压给到3.4V，SECHV 的上升沿下降沿的 tr/tf =100ps」（调参）
- U#206: 「pvt corner 调整为 SS, -40C」（调参）
- ULAST: 「还是这个网表，不过优化了电路，再帮我验证一下」（新需求，session 未完成此轮）

## 电路背景
- R_GidlAryCtrl_switch：DRAM 行译码电源开关
- 端口：GrDecPwr, SecHv, cm1_sw_total, cm1sw, vss!, vwlp!
- secHV 上升沿=ACT（激活），下降沿=PRE（预充电）
- cm1_sw_total/cm1sw 在开关窗口内恒定高电平
- NAND(SecHv, cm1) → D：ACT 时 D=L → PMOS 上拉 GrDecPwr→vwlp!；PRE 时 D=H → NMOS 下拉（经二极管钳位，弱放电）

## Assistant 工具链
1. read_files(R_GidlAryCtrl_switch.netlist) → 分析 CDL 网表
2. editor → 写 R_GidlAryCtrl_switch_tb.sp（NAND 选相版 testbench）
3. read_files(ALPS netlist) → 确认 DUT 结构 + 模型库
4. run_approved_command(probe_finesim.py) → 探测 FineSim 可用性
5. run_approved_command(launch_sim.py) → 启动 FineSim 仿真
6. run_approved_command(parse_2cycle.py) → 解析 GrDecPwr 波形
7. 迭代调参：cgr 200f→20f, vwlp 2.6→3.4V, tr/tf=100ps, PVT tt/25C→SS/-40C
8. search_codebase → 确认模型段名（ss, MOS_SS）

## 金标准（用户接受的最终结果）
- 最终配置：vwlp=3.4V, cgr=20f, SecHv tr/tf=100ps, SS/-40C, 两轮 ACT→PRE, 100ns
- SS/-40°C 结果（ASST#226，用户接受后继续迭代=隐含接受）：
  | 时间 | 事件 | GrDecPwr |
  | 0-5ns | PRE(初) | 1.9915V |
  | 25ns | ACT#1 峰值 | 2.2523V |
  | 55ns | PRE#1 末 | 2.2711V |
  | 75ns | ACT#2 峰值 | 2.2914V |
  | 100ns | PRE#2 末 | 2.3123V |
- 关键发现：ACT 上拉明显，PRE 下拉弱（二极管钳位无直流到地通路）

## 合成规划
- case_id: EDA-Eval-DesignFlow-GrDecPwrVerifTb-001
- domain: spice_sim, track: faithful (A-档), level: L2
- 交付：gen_grdecpwr_verif.py <dut_netlist> <params.json> <model.lib> <out_dir>
  生成验证 testbench（secHV PULSE, cm1 恒高, NAND 选相, cgr 负载, .tran, .measure）
  → 运行 HSPICE → 解析 GrDecPwr 电压 → 写 grdecpwr_verif_result.json
- A/B 切分：stub DUT 不同 W/L + 不同 vwlp/cgr/temp/timing
  A: Wp=80u, vwlp=3.4, cgr=20f, temp=25 → v_act=3.4, v_pre=0.80
  B: Wp=50u, vwlp=2.6, cgr=50f, temp=-40 → v_act=2.6, v_pre=0.85
- check.py: 13 条断言 a-m（zip+compile+help+tb 结构 4 条+L2 hspice B+结果键+充电+达 vwlp+放电+跨输入）
- .75 HSPICE 真跑 A/B 均 job concluded，A v_act=3.4/B v_act=2.6 跨输入护栏 ✓
