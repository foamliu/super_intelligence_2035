# Deepread: f2xzx — Vwlp switch-pumpcore 电路报告生成 (ryanren)

- **session**: `1793586031652_f2xzx.messages.json` (ryanren @ hfeg0pfn120 / 10.129.33.246)
- **mc**: 156 · **domain**: spice_sim · **kws**: hspice:186 (ratio 0.30 估算, 768KB 1 user turn)
- **发现途径**: 11-05 重扫令 — 1109 新扫描 545 fresh shard-B 候选；按 spice-dominant + new-user 过滤后 peek，f2xzx 为新用户 ryanren（B jsonl 110 个既有 user 中无）的首条真实 produce-task。
- **claim**: r418 ledger_B claimed (2026-11-12 05:1x)

## 用户真实任务（trace 原话）
msg[U1] user（**唯一**用户轮，agent 单轮长工作 768KB）:
> 根据 `/proj/dscqa/V0/simdir/hspice/ryanren/switch_pumpcore_test/test_1030/test_lv_new.fsdb` 的仿真波形，以及 DSCQA/V0 下 Ryantext 库中 `Vwlp_switchcore_test` 的电路，生成一个电路报告。这个电路是我在 Vwlp 的基础上改进的，新增的部分可以在 PASS 有效时直导通。

= 核心：读 HSPICE `.fsdb` 波形 + Vwlp_switchcore_test 电路，生成结构化电路报告，重点说明「在 Vwlp 基础上改进、PASS 有效时直导通」的改进点。

## .fsdb / 电路关键字段（grep 计数）
- fsdb=283（重度 FSDB 波形读取，Synopsys 波形二进制）
- Vwlp=1461（电路核心 net/实例名密度高）
- netlist=120, PASS=116（PASS 信号是改进核心）
- 报告=28, .tran=7, .measure=1
- tr0=0（用 .fsdb 不用 .tr0）

## agent 报告结构（从末尾 assistant text 提取，原文中文）
报告包含 6 节：
1. **电路层次结构**
2. **每个关键子电路的详细分析**（含端口定义、MOS 管尺寸、电容值）
3. **与原始 Vwlp 的对比表格**
4. **基于 FSDB 实际波形的时序分析**（含时序图）
5. **仿真条件**（工艺角、温度、激励序列）
6. **改进总结与结论**

## 关键波形/电路事实（agent 从 FSDB 读出的实测，用于忠实重建）
- 泵输出 `net2` 在 ~40ns 内从 **0.08V** 泵升至 **2.95V**
- Pass 有效期间（**19.4μs ~ 22.0μs**）Vwlp 稳定在 **2.95V**
- 直通路径有效降低了导通阻抗（PASS-gated direct conduction improvement over baseline Vwlp）
- 电路 = Vwlp 开关泵核（switch pumpcore）+ 新增 PASS 直导通支路

## 为何 A 档不可行 / B-synthesized
- 真实 `.fsdb` 在 `/proj/dscqa/.../test_lv_new.fsdb`，是 Synopsys 二进制波形，且 `/proj` 路径在沙盒不可达；FSDB 二进制无法直接作附件（体积+格式）。
- 真实电路在 DSCQA/V0 Ryantext 库（私有 PDK 单元），不可直接复用。
- ⇒ A 档（真实 .fsdb + 真实电路）不可行；按 §3 用 **B-synthesized**：
  - 忠实复刻电路拓扑（Vwlp 开关泵核 + PASS 直导通支路，PMOS/NMOS 开关 + 电容 + PASS 控制信号）
  - 用 **ASCII .tr0 / .meas 文本输出**（HSPICE `.option post=2` 产的文本波形或 `.measure` 结果表）替代二进制 .fsdb，保留关键节点 net2/PASS/Vwlp 的真实量级（0.08V→2.95V, 19.4-22.0μs）
  - 生成 A(可见)/B(隐藏) 两套，节点数/电压量级/PASS 时窗均不同（B 反硬编码）

## 合成计划（下轮首事交付，DEBT:1）
**case id**: `EDA-Eval-DesignFlow-VwlpPumpReport-001` (spice_sim / L2 / B-synthesized / k≥12)
- **资产 A**（可见）: `assets/.../A/` 下
  - `vwlp_pumpcore_a.sp`：合成 Vwlp 开关泵核 HSPICE 网表（PMOS 开关 + NMOS 下拉 + 泵电容 + PASS 直导通支路 + .tran + .measure）
  - `sim_a.tr0` 或 `meas_a.txt`：HSPICE 文本波形/measure 输出，net2 0.08V→2.95V @ ~40ns, PASS 窗 19.4-22.0μs（A 值）
  - `circuit_desc_a.json`：电路层次/端口/MOS 尺寸/电容（A 版）
  - `task_brief.md`：任务说明（生成 6 节结构化电路报告）
