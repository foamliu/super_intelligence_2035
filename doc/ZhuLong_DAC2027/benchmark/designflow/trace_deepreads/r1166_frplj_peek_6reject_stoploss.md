# r1166 选料轮 (0-case stop-loss) · 6 peek 全 reject

**日期**: 2026-11-24 21:12+
**shard**: B (spice_char)
**结论**: 0-case stop-loss (round 1/3)。真 peek 6 本域 fresh 候选全 reject。
**DEBT**: 1124 scan hspice-dominant 池未抽取到 workdir（ledger 排除需先把 done_sessions 写到 .75）；下轮先建 b_fresh_1124_hspice.tsv 再 peek。

## 候选来源
- b_fresh_1123_Bonly_538.tsv (mc≥5 hspice 池，r1110 重建)
- 直接 peek 1124 scan summary 中 hspice-dominant 条目

## 6 peek 清单与 reject 依据

### 1. my769 (e0017906@hfeg0plg96, mc620, hspice:99/drc:1867/netlist:868)
- **U0**: "你对模拟电路有没有什么好的分析方法" → "aether当前界面就是模拟电路，你分析一下" → "用 PyAether 写个脚本验证输入差分对的工作点" → "你没办法runhspice/finesim吗" → "去V0环境里边看" → "用官方 model+netlist 只跑 IO_CABufCore 的轻量 DC OP"
- **reject**: flow-driving 探索型，agent 最终未交付干净脚本，结尾 "要继续吗？" 无闭环 deliverable。drc/netlist 主导非 spice_sim 本域。判 weak。

### 2. usgf7 (aryaoy@hfeg0plg70, mc312, netlist:888/hspice:106)
- **U0**: 用户提供 test.sp (FineSim .alter 20 corner + PEX .spf + .tran + .measure) → "确认：一个TestBench放所有的DlyCell" → "必须在 Aether GUI 里建原理图再抽网表（路线 A）"
- **reject**: GUI-dependent schematic build (Aether 建原理图抽网表)，check() 无法在沙盒判分；非 L1 可复刻。park 不做。

### 3. bbei1 (eamonw@hfeg0plg101, mc290, drc:2979/lvs:586/netlist:405/hspice:30)
- **U0**: "两个项目网表差异比较，按子模块列出差异点" (wymLib_RowCtrl vs wymlib_DRCPA_RowCtrl)
- **reject**: near-dup 已有 NetlistStructDiff-001 / NetlistDiffBankLogic-001 / NetlistMisModCompare-001；drc/lvs 主导非 spice_sim 本域。

### 4. r1hnw (stanleyl@hfeg0plg102, mc271, netlist:864/aether:403/hspice:110)
- **U0**: "find the hierarchy of EccTop128x2New_DDGOA from TOP module"
- **reject**: near-dup 已有 HierarchyTrace-001 / WlHierarchyTraceProduce-001 / NetlistStructureGraphProduce-001。

### 5. frplj (ynbai@hfhds206, mc302, netlist:4738/hspice:37) — **已 cross-shard 占**
- **U0**: "写一个脚本，输入为netlist，输出为finesim ignore文件，抓 XIctop...XI_D_RWCBG 下一级 instance，输出 .option finesim_ignore 行"
- **reject**: 已被 shard D 占（ledger_D status=case, case_id=EDA-Eval-DesignFlow-FinesimIgnoreGen-001, cases/D/ 已有文件）。cross-shard 互斥，不可做。
- ⚠ 本轮深读了此 trace 的完整 deliverable (gen_ignore_all.py, msg 292, 4712 chars) — 若 D 的 case 下线可接力，但当前不做。

### 6. gtyj5 (easont@hfhds208, mc592, netlist:1942/waveview:334/hspice:33)
- **U0**: "can you read .../finesim.fsdb" → "有fsdb相关的MCP server吗" → "使用skill读取fsdb；根据波形说明signal的功能" → "读取netlist_AI,结合fsdb分析，说明模块功能"
- **reject**: analysis-only Q&A (波形+网表功能说明)，无程序化 deliverable，check() 无牙。waveview/netlist 主导非本域。

## 池状态
- 1123 fresh pool (b_fresh_1123_Bonly_538.tsv): hspice-dominant (top keyword == hspice, tv≥10) 仅 4 条，其中 zhuvs=已cased(r1113)、b99hz/k5jur/7c6ni mc≤4 低于 mc≥5 门槛。**1123 hspice-dominant 池真·耗尽。**
- 1124 scan (+6956 traces): r1163 估有 134 hspice-leaning fresh 候选，但未抽取成 pool 文件（需 ledger 排除，done_sessions 需先写到 .75 workdir）。**下轮首要任务: 建 b_fresh_1124_hspice.tsv。**

## 下轮计划
1. 把 4-shard ledger sessions 写到 .75 workdir done_sessions.txt
2. awk 1124 summary: hspice|finesim|spectre dominant, tv≥10, exclude done_sessions → b_fresh_1124_hspice.tsv
3. peek top 5，找 L1 可复刻 deliverable
4. 若连 3 轮 0-case (r1166 + 下两轮) 则转 §4.9 自查
