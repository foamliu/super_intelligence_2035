# Deep-read: 1789607429323_ly1qu (yzwang @ hfeg0pkn001, mc=31, layout_aether)

## 会话概况
- session: `1799607429323_ly1qu` (修正: `1789607429323_ly1qu`), user=yzwang, host=hfeg0pkn001, mc=31
- 734KB messages, 27 msgs (14 user / 13 assistant), 2026-09-17 01:10→08:14 (~7h), model deepseek-v4-flash, cwd `/home/pdk/yzwang`, status failed
- keywords: dbcreaterect:304, drc:232, dbcreatepolygon:69, dbcreatepath:68, dbcreatelabel:40, pdk:27, calibre:16, ddgetobj:4
- tools used: read_files×8, editor×2, run_commands×1（assistant 受 policy 限制无法直接写 /tmp 附件，最终以分析报告形式给出修改方案）

## 用户三轮真实需求
1. [0] 「这是一个关于DRC的QA报告，请系统总结一下」+ 附件 drcQa_..._Rev12_yzwang_2026-08-11.report (214KB) —— 总结 DRC QA 报告（非 seed，无交付物）
2. **[4] seed**：「这是一个pcell，用来QA drc写的是否正确，这个pcell中有许多pattern，但有些pattern在space和width设置成某种条件时会重合，现在已知我在默认设置下，生成的第四个和第五个pattern可能会重合，第六个和第七个pattern可能会重合，请帮我看看第五个和第七个的起始坐标应该怎么更改」+ 附件 oneOrTwoLayerSpaceFail.il (55.6KB SKILL, 1439 行)
3. [23] 跟进：「条件跟我上一次提问一样，第七个第八个pattern会出现最下边跟前几个pattern的最下边不在同一水平线上的问题，请问第七个第八个pattern该如何修改？」

→ 选 [4] 作 A 档任务说明的依据（提出需求、未给根因/修复）；本 case 取 B 档 synthesized（把 pcell pattern 结构提取成 manifest，交付一个可对任意 manifest 跑的几何诊断脚本）。

## assistant 的真实分析（ground truth）
默认设置（所有 boolean=nil）走 `else;check max` → `layer1==layer2` 子分支（L576 起），8 个 pattern 顺序及 basex 增量：

| # | pattern | basex_inc | x 范围 | basey 赋值 | 底边 y |
|:-:|:--|:--|:--|:--|:--|
| 1 | parallel_paths | `space` | `basex`~`basex+layer1width` | `2*space` | `2*space` ✅ |
| 2 | parallel_offset | `layer1width+layer2width+step` | `basex`~`basex+layer1width` | `basey` | `2*space` ✅ |
| 3 | neg_prl | `1.5*layer1width+layer2width+step` | `basex`~`basex+layer1width` | `basey` | `2*space` ✅ |
| 4 | **singular** | `1.5*layer1width+layer2width+step` | `basex`~`basex+layer1width+layer2width` | `basey` | `2*space` ✅ |
| 5 | **ring** | `layer1length+layer2length+2*step` | `basex-(space-grid)/2`~`basex+(space-grid)/2+layer1width` | `2*space` | `2*space` ✅ |
| 6 | **notch** | `1.5*layer1width+layer2width+step` | `basex`~`basex+3.5*layer1width` | `basey+0.5*layer1width` | `2*space` ✅(path 居中) |
| 7 | **polygon** | `1.5*layer1width+layer2width+step` | `basex`~`basex+2*layer1width+2*space` | `basey` | `2*space+0.5*layer1width` ❌ |
| 8 | **ring2** | `offset5+offset6+3*layer1width+2*layer2width+2*step` | `basex-(space+grid+layer2width)`~`basex+layer1width` | `basey+space` | `2*space+0.5*layer1width+grid-layer2width` ❌ |

（`step=3*space`；`offset5`=pattern5 增量，`offset6`=pattern6 增量）

**重叠根因**：
- 4→5 (singular→ring)：ring 增量 `layer1length+layer2length+2*step` 在 space 小、length 小、width 大时 < `layer1width+layer2width+(space-grid)/2` → ring 左边界落到 singular 右边界左侧。
- 6→7 (notch→polygon)：notch 最右 `basex+3.5*layer1width`，polygon 增量 `1.5*layer1width+layer2width+step` 在 layer2width/space 小、layer1width 大时 < `3.5*layer1width` → polygon 左边界落到 notch 右边界左侧。

**底边不对齐根因**：notch (L610) `basey=basey+0.5*layer1width` 永久抬高 basey；notch 自身 path 居中底边仍为 `2*space`，但后续 polygon (`basey=basey`)、ring2 (`basey=basey+space`) 继承偏移，底边偏离 `2*space`。

**修复（assistant 给出）**：
- pattern5 ring basex：增量加 `+layer1width+layer2width`
- pattern7 polygon basex：`1.5*layer1width`→`3.5*layer1width`；basey：`basey`→`basey-0.5*layer1width`
- pattern8 ring2 basey：`basey+space`→`basey+space+layer2width-grid`

## case 设计（EDA-Eval-DesignFlow-PcellPatternGeoDiag-001, layout_aether, B-synthesized, L1-boundary）
- 把 pcell pattern 结构提取成 manifest JSON（参数 + 每个 pattern 的 basex_inc/x_left/x_right/basey_set/bottom_y 公式）。SUT 写 `pcell_pattern_diag.py`：模拟 basex 累加 + basey 顺序赋值，算出每 pattern 坐标，检测 x 重叠 + 底边 y 不对齐，给修复，输出 JSON 报告。
- **A_run** = 真实 trace grounded（oneOrTwoLayerSpaceFail 默认设置 8 pattern，极端参数 space=0.001/layer1width=0.5/length=0.001 触发重叠 4→5、6→7 + 不对齐 7、8；自验 overlaps=[(4,5,0.5675),(6,7,0.897)], misalign=[(7,0.25),(8,0.2)]，与 assistant 分析一致）。
- **隐藏 B** = 结构不同（5 pattern, cell minSpaceCheck_qa, 不同公式/参数）→ overlaps [(2,3),(3,4),(4,5)], misalign [4,5]，击穿 A 硬编码。
- **B2 clean guard** = 4 pattern 大增量无 basey bump → 0 overlap / 0 misalign，杀 always-detect。
- **B3 heavy guard** = 5 pattern 微小增量 → 4 overlap + misalign {4,5}，杀 always-clean/always-FAIL。
- **k=15 a-o**：结构键 / pattern 数 / 数值字段 / basex 序列 / x_right 序列 / bottom_y 序列 / 重叠对集合 / 重叠量 / 不对齐 id 集 / 不对齐 delta / 重叠修复足量 / 不对齐修复修正 / B2 全清 / B3 重叠数+misalign 集 / 3-seed sha256 确定性。
- 自验本机 Python 3.12：golden submit.zip → check.py CHECK PASS True（15/15）；5 negative（empty_shell/print_expected/core_deleted/naive_hardcode_a/stub_no_compute）全 FAIL（ALL_NEG_FAIL=True）；3-seed sha256 STABLE。

## 选料链
r225 筛选轮 DEBT:1 → r226 降 mc 到 15、layout-affinity 打分。先试 mwxi calibre405 系列（6bs3u/7vfvg/i96df）全为 ops（runset 文件同步/VM 重启，非 physical_verify design），parked；4ckeg (e0014566, 433 virtuoso) 实为「解释 autovia/powerfill 工具」无交付物，parked；ly1qu (yzwang, 304 dbCreateRect/68 dbCreatePath/15 calibre) 真实 pcell DRC-QA pattern 几何修复 → seed。
