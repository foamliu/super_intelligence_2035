# Deepread — v4lvu (PyAetherCurDesignApi-001)

- **session**: `1793006248706_v4lvu.messages.json`
- **user/host**: e0023936 @ hfhds201
- **match_count**: 24 (mc≥15 shard A threshold)
- **size**: 37152 bytes, 17 msgs (10 user / 7 assistant)
- **domain**: eda_other (pyAether API doc-query)
- **claimed**: 2026-11-09 r262 (shard A)
- **case**: EDA-Eval-DesignFlow-PyAetherCurDesignApi-001 (A-faithful, L2-static+subprocess)

## Why this trace (selection)

r262 候选筛选: 18 fresh (mc≥15 + shard A tools, 4-shard EXCL 1889). 初选 dswuv (mc62
sine-wave) 深读后发现是已覆盖 WvSineWaveAnalyze-001 (ju0g4) 的 DUP → park. 复查 fresh
池: yrvv2/g8ory 亦 sine-wave DUP; k9dnd 是根因/修法 (setup_offline.sh 排障, 非
A-faithful 目标); lpn8o/u574y 是元/数据任务; nzxx2 是 skill 编排 (group-gen 仅薄
wrapper, 金标准难收). v4lvu 是干净 A-faithful doc-query (与 r261 WvCursorApiGen 同型,
但域不同: pyAether 取当前设计, 非 WaveView 光标).

## Real user turns

- **USER#0** (msg0, act): `使用MCP的工具查询pyAether接口文档 Get the currently opened schematic design.`
  → 纯目标 (API 文档查询), 无根因/修法. **A-faithful 合格**. 本 case 取此轮.
- USER#1 (msg7, act): `使用MCP的工具查询tcl接口文档 add a vertical cursor to panel.`
  → = r261 WvCursorApiGen-001 的 verbatim prompt (DUP, 跳过).

## Assistant tool chain (USER#0 portion, msgs 0-6)

1. `RAG_MCP_Server__search_apis(query="Get the currently opened schematic design",
   lang=pyAether, top_k=5)` + 同义改写 query → 命中 aeDesignIsSchematic (sim 0.73) /
   aeGetCurDesign (sim 0.68) / emyDesignIsSchematic / cbGetCurRefDesign /
   aeFindSDLLayoutForSchematic / aeFindSDLSchematicForLayout.
2. `RAG_MCP_Server__get_api_details(api_list=[aeGetCurDesign, aeDesignIsSchematic],
   lang=pyAether)` → 取完整签名/返回/示例.
3. 输出结构化 markdown 文档 (msg6): 核心 `aeGetCurDesign()` → emyDesign (当前绘图区
   cellview 标识); 补充 `aeDesignIsSchematic(cv: emyDesign) -> bool`; 官方示例
   `emyInitAether("-adv") → aeOpenDesign("test","test","layout") → aeGetCurDesign()`.

## Gold facts (verified via pyAether knowledge base)

核心 API (trace 答案):
- **aeGetCurDesign**() -> emyDesign — returns cell view identifier of current drawing
  area. 示例: `emyInitAether("-adv"); aeOpenDesign("test","test","layout"); aeGetCurDesign()`.
- **aeDesignIsSchematic**(cv: emyDesign) -> bool — flag whether design is schematic.
  示例: `design = aeGetCurDesign(); aeDesignIsSchematic(design)`.

相关 design 访问族 (知识库补全, 用于报告完整性):
- emyDesignIsSchematic(design) -> emyBoolean
- aeOpenDesign(lib, cell, view='layout', mode='edit', selLcv=False) -> bool
- aeGetCellView(da=None, level=0) -> emyDesign
- aeGetTopLevelCellView(da) -> emyDesign
- aeGetWndCellViewId(top=False, oritop=False, wnd=None, focus=False) -> emyDesign
- mdeGetCurrentLibCellView() -> tuple(string)

## Synthesized case

- **deliverable**: submit.zip = `schematic_design_api_report.json` (8 条 pyAether API
  结构化文档) + `get_current_design.py` (def get_current_design(): aeGetCurDesign →
  aeDesignIsSchematic → print).
- **A assets**: prompt.txt (verbatim USER#0) + task_brief.md + config_a.json
  (design_id=db:0x1A2B, is_schematic=true, lib=analog_lib/cell=amp_top/view=schematic).
- **hidden B**: design_id=db:0x7F4E, is_schematic=false (layout 视图), lib=digital_lib/
  cell=clk_div/view=layout (跨输入泛化).
- **Bp**: 3 seed (rf_lib/lna, io_lib/pad, pwr_lib/ldo) 防硬编码 design_id.
- **reference**: mock_pyAether.py (fixture-driven test double) + fixture_A/B +
  check.py (14 conds a-n: 报告结构 + API 事实 + 脚本静态 + mock 真跑跨输入 + 防硬编码).
- **self-verify**: REF PASS 14/14; 5 negative (wrong_report→c / print_only→i /
  core_deleted→j / naive_noop→h / hardcoded_a→l) 全 FAIL DISTINCT=5; §4.9 三假
  (empty→a / print-only→i / strip-core→j) 全 FAIL.
- **gate**: k_rationale == k_check == 14 ≥ 8. test_sha8 = d3d1a4b8.

## Note

本 case 与 r261 WvCursorApiGen-001 同为 doc-query 型 (A-faithful), 但 API 域不同
(pyAether 取当前 schematic 设计 vs WaveView Tcl 光标), 与 FindPcells-001 (pyAether
code-gen) 亦不同 (本 case 是文档+用法脚本, 非布局代码生成). 无 DUP.
