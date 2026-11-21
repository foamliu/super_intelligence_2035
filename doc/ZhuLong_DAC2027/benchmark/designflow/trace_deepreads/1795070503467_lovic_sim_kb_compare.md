# trace_deepread: 1795070503467_lovic (zqzhan / hfeg0plg94, mc33, spice_sim)

## 用户意图 (msg 逐字)
> nanospice你了解吗，和finesim、hspice等的差异

用户 zqzhan @ hfeg0plg94 在做 FineSim/HSPICE 仿真，想搞清楚 NanoSpice 这个仿真器与 FineSim/HSPICE 等的差异。session 共 26 条消息，spice 仿真相关占比 ~0.21（hspice:131 / aether:200 / mixed-signal:66 hits），属 low-mc B-pure analysis-Q&A 形态（mc=33，11-15 重审后合法）。

## agent 检索流 (trace 复刻)
1. 先尝试 **AskEDA** skill（Dify RAG 检索 EDA 知识库）→ 当前禁用（desktop app Settings 未配 dataset/API key）
2. 再尝试 **cimi-kb** 知识库检索 → 无可用 dataset
3. 回退到 **grep 本地 Aether 知识库** 三份文件：
   - `aether_tool_qa.md`（交流群问答 + 经验沉淀）
   - `part_VI_Mixed-signal_Design.md`（Aether MDE 手册 Part VI）
   - `ask_eda_skill.md`（AskEDA 技能说明）
4. 在三份文件里 grep 仿真器关键词（alps / hspice / finesim / nanospice / spectre / alps-ms / alps-cs）

## 检索结论 (agent 分析)
- **MDE 支持的仿真器**（来自 part_VI 手册 71.1）：MDE 声明支持 **4** 种仿真器 — Alps（Aether 自研 fast-SPICE）/ Hspice（Synopsys 高精度 golden）/ Alps-MS（混合信号）/ Alps-CS（协同仿真）。配置入口菜单 `Setup -> Netlist/Directory`。**无 Spectre，无 NanoSpice**。
- **FineSim 实操细节**（来自 aether_tool_qa 交流群问答）：
  - LSF 队列：`fqueue2h`（限时 2 小时，短仿真）/ `fqueue3`（不限时，常 pend，长仿真）
  - 波形加载工具：`wv`，单服务器实例上限 **2**，超过后热键 `ctrl+w` 失效，需手动 kill 旧 wv
- **NanoSpice 检索结论**：
  - 在 `ask_eda_skill.md` 示例里被提及（"Query 'NanoSpice 是什么仿真器？' → retrieves NanoSpice_X_User_Guide.pdf"）— 即 AskEDA 可查
  - 在本地 Aether 手册与交流群问答中 **无任何记录**（本地 KB 无 NanoSpice 手册条目）
- 仿真器对比：Alps=Aether 自研 fast-SPICE / Hspice=Synopsys 高精度 / FineSim=Synopsys fast-SPICE(LSF 提交) / NanoSpice=本地无记录仅 AskEDA 可查

## 本 case 物化
**form = 参数化 KB 检索 + 仿真器对比报告生成器**（Python `kb_compare.py` 读 `<kb_dir> <out_report.md>`，在三份标准命名 KB 文件里检索并生成结构化 markdown 对比报告）。

reframe = harness-for-teeth：trace 原意图=一次性 Q&A 回答 NanoSpice 差异；判分有牙需可重跑可换输入，故 reframe 成 produce 参数化 `kb_compare.py`。A 档 trace-faithful（用 zqzhan 原话 + 三份真实 KB 文件 aether_tool_qa_A / part_VI_Mixed-signal_Design_A / ask_eda_skill_A）；hidden B 异事实（5 仿真器含 Spectre / FineSim 队列 fqueueA+fqueueB / 波形工具 wvX 上限 3 热键 ctrl+q / ask-eda skill 无 NanoSpice 提及）→ anti-hardcode-A。

## 资产
- **A（可见）** `assets/EDA-Eval-DesignFlow-SimKbCompareGen-001/`：
  - `aether_tool_qa_A.md` — 4 sim/Alps,Hspice,Alps-MS,Alps-CS/fqueue2h+fqueue3/wv,2,ctrl+w/nanospice-in-askeda
  - `part_VI_Mixed-signal_Design_A.md` — MDE supports exactly 4 simulators + 菜单 Setup -> Netlist/Directory
  - `ask_eda_skill_A.md` — NanoSpice 在示例里被提及
