# 深读笔记：s922g — fracture table 字段报告（schema analysis）

- **session**: 1792128707529_s922g
- **user/host**: xinqiaoz @ 10.129.2.11（mc=61，keywords: drc:969 pdk:586 lvs:73 calibre:71）
- **size**: 244KB / 31 msgs / 20 user / 11 assistant / **1 real user turn**
- **tool_use**: read_files:5, run_commands:1, list_allowed_files:7, search_codebase:3, editor:2, run_approved_command:1
- **trace_source**: 真实 trace，11-15 令§二 analysis-Q&A/explain 类合法（B 类复活）

## 用户原话（U#0，逐字）

> 从当前的仓库中找几份 fracture table，如果找不到或者数据不够，可以从 /apps/imctf/develop/PDK_QA/DRC/ 的各个平台下找几份 fracture table。如 /apps/imctf/develop/PDK_QA/DRC/V2/DRGPY/0.2.0/V2_DRGPY_2_FractureTable.json。
> 然后我要求你向我报告一下，这些 fracture table 的每条数据都包含哪些字段？

## 真实意图

数据/文档分析：定位跨平台 fracture table JSON 文件，统计每条记录的字段结构（字段名/类型/可空性/含义/示例），产出一份字段报告。assistant 选取 5 份跨 3 平台样本（V2_DRGPY_2/V2_DRGPX_3/V2_DRGPY_5/DRDQP_1/G4B_DDJOC_2），写分析脚本统计 358 条记录逐字段，交叉核对 docs/conventions/entry_and_configuration.md 与 common/designManual/FractureTable.py 解析器，结论：26 字段统一 schema，仅 layer_num 为 int 其余 str。

## 真实 fracture table 结构（from /apps/imctf/develop/PDK_QA/DRC/V2/DRGPY/0.2.0/V2_DRGPY_2_FractureTable.json）

JSON 数组，每元素一个 dict，26 字段：
chip_extract_layer, chip_opc_layer, design_layer, eq_type, frame_opc_layer, grid, grid_chip, grid_frame, layer_name, layer_num(int), main_layer, manual_opc_output, mask_name, mask_tone, mask_type, opc, opc_grid, period_type, pie_remark, pr_type, refer_layer_chip, refer_layer_frame, second_layer, specialboolean, tapeout_fracture, td_type。
常 null 字段：chip_extract_layer / manual_opc_output / pie_remark / second_layer / specialboolean。

## reframe（mock-behavioral data-analysis 子型 `fracture-table-schema-report`，physical_verify）

- 真实 trace path-dependent（依赖 /apps/imctf/develop/PDK_QA/ 与用户仓库 pdkQaSystem）→ 纯 stdlib json 分析：给定若干 fracture table JSON 文件（每文件 JSON 数组、每元素一条记录），动态产出字段报告（files/field_schema/summary 三顶层键）。
- distinct vs r722 AptUsageReportGen=EDA-tool-usage-log CSV 聚合 / r723 DrcCwdRaceEvidence=drc.summary 头 CWD 竞争 / r725 PdkQaSyncWorkflowAnalyze=workflow-analysis markdown/yaml 解析 = 本例 **fracture table JSON 字段 schema 发现与统计报告**（不碰 CSV 聚合也不碰 log 解析，只做 JSON array → field schema）。

## case 产出

- **case_id**: EDA-Eval-DesignFlow-FractureTableSchemaReport-001
- **asset A**（visible）= 3 文件 26 字段 287 记录（V2_DRGPY_2:88 / V2_DRGPX_3:103 / V2_DRGPY_5:96）+ prompt.txt（逐字 U#0 + solve.py 接口）+ task_brief.md
- **hidden B**（反 A，全异）= 4 文件 26 字段 232 记录（G4B_DDJOC_2:71 / DRDQP_1:54 / ADC1T_4:62 / DHJOB_3:45），layer_num/mask_name/platform 与 A 全异
- **hidden B2**（edge，不同 schema）= 1 文件 24 字段 38 记录（G3_DEVQA_1，缺 chip_extract_layer + specialboolean，测动态字段发现 vs 硬编 26）
- **reference solve.py** 167 行纯 stdlib（json/os/sys/glob），动态发现字段并统计 type/nullable/null_count/example + per-file record_count + cross-file schema consistency
- **check.py 16 条件 a-p**：zip+py_compile+B run+JSON keys+total_files+total_records+unique_field_count+schema_consistent+field_names_sorted+layer_num schema+layer_num example+per-file counts+anti-hardcode+B2 run+B2 field_count=24+B2 missing fields+determinism
- **k_rationale == k_check == 16 ≥ 8 ✓**
- **3 negatives**（empty/print_expected/delete_core）全 FAIL distinct（c/d/f）✓
- **round-trip**：从 C.jsonl test 字段抽 check.py 重跑 reference submit.zip 16/16 PASS ✓
- **退化提交 §4.9 (a)空壳(b)print 期望(c)删核心 全 FAIL** ✓

## 教训

- 选料 fresh 过滤必须**规范化 sid**（strip `.messages.json`/`.messages.archive` 后缀）后再做并集去重，否则 ledger 用 `sid.messages.json` 而 candidates 用 `sid` 会让已造 session 重新入选（本轮 cuedk 因此撞车，已 2026-11-16 造为 3DLvsGuiCfgGen-001）。
- fracture table 真实 schema 固定 26 字段；为给 check() 留「牙」，hidden B2 用 24 字段（缺 2 个常 null 字段）测动态字段发现，避免 solver 硬编 26。
- A/B/B2 三 fixture 的 layer_num / mask_name / platform / record_count 全 disjoint，确保反硬编码条件 (l) 有牙。
