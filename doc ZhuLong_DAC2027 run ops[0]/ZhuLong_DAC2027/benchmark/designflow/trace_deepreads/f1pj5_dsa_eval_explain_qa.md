# Deepread — f1pj5 (jingc @ hfeg0pkn001, mc16, spice_sim)

**session_file**: `1792936692635_f1pj5.messages.json` (in subdir `1792936692635_f1pj5/`, 28 msgs / 165KB / 2 substantive user turns / agent=lead / 2026-10-25 14:00)
**trace_source**: `/home/jingc/.cline/data/sessions/1792936692635_f1pj5/` on hfeg0pkn001
**ledger session**: `1792936692635_f1pj5` (was parked 2026-11-10 23:23 "consultation what-is-DSA")

## 用户意图（原话）
1. `<user_input mode="act">DSA</user_input>`
2. `<user_input mode="act">如何评估DSA</user_input>`

用户给了一个极其简短且有歧义的缩写「DSA」并问「如何评估DSA」。典型 explain+how-to Q&A 真实意图（11-15 用户令 reaudit 后恢复可造，旧判 "reject consultation what-is-DSA" r435）。

## Agent 工具链
`list_allowed_files` → `skills(aether-tool-qa)` → `search_codebase` → `list_allowed_files(/Desktop/references)` (ENOENT) → `skills(ask-eda / cimi-kb-search / aether-tool-qa)` 多轮 → `read_files(/home/jingc/Desktop/.temp.drf)` (空返回) → `run_approved_command(ask_eda.py ask ...)` ×3 → `run_approved_command(cimi-kb-search retrieve ...)` (RAGFlow API Key 未配置, 失败)。

## 关键 AskEDA 回答（从 trace tool_results verbatim 提取）
1. **msg[19] askeda "DSA 是什么 在EDA芯片设计领域"** → `knowledge_base_used=false`, `retriever_resources=[]`。LLM 自由生成，解释 DSA = **Directed Self-Assembly**（定向自组装，BCP 嵌段共聚物光刻技术，SCFT/MC/工艺窗口/缺陷率/DRC/良率六维评估）。**无 KB 命中 → 不可信**。
2. **msg[23] askeda "Aether EDA DSA Design Style Analysis 是什么 如何评估"** → `knowledge_base_used=true`, `retriever_resources=[{document_name:"Aether_Manual.pdf", score:0.853515625}]`。**KB 命中 → 权威**。解释 DSA = **Design Style Analysis**（Aether 版图编辑器 DRD 设计规则驱动检查，Spacing/Width Rule，红/白颜色编码，操作步骤：启用 DRD→设检查类别→执行分析→解读结果→优化迭代）。
3. **msg[26] askeda "Aether DSA Design Style Analysis 功能 操作步骤 菜单 参数设置 详细说明"** → `knowledge_base_used=true`, `retriever_resources=[{document_name:"Aether_Manual.pdf", score:0.87109375}]`。详细操作步骤：Setup/Analysis 菜单，Design Tree(Parameters/Model Libraries/Simulation Files/Stimuli)，参数(Stop=10u/Errpreset=moderate/Op Param=vcp_out Start=0.6 Stop=1.2 Step=0.1)，分析类型(TRAN/AC/DC/Mixed-Signal)，Results/Direct Plot。

agent 最终（msg[27]）选 **Design Style Analysis** 解释，理由：①工作区是 Aether 上下文(.temp.drf/sxcmd.log) ②KB 命中(Aether_Manual.pdf) 的回答是 Design Style Analysis ③Directed Self-Assembly 回答无 KB 命中。这是正确的消歧逻辑。

