# aafag — innovus typo Q&A（trivial）· r394 deepread

- **session**: `1793790637246_aafag` · user `e0046718` @ `hfeg0plg76` (10.129.8.124) · mc=12
- **size**: 62948 B / 8 msgs / 1 user-text-turn / 3 tool_uses
- **keywords**: innovus:401;cadence:118;pdk:20;calibre:10;tempus:7;voltus:5;gdsii:5;genus:4
- **路径**: nested `/home/e0046718/.cline/data/sessions/1793790637246_aafag/1793790637246_aafag.messages.json`

## 对话流
- msg[0] user: `innouvs`（拼写错误，单字）
- msg[1] assistant: 识别为 "Innovus" 拼写笔误，search_codebase + RAG_MCP_Server__search_apis + skills(ask-eda)
- msg[5] assistant: run_approved_command 跑 ask_eda.py 问 "What is Cadence Innovus?"
- msg[6] tool_result: AskEDA 返回 Innovus 综述（placement/CTS/optimization/routing，iSpatial/ML/先进工艺）
- msg[7] assistant: 整理综述给用户（"innouvs 应该是 Cadence Innovus 拼写笔误..."）

## 判定
**trivial Q&A，0 produce-task，0 innovus 执行**。`innovus:401` 关键词来自 agent 解释文本（综述里反复提 "Innovus"），**非工具调用**。D-parked "boilerplate(innouvs)" 证实。A-parked r394。

## 方法学发现
**高 tool-keyword count 可能是解释文本假信号**：scan 关键词计数统计的是 session 全文 token 出现频次，agent 在 Q&A 中解释某工具时该工具名会被反复提及 → count 虚高，但无实际工具执行。`innovus:401` + `mc=12` 的组合（高 kw / 低 mc）是此类假信号的指纹。后续选料对"高 kw + 低 mc + top-tool 是 EDA 综合工具名"的候选应优先疑为解释文本，需 deepread 验证是否有真实 tool_use 调用。
