# 深读笔记 — 1791944811866_cv0pc (miccao @ hfeg0pkn36 / 10.129.32.47)

- **session**: 1791944811866_cv0pc · user miccao · host hfeg0pkn36 (10.129.32.47)
- **meta**: status=completed exit_code=0, terminal_marker=failed_external_process_exit (stale_session_reconciler), 318 msgs (164 user / 154 assistant), 22.9M input tokens, model deepseek-v4-flash, agent=lead, cwd /home/miccao/work/shell/tmp, started 2026-10-14 02:26, ended 2026-10-19 09:14
- **keywords** (mc30 scan): calibre:554 ; .gds:55 ; pdk:43 ; gdsii:31 ; aether:8 ; netlist:7 ; lib.defs:6 ; cmos:4 → 强 physical_verify 信号
- **prompt (msg[0])**: `[calibre-drc-log-analysis] /rundata/trgqx/V0/ver/lvs/hongfeil/calibreversion/ta4/argus/test/argusDRC.log分析这个log，报告放到对应位置`

## 对话流（5 个用户意图轮）

1. **msg[0]** (primary): 分析 argusDRC.log，报告放到对应位置
   - argusDRC.log = Empyrean Argus DRC 2026.06 格式（agent 明确 noted "different from Calibre DRC-H"），308931 行 ~20MB
   - agent 工具链: list_allowed_files → editor 写 drc_overview.py/drc_summary.py/drc_head.py/drc_tail.py/drc_pat.py/drc_block.py/drc_usetime.py/drc_ops.py/drc_rules.py/drc_connects.py/drc_layout.py/drc_report.py → run_approved_command (profile=python-runner) → read_files → editor 写 argusDRC.log.analysis.md → copy_report.py 拷到目标目录
   - 提取字段: TOTAL REAL TIME=7747s, TOTAL CPU TIME=268270, CPU CORE=64, PEAK MEM=192701M, RuleChecks=2560, Results=34027, 12401 operations, 264 CONNECT statements, category breakdown (DRC 36.8% / EDGE_TOPOLOGICAL 17.9% / EDGE_MEASUREMENT 10.7% / BOOLEAN_2 9.8%), top ops by USE TIME
   - **交付**: /rundata/.../argus/test/argusDRC.log.analysis.md (18.5KB / 228 行) — 用户未拒绝，msg[78] 转新任务 → 接受
   - **重叠**: 与既有 `DrcLogAnalyzer-001` (r176, Calibre DRC-H log → header/modules/connects/top_ops/vhc/huge_cells/source_layers/rulechecks) + `DrcLogHugeCellOverlap-001` (volume_proxy + overlap_candidates) 高度重叠 → **不取此轮做 case**

2. **msg[78]** (rundrc.log): 分析第二个更重的 log + 与上次对比
   - rundrc.log = Argus 2025.06.sp1.hf9, 247760s (~68.8h), 165151 results, 同 layout 53.8G, 2560 rules
   - agent 跑 n_summary/n_meta/n_block/n_ops/n_conn/n_deck.py，生成 rundrc.log.analysis.md (20.5KB/272 行) 拷到 argus/ 目录
   - **重叠**: 同 DRC log 分析 → 不取

