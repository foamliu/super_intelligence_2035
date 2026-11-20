# 深读笔记：cgqd1 — RTEXT/RNODE 标签审计 + 清理（layout_virtuoso 域）

**trace 来源**：e0014566 / hfeg0pkn001 (10.129.2.10) / session `1786541065533_cgqd1`
**规模**：1.75MB messages.json / 481 msgs (253 user / 228 assistant) / 250 tool_use (168 run_commands + 50 SKILL run_code + 21 editor + 8 read_files + 3 search_codebase)
**match_count**：772；keywords virtuoso:2058 / analog:837 / cellview:323 / .gds:135 / dbcreatelabel:122 / dbopencellviewbytype:101 / dbcreaterect:55
**真实任务**（user msg0 原文）：
> 请你帮忙看下 Library: auto_austin_case1, Cell: Array16G_B, View: layout, 这个版图。我现在要用 rscalc 计算电阻，看看其 powernet 上的 RTEXT，以及 RNODE 有没有打齐，没有的话，帮忙打上。打 RTEXT RNODE 方式见：test_layout_rscalc_flow_6

**用户后续**：msg459 确认 "RTEXT RNODE 打好了，是不是？"；msg461 "你做的对，而且很好。能不能总结出一个打 RTEXT RNODE 的切实有效的方法，让别的地方可以复用。"

---

## 一、领域知识（RTEXT / RNODE / rscalc 约定）

针对配置 `cxmt10G4plus` + `1p5m1x3y1z`：

- **RTEXT**（电源 pad / 源点）：图层 purpose = `RTEXT`（如 `("M1" "RTEXT")`）。label 文字 = 网络名（**不带 `!`**，如 `vdd`）。rscalc 从每个 RNODE 检查点测量到 RTEXT 电源 pad 的电阻。
- **RNODE**（检查点）：图层 purpose = `RNODE`（如 `("M1" "RNODE")`）。label 文字 = 网络名（不带 `!`）。
- **TEXT**（GDS 网络名）：图层 purpose = `drawing`，label 文字带 `!`（如 `vdd!`）。
- **可打 RTEXT/RNODE 的图层**（NetLayers/PointLayers）：`MT2, M0U, M1, M2, M3, M4, M5, RDL`
- **参考 flow_6 打 label 方式**（`gen_test_layout.py`）：
  - RTEXT: `dbCreateLabel(cv list("M1" "RTEXT") list(x y) "vdd" "centerLeft" "R90" "roman" 1.0)` — 放在 rail 起点和中间（电源 pad 位置）
  - RNODE: `dbCreateLabel(cv list("M1" "RNODE") list(x y) "vdd" "centerLeft" "R90" "roman" 0.8)` — 放在 rail 沿线检查点
  - TEXT: `dbCreateLabel(cv list("M1" "drawing") list(x y) "vdd!" ...)` — 带 `!` 的 GDS 网络名
- **"打齐" 判定**：每个真实电源网络在所用图层上 RTEXT>0 **且** RNODE>0（缺一不可：RTEXT=电源源点，RNODE=检查点，rscalc 算 RNODE→RTEXT 的电阻）。

---

## 二、agent 完整流程（可判分的 layout 域核心，msg 0–34）

### Phase A：打开版图 + 全量 label 扫描（msg18–22）
- `dbOpenCellViewByType("auto_austin_case1" "Array16G_B" "layout" "maskLayout" "r")`
- BBox: `((-17884.13 -14767.0) (17884.13 100.524))`；16449 rect / 74 label / 37 instance
- 遍历 `cv~>shapes`，对 `objType=="label"` 取 `s~>lpp`（layer+purpose）、`s~>theLabel`、`s~>xy`
- 按 purpose 分类：`RTEXT` / `RNODE` / `drawing`（drawing = 带 `!` 的 GDS 网络名，如 `vblh!`）

### Phase B：聚焦 RTEXT/RNODE 审计（msg22–24）—— **核心可判分数据**
按网络名（theLabel）分组统计 RTEXT/RNODE 数量 + 所在图层：

| 网络 | RTEXT 数 | RTEXT 图层 | RNODE 数 | RNODE 图层 | 状态 |
|------|---------|-----------|---------|-----------|------|
| vcc | 3 | RDL | 13 | RDL | 有重复 |
| vss | 3 | RDL | 13 | RDL | 有重复 |
| viso | 3 | RDL | 11 | RDL | 有重复 |
| test2 | 2 | RDL | **0** | — | ❌ 垃圾（RTEXT 有 RNODE 无） |
| edit_test | 1 | RDL | **0** | — | ❌ 垃圾（RTEXT 有 RNODE 无） |

