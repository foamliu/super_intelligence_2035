# r605 deepread — haoq @ hfeg0plg106, session 1793174783533_791f6

- **user**: haoq (10.129.8.238 / hfeg0plg106)
- **session**: 1793174783533_791f6.messages.json (1.14 MB, 346 msgs, agent=lead)
- **match_count**: 337 (drc:1461 / calibre:1005 / .gds:179 / gdsii:101 / cmos:70 / cadence:18 / pyaether:6)
- **domain**: physical_verify (Calibre DRC deck + GDS area computation)
- **旧 ledger 判定**: parked "status=failed exit1; user wanted calibre DRC deck computing GDS layer 302:7" (r42) — 旧规则以 trace status=failed 为由 parked
- **新判定 (2026-11-15 令)**: 可造。trace status=failed 非排除标准（真实用户意图仍在；失败 trace 是真实场景）；用户意图清晰 produce-task，agent 产出了真实可判分的算法（GDS 解析 + shoelace 面积）。

## 用户意图演进（21 user_input）

- **UI#0（核心 produce-task，提需求未给方案）**：「我想计算V1平台某个GDS中的层次占用的面积，能帮我做个在 calibre DRC 里面能够跑的deck，跑出的结果为这层的面积吗，gds层次是302：76」
  - = 写一个 Calibre DRC deck，跑出 GDS layer 302:76 的总面积
- UI#34: 报 SVRF 语法错 `Error INP1 on line 52 ... superfluous or invalid input object: L302_76`
- UI#42: 指定 GDS 路径 `/proj/ddgoa/V0/ver/drc/ddgoa_cmos_top/LP5TOP_qhtest/LP5TOP.gds`
- UI#146: 「你还是写成deck让我跑吧」（坚持 deck 形态）
- UI#150/160/161/169/175/179/187/195/197: 一连串 SVRF 语法/精度错（INP1/INP5/DCM4/precision mismatch/WAIVER_CRITERIA）
- **UI#216（关键）**：「Total Area of GDS Layer 302 DATATYPE 76 [µm²] 不显示面积」— deck 跑通但面积不显示
- UI#345: 「继续」

## agent 工具链与产物

1. **Calibre SVRF deck** `/home/haoq/measure_layer_302_76.drc`：迭代修复语法（PRECISION 10000 置于 LAYOUT PATH 前、LAYER MAP、DRC CHECK MAP、AREA 检查）。最终 deck 用 `AREA L302_76_flat > 0.000` 检查 + `@` 标题输出。
2. **Python GDS 面积脚本** `/home/haoq/calc_area_302_76.py`（UI#217 后 fallback）：raw GDSII 二进制解析（XY records）→ 提取 layer 302:76 的 boundary 多边形 → shoelace 面积 → 单位换算 → 报告。msg 340 输出 `boundaries_area_computed 0 / bad_xy_records 33 / AREA_302_76_db2 0`（坐标解析 bug，6375 多边形但面积算成 0）。
3. **dump_xy.py**（msg 341-344）：dump 原始 XY 字节确认 GDS 坐标格式。

## B 档 mock-behavioral reframe（承 r593-r604 script-task 模式）

- **源资产不可达**：`/proj/ddgoa/.../LP5TOP.gds` 在项目私有 NFS（沙盒不可达）→ asset_fidelity=synth。
- **reframe**：把「写 Calibre deck / Python 脚本计算 GDS 指定 layer:datatype 总面积（µm²）」参数化为纯 Python3 `gds_layer_area.py <gds_dump> <layer:datatype> <out_report.json>`。
- **输入格式**：简化的文本 GDS dump（保留 GDSII 结构：UNITS unit/uUnits、CELL、BND boundary{layer,datatype,xy in db units}、PATH/SREF distractor），忠实 agent 的 GDS 解析 + shoelace + dbunit→µm² 换算算法。
- **判分数据驱动**：check.py 自己解析 hidden B 的 dump 算 ground truth area，再断言脚本输出忠实反映 B（非硬编 A）。
- **隐藏 B**：换 layer:datatype（200:50）、不同 cells/polygons、含 datatype 51 distractor + layer 99 distractor + CCW 多边形（测 shoelace abs）。
- **隐藏 B2**：再换 layer:datatype（150:30）、含 A 的 layer 302:76 distractor（测反硬编 A）。
- **k≥8 断言**：zip+py_compile / B exit0+JSON / B polygon_count / B total_area_um2 容差 / B layer:datatype / B per_cell 求和 / dbunit 信息 / 反硬编 A / B2 反硬编 / 确定性 / 空层鲁棒 / CW/CCW abs / 多 cell 求和 / 非 BND 元素排除 / 非目标 layer 排除 = 14 条 a-n。

## 验收点对齐 trace

- 用户要「这层的面积」→ check 验 total_area_um2
- agent fallback Python 解析 GDS → reframe 为 Python 脚本（trace 真实产物）
- UI#216「不显示面积」→ 脚本必须输出数值（非空标题）
- agent `-flat` 推荐 → dump 预扁平化（所有 boundary 直接列出，跨 cell 求和）
