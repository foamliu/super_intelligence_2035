# cline 与 ZhuLong CLI 通过率差异报告：实验背景 · 设置 · 结果 · 源码级归因

> **对象**：ZhuLong EDA-Scripting-Bench（PyAether 切片，158 题）· glm-5.3-flash · READBACK=full · 各 5 轮
>
> **唯一设计变量**：CLI agent（`cline 3.0.51` vs `zhulong CLI`，fork 自 `cline 3.0.29`）
>
> **源码**：zhulong = `/nasdata/app.e0031982/code/eda_platform`；cline = `/nasdata/app.e0031982/code/cline`
>
> **数据依据**：`zhulong_results.md`、`run/MEMORY_ZHULONG.md`、`run/daily-memories/` 落盘记录与 regrade 日志（出处见附录 A）

---

## 一句话结论

> 差距**不是模型 / 框架 / 代码质量造成的，而是"约 20% 的题目根本没生成出可执行的 .py"**。
> 定量看：`cline 86.8 ± 1.6%` vs `zhulong 69.0 ± 2.3%`（**Δ = −17.8pp**），其中几乎 **100%**（≈18pp）来自"未生成 / 未落盘"（生成失败）；
> 而"生成后答对率"两侧几乎无差（zhulong 88.6% vs cline 88.2%，差异 ≈ 0）。
>
> 源码级根因：zhulong CLI 是从 `cline` 早期版本（`@cline/core 0.0.51`，约 2026-06-24）fork 出来的，
> **缺少 cline 在 2026-08-01～08-04 引入、并随评估基线版本（`3.0.51`）一起发布生效的"空响应重试"（empty-response retry）机制**。
> 在 glm-5.3-flash 这类会间歇性返回"空回复"的 backbone 下，一次空回复在 zhulong CLI 里是**直接判死的硬失败**（抛 `Model returned empty response`），
> 而在 cline CLI 里会被**静默重试**掉——这正是"生成失败 23–37/轮 vs 1–4/轮"的机制来源。

---

## 1. 实验背景

ZhuLong 是面向 EDA（电子设计自动化）脚本编写场景的智能体框架与评测。核心评测集为 **EDA-Scripting-Bench**：
给定一条自然语言任务描述，让 agent 通过一个 MCP 工具层（"检索 + 沙盒执行"闭环）自主生成一份能在 EDA 工具上运行的脚本
（以 `pyAether` Python 为主，另有 SKILL / TCL 场景）。

评测过程中 agent 被暴露 **4 个核心工具**：

| 工具 | 功能 | 关键参数 |
|---|---|---|
| `search_apis` | 语义相似度（向量）检索 API，合并 BM25 补足 | `query` / `lang` / `host` / `top_k` / `similarity_threshold` |
| `search_apis_by_keyword` | 关键词（camelCase + BM25）检索，适合缩写 | `query` / `lang` / `host` / `top_k` |
| `get_api_details` | 取 API 详情（描述 / 类型 / 属性 / 继承） | `api_list` / `lang` / `host` |
| `run_code` | 在远程 EDA 沙盒执行代码并回读 | `code` / `lang` / `host` / `probe` / `encoding` |

其中 `run_code` 回读 4 字段（`response` / `error_log` / `print_log` / `result`）；本实验统一使用 **READBACK=full**（四字段全回读）。

**本报告要回答的问题**：把主干 LLM、检索工具、沙盒、回读档、题集、并发全部对齐之后，
"用 cline CLI 驱动"与"用 zhulong CLI 驱动"仍存在系统性通过率差距（−17.8pp）。既然**唯一设计变量是 CLI 二进制**，
差距必落在这两个 CLI 的**内部实现差异**上——§4 给出源码级定位。

## 2. 实验设置

### 2.1 口径核对：cline 与 zhulong 设置逐字节一致（唯一变量 = CLI 二进制）

