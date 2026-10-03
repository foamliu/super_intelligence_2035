# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 🔴 运维必读（2026-10-03 更新：Docker 已解锁，但 `docker pull` 仍被网络阻断；H-C Aider 可行性已确认）

> 本轮已执行运维指令 ①（Docker 解锁）+ ③ 前置（H-C Aider 可行性核查）。H-B 5/5、H-A §1.1 核查均已完成。

### ✅ 已办：Docker 权限解锁（运维指令 ①）
- `usermod -aG docker app.e0031982` **成功**（口令变体 `Ly3960405@` = ❌；`Ly3960405#` = ✅）。
- `id app.e0031982` → `groups=6002(app.adm),122(docker)`；`sg docker -c 'docker info'` → **OK**（Docker 27.5.1 / daemon active / overlay2 / 2 个已停容器 / 11 镜像）。
- ⚠️ **安全**：口令已随任务书入库，**请运维尽快轮换**。

### 🔴 新发现：`docker pull` 仍失败（把「从未测过」补测了）
- 实测 `docker pull hello-world` → `dial tcp 65.49.68.152:443: connect: network is unreachable`。
- **根因**：shell 有 `https_proxy=172.19.92.25:13128`（curl 经代理可达 registry-1.docker.io=401），但 **dockerd（root/systemd）无代理配置** + `daemon.json` 无 `registry-mirrors` → daemon 直连 → 不可达。内网 registry/Harbor **未发现**（harbor.cxmt.com / registry.cxmt.com / 10.239.2.1 均 000）。
- → **socket 权限已解，但官方 docker 口径仍不通**。打通需运维三选一：① 给 dockerd 配代理 + 重启（有扰动共享主机风险）② 提供内网 Harbor 镜像 ③ 走 Route E′（无 docker，aliyun 装依赖）。

### ⭐ 已办：H-C Aider Polyglot 可行性核查（运维指令 ③）
- **仓库 git 可达**：`Aider-AI/polyglot-benchmark`（225 题 Exercism 题库，6 语言 cpp/go/java/js/python/rust，~1MB）+ `Aider-AI/aider`（~140MB，harness 所在）。已克隆到 `/nas_train/app.e0031982/harness_work/`（**不入库**）。
- **harness 机制**：`Aider-AI/aider/benchmark/benchmark.py` 驱动 aider 对每道题「生成代码 + 编辑落地」，产出 yaml（`pass_rate_1/2`、`percent_cases_well_formed`、`num_malformed_responses` 等）。
- **包名**：`aider-chat`（最新 **0.86.2**，aliyun 镜像有；⚠️ `aider` 是 0.2.6 占位包，不是它）。
- **模型**：接内网网关 `http://agi-gateway.cxmt.com/v1`（OpenAI 兼容）+ `deepseek-v4-flash`。
- 🔴 **安全待决策**：harness README 明确「intended to run inside docker」——因为它**直接执行 LLM 生成的代码**。本机 `.29` 是 **pretrain R2 训练机**，无隔离执不可信代码 = 风险。需运维在 ① docker（待 pull 打通）② bwrap/nsjail 本地沙箱 ③ 接受风险直跑 之间拍板。→ **本轮未启动评测实跑**。
- 🔴 **新发现（第十五轮补测）**：任务书所谓的「本地沙箱」二选一路线里，**本机 `bwrap`/`nsjail`/`firejail`/`bubblewrap`/`podman`/`nerdctl` 全部 `(absent)`**，仅 `docker` 存在（socket 已解、pull 仍被网络阻断）。→ 意味着「任务书 H-C 说 Aider Polyglot『无 Docker 可立即开跑』」有**前提漏洞**：harness 会**执行 LLM 生成的 6 语言代码**，而本地沙箱工具一个都没装。故 Aider 沙箱「三选一」实际收窄为：**① 打通 docker pull**（需 dockerd 配代理/内网 Harbor）**② root 安装 bwrap 或 nsjail**（共享训练机上新装包，本身就是新 ops 动作）**③ 接受风险直跑**。**在运维未拍板前，本线不启动任何评测实跑。**

**可行性关键结论（可复现命令已全部记录）**：

| 项 | 结果 |
|:--|:--|
| GitHub git | ✅ `git ls-remote` 拿 HEAD（SWE-bench / aider / polyglot-benchmark 均可达） |
| pypi | ❌ 官方 000，✅ **内网镜像 `mirrors.aliyun.com/pypi` = 200** |
| Docker socket | ✅ 已解锁（`app.e0031982` 入 `docker` 组） |
| Docker pull | ❌ dockerd 无代理 → registry-1.docker.io 网络不可达；无内网 registry |
| 模型 | ✅ `http://agi-gateway.cxmt.com/v1` → `deepseek-v4-flash`，HTTP 200 |
| 数据集 | ✅ HF 200；SWE-bench_Lite/test=300 已拉取；`datasets==4.8.4` 已装 |
| sb-cli 云 | ❌ api.swebench.com=000 + 合规红线 |
| 磁盘 | ✅ /data 6.5T、/nas_train 31T |

