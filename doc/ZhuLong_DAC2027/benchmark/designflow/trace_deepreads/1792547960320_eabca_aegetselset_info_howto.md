# deepread — 1792547960320_eabca (jianingw @ 10.129.8.134 / hfeg0plg83, mc=89)

**trace**: 194719 B / 67 msgs (1 real user-text seed turn U#0 + 8 mid-session user-text turns)
**domain**: layout_aether (pyAether API howto Q&A)
**host scan**: jianingw across hfeg0plg83/89/104/plg09/pkn002 — keywords pyAether:224;cellview:161;dbget:70;virtuoso:26;aether:21

## 用户真实意图（U#0 逐字）
`<user_input mode="act">用ae.aeGetSelSet获取选中对象之后，怎么查看选中对象的各种信息</user_input>`
= 单一明确 howto Q&A：在 pyAether 里用 aeGetSelSet 拿到选中对象后，如何查看对象的各种信息。
用户未给根因/未给修复方案 → 符合 A 档选轮规则。

## assistant 工具链（msg 1-21）
RAG 检索 pyAether API 文档 → 命中 aeGetSelSet / emyFig 信息查询 API 系列 → 综合产 how-to answer（msg 21, 2295B）。
- msg 1-20: 多轮 RAG search_apis（aeGetSelSet, emyFigGetTypeName, getBBox, emyFigGetBoundary, emyFigGetNetName, emyObjectGetProp, emyObjectIsInFigGroup, aeGetCurDesign, mdeGetCurrentLibCellView）+ get_api_details
- msg 21: 完整讲解：①aeGetSelSet 返回 Tuple[emyFig] + 变体(aaeGetSelectedSet/aeGetObjectSelectedSet/aeGetObjectSelectedSetEx) ②按类查信息(emyFigGetTypeName 类型 / getBBox+getBBoxWidth+getBBoxHeight 包围盒 / emyFigGetBoundary 边界 / emyFigGetNetName+emyFigGetTermName 网络/端子 / emyObjectGetProp 属性 / emyObjectIsInFigGroup+emyObjectIsFigGroup 图组 / aeGetCurDesign+mdeGetCurrentLibCellView 设计) ③万能方法 dir()+getattr()
- 注：沙箱未配置，代码未实跑，API 名称/签名均来自官方 API 文档（path-dependent：需 Aether 安装+license+GUI+在线 session）

## 后续 user turn（分离子任务，本 case 不取）
- U#22: virtuoso 中获取选中对象的函数 → geGetSelSet()（SKILL 域，分离）
- U#30: geGetSelSet ~> 获取参数列表，Aether 中如何 → 属性访问差异（分离）
- U#42: ~>row 获取行数，Aether 中如何 → 阵列实例 numRows/numCols（分离）
- U#56: 获取 list 第一个元素 → Python tuple 下标 [0]（基础，分离）
- U#58-65: fig=ae.aeGetSelSet() / dir(fig[0]) / 遍历所有属性 → 代码解释（分离）

## 11-15 §二 revival
旧 parked note（2026-11-03）：「T0='aeGetSelSet 怎么查看选中对象信息'=QA 非 design-flow」+ 2026-11-05 「screened r109: not shard-C deliverable (Q&A)」→ pre-11-15 误判（Q&A 类被排除）。
11-15 §二 revival：analysis-Q&A / howto / explain 全部复活 → 本 case 合法。

## reframe = mock-behavioral `aegetselset-info-howto-Q&A`
（r645-r742 family 新子型 **aegetselset-info-howto doc-extraction**，layout_aether，与 r741 aether-repeat-copy-howto 同族）
真实 pyAether 工具 path-dependent（需 Aether 安装+license+GUI+在线 session）→ mock-stdlib：SUT 仅读固定 pyAether 参考手册片段 + API cheatsheet（.txt），抽取「aeGetSelSet 后如何查看选中对象信息」相关事实到结构化 JSON 报告，每条事实附 evidence（来源文档名 + 文档中确切源行）。

## reframe mode ③evidence-only (P-006 r618 (C)-(A) 分流，同 r736/r740/r741)
analysis-Q&A on 固定文档 artifacts（无 process 可在 B 上重跑）⇒ SUT 仅产 report.json (answer-only)；B/B2 作 judge-self-check（判分器内部独立重算金标确认非硬编 A）；牙齿来自 ①content-correctness(18 断言) + ②evidence-verification + B/B2 cross-input guard + anti-stub。

## BUILD → EDA-Eval-DesignFlow-AeGetSelSetInfoHowto-001
- asset A(sample_input/docs/: pyaether_ref_manual_ch12.txt [aeGetSelSet 12.5 + variants] + ch45.txt [6 info APIs by Category tag] + ch50.txt [design] + cheatsheet [universal method dir]) + prompt.txt(U#0 逐字) + task_brief.md
- hidden B(hidden/b/docs/: ch14 [aeGetSelSet 14.9 → Tuple[emyFigObj], variants aeGetSelectedFigs*] + ch47 [emyFigTypeName/figGetBBox/emyFigGetOutline/emyFigGetNet/emyFigGetProp/emyFigInGroup] + ch52 [aeGetCurrentDesign] + cheatsheet [members]) 
- hidden B2(hidden/b2/docs/: ch9 [aeGetSelSet 9.3 → List[emyShape], variants aeGetSelFigs*] + ch33 [emyShapeType/getShapeBBox/emyShapeGetEdge/emyShapeGetNet/emyShapeGetProp/emyShapeInGroup] + ch38 [aeGetActiveDesign] + cheatsheet [listAttr])
- 三 fixture chapter/return_type/variant_names/6 info APIs/design/universal_method 八维度全不同 反硬编码
- reference solve.py(纯 stdlib: 读 docs/*.txt → 按 Category tag 抽 17 事实 + evidence map)；check.py 18 断言 a-r(B/B2/A expected 人工独立推得)

## 自验（本机 python3）
- reference solve.py PASS 18/18 ✓
- 3 negatives FAIL distinct: solve_empty→17 FAIL(b-r blocked) / solve_print_gold(硬编 A gold)→15 FAIL(d-n 内容全错 + o/q evidence 伪造 cite A 文档不在 B) / solve_no_evidence(硬编 A 无 evidence)→15 FAIL(d-n + o/q evidence 缺失) ✓
- §4.9 退化提交(空壳/print-gold/无 evidence)全 FAIL ✓
- k_rationale=k_check=18 ≥8 GATE PASS ✓
