# Codex 高 err 分类与归因（2026-10-25 17:5x 运维令 · 第 2 部分）

> 证据来源：`/tmp/tb_7x89/jobs_codex/2026-10-24__16-21-23/`（7×89 并发批次，只读）。
> 适配器源码：`harness/terminalbench/agents/codex.py`（codex-cli 0.94.0）。
> 对照物：`agents/cline_patched.py`（cline）+ 同批次 `jobs_cline-patched|opencode|pi`。
> 命名规程：本文件正文一律写 `cline`（代码路径 `cline_patched.py` 不改）。

## 1. 总览（reward.txt 实测，分母 87 = canonical 可跑任务）

| Harness | 完成(eval trial, 有 reward) | pass | exception | 完成率 | 条件通过率(pass/完成) |
|:--|--:|--:|--:|--:|--:|
| cline    | 80 | 43 | 26 | 92.0% | 53.8% |
| opencode | 75 | 41 | 27 | 86.2% | 54.7% |
| pi       | 80 | 35 | 23 | 92.0% | 43.8% |
| **codex**| **41** | **20** | **59** | **47.1%** | **48.8%** |

> 关键观察：codex 的 **条件通过率 48.8%**（在它完成的 41 题上）与 cline/opencode 相当；
> codex 的真正短板是 **完成率仅 47.1%**——59/87 题在 1800s 预算内没跑完即被超时杀掉。

## 2. 异常分类（逐 trial 读 exception.txt，59 个全部分类完毕）

**全部 59 个异常 = 超时，无其它类型。** 按异常被哪一层 `asyncio.wait_for` 捕获分两类：

| 异常类 | 计数 | 捕获层 | 含义 |
|:--|--:|:--|:--|
| `RuntimeError` | 44 | `harbor/environments/docker/docker.py:775` `_collect_buffered_output` 的 `asyncio.wait_for(process.communicate(), timeout=timeout_sec)` 超时 → 上抛 TimeoutError → 经 codex.py:171 `environment.exec` → harbor 包装 | codex CLI 进程读 stdout/stderr 超过 1800s 仍未退出 |
| `AgentTimeoutError` | 15 | `harbor/trial/trial.py:651` `_run_agent_phase` 的外层 `asyncio.wait_for` 超时 | 整个 agent 阶段超过 1800s 预算 |

> 44+15 = 59 = 全部异常。**没有** NonZeroAgentExitCode、context 超限、tool-call 解析失败、429 或网关 403。

### 前 3 条原文（每类）

**RuntimeError（44）代表 — build-pov-ray**（trial.log 末行）：
```
Trial build-pov-ray__uRX5ZqY failed: Command timed out after 1800 seconds
```
exception.txt 调用链尾：`codex.py:171 result = await environment.exec(...)` →
`docker.py:775 stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(input=stdin_data), timeout=timeout_sec)` →
`asyncio CancelledError`（被 wait_for 取消）→ `TimeoutError`。

**AgentTimeoutError（15）代表 — adaptive-rejection-sampler**：
exception.txt 调用链尾：`trial.py:651 await asyncio.wait_for(...)`（外层 agent-phase 超时）→
内层同 codex.py:171 → docker.py:775 communicate 超时。

两类根因相同：**codex CLI 在 1800s 内未退出**。

## 3. 归因（三选一，逐条带证据）

