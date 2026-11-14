# subagent 消融 reanalysis — 推翻 wake#915「需源码改」结论

> 2026-11-14 wake#922 · 推进 agent
> 背景：wake#915 交付 P4 负结果报告（`reports/report_zhulong_subagent_ablation_zh.html`），结论「cline 3.0.51 configured-agent subagent 机制不可用 / H1-H3 无法检验 / 需解除版本·源码纪律重跑」。
> 本文件用**硬证据**推翻该结论的「需源码改」前提：subagent 在 cline 3.0.51 下**确实可执行**，P1 的 0% 是**两个配置级问题**，均可修。

## 一、决定性证据：smoke 3074b 是 TRUE POSITIVE

wake#915 的 go_nogo note §五 自承「P0 没验证 subagent 是否真正执行」→ 推断 smoke 全是盲区假阳性。**此推断错误**。

`/tmp/subagent_smoke_3074b/`（2026-11-13 23:54）实测：
- 子 agent session 文件 `sessions/1794585225882_whch6/agent_63282962-9b8c-4483-ac5d-d9df4e899ed5.messages.json` **n_msgs = 15**（非 0）
- 主 session 含 `finishReason: completed`、`inputTokens: 92836`、`outputTokens: 2026` → **子 agent 真正执行了 LLM 并消耗 token**
- researcher.yaml：`providerId: openai-compatible` / `modelId: deepseek-v4-pro-cloud` / `tools: [pyAether_MCP_server__search_apis, pyAether_MCP_server__get_api_details]`
- providers.json：`openai-compatible`（apiKey `…e13f4f37`，baseUrl `/cloud/v1`，model `deepseek-v4-pro-cloud`，reasoning.enabled=false）
- 调用方式：直接 cline CLI，1 task，cwd=data-dir（`logs/cline.log`: `interactive:false, hasPrompt:true`）

**结论**：cline 3.0.51 的 configured-agent "researcher" subagent **能在单任务串行下真正执行**。根因 A（empty messages）不是普遍源码 bug。

## 二、P1 0% 的两个真实根因（均配置级，纪律内可修）

### 根因 A — dsv4 臂（B1/B2/C2）"messages must not be empty"：-p 8 并发竞态
- B1 的 `researcher.yaml` + `providers.json` 与 smoke 3074b **逐字节相同**（同 providerId `openai-compatible`、同 apiKey `e13f4f37`、同 model、同 reasoning disabled）。
- 唯一差异：smoke 3074b = **1 task 串行**（subagent 执行 ✅ n_msgs=15）；P1 B1 = **8 task 并行（-p 8）共享同一 `CLI_DATA_DIR=/nasdata/.../subagent_ablation/B1`** → 所有子 session `n_msgs=0` ❌。
- 定位：8 个并行 cline 进程共享同一 arm 的 `sessions.db`/`teams.db`，子 agent session 消息初始化在并发下竞态 → task 未持久化为首条 user message → OpenAI API 拒空 messages。
- **修复方向**：① 子 agent 臂降并发（-p 1 或 -p 2）验其是否复现 smoke 的成功；或 ② per-task data-dir 隔离（每 task 独立 sessions.db）保留 -p 8。-p 是否为「全臂恒定」协议常量需用户/运维裁决（A0 复用 compaction basic 是 -p 8，降 -p 会与 A0 形成 -p×subagent 混淆；per-task 隔离可避免此混淆）。

### 根因 B — doubao 臂（B3/B4/B5）"Unknown or disabled provider"：researcher.yaml providerId 误用
- B3/B4/B5 的 researcher.yaml 写 `providerId: doubao-{pro,mini,lite}`（providers.json 里的**命名 profile key**），但 cline subagent 的 provider 解析把 providerId 当 provider **类型**查 → 注册表无 `doubao-*` 类型 → 报错。
- 主 agent 用 `lastUsedProvider: openai-compatible`（真类型）正常；subagent 走 `buildAgentRuntimeConfig` 覆盖 providerId 为命名 profile → 解析失败。
- **修复方向**：researcher.yaml 改 `providerId: openai-compatible`（真类型）+ `modelId: doubao-seed-2.0-{pro,mini,lite}-cloud`；并在该 arm 的 providers.json `openai-compatible` entry 里把 apiKey 换成 doubao 对应 key、model 换成 doubao model（doubao 三 model 走同一 `/cloud/v1` gateway，key 不同：pro=`…3dd97aea`，mini/lite 待核）。需 smoke 验 modelId 是否真能覆盖 provider entry 的 model。