**发现 3 类问题**：
1. **垃圾 label**：`test2`（2 RTEXT, 0 RNODE, 坐标 (0,0)/(10,10)）和 `edit_test`（1 RTEXT, 0 RNODE, 坐标 (100,100)）位于调试坐标，不是真实电源网络，会污染 rscalc 自动检测
2. **重复 label**：vcc/vss/viso 的 RTEXT/RNODE 在相同坐标有重复（如 vcc 在 (17501.03,-1351.52) 有 2 个 RTEXT）
3. **只在 RDL 层**：参考 flow_6 应在 M1-M5 各金属层都打，当前仅 RDL（但 agent 分析后认为 M1-M5 drawing 金属在 array 子单元内部，rail 处只有 pin purpose，贸然加 M1-M5 会让 rscalc 找不到对应 drawing 金属 → 决定只在 RDL 上打齐）

### Phase C：清理（msg30）—— **删除垃圾 + 去重**
- `dbOpenCellViewByType(... "a")`（append 模式）
- 遍历 shapes，对 purpose==RTEXT/RNODE 的 label：
  - theLabel=="test2" || "edit_test" → 标记删除（垃圾）
  - 其余按 key=`(lpp, theLabel, xy)` 去重，重复的标记删除
- `dbDeleteObject(s)` 删除标记的 label
- `dbSave(cv)` 保存
- **结果**：删除 3 个垃圾 + 9 个重复 = **12 个 label**（RTEXT 12→6，RNODE 37→31）

### Phase D：验证清理后"打齐"状态（msg32–34）—— **核心可判分数据**
清理后统计：

| 网络 | RTEXT | RNODE | 状态 |
|------|-------|-------|------|
| vcc | 2 (x=±17581) | 11 | ✓ 打齐 |
| vss | 2 (x=±17664) | 11 | ✓ 打齐 |
| viso | 2 (x=±15870) | 9 | ✓ 打齐 |

三个真实电源网络在 RDL 上 RTEXT+RNODE 完整匹配，垃圾/重复已清除。

---

## 三、rscalc 批处理环境调试（msg 36–198，**不通用，不入 case**）

agent 随后运行 rscalc 批处理（GDS stream-out → label 提取 → LSF bsub 提交），经历 9 轮（v1–v9）cds.lib/layerMap 调试：
- v1: 缺库 `drjqa_array`（AI_Virtuoso cds.lib 只有 `drjpa_array` p≠q）→ 加 V0_Austin cds.lib
- v2: layerMap 空（`leGlobalVariables->layerMap` 未设）→ agent 脚本显式设 layerMap
- v3–v5: V0_Austin 完整库集 .cdsinit 在 -nograph 下崩溃 → 改混合 AI_Virtuoso tech + drjqa_* 库
- v6–v7: 多个 drjqa_* 库 + 3 个不存在的库目录 → 移除不存在路径
- v8: zlib/stdcells_ac cell 缺失 → 覆盖为 V0_Austin 版本
- v9: 完全显式 cds.lib（17 库，无 INCLUDE 冲突）

**这部分依赖具体库路径/tech 环境，不可在沙盒复现，不入 case。** case 只取 Phase A–D 的 label 审计+清理逻辑。

---

## 四、下轮 case 设计（第125轮合成 EDA-Eval-DesignFlow-LayoutVirtuoso-001）

**概念**：offline-Python RTEXT/RNODE 标签审计 + 清理工具。输入 = label inventory 文本（SKILL 扫描 dump），工具审计 rscalc 所需的 RTEXT/RNODE 完整性，产出清理报告。

**4 个 assets**：
1. `label_inventory_unclean.txt`：清理前 label dump（含 vblh! drawing labels + RTEXT/RNODE 含 test2/edit_test 垃圾 + 重复）。格式每行 `(layer "purpose")  "net"  xy=(x y)`
2. `label_inventory_clean.txt`：清理后 label dump（仅 vcc/vss/viso，去重去垃圾，全打齐）
3. `rscalc_conventions.md`：RTEXT=电源源点/RNODE=检查点/打齐判定/支持图层/label 文字不带 `!`/rscalc 算 RNODE→RTEXT 电阻
4. `task_brief.md`：CLI 接口（`--inventory <file>`）+ 输出格式（per-net: net/RTEXT 数/RNODE 数/layers/verdict + garbage_nets + duplicate_count + delete_list）+ 约束纯标准库

**proper 契约**：mode=design_flow / entry=outputs/submit.zip / 4 artifacts / Python 双参 `check(deliverable, workdir)` / 无 lang·host