### (a) 适配器 bug —— 部分成立（设计差异，非崩溃性 bug）
- codex.py:156-162 的命令：`codex exec --cd <cwd> --model kimi-k2.6-cloud --sandbox danger-full-access --skip-git-repo-check --json <instruction>` —— **无 max-turns / 迭代上限参数**。
- `codex exec --help`（codex-cli 0.94.0）确认：**无 `--max-turns` 标志**，仅有 `-c key=value` 覆盖 config.toml。
- 在 codex 源码 `codex-rs/core/src/` 中 grep `max_iterations|turn_limit|max_turns|iteration_limit|step_limit` —— **0 命中** → codex 0.94.0 exec 模式**无内置回合/迭代上限**。
- 后果：codex 在难题上**持续跑到外层 1800s 被杀**，记为 exception，而非干净退出。这**放大了 exception 计数、压低了 eval-trial 计数**（41/87），但不直接压低条件通过率。
- 对照 cline（cline_patched.py:180-186）：`cline -c <cwd> ... --auto-approve true --json` 同样无显式 max-turns，但 cline 完成 80/87 → cline 在 1800s 内更常自行结束（任务完成或提前停止），极少撞满预算。

### (b) 容量 / 上下文 —— 主要成立
- codex 完成率 47.1% ≪ cline/opencode/pi 的 86–92%。codex 跑满 1800s 的 59 题多为重编译/构建类：build-pov-ray、compile-compcert、build-pmars、make-doom-for-mips、make-mips-interpreter、mcmc-sampling-stan、largest-eigenval、qemu-startup …（与 cline 也超时的难题高度重叠，但 cline 超时仅 ~19 题）。
- 每轮开销更高：codex 0.94.0 走 `wire_api="responses"`，经 gw_proxy 翻译 `/v1/responses`→`/v1/chat/completions`（config.toml 见 codex.py:114-125）；codex 自身推理 loop 较重 → 单位时间内完成回合更少 → 难题 1800s 跑不完。
- 这不是「模型不行」：codex 完成的 41 题里通过 20 题（48.8%），与其它存活线条件通过率同档。

### (c) 上游服务 —— 不成立
- gw_proxy 9090/9091 在线（GET / 返回 403 是 API 代理对根路径的正常响应，只处理 /v1/*）。
- gw_proxy 日志仅见 `ConnectionResetError: Connection reset by peer`（客户端断开，benign）与 LiteLLM model-cost fetch `Errno 101 Network is unreachable`（loop 剥代理的已知 benign 现象，见运维口径 10-05）。
- codex 20 pass 的题证明模型调用通路正常，无 429 / 网关 403 / API 截断。

## 4. 修法判断：**非适配器可修（不硬改）**

- codex 0.94.0 exec 模式**无内置回合上限** → 无法通过 `-c key=value` 让它干净退出。
- 唯一可调旋钮 = `TB_AGENT_TIMEOUT`（_base.py:80，默认 1800s）：调小→codex 更快失败但不提分；调大→更费机时、边际通过率收益不明。
- 改 codex.py 命令/超时处理**不会提升通过率**（codex 已在它完成的题上拿到 48.8%）；只会把 59 个超时 exception 转成更早的干净失败。
- 铁律遵守：四 survivor 源码（含 codex.py）本轮**不改动**（与「不许动 cline/opencode/pi 既有结果与容器配置」一致）。

## 5. 结论

codex 高 err（59/87=67.8% exception，resolve 20/87=23.0%）的根因 = **(b) 容量为主 + (a) 适配器设计为辅**：
codex 0.94.0 exec 模式无内置回合上限 + 单轮开销较高（responses→chat 代理翻译 + 重推理 loop），
导致 59/87 题在 1800s 预算内跑不完被外层超时杀掉；**非上游服务问题，亦非可经适配器层修复的崩溃性 bug**。
条件通过率 48.8% 表明 codex 能力与其它存活线同档，短板是「在固定预算内完成题数少」。

## 6. 待办（需先报机时 + 与下载/复跑共存的 load，别三线挤爆）
- 若需进一步提升 codex 结果：可考虑(a)单独给 codex 提高超时预算并全量复跑（预计 87×~25min≈36h 串行，或并发降时）；(b)升级 codex 到支持回合上限的版本。两者均需先报机时与 load 共存评估，本轮不启动。
- 本轮 codex 部分（分类+归因+证据）已交付；hermes/claude-code 复跑正在跑，最终报告待复跑完成后合并产出。