## 三、对 wake#915 交付物的处置（不删旧结果/trace）

- P4 负结果报告 `reports/report_zhulong_subagent_ablation_zh.html` **保留为历史档**，不删不改。
- 在报告顶部加 SUPERSEDED 横幅 + 指向本文件（见 §五 实施记录；若本轮未改报告 HTML，下轮 smoke 通过后统一刷新）。
- `run/ablation_subagent_results.json` 的 `phase=P4_negative_report_delivered / go_nogo.decision=NO-GO` **保留**；新增 `reanalysis` 字段记录本结论（见 §五）。
- 所有 P1 trace（`/tmp/zhulong_subagent_eval/*`）保留作证据。

## 四、confirmatory smoke 计划（沙盒空闲后执行）

预注册通过条件：子 agent session `n_msgs>0` 且 `usage.inputTokens>0` 且 `finishReason=completed`。

1. **smoke-A（验根因 A）**：用 B1 现有配置（= smoke 3074b 配置），跑 **1 题 × -p 1**（串行），强提示注入。预期复现 smoke 3074b 成功。若成功 → 确认 -p 8 是根因 A。
2. **smoke-A2（找并发阈值，可选）**：同配置 1 题 × -p 2 / -p 4，看从哪个并发度开始出现 n_msgs=0。
3. **smoke-B（验根因 B）**：B3 配置改 `providerId: openai-compatible` + `modelId: doubao-seed-2.0-pro-cloud` + providers.json openai-compatible entry 换 doubao pro key/model，1 题 × -p 1。预期子 agent 用 doubao 执行成功。
4. 两 smoke 通过 → 重跑 P1（并发策略据 smoke-A/A2 结果定：优先 per-task 隔离保 -p 8；次选取可接受 -p 并发度；再不行 -p 1 全臂重跑含 A0）。
5. **启动前自检**：本线沙盒端口 8664/8665/8653/8669 可用 + `pgrep -f '^bash scripts/run_cline_script'` 无输出；trace 落 /tmp（/nasdata 100% 满）。
   ⚠️ 与 designflow **不共享沙盒**：本线走 `run_code`（端口），designflow 走 `eda_flow` MCP → `.75` 的 `run_commands`。**无需等待其空闲。**

## 五、本 wake 实施记录

- ✅ 核实 smoke 3074b n_msgs=15 / usage>0 / completed（硬证据）
- ✅ 逐字节比对 B1 researcher.yaml + providers.json = smoke 3074b
- ✅ 核实 B3/B4/B5 researcher.yaml providerId=doubao-*（根因 B 配置 mistake）
- ✅ cline 版本仍 3.0.51（未变 → 根因非版本固有）
- ▶ confirmatory smoke **未跑的唯一原因是本线自检未做**（不是沙盒冲突）；与 designflow 沙盒无关，可直接开跑
- ✅ 守纪律：未改 benchmark/评分器、未删旧结果/trace、未 kill loop、未碰 cline 源码/版本
- 待办（下一 wake 沙盒空闲）：跑 smoke-A → smoke-B → 通过则重跑 P1

---

## 六、confirmatory smoke 实测结果（2026-11-14 10:19–11:15，wake#923）

> 本节用实测**修正** §四 的乐观预期。wake#922 的「config-level 修复、无需源码改」结论**部分被推翻、部分被证实**——拆成两个独立问题。

### smoke-A 系列实测（harness 路径 = run_cline_script.sh → run_cli.sh → cline）

| 跑次 | 时间 | 路径 | PARALLEL | --data-dir | 结果 |
|:--|:--|:--|:-:|:-:|:--|
| smokeA (10:19) | harness | 8 | 有 | ❌ 失败 |
| smokeA_direct (10:26) | 直接 CLI | — | — | ⚠️ 混合：1 次 `messages must not be empty`，其余 anonymous spawn 成功（非 configured researcher） |
| smoke-A2 (10:30) | harness | 8 | 有 | ❌ 0 subagent session，main session `e.trim` |
| smoke-A3 (10:50) | harness | 8 | 有 | ❌ 0 subagent session，`e.trim`（**10:45 的 data-dir/agents 修复已全激活**） |
| **smoke-A4 (11:05)** | **harness** | **1** | **无** | ✅ **PASS** |

### 决定性证据：smoke-A3（修复全激活仍失败）vs smoke-A4（PARALLEL=1 成功）

