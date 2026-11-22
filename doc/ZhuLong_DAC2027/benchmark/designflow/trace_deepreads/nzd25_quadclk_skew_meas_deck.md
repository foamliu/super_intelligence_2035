# nzd25 — kaixuanx 四相时钟 skew .measure deck 生成

## 元数据
- session: `1795225694332_nzd25.messages.json`
- user: kaixuanx @ hfeahpc501 (10.129.x)
- mc=83, keywords: sp=50(hspice/spectre/simulator), v=0, s=44, net=12 → spice-dominant
- scan: summary_20261121_151844.tsv (Nov 21 15:21)
- 103 msgs, 823KB, agent=lead, model deepseek-v4-flash
- **路径修正发现**: cline 新版 session 是**目录** `<slug>/<slug>.messages.json`，非 flat `<slug>.messages.json`。
  r1017 "NFS stale" 误判根因 = 扫描记录 flat 路径但实际嵌套在目录内；`head` flat 路径 ENOENT，目录内文件完好可读。
  **此修正解锁 r1017 误判 parked 的全部 fresh 候选**。

## 用户真实意图 (6 user turns)
- U0/U1: "我想计算 ICLK/QCLK/IBCLK/QBCLK 四相时钟的 skew，帮我统计以下，帮给出可以写入到 .sp 文件的 .measure 命令"
- U2: "我现在已经打开了 waveview 文件，帮我统计我 plot 的四个相位波形的 skew"
- U3: "现在只有一个了"
- U4: "v(iclk_hf) v(qclk_hf)"  (信号名)
- U5: /proj/drgoa/V0/workdir/kaixuanx/simulation/TB_DLL_4PGen_DL_4PGen_schematic_ALPS/results/tt_25_1p1.fsdb
- U6: "统计的不对，电压不对，skew 应该在 109 左右" (校正：阈值/skew 量级)

## 两阶段意图
- **Phase 1 (U1, msg A[5])**: 生成 HSPICE `.measure` deck —— 四相时钟 skew（when 型绝对穿越时刻 + param 合成间隔 - 理想相位）。
  **本 case 取 Phase 1**（便携、结构可判分、纯 spice_sim produce，无需 .fsdb/WaveView 二进制）。
- Phase 2 (U2-U6, msg A[7..]): WaveView ACE Tcl 在 .fsdb 上实测四相 skew（需真实 .fsdb + WaveView bridge，不便携，判分无法跑 WaveView）。
  信号 v(iclk_hf)/v(qclk_hf)/v(ibclk_hf)/v(qbclk_hf), VDD≈1.2V, 阈值 0.587V, 周期~434.7ps(2.3GHz), 1473 稳态周期。
  Phase 2 的 skew≈109 对应 ps 量级（与周期 434.7ps 一致，T/4≈108.7ps ≈ 109）。

## 参考 deck (A[5] 逐字) — Phase 1 交付
```spice
.param clk_th = 'vddx/2'          $ 阈值=VDD/2
.param tq90   = <T/4>             $ 理想 90 度间隔 = 周期/4
.param Nedge  = 5                 $ 上升沿序号
.param td0    = 2n                $ TRIG 等待窗

.measure tran t_I     when v(ICLK)  val='clk_th' rise=Nedge td='td0'
.measure tran t_Q     when v(QCLK)  val='clk_th' rise=Nedge td='td0'
.measure tran t_IB    when v(IBCLK) val='clk_th' rise=Nedge td='td0'
.measure tran t_QB    when v(QBCLK) val='clk_th' rise=Nedge td='td0'

.measure tran d_IQ    param='t_Q  - t_I'
.measure tran d_IIB   param='t_IB - t_I'
.measure tran d_IQB   param='t_QB - t_I'

.measure tran skew_IQ    param='d_IQ  - tq90'
.measure tran skew_IIB   param='d_IIB - 2*tq90'
.measure tran skew_IQB   param='d_IQB - 3*tq90'
.measure tran skew_QBIB  param='d_IQB - d_IIB - tq90'

.measure tran skew_abs_IQ   param='abs(skew_IQ)'
.measure tran skew_abs_IIB  param='abs(skew_IIB)'
.measure tran skew_abs_IQB  param='abs(skew_IQB)'
.measure tran skew_max  param='max(skew_abs_IQ, skew_abs_IIB, skew_abs_IQB)'

*.option measdgt=6 measfile=1 measform=3
```

## reframe 为参数化 produce 任务
`quad_skew_meas_gen.py <netlist.sp> <spec.json> [--out <measure.sp>] [--report <report.json>]`
- 读 netlist 提取可用 v() 节点（.probe v(sig) 行 / 节点声明）→ 验证 spec 信号 ∈ netlist 节点
- spec: {ref_sig, phases:[{name,sig,ideal_quarters}], vdd_param, period, nedge, td, sim_type}
- 输出 .measure deck: 1 ref + N phase when-measures @ threshold rise=nedge td=td; N interval params (phase-ref);
  N skew params (interval - ideal_quarters*tq90, tq90=period/4); N abs + 1 max; .option 行
- L1, 纯 Python 无 EDA 二进制, 结构化判分（regex/grammar 解析 .measure, 非文本相似）

## 判分齿（核心反 naive/反硬编码）
- when 信号名必须来自 spec B（反硬编码 A）
- skew = interval - ideal_quarters*tq90（反 naive 只输出 interval 不减理想相位）
- tq90 = period/4（反 naive 硬编码 90°固定值）
- 信号必须存在于 netlist（反 naive 不读 netlist 凭空输出）
- abs + max 汇总（反 naive 只输出原始 skew）

## 去重 distinct
vs CmdEdgeMeasGen(单信号 Nth-edge 门控)/DutySkewAvg(分频器多相 duty+skew 窗口均)/Mt0TskewCalc(.mt0.csv 后处理)/CaSkewEdgeStat(.fsdb 波形文本 stat)/TimingMeasGen(单边沿 50% 时差)/DevFourTermMeasGen(四端器件电流) — **本 case=四相正交时钟 when+param+理想相位偏移减法 skew deck 生成，无重复** ✓
