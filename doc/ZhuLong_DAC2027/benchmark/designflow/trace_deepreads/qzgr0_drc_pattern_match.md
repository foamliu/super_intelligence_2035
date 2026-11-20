# 深读笔记 · qzgr0 · xinqiaoz · PDK DRC pattern-check rule→cell 匹配引擎

## trace_source
- user: xinqiaoz
- host: 10.129.2.11 (亦见 10.129.35.75 / 10.129.32.75；trace 缓存在 .75 `default_designflow_shardC_shardc_r738_0/qzgr0.messages.json` 1.72MB)
- session_file: 1789893440245_qzgr0
- match_count: 642 (keywords: drc:6099;pdk:1208;calibre:803;.gds:133;virtuoso:11;pex:7)
- domain: physical_verify (PDK QA / DRC pattern check)
- mc: 642 (cached on .75 — 本轮 11/19 内网 NFS 对用户 home 全集群 stale，461oe/d52pq/j36z8 乃至 r813 oyqu3/r816 ngrdz 均已不可 open；改从 .75 历史 shardC scout 缓存取 fresh-across-all-shards 的 qzgr0)

## 会话全貌
- 347 msgs (185 user / 162 assistant)；多轮迭代开发 `pdkQaSystem/DRC/pattern/DrcPatternCheck.py` + 文档 `docs/proposals/01_drc_pattern_check_good_bad_split.md`
- 工作流：handoff resume → 校验漂移 → 代码迭代 → 用户验证 → 文档重写
- 主交付物：DrcPatternCheck.py 的 good/bad 拆分匹配 + legacy fallback + 6 策略匹配引擎

## 用户真实意图（逐轮）
- U#1: 从 HANDOFF_drc_pattern_check.md 恢复上下文继续工作
- U#16: 917 二轮验证通过；STI_F_01_V1~V4 根因=cell 未拆 _F/_P（数据问题不改代码）；writeWaiveDrcFile 只参数化 opc1/opc2 层号
- U#24: 对比 0917/0917_1 两 report——为何新代码打印很长 PatternNotFound 表格而旧代码不打印？
- U#39: 当前表格显示哪些状态？哪些不显示？含义？
- U#41: patternNotFound 改紧凑列表；Q unusedCellCount 含义；waivedCount 顺序放 passCount 后
- U#51: 需支持旧式 cell 名（无 _F/_P 无 good_/bad_）作兜底匹配，先讨论
- U#63: 提出具体改动点（collect legacy / Step 5 兜底 / goodExisting 默认值）
- U#67: 旧 cell 检查哪些问题？原则？之前只有 pass/fail
- U#74: 实现一版，先备份到 .tmp
- U#86: 已解决。下一题：TSV_S_03_ICT/IM0/ISC 三 rule 没匹配 cell，但 GDS 有 TSV_S_03，为何？
- U#97: 更复杂匹配 ruleId=TSV_S_03_ICT/IM0/ISC，cell=TSV_S_03_F/TSV_S_03_P，方案考虑到了吗？
- U#98: 修复——Step 5 legacy fallback 加前缀兜底；先备份
- U#106: 测试通过；回头按代码反更新初始文档（可能需重写）
- U#161: handoff skill 写交接文档

## 助手真实算法核心（6 策略 rule→cell 匹配引擎）
来自 A#51/A#54/A#88 的精确描述：

```
parsePatternCell(cellName):
  ends "_F" → (base, "bad")      # F = Fail pattern = bad
  ends "_P" → (base, "good")     # P = Pass pattern = good
  starts "BAD_" → (base, "bad")
  starts "GOOD_" → (base, "good")
  else → None (legacy cell)

buildCellsByBase(cells): {base: {bad:[...], good:[...]}} (跳过 None)

getTargetCellPair(ruleName):
  Step 1: 精确名匹配 cellsByBase[ruleName.upper()] 有 bad+good → (bad, good)
  Step 2: core/peri 后缀剥离——strip rule 末尾 _C/_P 后再精确 → (bad, good)
  Step 3: 反向后缀匹配 → (bad, good)
  Step 4: 前缀模糊匹配 rule.startswith(base+"_") → (bad, good)
  Step 5: legacy 兜底——getTargetCellName(精确→前缀→stopToUndeline) → (legacy, None)
  Step 5b: legacy 前缀兜底——strip rule _C/_P；rule.startswith(cell) 且 charCountMatchGap(下划线数差)≤1；恰 1 候选 → (legacy, None)
  else → (None, None) → patternNotFound
```

## 7 状态分类（A#32）
| 状态 | 含义 |
|---|---|
| pass | bad+good 跑 calibre 三象限全无问题 |
| fail | 跑 calibre 有未 waive 残留（Bad Missing/Good Existing/Incomplete>0）|
| waive | raw 有问题但全被 waive 扣除 |
| error | calibre 执行失败 |
| patternNotFound | GDS 找不到成对 bad/good cell |
| notCheck | 配置中标记 waive |
| skip | deck 中标记 notUse |

report 摘要 7 计数：failCount/errorCount/passCount/waivedCount/patternNotFoundCount/notCheckCount/skipCount + unusedCellCount

## 档 B reframe 决策
- A 档 gold = free-text markdown 文档重写（U#106）+ 多轮代码 edit → 无 ≥8 硬断言牙（print-only stub 打印同形 markdown/pass 即违 §4.9）
- reframe = 抽离助手在 trace 中真实反复做的「6 策略 rule→cell 匹配 + 状态分类 + 摘要计数」算法核心成参数化 Python 工具 `drc_rule_cell_matcher.py`
- CLI: `<rules.json> <cells.json> <out.json>`；输入 rule 列表（含 waive/notUse/verdict_hint 标记）+ cell 列表；输出每 rule 的 matched_cell/match_strategy/bad_cell/good_cell/status + summary 8 计数 + unusedCells
- verdict_hint ∈ {pass,fail,waive,error} 模拟 calibre 输出（真实 calibre 不可在沙盒跑），匹配引擎本身是用户迭代最多的硬核
- visible A = 真实 xinqiaoz PDK rule/cell（STI_F_01_F/_P、TSV_S_03_ICT→TSV_S_03 等）
- hidden B = 合成不同 PDK（ST22 via 层，V1G/V1D/V1R 命名）anti-hardcode

## 子型
`pdk-drc-rule-cell-match-engine` —— C 域「rule→cell 多策略匹配引擎」首例（之前 C 多 deck 解析/调试诊断/报告生成/PPT/布局概念，本例是匹配引擎算法）

## 真实性 / 意图审计
- 2026-11-15 §二 reaudit：debug-Q&A / flow-driving / setup 类全部恢复合法 → 本 session 是真实的 PDK QA 工具迭代开发，合法 user 意图
- keep：用户真实在做 DRC pattern check 工具的匹配引擎开发 + 文档更新，非凑配额
- 档 B reframe 忠实捕获「6 策略匹配 + 7 状态分类 + 8 计数摘要」算法核心
