# 深读笔记 · r592 候选池重审 deepread 验证（3 条）

> 背景：r589/r590 候选池重审基于 ledger note 关键词批量 revival 306 条为"可造"，并标注"需 deepread 确认 check() 可写"。
> r592 随机抽 3 条做 deepread 验证（对照真实 trace 原文），检验批量 revival 的准确率。

## 方法
从 pool_reaudit_C.tsv 新判定="可造"中抽 3 条（覆盖 debug/Q&A/analysis 三类旧判 weak），scp `<sid>/<sid>.messages.json` 到 .75 → 解析 user_input + tool_use → 对照 r590 拟造任务形态判断是否真的 C-domain + check() 可写有牙。

## 验证结果（3/3 = 100% FALSE POSITIVE）

### 1. 1791526217197_87257 (t0002962@hfeg0pkn003, mc=460, layout_aether)
- **r590 新判定**：可造（debug/analysis: check 验根因+修复+hidden B）
- **r590 revival 触发词**：旧 note 含 "debug"
- **trace 原文**（242 msgs, 3 user_input, 132 tool_use 53 run_approved_command+42 list_allowed_files）：
  - U1: "The policy on disk is **correct** now ... But the policy engine **cached the old values at session startup** (session 1791525861730_k613u), so it still thinks expectedExecutableOwnerUid is..."
  - U2: "I grant you the permission to change the file yourself"
  - U3: "done how could I prompt you in the new session"
- **结论**：trace = **Cline agent-policy-engine 缓存/权限 debug**（用户 grant 权限改 policy 文件、讨论新 session 如何 prompt），**非 EDA、非 design-flow**。
- **判定**：**不可造**。原 parked note（"meta: UI#0 policy engine caching/permission debug, not a design-flow seed"）**正确**。r590 "debug" 关键词批量 revival = **FALSE POSITIVE**。

### 2. 1794400409399_njh7p (jackjia@10.129.32.100, mc=459, 空域)
- **r590 新判定**：可造（Q&A/analysis: check 验答案结构+关键事实+hidden B）
- **r590 revival 触发词**：旧判 "Q&A" 现合法
- **trace 原文**（380 msgs, 57 user_input, 140 tool_use 71 SandBox_MCP_Server__run_code）：
  - U1: "boxing 的颜色在呢嘛固定"（Aether Q&A）
  - U5: "WOWTOP schematic Ictop, DDR5TOP schematic I_Channel, Channel schematic I_BCenter, ... I_C_MrwSetMr2 schematic MROPT<1> 分析下"
  - U7: "MROPT<1> 为什么分成这个PMRW PMWRR"
  - U11: "分析下pmrr pmrw的区别"
  - U12: "这个层次的pmrw<2> 接到哪里去了"
- **结论**：trace = **Aether 原理图层次 Q&A + 信号 tracing**（MROPT<1>/PMRW/PMWRR 跨 schematic hierarchy 追踪），域 = **schematic_netlist（D-shard）**，非 C（physical_verify/layout）。summary 的 calibre/drc 关键词是 FALSE-POSITIVE（scanner 计了文件内容非对话）。
- **判定**：**不可造-for-C（域错 = D）**。r538 "Q&A" revival 对 C 是**域错 FALSE POSITIVE**。

### 3. 1790737047923_1495z (ellawu@hfeg0pkn001, mc=79, physical_verify)
- **r590 新判定**：可造-低优（Q&A/analysis: check 验答案结构+关键事实+hidden B）
- **r590 revival 触发词**：旧判 "Q&A SVRF SETLAYER syntax explain" 现合法
- **trace 原文**（57 msgs, 6 user_input, 31 tool_use 9 read_files+8 RAG search_apis+7 search_codebase）：
  - U1: "SETLAYER PRB_RANGE_ENCRegion_NMOS_Y = ENC AT4_NCH_Hori_Edge PRB_RANGE_For_NMOS <= $AT4_NCH_MaxW ABUT > 0 < 90 OPPOSITE REGION"（粘贴 Calibre TVF rule deck）
  - U2: "fenxizhejudejieguo"（分析这局的结果）
  - U4: "meiyijudejutihanyishishenme"（每一局的具体含义是什么）
- **结论**：trace = ellawu 多轮 **Calibre TVF SETLAYER rule deck 逐行解释**（AT4_NCH ENC / PG dummy fill / LENGTH ANGLE）。域 = physical_verify（C 正确）。但 r337 已 deepread 判定 **DUPLICATES r330 TvfSetlayerExpl-001**（同 ellawu、同 SETLAYER-explanation 主题）。
- **判定**：**不可造-dup**（已被 r330 覆盖）。原 r337 parked dup 判定**正确**，r590 revival = **重复 FALSE POSITIVE**。

## 汇总
| session | r590 判定 | deepread 实判 | 原 parked 是否正确 | revival 类型 |
|---|---|---|---|---|
| 87257 | 可造(debug) | 不可造(非EDA) | ✓ 正确 | 关键词误触发 |
| njh7p | 可造(Q&A) | 不可造-for-C(域=D) | ✓ 正确(r538 peek 已指出) | 域错 |
| 1495z | 可造-低优 | 不可造-dup | ✓ 正确(r337 已指 dup) | 重复 |

**结论**：3/3 batch revival 为 FALSE POSITIVE，原 parked 判定均正确。r590 候选池重审的 306 条"可造"中，基于"debug/Q&A/analysis 关键词"机械 revival 的部分**可能大量为 FALSE POSITIVE**——原 parked note 的 reject 理由（非EDA/域错/dup）往往是 agent 当初 deepread 的准确结论，不应仅凭关键词推翻。

**对 r590 审计结论的修正**：
- r590 报 "新可造=398（新增 306 条被旧规则误杀）" → **此数高估**。deepread 验证表明需逐条对照 trace 原文确认，关键词 revival 不可信。
- **建议**：r590 的 306 "可造" 条不应直接作为选料池；选料时必须 deepread trace 原文，且优先尊重原 parked note 的 reject 理由（除非有明确证据原判错误）。
- **真正可信的 revival** 应限于：原 note 明确写 "weak: Q&A/analysis-only（旧规则判 weak）" **且** trace 确为 C-domain EDA 任务 **且** 非 dup。这类需逐条 deepread 确认，不能批量采信。

**下一步**：继续造题应回到「fresh-pool 逐条 deepread 选料」（r588 模式：summary scan → 4-shard ledger 交叉 → fresh → peek produce-task），而非从 r590 的 306 revival 池直接取。本 shard 下一轮（r593）回到 fresh-pool 选料。