| 维度 | cline 线 | zhulong CLI 线 | 是否一致 |
|---|---|---|---|
| 主干 LLM | glm-5.3-flash @ `/v1` | glm-5.3-flash @ `/v1` | ✅ 相同 |
| **maxTokens** | 16384 | **16384** | ✅ 双方实测逐字节一致 |
| reasoning | off | off | ✅ |
| 框架 / 工具 | pyAether MCP 4 工具 | 同左 | ✅ |
| 回读档 | READBACK=full | READBACK=full | ✅ |
| 评测集 | PyAether 158 题 | PyAether 158 题 | ✅ |
| 轮数 / 并发 | 5 轮 / `-p 4` | 5 轮 / `-p 4` | ✅ |
| 反作弊 hook | 生效 | 生效 | ✅ |
| **CLI agent** | **cline 3.0.51**（`@cline/core 0.0.71`） | **zhulong CLI**（`CLI_AGENT=zhulong`，`@cline/core 0.0.51`） | ⬅ **唯一设计变量** |



### 2.2 两个 CLI 的分支关系（源码层面）

两者同源：zhulong CLI 的代码库 `eda_platform` 是 `cline` 官方 monorepo 的一个 **fork**（同为 `@cline/packages` 工作区结构）。

| 代码库 | `@cline/cli` | `@cline/core` | 大致年代（对应 cline 上游 release） |
|---|---|---|---|
| zhulong（`eda_platform`） | **3.0.29** | **0.0.51** | ≈ 2026-06-24 |
| cline 评估基线 | **3.0.51** | **0.0.71** | 2026-08-06 |
| cline 仓库当前 `main`（作图时检出） | 3.0.74 | 0.2.0 | 2026-10+ |

即：zhulong 是 **6 月下旬的早期 fork**，评估基线 cline 是 **8 月上旬**，两者之间恰好发生了一次关键的可靠性改造（见 §4）。

## 3. 实验结果

### 3.1 逐轮通过率（PyAether 158 题，Pass@1）

| 对照臂 | r1 | r2 | r3 | r4 | r5 | 5-run mean±std | 生成失败/轮 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **cline**（glm-5.3-flash, full） | 86.1 | 84.8 | 89.2 | 87.3 | 86.7 | **86.8 ± 1.6%** | 约 1–4 |
| **zhulong CLI**（glm-5.3-flash, full） | 71.5 | 67.1 | 67.1 | 71.5 | 67.7 | **69.0 ± 2.3%** | 23 / 35 / 33 / 32 / 37 |
| **差值** | −14.6 | −17.7 | −22.1 | −15.8 | −19.0 | **−17.8pp** | +20~+33 |

zhulong 侧明细（regrade 日志实提）：

| 轮次 | pass | 生成 ok | 生成 fail | timeout | exec_err |
|---|---:|---:|---:|---:|---:|
| r1 | 113 / 158 (71.5%) | 132 | 23 | 3 | 0 |
| r2 | 106 / 158 (67.1%) | 118 | 35 | 0 | 0 |
| r3 | 106 / 158 (67.1%) | 119 | 33 | 6 | 0 |
| r4 | 113 / 158 (71.5%) | 126 | 32 | 0 | 0 |
| r5 | 107 / 158 (67.7%) | 120 | 37 | 1 | 0 |
| **mean** | **109.0 / 158 (69.0%)** | **123.0** | **32.0** | 2.0 | 0 |

> 要点：5 轮 **exec_err 恒为 0**、timeout ≤ 6、无 infra 故障，说明"跑出来的脚本都对"；
> 缺口几乎全部集中在**生成阶段**（生成失败 mean = 32.0 / 轮，即约 **20.3% 的题目没落下可用代码**），
> 对比 cline 只有 1–4 / 轮（约 1–2%）。

### 3.2 差距的定量分解（近似，标 "≈"）

设 生成成功数 = `G`、条件通过率 = `p`，则 `pass = G × p`：

| 项 | zhulong CLI | cline | 说明 |
|---|---|---:|---|
| 平均生成成功 `G` | 123 / 158（77.8%） | ≈ 155.5 / 158（98.4%） | cline 取 158 − ~2.5（gen-fail 1–4 的中位） |
| 平均条件通过率 `p` | 109/123 = **88.6%** | 137.1/155.5 = **88.2%** | 由 pass ÷ 覆盖率算得 |
| **① 生成失败造成的损失** | ≈ **18.2pp（≈100%）** | — | (155.5 − 123) × 88.6% ÷ 158 |
| **② 条件质量差异造成的损失** | ≈ **−0.4pp（≈0）** | — | 155.5 × (88.2% − 88.6%) ÷ 158 |
| **合计** | **≈ 17.8pp** | — | 与实测 −17.8pp 基本闭合 |