- **隐藏 B**: `hidden/` 下 vwlp_pumpcore_b.sp + sim_b.tr0/meas_b.txt + circuit_desc_b.json（**不同**节点数/电压量级/PASS 时窗/MOS 尺寸，B 反硬编码）
- **reference**: `vwlp_pump_report_ref.py` — 读 B 的网表+波形+desc，生成 6 节报告（Markdown）：
  - §1 电路层次（顶层 + 子电路列表）
  - §2 子电路详细（端口/MOS 尺寸 W/L/电容值，从 desc_b.json 提取）
  - §3 与原 Vwlp 对比表（基线 vs 改进，直导通支路差异）
  - §4 基于波形的时序分析（net2 泵升时间 + PASS 窗 + Vwlp 稳态电压，从 meas_b.txt 提取）
  - §5 仿真条件（工艺角/温度/激励，从网表 .tran/.option 提取）
  - §6 改进总结（PASS 直导通降低导通阻抗）
- **check.py ≥12 断言** (a..l):
  a. zip 解压 + py_compile 通过
  b. 候选脚本在 B 上 exit 0 产 report.md
  c. report 含 6 节标题（层次/子电路/对比表/时序分析/仿真条件/改进总结）
  d. §2 含 B 的 MOS 尺寸（W/L 值与 desc_b 一致，反硬编码 A 值）
  e. §3 含「直导通支路 / PASS / direct conduction」改进点描述
  f. §3 含对比表（基线 Vwlp vs 改进，≥2 行）
  g. §4 含 net2 泵升电压量级（B 的值，tolerance，反硬编码 A 的 2.95V）
  h. §4 含 PASS 有效时窗（B 的 μs 范围）
  i. §4 含 Vwlp 稳态电压（B 的值）
  j. §5 含仿真条件（工艺角/温度/.tran 时间，从网表提取，与 B 网表一致）
  k. 跨输入 A 也运行 exit 0（泛化）
  l. 反硬编码：B 的 net2 电压 ≠ A 的 2.95V（B 报告里的值必须是 B 的，非 A）
  (m) 反空转：report 非空且 §1-§6 均非空（n）数值来自 B 波形而非固定串
- **negative**: naive_copy(A 报告) / only_print_sections / hardcoded_A_values / empty_report / ref_core_deleted（全 FAIL）
- **test_rationale**: `14 条断言：①…` (k_check==14≥8)

## 11-09 扫描 / 本轮 peek 取证（0-CLEAN-deliverable 证据链）
- 本轮 peek 22 个 1109 fresh spice-dominant 候选（top spice_primary + new-user 优先）：
  - **3 个 produce-task 全是 dup**：ws2bi→SpiceSim-001 (irene1li, 同 session 同 tr/tf/duty/skew)、x6taw→McRonMismatch-001 (clarawu, 同 RON_PU/PD_mismatch 6×std/230)、81adx→x6taw verbatim dup
  - **1 个 produce-task dup-risk**：65daa (tongni Vcc2scAct 第 6 个 tongni case, 覆盖递减)
  - **14 个非 produce / wrong-type**：ujw1y/9knot/qzva9/roznq/tc4yu/pqeal/bsjfb/p8z88/t1epq(consultation), 3h21t(bridge debug), n78nn/6dmno(skill), z6elv(chit-chat), 71ttn(continuation), la00c(collaborative)
  - **1 个 borderline**：ca3hh (guangmingz '解析dsim_block', 单轮简短, deliverable 不明)
  - **1 个 viable new-user CLEAN**：f2xzx (ryanren, Vwlp 电路报告, L2 judgeable) ⇒ CLAIM + 本 deepread, DEBT:1 合成下轮
- ⇒ 本轮 0 case 交付（DEBT:1 f2xzx 未合成），但**池未枯竭**：f2xzx 为可行新候选，545 fresh 仅 peek 22（top spice-dominant），余 523 未 peek；1105 口径 mc10.fresh=0 但 1109 fresh=545 持续有效。
- 20 个 peeked rejected 已 park ledger（含 3 个 dup 发现，防下轮重 peek）。