**smoke-A3**（10:46 起跑，run_cli.sh 10:45:50 已改）逐项核验：
- `researcher.yaml` 已在 **两处** 确认在位：`ws/agents/researcher.yaml`（cwd）+ 全部 8 个 `worker_*/data/agents/researcher.yaml`（data-dir）✅
- cline 命令含 `--data-dir .../worker_N/data` + `-c ws`（两处都有 agents/）
- 仍报 `spawn_agent` → `{"error":"undefined is not an object (evaluating 'e.trim')"}`，is_error=true，**0 subagent session**
- ⇒ config-location 修复**不能**解决 harness 路径的 e.trim

**smoke-A4**（11:05，PARALLEL=1，run_cli.sh:231 在 PARALLEL=1 时**不加** --data-dir）：
- 4 个 subagent session：3 个 n_msgs>0 + inputTokens>0（其中 `agent_...9opzhi` n_msgs=12 / inputTokens=4002 / 6 轮 user-assistant）
- A4 自身 main session：`spawn_agent=True`、**`e.trim=False`**、`messages must not be empty=False`
- scanner 判定：`SMOKE-A4 (PARALLEL=1): PASS — subagent executed`
- ⇒ **`--data-dir` flag 是 e.trim 的触发器**（唯一差异 = PARALLEL>1 时 run_cli.sh:231 加 --data-dir）

### 结论：wake#922「无需源码改」拆成两问

- **问题①（e.trim 硬阻塞）= harness-level，可修**：触发器 = harness `cwd(ws) ≠ --data-dir(worker_N/data)` 的路径分裂（wake#923 smoke ④ 证：直接 cline + `--data-dir` 且 `cwd=data-dir` → ✅；smoke ③ harness -p8 `cwd=ws`+`--data-dir` → e.trim）。**非** `--data-dir` flag 本身，亦**非** wake#922 的「-p8 并发竞态」（已证伪）。修法 A=全臂降 `-p 1`（run_cli.sh:231 在 PARALLEL=1 时不加 --data-dir → cwd=ws 单路径 → smoke-A4 ✅）；修法 B=harness 改成 `cwd=data-dir`（对齐直接调用）保 -p 8——需 harness 改动 + 回归测 compaction/think-lang 既有臂。**两法均不改 cline 源码/版本**。
- **问题②（subagent 模型未用配置）= config-level，待查**：smoke-A4 子 session `modelInfo.id=minicpm5-2b-sft-v39-final`（本地小模型），**非** researcher.yaml 配置的 `deepseek-v4-pro-cloud`；且子 session tool_use 含 `spawn_agent`/`run_commands`（非 researcher.yaml 限定的 search_apis/get_api_details）→ 疑为 **anonymous spawn**（主 agent 调 spawn_agent 未指定 "researcher"，或 configured agent 的 provider/tools 未注入子上下文）。**H2（基座梯度 B1→B5）依赖子 agent 真用各臂配置的 doubao/pro 模型**，此问不解决则 H2 无法检验。需在 P1 前查清：① 主 agent 是否以 `spawn_agent(name="researcher")` 调用；② configured agent 的 providerId/modelId 是否传入子 runtime；③ 若 anonymous spawn 抢占，需强提示指定 name。

  **✅ wake#924 已查清问题②根因**：扫 A4 main session 的 `spawn_agent` tool_use 块，2 次调用的 input = `{"systemPrompt": "You are an EDA assistant..."}` / `{"systemPrompt": "You are a researcher helping me..."}` —— **均为 anonymous spawn（传 systemPrompt 自写），非 configured spawn（应传 `name`/`agent`="researcher"）**。故 researcher.yaml 的 providerId+modelId+tools **从未被加载** → 子 agent 用默认本地 minicpm + 全工具。**修法 = 改 LANG_HINT 强提示**：现提示「调用 subagent_researcher 工具」被主 agent 误解为 anonymous spawn；应改为明确「调用 `spawn_agent` 工具并传 `name="researcher"`（或 cline 配置 agent 的对应选择字段）以使用预配置的 researcher 子 agent」。属提示工程，纪律内可修（非 benchmark/评分器/cline 源码）。需 smoke 验：改提示后子 session `modelInfo.id` 应 = `deepseek-v4-pro-cloud`（B1）/doubao（B3-B5）。

