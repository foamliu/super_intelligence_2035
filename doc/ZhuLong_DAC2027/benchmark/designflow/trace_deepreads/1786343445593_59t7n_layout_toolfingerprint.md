# 深读笔记 — 1786343445593_59t7n (e0014566 @ hfeg0pkn001, mc=122)

- **session**: 1786343445593_59t7n.messages.json, 61 msgs, agent cline + pyAether/RAG MCP
- **tools (实际 tool_use)**: read_files:5, run_commands:3, RAG search_apis:18, get_api_details:5, SandBox run_code:5, search_codebase:1
- **真实任务**: USER#0 `read the prompt.md and do the job in it.` → prompt.md 要求分析 Aether layout `drjqa_top/BCenterL/Layout`：(1) 列出所有构成元素 (2) 识别哪些由 `autovia` 和 `powerfill` 生成。
- **工具理解（agent 读 SKILL.md + .il + genPowerFill.py 得出）**:
  - AutoVia：生成 cell 名 `<topcell>_<viaTypeSel>_<pwrnet>_VIA`（实测为 `<topcell>_YYYYMMDD_VIA_TOP`，日期来自 `IMCleGetTimeString` → YYYYMMDD，如 20250425=2025-04-25），cell 内是海量 customVia 阵列，在原点 (0,0) R0 实例化。
  - PowerFill：Y-layer shape 带 `flight` purpose（y0–y9，genPowerFill.py L679–698 处理 drawing+flight 两 purpose）；fill 产物命名 `auto_pgdm`（auto power-ground dummy metal，默认 stream-in lib `auto_pgfill`）；Y-layer via 中间表示命名 `auto_pc`（喂给 `cxmt_layout_convertYlayerToPcell`）。生成 fill shape，不生成 via 对象。
- **内省取证（dbOpenCellViewByType 只读打开）**:
  - bbox `((-17881.25 -895.793) (-5052.49 882.27))` micron
  - 总量：166 instances(40 unique masters/6 libs)、7453 shapes(47 layer/purpose 类)、886 customVia(全部 nil viaDefName/viaHeader)、1611 routes、1897 nets、7 figGroups(Group0–Group5+Group3_0)、4 markers、0 pins/terms/blockages/rows
  - 实例 master 名取法：`inst~>cellName`/`libName`/`viewName`（不是 `inst~>master~>...`，初试返回 nil）；`foreachkey` 在 pyAether 不可用 → 改 list-based key collection
- **三候选 tool-generated cell（lib=zlib）**:
  - **I30 `BCenterL_20250425_VIA_TOP`** → AutoVia。含 **49,322 vias**（海量 customVia 阵列），名含 `VIA`+日期戳 `20250425`。输出过大被截断 → 改只取计数/shape 摘要/首个 via header。
  - **I21 `BCenterL_au_to_pg`** → PowerFill(fill)。`au_to_pg`=auto→PG fill，6874 shapes（6809 rect AT4 DUMMY2 + 62 polygon AT4 DUMMY2 + 2 PG DUMMY + 1 NW），5 个 sub-instance `BCenterL_auto_pgdm_{1,2,3,0519}`+`BCenterL_auto_pgdm`，0 vias。
  - **I29 `BCenterL_PCUCT_auto_pc1`** → PowerFill(Y-layer)。`auto_pc`=auto pcell，584,024 shapes（y5/y6/y8/y9 `flight` purpose labels+rects + MT2 drawing），0 vias/0 inst，是 convertToPcell 前的原始 Y-layer GDS。
- **失败模式/教学点**:
  1. 实例 master 名属性路径错（`master~>cellName` 返回 nil）→ 正解 `inst~>cellName`
  2. `foreachkey` 不可用 → 用 list 聚合 key
  3. 49322 via 阵列迭代致输出过大被截断 → 改取计数+摘要
  4. 工具识别 = 命名约定（regex/关键字）+ 内容取证（via 阵列规模/nil_viaDef、Y-layer flight purpose、fill shape、0 vias）双重印证，而非单一信号
- **gold 不可复现（A-档不可行）**：gold = 对 live Aether OA cellview `drjqa_top/BCenterL/Layout` 的分析报告，依赖 live Aether + 该设计 + 49322 via 阵列，working dir 已清理 → B-档 synthesized L1-boundary，seed=真实命名约定+取证数据。
- **case 合成**：`EDA-Eval-DesignFlow-LayToolFingerprintAudit-001`（layout_aether）。交付 `lay_tool_fingerprint_audit.py`（argv <introspection.json> <tool_specs.json> <out.json>，stdlib-only），按命名约定+内容特征判别每实例 AutoVia/PowerFill/neither，emit tool_classification+summary+forensic_flags。资产 A=BCenterL 真实取样；hidden B=ChipTop(20260115/31204/AT3 DUMMY1/y2,y7 flight)全异。12 条断言①-⑫(a-l)。
- **正交性**：shard C 首个「**Aether layout cellview 工具指纹审计**」子主题，正交于 DRCPatGen/DRCPatPlacePlan（DRC testpattern 生成）、AutoViaLayoutMerge（via 合并）、PowerFillMergeGen/PFMergeDupAudit（power-fill 合并去重）。本 case=从 cellview 内省反查「哪个工具生成了哪个实例」，非生成/非合并。