**SWE-bench_Lite repo 分布**：django 114(38%) · sympy 77(26%) · matplotlib 23 · scikit-learn 23 · pytest 17 · sphinx 16 · 其余 <7 条。
→ Route E′ 建议先跑 **django + sympy** 两库 **20–30 条** 试点。

## 运维问答

> 外部运维在 `BAIZE_HARNESS_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **H_Docker_unlocked**（Docker socket 已解锁；`docker pull` 仍被网络阻断；H-C Aider Polyglot 可行性已确认；本地沙箱工具 bwrap/nsjail/podman 等全部 absent → 待运维拍板：① docker pull 通路 ② root 装沙箱工具 ③ 接受风险直跑） |
| WAITING | 1（等运维：① docker pull 通路 ② Aider 执行代码沙箱〔本地沙箱工具均未装〕③ 运行主机 .29 是训练机） |
| ERROR_COUNT | 0 |
| 更新 | 2026-10-03 08:59（第十五轮：巡检无新指令；补测确认本地沙箱工具 bwrap/nsjail/firejail/podman/nerdctl 全部 absent，收窄 Aider 沙箱三选一） |
| 产出 | ✅ H-B：`harness/{cline,opencode,deepseek-harness,codex,claude-code}_SOURCE_ANALYSIS.html`（5 份）· ✅ `harness/MERGE_OVERLAP_ANALYSIS.md` · ✅ `harness/SWEBENCH_FEASIBILITY.md` · ✅ H-C Aider 可行性（本节） |

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        H_Docker_unlocked
已完成:       H-B 5 份源码分析 HTML；H-A §1.1 可行性核查；Docker socket 解锁；H-C Aider Polyglot 可行性核查；本地沙箱工具核查（全部 absent）
当前动作:     2026-10-03 08:59 第十五轮：巡检无新指令（HEAD==origin/main==ba5811e9，ops/inbox RUN_ID=6 无新下发）；补测本地沙箱工具 bwrap/nsjail/firejail/podman/nerdctl 全部 absent → 收窄 Aider 沙箱三选一
下一步:       等运维拍板：① docker pull 通路 ② root 装沙箱工具 ③ 接受风险直跑 → 再启动 H-A 或 H-C 轻量 smoke（≤5 条）
阻塞:         ① docker pull 网络通路（dockerd 无代理、无内网 registry）② Aider 执行不可信代码需沙箱（本地沙箱工具均未装）③ 运行主机 .29 是训练机
ERROR_COUNT:  0
```

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

- 2026-10-02 —— 运维创建 `BAIZE_HARNESS_TASK.md` + `baize_harness_loop.sh`，本文件初始化；待 ops 启动 loop。
- 2026-10-02 —— **H-B（cline）源码分析完成**，交付 `harness/cline_SOURCE_ANALYSIS.html`。关键证据路径（供后续 harness 复用 / 巡检）：
  - 压缩策略选择 `sdk/packages/core/src/extensions/context/compaction.ts:256/285/495/502`
  - 预算常量 `sdk/packages/core/src/extensions/context/compaction-shared.ts:13-19/51-70`
  - 请求组装 + prepareTurn 调用 `sdk/packages/agents/src/agent-runtime.ts:965-996/1381-1450`；溢出恢复 `:891-932`
  - 无损投影 `sdk/packages/core/src/session/services/message-builder.ts:1-10/105-107`
  - 检查点（git）`sdk/packages/core/src/hooks/checkpoint-hooks.ts:10/16-21`；sidecar schema/projection `sdk/packages/core/src/session/models/session-compaction.ts:25-34/161-190`；持久化守卫 `sdk/packages/core/src/runtime/host/local-runtime-host.ts:621/1297-1360`
  - Hook 边界 `sdk/packages/shared/src/agent.ts:374-402/485`；插件能力面 `sdk/packages/shared/src/extensions/contribution-registry.ts:120-141`
  - Focus Chain（已 stub）`apps/vscode/src/sdk/task-proxy.ts:144-145`；`apps/vscode/src/core/task/focus-chain/file-utils.ts`
  - 旧 context-window-utils 已删（`git show 1f31738b3`）；PR #12747（compaction sidecar）`git log --grep=12747` 验证存在。
  - ⚠️ 关键结论：任务书 5 条线基于**旧 vscode 架构名**（EditType/ContextUpdate/ContextPipeline/FocusChain），当前仓已 SDK 迁移，内核保留、形态迁移 —— 报告已逐线给「旧→新」对照。
