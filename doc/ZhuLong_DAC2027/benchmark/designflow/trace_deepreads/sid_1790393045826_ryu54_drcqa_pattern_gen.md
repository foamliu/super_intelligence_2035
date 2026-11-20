# Deep-read: sid_1790393045826_ryu54 (kenwang / hfeg0pkn005, mc=273, domain=layout_aether)

- **trace_source**: user=kenwang, host=hfeg0pkn005, session_file=1790393045826_ryu54.messages.json, match_count=273, real_task_summary=生成 DRC QA pattern SKILL 脚本（AA_W_1 WIDTH 规则 + M1_S_1 SPACE 规则 + 双重图形 mask color + auto_pattern_width.md 文档）
- **size**: 2,307,558 bytes / 641 msgs / agent=lead → **qualifies for deepread-only exception (>2MB AND >600msgs)**
- **tool_use counts**: editor=162, read_files=136, search_codebase=7, RAG_search_apis=2, RAG_get_api_details=2, list_allowed_files=7, run_commands=2, run_approved_command=1, ask_question=1
- **files written (gold)**: `/home/kenwang/.cline/scripts/data/{AA_W_1.il, M1_S_1.il, run_M1_S1.il, auto_pattern_width.md}`

## User intent (7 UI turns, verbatim)

- UI#0 (msg0, context summary): 文件可能受损了。我先读取当前状态，然后根据结果决定如何继续。
- UI#1 (msg31): 「1. 旋转45度的pattern覆盖的 bad marking layer 的形状随便修改为了 扇形，但是依然没有覆盖再 AA pattern上面，2 . "口"字形状的 pattern 没有产生；」= **A-档 seed ✓**（提出两个缺陷未给根因）
- UI#2 (msg82): 「请重新产生一下 AA_W_1.il 文档，误操作把他删掉了」
- UI#3 (msg186): 「现在从效果来看，W_1 产生的pattern基本合格，现在我们开始创建 space 的pattern，可以学习的pattern当然依然可以创建 M1_S_1 的pattern 绘制类型」
- UI#4 (msg274): 「现在就创建，可以在 skill IDE 加载进去即可创建出cell，可以看到他们的layout 结构」
- UI#5 (msg287): 「*Error* dbCreateRect: Invalid layer/purpose - ("M1" "drawingA") 创建 M1.drawingA layer 在 techfile 文件中并没有该layer，需要通过 ("M1" "drawing") layer 创建，如果是需要添加颜色，需要通过命令 shapeColor 命令 然后通过 colorLock 命令」= **用户指出根因 + 给出修复方案 → 不可作 A-档任务说明（可作 hint）**
- UI#6 (msg601): 「把以上的对话整理成一个 auto_pattern_width.md」

## Workflow & gold

### 1. AA_W_1.il — AA layer WIDTH rule DRC QA pattern
- **规则**: AA 最小宽度 WIDTH（GOOD = value+grid 通过 / BAD = value-grid 失败 + DRC_BAD mark）
- **11 种 pattern 类型 (A–K)**: 矩形(rect)、多边形(polygon)、旋转45°菱形(rotated diamond)、"口"字环(ring) 等
- **辅助过程 (7)**:
  - `drqaCreateRectWidth` — dbCreateRect + 打属性
  - `drqaAddMarkBox` — 矩形 DRC_BAD mark
  - `drqaAddMarkPolygon` — 多边形 DRC_BAD mark (dbCreatePolygon)
  - `drqaCreatePolygonWidth` — dbCreatePolygon + 打属性
  - `drqaCreateRotatedWidth` — 旋转45°菱形（旋转公式）
  - `drqaRotatedVertices` — 返回菱形精确4顶点（与 drqaCreateRotatedWidth 同公式，确保 mark 与 AA 菱形重合）
  - `drqaCreateRingWidth` — "口"字环 via `dbLayerAndNot`（外矩形 ANDNOT 内矩形 = 真环，**非**自交多边形——dbCreatePolygon 不允许自交）
- **GOOD cell**: 全部类型用 value+grid（通过 DRC）
- **BAD cell**: 全部类型用 value-grid + DRC_BAD mark（菱形 mark 用 drqaRotatedVertices 精确覆盖；环用 drqaCreateRingWidth）
- **主过程**: `drqaRun_AA_W_1()` — 打开/创建 cell，循环 11 类型生成 GOOD+BAD，dbSave

### 2. M1_S_1.il — M1 layer SPACE rule DRC QA pattern
- **规则**: M1.S.1 — M1 最小间距 ≥ 0.014um（GOOD gap=0.0141 / BAD gap=0.0139）
- **核心逻辑**: 两矩形之间有 gap
- **双重图形 (Multiple Patterning)**:
  - **初版（错误）**: 左矩形画在 `lppA=list("M1" "drawingA")` GDS 88:651，右矩形画在 `lppB=list("M1" "drawingB")` GDS 88:652
  - **错误**: `*Error* dbCreateRect: Invalid layer/purpose - ("M1" "drawingA")` — techfile 无 drawingA/drawingB
  - **修复（UI#5 用户指示）**: 全部画在 `list("M1" "drawing")`，通过 `dbSetShapeColor(shape, mask1Color/mask2Color)` + `colorLock` 区分两侧 mask
  - 新增 `drqaSetMaskColor(shape, maskNum)` 辅助函数