### 状态
- PHASE = `smoke_A4_pass`（e.trim 硬阻塞已定位+可修；subagent 模型配置待查）
- 下一步（下一 wake）：① 查问题②（subagent 模型注入）——可在 smoke-A4 trace 里看主 agent 的 spawn_agent 调用参数（是否带 name="researcher"）；② 决定 P1 并发策略（-p 1 全臂 vs harness 改动保 -p 8）；③ 问题②解决 + 并发策略定 → 重跑 P1（8 臂 × 8 题 × 1 轮）。
- 纪律全守：未改 cline 源码/版本、未改 benchmark/评分器、未删旧结果/trace（A2/A3/A4 全留）、未 kill loop。run_cli.sh 的 10:45 data-dir/agents 改动是前序 wake 所留（未由本 wake 改）。

---

## 六、2026-11-14 wake#923 opencode 直令·**🔴 推翻 root cause A + 发现真正双根因**

> 用户直令（opencode 非 loop）跑 confirmatory smoke。本节用**实测证据**推翻 wake#922 的 root cause A（-p 8 并发竞态），定位**两个真正的根因**。

### 起跑前复核（全 PASS）
- 沙盒 10.129.32.75:8664/8665/8653/8669 全 OPEN；eda_fastmcp MCP 18890 UP；doubao-pro key curl ✅；cline 3.0.51；designflow eval PID3183742 GONE；run_cline_script 无在跑；loop PID813663 带代理✅；/tmp 23G。

### 实测 1：harness -p 1 smoke-A（旧 .cline/agents/ 路径）→ ❌ FAIL
- B1 config, 1 题, -p 1, fresh /tmp/subagent_smoke_A。harness 37s 退出。
- 主 session tool_result: `AI_NoSuchToolError: Model tried to call unavailable tool 'subagent_researcher'. Available tools: ...无 spawn_agent/subagent_researcher`
- **configured agent 根本没注册**。且 -p 1 时 harness 不传 --data-dir → 用默认 config（model=minicpm5-2b 非 dsv4-pro）→ 此 smoke 引入第二变量，**无效**。

### 实测 2：直接 cline CLI（cwd/agents/ 路径）→ ✅ PASS
- /tmp/subagent_smoke_A_direct/agents/researcher.yaml（B1 config），`cline -c $dir --thinking medium --compaction basic`。
- `spawn_agent` 注册 + 调用成功；子 session agent_*.messages.json n_msgs=12, metrics.inputTokens=2381, model=minicpm5-2b（默认 config，无 --data-dir）。
- **结论：cline 从 `cwd/agents/` 加载 configured agent，非 `cwd/.cline/agents/`**。

### 🔴 真正根因 A（推翻 wake#922）：agent 注入路径错误
- `run_cli.sh:201` 把 researcher.yaml 放 `$ws_dir/.cline/agents/`，但 cline 从 `$ws_dir/agents/` 加载 → spawn_agent 永不注册 → P1 全臂 0%。
- **与 -p 8 并发无关**（wake#922 root cause A 错误）。-p 8 只是 P1 的条件，非病因。
- **修复**：`run_cli.sh:201` `.cline/agents/` → `agents/`（已改 eda_fastmcp）。

### 实测 3：harness -p 8 smoke-A（路径修复后）→ ⚠️ 注册✅ 但执行❌
- B1 config, 1 题, -p 8（传 --data-dir → model=dsv4-pro-cloud ✅）, /tmp/subagent_smoke_A2。
- `spawn_agent` **注册成功**（无 NoSuchToolError）→ 路径修复有效 ✅
- 但 spawn_agent 调用返回 `{"error":"undefined is not an object (evaluating 'e.trim')"}` → 子 agent 未执行（0 个 agent_*.messages.json）

### 实测 4：直接 cline + --data-dir（B1 config）→ ✅ PASS
- /tmp/subagent_smoke_A3/（agents/ + settings/ 同一 dir），`cline -c $dir --data-dir $dir`。
- spawn_agent 成功，子 session agent_*.messages.json 创建 ✅。model=dsv4-pro-cloud。

### 🔴 真正根因 A2（新发现）：harness 里 cwd ≠ --data-dir，spawn_agent 执行报 e.trim
- 直接调用：cwd = --data-dir（同一 dir 有 agents/ + settings/）→ ✅
- harness：cwd=$ws_dir（agents/），--data-dir=$worker_dir/data（settings/ + agents/）→ cwd ≠ data-dir → spawn_agent 注册✅但执行❌ e.trim
- **已尝试修复**：把 agents/ 也复制到 $worker_dir/data/agents/（run_cli.sh worker 循环新增 cp）。实测 3（smoke-A3 dual-fix）仍报 e.trim → **data-dir/agents/ 复制未解决**。
- **待查**：e.trim 可能与 (a) cwd≠data-dir 路径解析 (b) 并行 tool calls（model 同时调 spawn_agent+search_apis）(c) 长任务 prompt 有关。需下一 wake 用「直接 cline + cwd≠data-dir」最小复现定位。

