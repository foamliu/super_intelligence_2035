# Trace Deepread — 1790576594987_e7fdl (kenwang @ hfeg0pkn004, mc=147)

- **Domain**: layout_virtuoso (SKILL / Virtuoso IC617, dbCreateRect/dbCreatePolygon/dbLayerAndNot, cellview, .il pattern generation)
- **NEW user**: kenwang (no prior ledger_C entry)
- **Tools count**: dbCreateRect:332, dbOpenCellViewByType:135, dbCreatePolygon:116, ddGetObj:61, cellview:23, virtuoso:9, drc:129; assistant tool_use: read_files:97, editor:69, run_commands:2 — heavy .il script editing
- **Session**: 364 msgs, 188 user turns; status: edited AA_W_1.il / M1_S_1.il / drqa_utils_v2.il

## Real task (用户原话选轮)

- msg#0 (root-cause, 不取 A-档): "访问 auto_pattern_width.md … M1_S_1.il run_M1_S1.il drqa_utils_vs.il 在 skill IDE 加载报 *Error* eval: unbound variable - cvGood，我们已经拥有创建 AA_W_1 pattern 的能力了，为什么还会犯同样的错误呢"
- msg#73 (goal, A-档候选): "请学习 autoPatternFamily/ 文档，它总结的是绘制不同类型 pattern 的原则和种类，学习之后更新在我们之前已经产生的 width，space 等 pattern 中"
- **msg#187 (clear spec, A-档候选)**: "good pattern 在结构上应该和 bad pattern 一样，但是它不应该报 DRC error，数值应该卡 value 和 value+grid 的"
- msg#337 (root-cause): "bad pattern 中 width 0.249 的 口 型 pattern 的 error marking layer 覆盖不够全面"
- msg#343-345 (goal): "请分析参考 space QA pattern 绘制方法，在 M1_S_1 中重新修改 rule … 口 形状 pattern 中心不需要填充"
- msg#350 (goal): "请根据参考文档学习并更新修改 M1_S_1.il，pattern 按照参考图形绘制"

## 关键产物 (真实附件, ground on disk)

`/home/kenwang/.cline/scripts/data/`:
- `auto_pattern_width.md` (10289B) — SKILL 开发记录: AA.W.1 width rule, grid 0.0001µm, value 0.025, w_pass=0.0251 (value+grid), w_fail=0.0249 (value−grid), 11 种 width 类型 A/B/C/H/J/K/L/U/O/F/G (catalog §5.1), mark layer DRC_BAD mark1 (GDS 9999:9999)
- `AA_W_1.il` (21848B) — 完整 SKILL 实现: drqaCreateRectWidth / drqaCreateRotatedWidth (45° 菱形, c=s=0.70710678, db=10000 round to grid) / drqaRotatedVertices / drqaCreateRingWidth (dbLayerAndNot 外矩形减内矩形, 8 顶点 frame) / drqaCreatePolygonWidth (L 6 顶点 / U 8 顶点) / drqaAddMarkBox / drqaAddMarkPolygon; good cell = PASS_HIGH(w_pass)+BOUNDARY(value); bad cell = FAIL_LOW(w_fail)+mark
- `Auto_pattern_AA.md` (10913B) — 项目背景, pipeline design_rule.xlsx → plan.json → SKILL → GDS, 35HDBC PDK, Virtuoso IC617, Calibre DRC, layout precision 10000
- `drqa_utils_v2.il` (7270B) — 共享工具库 drqaStringProp / drqaAssertNewCell / drqaCreateWidthCell / drqaCreateSpaceCell 等
- `space-qa-pattern-report.md` (21815B), `autospacePattern.md` (7609B) — space pattern 侧

## 关键 spec (msg#187, grounded)

good pattern 结构 == bad pattern 结构，但 good 不报 DRC；数值卡 **value**（BOUNDARY，正好等于 rule value）和 **value+grid**（PASS_HIGH）；bad 卡 **value−grid**（FAIL_LOW，必违规）+ mark 覆盖违规区。菱形 mark 用 polygon 精确覆盖（drqaRotatedVertices 同公式）；口字环用 dbLayerAndNot（不可自交多边形）。

## 合成方向 (B-档 synthesized, grounded on real AA_W_1.il + msg#187 spec)

把 SKILL width-rule QA pattern 生成逻辑抽成可离线复用的 **Python 生成器** `qa_width_pattern_gen.py`，读 rule spec JSON → 输出结构化 manifest (good PASS_HIGH+BOUNDARY / bad FAIL_LOW+mark, 12 形族 A/V/B/C/H/J/K/L/U/O/F/G, H=polygon 4 顶点, O=ring 8 顶点 frame, L=6, U=8)。资产 A=真实 AA.W.1 (value 0.025, grid 0.0001, 12 types); 隐藏 B=重参数化 M1.W.1 (value 0.080, grid 0.0005, 8-type subset, mark DRC_ERR); B_broken=value/grid=0 退化优雅报错。判分 16 条 ①–⑯ a–p。

## DISTINCT vs 既有 shard C cases

- r195 AutoViaDeGui (layout_virtuoso AutoVia GUI), r192 FloatingPinGen (layout_virtuoso floating pin), r189 DeleteM1Shapes (layout_virtuoso M1 删除) — 均非 DRC QA pattern 生成
- r206 DupViaPriorityCheck (layout_aether gdspy 连通性), r202 AntPatternConfigAudit (layout_aether ANT config BFS), r201 CentroidPlaceAudit (layout_aether 共质心), r199 HierCellPatternFind (layout_aether 层级 cell), r204 HierJumpToolbarGen (layout_aether GUI) — 均非 width-rule good/bad pattern 形族生成
- 本案首次 ground on **DRC QA width-rule good/bad pattern 形族生成** (PASS_HIGH/BOUNDARY/FAIL_LOW 三档 + value/value±grid 边界 + 45° 菱形旋转公式 + 口字环 dbLayerAndNot frame + 12 形族)，与既有互补不重叠