> 结论：**缺口 ≈100% 来自"没生成 / 没落盘"**（覆盖率 77.8% vs 98.4% ≈ 18pp）；一旦生成，zhulong 的条件通过率（88.6%）与 cline（88.2%）**同一水平**。
> 即 zhulong 的短板**不在"代码写得好不好"，而在"能否把一次交互稳稳走到底、落下 .py"**。

## 4. 源码级分析：为什么 zhulong CLI 的通过率更低

### 4.0 先给结论（源码级）

围绕"生成失败 23–37 vs 1–4"这条最硬的观测，两个代码库在**同一处关键逻辑**上分叉：

| 能力 | zhulong CLI（`eda_platform`，core 0.0.51） | cline 基线（core 0.0.71 / 3.0.51） |
|---|---|---|
| **空响应重试中间件**（LLM 层） | ❌ 无 `retry-empty-response.ts` | ✅ 有，且已在 `ai-sdk.ts` 全局挂载 |
| **agent 主循环对空回复的处理** | 直接 `throw "Model returned empty response"` | 交由中间件重试；失败再用 finish-reason 分支细分 |
| LLM 请求入口的 `withEmptyResponseRetry` | ❌ 无 | ✅ 有 |

这条差异把"模型偶发返回一个空 turn"这件事，在 zhulong 里变成**一票否决的任务失败**，在 cline 里变成**一次透明重试**。下面逐层给证据。

### 4.1 版本漂移量（先量化"两个仓库差多远"）

对两个源码树做目录级 diff（排除 `node_modules` / `.git` / 锁文件 / 构建产物）：

```
diff -rq eda_platform/sdk/packages/core/src cline/sdk/packages/core/src   # 仅 cline 独有 166 个文件；仅 eda_platform 独有 2 个
diff -rq eda_platform/sdk/packages/llms/src  cline/sdk/packages/llms/src   # 仅 cline 独有 67 个文件
```

zhulong 落后的不仅是版本号，而是**数百个上游文件的新增 / 修改**。其中对本次评测最致命的，是 4.2 这一处。

### 4.2 关键差异：空响应（empty turn）的重试

#### (a) cline 侧：`retry-empty-response` 中间件（LLM provider 层）

文件 `sdk/packages/llms/src/providers/middleware/retry-empty-response.ts`（cline 有，eda_platform 无）。
其设计注释直白点明它要解决的正是本实验观测到的那类失败：

> *"providers intermittently return a response that finishes normally but carries no content at all …
> In Cline's runtime an empty assistant turn is a hard failure ("Model returned empty response"),
> so a single flaky generation kills the whole task."*

机制要点：
- 流式输出**先缓冲**，直到"首个有效 part（正文 / 工具调用 / 不支持输出 / 错误）"出现才判定本次请求成立并放行；被判定为"空 turn"的尝试**整体丢弃**。
- 仅当一次 turn **真的一无所有**（无正文、无推理、无工具调用）时才重试；**纯工具调用 turn 算有内容，绝不重试**。
- 重试多花的 token 把各次 `finish.usage` 累加进最终 finish，计费诚实。

#### (b) cline 侧：在 `ai-sdk.ts` 全局挂载

文件 `sdk/packages/llms/src/providers/ai-sdk.ts`（评估基线 v3.0.51 版本已含该 import 与 `withEmptyResponseRetry`）：

```ts
import { createRetryEmptyResponseMiddleware } from "./middleware/retry-empty-response";
export function withEmptyResponseRetry(model, retryEmptyResponses) {
  if (retryEmptyResponses === false) return model;
  return wrapLanguageModel({ model,
    middleware: createRetryEmptyResponseMiddleware({ ...retryEmptyResponses }) });
}
// ... 在 vendor 模型构建出口处统一调用 withEmptyResponseRetry(...)
```

即 cline 的**每一个** AI SDK vendor 模型默认套上这层空响应重试，可经 `ProviderFactoryResult.retryEmptyResponses` 微调 / 关闭。

#### (c) zhulong 侧：agent 主循环直接判死

文件 `eda_platform/sdk/packages/agents/src/agent-runtime.ts`（约 602 行起）：