3. **msg[130]** (deck 对比): "deck 相同吗?" ← **本 case 选用此轮**
   - agent 工具链: cmp_deck.py (SELECT RULE 选集对比) → deck_diff.py/deck_diff2.py (整体 diff) → deck_diff3.py (**RULE 块感知** 对比) → deck_full.py → deck_multiset.py (header 多重集对比) → deck_set.py (逐设置核对)
   - **真实 deck 格式** (from deck_diff3.py 解析):
     - rule block regex: `^RULE\s+(\S+)\s*\{`  (块体到 `}`)
     - deck A = test/.__argus.rule__ (36308 行, 2700 rules, 无 layout_input — 由 wrapper .calibreDRC.rule.use_db 提供)
     - deck B = argus/argus.rule (36312 行, 2700 rules, 自带 layout_input)
     - **rule 对比结果**: common=2700, unique_A=0, unique_B=0, body_diffs=0 (2700 rules 全部 body 逐行一致)
   - **header 多重集对比** (deck_multiset.py, Counter of non-empty stripped lines):
     - lines only in A (test, 4): `drc_result ( db "WOWTOP_Die1.drc.results" text_format )`, `drc_summary ( "WOWTOP_Die1.drc.summary" by_cell )`, `drc_max_vertex ( 199 )`, `drc_output_cell_name ( yes cell_coordinate transform_to_top all )`
     - lines only in B (argus.rule, 6): `drc_result ( db "drc.results" text_format )`, `drc_max_vertex ( 4096 )`, `drc_output_cell_name ( yes cell_coordinate transform_to_top )`, `drc_summary ( "drc.summary" overwrite by_cell )`, `virtual_connect ( report_warning yes unsatisfied )`, `virtual_connect ( report_max all )`
   - **关键设置差异** (deck_set.py):
     - `drc_max_vertex`: A=199, B=4096
     - `virtual_connect`: A 2 条 (colon no, name ?), B 4 条 (colon no, report_warning yes unsatisfied, report_max all, name ?)
     - `drc_result`: A "WOWTOP_Die1.drc.results", B "drc.results"
     - `drc_summary`: A "WOWTOP_Die1.drc.summary" by_cell, B "drc.summary" overwrite by_cell
     - `drc_output_cell_name`: A 带 "all" 后缀, B 不带
     - `layout_input`: 仅 B 有 (A 由 wrapper 提供)
   - **agent 结论** (msg[174]): "规则 deck 完全一致，但两次运行的 control/IO 设置不同" — 2700 rules body 逐行一致, 仅 10 条 header control 行不同
   - **DISTINCT**: 与 `LvsDeckCmp-001` (difflib hunks / LVS deck / #DECRYPT filter) 不同 — 本任务是 RULE-块感知的结构等价审计 (rule name 集合 + body 逐行 diff + header 多重集 diff + verdict 分类); 与 `DRCSFCompare-001` (变量缩放对比) 不同; 与 `DRCKDeckOpt-001` (deck 优化器) 不同 — 本任务只做对比不改 deck

4. **msg[176]** (huge cell + skill 更新): skill 是否覆盖 huge cell? → 加 huge cell 清单到报告模块三 + 更新 SKILL.md
   - 22 huge cells (instance≥1M 或 polygon≥100k) 从 ARGUS LAYOUT INPUT INFORMATION 段抽取
   - **重叠**: DrcLogHugeCellOverlap-001 已覆盖 → 不取

5. **msg[232]** (面积相近+重叠 cell): 找面积相近且重叠的两 cell → GDS bbox 提取 (57.78G GDS, 单趟扫描被 SIGKILL 超时) + log 代理候选
   - **重叠**: DrcLogHugeCellOverlap-001 (volume_proxy + overlap_candidates) 已覆盖 → 不取

## 选用与合成

- **选用轮**: msg[130] deck 等价对比 — 唯一与既有 case 不重叠的子任务
- **不取 A-档**: msg[130] 是用户"已指出根因"式追问 ("deck 相同吗?") 而非"提出需求"轮; 且 session terminal_marker=failed_external_process_exit, 无用户明确接受 deck 对比最终产物 → 取 **B-档 synthesized**, grounded on 真实 deck 格式 (RULE block regex / header control 行语法 / multiset diff 方法 / 三类 verdict)
- **合成任务**: "Argus DRC rule deck 结构等价审计器" — SUT 写 argus_deck_equiv_audit.py, CLI 2 参 (<deck_a> <deck_b>), 解析两 deck 的 RULE 块 (regex `^RULE\s+(\S+)\s*\{`), 算 rule 名集合交集/差集, 对 common rules 逐行比 body, 对非 rule 行做 multiset diff, 输出 JSON {rule_counts, common_rules, unique_to_a, unique_to_b, body_diffs, header_diffs, rules_identical, headers_identical, verdict}
- **verdict 语义** (grounded on agent 结论):
  - rules_identical = (no unique) AND (body_diffs==0)
  - headers_identical = (header_diffs 全空)
  - verdict = "identical" (both) | "rule_equivalent_header_diff" (rules 同 + header 不同) | "different" (rules 不同)
- **资产 A** (visible): deck_A1.rule (full deck, 带 layout_input + drc_max_vertex=4096 + 4 条 virtual_connect + 5 RULE R1-R5) vs deck_A2.rule (test/wrapped 版, 无 layout_input + drc_max_vertex=199 + 2 条 virtual_connect + 同 5 RULE R1-R5 body 一致) → A1 vs A2 = rule_equivalent_header_diff (镜像真实 trace: argus.rule vs test/.__argus.rule__)
- **隐藏 B**: deck_B1.rule (6 RULE S1-S5 + S5_unique, header drc_max_vertex=8192) vs deck_B2.rule (5 RULE S1,S2_modified,S3,S4,S6_unique, header drc_max_vertex=2048) → B1 vs B2 = different (common S1-S4, unique B1=S5, unique B2=S6, body_diff S2, header diff drc_max_vertex) — 全重参数化 (rule 名 S vs A 的 R, header 值全异) 击穿硬编码 A
- **B-broken**: deck_B_broken.rule (不平衡大括号 / 0 RULE 块) → 优雅报错
- **判分**: 16 条 ①–⑯ a–p, 对 B 跑候选 + cross-input guard A + B-broken 哨兵

## 去重核对

- DISTINCT from `DrcLogAnalyzer-001` (log 解析, 非 deck 对比)
- DISTINCT from `DrcLogHugeCellOverlap-001` (cell 体积/重叠, 非 deck 对比)
- DISTINCT from `LvsDeckCmp-001` (LVS deck + difflib hunks + #DECRYPT; 本 case 是 DRC deck + RULE 块感知 + multiset header diff + verdict 分类)
- DISTINCT from `DRCSFCompare-001` (变量缩放对比; 本 case 是结构等价对比)
- DISTINCT from `DRCKDeckOpt-001` / `DRCDeckOpt-001` (deck 优化器改 deck; 本 case 只对比不改)
- DISTINCT from `DeckIncludeResolve-001` (#DEFINE 解析; 本 case 是 rule 块等价)
- DISTINCT from `DRCDeckSyncPlan-001` (文件同步; 本 case 是内容等价)
