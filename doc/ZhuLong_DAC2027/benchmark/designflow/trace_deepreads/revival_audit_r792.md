# revival_audit_r792 — 候选池重审 deepread 批次 (2026-11-19, shard C r792)

> 2026-11-15 用户令 §二「候选池重审」执行：对 pool_reaudit_C.tsv 的 revival 候选逐条 deepread，
> 用「两条保留排除标准」(①无真实 trace ②写不出有牙 check()) 判定可造/不可造。

## 本轮 deepread 6 条 (eda_flow MCP 通道全程可用，ssh-from-.75 fetch)

### 1. s5o5k (mc=400, e0047527@hfeg0pnd001) — ❌ 不可造(C)：cross-shard 已 case
- **trace**: 358 msgs，用户桥接服务端口 troubleshooting + U#280「把eda桥接到过程写个文档」+U#298「只写配置过程就行了」。
- **deepread 发现**: 助手产出 `EDA桥接配置指南.md` (10542 chars)，含可验配置事实（env var `CXMT_START_EDA_AGENT_SERVER=1`、`aether -ADV`、ip_port.json 路径、端口公式 `20000+(uid*mult)%45533`、3 服务 multipliers 10008/10009/10010）——**本可造**（端口公式计算可作 cross-input computational teeth）。
- **判定**: **cross-shard 冲突** —— shard B 已于 2026-11-15 造 `EDA-Eval-DesignFlow-BridgeCfgDiag-001` (B.jsonl, domain=eda_other)。C 的 r537 parked 行是 stale 残留。
- **处置**: 不可造(C)；session-level mutex。C r537 parked 行保留作 stale 证据。

### 2. slj4a (mc=341, t0002729@hfeg0plg83) — ❌ 不可造：check 不了有牙
- **trace**: 150 msgs，12 user_input。用户纯探索 Q&A：「查下你当前有没有接入我的aether」「你能协助我在aether下做什么工作」「查下公司现有的版图编辑脚本目前能实现的功能」「帮我看看有没有修drc的辅助脚本」「跑一下calibre的DRC」「我现在跑了一次drc，你能读结果没」。
- **deepread 发现**: 助手 **0 write/edit**（tools: 23 SandBox_run_code, 20 read_files, 23 list_allowed_files —— 只读+跑现有代码，无产出物）。用户自己跑 DRC，让助手读结果。
- **判定**: 意图合法(新规则 Q&A 合法)，但**写不出有牙 check()**——无 concrete artifact，deliverable 只能是"回答/解释"，判分退化为子串匹配，违 §4.3「仅子串出现式断言」。**符合排除标准 ②**。
- **处置**: 不可造。pool_reaudit「可造」判断修正为「意图合法但 check 不了有牙」。

### 3. goeio (mc=220, kepeim@hfeg0plg90) — ❌ 不可造：check 不了有牙
- **trace**: 127 msgs，31 user_input。纯 stdcell layout 概念教学 Q&A：「教教我如何理解nand3LVS_pc60器件，schematic和layout」「nand门是不是实现操作只需要三个并联pmos」「为啥pmos三个不全共用有源区，防止latchup吗」。
- **deepread 发现**: 助手 **0 write/edit**（25 read_files, 15 RAG search_apis, 1 ask_question —— 只解释，无产出物）。
- **判定**: 概念教学 Q&A，同 30cgz r668 REJECT 性质。**符合排除标准 ②**（无 artifact，check 无牙）。
- **处置**: 不可造。

### 4. qwreb (mc=59, ellawu@hfeg0plg83) — ❌ 不可造：check 不了有牙
- **trace**: 56 msgs，17 user_input。用户贴 `genPGDummy_for_Logic.py` + `G5_AA_PG_dummy_fill_for_Logic.rule`，问「这个flow理一下」「SETLAYER...这两个有什么区别」「修改点10详细」—— SVRF rule **解释** Q&A。
- **deepread 发现**: 助手 **0 write/edit**（9 read_files, 2 search_codebase, 1 run_commands —— 只解释 rule 语法，无修改 rule/无产出物）。
- **判定**: rule-解释 Q&A（非 rule-WRITING）。**符合排除标准 ②**。
- **处置**: 不可造。

### 5. pvl8c (mc=139, steveny@hfeg0pnd001) — ✅ **可造 → 本轮落库**
- **trace**: 127 msgs，6 user_input，28 editor writes。用户修改 `eda_agent` 路由层 skill：U#23「已有案例优先，案例找不到才找源码（缓存）」反转核心原则；U#106/U#108「你从哪里知道的用户名ip和port」「SandBox_MCP_Server不在本机也要用占位符」；U#123「任务过程中创建的临时文件需要删除」。
- **deepread 发现**: 助手 28 次写入 `~/.cline/skills/eda_agent/SKILL.md` + 子 skill SKILL.md。**有 concrete artifact**（修改后的 SKILL.md）。路由表(keyword→platform→sub-skill→lang) 可解析→**computational cross-input teeth**（hidden B 查询关键词→验路由平台+lang）；核心原则反转(源码优先→案例优先)是结构性判定；占位符/清理规则是事实判定。
- **判定**: 可造。k_check=12（a-l），ref PASS 12/12，4 negative FAIL distinct(a/b/e/g)，§4.9 fake_core_deleted FAIL，NEG_RC=0。
- **处置**: 落库 `EDA-Eval-DesignFlow-EdaAgentSkillRouteRewrite-001` (physical_verify, L1, A档, k_check=12)。C.jsonl 483→484。

### 6. (复核) pool_reaudit「可造」6 条 staleness
- iacrk → **已是 case** `BwzDummyFlowExtract-001` (C.jsonl)
- kkjsm → **已是 case** `DrcRuleExplainQa-001` (C.jsonl)
- eabca → **已是 case** `AeGetSelSetInfoHowto-001` (C.jsonl)
- n9l88 → **已是 case** `CutLayerIdxBugFix-001` (C.jsonl, 2026-11-16)
- 19e3k → **已是 case** `AetherLauncherSkill-001` (C ledger, B/D)
- pvl8c → 本轮落库（见上）
- s5o5k → **已是 case** `BridgeCfgDiag-001` (B, cross-shard)
- **结论**: pool_reaudit「可造」清单 stale——6 条中 4 条已落库 case，1 条 cross-shard，仅 pvl8c + xk5uw 真正未造。xk5uw(doc-search PDK 层解释)同 slj4a 性质，预期 check 不了有牙（未 deepread，下轮验）。

## 本轮结论
- **1 case 落库** (pvl8c → EdaAgentSkillRouteRewrite-001)。
- revival 候选 deepread 证实：r537「Q&A/sim/run-existing」类候选**意图合法但普遍 check 不了有牙**（无 concrete artifact → §4.3 子串退化 → 排除标准 ②）。pool_reaudit「可造」清单 stale（4/6 已 case）。
- eda_flow MCP 通道全程可用（open_session + ssh-from-.75 fetch 6 trace + run_commands 扫 summary.tsv），**非 infra-block**。
