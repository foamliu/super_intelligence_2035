# 深读笔记 — trace 1791017602459_fwgyy（FineSim 自主仿真工作流形成）

## 元数据
- session: `1791017602459_fwgyy.messages.json`
- user: `zjqiao` @ `hfhds206` (10.129.32.80)
- match_count: 221；messages: 198；size: ~1.5MB
- domain: spice_sim（shard B）
- keywords: netlist:2652; aether:269; hspice:268; cellview:222; pyaether:67; spectre:52; virtuoso:44; lib.defs:21
- tool 序列: editor:35, read_files:27, list_allowed_files:20, RAG_search_apis:16, RAG_get_api_details:10, run_commands:2(被拒), run_approved_command:2(被拒), skills:1

## 真实对话流（逐轮用户意图）
1. **U#1 idx=0（需求轮，A 档候选）**：「你能否自己形成一个工作流进行finesim仿真」
   - 纯目标表达，未给根因/修复 → 符合 A 档选轮规则。
   - 意图：让 agent 自主形成一个可复用的 FineSim 仿真工作流（不是单次跑一个仿真，而是"形成工作流"）。
2. 之后用户无更多需求轮（其余为 agent 自主推进 + 工具结果）。
3. 末尾 agent 自宣"工作流完成"，**用户未明确接受** → B 档 synthesized（金标准由 .75 标定，子技能忠实）。

## agent 实际做了什么
- 环境：`run_commands`（raw shell）被禁用；`run_approved_command` profile `hello_world` **DENIED**（uid 不匹配 10741 vs 200329）→ **agent 全程无法执行任何 shell / 仿真命令**。
- 唯一可用执行通道：`RAG_MCP_Server__search_apis` / `get_api_details`（查 pyAether API）、`editor`（写文件）、`skills`（skill-creator）。
- agent 通过 RAG 检索到 pyAether MDE（Maestro）API 全集：`MdeSession`/`MdeSetting`/`MdeDcAnalysis`/`MdeTranAnalysis`/`MdeAcAnalysis`/`MdeStbAnalysis`/`MdeNoiseAnalysis`/`seGuiRunSimulation`/`MdeResult`/`cdfGetSimInfo`/`emyInitAether`。
- 交付两文件（均经 editor 多次 insert/patch 拼出，从未执行）：
  1. `/home/zjqiao/Documents/Cline/Workflows/finesim_simulation_workflow.SKILL.md` — 工作流定义（目标/验收 5 条/资源边界/两种仿真方式 MDE State vs 命令行/API 速查 9 个/方法论/输出规格/7 个已知陷阱）。
  2. `/home/zjqiao/finesim_workflow.py` — `FineSimWorkflow` 类，8 阶段：`init_aether`→`open_session`→`add_model_file`→`configure_dc/tran/ac/stb/noise_analysis`→`run_simulation`(netlistAndRun)→`save_results`(detail/summary/transpose CSV)→`create_netlist`(调试)→`close_session`。CLI 入口 `--lib --cell --state`。
- 最终"语法验证" `run_approved_command` 仍 DENIED → **脚本从未跑过、从未产生任何仿真结果**。

## distinct vs 已有 B spice_sim case
- FineSim 三 case：gvm3g='can't find model' 修复 / hk622='no reference ckt' 修复 / uky6c=DC 不收敛诊断修复 / cllpy='cannot open include' RCC 路径诊断。
- 本条 = **自主 FineSim 仿真工作流生成器/运行器（netlist→配置多分析→run→parse→CSV 报告）**，交付"工作流脚本"而非"修复器/诊断器"。shard B 首个"workflow generator/runner"子技能，distinct ✓。

## 便携化方案权衡（关键）
- trace 原路径 = pyAether **MDE (Maestro) Session** GUI API 驱动 FineSim。.75 上 eda_flow `run_code(lang=pyAether, host=aether)` 提供 pyAether，但 MDE Maestro session headless + foundry model 链路未验证，calibration 风险高。
- **便携 reframe（推荐，B 档 synthesized）**：保留"自主 FineSim 工作流"意图，交付 = Python `finesim_workflow.py`，给定 netlist.sp + 模型，经 **subprocess 调 `finesim`**（shell 路径，.75 已验证可用，见 FineSimDcConvFix-001）→ 配置 DC/Tran/AC 多分析（多 .control 块或多次跑）→ 解析 .lis/.tran0/.ac0 → 落 detail/summary/transpose CSV + run_report.json。
  - 候选 `finesim_workflow_ref.py`（CLI `<netlist.sp> <model.sp> <out_dir> [--analyses dc,tran,ac]`：构造 testbench 含 .dc/.tran/.ac + .measure → 跑 finesim -spice → 解析 .measure 结果 + .lis 状态 → CSV + workflow_report.json{analyses_run, converged, measures, csv_paths}）。
  - check.py ≥8 条：subprocess+finesim 真跑 / 三分析全跑 / .measure 解析 / CSV 三件齐全 / converged 无 non-conv / name-agnostic / 跨输入守卫 / report.json 字段 / 三假全 FAIL / negatives。
  - GT：A/B 用 level-1 Shichman-Hodges MOS（反相器 + RC）不同 sizing/vdd/节点名，.75 FineSim -spice 标定。
- **DEBT:1**：本轮仅深读 + 选定便携 reframe，未合成（calibration + check + negatives 需 dedicate 一轮）。**下轮第一件事**：.75 上验证 `finesim -spice` 跑 level-1 反相器 DC+Tran+AC 三分析一把过 → 标定 A/B GT → 合成 FineSimWorkflowGen-001 → 自验 → jsonl。

## 选轮 A 档可行性
- U#1 逐字原文「你能否自己形成一个工作流进行finesim仿真」可作 A 档任务说明（仅掩码无 key）。
- 但 A 档需 trace 末尾用户实际接受的结果作金标准 → 本 trace 用户未接受、无真实产物 → **A 档不可行**，走 B 档 synthesized（子技能忠实，金标准 .75 标定）。

## 结论
- ledger: claimed → deepread。DEBT:1。
- 下轮 synthesize FineSimWorkflowGen-001（spice_sim, B档 synthesized, L2, k≥8）。