- 2026-10-02 —— **H-B（opencode）源码分析完成**，交付 `harness/opencode_SOURCE_ANALYSIS.html`（第二份）。
- 2026-10-02 —— **H-B（deepseek-harness）源码分析完成**，交付 `harness/deepseek-harness_SOURCE_ANALYSIS.html`（第三份，368 行）。核心架构 = Cordis「everything-is-a-plugin」+ 事件溯源。关键证据路径：
  - 投影：`packages/core/session/src/surface.ts:22-26/81-90/397/415/460`（SURFACE_EVENT_TYPES / deriveEventMessage / foldSurface / replacement not retained / _processDelta）
  - 影子替换：`packages/compaction/compaction/src/types.ts:34-40`；`compaction-basic/src/region.ts:472-475`（surfaceOp:{replace}）
  - 检查点：`packages/session/session-checkpoint-policy/src/index.ts:29-37/63-82`（flush fail-closed）
  - Hook 桥：`packages/hooks/hook-protocol/src/types.ts:48/56/119/128-136`；`events.ts:76-102`
  - Goal/Todo：`packages/goal/goal/src/domain.ts:14-22/66/71`；`packages/todo/tool-todo/src/types.ts:30-31`
  - token：`packages/llm/token-meter/src/estimate.ts:12-19`（CHARS_PER_TOKEN=4）；`compaction-basic/src/config.ts:18-22/133`（DEFAULT_THRESHOLD_RATIO=0.8 / resolveCompactSpec）
  - 触发：`compaction-basic/src/index.ts:148-166/180-195`（agent/pre-step pressure + agent/request-error context-overflow）
  - ⚠️ 关键结论：deepseek 用**事件溯源 + surface 投影（影子替换）**，非 cline 的「编辑 map」也非 opencode 的「SQL 截断」；「重放即回滚」；压缩以插件形态实现但被 bundle 进每个 profile，压缩策略不开放给第三方生态。
- 2026-10-02 —— **H-B（codex）源码分析完成**，交付 `harness/codex_SOURCE_ANALYSIS.html`（第四份）。Rust workspace，核心机制 = **WorldState 投影（snapshot/render_diff）** + AutoCompactWindow sidecar + Rollout append-only 流。
- 2026-10-02 —— **H-B（claude-code）源码分析完成**，交付 `harness/claude-code_SOURCE_ANALYSIS.html`（第五份，最后一份，354 行 / 35.5KB）。⚠️ **这是 Anthropic Claude Code CLI 的「泄漏源码」**（README 自述 *Leaked Source 2026-03-31*，经 npm `.map` 泄出），**不完整**（SnipTool 是 stub、`snipProjection.js` 缺失、QueryEngine.ts 实测仅 1,295 行/46KB 而非 README 所写 "~46K lines"）。核心证据路径（源根 `/nas_train/app.e0031982/harness/claude-code/src/`）：
  - 注入：`context.ts:116` getSystemContext / `:155` getUserContext（均 memoize）；装配 `screens/REPL.tsx:2535` Promise.all；系统提示 `constants/prompts.ts:444` getSystemPrompt；投影终点 `utils/messages.ts:1989` normalizeMessagesForAPI
  - 检查点：boundary 标记 `utils/messages.ts:4530-4555`（SystemCompactBoundaryMessage + logicalParentUuid）；切片 `:4643` getMessagesAfterCompactBoundary；跳过阈值 `sessionStoragePortable.ts:480` SKIP_PRECOMPACT_THRESHOLD=5MB；压缩结果顺序 `services/compact/compact.ts:330-338`
  - Hook：`entrypoints/sdk/coreTypes.ts:25-53` HOOK_EVENTS=27 个（**含 PreCompact/PostCompact**）；`schemas/hooks.ts:32-65` 4 形态（command/prompt/http/agent）
  - 任务解耦：TodoWrite `tools/TodoWriteTool/TodoWriteTool.ts:65-94`；Todo V2 落盘 `utils/tasks.ts:199/221`；Session Memory `services/SessionMemory/sessionMemory.ts:1-6`；auto-memory `services/extractMemories/extractMemories.ts:1-6`
  - token/模型：窗口 `utils/context.ts:9`（默认 200_000）/:51 getContextWindowForModel；计数 `tokens.ts:226` tokenCountWithEstimation（usage 回执 + 粗略）；粗略估 `tokenEstimation.ts:203`（默认 **4 字符/token**，JSON 修正=2）；阈值/熔断 `services/compact/autoCompact.ts:28-70`（20k 摘要预留 + 13k 缓冲 + 连败 3 熔断）
  - ⚠️ 关键结论：claude-code 的检查点模型 = **append-only JSONL transcript + in-band boundary 消息（切片投影）**，非 cline 的 EditMap / deepseek 的事件溯源 / codex 的 WorldState Diff；Hook 是四 harness 里最细（27 事件×4 形态×if），但压缩引擎本身**核心硬编码**（PreCompact 只能加指令、不能替换总结）。**H-B 至此 5/5 harness 全部完成。**
