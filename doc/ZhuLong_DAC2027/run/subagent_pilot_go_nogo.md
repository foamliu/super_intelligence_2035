# subagent 消融 P1 pilot — go/no-go 决策（NO-GO）

> 2026-11-14 02:30 · wake#914 · 决策者：推进 agent
> 任务书：`ZHULONG_TASK.md` §🔴 2026-11-13 21:2x 令「启动 subagent 消融」
> 计划书：`reports/plan_zhulong_subagent_ablation_zh.html`（P0 声称 17:20 PASS）

## 一、结论一句话

**NO-GO。** P1 pilot 8 臂全部跑完，subagent 工具被调用率 100%，但 **subagent 实际执行成功率 = 0%**（所有臂所有 spawn 调用全部 `finishReason=error`、`usage=0/0`、subagent session 0 messages）。subagent 从未真正运行 LLM；所有 Pass@1 全是主 agent 独立完成。**不进 P2**，否则 16h 产出无意义数据（违反「不许包装成增益」「真实裁判=Pass@1」红线）。

## 二、go/no-go 判据复核

预注册（计划书 §六）：「subagent 调用率 ≥ 30% → 进 P2；20-30% → 升级提示后重跑 P1；<20% 且强提示后仍 <30% ⇒ 判无效停 P2 出负结果报告」。

- **字面「调用率」（工具被调用 / 任务数）= 100%** ≥ 30% → 字面判 GO。
- **但「调用率」的实质 = subagent 真正执行 LLM 的比例 = 0%** < 20% → 实质判 NO-GO。
- 预注册判据**只度量了工具是否被调用，没度量 subagent 是否真正执行**——这是 P0 验证的盲区（见 §四）。
- 按实验目的（H1/H2/H3 全依赖 subagent 真正执行 + 消耗 token），0% 执行率下 P2 无法判任何假设 → **NO-GO**。

## 三、Pilot 真实结果（8 臂 × 8 题 × 1 轮）

| 臂 | 配置 | spawn 调用 | spawn 执行成功 | sub_tok_in/out | Pass@1(子集) | wall_sec | main_tok |
|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|
| A0 | baseline (spawn off, 复用 compaction basic) | — | — | — | 69.2%(40题) | — | — |
| A1 | spawn-on 无 configured agent | 0 | — | 0/0 | 87.5%(7/8) | 2516 | 5.39M |
| B1 | cfg-same dsv4-pro-cloud | 17 | **0 (17 error)** | 0/0 | 62.5%(5/8) | 5276 | 7.10M |
| B2 | cfg-dsv4-flash | 18 | **0 (18 error)** | 0/0 | 87.5%(7/8) | 3509 | 5.40M |
| B3 | cfg-doubao-pro (rerun) | 9 | **0 (9 error)** | 0/0 | 85.71%(6/7) | 5489 | 8.11M |
| B4 | cfg-doubao-mini (rerun) | 9 | **0 (9 error)** | 0/0 | 87.5%(7/8) | 3613 | 6.82M |
| B5 | cfg-doubao-lite (rerun) | 8 | **0 (8 error)** | 0/0 | 87.5%(7/8) | 5149 | 7.95M |
| C1 | cfg-iter5 dsv4-flash | 20* | *见下 | 0/0 | null(6/8 ok) | 2694 | 7.92M |
| C2 | cfg-iter30 dsv4-flash | 18 | **0 (18 error)** | 0/0 | 75.0%(6/8) | 2625 | 3.46M |

\* C1 cost JSON 报 spawn=20，但 trace 扫描在该 batch 找到 0 个 subagent tool_use（batch 路径/结构差异，待核；不影响结论）。

**doubao 三臂连通**（计划书 §六 go/no-go 第三项）：doubao key curl 在 P0 通过，但 subagent 运行时全部 `Unknown or disabled provider` → **subagent 层连通失败**。

## 四、Root Cause（两类，均 cline 3.0.51 内部，非快速配置可修）

