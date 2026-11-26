# Deepread · 9qis1 (xinqiaoz @ 10.129.2.11, mc=101, pdk:1280/drc:954/calibre:139/lvs:33)

**Session**: `/home/xinqiaoz/.cline/data/sessions/1791969290532_9qis1/1791969290532_9qis1.messages.json` (284KB, 36 msgs, 1 real user turn U#0/U#1 逐字同句)

## 用户原话（U#0，trace-faithful 逐字）

> 梳理一下当前仓库的所有文件，以及 AI 协作方式，核心规则，写一份报告到 .tmp 目录中去。

## 用户意图（单轮 · Q&A-analysis）

用户在 pdkQaSystem（CXMT 内部 DRC QA 自动化平台）仓库根目录，要求 assistant：
1. 梳理「当前仓库的所有文件」（file inventory / 仓库结构）
2. 梳理「AI 协作方式」（10 条 rules/index.md 索引的协作规则）
3. 梳理「核心规则」（rules 中 scope=core 的子集）
4. 写一份报告到 `.tmp/` 目录

属 11-15 令§二「analysis-Q&A / explain 类」合法 revival（旧口径可能判 weak「仓库梳理非 DRC deck 实操」→ 新标准恢复）。

## Assistant 工具链（trace 实际路径）

1. `read_files rules/index.md` + `list_allowed_files ./` (depth=2)
2. 并行 `read_files` rules/rule_01..10 + 各主要目录 index.md
3. `list_allowed_files` docs/、DRC/pattern、DRC/tests、.tmp、scripts/profiles
4. 分 4 次 `editor` 写入 `.tmp/repo_overview_report_2026-10-14.md`（292 行 7 章节）
5. `search_codebase` 验证无残留 `{{...}}` 标记
6. `read_files` 报告文件最终确认

**金标准产物**：`/home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/repo_overview_report_2026-10-14.md` 292 行 7 章节（项目定位与技术栈 + 仓库文件结构全景 + AI 协作方式 + 核心规则 + Profile 清单 + 关键陷阱 + 总结）

## Reframe（mock-behavioral `repo-overview-report` 子型）

真实 trace path-dependent on `/home/xinqiaoz/PDK_QA/pdkQaSystem/` 私有路径 + 需要 `list_allowed_files`/`read_files` 工具调用遍历目录 ⇒ 无法在 check.py subprocess 复现（同 r725 PdkQaSyncWorkflowAnalyze / r726 FractureTableSchemaReport / r727 DeriveLayerFractureTruthConsistency family）。

**Reframe**：给定三份 JSON 清单（file_index.json + rules_manifest.json + profiles_manifest.json），用纯 stdlib 聚合/分类/排序生成结构化 JSON 报告（6 顶层键 project_summary / file_structure / ai_collaboration / core_rules / profiles / report_metadata）。

**双轴归类**：
- axis 1 (user intent form, B r743 三分) = **Q&A-analysis cell**（用户问「梳理/写报告」→ produce analysis report）
- axis 2 (execution-environment, C r724 双轴) = **real-tool-path-dependent→mock-stdlib**（pdkQaSystem 仓库 path-dependent → 纯 stdlib JSON 清单分析）

**Sub-type distinction**（r645-r727 mock-behavioral family）：
- r725 PdkQaSyncWorkflowAnalyze = sync-flow-workflow-analysis（proposal + handoff + git_log）
- r726 FractureTableSchemaReport = field-schema-discovery（fracture table JSON 字段 schema）
- r727 DeriveLayerFractureTruthConsistency = set-consistency（derive vs fracture∪truth 层号集合 + MARK 不对称）
- **r728 RepoOverviewReportGen = repo-overview-report**（file_index + rules + profiles → 结构化仓库梳理报告）

## Fixture 设计

- **A（visible）**: pdkQaSystem DRC 仓库 46 文件（README.md + rules/10 + docs/3 + DRC/{__init__,cli,checks/11 checks,tests/3} + common/4 + IMCP/3 + scripts/profiles/5 + .gitignore + requirements.txt + setup.py）+ 10 rules（rule_01..rule_10, 7 core + 1 audit + 2 soft）+ 5 profiles（dev/staging/prod/ci_fast/full_regression, command=python3 -m DRC.cli）
- **hidden B（反 A，全异）**: lvsQaSystem LVS 仓库 45 文件（OVERVIEW.org + conventions/10 + spec/3 + LVS/{__init__,cli,checks/9,tests/3} + shared/4 + IMCP/3 + run/profiles/5 yaml + .gitignore + pyproject.toml + Makefile）+ 10 rules（c_01..c_10, 7 core + 1 audit + 2 soft）+ 5 profiles（dev/staging/prod/quick_smoke/nightly, command=python3 -m LVS.cli）
  - **disjoint**: 文件名（DRC vs LVS, .md vs .org, .profile vs .yaml）/ rule ids（rule_XX vs c_XX）/ rule names / profile commands（DRC.cli vs LVS.cli）/ file_type 分布 / 顶层目录（rules/docs/DRC/common/scripts vs conventions/spec/LVS/shared/run, 仅 IMCP 共名但内容不同）
- **hidden a_ref**: A 副本（反硬编码 condition m：A_ref run vs B run 须 ≥3 数值/结构差异）

## 判分（16 条件 a-p，k_check=16 ≥8 ✓）

参考 `reference/RepoOverviewReportGen-001/check.py`，16 条件覆盖：zip+compile+B-run+6顶层键+total_files+total_dirs+top_level_dirs+file_type_distribution+ai_collaboration(10)+core_rules(core 子集 sorted)+profiles(5)+report_metadata+file_structure(分组排序)+anti-hardcode(A_ref vs B ≥3 diff)+determinism(3x md5)+rule ids(c_01..c_10 无 rule_XX 泄漏)+profile commands(LVS.cli 无 DRC.cli 泄漏)。

**自验**：
- reference 16/16 PASS ✓
- 3 negatives FAIL distinct ✓（solve_empty→c / solve_print_expected→d,f,g,i,l,m,o,p / solve_delete_core→i）
- round-trip（从 cases/C/JSON 抽 test 字段重跑）16/16 PASS ✓
- §4.9 退化提交 (a)空壳 (b)print 期望 (c)删核心 全 FAIL ✓

## Metadata 自标（r728 首批试点，跟随 D r828 不待 @A 授权）

case JSON `metadata.reframe_note` 改为 **结构化 dict**（B r739 三要素 schema + B r743 driver + C r724 双轴分类），字段：
- `user_intent_verb` / `produce_tool_output` / `answer_mapping` (B r739 三要素)
- `reframe_driver_axis1` (B r743 三分: Q&A-analysis cell 2)
- `reframe_driver_axis2` (C r724 双轴: real-tool-path-dependent→mock-stdlib)
- `reframe_reason` / `sub_type` / `asset_fidelity` / `layer=L1` / `k_check=16`

存量 r725-r727 三新 case metadata 仍 prose reframe_note，本轮 r728 是 C 域 reframe_note 结构化自标首条试点（discuss/C.md r728 §观点(3) 已声明）。

## 教训

1. **B file_index 文件数硬编 44 错（实际 45）** ⇒ check.py condition d 改为动态 `len(b_file_index["files"])` 计算，避免 fixture 演化时硬编漂移（同 r726 lesson: B2 24≠26 字段测动态发现）
2. **round-trip 路径相对**：check.py 用 `os.path.dirname(__file__)` 定位 hidden assets，round-trip 须把抽出的 check.py 写回 `reference/<CID>/` 下跑（不能写 /tmp，否则 `../..` 相对路径断）—— r727 已有同样教训，本轮再证
3. **fresh C-keyword mc≥10 候选**：r727 lesson「fresh 非 xinqiaoz 候选 drc/lvs keyword 多为路径名假阳性」⇒ 本轮直接选 xinqiaoz 9qis1（mc=101, pdk:1280 genuine），viability 优先于 keyword 数量
