# r594 deepread — lizwen / 1790216513217_vvhhs / DRC deck rule parser

## 选料 (r588/r593 模式)
- src=ssh_eda_search_20261115_081559 (summary_1115_081559.tsv 本地)
- C-keyword (calibre|virtuoso|aether|ipcustom|layout|lvs|drc|pexivirtuoso) mc≥10 → 4-shard ledger anchor 归一交叉 (`sub(/\.messages\.json$/,"")`) → **394 truly fresh** (与 r593 的 398 一致口径)
- top by mc peek 6 候选（ploz9/yavow/vvhhs/g1olj/f953o/9pcjd）：
  - ploz9 (steveny,mc97,virtuoso:513) → REJECT (项目文档/cli化改造分析, doc/analysis 非干净 produce)
  - yavow (miccao,mc90,lvs:216) → REJECT (启动 3D_LVS_GUI.py 脚本+GUI 弹窗, run-existing/GUI 不可离线判)
  - **vvhhs (lizwen,mc84,drc:317) → ACCEPT** (modify DRC deck + skill rule 识别, produce-task, 干净可判)
  - g1olj (e0047488,mc76) → REJECT (量测函数/多边形数据结构 Q&A, 概念解释无牙 check)
  - f953o (e0039602,mc83) → REJECT (DDR5 vsim 仿真环境阅读/波形查找, verilog/sim 域非 C)
  - 9pcjd (miccao,mc79) → backup (autocell vs TECHLIB 安全审计报告, audit-report check 难有牙)

## trace (lizwen, 52 msgs, 2 user_input)
- U@M0: `/home/lizwen/.cline/scripts/data/sample_drc_deck/specs/test_deck_new 每条rule的名字后面加：其他内容不变` — sub-task 1: 给 deck 每条 rule 名后加冒号
- agent: read test_deck_new → 写 add_colon.py (re.sub 加 ":") → run → rm → 重写 → in-place 改 test_deck_new
- U@M20: `该skill识别rule 的数据识别 test_deck_new 文件里的内容` — sub-task 2: 让 drc-pattern skill 从 test_deck_new 识别 rule
- agent: skills(drc-pattern) → read drc_pattern_gen.py + drc_rules_spec.json → 改 drc_pattern_gen.py 加 `parse_test_deck()` → 写 test_parse_deck.py 验证

## test_deck_new 格式（人类可读 DRC rule spec）
```
宽度类规则 (Width)              <- 类别标题 (CJK + 括号, 不以规则名开头)
规则名        说明               <- 列头行 (startswith 规则名, 跳过)
DNW_W_000_00:        Min - DNW width [in peri : 8.260]   <- 规则行 RULE_NAME:  desc
M1_S_008_01        Min - M1 spacing wide ...             <- 冒号可省
```

## 真实 parse_test_deck() (lizwen 最终交付, drc_pattern_gen.py:84-114)
- regex `^([A-Za-z][A-Za-z0-9_]+):?\s+(.*)$` → rule_id / description
- 跳过空行 + `规则名` 列头行
- 非规则行 → current_category (类别标题)
- 返回 `[{rule_id, category, description}]`

## case: DeckRuleParseExtract-001 (physical_verify L2-boundary, B档 mock-behavioral, k=14 a-n)
- 把"让 skill 从 test_deck_new 识别 rule"重构为独立纯 Python 脚本任务 `parse_test_deck.py <deck> <out_json>` → JSON 数组
- 输入 A (可见): test_deck_A (6 rule/3 cat, 示例格式)
- 隐藏 B: test_deck_B (14 rule/5 cat, 含无冒号 rule M1_S_008_01 + 空行 + 列头)
- 隐藏 B2: test_deck_B2 (6 rule/3 cat, 含无冒号 rule MT2_S_006_00) — 反硬编 (计数≠B)
- ref parse_test_deck.py (faithful to lizwen 的 regex/跳过/类别逻辑, 参数化 argv)
- **14 条 a-n**: zip含脚本 / py_compile / B exit0+JSON / B rule数14 / B类别数5 / B rule_id集合精确14 / 无冒号rule被解析 / 列头行不漏为rule / 首条rule+category / 末条rule+category / 类别顺序 / B2 rule数6≠14 / B2类别数3≠5 / 确定性两跑字节一致
- 自验: REF 14/14 PASS✓；3 neg (empty/print_only/deleted_core) 全 FAIL✓；NEGATIVE_SELFTEST ALL-FAIL-OK✓；embedded test==disk roundtrip✓；k=14≥8✓
- C.jsonl 361→362。mark case✓ (pv 154→155)

## 谱系
produce-task 子型: drc-deck-rule-parse (test_deck_new 格式解析, 承 r593 DrcDeckValueCompare 同 lizwen-邻域 deck-script 模式)
anti-hardcode: dual-hidden-fixture (B 14rule/5cat vs B2 6rule/3cat)
