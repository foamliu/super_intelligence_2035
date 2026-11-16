# r649 deepread — xflin @ hfeg0pkn003 (10.129.2.12) · session 1794190927249_42mhi

**shard C revival-pool mid-mc 选料**（pool_reaudit_C.tsv 可造段，mc=128 layout_virtuoso）。
旧 parked reason (r299): "how-to Q&A (pcell instance array), idle, prose go"。
reaudit r622 标 可造（"Q&A/analysis:check验答案结构+关键事实+hidden B"）。
本轮 r649 deepread 复核（承 2026-11-15 用户令「候选池重审」）。

## trace 事实
- file: `/home/xflin/.cline/data/sessions/1794190927249_42mhi/1794213257272...` → 实际 `1794190927249_42mhi/1794190927249_42mhi.messages.json`
- size 1,455,367 B；NMSG 48；real user turns 6
- **0 file writes / 0 edits**（assistant 全程 search_codebase + read_files + RAG_MCP_Server + skills，纯 prose 答复）
- keyword profile (scan): aether:2325; dbget:383; schematic:334; virtuoso:184; cellview:172; dbcreateinst:144; pyaether:132; floorplan:112

## user 轮（逐字）
- U#0/U#1: "烛龙，怎么把instance 矩阵化，我现在有个pcell叫inductor dummy cell，我想设置他的个数和长宽"（U#1 补 "我是在virtuoso环境里"）
- U#2: "版图里怎么等距离复制cell个数，并且可以设置距离和个数大小"
- **U#3 (MSG#45)**: "Minimum metal density in window 125 x125, stepping 62.5 >= 0.1 exclude IND area This rule is not applied when the width of (checking window NOT exclude area) is smaller than 10 um. This rule is only applied when the area of (checking window NOT exclude area) >= 1/4 checking window area 怎么改"
- U#4 (MSG#46): "？"
- U#5 (MSG#47): "？"

## assistant 答复
- MSG#21: Aether Instance 矩阵化（Create Instance 表单 Rows/Cols/Pitch/Space，快捷键 I）— 答 U#0
- MSG#34: Virtuoso pcell array（Create Instance + bus name M<0:2>_<0:3> + Delta X/Y + CDF 参数）— 答 U#1
- MSG#44: Virtuoso 等距复制（Copy+Array Rows/Columns/Delta X/Y；Repeat Copy 快捷键 `.`；SKILL dbCopyFig 循环示例）— 答 U#2
- **MSG#45 之后无 assistant 回复** — U#3 (DRC density rule "怎么改") **未答**，U#4/U#5 "？"×2 亦无回复，session 终止

## 判定
1. **U#3 是真实 C-domain user 意图**（physical_verify：修改 Calibre SVRF density rule），且是 produce-task（可 teeth：验修改后 rule 的结构/阈值/排除条件）。**但无 gold** —— trace 中该问题未被回答，用户连发 "？"×2 后离开。⇒ 符合排除标准 2（无 accepted gold ⇒ 写不出能区分真假交付的 check）。
2. U#0-U#2 已答，gold = prose how-to（GUI 操作步骤 + SKILL 片段），无结构化 artifact。§4.3 teeth-able check 未证实：prose 步骤难拆 ≥8 独立非子串条件 + hidden B 结构异 + 3 negative 全 FAIL，易退化成「答里有没有提 'Delta X'」式子串断言（§4.3 明禁）。
3. 旧 r299 "idle/prose go" 部分正确（prose），但漏判 U#3 是真实 DRC produce-task（仅无 gold）。

## 处置
- pool_reaudit_C.tsv 新判定 → **可造-低优(deepread r649)**（不删，保留待 B档 structured-glossary reframe 验证 U#0-U#2 的 teeth 可能性；U#3 因无 gold 永不可造）
- 不落 ledger（session 42mhi 已于 r299 parked，无需重复 park）
- 不造 case（无 gold / prose teeth 未证实）

## 备注（Q&A teeth 探索方向，留待后续）
若未来要把 U#0-U#2 这类 Virtuoso 操作 how-to 造成 teeth-able case，唯一可行路径是 **B档 structured-glossary reframe**：把"问→答"重定为"问→产结构化 JSON 步骤卡"（字段：{operation, menu_path, shortcut, parameters[], skill_api, example}），hidden B 换一个不同操作（如 stretch/split），check 验字段齐全 + 参数正确 + skill API 名真实存在 + 步骤序合法。但这属 B档 synthesized gold，非 A档 trace-faithful；需单独验证 gold 不反推答案。本轮不实施（时间预算不足 + 需先确认 A/B 档分开报口径）。