### A. dsv4 臂（B1/B2/C2）：`"Invalid prompt: messages must not be empty"`
- provider 解析成功（`providerId: openai-compatible` 是真 provider 类型，= 主 agent 同款）。
- subagent session 文件 `agent_*.messages.json` 全部 `n_msgs=0`——**task 从未成为 user message 持久化**。
- `configured-agent-tool.ts:198` 调 `subAgent.run(input.prompt)`（input.prompt 非空，已从 trace tool_use 核实），但 `SessionRuntime.run()` 路径下首次 LLM 调用 messages 数组为空 → OpenAI API 拒绝 → error。
- 定位：cline 3.0.51 `delegated-agent` / `SessionRuntime` 消息初始化路径 bug（task 未注入为首条 user message 即发起 LLM 调用）。

### B. doubao 臂（B3/B4/B5）：`"Unknown or disabled provider \"doubao-{pro,mini,lite}\"."`
- `providers.json` 里 `doubao-lite` 等是**命名 profile**，其 `settings.provider` 实为 `"openai-compatible"`（同 baseURL/apiKey，仅 model 不同）。
- researcher.yaml 写 `providerId: doubao-lite`，被 subagent 的 provider 解析当作 provider **类型**查 → 注册表里无此类型 → "Unknown or disabled provider"。
- 主 agent 用 `lastUsedProvider: openai-compatible`（真类型）能跑；subagent 走 `buildAgentRuntimeConfig`（`configured-agent-tool.ts:139`）覆盖 `providerId` 为命名 profile → 解析失败。
- 定位：subagent provider 解析按**类型**查，不按**命名 profile**查；需 cline 源码改动或改 researcher.yaml `providerId` 为 `openai-compatible` + 另设 model/baseURL（但当前架构 subagent 连接配置来自 base runtime，覆盖 model 的路径未验证）。

## 五、P0 验证盲区（为何 17:20 PASS 仍跑出 100% error）

P0 声称 3 项通过：①doubao key curl OK ②configured agent 工具出现在列表 ③主 agent 调用了 subagent。
**P0 没验证**：subagent LLM 是否真正执行（messages 非空、usage>0、finishReason=completed）。
→ 工具「注册+被调用」≠ subagent「真正运行」。这正是 pilot 该抓的，但 P0 判据漏了。

## 六、下一步建议（由用户/运维裁决，agent 不擅自升级 cline 或改源码）

1. **修 root cause A**（messages empty）：需查 `SessionRuntime.run()`（`runtime/` 下）为何 task 未成 user message；可能是 cline 3.0.51 已知 bug 或需 ≥3.x 某版本。**红线：harness=cline 3.0.51 不改版本（任务书 11-07 令）**——若修需提请用户放行版本变更。
2. **修 root cause B**（doubao provider）：试改 researcher.yaml `providerId: openai-compatible` + `modelId: doubao-seed-2.0-{pro,mini,lite}-cloud`，并在 subagent 连接配置里设 doubao baseURL/apiKey；或 cline 源码支持命名 profile 解析。
3. **最小重验证**：任一修复后，先 1 题 smoke 确认 subagent session `n_msgs>0` + `usage>0` + `finishReason=completed`，再重跑 P1 8 题。
4. **若不修**：按预注册「判无效 → 出负结果报告」收尾，报告结论 = 「cline 3.0.51 当前配置下 subagent 机制不可用，H1/H2/H3 无法检验」。

## 七、证据索引

- trace（100% error 扫描脚本输出 + per-arm 统计）：本轮 wake#914 shell 记录
- subagent session 0 messages：`/tmp/zhulong_subagent_eval/2026_1114_015525/trace/<task>/agent_*.messages.json`（`n_msgs=0`）
- tool_result 原文：`{"text":"Unknown or disabled provider \"doubao-lite\".","iterations":1,"finishReason":"error","usage":{"inputTokens":0,"outputTokens":0}}`
- cost JSON：`run/cost_S_{B3,B4,B5}_r1.json`（rerun，spawn rate 1.0 但 sub_tok=0）
- cline 源码：`/nasdata/app.e0031982/code/cline/sdk/packages/core/src/extensions/tools/team/{configured-agent-tool,delegated-agent,spawn-agent-tool,subagent-prompts}.ts`
- rerun 日志：`/tmp/rerun_doubao.log`（B3/B4/B5 rerun 全 exit=0 但 subagent error）
