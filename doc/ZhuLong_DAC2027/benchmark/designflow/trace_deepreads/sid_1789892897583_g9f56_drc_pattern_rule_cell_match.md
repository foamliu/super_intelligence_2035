# Deep-read: 1789892897583_g9f56 (xinqiaoz @ hfeg0pkn002, mc=366, 194 msgs, 1.01MB)

- **trace_source**: user=xinqiaoz, host=hfeg0pkn002, session_file=1789892897583_g9f56.messages.json, match_count=366, real_task_summary=PDK_QA DRC pattern-check tool dev (DrcPatternCheck.py): report format fix + legacy cell-name fallback matching
- **tool keywords**: 150 calibre (DRC QA deck/report), pyAether
- **跨 shard 查重**: 选题前 `grep g9f56 trace_ledger_*.tsv` → 仅 shard C 本 ledger（fresh，无碰撞）

## 真实任务流（user turns，逐轮意图）

- U#0: handoff 恢复上下文（HANDOFF_drc_pattern_check.md），继续之前工作
- U#25: 917 第二轮验证通过；STI_F_01_V1~V4 根因=cell 未拆 _F/_P（非代码问题）；writeWaiveDrcFile 参数化 opc1/opc2 层号；暂不提交
- U#40: 对比修改前后两份 drcQa report，发现新代码打印了很长的 PatternNotFound 表格而旧代码没有 → 问为什么（**诊断轮，给现象**）
- U#68: 确认表格显示/不显示哪些状态及含义（Q&A）
- U#72: patternNotFound 改紧凑列表（类似 skip）；问 unusedCellCount 含义；waivedCount 顺序放回 passCount 后
- U#91: **需求轮（A 档候选）**：支持无 _F/_P、无 good_/bad_ 的旧式 cell 名作为匹配兜底，避免版本切换问题；先讨论不改代码
- U#113: **给方案轮**（→ 不可作 A 档任务说明）：列 5 个改动点（check 收集 legacy cell / getTargetCellPair 加 Step 5 fallback / goodExisting 默认值 / 复用 parsePatternCell+getTargetCellName），约 10-15 行
- U#115/U#119/U#121: 评估改动量、report 是否改、旧 cell 检查哪些问题（原则 pass/fail）
- U#134: 实现一版，先备份到 .tmp
- U#154: **需求轮**：TSV_S_03_* 3 条 rule 未匹配，GDS 里其实有 cell TSV_S_03，问原因
- U#176: **需求轮**：更复杂匹配——ruleId TSV_S_03_ICT/IM0/ISC，cell TSV_S_03_F/TSV_S_03_P，方案考虑到吗
- U#178: **给方案轮**：Step 5 legacy fallback 加前缀兜底，把 rule 捞回；先备份
- U#193: 回头更新初始 proposal 文档（代码反向更新文档）

## 关键产物（assistant editor/run）

- 编辑 `/home/xinqiaoz/PDK_QA/pdkQaSystem/DRC/pattern/DrcPatternCheck.py`（多轮）：
  - patternNotFound 去重排序 + 紧凑列表；unusedCellCount 计算（usedCells 差集）；waivedCount 顺序
  - **legacy cell fallback**：check() 收集 parsePatternCell==None 的 cell → self.legacyCellList + self.legacyCellUpperListInfo
  - getTargetCellPair 末尾加 Step 5：调 getTargetCellName(legacy) 做兜底 → (legacyCell, None)
  - runCalibreForCell：goodCell 可为 None（legacy 跳过 good run）
  - Step 5 加前缀兜底（rule startswith legacyCell+"_"）
- 备份到 .tmp；py_compile 验证；跑测试 case

## 核心算法（从 trace read_files 还原，faithful）

1. `parsePatternCell(cellName)` → `(matchKeyUpper, goodBad, corePeri)` 或 `None`（legacy cell）：
   - 尾 `_F`→bad/`_P`→good，去后缀得 base；首 `BAD_`→bad/`GOOD_`→good；否则 None
   - base 尾 `_C`/`_P` = corePeri
2. `buildCellsByBase(gdsCellList)` → `{matchKeyUpper: {"bad":cell|None, "good":cell|None}}`
3. `getTargetCellPair(ruleName, cellsByBase, legacy...)` → `(badCell, goodCell)`，5 策略顺序：
   - S1 exact_base：ruleUpper in cellsByBase
   - S2 strip_coreperi：rule 尾 `_C`/`_P`，ruleBase in cellsByBase
   - S3 reverse_coreperi：key 尾 `_C`/`_P`，keyBase==ruleUpper + charCountMatchGap
   - S4 prefix：key.startswith(rule+"_") 或 rule.startswith(key+"_")，charCountMatchGap，唯一匹配
   - S5 legacy fallback：getTargetCellName(legacy) 精确 → (legacyCell, None)；再 legacy prefix：rule.startswith(legacyCell+"_") + charCountMatchGap → (legacyCell, None)
4. `getTargetCellName` / `getTargetCellNameOri`：精确 → ruleSpecial1 时 cell 作 rule 前缀 → 否则 rule 作 cell 前缀 + charCountMatchGap，唯一
5. `charCountMatchGap(drcId, cellName, defaultGap=1, targetChar="_")`：count 差 <= 1
6. `getCharCount`：边界感知的 "_" 计数
7. `stopToUndeline`：`.` → `_`（TSI/MARS）

## 合成决策

- 抽「rule→cell 匹配」子技能重构为**便携式 drc_rule_cell_match.py**（纯标准库，CLI `--rules --cells --out`，确定性 JSON）
- B-档 synthesized（提取通用算法，不绑 PDK_QA 框架）；L1-boundary（离线匹配，不跑 calibre）
- A=可见 fixture（7 rule × 8 cell，覆盖 S1-S5 + unmatched）；隐藏 B=不同命名/规模（8 rule × 9 cell），强制通用非硬编码
- 判分 15 条(a-o)：zip+compile+stdlib / --help / B 跑出合法 JSON / B stats 4 项 / B 各策略 rule 命中（exact_base/strip_coreperi/reverse_coreperi/prefix/legacy_exact/legacy_prefix/unmatched）/ 跨输入守卫 A（legacy_prefix TSV_S_03 + strip_coreperi MUX8_C + cellsByBase）
- 负样本：fake_empty / fake_print_expected(跨输入守卫杀) / fake_core_deleted(legacy fallback 删→legacy_matched=0) / naive_legacy_no_prefix(无前缀兜底→ANT_METAL_7_TIE 漏) / naive_no_charcountgap(过匹配)