**reference**：`rtext_rnode_audit.py`（纯标准库）解析 label inventory → 按 net 分组 → 按 purpose(RTEXT/RNODE) 计数 → 标记 garbage(RTEXT>0 & RNODE==0) + duplicates(同 lpp+text+xy) → 产出 cleanup_report + verdict

**test 7 条件（独立有牙）**：
- a) 解 zip 校验 4 文件齐全
- b) rtext_rnode_audit.py 语法合法
- c) 实跑 `--inventory label_inventory_unclean.txt` 退出码 0 + 识别 test2+edit_test 为 garbage(RTEXT>0 RNODE=0) + 报告 vcc/vss/viso 为真实网络（naive 只数总 label 数不分 net/purpose → FAIL c）
- d) 识别重复 label 计数正确（RTEXT 重复 + RNODE 重复；naive 不去重 → FAIL d）
- e) per-net verdict：test2/edit_test=MISSING/GARBAGE，vcc/vss/viso=（含重复标记）；naive 只看 RTEXT>0 不查 RNODE==0 → garbage 误报 OK → FAIL e
- f) 实跑 `--inventory label_inventory_clean.txt` → 3 网全 OK(RTEXT>0 AND RNODE>0) + 0 garbage + 0 dup
- g) cleanup_report 枚举 per-net(net/RTEXT 数/RNODE 数/layers/verdict) + delete_list(junk+dups 带 xy)

**ref 自验**：unclean=识别 2 garbage(test2/edit_test) + dups + 3 real nets；clean=3 OK 0 garbage 0 dup
**naive 验牙**：device-counter 风格（只总数不分 net）→ FAIL c；不查 RNODE==0 → FAIL e

---

## 五、关键原始数据（用于合成 assets）

### 清理前 RTEXT（12 个，含垃圾+重复）：
```
(RDL "RTEXT")  "edit_test"  xy=(100.0 100.0)      ← 垃圾
(RDL "RTEXT")  "viso"       xy=(15818.61 -1351.52) ← 重复
(RDL "RTEXT")  "vss"        xy=(17664.2 -1351.52)  ← 重复
(RDL "RTEXT")  "viso"       xy=(15818.61 -1351.52) ← 重复(删)
(RDL "RTEXT")  "vss"        xy=(17664.2 -1351.52)  ← 重复(删)
(RDL "RTEXT")  "viso"       xy=(-15869.87 -1351.52)
(RDL "RTEXT")  "vcc"        xy=(17501.03 -1351.52) ← 重复
(RDL "RTEXT")  "vcc"        xy=(17501.03 -1351.52) ← 重复(删)
(RDL "RTEXT")  "test2"      xy=(0.0 0.0)           ← 垃圾
(RDL "RTEXT")  "vcc"        xy=(-17581.43 -1351.52)
(RDL "RTEXT")  "vss"        xy=(-17664.23 -1351.52)
(RDL "RTEXT")  "test2"      xy=(10.0 10.0)         ← 垃圾
```

### 清理前 RNODE（37 个，含重复）—— 部分样例：
```
(RDL "RNODE")  "vcc"  xy=(1060.491 -1351.52)
(RDL "RNODE")  "vcc"  xy=(8564.752 -1351.52)
... (13 个 vcc，含重复如 17501.03 出现 3 次)
(RDL "RNODE")  "vss"  xy=(7794.968 -1351.52)
... (13 个 vss，含重复如 17664.2 出现 3 次)
(RDL "RNODE")  "viso"  xy=(15406.69 -1351.52)
... (11 个 viso，含重复如 15818.61 出现 3 次)
```
注意：test2/edit_test 的 RNODE = 0（无任何 RNODE）

### 清理后 RTEXT（6 个，全打齐）：
```
(RDL "RTEXT")  "viso"  xy=(15818.61 -1351.52)
(RDL "RTEXT")  "vss"   xy=(17664.2 -1351.52)
(RDL "RTEXT")  "viso"  xy=(-15869.87 -1351.52)
(RDL "RTEXT")  "vcc"   xy=(17501.03 -1351.52)
(RDL "RTEXT")  "vcc"   xy=(-17581.43 -1351.52)
(RDL "RTEXT")  "vss"   xy=(-17664.23 -1351.52)
```

### 清理后 RNODE（31 个，去重）：vcc=11, vss=11, viso=9

### drawing-purpose labels（带 `!`，74 个里的 ~24 个）：
```
("text" "drawing")  "vblh!"  xy=(-15292.03 -1380.34)
... (24 个 vblh! 沿 y≈-1380 分布)
```
这些是 GDS 网络名标签，**不是** RTEXT/RNODE，审计工具须忽略（按 purpose=="drawing" 排除）。