- **B（隐藏）** `assets/.../hidden/`：
  - `aether_tool_qa_B.md` — 5 sim(含 Spectre)/fqueueA+fqueueB/wvX,3,ctrl+q
  - `part_VI_Mixed-signal_Design_B.md` — MDE supports exactly 5 simulators (Alps/Hspice/Alps-MS/Alps-CS/Spectre)
  - `ask_eda_skill_B.md` — **无** NanoSpice 提及（仅 FineSim/Spectre 示例）
  - `hidden_manifest.json` — suffix→standard-name 映射 + B 差异说明

## 判分
**check.py 14 条 a-n**（k_rationale == k_check == 14 ≥ 8 硬闸门）：
- (a) submit.zip 有效且解压后顶层含 kb_compare.py
- (b) kb_compare.py 通过 py_compile
- (c) 在可见 A KB 上以 `python3 kb_compare.py <kb_dir> <out>` 运行 exit 0
- (d) report_A.md 产出且非空（≥100 字符）
- (e) report_A 含全部 4 个 MDE 仿真器名（Alps/Hspice/Alps-MS/Alps-CS）
- (f) report_A 声明 MDE 仿真器数量 = 4
- (g) report_A 含 FineSim LSF 队列 fqueue2h 与 fqueue3
- (h) report_A 含波形工具细节 wv / 上限 2 / 热键 ctrl+w
- (i) report_A 同时提及 NanoSpice 与 AskEDA
- (j) report_A 含 MDE 菜单路径 Setup -> Netlist/Directory
- (k) report_A 仿真器对比表 ≥4 行
- (l) report_A 含检索状态节且提及 ≥2 个源
- (m) report_A 明确指出本地 KB 无 NanoSpice 手册条目
- (n) **反硬编码 A（cross-input guard）**：在隐藏 B（5 仿真器含 Spectre / fqueueA+fqueueB / wvX 上限 3 热键 ctrl+q / ask-eda 无 NanoSpice）上重跑，report_B 必须反映 B 的事实且不得泄漏 A 的 fqueue2h/fqueue3/独立 wv/ctrl+w

## 自验
- reference_submit.zip（=kb_compare_ref.py 改名）→ check.py **PASS 14/14**（A 报告 4 sims/fqueue2h,fqueue3/wv,2,ctrl+w/nanospice-in-askeda/本地无记录；B 报告 5 sims+Spectre/fqueueA,fqueueB/wvX,3,ctrl+q/nanospice-absent/本地无记录）
- §4.9 三假 + hardcode_a 负样 **4/4 FAIL**：
  - neg_empty.py（空脚本）→ cond d FAIL（report_A 未产出）
  - neg_print_expected.py（直接打印 A 预期报告）→ cond n FAIL（report_B 缺 Spectre）
  - neg_core_deleted.py（删核心检索逻辑，占位报告）→ cond d FAIL（report_A 太短 17 字符）
  - neg_hardcode_a.py（硬编码 A 事实）→ cond n FAIL（report_B 缺 Spectre，泄漏 A）
- JSON round-trip 验证：从 cases/B json 提取 check.py 字节 → 跑 reference_submit.zip → PASS（字节级一致）

## 落库
- cases/B 494 → 495（`cases/B/EDA-Eval-DesignFlow-SimKbCompareGen-001.json`）
- B.jsonl 492 → 493（build_jsonl.py --shard B 重建）
- ledger_B case 654 → 655（lovic mark case）
- spice_sim 域
- mc≥10 fresh 277 → 276（claim lovic）
- 总断言 +14

## 备注
- form 新增：KB-grep + 结构化对比报告生成器（同 r970 GenguiToolkitProvenanceAnalyze 的 provenance 解析、r967 XtalkDeepDfsProvenanceAnalyze 的 deepDFS 解析同属 analysis-Q&A→参数化生成器 reframe 谱系，但本 case 是 **检索/对比** 而非 provenance/解析）
- A/B 资产用 `_A`/`_B` 后缀存储，check.py 用 `_stage_kb` 临时目录重命名为标准名（aether_tool_qa.md 等）再喂给 candidate，保持 SUT 契约简洁（candidate 只认标准名）
- NanoSpice 在 A 档 ask-eda skill 有提及、B 档无提及 — 这一差异是 cross-input guard (n) 的关键牙之一（hardcode A 的脚本会在 B 上误报 NanoSpice-in-askeda）
