# Deepread: 0uitr — ESD EM-only tech file via-name KeyError 诊断 Q&A

**Session**: 1791972643413_0uitr · **User**: thomasz · **Host**: hfeg0pkn002(10.129.2.11) · **mc**: 29 · **Domain**: analog_context
**Agent**: deepseek-v4-flash · **25 msgs** · **Status**: completed (terminal_marker: failed_external_process_exit)

## 用户原始意图（逐字）

`/rundata/totem/drexp/ESD/MiniCMOS_WOW_Top_1009/log 看下为啥报错了`

## 对话流解析

| Msg | Role | 内容摘要 |
|:--|:--|:--|
| 0 | user | 原始意图（逐字） |
| 1 | assistant | thinking: "look at log to see why there's an error" → list_allowed_files |
| 2-3 | tool_result | `/rundata/.../log` 是文件不是目录 + agent policy enforcing |
| 4 | assistant | thinking: "path is not a directory, check parent" |
| 5 | tool_result | list parent dir → 见 log 文件 |
| 6 | assistant | "log 其实是一个文件。这是 GP 的运行日志。让我读取它" |
| 7 | tool_result | **read_files log (5843B)** → FATAL<SCH.114> KeyError('CT') + 完整 traceback |
| 8 | assistant | thinking: "FATAL error. The key error: FATAL<SCH.114> Error occurred while executing thpkgs_internal.tech.table_gen.load_technology_file..." |
| 9 | tool_result | run_commands 被 policy 拒（Raw shell tool disabled） |
| 10 | tool_result | search_codebase timed out |
| 11 | assistant | thinking: "search timed out, use read_files on .tech file directly" |
| 12 | tool_result | **read_files ESD_CD.tech (50 行)** → 10 via: VIA4/VIA3/VIA2/VIA1/CT/CTA/PCU/PCN/PCP/PCPG |
| 13 | assistant | thinking: "tech file defines EM_RULE_SET, does NOT contain stackup/layer definitions" |
| 14 | tool_result | **read_files totem.tech (31870B)** → 完整 base tech |
| 15 | assistant | thinking: "reference totem.tech is full Apache Redhawk tech file with metal, via, dielectric layers" |
| 16 | tool_result | **read_files totem.tech:300-560** → metal M1/M2 定义 + via PCN/PCP/PCNPG/PCPPG/VIA1/VIA2 定义 |
| 17 | assistant | thinking: "base totem.tech via layers with LowerLayer/UpperLayer, e.g., via PCN {LowerLayer NDIFF, UpperLayer M1}" |
| 18 | tool_result | read_files run.py + common_args_options.py → tech_view_args=dict(tech_file_name=tech_file, em_only_tech_file_name=em_tech_file) |
| 19 | tool_result | search_codebase timed out again |
| 20 | assistant | thinking: "loading pipeline: em_tech_file='ESD_CD.tech' passed as em_only_tech_file_name" |
| 21 | tool_result | **read_files input.py** → tech_file='.../totem.tech', em_tech_file='ESD_CD.tech' |
| 22 | assistant | thinking: "em_tech_file='ESD_CD.tech' is passed as em_only_tech_file_name. Pathfinder will load this EM-only tech file to override EM limits" |
| 23 | tool_result | **read_files totem.tech:559-722** → VIA2/VIA3/VIA4/VIA5/HLV/CTB_CYL/CTB_NBP/HSV/TDB 定义 |
| 24 | assistant | **最终诊断**（thinking + text）→ root_cause: ESD_CD.tech 里 CT/CTA/PCU/PCPG 不在 base totem.tech 里 → KeyError('CT') |

## 金标准诊断（agent 末尾产出）

1. **FATAL**: `FATAL<SCH.114> KeyError('CT')` at `load_technology_file → get_nrc_contents → parse_Apache_tech_file → translate_to_stackup → __process_em_via_layers → __process_em_via_attribute → __construct_upper_lower_layer_conditions`
2. **机制**: `ESD_CD.tech` 作为 EM-only tech file 传给 pathfinder（`em_only_tech_file_name=em_tech_file`），用来覆盖 EM 限值。Pathfinder 处理每个 via 时需查 LowerLayer/UpperLayer。
3. **根因**: `ESD_CD.tech` 列了 10 个 via（VIA4/VIA3/VIA2/VIA1/CT/CTA/PCU/PCN/PCP/PCPG），其中 `CT/CTA/PCU/PCPG` 4 个在 base `totem.tech` 里不存在（base 里是 PCNPG/PCPPG 非 PCPG，是 CTB_CYL/CTB_NBP 非 CT/CTA）。
4. **crash 点**: VIA4→VIA3→VIA2→VIA1 都在 base 里（只报警 TEC.213），到第 5 个 `CT`（第一个 missing）时查不到 → `KeyError: 'CT'`。
5. **修复**: 删除/纠正 ESD_CD.tech 里的 CT/CTA/PCU/PCPG，或补上 LowerLayer/UpperLayer 定义。

## 可造性判定（11-15 §二 revival）

- **真实 trace**: ✓ 25 msgs 完整对话流，agent 产出明确诊断结论
- **有牙 check()**: ✓ 交付=结构化诊断 JSON（root_cause + missing_via_names + cited_evidence + fix_recommendations），可机械核验
- **旧判 parked 原因**: "debug Q&A, non-produce" — 11-15 §二 已作废此排除标准
- **新判**: 可造（A档 trace-faithful cited-evidence-chain diagnostic Q&A）

## 与 r874 TotemLayermapFatalDiag-001 区别

- **r874 (4prf6)**: FATAL<PHY.103> layermap parsing, GDS2SC stage, missing_type_field root cause, 文件链=log+layermap+gds.cfg
- **本 case (0uitr)**: FATAL<SCH.114> KeyError('CT'), technology file load stage, EM-only tech via-name mismatch root cause, 文件链=log+ESD_CD.tech+totem.tech+input.py+common_args_options.py
- 同用户(thomasz)同项目(MiniCMOS_WOW_Top_1009)但不同 session、不同 FATAL 类型、不同根因、不同文件链路 → 非重复

## Case 落地

- **case_id**: EDA-Eval-DesignFlow-EsdEmTechViaKeyErrorDiag-001
- **domain**: analog_context
- **20 断言 (a-t)**: zip/compile/B-run/keys/has_fatal/fatal_code/fatal_keyerror_name/first_missing_via/missing_set/em_via_order/base_via_subset/em_only_mode/em_tech_file_name/root_cause/fix_recs/cited_evidence/B2-clean/warnings/traceback/anti-hardcode/determinism
- **B hidden**: DDR5_TOP_1115 场景, KeyError('CONT'), missing={CONT,CT_M0,PVIA}, em_override.tech
- **自验**: reference 20/20 PASS, 3 negatives 全 FAIL
