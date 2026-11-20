# Deep-read: 1789892850910_sp2d6 (xinqiaoz @ hfeg0pkn004, mc=297)

- **session**: `/home/xinqiaoz/.cline/data/sessions/1789892850910_sp2d6/1789892850910_sp2d6.messages.json` (1.0 MB, 194 msgs)
- **tools**: 150 calibre (pure DRC pattern-check), netlist/schematic 轻
- **domain**: physical_verify (DRC pattern QA)
- **real work**: 维护 PDK QA DRC pattern-check 工具 `DrcPatternCheck.py` (calibre DRC 跑 good/bad pattern cell 对，产 drcWithPattern 报告)

## 用户轮（意图）
- U#0 handoff 恢复上下文 (HANDOFF_drc_pattern_check.md)
- U#25 917 第二轮验证通过 / STI_F_01 root cause (cell 未拆 _F/_P) / writeWaiveDrcFile 参数化 opc1/opc2 层号 / 暂不提交
- U#40 修改前后两份 report 对比：原 drcWithPattern 不打印 PatternNotFound 表，新代码打印很长一条，为什么
- U#68 当前表格显示哪些状态 / 哪些不显示 / 含义 (纯意图 explain)
- U#72 patternNotFound 改紧凑列表 (skip 式) / unusedCellCount 是什么 / waivedCount 顺序恢复
- U#91 需求：支持旧式 cell 名 (无 _F/_P, 无 good_/bad_) 作兜底匹配；先讨论
- U#113 改动点清单 (~10-15 行，复用已有函数)
- U#115 总改动量 / 目录结构 / 可行性
- U#119 report 要改吗
- U#121 旧 cell 检查哪些问题 / 原则 / 与之前是否一致
- U#134 实现一版，先备份
- **U#154 (本 case seed, 纯意图)**: report 379~381 行 3 条 TSV_S_03_* rule 没找到 cell，但 gds 里有 cell TSV_S_03，什么原因没匹配上
- U#176 更复杂匹配：ruleId TSV_S_03_ICT/IM0/ISC ↔ cell TSV_S_03_F/TSV_S_03_P，方案考虑到了吗
- U#178 修复 Step 5 legacy fallback 加前缀兜底，先备份

## assistant 关键产出
- U#68 (msg71): 7 种状态总览 (pass/fail/waive/error/patternNotFound/notCheck/skip) + 显示 vs 不显示 (循环1/循环2)
- **U#154 (msg175, 本 case 金标准)**: 推演匹配流程
  1. parsePatternCell("TSV_S_03") → None (无 _F/_P) → legacyCellList
  2. getTargetCellPair Step5 → getTargetCellName → getTargetCellNameOri
  3. ruleNameSpecial1 = "_C_" or "_P_" in rule or endswith _C/_P → False (TSV_S_03_ICT 后缀 _ICT)
  4. ruleNameSpecial1=False → mode B (rule-is-prefix-of-cell) → cell.startswith(rule+"_") → TSV_S_03 比 rule 短，False → patternNotFound
  根因：mode A (cell-is-prefix-of-rule) 仅在 ruleNameSpecial1=True 时激活，漏掉 _ICT/_IM0/_ISC 后缀
- U#176 (msg177): cell 带 _F/_P 走 Strategies 1-4 (Strategy 4 前缀模糊命中)，已能匹配，不需 legacy fallback；charCountMatchGap 限制 _ 数量差 ≤1
- U#178 (msg186): 实现 Step 5b legacy prefix fallback (ruleUpperForPrefix.startswith(cellUpper))

## 关键源码 (从 trace 工具结果重建)
- getTargetCellNameOri (L290-313): ruleNameSpecial1 → mode A/B 分支
- getTargetCellPair (L378-412): Strategies 1-4 + Step5 legacy fallback (L412-417)
- parsePatternCell (L323-348): _F/_P/BAD_/GOOD_ → (matchKey, goodBad, corePeri) or None
- charCountMatchGap (L282-288): _ 计数差 ≤ defaultGap(1)

## case 合成
- A-档 faithful, physical_verify, L1-boundary
- deliverable: `drc_match_rca.py` 通用诊断器 (report+cells+logic 源码 → 结构化 RCA JSON)
- A: report_A.txt (TSV report, patternNotFound 18 含 TSV_S_03_ICT/IM0/ISC) + cells_A.txt (含 TSV_S_03) + drc_pattern_match_logic.py (重建匹配逻辑)
- 隐藏 B: report_B (M3_ENC_X/Y/Z + NOMATCH_BAZ) + cells_B (含 M3_ENC)，同一 logic，强制通用解析
- check.py 15 条 (a-o): ref PASS + 4 neg 全 FAIL + §4.9 三假全 FAIL ✓