## 案例合成（A 档 trace-faithful + 产出生成式 explain/how-to 指南）
- **case_id**: `EDA-Eval-DesignFlow-DsaEvalExplainQA-001`
- **domain**: spice_sim (ledger 分类；DSA 在 Aether = 设计/仿真 setup 分析，characterization 邻接)
- **archetype**: explain-Q&A + how-to-Q&A → produce (revival #79 from pool_reaudit_B)
- **A 输入** (SUT 可见, `doc/`): `workspace_listing.json`(Aether Desktop: .temp.drf/sxcmd.log) + `askeda_answer_design_style.txt`(msg[23] KB 命中 Aether_Manual.pdf) + `askeda_answer_directed_self_assembly.txt`(msg[19] KB 未命中, 干扰项) + `askeda_answer_detail_steps.txt`(msg[26] KB 命中详细步骤) + `requirements.json` + `scenario.txt` + `task_brief.md`
- **B 输入** (hidden cross-input guard): **光刻/OPC 工程师**上下文(workspace: opc_recipe.lbc/bcp_process.json/guide_pattern.gds/mask_floorplan.oas) + `askeda_answer_b_dsa_litho.txt`(KB 命中 Litho_Process_Handbook.pdf score 0.91, DSA=Directed Self-Assembly) + `askeda_answer_b_ambiguous.txt`(Design Style Analysis, KB 未命中, 干扰项 B 应拒绝) + `askeda_answer_b_detail.txt`(KB 命中光刻详细步骤) + `requirements.json`。任务=同一个模糊问题「DSA 是什么/如何评估 DSA」，但 B 的正确答案=Directed Self-Assembly(非 A 的 Design Style Analysis)。
- **任务**: 写 `dsa_eval_guide.py(workdir,out_dir)` 读 `doc/` 输入，按工作区信号 + KB 命中回答消歧 DSA 含义，产 `dsa_eval_guide_report.json`(14 顶层键)。
- **check.py**: 25 条独立断言 (k_check==k_rationale==25, ≥8 硬闸门)
  - a0-a4 (5): zip 存在/含脚本/可编译/B 输入齐全/analyze 可调用产 JSON
  - a5 (1): 3 次重跑 sha256 一致(确定性)
  - a6-a7 (2): JSON dict / 14 顶层键齐全
  - a8-a9 (2): dsa_full_name=='Directed Self-Assembly'(B 正确) / dsa_meaning 含 BCP/自组装
  - a10 (1): disambiguation_rationale 引用光刻上下文 + KB 命中
  - a11-a12 (2): evaluation_methods >=6 项 / method_categories 覆盖 B 必需集 >=5
  - a13 (1): kb_grounding 引用 Litho* 手册, 不引用 Aether_Manual.pdf
  - a14 (1): context_evidence 引用 >=2 个 B 工作区文件
  - a15 (1): workflow_steps >=5 步
  - a16 (1): parameters 含 >=3 个 B 专属参数(PS-b-PMMA/BCP/guide pattern/LWR/CD)
  - a17 (1): A-leak guard: 不含 A 专属 token(Aether/Design Style Analysis/.temp.drf/DRD/Spacing Rule 等 20 token)
  - a18 (1): B-grounding guard: 含 >=6 个 B 专属 token(Directed Self-Assembly/BCP/PS-b-PMMA/SCFT/guide pattern/LWR/光刻/自组装/Litho_Process_Handbook/opc_recipe)
  - a19 (1): caveats >=2 项
  - a20 (1): conclusion 长度>30 且提及 DSA
  - a21 (1): report_overview 提及光刻项目/工具族
  - a22 (1): methodology 引用 AskEDA 输入 + workspace_listing
  - a23 (1): deliverable_checklist >=4 项
  - a24 (1): 报告不含 'Design Style Analysis'(A 解释未泄漏)
- **negative samples**: 4 个 (stub_empty / stub_print_only / stub_hardcode_a / stub_deleted_core)
- **自验**: ref 25/25 PASS on B + 4 negatives 全 FAIL ✓ + 双向验证(ref 跑 A 得 Design Style Analysis, 跑 B 得 Directed Self-Assembly ⇒ 非硬编码) ✓
- **cross-input guard**: A=Aether/Design Style Analysis/Aether_Manual.pdf, B=光刻/Directed Self-Assembly/Litho_Process_Handbook.pdf；A-leak 20 token / B-grounding 10 token，互斥

## 关键 quirk / 注意事项
- trace 文件在子目录 `1792936692635_f1pj5/` 下（非根 .messages.json），scp 直路径会失败，需 `find` 子目录（同 m40h5/5kysh/6ipfr 模式）
- B 故意选光刻/Directed Self-Assembly 而非 Aether/Design Style Analysis — 测试 SUT 是否真的从 workspace 文件 + KB 命中回答消歧，而非硬编码 "Design Style Analysis"
- B 的干扰项 askeda_answer_b_ambiguous.txt 是 "Design Style Analysis" 但 knowledge_base_used=false — 测试 SUT 是否只信任 KB 命中的回答
- .oas(OASIS 掩膜文件) 不能误匹配 Aether 信号 .oa — 参考解用 word-boundary 正则避免（B workspace 含 mask_floorplan.oas）
- cimi-kb-search 在 trace 中因 RAGFlow API Key 未配置失败(msg[24]) — 不影响 case（case 只用 AskEDA 回答）
