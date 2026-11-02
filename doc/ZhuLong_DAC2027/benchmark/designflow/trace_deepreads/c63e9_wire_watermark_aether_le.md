# 深读 c63e9 — Aether LE Wire Watermark (hongyuy)

- session: `1792393017757_c63e9` (hongyuy / hfeg0plg64, mc=233)
- file: `/home/hongyuy/.cline/data/sessions/1792393017757_c63e9/1792393017757_c63e9.messages.json` (1.0MB, 264 msgs, 4 user_input turns)
- tools: editor 47, RAG search_apis 49, run_approved_command 27, read_files 14, SandBox run_code 2, list_allowed_files 4
- domain: layout_aether (A-faithful 候选, NEW 用户 hongyuy)

## 用户原话轮

- **U[0]** (seed, A-档合规——纯需求、无根因、无修复): 逐字原文
  > 请帮我写一段 Aether LE 的 SKILL 脚本，实现以下功能：
  > ## 功能概述
  > 在版图编辑器中，给指定金属层的 wire 添加**斜线方向（45度角）的水印文字**，文字内容为该 wire 所属的 net name。
  > ## 详细规则
  > ### 1. 基础显示 — 每条 wire 以水印文字（45度倾斜）在 wire 内部显示其 net name；水印仅显示在当前编辑层次的 wire 上（不穿透层次）
  > ### 2. 自动继承 name（连接传播）— 新增 wire 无 net name 但通过端到端或 Via 与已有 net name 的 wire 相连，自动继承并显示该 name
  > ### 3. 短路检测与显示 — 新加 wire 短路两个不同 net name 的 wire → 显示 `name1 --short-- name2`
  > ### 4. 截断后 floating 处理 — 已有 net name 的 wire 被截断，floating 部分水印消失，仍相连部分保留原 name
  > ### 5. 层次化 name 显示 — 水印始终显示当前编辑层次的 net name（底层 L2=as1，顶层 L1=ast）
  > ### 6. 适用范围 — 可指定金属层（M1/M2/M3…），可扩展为所有层次统一处理
  > ## 实现要求 — SKILL 语言，兼容 Aether LE 脚本接口；回调/事件触发；45度斜角，wire 几何中心附近，密度适中不重叠

- U[239] "写好了吗" / U[241] "怎么使用" / U[243] "需要" — 后续状态/用法询问，非新需求（不影响 A-档 seed 资格）。

## assistant 工具链

- 先 `list_allowed_files` 发现 `/home/hongyuy/Desktop/` 已有 `wire_watermark.il` / `wire_watermark.py`（用户会话前的既有产物）→ `read_files` 读取既有 SKILL 版（`wireWatermarkMain` + `dbCreateLabel` + `R45/MXR90` orient + `pathSeg` 遍历）。
- `RAG search_apis` 49 次：查 `aeCreateText`/`emyShapeGetNetName`/`emyPointF`/`emyPathSegGetWidth`/`dbCreateLabel`/`deGetCellView`/`dbStartGenShape`/`weGetPathSegWidth` 等 Aether LE API。
- `editor` 47 次写多版本：
  - `wire_watermark_complete.py` (pyAether 版, 185 行, A[129] final 3632B) — `emyInitAether -adv` + `emyShapeGetNetName` 取 net + `emyPathSegGetWidth` 取宽 + 45° `aeCreateText` + `_short_label(net1,net2)` 短路串 + 沿中心线 `floor(length/spacing)` 重复 + 自动刷新 timer + cleanup。
  - `wire_watermark_enhanced.il` (SKILL 版, A[252] final 1766B) — `wireWatermarkMain` + `deGetCellView` + `dbStartGenShape` 遍历 pathSeg + `_wmGetNetName`/`_wmGetLayer`/`_wmGetLength`/`_wmGetPointAt` + `dbCreateLabel` orient `MXR90` + `wireWatermarkEnableAuto`/`Disable`/`Cleanup` + 别名 `wwm/wwa/wwd/wwc`。
  - `gen_skill_final.py` (Python 生成器, 141 行, A[258-260] final 4586B) — 因 editor 单次 new_text 6000 字符上限，改用 python-runner 把 SKILL 文件分段写出，A[263] tool_result: `Written 106 lines to wire_watermark_enhanced.il`，exitCode=0。
- `SandBox_MCP_Server__run_code` (pyAether @ 10.129.8.111:38894) A[81] 试 `import pyAether` → A[245] tool_result: **Connection refused by sandbox** — 沙盒不可达，脚本写完但**未能在线验证**。
- 会话末轮 A[263] 为生成器成功运行的 tool_result，无显式用户接受；U[241]"怎么使用"后 A[242] 给出完整用法指南（CIW load + wwm/wwa/wwd/wwc + pyAether 交互用法）。

## 真 L2 阻塞（同先例）

live Aether LE (`emyInitAether -adv` + `import pyAether` 2509sp1hf7) + OA 库 + techfile attach + `deGetCellView`/`dbCreateLabel`/`dbStartGenShape` 在 .75 sandbox 不可达：
- 本 session 沙盒 (`10.129.8.111:38894`) Connection refused，连 import 都失败。
- .75 sandbox 无 empyrean / 无 OA 库 / 无 PDK techfile。
→ L1-boundary 占位（同 PinFloatAether / ERCFlowAether / CTLEAether / DRCPatGen / M2PathLayout / AddCellPin 先例）。

