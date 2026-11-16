# Deepread — r690 xinqiaoz @ 10.129.2.11 session 1794311735311_4msuj

## Trace source
- user: xinqiaoz (PDK QA 工程师, G5_CIP 节点)
- host: 10.129.2.11
- session: 1794311735311_4msuj (mc=315, keywords: drc:5423/pdk:1136/calibre:690/lvs:35/.gds:24)
- date: 2026-11-10
- size: 877KB / 165 msgs / 7 user text turns / 49 editor + 21 read_files + 12 run_approved_command

## User real intent (verbatim from U#1)
> 我先描述问题：
> drcQa_G5_CIP_DECQA_v0d5_Rev12_weizhao_2026-11-10.report，这是问题出现的 report。注意第 78~80 行的报错，我下面以第 70 行的报错为例。
> 在 ldr 中，有 V1_ENC_007_00，V1_ENC_007_00_Auto 这两条 rule，在 DRC deck 中，也同样有这两条 rule。drc deck 中 V1_ENC_007_00 这条 rule 没有定义 variable，V1_ENC_007_00_Auto 定义了 variable _V1_ENC_007_00_AUTO_。
> 在最终的 report 中，有可能 V1_ENC_007_00 这条 ldr 误匹配到了 _V1_ENC_007_00_AUTO_ 这个 variable，导致最终报错。

## Assistant workflow (issue-handler 10 步流程)
- 步骤 1-2 (前置 + 目录结构): 创建 `DRC/issues/1110_zhaowei/` + 软链接到 `/home/pdk/weizhao/00_drc/G5_CIP/LP_QA`, 顶层 README.md
- 步骤 3 (理解 + 复述): 确认 report 关键内容 — 第 27 行 `drcValue fail`; 第 76-80 行 `[error]variable with unmatched value(variableValueUnmatchedCount=4)` 列出 `_AT4_WMAX_002_03_C_` (77), `_V1_ENC_007_00_AUTO_` (78), `_V2_ENC_007_00_AUTO_` (79), `_V3_ENC_007_00_AUTO_` (80)
- 步骤 4 (交叉验证 — KEY): LDR 侧 grep 确认 `V1_ENC_007_00` (LDR_RULE_0.256, -0.019) vs `V1_ENC_007_00_Auto` (LDR_AUTO_0.256, 0.012) 在不同 sheet, 不同值; deck 侧 `calibreDRC_LP6.rule-LPDRC_CHECK-preprocessed` 第 18091-18092 行 `//VARIABLE _V1_ENC_007_00_ 0.019` (注释) + `V1_ENC_007_00 { ... 硬编码 0.019 ... }`, 第 44425-44429 行 `#IFDEF DYT4E_AUTO_CHECK` 块内 `VARIABLE _V1_ENC_007_00_Auto_ 0.012` (有效) + `V1_ENC_007_00_Auto {`. 数值对账: LDR `V1_ENC_007_00_Auto`(0.012) = deck `_V1_ENC_007_00_Auto_`(0.012) → 本应匹配成功, 不该报错. 大小写线索: report `_V1_ENC_007_00_AUTO_` (全大写) vs deck `_V1_ENC_007_00_Auto_` (混合) → 匹配/报告环节有大小写归一化. **初步判断: 代码 bug (工具误报)**, 推断误匹配机制: 精确名 `_V1_ENC_007_00_` 因被注释不在有效 variable 集合 → 匹配逻辑回退到模糊匹配 (疑似前缀/包含式 + 大小写不敏感) → 误命中 `_V1_ENC_007_00_Auto_` → 用 LDR 值 -0.019 与 variable 值 0.012 比对不等 → 误报. V2/V3 同理.
- 步骤 5 (最小复现环境): `prepare_base.py --expand-rules` 构建base/ (27 文件, INCLUDE 改写为 base/ 内相对路径); `s1/config.ini` 最小化 (drc/ldr/prepOption/precision), 去掉 gds/fracture/powerList/ldf/Truth 等无关字段
- 步骤 6 (复现): `python DRC/DrcQa.py -c config.ini -ci drcValue` exit 0; **核心误报完全复现** — variableValueUnmatchedCount=4, `_V1/V2/V3_ENC_007_00_AUTO_` 全部存在. 唯一差异 unmatchedDrcCount 4→1 (工具版本 1.0.3→1.1.0, 与本 issue 无关). 一个插曲: 首次运行失败因 `DrcInfo.readDrc()` 按进程 cwd 解析 INCLUDE 相对路径 (DrcInfo.py:364-367) — 通过在 s1/ 内为 base/ 的 18 个 INCLUDE 子文件建符号链接解决
- 步骤 7 (handoff, 未执行): 定位代码入口 `DrcValueCheck.findTargetVariable()` (~270-350 行) → `compareLdrValueWithVariableValue` (:262 写入 variableValueUnmatched). HANDOFF 文档生成 `.handoffs/HANDOFF_1110_zhaowei_drcValue.md`