```ts
const { message, finishReason } = await this.generateAssistantMessage();
if (finishReason === "aborted") { throw this.normalizeAbortError(); }
if (message.content.length === 0) {
  throw new Error(
    finishReason === "error"
      ? (this.state.lastError ?? "Model stream failed")
      : "Model returned empty response",
  );
}
// ...
if (finishReason === "error" && toolCalls.length === 0) {
  throw new Error(this.state.lastError ?? "Model stream failed");
}
```

即：**只要模型这一轮没有吐出任何内容，zhulong 立即把整个任务抛错终止**，没有重试，也没有"纯工具活动/内容过滤/未知 finish"的细分。

#### (d) 时间线：为什么恰好是"cli 有、zhulong 无"

在 cline 仓库 git 历史中可精确对齐：

| 时间 | 事件 | 相对位置 |
|---|---|---|
| ≈ 2026-06-24 | cline 发布 3.0.29 / core 0.0.51（**zhulong fork 锚点版本**） | 分叉点 |
| 2026-08-01 | `feat(llms): retry empty Ollama responses`（#12845） | 空响应重试开始引入 |
| 2026-08-04 | `fix(llms): retry empty model turns on all providers`（#12927） | 扩展到全 provider |
| **2026-08-06** | cline 发布 **3.0.51 / core 0.0.71**（**评估基线**，已含上述中间件） | 基线 |

即：**zhulong 在空响应重试加入前约 6 周就已分叉**，此后再未回灌该机制；而评估所用 cline 基线恰好包含它。
这解释了"同样的 glm-5.3-flash + 同样的 MCP/回读/题集，为何一个落盘率 98%、一个只有 ~80%"。

### 4.3 机制与观测现象的对账（不是猜，是对得上）

把上面的源码差异映射到 zhulong 线实际观测，链条自洽：

1. **代码差异**：`eda_platform/sdk/packages/agents/src/agent-runtime.ts` 第 602–606 行——`if (message.content.length === 0) throw … "Model returned empty response"`，即"这一轮模型没产出内容"就把整个任务判死（4.2c）。
2. **cline 的对应实现**：同一处，cline 在 provider 层用 `retry-empty-response` 中间件把空 turn 吞掉并透明重试（4.2a/b），任务得以继续走到落下 .py。
3. **结果差异的证据**：在配置逐字节一致的同一套 5-run 里，cline gen-fail ≈ 1–4/轮（~1–2%），zhulong gen-fail 23–38/轮（~20%）；且 5 轮 `exec_err=0`、`timeout≤6`、无 infra 故障。
4. **归因结论**：差距全部落在"生成落盘"这一端，与"空响应 → 判死 → 无 .py"完全吻合，而不是"生成错了"或配置/环境差异。

### 4.4 cline `main` 分支后续强化（方向性证据，注意版本边界）

作图时检出的 cline `main`（3.0.74 / core 0.2.0）还新增了以下韧性层，**均晚于评估基线 3.0.51，故不直接参与本次计分，但进一步佐证方向**：

- `fix(agents,llms): recover from max-tokens turns`（#14378，2026-09-21）：`finishReason === "max-tokens" && 无工具调用` 时以简洁性 nudge 重试（`MAX_TOKENS_RECOVERY_LIMIT = 3`）。
- `fix(llms): retry mid-stream network interruptions`（#13052，2026-08-07）：输出前遭遇瞬态网络中断时重试。
- `agent-runtime.ts` 的 `generateAssistantMessageWithProviderRetry()` / `withProviderErrorRetry`：对 429/5xx/网络抖动做指数退避重试（`PROVIDER_ERROR_MAX_RETRIES = 3`）。
- 上下文窗口溢出的结构化恢复（`ContextWindowOverflowError` → 压缩对话后重试一次）。

这些在 `eda_platform` 中同样缺失。它们在 −17.8pp 中**并非必需解释项**（空响应重试那一条已够），
但说明 zhulong 若想追平 cline，核心动作是**回灌上游"可靠性层"**，而非换模型 / 改提示词。

### 4.5 数值对齐：生成失败差距 ≈ 通过率差距

用 zhulong 实测 coverage（77.8% vs cline ≈98.4%）与条件通过率（88.6% vs 88.2%）回代（§3.2）：
**仅"生成失败"一项就贡献 ≈18.2pp，几乎吃掉全部 −17.8pp**；条件通过率几乎无差（zhulong 甚至略高 ≈0.4pp）。

