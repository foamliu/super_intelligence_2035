# r1141 — trace 1795424182447_3pyum → ResCharPlotSummaryProduce-001

**Shard**: B (spice_sim/characterization)
**Round**: r1141 (2026-11-24)
**Trace**: `1795424182447_3pyum` — lvyy @ hfeg0pkn005, mc=46
**Case ID**: `EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001`
**Difficulty**: L1 (pure Python stdlib + matplotlib, no EDA tool runtime)
**k (assertions)**: 12

## 1. Trace 溯源

- **User**: lvyy (原始用户名，未脱敏)
- **Host**: hfeg0pkn005
- **Session file**: `1795424182447_3pyum` (366 msgs, 16 user turns)
- **Scan**: 20261124_023802 (fresh candidates batch)
- **match_count**: 46

### 真实任务摘要

lvyy 在 hfeg0pkn005 上跑多种电阻 (rhrp/rndif/rnmg/rnwaa/rnwsti/rpdif) 在 5 个 PVT corner (FF/TT/SS/SF/FS) 下的 FineSim 温度扫描，产出 `manyRes/<res>_res/<res>_res{,#1-#4}.pd0` parametric data (4 列: temp/vstep/imeas/rvalue, 温度 -40/0/25/45/85/130)。

- **U#0**: "跑了不同电阻的结果...给我生成图片" → 要求画 R-vs-temp 图
- **U#4/U#5**: follow-up "总结表格里要有不同电阻随温度和 corner 变化的百分比比例"，指定 -40/45/130 三个温度点
- assistant 写 `gen_plots.py` (每 resistor R-vs-temp 图 + 每 corner 对比图) 和 `gen_summary.py` (summary_corner.csv: R@25C per corner + %delta vs TT + spread; summary_temperature.csv: R@-40/45/130 + %delta vs R@25)

本 case 取 res-char 子任务 (produce loop)。CV 子任务 (U#7+) 需跑 FineSim 为 L2+，超单轮范围。

## 2. Case 设计

### 契约
- mode: design_flow
- entry_point: outputs/submit.zip
- 脚本签名: `python3 res_char.py <manyRes_input_dir> <output_dir>`
- 输出: plots/<res>_R_vs_temp.png + plots/compare_corner_<C>.png + tables/summary_corner.csv + tables/summary_temperature.csv + manifest.json

### A/B 数据集差异 (§4.1)
| 维度 | A (SUT 可见) | B (隐藏) |
|---|---|---|
| resistor 数 | 6 (rhrp/rndif/rnmg/rnwaa/rnwsti/rpdif) | 5 (rnhv/rnpoly/rpdifsab/rpmg/rppoly) |
| 阻值量级 | ~950-3100 Ω | ~1200-4400 Ω |
| 温度网格 | 6 点 (-40/0/25/45/85/130) | 7 点 (-40/-10/25/45/90/130/150) |

### 12 条 check() 断言
1. submit.zip 可解析 + 含 .py 脚本
2. 候选脚本在隐藏 B 上 exit 0
3. 每 resistor 的 R_vs_temp.png 存在 + 合法 PNG + >2KB
4. 5 个 corner 的 compare_corner_*.png 全存在 + 合法
5. summary_corner.csv 表头完整 + 行数==resistor 数
6. R25_TT 及各 corner R25 与独立重算匹配 (exact grid pt)
7. del_FF/SS/SF/FS_pct 与重算匹配
8. spread_pct = max-min(5 delta) 匹配
9. summary_temperature.csv 表头完整 + 行数==resistor×corner
10. R@-40/45/130 与重算匹配 (exact grid pt)
11. del_-40/45/130_pct 与重算匹配
12. manifest.json 可解析 + files 列表长度 ≥ resistor+corner+2

## 3. 验证

### .75 沙盒端到端验证 (solution.py)
- solution.py 上传到 .75 session workdir，用 verify_solution.py 生成合成数据集跑通
- EXIT 0，所有 PNG 合法 (44-115KB，远超 2KB 阈值)
- R25_TT 精确匹配 (1000.0000 / 2000.0000)
- summary_temperature.csv 行数 = 2×5 = 10 ✓
- manifest.json 9 files ✓

### 本地 self-test (stub)
- check.py 用 /tmp/res_char_stub.py (无 matplotlib，PNG 用 stub，CSV/数值逻辑与 solution.py 完全一致) 自测: 12/12 PASS
- 3 个 negative (empty/print_only/core_deleted) 全部 FAIL (exit 1)
- negative_selftest.py 路径 bug 已修 (REF_DIR → HERE)

### 三假提交回归 (§4.9)
- empty.py: 无输出 → (3) missing plot FAIL
- print_only.py: 硬编码 A 值 (rnhv 单行) → (5) rows≠resistors FAIL
- core_deleted.py: 空 header stub → (5) missing columns FAIL

## 4. 交付物

- `cases/B/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001.json` — case JSON
- `assets/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001/manyRes/` — A 数据集 (30 .pd0)
- `assets/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001/hidden/manyRes/` — B 数据集 (25 .pd0)
- `reference/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001/solution.py` — 参考解
- `reference/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001/check.py` — 12 条断言
- `reference/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001/negative/{empty,print_only,core_deleted}.py` — 3 假
- `reference/EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001/negative_selftest.py` — 回归 harness

## 5. 台账

- 3pyum: claimed → case (EDA-Eval-DesignFlow-ResCharPlotSummaryProduce-001)
- B covered: 596 → 597