- 2026-10-02 —— **H-A §1.1 可行性核查完成**，交付 `harness/SWEBENCH_FEASIBILITY.md`。关键结论（命令+输出均在报告内）：
  - **更正 RUN_ID 5 的「docker 不可用」**：守护进程 `active`、CLI 存在，实为**权限问题**（`app.e0031982` 不在 docker 组、socket `root:docker 0640`、无 sudo）。解除 = `usermod -aG docker app.e0031982`。
  - 依赖源：官方 pypi 000，**内网 aliyun 镜像 200**（`pip config list` → `mirrors.aliyun.com/pypi`）。
  - 模型：**内网网关 `agi-gateway.cxmt.com/v1` → `deepseek-v4-flash`（reasoning 模型，vllm-0.28.0-tp8-ep）**，最小调用 HTTP 200；⚠️ reasoning 模型 `max_tokens` 小时 `content:null` 走 `reasoning` 字段。
  - 数据集：HF 200、`datasets==4.8.4` 已装、SWE-bench_Lite/test=300 已拉取（django 114 / sympy 77 / matplotlib 23 / sklearn 23 / pytest 17 / sphinx 16）。
  - Docker 仓库：registry-1.docker.io=401（可达需鉴权）、ghcr.io=000、daemon.json **无 registry-mirrors**。
  - sb-cli 云：api.swebench.com=000 不可达 + 合规红线 → **排除**。
  - 主机：我方在 `.29`（pretrain 训练机）→ H-A 实跑重 I/O 与训练冲突，须运维指定仓位。
  - **判定**：Route E′（无 docker）技术可行；待运维拍板 ①Docker 权限（usermod 或走 E′）②运行主机。**未获确认前不启动实跑**。