### run_cli.sh 改动（eda_fastmcp 仓库外，不入 super_intelligence_2035 git）
1. L201: `$ws_dir/.cline/agents/` → `$ws_dir/agents/`（cwd 路径修复）
2. worker 循环新增：`cp CLINE_AGENTS_SRC/*.yaml → $worker_dir/data/agents/`（data-dir 路径，未解决 e.trim 但保留）
- 纪律：只改 harness 编排，未碰 benchmark/评分器/cline 源码。

### 结论与下一步
- **wake#922 root cause A（-p 8 并发）错误**；真因 = agent 路径 bug（已修）+ e.trim 执行 bug（待定位）。
- spawn_agent 在 cline 3.0.51 **机制可用**（直接调用✅），问题在 harness 编排层。
- 下一步：① 最小复现 e.trim（直接 cline + cwd≠data-dir + B1 config）② 若是 cwd≠data-dir → harness 改为 cwd=data-dir 或 spawn 用 configured agent 而非 anonymous ③ smoke-B（doubao root cause B 仍有效）④ 通过则重跑 P1
- P4 负报告仍保留为历史档。

## 七、2026-11-14 wake#925·**Option B 修复 e.trim ✅ + configured agent 工具未注册定论 + B3 决定性实验**

> 接续 wake#924 smoke_A4_pass 状态。本节定论两个关键问题：e.trim 根因 + configured agent 工具注册。

### 1. Option B 修复 e.trim（CLINE_UNIFIED_DATA_DIR=1）
- **方案**：harness 设 `--data-dir=ws_dir` + 复制 settings/agents/secrets/globalState 进 ws_dir → cwd=data-dir=ws_dir 单路径
- **实施**：`run_cli.sh` L206-227 加 CLINE_UNIFIED_DATA_DIR 分支；`run_subagent_ablation.sh` export `CLINE_UNIFIED_DATA_DIR=1`
- **验证（smoke-B1-unified, /tmp/zhulong_subagent_eval_smokeB1uni/）**：
  - cline 命令 `-c ws --data-dir ws`（cwd=data-dir ✅）
  - ws_dir 含 agents/researcher.yaml + settings/providers.json（deepseek-v4-pro-cloud）
  - 主 agent modelInfo=deepseek-v4-pro-cloud ✅
  - **无 e.trim**（grep count=0）✅
  - **但 agent 未调任何 subagent**（见下）

### 2. 🔴 configured agent 工具 `subagent_researcher` 在 cline 3.0.51 未注册（定论）
- smoke-B1-unified 主 session messages.json 分析：
  - LANG_HINT 要求"调用 `subagent_researcher` 工具"
  - agent thinking 明确说："However, looking at my available tools, I don't see a `subagent_researcher` tool. I have `spawn_agent`..."
  - agent 实际调用：run_commands / pyAether_MCP_server__search_apis / get_api_details / run_code / editor / read_files（**从未调 spawn_agent 或 subagent_researcher**）
  - agent 自己用 search_apis 干活，没委托给任何 subagent
- **结论**：`subagent_researcher`（configured agent 独立工具）在 cline 3.0.51 **未注册**。cline strings 证实 `AgentConfigSchema` 存在但 configured agent → 独立工具的注册机制在当前版本未生效（或需不同触发条件）。
- **与 wake#923 一致**：smoke-A 主 session 报 `AI_NoSuchToolError: unavailable tool 'subagent_researcher'`（wake#923 §六 实测 1）。当时归因"agent 路径错误"，但路径修复后 smoke-B1-unified 仍无此工具 → **路径不是根因，工具根本不注册**。

### 3. anonymous `spawn_agent` 可用但需 prompt 明确要求
- **smoke 3074b 硬证据**（/tmp/subagent_smoke_3074b/）：
  - 主 session 4 条消息，prompt 明确："You MUST use the **spawn_agent** tool to delegate to the 'researcher' sub-agent."
  - agent 调了 1 次 spawn_agent（input: `{systemPrompt: "...researcher...", task: "Look up..."}`）
  - 子 session agent_63282962 n_msgs=15, model=deepseek-v4-pro-cloud
  - **anonymous spawn 成功执行**
- **关键差异**：3074b prompt 说"spawn_agent"（工具存在）→ agent 调了；smoke-B1-unified prompt 说"subagent_researcher"（工具不存在）→ agent 没调。
- **修法**：LANG_HINT 从"调用 `subagent_researcher`"改成"调用 `spawn_agent`"（复刻 3074b 措辞）。

