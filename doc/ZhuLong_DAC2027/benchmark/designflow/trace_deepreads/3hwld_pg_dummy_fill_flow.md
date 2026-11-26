# Deepread: 1792496117600_3hwld (ellawu @ 10.129.2.10, mc46) — pg_layout

**trace_source**: user=ellawu, host=10.129.2.10 (hfeg0plg*), session_file=1792496117600_3hwld, match_count=46
**keywords**: drc:1865; .gds:91; calibre:63; aether:20; transistor:9; cmos:5; pyaether:4; techfile:3
**domain**: pg_layout (PG dummy fill rule deck)
**ledger status**: claimed r696 (2026-11-17), build deferred to r697

## 用户真实意图 (U#0 逐字)
> 整理一下flow详细一点
> --- Attached file: G4C_AA_PG_dummy_fill_for_Logic.rule → uploads/G4C_AA_PG_dummy_fill_for_Logic.rule

用户（ellawu，物理验证工程师）给了一份 Calibre TVF (Tcl Verification Format) rule deck
（AA/PG dummy fill for G4C logic block cells，3169 行），要求把这份 deck 的 **flow 详细整理**一下。
即：解析 deck 结构 → 产出有组织的流程说明。属于 11-15 任务初心下合法的 analysis/organize 任务。

## Asset A (真实附件，原文)
- 文件: `G4C_AA_PG_dummy_fill_for_Logic.rule` (3169 行, TVF/Calibre DRC deck)
- 已 scp 到 r696 workdir: `pg_dummy_fill.rule`
- 头部: Copyright ChangXin Memory; Description "auto adding AA/PG dummy for G5 block cells"
- Revision History: v1.0–v2.0 共 11 条 (authors: hana.song v1.0–v1.8, cedard v1.9–v2.0), 格式 `//    vX.Y  YYYY/MM/DD author`
- LAYOUT PATH "/proj/drexp/V0/ver/drc/ella/MatBlock_9X5_2/AA_PG_DUM_Logic/MatBlock_9X5_2.gds"
- LAYOUT PRIMARY "MatBlock_9X5_2", LAYOUT SYSTEM GDSII
- DRC setup: DRC RESULTS DATABASE "AAAAA.drc.results" ASCII; DRC SUMMARY REPORT "AAAAA.drc.summary" HIER; DRC MAXIMUM RESULTS ALL; DRC KEEP EMPTY YES
- RESOLUTION 1 / PRECISION 10000 / UNIT LENGTH U
- FLAG: ACUTE/OFFGRID/SKEW/NONSIMPLE POLYGON/NONSIMPLE PATH = YES
- INCLUDE "/apps/imctf/runset/calibre/cxmtG4C/current/common/Layer/calibre.layer_20240920"
- LAYER MAP 235 DATATYPE 250 20000; LAYER PR_BOUNDARY 20000
- `set VAR value` TVF 变量定义 ~30+ (PG_Dummy_MinWidth 0.036, AT4_NCH_MaxW 0.3, ...)
- VERBATIM { } 块 10 个 (lines 4/157/165/252/579/953/963/1024/1033/...) — 主要 flow 单元
- DRC SELECT CHECK (line 3068) 列出 check names (1st_2nd_DIF_OUTER_PGDummy_interact_SUB, ...)
- CHIP = OR BORD_drawing (EXTENT)

## 拟造任务形态 (r697 BUILD plan) — L1 / pg_layout / trace-faithful A档
**case_id**: EDA-Eval-DesignFlow-PgDummyFillFlowOrganize-001
**reframe**: 给 SUT 一份 TVF rule deck (asset A 真实附件) + prompt (U#0 逐字 + 交付接口),
SUT 产出纯 stdlib `pg_dummy_fill_flow_organize.py`，读 deck → 输出**结构化 JSON flow 描述**:
- deck_meta: {description, copyright_holder}
- revisions: [{version, date, author}] (从 `//    vX.Y  YYYY/MM/DD author` 解析)
- layout: {path, primary, system}
- drc_setup: {results_db, summary_report, max_results, keep_empty}
- includes: [INCLUDE 路径]
- layer_maps: [LAYER MAP 行]
- variables: [{name, value}] (从 `set NAME value`)
- flag_settings: [{flag, value}]
- verbatim_blocks: [{line_no, count}] (VERBATIM { 块)
- drc_select_checks: [check 名]
- stats: {n_lines, n_revisions, n_variables, n_verbatim_blocks, n_includes, n_comment_lines, n_blank_lines}

**Hidden B** (反硬编): 构造一份 ~120 行结构同构但取值/命名全异的 TVF deck
(不同 revisions 作者/日期、不同 LAYOUT path、不同变量名/值、不同 INCLUDE、不同 DRC SELECT check 名)。
B 与 A 规模/取值/结构均不同 (§4.1)。

**check() (k>=8 独立断言, 跑 B)**:
① submit.zip 含 pg_dummy_fill_flow_organize.py 且 py_compile 通过
② 在 B 上 exit 0, stdout 含 'PG Dummy Fill Flow' 头, 写出合法 JSON 含全部 11 个顶层 key
③ revisions 数组长度 == B 的 revision 数; 每条含 version/date/author
④ revisions 的 author 集合 == B 实际作者集合 (反硬编 A 的 hana.song/cedard)
⑤ layout.path/primary/system == B 的 LAYOUT 声明 (反硬编 A 的 MatBlock_9X5_2)
⑥ variables 数组长度 == B 的 set 定义数; name 集合正确 (反硬编 A 的 PG_Dummy_MinWidth 等)
⑦ includes == B 的 INCLUDE 路径列表 (反硬编 A 的 calibre.layer_20240920)
⑧ flag_settings 长度 == B 的 FLAG 行数; 各 flag=value 正确
⑨ verbatim_blocks 计数 == B 的 VERBATIM { 块数
⑩ stats.n_lines == B 行数; stats.n_revisions == len(revisions); stats.n_variables == len(variables)
⑪ drc_select_checks == B 的 DRC SELECT CHECK 名列表 (反硬编 A)
⑫ 退化回归: 空壳 / 只 print A 期望串 / 删核心(返回硬编 A 的 JSON) 三假提交全 FAIL
⑬ 随机化: 2 次跑 B 输出一致 (deterministic)

**negative/**: naive_stub (print 固定 JSON) + always_empty + hardcoded_A_json (返回 A 的解析结果) → check() 全 FAIL

**distinct vs existing**: PgSvrfRuleAnalyze-001 / DrcPgOpenRuleGen-001 是 *生成* 规则或 *提取单一规则类型*;
本例是 *整理解份完整 deck 的 flow 结构* (multi-section structural extraction), 不同。
DrcEnclosureRuleExtract-001 提取单一类型 (enclosure); 本例提取全 deck 11 类结构 section。

## r697 BUILD 清单
- [ ] assets/EDA-Eval-DesignFlow-PgDummyFillFlowOrganize-001/ : G4C_AA_PG_dummy_fill_for_Logic.rule (A), prompt.md, task_brief.md
- [ ] assets/.../hidden/ : pg_dummy_fill_B.rule (手造 ~120 行), hidden_manifest.json
- [ ] reference/.../ : gen_pg_dummy_fill_flow_organize.py (gold), check.py, negative/ (3 stubs + selftest)
- [ ] 自验: gold 在 A 与 B 上都跑通; 3 假提交 FAIL; py_compile
- [ ] jsonl: EDA-Eval-DesignFlow_C.jsonl 追加 1 条 (k_rationale == k_check == 13)
- [ ] ledger mark --status case --case-id ...
- [ ] MEMORY + git 双仓提交
