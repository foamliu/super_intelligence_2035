# trace_deepread: 1795067700169_7ns06 (joeyl @ hfeg0plg53)

- **mc=96**, keywords: `netlist:150;synopsys:110;schematic:66;hspice:54;aether:6;mosfet:5`
- **session**: `1795067700169_7ns06` (forked from `1795067695624_n0rn3`), model `deepseek-v4-flash`, status `failed` (external process exit), 174 msgs, 21h span.
- **cwd**: `/ai_sandbox/drgqa/V0/agentdir/joeyl`

## 用户意图（原话）

> 请看这两个 testbench，里面都只有一个 diff 电阻，但分别属于 v1 和 hl22 工艺，我想请你帮忙仿真电阻的 tt，ss，ff corner，并绘制出 3 个 corner 的 -40～130 摄氏度的电流曲线（step=10 摄氏度），并对两个工艺的电阻 variation 进行对比并绘图

两个 testbench：
1. **v1**: `/rundata/drvsa/V0/simdir/finesim/workdir/joeyl/simulation/15_res/1_tran.sp` — `XRR1 vcc! vss! vss! rndiff_3t_ckt l=5e-6 w=120e-9 flag_res=1 nm=2`，模型 `.lib '/proj/drgqa/V0/model/current/model.sp' tt` + `incFile_lp` 的 `res_tt/bjt_tt/...`
2. **hl22**: `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/ex_res/1_tran.sp` — `rndif_3t`（l=25e-6 w=2e-6），模型 `/proj/m2701/V0_DDR4/model/current/model.sp`（22nm ULL, hspice, -40~150C），corner 走 `v0p5_0d13/...lib` 的 `tt_res/ss_res/ff_res`

## 关键技术事实（从 trace 抽取）

- **FineSim** `/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim` 可用；Python 3.7.1 + numpy 1.21.6 + matplotlib 3.5.1。
- **v1 电阻模型 `rndiff_3t_ckt`**（来自 incFile_lp）：pins `n1 n2 sub`；`rsh=(243+drsh_rndiff)*(1+rshmis)` @ ref temp 98C；`tcoef_temper=1+(temper-98)*(tc1r+tc2r*(temper-98))`，`tc1r=1.16e-3, tc2r=3.59e-7`（正温度系数，R 随 T 升）。
- **hl22 电阻模型 `rndif_3t`**：在 `v0p5_0d13/hlmc_cl022ul_spice_v0p5_0d13_for_vodka_shrink0d855.lib` 的 `tt_res/ss_res/ff_res` section 下，l=25e-6 w=2e-6。
- **45C v1 .op**：`i(vvcc)=1.1452e-4 A`，电阻分 4 段 body(r1-r4 各 2132.5Ω) + 2 contact(r0/r5 各 101Ω)，总 R≈8732Ω。
- agent 的策略：在 agentdir 里重建 testbench + 扫 corner×temp 跑 finesim，解析 `.meas`/`.op` 取 `i(vvcc)`，matplotlib 绘图。

## 为什么选这条

- **真实 trace**：用户原话完整、意图清晰（corner×temp 表征 + 跨工艺对比）。
- **本 shard 契合**：spice_sim/characterization 的典型流（FineSim + corner + temp sweep + 绘图）。
- **可复现**：真实 PDK 模型在 /proj 下对沙盒不可读（permission denied），但电阻模型是行为级 R（rsh×leff/weff × tempco），可自包含重建，物理保真。
- **check 有牙**：解析 .sp 参数 → 解析公式算 R(T,corner) → I=V/R，数值可精确校验（<1%），corner 顺序 ss<tt<ff、温度单调性、3 corner×18 temp 覆盖、plot 存在，共 12 条独立断言。

## case 化决策

- **L1（离线 Python 复刻）**：沙盒内 FineSim 可跑但真实 PDK 不可读；行为级 R 模型可解析计算，等价于仿真结果。判分器用 subprocess 跑 SUT 脚本于隐藏 B（不同 rsh/tref/tc/l/w/nm/pvdd），校验数值 + 结构 + 物理。
- **隐藏 B**：v1_B(rsh=210/222.6/199.5, tref=85, tc1=1.25e-3, l=8e-6, w=150e-9, nm=3) + hl22_B(rsh=165/175/155, tref=30, tc1=1.4e-3, l=20e-6, w=1.5e-6, pvdd=1.2)。
- **case_id**: `EDA-Eval-DesignFlow-ResCornerTempSweep-001`