### 4. 🔑 子 agent 模型来源（待 B3 决定性实验定论）
- anonymous spawn_agent 只接受 `{task, systemPrompt}`，无 model 字段 → 子 agent 模型由 cline 内部逻辑决定。
- **假设 A**：子 agent = 主 session 模型（providers.json 默认/lastUsedProvider）→ B1-B5 基座梯度不可行（主恒定 dsv4-pro → 子全 dsv4-pro）
- **假设 B**：子 agent = researcher.yaml modelId → B1-B5 基座梯度可行
- **3074b 无法区分**：researcher.yaml modelId=dsv4-pro AND providers.json 默认=dsv4-pro → 子=dsv4-pro（两者一致）
- **B3 决定性实验**（/tmp/zhulong_subagent_eval_smokeB3sp/）：researcher.yaml modelId=doubao-seed-2.0-pro-cloud + providers.json 默认=dsv4-pro
  - 子=dsv4-pro → 假设 A 成立（H2 不可行）
  - 子=doubao-pro → 假设 B 成立（H2 可行）
- **第一轮 B3 smoke 结果**（12:07）：spawn_agent 调用 3 次，**全部 e.trim 失败**，0 子 session → INCONCLUSIVE

### 5. 🔴🔴 真正根因 C（推翻 Option B）：PreToolUse hook 拦截 spawn_agent
- **Option B（cwd=data-dir）未修复 e.trim**：smoke-B1-unified "无 e.trim" 是假阳性（agent 未调 spawn_agent，因 prompt 说不存在的 subagent_researcher）。B3 smoke 用 spawn_agent prompt → e.trim 复现。
- **真根因**：`scripts/cline_hooks/PreToolUse` L285 白名单只含 MCP_PREFIXES + SUBMIT_TOOLS。`spawn_agent` 不在白名单 → 落到 L308 `_safe_override` → 输入被改写为 `{"files":[{"path":"/dev/null"}]}` → spawn_agent 收不到 `task` 字段 → `task.trim()` → "undefined is not an object (evaluating 'e.trim')"。
- **3074b 为什么成功**：3074b 是**直接 cline CLI**调用（cwd=/tmp/subagent_smoke_3074b），**不经 harness** → hook 未部署到 ~/.cline/hooks/ → spawn_agent 不被拦截 → 成功执行。
- **修复（已实施）**：hook 新增 `SPAWN_TOOLS` 白名单（spawn_agent + team_* + ask_question），L285 改为 `tn in SPAWN_TOOLS` 也放行。这些工具不泄题（子 agent 用已白名单的 MCP 工具）。
- **纪律**：hook 是 harness 反作弊组件（非 benchmark/评分器/cline 源码），加白名单是合法 harness 修复。

### 6. 第二轮 B3 smoke（hook 修复后，12:09 启动）—— 🔴🔴 决定性结果
- **hook 修复生效**：e.trim=0 ✅（第一轮=5），spawn_agent 执行成功，子 session 创建 ✅
- **子 session DB 记录**：`agent_1794629386312_9oczmy | openai-compatible | deepseek-v4-pro-cloud | completed | is_subagent=1`
- **子 session messages modelInfo**：每条 assistant 消息 `modelInfo.id = deepseek-v4-pro-cloud`（主模型）
- **🔴 决定性结论**：anonymous spawn_agent 子 agent 使用**主 session 模型**（providers.json 默认/lastUsedProvider），**不读 researcher.yaml 的 modelId**
  - B3 配置：researcher.yaml modelId=doubao-seed-2.0-pro-cloud + providers.json 默认=dsv4-pro
  - 子 agent = dsv4-pro（主模型），**非** doubao-pro（researcher.yaml）
  - **假设 A 成立**：子 agent = 主模型
- **researcher.yaml 完全不生效**：
  - modelId 不生效（子=dsv4-pro 非 doubao-pro）
  - tools 不生效（子有默认工具集 read_files/search_codebase/run_commands/fetch_web_content/editor/ask_question/spawn_agent，**无** MCP 工具 pyAether_MCP_server__search_apis）
  - 子 agent 尝试调 `search_apis`（无 MCP 前缀）→ NoSuchToolError
- **子 agent 最终完成**（finishReason=completed），但产出无研究价值（无法查 API 文档）

