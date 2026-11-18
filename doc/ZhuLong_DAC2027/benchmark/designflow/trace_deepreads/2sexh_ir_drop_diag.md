# 深读笔记 · 2sexh · Totem-SC vss IR-drop 异常诊断

- **session**: 1792841178220_2sexh
- **user/host**: thomasz @ hfeg0pfn060 (10.129.33.186)
- **mc**: 18 | scan domain: netlist | **真实语义域: pg_layout / IR-drop (shard C)**
- **status**: parked (lean-C, defer to shard C) — r870
- **meta**: model=deepseek-v4-flash, interactive, 69 msgs (33 assistant / 36 user), started 2026-10-24 11:26, ended 2026-11-06, **terminal_marker=failed_external_process_exit (stale_session_reconciler) — 无用户明确接受的最终答案**

## 用户原话（verbatim, A 档可用）
> /rundata/totem/dscqa/IR/20261017/DDR6TOP_IDD5B_11600_TT1.025v70c/GEB_Report/DDR6TOP.ir.avg.lay.dr 看下这份报告里的vss ir drop明显异常，仿真log在/rundata/totem/dscqa/IR/20261017/DDR6TOP_IDD5B_11600_TT1.025v70c/run.log

## 真实意图
诊断 DDR6TOP_IDD5B (11600 MT/s, TT1.025V 70C) Totem-SC 动态 IR 分析中 **vss! IR drop 明显异常** 的原因，交叉参考 run.log。

## assistant 工具链（policy-engine 限制：run_commands disabled，用 run_approved_command + python-runner profile 执行自写 .py）
1. `list_allowed_files` 探 `/rundata/.../GEB_Report` 与 `db/` 目录
2. 写 `inspect_ir.py` → symlink 解析 + 文件大小：`DDR6TOP.ir.avg.lay.dr` 是 283MB 符号链接 → `db/data_mining/Report/av/avgIR/DDR6TOP.dvd.mmx.lay.dr`
3. 写 `peek_ir.py` 读 report 头部 → 列格式 `num,hierpath,type,location,power,drop(mV),volt(V),ideal_volt(v),mode,sch_hierpath`
4. `read_files` 读 run.log → 关键行 `max_pos_drop 0.0150437 at Instance(52476) Pin(7143644) max_neg_drop -1.36479 at Instance...`
5. 写 `analyze_ir.py` 按 power(net) 聚合 worst drop（修 row 长度守卫 bug）
6. 写 `vss_stats.py` 算 vss 分布：total boxes 1,125,934；netcount vss!=1,089,880；p50=12.05mV, p99=10.03mV, **worst=1314.84mV**（vss ideal=0V → -1.315V drop 明显异常）
7. 写 `peek_extra.py` 读 `pads.rpt` + `worst_xtor_pin_voltage.rpt`（vwlp! pin 3.04V @ x=-16208）
8. 写 `pads_analysis.py`（修 `f` 变量遮蔽 bug → 改 `flt`）→ vss! 仅 55 pads vs vblh! 689060
9. 写 `pads_ploc.py` 读 `PG_PAD.ploc.IDD5B` → 全部为 `.extra` pads（非物理 C4 bump）
10. 写 `pads_bounds.py`（解析失败）→ `read_files` 读 ploc 原文 → 格式 `name x y layer P/G`，**所有 vss pad 都在 x=-16097.704（单边）**

## 关键诊断事实（可作金标准断言，若 C 线造题）
- vss! AvgWorstIR = **1314.84 mV**（drop -1.315V，ideal 0V）— 异常
- vss! box 数 1,089,880 / 总 1,125,934；p50≈12mV 但 worst 1314mV → 局部热点
- run.log `max_neg_drop -1.36479`（与 worst drop 量级一致）
- vss! 仅 55 pads（vs vblh! 689,060），且 PG_PAD.ploc.IDD5B 中全为 `.extra` 派生 pad，非物理 C4 bump，全部位于 x=-16097.704 单边
- **结论方向**: vss 物理 pad 覆盖严重不足（仅 extra-derived、单边放置）→ PG 网络无有效供电 bump → 局部 IR drop 飙至 1.3V

## 为何判 lean-C（不归 D）
- 真实任务 = 电源完整性 / IR-drop / pad 放置分析 = **pg_layout**（TASK shard 配置明列 C: pg_layout）
- D-confirm 的 kw_D=96% 来自 transistor:40 计数，但语义上 transistor 仅出现在 netlist 文件名扫描，用户意图与 transistor/netlist/schematic/waveform 无关
- 同 r864 跨 shard 误分类模式（8n60f 同款）

## 为何 r870 不造题
1. 域属 C（pg_layout），D 造违「🚫 不改别人 shard」
2. session stale-reconciled，无用户明确接受的最终答案（违 A 档金标准要求，B 档可定义但域错）
3. 真实报告 283MB，造题需合成 miniature asset（C 线若造可参考本笔记）

## 资产路径（C 线若需）
- 报告: `/rundata/totem/dscqa/IR/20261017/DDR6TOP_IDD5B_11600_TT1.025v70c/GEB_Report/DDR6TOP.ir.avg.lay.dr` (283MB symlink)
- run.log: 同上目录 `run.log`
- ploc: 同上目录 `PG_PAD.ploc.IDD5B`
- pads.rpt: `db/data_mining/Report/av/pads.rpt`
- 均在 10.129.33.186 (thomasz, e0031982 可 ssh 免密)