## 金标来源（工具真实产物，人工复核）

assistant 写出的两个版本（本机 Desktop 已被清理，从 session messages 末次 editor write 重建）：
1. `wire_watermark_complete.py` (pyAether, 185 行) — 配置 TARGET_LAYERS=[M1..M6] / WATERMARK_LAYER="y0" / LABEL_HEIGHT_FACTOR=0.7 / LABEL_SPACING_FACTOR=2.5 / WATERMARK_ANGLE=45.0；helper `_get_net_name`(emyShapeGetNetName) / `_get_pathseg_geometry`(getPoints+emyPathSegGetWidth) / `_short_label(net1,net2)` → "n1 --short-- n2" / `_pathseg_length`(hypot) / 沿中心线 `floor(length/spacing)` 重复标签。
2. `gen_skill_final.py` → 生成的 `wire_watermark_enhanced.il` (106 行) — SKILL 版同构：`wireWatermarkMain` 遍历 pathSeg，按 layer 过滤，`dbCreateLabel` orient=`MXR90`（45°镜像旋转），`floor(quotient ln sp)` 个标签，位置 `_pt(ps, (i+0.5)/n)`（中心化），短路/floating/层次化逻辑同 pyAether 版。

人工复核 6 条规则对应实现：
- 规则1 基础45°显示 → `WATERMARK_ANGLE=45.0` / orient `MXR90` ✓
- 规则2 继承 name → `emyShapeGetNetName` 读 net（unnamed → None → 不显示，连接传播由 Aether net 推断；静态子任务需显式 connectivity）✓
- 规则3 短路串 → `_short_label(n1,n2)` = "n1 --short-- n2" ✓
- 规则4 floating → 无 net 不显示 ✓（静态子任务需显式 isolated 检测）
- 规则5 层次化 → `aeGetCurDesign()` 当前层 ✓（静态子任务用 `current_edit_level` + `net_by_level`）
- 规则6 层过滤 → `TARGET_LAYERS` member 判断 ✓
- 密度 → `label_height = max(width*0.7, 0.001)`，`spacing = label_height*2.5`，`n = max(1, floor(length/spacing))`，位置 `t=(i+0.5)/n` ✓

## 合成策略（L1-boundary, A-faithful）

verbatim U[0] 指向 live-draw SKILL/pyAether（L2 不可达），故合成 task_brief 围绕**确定性上游子任务 = wire watermark placement plan generator**：
- 输入：wire spec JSON（pathSeg 列表 {id, layer, p1, p2, width, net_by_level} + vias + config {target_layers, label_height_frac, label_spacing_frac, orientation, annotation_layer/purpose, current_edit_level}）
- 输出：结构化 manifest JSON（watermarks[per-wire: text/net/layer/orient/labels[]/label_count/inherited_from/short_with] + shorts[] + inherited[] + floating[] + skipped_layer[] + summary + config_echo）
- 算法（确定性，纯几何+拓扑）：
  1. 解析 net = net_by_level[current_edit_level]
  2. 连通分量：端点重合（同点）或 via 连接（via.at 落在两端点）→ 同一分量
  3. 分量内 ≥2 个不同非空 net → SHORT（按字典序排序 n1<n2，text="n1 --short-- n2"）；后出现且连到前者不同名 net 的 wire 显示短路串
  4. 分量内 unnamed wire + 单一 named → 继承该 net（inherited_from 记首个 named wire / via id）
  5. 孤立 wire（分量大小1，无端点重合、无 via）+ named → floating（不显示标签）
  6. layer 不在 target_layers → skipped（不显示）
  7. 命中 wire（target layer、非 floating、有 resolved net）→ 沿中心线 `label_height=label_height_frac*width`，`spacing=label_spacing_frac*label_height`，`n=max(1,floor(length/spacing))`，位置 `p1 + (i+0.5)/n * (p2-p1)`，orient = config.orientation
- track = faithful（U[0] verbatim 作 prompt）；layer=L1-boundary

## 资产规划

- A (visible) = `inputs/spec_A.json`（6 wires, 4 行为: 继承/短路/floating/层过滤, 端点重合连通, 无 via）+ `task_brief.md`
- B (hidden) = `hidden/spec_B.json`（8 wires, 2 vias [via 连通不同于 A 的端点重合], 不同 net/layer/数值, 继承2/短路1/floating1/skip1, current_edit_level="chip"）
- reference = `check.py`（17 条独立断言 a-q: zip 结构 / 6 顶层键 / summary 6 计数 / 继承 w2←w1 as1 / 短路 w3-w4 ast-vbx text / floating w5 / skip w6 M3 / R45 orient / 密度 w3 label_count==20 / config_echo annotation_layer+purpose / w4 短路串文本 / cross-input guard B 重跑 8 wires+gnd-vss 短路+via 继承 b8+skip b5 M1）+ `reference_submit.zip`（gold generator + manifest_A.json）
- negative = 4 假提交（empty_shell / only_print_expected / ref_deleted_core / naive_hardcode_A）+ negative_selftest.py 全 FAIL

（详见 EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/{assets,reference}/EDA-Eval-DesignFlow-WireWatermark-001/）
