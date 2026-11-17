# Deep-read + Synthesis Plan: dse5n — Low-Power Flow Plan Analyze (revived under 11-15 new standards)

**Session**: 1793004375421_dse5n · **User**: e0046913 · **Host**: hfeg0pkn003 · **Date**: ~2026-10-26
**Domain**: eda_other (digital mid-flow / low-power flow planning) · **Track**: A-faithful (C-A Q&A)
**Ledger status**: was parked (旧判 "Q&A unfit / 无交付物" under old weak filter) → **REVIVED** under 2026-11-15 用户令 (analysis-Q&A / flow-planning = real user intent)
**Deepread rounds**: r686 (本轮, 全量深读 + evidence 锚点逐条核验 + A 资产落盘 4/7)

## 1. User verbatim (A-档, trace-faithful, U#0)
> 我是一名数字芯片中端flow工程师，希望从零搭建一个low power flow全流程。以下是我的想法细节：1.我想参考/apps/imctf/cad/script/digital_flow/feint 目录下的dc、fm、pt 流程化脚本设置方案（这些脚本是参考基础）；2.我并不够了解low power flow具体在数字流程中的哪些环节、使用哪些工具，但我知道这同时设计到前端、中端、后端的流程，请详细告诉我其中的流程细节与对应工具；3.我可以自己负责中端相关流程的low power适配（比如：适配到syn、formal、sta），但是前端和后端的相关适配可能需要他人来协作完成。如果我作为总指挥官，我需要和前端、后端做low power flow的同事们重点对齐哪些细节？（比如：交付件版本、格式）我该如何指挥、推进这项工作？

**A-档判定**: CLEAN ✓ — 纯需求轮（给目标 + 真实参考脚本路径，未给根因/修复/答案）。真实用户意图 = 分析-Q&A / flow-planning（按 11-15 新标准 = 合法任务）。

