# Deepread — sid 1789892841041_i4c8d (xinqiaoz @ hfeg0plg76, mc=321)

- **session**: `/home/xinqiaoz/.cline/data/sessions/1789892841041_i4c8d/1789892841041_i4c8d.messages.json` (1.12MB, 206 msgs, 112 user / 94 assistant)
- **host**: hfeg0plg76 (=10.129.8.124); user xinqiaoz; cline v3 nested dir layout
- **tools used**: read_files 34, run_approved_command 31 (profile-based: git_log/status/diff_pdkqa, py_compile_pdkqa, shell_generic_pdkqa), editor 29, search_codebase 2, skills 1 (handoff)
- **keywords**: pdk:714; calibre:414; .gds:113; virtuoso:9 → **physical_verify** (PDK QA DRC pattern check on calibre)
- **codebase**: `/home/xinqiaoz/PDK_QA/pdkQaSystem/DRC/pattern/DrcPatternCheck.py` (live, intranet-only, NOT reachable from .75 sandbox)

## 用户意图流（逐字原文，仅 key/token 掩码）

- **USER#1 @msg0** (handoff seed): 「请使用 handoff 技能，从以下交接文档恢复上下文并继续之前的工作：/home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/HANDOFF_drc_pattern_check.md」
- USER#2 @msg25: 「1. 917 第二轮验证结果通过 2. STI_F_01_V1~V4 根因是 cell 未拆分成 _F, _P。非代码问题，代码不改。3. writeWaiveDrcFile 中只需要参数化 opc1,opc2 的层号 4. 暂时不提交更改」(给状态+约束=hint 不进 prompt)
- USER#3 @msg40: report 对比，问 patternNotFound 表格打印变长 (给根因=hint)
- USER#4 @msg68: 「先确认一下，我们当前会在表格中显示哪些状态。哪些状态不显示？这些状态都是什么意思？」(澄清=hint)
- USER#5 @msg72: 「暂时先把 patternNotFound 改成类似 skip 的紧凑列表。另外 unusedCellCount 是什么？waviedCount 顺序放在 passCount 后面」(给修复=hint)
- **USER#6 @msg91 (A-档 seed, 提出目标未给根因/修复)**: 「好的，接下来我有一个需求，我们需要同时支持原来的无 _F/_P，无 good_/bad_ 的 cell 名称，作为匹配时的兜底机制。以避免版本切换带来的一系列问题。你先不要修改代码，我们先讨论一下。你觉得这个需求是怎样的？你理解吗？你觉得这里应该怎么去改？改动量如何？」
- USER#7 @msg113: 给出 3 点修复方案 (收集旧式 cell + Step 5 兜底 + goodExisting 默认值, ~10-15 行) = **hint 不进 prompt**
- USER#8-10 @msg115-121: 评估可行性 / report 是否改 / 旧 cell 检查哪些问题 (澄清=hint)
- USER#11 @msg134: 「你先实现一版吧。实现之前先备份代码到 .tmp 目录」(指令=hint)
- USER#12 @msg154: 「drcQa_TSI_TSI2.0b1..._drcWithPattern 第 379~381 行 3 个 TSV_S_03_ 开头的 rule 没找到 cell。通过查看 gds 发现其实有的，3 条 rule 对应一个 cell 名叫 TSV_S_03」= **根因 hint 不进 prompt**
- USER#13 @msg176: 「ruleId：TSV_S_03_ICT, TSV_S_03_IM0, TSV_S_03_ISC; cell name: TSV_S_03_F, TSV_S_03_P。你的方案有考虑到吗？」(给复杂场景=hint)
- USER#14 @msg178: 「1. 这个限制不做调整 2. 请修复问题，在 Step 5 legacy fallback 中增加前缀兜底，把这些 rule 再捞回来 3. 修复之前仍然先做备份」= **修复指令 hint**
- **USER#15 @msg193 (最终用户接受)**: 「测试完了，没有问题，当前这个需求的开发基本是落地了。我们再回头看初始的文档：/home/xinqiaoz/PDK_QA/pdkQaSystem/docs/proposals/01_drc_pattern_check_good_bad_split.md。这个文档在我们代码的多轮迭代过程中很多描述已经不准确了，需求甚至也有变更。因此请根据我们的代码，反过来再更新一下文档。」

## assistant 工具链 / 实现要点