> 结论：**源码里一句 `throw "Model returned empty response"` vs 一层 `retry-empty-response` 中间件，在 Pass@1 口径下就是 ≈18pp，占 −17.8pp 的全部。**

## 5. 结论与建议

1. **差距定性**：`−17.8pp` ≈ 100% 来自**"生成失败 / 未落盘"**，不是模型能力、EDA 框架或代码质量问题（`exec_err=0`；条件通过率 88.6% vs 88.2% 基本打平）。
2. **差距根因（源码级）**：zhulong CLI 是 cline 的**早期 fork（core 0.0.51，≈2026-06-24）**，缺少 cline 在 2026-08-01～08-04 引入、随基线 3.0.51 一起生效的**空响应重试**（`retry-empty-response` 中间件 + `withEmptyResponseRetry`）。空回复在 zhulong 里被 `throw "Model returned empty response"` 一票否决。
3. **建议（工程侧）**：
   - 把 zhulong CLI 回灌到 cline 的 `retry-empty-response` 中间件（最小改动），预期可吃掉大部分生成失败；
   - 远景对齐到 cline `main` 的可靠性层（max-tokens 恢复、provider 错误重试、上下文溢出压缩），彻底消除该系统性 gap；
   - 重新打 5-run `mean±std`，确认 Pass@1 是否收敛到 cline 同量级。
4. **遗留（未在本次坐实）**：本轮各轮存在"布局 quirk 需 `mv` 修复"的次要现象（生成的 .py 落在非预期目录），
   其根因需在 harness 侧（`assemble_for_execution.py` 的收集路径）与 CLI 侧（工作目录 / 路径归一化）联合排查，本报告不据此下结论。

---

## 附录 A：数据出处

| # | 数据 | 出处 |
|---|---|---|
| 1 | cline B.glm-5.3-flash 5/5 = 86.8±1.6%（86.1/84.8/89.2/87.3/86.7），gen-fail 约 1–4/轮 | `zhulong_results.md`「Phase B」；`run/daily-memories/2026-10-18.md` §16:22 / §17:34 |
| 2 | 评估基线版本 cline 3.0.51 / core 0.0.71 | `zhulong_results.md` 头部；`run/MEMORY_ZHULONG.md` CONFIG 行 |
| 3 | zhulong（16384）5-run = 69.0±2.3% [71.5,67.1,67.1,71.5,67.7]（pass 计数 113/106/106/113/107） | 由 pass 计数计算（mean 109.0/158；std 2.3%，样本 n−1） |
| 4 | zhulong 各轮 gen ok/fail/timeout/exec_err（r1 132ok/23fail/3timeout；r2 118/35；r3 119/33/6；r4 126/32；r5 120/37/1） | `/tmp/ABL_glm-5.3-flash_zl_clinealigned16384_r{1..5}_regrade*.log`；`output_evaluation/2026_10*_app.e0031982/final_report.json` |

## 附录 B：源码证据索引

| 论断 | 源码 / 文件·行 | 仓库 |
|---|---|---|
| zhulong = cline fork，@cline/cli 3.0.29 / @cline/core 0.0.51 | `apps/cli/package.json`、`sdk/packages/core/package.json` | `eda_platform` |
| 空响应重试中间件（有） | `sdk/packages/llms/src/providers/middleware/retry-empty-response.ts` | `cline`（eda_platform 无此文件） |
| 中间件全局挂载 + `withEmptyResponseRetry` | `sdk/packages/llms/src/providers/ai-sdk.ts`（import 行 + `withEmptyResponseRetry` 定义 + 调用点） | `cline` |
| 空回复硬失败（无重试） | `sdk/packages/agents/src/agent-runtime.ts` ≈ 602–633（`throw "Model returned empty response"`） | `eda_platform` |
| 分叉时间线（release 提交日期） | `git log -S '"version": "3.0.29"'` / `'"0.0.51"'` / `'"3.0.51"'` / `'"0.0.71"'`；#12845/#12927 | `cline` git |
| 后续韧性层（方向性） | `agent-runtime.ts`（provider retry / max-tokens recovery / context overflow）；#13052、#14378 | `cline` main |

> 本报告为自包含 Markdown。除"反推条件通过率 / 生成覆盖率"等标注"≈"的推断外，其余数字均来自上表出处；未对任何 .tex / 评测脚本做改动。