## Reframe plan — DrcVarMisMatchDiag-001 (mock-behavioral, physical_verify, L1)
- 新子型 `drc-var-mismatch-prefix-collision-diagnose`, **C 域首例 PDK-QA-误报-根因-诊断器** (diagnose existing report, 非 generate/translate/validate/classify)
- 真实交付路径依赖私有 PDK 文件 (`/home/pdk/xinqiaoz/01_dummy/G5_CIP_DRCOA/`, `/home/pdk/weizhao/00_drc/G5_CIP/LP_QA`) 不可入沙盒 → reframe 为纯 stdlib 诊断器
- 输入三件: ldr_A.tsv (rule_name/sheet/value) + deck_A.svrf (含 `VARIABLE _x_ v` 有效 / `//VARIABLE _x_ v` 注释 / `rule_name {` 定义) + report_A.txt (含 `[error]variable with unmatched value(variableValueUnmatchedCount=N)` 段落 + 缩进 `_xxx_` 行)
- 输出 JSON: summary + findings 列表, 每个 unmatched variable 分类为 `collision_false_match` (case-insensitive 精确匹配存在且值一致, 但工具的前缀回退把另一条 LDR rule 误配 → 误报) / `true_mismatch` (精确匹配 + 有效 deck var + 值确不等) / `no_ldr_entry` (无 LDR 对应)
- 关键诊断字段: `intended_rule` (应匹配的 LDR rule) / `mismatched_rule` (被前缀误配的 LDR rule) / `ldr_value` / `deck_variable_value` / `deck_variable_effective` / `recommended_fix`
- asset A: V1/V2/V3_ENC_007_00 同族 prefix-collision (3 collision_false_match) + AT4_WMAX_002_03_C true_mismatch (deck 0.6 ≠ LDR 0.5)
- hidden B (anti-hardcode 全异 rule 家族): N1/N2_WMIN_005 同族 prefix-collision (2 collision_false_match) + K1_AREA_009_D true_mismatch (deck 0.55 ≠ LDR 0.42)
- hidden B2 (退化干净): Q1_WIDTH_001 / Q2_SPACING_002 全部有效匹配, 0 unmatched
- check() 16 条件 a-p (zip+compile / B exit0 / JSON shape / 4 summary 计数 / N1_WMIN_005_AUTO 分类+字段+值+fix / K1_AREA_009_D true_mismatch 字段+值 / B2 退化 / 确定性)
- 3 negatives (empty_shell/print/no_core_logic) — distinct first-fail (e/d/f) ≥3
- distinct vs r688 SvrfPvrsConvert (SVRF→PVRS 翻译) / r687 DrcPgOpenRuleGen (spec→SVRF 生成) / r685 AutoCellTclFlowValidate (校验既有 TCL) / r682 DrcEnclosureRuleExtract (deck 规则分类) — 本例 **诊断既有 report 的误报根因**, 核心差异 = diagnose vs generate/translate/validate/classify