1. handoff skill 恢复上下文 → read_files 读取 DrcPatternCheck.py / HANDOFF_drc_pattern_check.md / 交接文档
2. 讨论阶段 (USER#6-8): read_files 完整读取 getTargetCellPair / getTargetCellName / getTargetCellNameOri / parsePatternCell / buildCellsByBase / checkDrcRuleByCell / checkDrcRuleByCell_Round2 / writeBadCellCheck / runCalibreForCell
3. 实现 (editor 7 次改 DrcPatternCheck.py):
   - **editor#3 @msg141**: `check()` 里 buildCellsByBase 之后收集 legacy cells:
     ```python
     self.legacyCellList = []
     self.legacyCellUpperListInfo = {}
     for cellName in gdsCellList:
         if not self.parsePatternCell(cellName):
             self.legacyCellList.append(cellName)
             self.legacyCellUpperListInfo[cellName.upper()] = cellName
     ```
   - **editor#4 @msg141**: `getTargetCellPair` Step 5 兜底 (在 return None,None 之前):
     ```python
     # Step 5: Legacy fallback
     legacyCell = self.getTargetCellName(ruleName, self.legacyCellList, self.legacyCellUpperListInfo)
     if legacyCell:
         return legacyCell, None
     return None, None
     ```
   - **editor#5 @msg141**: `checkDrcRuleByCell` 允许 goodCell=None (legacy bad-only): `if not badCell: patternNotFound; return`; `if not badCell and not goodCell: patternNotFound; return`
   - **editor#6 @msg141**: goodExisting 默认 0 (CHECK1/CHECK2 不检查=不 fail) for legacy bad-only:
     ```python
     goodExisting = 0       # CHECK1: after waive (0 = no good cell, not checked)
     goodExistingRaw = 0    # CHECK2: before waive
     ```
   - **editor#7 @msg185 (USER#14 修复)**: Step 5b legacy prefix fallback:
     ```python
     # Step 5b: cell name is a prefix of rule name, e.g. rule="TSV_S_03_ICT", cell="TSV_S_03"
     ruleUpperForPrefix = ruleUpper
     if ruleUpperForPrefix.endswith("_C") or ruleUpperForPrefix.endswith("_P"):
         ruleUpperForPrefix = ruleUpperForPrefix[:-2]
     legacyMatched = []
     for cellName in self.legacyCellList:
         cellUpper = cellName.upper()
         if ruleUpperForPrefix.startswith(cellUpper) and self.charCountMatchGap(ruleName, cellName):
             legacyMatched.append(cellName)
     if len(legacyMatched) == 1:
         return legacyMatched[0], None
     return None, None
     ```
   - **editor#1-2 @msg75-79**: report 改 patternNotFound 为紧凑列表 (`splitString.join`), waivedCount 放 passCount 后, 加 unusedCellCount
4. 验证: py_compile + git_diff + run_approved_command (profile shell_generic_pdkqa 跑 case 对比 report) + USER#15 测试通过
5. 收尾: read proposal doc → editor 更新 01_drc_pattern_check_good_bad_split.md 反映代码

## gold 依赖 → A/B 档判定

- gold 依赖 **live PDK_QA 代码库** (`/home/xinqiaoz/PDK_QA`, 内网) + **live calibre** (经 profile shell_generic_pdkqa) → **.75 沙盒不可达** → **A-档 disqualified (tooling)** → **B-档 synthesized L1-boundary** (纯离线 manifest → legacy fallback matcher 生成)
- 真实意图 (A-档 seed): USER#6 逐字「我们需要同时支持原来的无 _F/_P，无 good_/bad_ 的 cell 名称，作为匹配时的兜底机制」—— 提出目标，未给根因/修复 → 合格 seed

## 合成方向（与存量 case 正交）

- **核心**: legacy cell 名兜底匹配 + Step 5b 前缀兜底 + goodExisting 默认 0 + matchType 分类 (new_pair / legacy_bad_only / patternNotFound) + 紧凑 patternNotFound 列表
- **正交性**:
  - r94 DrcPatCheckAudit (matchKey+layerMap 审计) — 审计类, 不重叠
  - r96 DrcPairWaiveClassify (配对约束 + 三档 waive 分类 + CHECK1/2/3 执行引擎) — 配对/waive 类, 本案是 legacy 兜底匹配类
  - r80 DRCSpecGen (spec→SVRF 生成), r81 MVValueCmp (值比对) — 不同域
- **case_id**: EDA-Eval-DesignFlow-DrcLegacyFallback-001 (physical_verify, B-档 synthesized, L1-boundary, 生成类)
- **候选**: `legacy_fallback_matcher.py` (标准库, 确定性无随机) 读 `pattern_manifest.json` (cells + rules + parse_convention) → 产 `legacy_match_report.json`
- **资产 A 忠实** (xinqiaoz PDK_QA 风格): cells 含 new-style (BAD_/GOOD_ + _F/_P) + legacy (bare) + 同 base 两种; rules 含 TSV_S_03_ICT 式前缀匹配
- **hidden B**: 不同 cell/rule 集, 含 B2 (全 new-style 无 legacy 击穿 always-legacy) / B3 (全 legacy 无 new-style 击穿 always-new-pair) / B4 (多 legacy 同前缀歧义 → patternNotFound 击穿 always-first)
- **check.py ≥14 条断言**: a zip+py_compile / b run B exit0+report+stdout==file+键 / c reportCounts total==len(rules_B) 独立重计数 / d parsePatternCell 分类正确 (new vs legacy) / e buildCellsByBase 正确分组 / f Strategy 1-4 new-pair 匹配 / g Step 5 legacy exact/suffix/prefix 匹配 / h Step 5b legacy 前缀兜底 (strip _C/_P) / i goodExisting 默认 0 for legacy bad-only / j matchType 分类 (new_pair/legacy_bad_only/pattern_not_found) 互斥 / k patternNotFound 紧凑列表+count / l B2 全 new-style 击穿 always-legacy / m B3 全 legacy 击穿 always-new-pair / n B4 多 legacy 同前缀歧义→patternNotFound 击穿 always-first / o 确定性 3×md5 / p A↔B guard (rules_A≠rules_B 且 counts_A≠counts_B 击穿 fake_print_expected)
