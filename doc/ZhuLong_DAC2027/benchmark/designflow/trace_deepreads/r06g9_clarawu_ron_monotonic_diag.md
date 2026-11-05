# 1793338010547_r06g9 — clarawu RON 单调性诊断 + 优化迭代

## trace meta
- session_file: `1793338010547_r06g9.messages.json`
- user: clarawu · host: hfeg0pkn004 (10.129.32.75)
- match_count: 461 · spice tool 2089 / total 4144 = ratio 0.504
- 关键字: hspice/finesim:2089 netlist:312 schematic:41
- snapshot: ssh_eda_search_20261105_192825/summary.tsv (NEW vs 10-28)
- ledger: trace_ledger_B.tsv line 163 → status `case` (EDA-Eval-DesignFlow-RonMonoDiag-001)

## 用户意图（verbatim，作 case prompt）
> 检查刚仿真出来的RON曲线：@/home/clarawu/sim_iter/v5_all/v5.md0、v5#1.md0、v5#2.md0、v5#3.md0、v5#4.md0，rpd_50随zqcode变化的单调性，如果不单调，就优化电路

## 深读笔记（607 msgs）
- 5 个 .md0 = 5 PVT corner ALTER 仿真（temper 25/-40/110/-40/110C，alter#1..5），zqdec dc sweep 0..63，.measure rpd_50 取 pulldown on-resistance
- rpd_50 随 zqcode 递减但**不严格单调**：bit-4/5 边界 15→16、31→32、47→48 处反向跳变（zq-decoder 二进制权重位翻转处 RON 不单调）
- 根因：zq-decoder 高位晶体管 size 权重不匹配
- 优化半意图（**未入 case**，netlist_vZZ 权限拒绝不可读）：多轮 netlist 迭代 v5→v10h，L 统一到 30nm，rpd/rpu_50 全单调，mismatch≤4%
- 终态接受产物：netlist_v10h

## cased 子流（单调性检查+诊断）
- case: EDA-Eval-DesignFlow-RonMonoDiag-001 (spice_sim A-faithful L2, k=14)
- 交付: analyze_ron.py <md0_dir> <out.json> 解析 .md0 → rpd_50 vs zqcode 单调性 + 反向跳变点 + 根因分类
- A: 5 真实 .md0 (v5_all/) bit-4/5 边界 15→16/31→32/47→48
- B: 5 合成 corner bit-3 边界 7→8/23→24/39→40/55→56，rpd_50 116.5..400.0
- check.py 14 断言 a..n，6 negatives + §4.9 empty-shell 全 FAIL

## distinct ✓ vs
- McRonMismatch (mismatch 表 + corner 间一致性，非单调性边界)
- FineSimTbAuditFix (deck .meas 提取，非 .md0 解析)
- MeasExtractCornerTrace (静态 deck 提取，非 measure 数据反推单调性)
- AlterDeckSplit (deck ALTER 拆分，非 measure 数据诊断)
- RonMismatch (本 shard 既有，rpd/rpu mismatch 比对，非 zqcode 单调性 + bit 边界根因)