## 2. Assistant work (14 msgs, 246KB trace)
1. list_allowed_files 探查 feint 目录 → 存在 + 有 pwr_setup.tcl
2. read_files: Makefile, dc.tcl, fm.tcl, pt.tcl, common_setup.tcl, pwr_setup.tcl (真实可读资产)
3. search_codebase: UPF/golden/power_domain/isolation/level_shifter/retention 关键词
4. 补读 dc.tcl L330-560/L920-1238, fm.tcl L60-205/L140-205, pt.tcl power 段
5. 产 9101-char 完整分析 (#13)：feint baseline low-power 现状 → low power flow 全景(前/中/后端) → 总指挥对齐 checklist

## 3. Evidence 锚点逐条核验 (本轮在 .75 上读真实 feint 脚本确认)

所有 assistant 主张均在真实 feint 脚本中逐行验证通过：

| assistant 主张 | 真实脚本证据 | 核验 |
|---|---|---|
| common_setup.tcl UPF_MODE = none\|prime\|golden | `set UPF_MODE none ;# prime \| golden \| none` (common_setup.tcl) | ✓ |
| UPF_FILE / DCRM_MV_SET_VOLTAGE_INPUT_FILE 变量已存在 | `set UPF_FILE ""` / `set DCRM_MV_SET_VOLTAGE_INPUT_FILE ""` | ✓ |
| DC golden: set_app_var enable_golden_upf true | dc.tcl L48 | ✓ |
| DC load_upf -strict_check true (golden) | dc.tcl L351-358 | ✓ |
| DC save_upf -include_supply_exceptions -supplemental | dc.tcl L1216-1218 | ✓ |
| DC MV 三层库 + set_multi_vth_constraint -lvth_percentage | dc.tcl L287 + common_setup TARGET_LIBRARY_FILES (lvt/ulvt) | ✓ |
| DC check_mv_design -power_nets | dc.tcl L406-414 | ✓ |
| DC golden 输出 ${DESIGN_NAME}.mapped.pg.v | dc.tcl L1208-1209 `write_file -format verilog -hierarchy -pg -output .../${DESIGN_NAME}.mapped.pg.v` | ✓ |
| FM 双读: 参考 load_upf -r (golden) + 实现 load_upf -i -target -supplemental | fm.tcl L147-148, L216-226 | ✓ |
| FM retention register 模型替换注释 | fm.tcl L130-137 | ✓ |
| FM verification_force_upf_supplies_on false (注释) | fm.tcl L262 | ✓ |
| PT read_vcd -rtl / SAIF 活动因子标注 | pt.tcl L373-375 | ✓ |
| PT report_switching_activity -list_not_annotated | pt.tcl L377, L385 | ✓ |
| PT report_power / update_power / check_power | pt.tcl L396-400 | ✓ |
| PT fix_eco_power (leakage ECO, 注释) | pt.tcl L488 | ✓ |
| PT power_enable_multi_rail_analysis | pt.tcl L128 | ✓ |
| pwr_setup.tcl = PTPX 专用骨架 | pwr_setup.tcl (PT power vars) | ✓ |
| lec_dofile = Cadence LEC 第二条等价性路线 | feint/scripts/lec_dofile 存在 | ✓ |
| Makefile MODULE_SYN=ds/dc/2023.12-SP5, MODULE_FM=ds/fm/2023.12-SP5, MODULE_PA=ds/pt/2022.12-SP5 | Makefile | ✓ |
| Makefile PT_CORNER=tt0p8v25c, targets dc_syn/fm_r2g/fm_g2g/fm_r2r/sta-pa | Makefile | ✓ |

## 4. Case design (LowPowerFlowPlanAnalyze-001, C-A analysis-Q&A 模板, 待 r687 合成)

- **task_id**: EDA-Eval-DesignFlow-LowPowerFlowPlanAnalyze-001
- **domain**: eda_other
- **source-type**: C-A (trace-faithful A-档 Q&A, 真实参考脚本作 evidence anchor)
- **Deliverable**: `outputs/submit.zip` 含 `low_power_flow_analysis_report.json` (报告 only, 不要求脚本)
- **A 资产 (SUT 可见)**: feint/ 真实树 (Makefile + scripts/{dc,fm,pt}.tcl + setup/{common_setup,pwr_setup,hl22_syn_dont_use}.tcl) — trace-verbatim, 本轮已落盘 4/7 (dc.tcl/fm.tcl/pt.tcl/hl22), 待补 Makefile/common_setup.tcl/pwr_setup.tcl (内容已在 .75 workdir + 本轮 tool-output, r687 重拉即可)
- **B 隐藏变体 (check 跑 B, 不进 SUT 沙箱)**: feint_B/ 同结构 ≥10 维全异 (anti-hardcode):
  - UPF_MODE: none → prime (common_setup)
  - UPF_FILE: "" → "power/upf/top.upf"
  - LOWEST_VTH_PERCENTAGE: 30 → 20
  - PT_POWER_ANALYSIS_MODE: averaged → time_based
  - PT_DEFAULT_TOGGLE_RATE: 0.1 → 0.2
  - PT_CORNER: tt0p8v25c → ss0p72vm40c (Makefile)
  - OPTIMIZATION_FLOW: none → hplp
  - DFT_CONFIGURATION: SCAN → TP_SCAN
  - leakage_pattern_priority_list: "" → "HVT NVT LVT" (pt.tcl)
  - FM_MODE default: rtl2gate → gate2gate (Makefile)
  - MODULE_PA: ds/pt/2022.12-SP5 → ds/pt/2023.12-SP2
- **参考解**: 候选读 feint 树 → 产 `low_power_flow_analysis_report.json` (baseline + flow_overview + alignment_checklist + reasoning + evidence + summary + conclusion)
- **check.py (≥8 条, 目标 k=16, 跑 B)**: 模板照 SocProjStructAnalyze-001-v2 (reference/EDA-Eval-DesignFlow-SocProjStructAnalyze-001-v2/check.py)
  - (a) report 合法 JSON 含全部必需 key
  - (b)-(l) content-correctness: baseline.upf_mode/upf_file/lowest_vth_percentage/dc_load_upf_strict_check/fm_impl_upf_mode/pt_power_mode/pt_toggle_rate/pt_corner/leakage_pattern/optimization_flow/dft_config/module_versions 各对 A_EXPECT 真值 (从 A 真实脚本导出)
  - (m) flow_overview 列三中端工具 dc/fm/pt + 前端(UPF authoring) + 后端(PR PG-aware, IR drop)
  - (n) alignment_checklist ≥3 项聚焦交付件版本/格式 (UPF 版本, pg.v netlist, SAIF/VCD activity, supplement.upf)
  - (o) evidence-verification: evidence ≥5 项 {claim,source,token}, token 为所引 A 文件原文真实子串, 覆盖 UPF_MODE + dc load_upf + fm dual read + pt power + Makefile module
  - (p) B judge-self-check: 内嵌 _parse_feint_baseline(B_dir) 独立解析 B 真实脚本 → B_EXPECT, 与 report A 值 ≥6 维不同 (反硬编 A)
  - (q) 3-seed: 打乱 B 文件解析顺序, parser 输出稳定, sha256 三 seed 一致
- **negatives (≥4, 全 FAIL)**: neg_naive(空 report), neg_print_expected(硬编 A golden/none/0.1/30 → 被 (p) B-self-check + (b)-(l) B 值拦截), neg_stub(键对值错), neg_core_deleted(缺 baseline 段)
- **§4.9 三假**: empty_shell / print_expected / core_deleted 全 FAIL

## 5. 自验计划 (r687)
1. 补齐 A 资产 3 文件 (Makefile/common_setup.tcl/pwr_setup.tcl, 内容已在本轮 tool-output, 或 .75 workdir feint_scripts/ 重拉)
2. 生成 B 隐藏变体 (python 脚本对 A 文件做 ≥10 处替换, 写 hidden/feint_B/)
3. 写 reference report (按 A 真值)
4. 写 check.py (照 SocProjStruct-v2 模板, 内嵌 _parse_feint_baseline + A_EXPECT/B_EXPECT)
5. 写 4 negatives + negative_selftest.py
6. 自验: ref 16/16 PASS + 4 neg 全 FAIL + §4.9 三假全 FAIL + e2e jsonl test==disk round-trip
7. 追加 EDA-Eval-DesignFlow_A.jsonl

## 6. 台账动作
- r686: claim dse5n (从 parked 复活, 旧 weak 筛子作废)
- r687: 出完 case → mark --session 1793004375421_dse5n --status case --case-id EDA-Eval-DesignFlow-LowPowerFlowPlanAnalyze-001

## 7. 真实性溯源
- user: e0046913 (原值, 不脱敏)
- host: hfeg0pkn003
- session_file: 1793004375421_dse5n.messages.json
- match_count: n/a (reaudit 复活候选, 旧 summary mc 列 n/a)
- real_task_summary: 数字中端 flow 工程师从零搭建 low power flow, 参考 feint dc/fm/pt 脚本, 问流程细节/工具/前后端对齐/总指挥推进

## 8. r687 兑现记录 (单轮闭环, A.jsonl 350->351)
- eda_flow open_session 重拉 .75 feint/ 3 文件, A 资产 7/7 全落盘。
- hidden/feint_B/ 由 _gen_b.py 生成 (11 处精确替换, 7 文件全复制)。
- check.py k=18 (a-r) 写完, 内嵌 _parse_feint_baseline 反硬编 + 3-seed。
- reference report 17 keys + 16 evidence 全 verbatim A 子串 (16/16 OK)。
- 4 negatives + negative_selftest.py: 全 FAIL distinct labels {a,c,p,q}; §4.9 三假全 FAIL。
- A.jsonl 350->351, disk round-trip OK。trace_ledger_A.tsv dse5n 行 parked->case。
- 状态: DEBT 1 兑现, case 入库 EDA-Eval-DesignFlow-LowPowerFlowPlanAnalyze-001。
