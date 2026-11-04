# Trace Deep-Read: 8qjr2 — DRC Pattern Check pair/waive classification

- **session**: 1789540996998_8qjr2 (xinqiaoz @ hfeg0pkn004/10.129.2.13, hfeg0plg76/10.129.8.124)
- **match_count**: 325 (keywords calibre:764; pdk:693; .gds:88; virtuoso:10; tools 403 calibre)
- **agent**: lead, 227 msgs, 1.2 MB
- **domain**: physical_verify (PDK_QA DRC pattern check tool development)
- **path note**: cline v3 nested session dirs — file at `sessions/<sid>/<sid>.messages.json` (NOT flat). 10-28 summary.tsv used flat path; all "GONE" re-checks were wrong until nested path used.

## User intent (verbatim, A-档 seed evaluation)

- **USER#0** (seed, 提出目标): 「阅读 home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/0915_drc_pattern_check_handover.md 这份对话交接文档。了解背景、需求、当前的状态。」— comprehension/orientation on DrcPatternCheck Good/Bad 拆分改造。
- **USER#6**: 询问旧 vs 新执行流程、新增/修改步骤（理解类，给方向）。
- **USER#19**: 询问两个 fallback 作用 + good/bad 共享语义（理解类）。
- **USER#49** (gives root-cause + fix direction → NOT A-档 seed, is hint): 「good/bad cell 是成对出现的…允许 {"rule1":[cell_a_P,cell_a_F]},{"rule2":[cell_a_P,cell_a_F]}」(pair-sharing constraint).
- **USER#53**: 「请修改，修改之前必须做好代码的备份」(执行类).
- **USER#89** (gives root-cause + fix → hint, not seed): 「新的 check 会把 pass 和 failed & waive 混到一起，都叫 pass。完全丢弃了 waive 的属性。我们需要区分。」(3-tier waive distinction — the core bug fix).
- **USER#129–157**: 代码理解类（checkDrc 作用、drc2cell vs drc2cellPair、round1/round2、runCalibreForCell 返回值 → USER#157「去掉返回值」).
- **USER#201** (final): 「把这个会话中的东西提炼出来再回写到这个交接文档…核对文档和代码一致」(doc update).

## Assistant tool chain

read_files + run_approved_command(profile system) + editor. Edits target `DRC/pattern/DrcPatternCheck.py` (563 insertions / 232 deletions). Backup before edit (`.tmp/DrcPatternCheck.py.bak_*`). py_compile after each edit. Stages:
1. 读交接文档 → 提取旧 checkDrc 流程.
2. 实现 pair-based fallback (USER#49): bad/good 同 base 配对，共享 OK，不混配.
3. 修复 waive 丢失 (USER#89): 新增 CHECK2/CHECK3 calibre geometry/reference 比对；ruleResults 三档 {pass, failed, waive}；waivedRules 单独列出.
4. 去掉 runCalibreForCell Boolean 返回值 (USER#157).
5. 回写交接文档 (USER#201).

## Gold & A-档 qualification

gold = 修改后的 `DrcPatternCheck.py` + 更新的 `0915_drc_pattern_check_handover.md`，依赖 live PDK_QA 代码库 (/home/xinqiaoz/PDK_QA，内网) + live calibre → **.75 沙盒不可达 → A-档 disqualified (tooling)** → **B-档 synthesized L1-boundary**（纯离线 manifest→分类器生成）。

## B-档 synthesis (EDA-Eval-DesignFlow-DrcPairWaiveClassify-001)

把 DrcPatternCheck 的核心逻辑固化为自包含分类器 `drc_pair_waive_classify.py`：读 pattern_rules.json (rules + cells) + calibre_results.json (per-cell CHECK1/2/3) → 配对约束校验 (base 一致 + type 正确 + 共享 OK + 不混配) → 三档分类 (pass/failed/waive，waive 不并入 pass) + pattern_not_found → pattern_check_report.json。与 r73 DdgoaDeviceAudit / r76 MVVarNamingAudit / r79 DRCDeckSyncPlan / r80 DRCSpecGen / r81 MVValueCmp / r86 DRCReportIpAudit / r84 FillImplantFlowAudit / **DrcPatCheckAudit-001**(matchKey+layerMap audit) 正交——本案是**配对约束 + 三档 waive 分类 + CHECK1/2/3 执行引擎**（生成类，非审计）。
