# subagent 消融 reanalysis — 推翻 wake#915「需源码改」结论

> 2026-11-14 wake#922 · 推进 agent
> 背景：wake#915 交付 P4 负结果报告（`reports/report_zhulong_subagent_ablation_zh.html`），结论「cline 3.0.51 configured-agent subagent 机制不可用 / H1-H3 无法检验 / 需解除版本·源码红线重跑」。
> 本文件用**硬证据**推翻该结论的「需源码改」前提：subagent 在 cline 3.0.51 下**确实可执行**，P1 的 0% 是**两个配置级问题**，均在红线内可修。

## 一、决定性证据：smoke 3074b 是 TRUE POSITIVE

wake#915 的 go_nogo note §五 自承「P0 没验证 subagent 是否真正执行」→ 推断 smoke 全是盲区假阳性。**此推断错误**。

`/tmp/subagent_smoke_3074b/`（2026-11-13 23:54）实测：
- 子 agent session 文件 `sessions/1794585225882_whch6/agent_63282962-9b8c-4483-ac5d-d9df4e899ed5.messages.json` **n_msgs = 15**（非 0）
- 主 session 含 `finishReason: completed`、`inputTokens: 92836`、`outputTokens: 2026` → **子 agent 真正执行了 LLM 并消耗 token**
- researcher.yaml：`providerId: openai-compatible` / `modelId: deepseek-v4-pro-cloud` / `tools: [pyAether_MCP_server__search_apis, pyAether_MCP_server__get_api_details]`
- providers.json：`openai-compatible`（apiKey `…e13f4f37`，baseUrl `/cloud/v1`，model `deepseek-v4-pro-cloud`，reasoning.enabled=false）
- 调用方式：直接 cline CLI，1 task，cwd=data-dir（`logs/cline.log`: `interactive:false, hasPrompt:true`）

**结论**：cline 3.0.51 的 configured-agent "researcher" subagent **能在单任务串行下真正执行**。根因 A（empty messages）不是普遍源码 bug。

## 二、P1 0% 的两个真实根因（均配置级，红线内可修）

### 根因 A — dsv4 臂（B1/B2/C2）"messages must not be empty"：-p 8 并发竞态
- B1 的 `researcher.yaml` + `providers.json` 与 smoke 3074b **逐字节相同**（同 providerId `openai-compatible`、同 apiKey `e13f4f37`、同 model、同 reasoning disabled）。
- 唯一差异：smoke 3074b = **1 task 串行**（subagent 执行 ✅ n_msgs=15）；P1 B1 = **8 task 并行（-p 8）共享同一 `CLI_DATA_DIR=/nasdata/.../subagent_ablation/B1`** → 所有子 session `n_msgs=0` ❌。
- 定位：8 个并行 cline 进程共享同一 arm 的 `sessions.db`/`teams.db`，子 agent session 消息初始化在并发下竞态 → task 未持久化为首条 user message → OpenAI API 拒空 messages。
- **修复方向（红线内）**：① 子 agent 臂降并发（-p 1 或 -p 2）验其是否复现 smoke 的成功；或 ② per-task data-dir 隔离（每 task 独立 sessions.db）保留 -p 8。-p 是否为「全臂恒定」协议常量需用户/运维裁决（A0 复用 compaction basic 是 -p 8，降 -p 会与 A0 形成 -p×subagent 混淆；per-task 隔离可避免此混淆）。

### 根因 B — doubao 臂（B3/B4/B5）"Unknown or disabled provider"：researcher.yaml providerId 误用
- B3/B4/B5 的 researcher.yaml 写 `providerId: doubao-{pro,mini,lite}`（providers.json 里的**命名 profile key**），但 cline subagent 的 provider 解析把 providerId 当 provider **类型**查 → 注册表无 `doubao-*` 类型 → 报错。
- 主 agent 用 `lastUsedProvider: openai-compatible`（真类型）正常；subagent 走 `buildAgentRuntimeConfig` 覆盖 providerId 为命名 profile → 解析失败。
- **修复方向（红线内）**：researcher.yaml 改 `providerId: openai-compatible`（真类型）+ `modelId: doubao-seed-2.0-{pro,mini,lite}-cloud`；并在该 arm 的 providers.json `openai-compatible` entry 里把 apiKey 换成 doubao 对应 key、model 换成 doubao model（doubao 三 model 走同一 `/cloud/v1` gateway，key 不同：pro=`…3dd97aea`，mini/lite 待核）。需 smoke 验 modelId 是否真能覆盖 provider entry 的 model。

## 三、对 wake#915 交付物的处置（守红线 🚫 不删旧结果/trace）

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
5. **红线复检**：smoke/P1 启动前 `pgrep -f designflow` / 沙盒端口 FREE / 不与 designflow 并发；trace 落 /tmp（/nasdata 100% 满）。

## 五、本 wake 实施记录

- ✅ 核实 smoke 3074b n_msgs=15 / usage>0 / completed（硬证据）
- ✅ 逐字节比对 B1 researcher.yaml + providers.json = smoke 3074b
- ✅ 核实 B3/B4/B5 researcher.yaml providerId=doubao-*（根因 B 配置 mistake）
- ✅ cline 版本仍 3.0.51（未变 → 根因非版本固有）
- ⏸ 未跑 confirmatory smoke：designflow eval 运行中（PID 3183742，沙盒占用，红线 🚫 不与 designflow 并发）
- ✅ 守红线：未改 benchmark/评分器、未删旧结果/trace、未 kill loop、未碰 cline 源码/版本
- 待办（下一 wake 沙盒空闲）：跑 smoke-A → smoke-B → 通过则重跑 P1
