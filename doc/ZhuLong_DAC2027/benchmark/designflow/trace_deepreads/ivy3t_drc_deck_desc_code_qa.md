# Deepread: ivy3t — DRC deck desc↔code numeric QA (kenwang@hfeg0plg16, mc=59)

## trace_source
- session_file: 1794707679075_ivy3t.messages.json
- user: kenwang / host: hfeg0plg16 / match_count: 59 (drc:278 calibre:214 dominant)
- 157 msgs, 5 typed user_inputs (1 task + 4 "go on"), tools: editor×33 read_files×28 run_approved_command×10

## 真实意图 (msg 0)
kenwang: "~/zl/4_5_52_Mxa.ev 文件，请帮我QA一下针对 rule 中的写法是否存在问题，尤其是检查 code 数值是否与description一致，如果有相同描述的请参照该文件 /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/Ref/ calibre_n7.drc calibre_n5.drc"
= QA a Calibre DRC rule deck (4_5_52_Mxa.ev, 1875 行, ~120 check blocks): check whether code numeric values match the description text, cross-reference n7/n5 decks.

## assistant 工作流 (gold)
1. read_files 读完整 .ev (1875 行，分多段补读)
2. 写 qa_45_52.py (editor 多次写入): 解析 check 块 (name/desc/code/行号) → 逐块提取 description 数值 vs code 数值双向比对 → 输出 qa_45_52_report.txt (1100 行, 4 PART: derived layers / desc-vs-code / 重复 / 可疑模式)
3. run_approved_command 跑 qa_45_52.py (shell-runner .sh 包装，python-runner 沙箱缺 encodings)
4. 写 dump_refs.py / dump_refs2.py: 从 n7/n5/35H deck 提取同名/同描述规则原文做裁决
5. 写 qa_45_52_final_report.md (12 确认问题 A1-A12 + B 类边界项)
6. 写 fix_45_52.py: 23 组带严格计数断言的精准替换 (任一不匹配即中止不写盘)，14/14 后置校验通过，块结构前后一致 (174 blocks)

## .ev 格式 (从 trace tool_result 提取，真实)
- 顶层派生层: `L19    M3_156_up = M3 WITH WIDTH >= 156` (BUG: 应 0.156)
- 检查块: `RULE_NAME { @ description ... code lines }`，多行 desc 用多个 @ 行
- QA report PART 0 列派生层 (L1..L19..)，PART 1/2/3/4 做 desc↔code 比对

## 确认的 12 类 bug (A1-A12, 用于 fixture 植入)
- A1 missing_decimal: `WIDTH >= 156` 应 `0.156` (L19 M3_156_up)
- A2 magnitude_10x: `< 0.505` 应 `0.0505` (L702 M3_R_18_1)
- A3 wrong_layer_name: `M3_NMINP_GRP_Region` 应 `M3_MINP_GRP_Region` (L270)
- A4 polarity_reversal: 密度 `> 0.125` 应 `< 0.125` (L396 M3_DN_1_1, 最小密度极性反)
- A5 wrong_window_dims: `30*30/4` 应 `40*40/4` (L397/L411)
- A6 wrong_layer: 检查 M4 应 M3 (L372 M3_L_1, M4 模块拷贝残留)
- A7 desc_code_value_swap: desc "[0.25 x 0.5]" 但 code `0.5 0.5` (L731 M3_R_19_RCM, 应 0.5 0.25)
- A8-A12: CS_19 ECX、CS_14 阈值、EN_31_3 GOOD、DN_9_1 阈值、EN_32/33/35_9 结构

## reframe (档B fixture-driven)
agent 写 `drc_deck_desc_code_audit.py`: 解析 .ev deck → 派生层 + 检查块 → 每块提取 @desc 数值 vs code 数值 → 分类 flag 7 种 mismatch (missing_decimal / magnitude_10x / polarity_reversal / wrong_window_dims / wrong_layer / desc_code_value_swap / value_mismatch) → 输出 JSON {deck_path, derived_layers, blocks, findings[{rule_name,line,mismatch_type,desc_value,code_value,severity,description}], summary}
check() 在 hidden B 上跑候选，断言结构 + 8 个植入 bug 全检出 + 5 clean 块无假阳 + 3-seed 确定 + 退化提交 FAIL

## 跨 shard / 同 domain 串台检查
- 4-shard ledger: ivy3t 仅 C (本 claim)
- 4-shard jsonl: 0 hit
- 同 domain 近邻 case 全正交:
  - DrcDeckQaScan-001 = typo/structural scan (REGIO/EXTENTS/empty block/operator name) ≠ intra-block desc↔code numeric
  - DrcDeckRuleQa-001 = update-diff QA (per-rule vs update_log) ≠ single-deck desc↔code
  - DrcDeckUpdateQa-001 = spec-vs-deck verdict ≠
  - DrcDeckValueCompare-001 = two-deck shrink-factor scaling ≠
  - DrcQaReportSummary-001 = parse QA report text ≠
  - DrcVsDrmRuleAudit-001 = DRM manual vs deck ≠
  - DrcDeckBlockReformat-001 = block→single-line format ≠
  - 子型 "drc_deck_desc_code_numeric_audit" 首例
