# Deepread: 1793858542305_5arbb (alleng@10.129.33.27, mc=39)

## 元数据
- session: 1793858542305_5arbb
- user: alleng
- host: 10.129.33.27 (hostname hfeg0plg77 per ledger)
- mc: 39
- keywords: lvs:90;verilog:60;analog:60;floorplan:48;cmos:27;pyaether:14;transistor:10;vhdl:6
- domain classified: analog_context (D shard)
- session file: /home/alleng/.cline/data/sessions/1793858542305_5arbb/1793858542305_5arbb.messages.json (812KB, 110 msgs, 55 user / 55 asst)
- agent: "lead" (cline)

## 判定: parked — false-positive keywords (not a design-flow produce-task)

## 理由

用户在整个 110-msg session 中仅输入 3 条真实消息（其余为 skill_instructions setup / tool_result 回填）：

1. **msg 60**: "以上内容输出文本文档" (output the above content as a text document)
2. **msg 96**: "linux系统怎么打开.md格式文件" (how to open .md format files on Linux)
3. **msg 98**: "pandoc 安装" (pandoc installation)

这是**通用 IT / 文档工具 Q&A**，不是 EDA 设计流任务。

## keyword 误判根因

session 的 keyword 命中 (lvs:90, verilog:60, analog:60, floorplan:48) 来自 **cimi-kb-search 技能检索的知识库内容**，不是用户的 EDA 工作。msg 0 是 `<skill_instructions name="cimi-kb-search">` 技能启动块，agent 在后续消息中用 KB 检索命令查回了含 lvs/verilog/analog/floorplan 关键词的文档片段，这些片段文本命中了 scan summary 的 keyword 计数器。

用户实际意图 = 文档导出 + Linux .md 文件操作 + pandoc 安装，全部为通用 IT 问题。

## 11-15 重审口径下的判定

按 11-15 令「候选池重审」精神，Q&A 是合法任务类型。但本 session 的 Q&A 是**通用 IT Q&A**（非 EDA 设计流 Q&A），且：
- 无 EDA 工具调用（agent 全程用 cimi-kb-search + 文件读写）
- 无 EDA 设计/验证/分析产物
- 写不出能区分真假 EDA 交付的 check()（判分无牙）

⇒ 维持 parked，但 parking 理由从旧口径 "Q&A" 修正为新口径 "false-positive keywords: KB-search content hit EDA keywords, user actual intent = generic IT Q&A, not EDA design-flow"

## 对 D filter 的启示

D shard filter (trace_ledger.py line 38) `"waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic"` 是 inclusion-only，凡 keyword 命中即纳入候选。本 session 是 **skill-driven KB-search** 类型（cline skill_instructions 触发 KB 检索），KB 内容文本命中 keyword 但用户无 EDA 意图。此类 false-positive 在 fresh 池扫描中应加一层过滤：**排除 agent="lead" 且首条 user msg 含 `<skill_instructions name="cimi-kb-search">` 的 session**（或更宽：排除首条 user msg 是 skill_instructions 块且后续无 EDA 工具调用的 session）。

## r860 选料实测

本轮 r860 为兑现 r859 计划「选料优先 waveview/analog dominant fresh 候选」，从 candidates_mc10.tsv 用 4-shard ledger union 过滤 fresh 候选：
- **D-domain top-keyword fresh pool 极度枯竭**：top_d≥20 仅 3 条 (uq3df mc=82 stale / uxc45 mc=12 / 7g1bd mc=13)
- 放宽至 D-domain top-2 keyword 且 top_d≥10：14 条，但多数 mc<20
- uq3df (schematic:290/pyaether:290, mc=82) claimed → **stale** (session file rotated, host 仅剩 1 个更新 session)
- 5arbb (analog:60 2nd to lvs:90, mc=39) claimed → **false-positive keywords** (本笔记)
- 其余 fresh 候选 mc≤20，质量风险高

⇒ fresh D-domain 池已到「枯竭+stale+false-positive」三重夹击阶段，造题需转向 parked 重审（11-15 令优先级）或接受低-mc 候选深读。

## 处置
- ledger: `mark --session 1793858542305_5arbb --status parked --note "r860 false-positive keywords..."`
- 不造 case（无 EDA 设计流意图，写不出有牙 check()）
