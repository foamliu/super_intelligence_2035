# r1126 (2026-11-24) — 0-case 治理轮 · B-spice fresh 池 cross-shard dedup 重建 + §4.9 完整性确认

## 背景
r1125 判「扩池无效」(3 轮 19 peek 0 produce)，建议下一步：①等新 scan ②探低 mc high spice-density 段(keyword ratio 排序) ③§4.9 自查。本轮执行 ②③ + 修复 r1088 发现的 fresh 池 cross-shard dedup 过期问题。

## ① §4.9 selftest 完整性审计（shard B 全量）
- 扫描 cases/B/ 全部 case 的 reference/ 目录（含 full-name + short-name 两种命名约定）
- 检查 negative_selftest.py 是否存在（reference 根 OR reference/negative/ 子目录两处）
- **结果：208/208 shard B case 全部有 negative_selftest.py（0 缺失）**
- §4.9 selftest campaign 对 shard B 已完全收口（r1098-r1102 campaign + 后续 inline 产出均含 selftest）

## ② fresh 池 cross-shard dedup 重建（核心治理产出）
r1088 发现 b_fresh_1123_Bonly_538.tsv 的 cross-shard dedup 过期（yd89p/qsn6y 在 D 台账但 B fresh list 仍标 fresh）。本轮用全部 4 shard 台账（A:868 B:1738 C:1518 D:2048 = 4671 unique sids）重新 dedup：

| 口径 | 数量 |
|---|---|
| b_fresh_1123_Bonly 原池 | 538 |
| 扣 4-shard 台账后真 fresh | **200** |
| 真 fresh 且 spice kw count≥20 | **13** |
| 真 fresh 且 spice kw count≥50 | 4 |

→ 输出 `designflow/b_fresh_r1126_xshard_dedup.tsv`（200 行，准确的真 fresh 池，修复 r1088 dedup bug）

## ③ 真 fresh spice 候选逐一核验（suggestion #2 keyword-ratio 排序）
13 条 spice≥20 候选按 spice count 降序核验：

| sid | user | mc | spice | top_kw | 判定 |
|---|---|---|---|---|---|
| ts1wg | e0039786 | 1 | 306 | dbcreaterect | layout/PEX-dominant (shard C), mc1 噪声 |
| 5z9ge | han1liu | 102 | 67 | netlist | **本轮 peek**: HFSS/S-parameter touchstone 互容互感 + shmoo eye sim; SI/PI domain 非 B; park |
| udonu | yinyus | 105 | 60 | drc | drc-dominant (shard C) |
| mkazt | yinyus | 129 | 48 | drc | drc-dominant (shard C) |
| 4cdcu | junlingw | 56 | 41 | .lef | .lef-dominant, 低 spice |
| a36vu | kaixuanx | 51 | 33 | aether | aether-dominant, 无真 spice |
| samw8 | jason1t | 126 | 30 | netlist | netlist+cellview+pyaether, 低 spice |
| koykq | e0039786 | 51 | 28 | aether | **r1114 已 peek 拒**(/anasimpro-gui-start 斜杠命令) |
| 827bk | carlhe | 62 | 27 | verilog | verilog+drc, 非 spice |
| qjt9a | e0019946 | 1 | 25 | netlist | mc1 噪声 |
| 6kfqu | aryaoy | 8 | 24 | netlist | **r1114 已 peek 拒**(grill-me 规划命令) |
| v8ou8 | rongjiez | 12 | 23 | netlist | **r1114 已 peek 拒**(脚本干嘛+skill Q&A) |
| wgir6 | steveny | 103 | 22 | pyaether | pyaether-dominant, 非 spice |

**13 条全 reject**：4 条 r1114 已 peek 拒、5 条 layout/drc/aether-dominant 属 C/A 域、1 条 SI/PI 非 B 域(本轮 peek 拒)、3 条 mc≤12 低密度噪声。

## 5z9ge peek 详情（本轮唯一新 peek）
han1liu@hfeg0plg11 mc102 390msgs。U#0 "你是否会HFSS建模"→U#8 "已跑出 touchstone s30p 10 网络，看两对"→U#22 "计算 DQ0/DQ1 和 DQ2/DQ3 的互容互感"→U#33 "算两根线之间互容互感(port1→port11→port21 一金线)"→U#177 "生成脚本生成不同 config 重复跑 main_shmoo_va.py 获取所有 DQ 结果"。
**domain = SI/PI + HFSS + touchstone 互感互容提取 + shmoo eye sim**，非 spice_sim/characterization。hspice:67 是 shmoo flow 生成 .sp 的副产物。park 入台账（1738→1739）。

## 结论
- **r1125「扩池无效」结论经本轮 rigorously reconfirm**：用 4-shard 台账 dedup 后真 fresh 仅 200（非 538），spice≥20 仅 13 且全 reject。
- **r1088 cross-shard dedup 过期 bug 本轮修复**：输出 b_fresh_r1126_xshard_dedup.tsv (200 行) 作为后续选料的准确基线。
- **§4.9 selftest 对 shard B 完全收口**（208/208）。
- 残存真 fresh B-spice produce 候选 = 0。需新 scan 注入高 mc hspice/finesim/spectre-dominant 段，或转 ledger 治理 / §4.9 跨 shard 审计。

## 动作
- 5z9ge claim+park（1738→1739）
- b_fresh_r1126_xshard_dedup.tsv 落盘（治理产出）
- 台账 B: 1738→1739（+1 parked）
- 📊 covered=588/4529=13.0%(mc>=10, 不变)
- 🎯 最近20条 20/20=100%(观察值,不变)
- DEBT:0

## 下一步建议
1. 等待新 scan（>mc10 hspice/finesim/spectre/siliconsmart dominant 段）
2. 或跨 shard §4.9 审计（A/C/D 的 negative_selftest.py 完整性，本轮确认 B 已 100%）
3. 新 scan 到达后用 b_fresh_r1126_xshard_dedup.tsv 的 dedup 方法重建 fresh 池（避免再踩 stale dedup 坑）
