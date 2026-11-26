# r838 — A-pure 枯竭第 8 次确认（11-19 全扫描，A-domain-keyword-top 全量核验）

**日期**: 2026-11-20
**轮次**: r838（0-case 选料轮）
**扫描源**: `ssh_eda_search_20261119_172105/summary.tsv`（44935 行 / 5694 dedup mc≥1 / mc10=3997 / 692 hosts）

## 一、方法

本轮不再只看 `trace_ledger next` 的 peek top-5（mc5-9 band），而是对**整个 11-19 扫描**按"A-domain 关键词为 top keyword"全量筛选，逐条核验台账状态。A-domain top-keyword 集合：`verilog / rtl / sdc / synthesis / innovus / primetime / vcs / dc_shell / formality / verilint / vivado / yosys / openroad / systemverilog`。

## 二、A-domain-keyword-top 候选核验（mc≥500 全部）

| sid | mc | user@host | top kw | 台账状态 | 结论 |
|---|---|---|---|---|---|
| w4x70 | 1575 | haoyut@hfeg0plg15 | verilog:3222 | **case** SpefAnnotAudit-001 (r831) | 已造 |
| 9knot | 986 | vincelu@hfeg0plg100 | verilog:6114 | **parked** r785 REJECT (char C SiliconSmart, cmos:5640/netlist:4613/lvs:676 主导 → C) | 已 parked |
| ppl5a | 557 | harrys@hfeg0plg58 | rtl:723/assembler:648 | **case** McuAsmGen-001 (2026-11-12) | 已造 |
| vi5wa | 541 | e0039602@hfeg0plg95 | verilog:1075/netlist:1049 | **case** NetlistModSplice-001 (2026-11-12) | 已造 |
| 6i6lk | 536 | jason17w@hfeg0pnd002 | verilog:4030/drc:2740 | **case** VerilogrunPreserve-001 (2026-11-09) | 已造 |
| pwhqb | 520 | jason17w@hfeg0pnd002 | verilog:3955/drc:2710 | **parked** redundant dup of 6i6lk | 已 parked |
| xm22u | 515 | jason17w@hfeg0pnd002 | verilog:3947/drc:2710 | **parked** redundant dup of 6i6lk | 已 parked |

**mc≥500 的 A-domain-keyword-top 候选 7 条，全部已 ledgered（4 case + 3 parked），0 条可造。**

## 三、mc5-9 band fresh 候选深读（peek top）

| sid | mc | user@host | keywords | 深读判定 | 域 |
|---|---|---|---|---|---|
| v593e | 82 | t0002614@hfeg0pkn004 | aether:346/netlist:295/schematic:114/mixed-signal | aether/cellview/schematic 主导 | C |
| hasla | 41 | zqzhan@hfeg0pkn001 | drc:2662/netlist:2246/analog/hspice | **已 case** FinesimForceNodeAdvise-001 (B, 2026-11-16); 深读确认 finesim DDR SPICE deck | B |
| frxg5 | 54 | hswang@hfhds201 | netlist:179/verilog:115/drc:81/synopsys:16 | **已 case** AgingScriptAnalyze-001 (B, 2026-11-16); 深读确认 finesim aging MOSRA 两阶段仿真脚本分析 | B |
| 7l4sx | 171 | e0017906@hfeg0plg96 | cellview:301/aether:217/drc:206/lvs:56 | aether/cellview 主导 | C |
| ibwba | 48 | zhililu@hfhds219 | spectre:210/maestro:202/virtuoso:190/pex | SPICE/spectre/maestro | B |
| i0cnz | 13 | mwxi@hfhds228 | calibre:84/verilog:47/drc:44/innovus:8 | **host 不可达** (10.129.32.228 No route to host), 无法深读 | n/a |
| 1e0xa | 23 | sagequan@hfhds0pbn14 | analog:30/calibre:16/hspice:15/rtl:10 | analog+hspice 主导 | C |
| kubzy | 29 | zhililu@hfhds219 | netlist:178/aether:167/schematic:83/lvs:31 | aether/schematic | C |
| f1pj5 | 27 | jingc@hfeg0pkn001 | aether:144/mixed-signal/floorplan | aether layout | C |
| cn4bl | 13 | steveny@hfeg0pnd001 | pyaether:97/virtuoso:20 | pyaether layout | C |

**mc5-9 band fresh 候选 10 条：2 条已 B case（frxg5/hasla）、1 条 host 不可达（i0cnz）、7 条 C/B 域。0 条 A-pure 可造。**

## 四、关键发现

1. **frxg5 (mc54) 与 hasla (mc41) 表面像 A**（verilog/drc/netlist 命中），**深读确认均为 B 域 finesim SPICE 仿真**：
   - frxg5: 用户原话「查看 matrixrun_aging 脚本并分析 aging 部分代码」= finesim aging MOSRA 两阶段仿真脚本分析-Q&A → B 已造 AgingScriptAnalyze-001
   - hasla: 用户粘贴 finesim DDR IO SPICE deck（drcpa/V0 regression），U#2「你直接给我个脚本语句告诉我怎么写就行」→ B 已造 FinesimForceNodeAdvise-001
   - **教训重证**：scan keyword verilog/drc/netlist 在 finesim 仿真目录会大量假命中（deck 里含 .option/netlist 文本），不能只看 keyword 判域，必须深读用户原话。
2. **mc≥500 A-domain-keyword-top 7 条全已 ledgered** — 高 mc A 料已全部采完，无遗漏。
3. **path-bug revival 矿脉已枯**：frxg5/hasla 均 subdir-ALIVE（flat NOFILE），但已是 B case，无 A 复苏空间。

## 五、结论

**A-pure 枯竭第 8 次确认**（r760/r761/r824/r826/r831/r835/r837 + 本轮 r838）。本轮用**全量 A-domain-keyword-top 筛选 + 逐条台账核验**取代此前的 peek top-5 采样，证据更 exhaustive：
- mc≥500 A-keyword-top：7/7 已 ledgered
- mc5-9 fresh：10 条中 0 条 A-pure 可造（2 已 B case + 1 不可达 + 7 C/B）
- 守任务初衷第 1 条：不为凑数造非真实 A 意图题；不为凑数把 B/C/D 强塞进 A。

## 六、处置

- 本轮 0 case（A.jsonl 415 不变，cases/A 不变，台账 A 685 不变）
- frxg5/hasla 已在他 shard B 台账（case），A 无需重复登记（跨 shard 互斥已生效）
- i0cnz (mc13, host 不可达) 暂不 ledger，待主机恢复或下次扫描
- DEBT 转向：(a) waveview_real_cases 协作 (b) intent_audit 续 (剩 295) (c) phantom-revival bug code-fix (d) 等运维扩池/新扫描

## 七、判分纪律

本轮不造题 = 不存在 check()/negative/hidden-B 产物。0-case 轮的"牙"在于**选料判域的诚实性**：每条候选的域判定都基于用户原话深读，而非 scan keyword 表面命中（frxg5/hasla 的 keyword-vs-原话偏差即为证据）。