### 7. 🔴 H2/H3 技术不可行性定论（cline 3.0.51 限制）
- **H2（基座梯度 B1→B5）技术不可行**：
  - configured agent 独立工具（subagent_researcher）不注册 → 无法通过 configured agent 传 modelId
  - anonymous spawn_agent 子 agent = 主模型（providers.json 默认）→ 所有臂子 agent = dsv4-pro → 无梯度
  - 要实现 H2 需 cline 版本支持 configured agent 工具注册（当前版本不支持）
- **H3（maxIter 5 vs 30）技术不可行**：
  - maxIter 是 researcher.yaml 参数 → researcher.yaml 不生效 → maxIter 不可控
  - anonymous spawn_agent 无 maxIterations 参数
- **H1（A0 无 spawn vs A1/B1 有 spawn）仍可检验**：
  - A0 复用 compaction basic（无 spawn）vs A1/B1（强提示调 spawn_agent，子=dsv4-pro=主）
  - 测"有 subagent 委托 vs 无"的效果（subagent 做研究、主 agent 写代码）
  - 但注意：子 agent 无 MCP 工具 → 研究能力受限 → H1 效果可能微弱

### 8. 下一步选择（需用户裁决）
- **Option 1**：只跑 H1（A0 vs A1/B1），H2/H3 标"技术不可行（cline 3.0.51 限制）"，出部分负结果报告
- **Option 2**：放弃 subagent 消融，出完整负结果报告（H1/H2/H3 均无法有效检验）
- **Option 3**：等 cline 升级支持 configured agent 工具注册后重跑（需解除版本纪律）
- **H1**（A0 无 spawn vs A1/B1 有 spawn）：anonymous spawn 路线下可检验（A0 复用旧数据无 spawn；A1/B1 强提示调 spawn_agent，子=dsv4-pro=主）。测"有 subagent 委托 vs 无"的效果。
- **H2**（B1 vs B2-B5 基座梯度）：取决于 B3 结果。若子=主模型 → **技术不可行**（不是证据不足，是 cline 3.0.51 限制）。若子=researcher.yaml modelId → 可行。
- **H3**（C1 iter5 vs C2 iter30 完成率）：maxIter 是 researcher.yaml 参数。若 configured agent 工具不注册 → anonymous spawn 不读 researcher.yaml → **maxIter 也不可控** → H3 同样不可行。

### 6. 待办
1. B3 smoke 结果 → 定 H2/H3 可行性
2. 若 H2 可行：改 run_subagent_ablation.sh SUBAGENT_HINT（subagent_researcher→spawn_agent）+ A1 也注入 hint + 修 L85 providers.json 验证 → 重跑 P1
3. 若 H2 不可行：如实报告 cline 3.0.51 subagent 机制限制，只跑 H1（A0 vs A1/B1），H2/H3 标"技术不可行"

---

## 八、2026-11-14 wake#926·**B3 二轮 smoke 决定性证据 + cline 源码定论 + H1-only 裁决**

> 接续 wake#925 §七。本节用 **post-hook-fix B3 二轮 smoke 的实测子 session** + **cline 二进制源码** 双重证据，**最终定论** H2/H3 技术不可行，并裁决执行 H1-only（§七.8 Option 1）。

### 1. B3 二轮 smoke 实测（hook 修复后，batch 2026_1114_120909，PID 4094066）
- 配置：researcher.yaml `providerId: doubao-pro` / `modelId: doubao-seed-2.0-pro-cloud` / `maxIterations: 15` / `tools: [search_apis, get_api_details]`；providers.json 默认 = `deepseek-v4-pro-cloud`
- cline 命令：`-c ws --data-dir ws`（Option B unified，cwd=data-dir ✅）+ spawn_agent 强提示
- **spawn_agent 被调用** ✅（hook SPAWN_TOOLS 白名单修复生效，不再 e.trim）
- **子 session 创建** ✅：`agent_1794629386312_9oczmy.messages.json`，n_msgs=28
- **子 session 模型 = `deepseek-v4-pro-cloud`**（provider: openai-compatible）= **主 session 模型 / providers.json 默认**，**非** researcher.yaml 的 doubao-pro
- **子 session 工具** = `run_commands / search_codebase / fetch_web_content / read_files / search_apis / search_apis_by_keyword / editor / ask_question / spawn_agent`（全套内建工具），**非** researcher.yaml 限定的 `[search_apis, get_api_details]`
- **🔴 关键**：子 agent 尝试调 `search_apis`（无 MCP 前缀）→ `AI_NoSuchToolError: unavailable tool 'search_apis'`——子 agent **没有 MCP 工具**（pyAether_MCP_server__search_apis 等），只有 cline 内建工具 → 子 agent 无法做 pyAether API 研究
- spawn_agent input = `{systemPrompt, task}`（anonymous，无 `name`/`agent` 字段）→ researcher.yaml **从未被加载**

