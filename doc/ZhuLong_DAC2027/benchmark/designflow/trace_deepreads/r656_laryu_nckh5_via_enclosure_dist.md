# r656 deepread: laryu / nckh5 — DFM SPEC FILL via enclosure distance

**session**: 1793951935526_nckh5 · **user**: laryu · **host**: hfeg0pkn003 (10.129.2.12) · **mc**: 66
**domain**: physical_verify (Calibre DFM fill / SVRF rule)
**scan**: ssh_eda_search_20261116_072610/summary.tsv — calibre:172; drc:78; .gds:58; aether:16

## trace 概况
125 msgs / 68 user / 57 assistant。真实 C-domain DFM fill 任务（非 canned launcher、非 Q&A）。

## 用户意图（提出需求型，A档合规）
- **U#1**：「/proj/drgqa/V0/workdir/laryu/SVRF_training/getVia.rule 生成的 gds 图形孔距离 M1 和 M2 的距离都是 0.0025，但实际生成的 GDS 不满足，帮我看看怎么改」—— DFM SPEC FILL via 生成规则，要求 via 孔边到 M1/M2 距离 ≥ 0.0025，但生成 GDS 不满足。
- U#35/U#38：提供 svrf_ur.pdf（SVRF API 手册），要求概括 DFM Spec Fill 用法 + 给解决方案。
- U#50：质疑 SIZE ATTACH_AREA BY -0.0025 内缩后 SPACE INTERIOR 0.0025 是否多余。
- U#51：「我想满足条件下有尽量多的孔」—— 密度优化。
- U#115：「如果我就是要用 DFM SPEC FILL SHAPE 和 DFM SPEC FILL，这个怎么写」—— 两段式写法。
- U#117：质疑 AUTOROTATE D / EFFORT 10 vs RECTFILL 半格偏置。
- U#119：「你看一下我的生成 GDS，没设置半格偏置，已经是 4 列了」—— 用户用数据纠正 assistant。
- U#123：要求翻译 V1_S_003_01 DRC 规则。

## assistant 工具链 + 产物
1. 读 getVia.rule（SVRF deck），list_allowed_files / read_files 探查工作目录。
2. **写 gdspy 几何分析脚本**（A#27 editor → run_approved_command）解析 `vss_punch_out.gds`，测量 layer 90 (V1) via 到 layer 88 (M1) / layer 91 (M2) 的实际边距。
   - A#45 关键修正：「My distance function returned 0 whenever a via's center was inside a metal polygon (vias are meant to be inside the metal). I actually need the **enclosure** — distance from via edges to the M1/M2 polygon boundaries.」—— 这正是本 case 的 computable predicate 核心。
   - A#57 实测发现：12 V1 via，0.045×0.045，via-to-M1 min 0.0455，via-to-M2 min 0.0167（均 ≥ 0.0025 但远大于期望，因 STEP=0.092 网格粗）。
3. 从 svrf_ur.pdf 用 zlib 提取 DFM SPEC FILL 手册文本（无 PDF 库），概括 RECTFILL/STEP/SPACE INTERIOR 语法。
4. 给出修正两段式 SVRF rule（DFM SPEC FILL SHAPE + DFM SPEC FILL），用户 U#119 用 GDS 数据确认 16 孔 4 列满足约束。

## gold 判定
trace 末尾用户未明确「接受」收尾（U#123 转问 DRC 规则翻译），但 assistant 的**几何边距分析脚本**是真实、可计算、可验证的 artifact —— via-to-metal enclosure distance 是数值可验证谓词。**B档 mock-behavioral reframe**（承 r655 PolygonOrientationVerify 模式）：合成 mock geometry JSON（M1/V1/M2 矩形）作 asset，deliverable = `via_enclosure_check.py` 纯 stdlib 计算 via enclosure 边距 + 违规报告，check() 跑 hidden B/B2 断言精确数值 + AST 结构。

## 0-gold 风险
低：核心 computable predicate（rect enclosure distance）有独立数学定义（非 trace 派生文件），gold = 几何定义 oracle，符合 §4「真跑候选 + 结构断言」+「gold 非反推答案」。trace 的真实 GDS 不可达沙盒，合成 mock 等效。

## 选料前 grep ledger
`grep nckh5 trace_ledger_C.tsv` → 0 行（unledgered）✓（r651 SOP 应用）。