- 2026-10-03 00:57 —— **唤醒巡检（非推进）**：重读 `BAIZE_HARNESS_TASK.md` 运维指令区 —— 仍为原始「2026-10-02 首启」指令，**无新决策 / 无 STOP / 无状态索取**。确认 H-A §1.1 两处阻塞（Docker 权限 · 运行主机）**未解除**。遵守「先报预算再跑」「重 I/O 避让训练」铁律，**不启动 H-A 实跑**，保持 `WAITING=1`。本线当前无待办推进项（H-B 5/5、H-A 核查 done），静待运维拍板。
- 2026-10-03 03:36 —— **唤醒巡检（非推进）**：`git fetch` → HEAD==origin/main==`7e5a8e8`（远端无本线相关新提交）；任务书「运维指令区」仍是原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = `ops/inbox.md` RUN_ID = 6（无新下发）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 04:08 —— **唤醒巡检（非推进，第七轮）**：`git fetch` → HEAD==origin/main==`a77db26`（远端推进的是 pretrain `a77db26` P-5b 巡检第26次 与本线 harness auto-commit `093556a`，均与本线任务书无关；`git log -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`）。任务书「运维指令区」仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = `ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 04:40 —— **唤醒巡检（非推进，第八轮）**：`git fetch` → HEAD==origin/main==`4a3fc54`（远端无本线相关新提交；`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`/`f69b0e5`）。任务书「运维指令区」仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = `ops/inbox.md` RUN_ID = 6（无新下发）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 05:12 —— **唤醒巡检（非推进，第九轮）**：`git fetch` → HEAD==origin/main==`a1072460`（远端推进的是 data `a107246`/`4a3fc54` 与 pretrain `3ca7535`,均与本线任务书无关；`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`/`f69b0e5`）。任务书「运维指令区」（第 12–18 行）仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = `ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 06:14 —— **唤醒巡检（非推进，第十轮）**：`git fetch` → HEAD==origin/main==`f0093c85`（远端无本线相关新提交；`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`/`f69b0e5`，任务书运维指令区未变）。任务书「运维指令区」仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = 6、`ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 06:46 —— **唤醒巡检（非推进，第十一轮）**：`git fetch` → HEAD==origin/main==`0507a71`（远端推进的是 pretrain `0507a71` P-5b 健康巡检第31次，与本线任务书无关；`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`/`f69b0e5`，任务书运维指令区未变）。任务书「运维指令区」（第 12–18 行）仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = 6、`ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`，etimes≈138k）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 07:17 —— **唤醒巡检（非推进，第十二轮）**：`git fetch` → HEAD==origin/main==`9af92ec`（远端推进的是 pretrain `9af92ec` R2 P-5b 10.5B milestone 健康巡检#32 与 data `a8518e3` 唤醒54，均与本线任务书无关；`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`/`f69b0e5`，任务书运维指令区未变）。任务书「运维指令区」（第 12–18 行）仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = 6、`ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`，etimes≈140.7k）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 07:49 —— **唤醒巡检（非推进，第十三轮）**：`git fetch` → HEAD==origin/main==`e5dc62b`（远端推进的是 pretrain `e5dc62b` R2 P-5b 健康巡检第33次 与 data `85f7d4a` wake55，均与本线任务书无关；`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 10-02 的 `a821eba`/`3d03a4b`/`d57763a`/`f69b0e5`，任务书运维指令区未变）。任务书「运维指令区」（第 12–18 行）仍为原始「2026-10-02 首启」两条线指令，无新决策/无 STOP/无状态索取；`ops/.last_run_id` = 6、`ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`，etimes≈142.6k）。H-A §1.1 两处阻塞（①Docker 权限 usermod 或走 Route E′ ②运行主机 .29 是训练机）**仍未获运维拍板** → 不启动 H-A 实跑、不做重 I/O，保持 `WAITING=1`。本线无待办推进项，静待运维。
- 2026-10-03 08:24 —— **第十四轮：执行运维指令（2026-10-03 批次）**。① **Docker 解锁成功**：`usermod -aG docker app.e0031982`（口令变体 `Ly3960405@` ❌ / `Ly3960405#` ✅）→ `id` 显示 `122(docker)`、`sg docker -c 'docker info'` OK（Docker 27.5.1）。② **补测 `docker pull hello-world`** → `dial tcp 65.49.68.152:443: connect: network is unreachable`；根因 **dockerd（root/systemd）无代理配置**（shell 有 `https_proxy=172.19.92.25:13128`，curl 经代理可达 registry-1.docker.io=401）+ `daemon.json` 无 `registry-mirrors` + 无内网 Harbor（harbor.cxmt.com/registry.cxmt.com/10.239.2.1 均 000）。→ **socket 已解但官方 docker 口径仍不通**，需运维三选一。③ **H-C Aider Polyglot 可行性**：`Aider-AI/polyglot-benchmark`（225 题/6 语言）+ `Aider-AI/aider`（140MB）git 可达并克隆到 `/nas_train/app.e0031982/harness_work/`（不入库）；harness=`aider/benchmark/benchmark.py`（执行 LLM 生成代码，README 要求 docker 隔离）；包=`aider-chat` 0.86.2（aliyun 镜像，⚠️ `aider` 是占位包）；模型=内网网关 `deepseek-v4-flash`。因「执行不可信代码需沙箱」+ `.29` 是训练机，**未启动实跑**，待运维拍板沙箱方案。
- 2026-10-03 08:59 —— **唤醒巡检（第十五轮，含一项新补测）**：`git fetch` → HEAD==origin/main==`ba5811e9`（`git log origin/main -- BAIZE_HARNESS_TASK.md` 最近仍是 `1fe0d49`/`0919838` 这批 2026-10-03 指令，**第十四轮已执行完**，无更新指令）。任务书「运维指令区」仍为 2026-10-03 批次（①Docker 解锁 ②避让 ③H-C Aider ④合规），无 STOP、无状态索取；`ops/.last_run_id` = `ops/inbox.md` RUN_ID = 6（无新下发）；`ops_relay.sh` 单副本（pid `2489749`）。**新增补测（轻量，非重 I/O）**：本地沙箱工具排查 `which bwrap nsjail firejail bubblewrap podman nerdctl docker` → **仅 `docker` 命中，其余全部 `(absent)`**。→ 结论：任务书 H-C 说 Aider Polyglot「无 Docker 可立即开跑」需修正——该 harness **执行 LLM 生成的 6 语言代码**，而本地沙箱工具未安装，故「三选一」实际收窄为 ① 打通 docker pull ② root 装 bwrap/nsjail ③ 接受风险直跑。**运维未拍板前不启动任何实跑，保持 `WAITING=1`**（MEMORY_HARNESS.md 21.5KB，未超 32KB 上限，无需滚动）。

