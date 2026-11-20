# Deepread: 1792204849864_ly0mw — DDJOB Auto 315B

- **session**: `1792204849864_ly0mw` (file: `1792204849864_ly0mw/1792204849864_ly0mw.messages.json`)
- **user / host**: e0039516 / hfeg0plg76
- **mc**: 19 · ledger domain tag: `spice_sim` (keyword-based, **misclassified**)
- **agent**: zhulong (lead), 19 messages, 531 KB
- **claimed**: 2026-11-17 05:02 (lingered as `claimed` across rounds — untracked DEBT)
- **disposed**: r776 (2026-11-18) → **parked, wrong-domain**

## 用户真实意图
- msg0 (user): `DDJOB Auto 315B` (极简)
- 经 agent ask_question 澄清，user 选 `Provide documentation about DDJOB Auto job submission`
- ⇒ **doc-search / explain Q&A** 任务：要 DDJOB Auto 作业提交的文档说明

## Agent 工具链
list_allowed_files → get_agent_policy_status → RAG_MCP search_apis (skill/pyAether, 空) →
search_codebase (DDJOB/ddjob/auto.*job, 命中 `CXMTleFillM0UForddjob.py`) →
skills(cimi-kb-search) → ask_question(澄清) → search_codebase + run_approved_command(kb-search-cli.py)
→ **末条 tool_result = failed** (`RAGFlow API Key 未配置`)
- trace 在失败工具调用处终止，**agent 未交付任何文档**（无 final answer / 无 deliverable）

## 域判定（关键）
raw 关键词计数（全 trace）：
| spice 域 | 计数 | layout/job 域 | 计数 |
|---|---|---|---|
| hspice | 0 | ddjob | 934 |
| finesim | 0 | M0U | 338 |
| siliconsmart | 0 | aether | 553 |
| spice | 0 | job submission | 202 |
| characteriz | 0 | LSF/OGE/Donau | 79/81/109 |
| subckt / .scs / .meas | 0 | layout | 128 |

- `spectre:72` / `corner:62` 命中来自 system_prompt 与 Aether Reference Manual 的通用 EDA 上下文，**非用户任务主题**
- 用户任务主题 = Aether layout 的 M0U metal-fill 自动化 (`CXMTleFillM0UForddjob.py`) 的 **作业提交文档**（LSF/OGE/Donau）
- ⇒ 真实域 = **eda_other (job-submission doc) / layout_aether**，属 shard A / C，**非 B (spice_char)**

## 处置理由
1. **wrong-domain**：trace 主题是 EDA layout 作业提交文档，spice 域关键词全 0；ledger 的 `spice_sim` 标签是 keyword-based 误分类（可能匹配到 summary.tsv 的泛 spice 词）。与 r712 host-verify 发现的 "5 wrong-domain" 同类。
2. **trace 不完整**：agent 末条工具调用失败（RAGFlow key 未配置），无最终交付物；即便域正确，也无 "真的交付了用户要的东西" 可建模判分。
3. shard B 纪律：🚫 不碰别 shard domain ⇒ 不造 case，parked。

## ledger 动作
`mark --session 1792204849864_ly0mw --status parked --note "wrong-domain: ... r776 host-verified"`
（注：原 claim 用 bare slug `1792204849864_ly0mw`，mark 落 `.messages.json` 变体行；ledger append-only，两行并存，mc-matrix 按 session 归一化已计 touched，fresh 不受影响）

## 教训
- `claimed` 状态长期未合成且未记 DEBT ⇒ 本轮 host-verify 才发现是 wrong-domain。**claim 后应尽快深读判定域**，wrong-domain 当轮即 park，勿留 claimed 悬挂。
- summary.tsv 的 keyword 域标签对边界 topic（job-submission / layout-automation）不可靠，须 host 端深读 trace 原文复核域。
