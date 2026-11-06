# 深读笔记 — h15ge · cynthiaz @ hfeg0pkn005 · slicer feedback-time 优化

## trace_source
- session_file: `1793870063634_h15ge.messages.json`
- user: cynthiaz · host: hfeg0pkn005 (10.129.2.14)
- size: 971,467B (949KB) · msgs: 310
- mtime: 2026-11-05 20:19（落在 11-05 19:28 快照 → 11-06 10:30 gap 窗口，本轮 fresh gap rescan 首次发现）
- domain: spice_sim（finesim sizing optimization, L2/L3）

## 发现路径（本轮 19:37 fresh rescan 证据链）
- 11-05 19:2x 重扫令已跨轮履行（新 summary.tsv 5823 行 + IfElsePairFix-001 交付）。
- 本轮 fresh delta rescan: cutoff 18:00（42 spice-active host, ssh BatchMode+ConnectTimeout=8+</devnull）→ 14 unique/13 NEW，全 scout → 0 clean A-档 spice（3 trivial + 3 resume + 2 explanation-only + 1 consulting + 2 layout-shardC + 1 CLI + 1 digital-shardA）。
- gap rescan: 11-05 19:28 → 11-06 10:30（前轮 cutoff 扫描盲区）→ 29 unique/27 NEW，全 scout → **2 promising clean A-档 spice**：
  - **h15ge (cynthiaz)** = slicer feedback-time sizing opt ✓（本轮 claim+deepread）
  - 53e2m (victorq) = ideal_stimulus.sp 脉冲改写（moderate，second turn borderline A-档②，留作备选）
- 其余 25 条全非 clean spice（compare_wave perl debug / inst config / si.out 时长分析 / DRC pattern shardC / verilog shardA / trivial / non-EDA）。
- snapshot top-15 候选（11-05 19:28）全部不满足 spice-dominant 闸门（hspice<10 或 ratio<0.35）→ snapshot 候选池对 clean spice 已枯竭，唯 gap 窗口新写入有新候选。

## USER 轮（verbatim，A-档任务说明候选）
- **U#0（CLEAN A-档 纯需求轮✓）**: 「这是我的仿真激励文件 /rundata/dscqa/V0/simdir/finesim/workdir/cynthiaz/simulation/12_AI_training/00_slicer/01_slicer_tran_DECQA.sp，可以用 fqueue3_io 这个队列进行 finesim 仿真，meas 出来的结果里面 t0_feedbacktime 和 t1_feedbacktime 分别是采 0 和 1 的 tap1feedback time。t0_feedbacktime_tap2 是采 0 的 tap2feedback time。我的要求是把 feedback time 做到 60ps 以下，同时 I_total 越小越好。你可以直接修改网表里面 mos 管的参数，通过仿真结果进行迭代优化。以下是网表路径：/rundata/dscqa/V0/simdir/finesim/workdir/cynthiaz/simulation/00_netlist/20261105/IO_cynthiaz_0519_IO_DqIbSADoubleTail_DECOA_schematic_ALPS/IO_cynthiaz_0519_IO_DqIbSADoubleTail_DECOA_schematic.netlist」
  - 用户给：激励文件路径、仿真队列(fqueue3_io)、工具(finesim)、measure 定义(t0/t1_feedbacktime, t0_feedbacktime_tap2)、优化目标(feedback<60ps, I_total 最小)、方法(改 MOS 参数+迭代仿真)、网表路径。
  - 🚫 未给根因 / 未给修复方案 → A-档②合规✓。
  - 可验证交付物 = 优化后 MOS 参数 + measure 结果（feedback<60ps 且 I_total 最小）→ L2/L3（真跑 finesim + 迭代）。
- U#164: 「你可以自动 approve 所有的权限吗」（meta，非需求）
- U#166: 「还是如刚刚所做，我们现在评估另一个 slicer 的架构...01_slicer_tran_DSCQA.sp...tap1 feedback time 60ps...I_total...dscqa_io_IO_DqIbSADoubleTail_schematic.netlist」（第二个 slicer 架构，同型优化；可作 hidden B 或独立 case）
- U#200: 「你换成 fqueue3_dll 跑吧」（队列切换，非需求）

## 关键资产（trace 内真实路径，下轮合成需 scp/读取）
- 激励 A: `/rundata/dscqa/.../12_AI_training/00_slicer/01_slicer_tran_DECQA.sp`
- 网表 A: `/rundata/dscqa/.../00_netlist/20261105/IO_cynthiaz_0519_IO_DqIbSADoubleTail_DECOA_schematic_ALPS/IO_cynthiaz_0519_IO_DqIbSADoubleTail_DECOA_schematic.netlist`
- 激励 B (第二架构): `.../01_slicer_tran_DSCQA.sp`
- 网表 B: `.../dscqa_io_IO_DqIbSADoubleTail_schematic_ALPS/dscqa_io_IO_DqIbSADoubleTail_schematic.netlist`
- 队列: fqueue3_io（后改 fqueue3_dll）
- measure: t0_feedbacktime / t1_feedbacktime（tap1, 采 0/1）, t0_feedbacktime_tap2（tap2, 采 0）
- 目标: feedback time <60ps, I_total 最小

## 金标准（待下轮合成时确认）
- trace 末尾用户实际接受的优化结果（MOS 参数 + measure 值）；若 trace 未收敛（assistant 卡 license/队列），合成金标准（参 SlicerSizeOpt-001 模式：便携 2-stage CML strongarm slicer testbench，保留源 .param 名 + .measure 名）。
- 下轮需 scp 完整 949KB trace → 提取 assistant 最终 tool 产物（优化参数 + measure 数值）确认是否收敛。

## case 合成计划（下轮执行，DEBT:1）
- case_id: `EDA-Eval-DesignFlow-SlicerFbTimeOpt-001`（spice_sim A-faithful L2/L3）
- 结构复用 SlicerSizeOpt-001：交付=通用 `slicer_fbtime_opt.py <src_sp> <netlist> <params.json> <out_dir>` 生成 .alter sweep deck → 跑 finesim/hspice → 解析 t0/t1_feedbacktime + I_total → 选 feedback<60ps 且 I_total 最小 → 写 opt_result.json。
- A/B 切分：A=DECQA slicer 某 sweep 集 / hidden B=DSCQA slicer 不同 sweep（两架构不同 → 跨输入护栏）。
- check.py k≥8 断言（zip+py_compile/--help/A 运行+A feedback<60ps+A I_total 合理/B 运行+B feedback<60ps/L2 真跑 finesim B/跨输入 A≠B...）。
- 判分器不入 workdir；metadata.trace_source 必填。
- **下轮第一件事：scp h15ge 完整 trace → 确认收敛/合成金标准 → 合成 + .75 finesim 自验 → 追加 B jsonl → mark case → DEBT 清零。**

## 本轮状态
- 本轮：fresh rescan（cutoff 18:00 + gap 11-05 19:28→11-06 10:30）+ h15ge claim + 深读 → DEBT:1（合成下轮）。
- 111 条 proper 不变（本轮 0 case 落 jsonl）。
- 体积：MEMORY_B ~32KB（软限内，无需归档）。