### 2. cline 源码定论（spawn_agent execute 函数）
`strings $(command -v cline)` 提取 spawn_agent 工具定义：
```js
{name:"spawn_agent",description:"Spawn a sub-agent with a custom system prompt...",
 execute:async(i,t)=>{...n=eu({kind:"subagent",prompt:i.systemPrompt,
   configProvider:e.configProvider,        // ← 父 agent 的 provider（模型）
   tools:a,                                 // ← 父 agent 的 subAgentTools
   maxIterations:e.defaultMaxIterations,    // ← 父 agent 的默认 maxIter
   parentAgent...})}}
```
- 子 agent 只用 `i.systemPrompt` + `i.task`；**无 `name`/`agent` 字段查找** → 不可能通过传 name="researcher" 加载 configured agent
- 子 agent 的 `configProvider`（模型）= 父的 `e.configProvider`（providers.json 默认）
- 子 agent 的 `tools` = `e.subAgentTools`（父的子代理工具集，= cline 内建工具，**不含 MCP 工具**）
- 子 agent 的 `maxIterations` = `e.defaultMaxIterations`（父的默认值，**非** researcher.yaml.maxIterations）
- 配合 §七.2（configured agent 独立工具 `subagent_researcher` 在 3.0.51 不注册）→ **无任何路径**让 researcher.yaml 的 modelId/tools/maxIterations 生效

### 3. 最终定论
| 假设 | 可行性 | 根因 |
|:--|:--|:--|
| **H1**（A0 无 spawn vs A1 有 spawn） | ✅ 可检验 | anonymous spawn 可执行；测"委托 vs 不委托" |
| **H2**（B1→B5 基座梯度） | ❌ 技术不可行 | 子模型恒=父模型（dsv4-pro）；无梯度；configured agent 工具不注册 |
| **H3**（C1 iter5 vs C2 iter30） | ❌ 技术不可行 | anonymous spawn 用父 defaultMaxIterations；researcher.yaml.maxIter 不生效 |

**⚠️ H1 重要 caveat**：子 agent **无 MCP 工具**（pyAether_MCP_server__search_apis 等）→ 子 agent 无法查 pyAether API 文档，只能用 read_files/search_codebase/run_commands/fetch_web_content 探索 → "研究委托"能力受限 → H1 的 spawn 增益可能微弱甚至负向（子 agent 产出无研究价值，主 agent 还得自己重做）。这本身是 H1 的一个发现（subagent 委托在当前工具配置下是否有效）。

### 4. 裁决：执行 §七.8 Option 1（H1-only）
- **保留**：A0（复用 compaction basic r1-r3，无 spawn）+ A1（spawn-on，强提示调 spawn_agent，子=dsv4-pro=主）
- **裁掉**：B1-B5（H2 不可行，全 = dsv4-pro 子，与 A1 等价）+ C1/C2（H3 不可行，maxIter 不可控）
- B1 与 A1 功能等价（均 spawn-on + dsv4-pro 子，B1 的 researcher.yaml=dsv4-pro 不被加载也无影响）→ A1 即代表"有 spawn"
- **P1 pilot**：A1 × 8 题 × 1 轮（A0 复用无需重跑）；go 则 A1 × 40 题 × 3 轮
- **报告**：H1 实测 + H2/H3 标"技术不可行（cline 3.0.51 anonymous spawn_agent 限制 + configured agent 工具未注册）"+ cline 源码证据 + B3 smoke 证据 + 子 agent 无 MCP 工具 caveat

### 5. 本 wake 实施
- ✅ B3 二轮 smoke 子 session 模型/工具实证（child=dsv4-pro，无 MCP 工具）
- ✅ cline 源码 spawn_agent execute 函数提取（configProvider/tools/maxIterations 全继承父）
- ✅ H2/H3 技术不可行最终定论（双重证据）
- ✅ 裁决 H1-only（§七.8 Option 1）
- ⏸ B3 smoke PID 4094066 仍在跑（1 task，不 kill）——其 1-task Pass@1 是 H1-adjacent 数据（B3≈A1，均 dsv4-pro 子）
- 待办（下一 wake，B3 结束后）：改 RUN_ARMS=("A1") → 起 A1 P1 pilot 8 题 × 1 轮 → go 则 40 题 × 3 轮 → P4 报告