- **辅助过程 (9)**: 上述 7 个 + `drqaCreateRectSpace`（两矩形 + gap）+ `drqaCreateRotatedSpace`（旋转 SPACE）
- **GOOD/BAD cell**: 11 种 SPACE 类型，GOOD gap=0.0141，BAD gap=0.0139 + DRC_BAD mark
- **主过程**: `drqaRun_M1_S_1()`
- **run_M1_S1.il**: 一键运行脚本（load drqa_util + M1_S_1 + 调用主过程）

### 3. auto_pattern_width.md — 对话整理文档（~330 行，11KB，9 节 + 2 附录）
1. 项目背景 2. 文件清单 3. AA_W_1 Width Pattern 4. M1_S_1 Space Pattern 5. 双重图形 mask color 方案 6. 辅助过程清单 7. GOOD/BAD 设计 8. 错误与修复 9. TODO + 附录

## 关键 API / 错误（断言素材）

- `dbCreateRect` / `dbCreatePolygon` / `dbLayerAndNot`（环）/ `dbSetShapeColor` + `colorLock`（mask）/ `dbSave`
- **错误 1**: `*Error* dbCreateRect: Invalid layer/purpose - ("M1" "drawingA")` — techfile 无 drawingA，根因=用了不存在的 layer/purpose；修复=改用 ("M1" "drawing") + dbSetShapeColor mask1Color/mask2Color + colorLock
- **错误 2**: 旋转45°菱形 mark 硬编码顶点偏离 → drqaRotatedVertices 用与 drqaCreateRotatedWidth 同公式重算4顶点
- **错误 3**: "口"字环用 dbCreatePolygon 自交多边形不产生环 → drqaCreateRingWidth 用 dbLayerAndNot(外 ANDNOT 内)
- **文件腐败问题**: editor 增量编辑多次留下乱码残留，反复重建（162 editor calls 主因）

## A-档可行性判定

- gold (AA_W_1.il / M1_S_1.il / auto_pattern_width.md) 依赖 **live Aether SKILL IDE + techfile + 私有库** → **A-disqualified**（无法在 SUT 沙箱内独立复现真跑）
- → **B-档 synthesized L1-boundary**：合成离线审计任务（纯 Python 标准库解析 manifest），断言 pattern-gen 脚本结构 / 辅助过程 / GOOD-BAD 设计 / 双重图形 mask color 修复 / dbCreateRect layer/purpose 错误根因 / dbLayerAndNot 环 / drqaRotatedVertices 顶点 / 11 类型 / 文档结构

## 与既有 layout_aether case 区别

| 既有 case | 主题 |
|---|---|
| LabelApiPolDiag (r69) | label add/save/delete API + policy guard + policy change |
| APRRoutePrecondDiag (r68) | APR 路由前置条件 |
| NetDelSaveAudit (r67) | net delete + save |
| SchPinPlanAudit (r66) | sch pin plan |
| CTLESchGenAudit (r65) | CTLE sch gen |
| PinFloatAether-001 | pin float (bottom→top) |
| LayoutAether-001 (rebuilt) | LVS netlist compare |
| **本案 (ryu54)** | **DRC QA pattern generation（WIDTH/SPACE 规则、GOOD/BAD 11 类型、旋转菱形、dbLayerAndNot 环、双重图形 mask color）— 主题独立** |

## 下一轮合成计划（DEBT: 1）

- task_id 候选: `EDA-Eval-DesignFlow-DRCPatGenAudit-001`（layout_aether, B-档 synthesized, L1-boundary）
- 候选脚本: `drcqa_pattern_audit.py`（stdlib json/re/sys）：解析 manifest（pattern_gen 脚本结构）→ 审计 ①辅助过程齐全（drqaCreateRectWidth/drqaRotatedVertices/drqaCreateRingWidth/drqaSetMaskColor 等）②11 类型 A-K ③GOOD=value+grid / BAD=value-grid+mark ④旋转菱形顶点公式 ⑤"口"环=dbLayerAndNot(非自交多边形) ⑥M1 双重图形修复：drawingA→drawing+dbSetShapeColor mask1Color/mask2Color+colorLock ⑦dbCreateRect Invalid layer/purpose 错误根因+修复 ⑧主过程 drqaRun_AA_W_1/drqaRun_M1_S_1 ⑨run_M1_S1.il 一键脚本 ⑩auto_pattern_width.md 9节结构 ⑪cross-input hidden B（不同规则/层/类型数）⑫确定性 ⑬结构 API 名真实 ⑭verdict → stage
- check.py 目标 k=14 条断言（①-⑭），k_check≥8 GATE PASS
- A=AA_W_1 manifest（WIDTH, AA 层, 11 类型, 旋转菱形+环）；hidden B=M1_S_1 manifest（SPACE, M1 层, 9 类型, 双重图形 mask color）；B2/B3 变体杀硬编码
