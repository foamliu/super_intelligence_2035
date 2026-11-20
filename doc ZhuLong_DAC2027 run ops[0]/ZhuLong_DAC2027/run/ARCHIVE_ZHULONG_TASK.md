

<!-- archived from ZHULONG_TASK.md 2026-10-19 23:0x (closed blocks) -->

<!-- 二十九 ZL 改 glm-5.2 -->
### 🆕 运维指令 · 2026-10-18（二十九）— 🔁 **ZL 评测基模改为 `glm-5.2`**（v4-pro-cloud 被网关 403 封族）→ 跑 158 集得分数【用户直令 · 最高优先 · 覆盖令二十八③的模型口径】

> **用户令（2026-10-18）**：「那就把 eda_platform 评测的基模换成 glm-5.2」
> ⇒ **令二十八的其他内容全部继续有效**（`eda_platform/apps/cli` 编译、`zhulong`/`zl` 安装、**不碰 cline 3.0.51**、隔离配置、158 集口径、n=1 标 provisional）；**仅替换"底模"这一项**：`deepseek-v4-pro-cloud` → **`glm-5.2`**。

**① 为什么可以换（已核实）**：`glm-5.2` @ `http://agi-gateway.cxmt.com/cloud/v1` 与你给的 key（`02_088EE…c2759d74`）**实测 200**（令二十八 agent 自测的对照组），且 gateway 401 已于 07:40 恢复 → **无阻塞**。

**② 重新配置（只改 zhulong 自己的 data dir）**
```bash
export PATH="$HOME/.local/bin:$PATH"
zhulong auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2 --data-dir ~/.zhulong
zhulong --version; zl --version
```
- 期望：`Provider configured: openai-compatible (glm-5.2)`；`--data-dir` 仍为 **`~/.zhulong`**；**🚫 不写 `~/.cline`**。
- 贴出生效的 `model=glm-5.2` / `baseUrl=…/cloud/v1` / key 末 8 位（应为 `88ea2f23`）/ data dir。

**③ 先做两个前置核验（上一轮漏了 SDK 版本，这次必须先补）**
1. **`@cline/core` 版本三连**（这是"老 SDK 0.0.51 改造版"的实验前提）：
   `grep -n '"@cline/core"' package.json apps/cli/package.json bun.lock | head` ·
   `cat node_modules/@cline/core/package.json apps/cli/node_modules/@cline/core/package.json 2>/dev/null | grep -m2 version` ·
   `bun pm ls 2>/dev/null | grep -i cline | head`
   → **期望 `0.0.51`**；若不是（如被解析到 `0.0.71+`），**照实记录并继续跑**，但必须在回报里显式标注"SDK 已漂移，对照含义变化"，🚫 不得隐瞒。
2. **cline 3.0.51 未被改动**：`cline --version`（=3.0.51）+ `readlink -f $(which cline)` 与令二十八取证**逐字一致**。

**④ 起跑（口径照旧，只换模型）**
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
export PYTHON=$PWD/venv/bin/python
setsid bash scripts/run_zhulong_script.sh -p 8 -n > /tmp/ZL_glm52_r1.log 2>&1 < /dev/null &
```
- 评测集 `EDA-Eval-pyAether-158`；4 端口 `8650/8651/8652/8654` + `SANDBOX_HOST=10.129.32.75` + V3 文档 + 自探索 ON；**反作弊 hook canary 必须先过**（应被拒未被拒 ⇒ 停，本批作废）。
- 若出现 **429/限流**（glm 族历史上有并发限流）⇒ 按令二十七① **降 `-p 4` 重跑一次**（只降并发，不改模型/配置），心跳注明。
- 若出现 **401/403** ⇒ 立即停，贴响应头原文，报 blocker（不空转）。

**⑤ 打分与回报（本轮就要）**
1. 构建产物与安装不变项：`zhulong --version` = **3.0.29** vs `cline --version` = **3.0.51**（版本差异即被测变量）。
2. 配置三项（model / base / data dir）+ ③ 的两个核验原文。
3. **`glm-5.2` × `zhulong(3.0.29)` 158 题 Pass@1 = xx.x%（通过数/158）** + `pass (` 原文 + timeout / gen-fail / quota 计数。
4. **对照必须写清"同模型、不同 CLI/SDK"**：既有 `glm-5.2` 臂 = **83.3±3.1%（n=5，cline 3.0.51 / cline-core 0.0.71）**；本次为 **n=1、zhulong 3.0.29**，因此只能单值 + `[provisional,n=1]`，🚫 不得写 ±、🚫 不得据此断言"改造版更好/更差"（n=1 + 版本双变量）。
5. 同步 `MEMORY_ZHULONG.md`（STAGE=`ZL`，CONFIG 改为 `ZL.glm-5.2`）+ `zhulong_results.md` 新增一行（标 `[provisional,n=1]`，注脚写 `zhulong 3.0.29 / cline-core X` 与 `cline 3.0.51 / cline-core 0.0.71` 的对照）+ `daily-memories/2026-10-18.md`；commit 前缀 `zhulong zl:`。

**⑥ 红线（不变）**
- 🚫 覆盖/删除/重链 cline 3.0.51、改 `~/.cline`、`curl|bash` 官方安装器。
- 🚫 不改论文口径、不 kill loop / ops 中继 / 别人在跑的任务；n=1 不进论文表。
- ✅ 每轮只推进一步；`WAITING=1` 仅在评测真正跑起来时置位。


> **用户令（2026-10-18）**：「编译 `eda_platform` 目录下的 `cline-cli`，把它安装成命令行工具 `zhulong`/`zl`，设置使用 `DeepSeek-V4-Pro-Cloud` 这个底模，用你一直使用的评测集测试一次，得出分数。」
> **用户补充（同日，必须遵守）**：① `eda_platform` **本身就是 cline 仓库改造而来**，`apps/cli` 就是原来的 cline → **直接编 `eda_platform/apps/cli`，不用满盘找**；② **36.15 已装的 cline 3.0.51 不许覆盖/删除/改动**——迄今所有被测分数都是它跑出来的基线；新产物只叫 `zhulong`/`zl`。
> ⚠️ **本条优先级高于令二十七（glm-5.3 复测）**；glm-5.3 复测暂停，等本条跑完或网关恢复后再议。

**① 路径与前提**
- 仓库根：`eda_platform`（36.15 本机，`/nasdata/...`）。目标包 = **`apps/cli`**（`package.json` 里应是 `@cline/cli` 或改造后的同名包）。先 `cd <eda_platform> && git status -sb && git log --oneline -1` 记录源版本。
- 🔢 **用户提供的关键前提（务必按此解读结果）**：
  - `eda_platform` 里的 cline 是**老版本**，其 **`cline-core` SDK 版本 = `0.0.51`**；
  - 被测基线 **cline 3.0.51 的 `cline-core` SDK 版本 = `0.0.71`**。
  - ⇒ 这条线测的是**"老 SDK 的改造版" vs "新 SDK 的官方版"**，SDK 代差是**结果的主要解释变量之一**，回报时必须显式写明两侧 `cline-core` 版本（`zhulong` 侧 = 你构建出来的实际版本，`cline` 侧 = `0.0.71`）。
  - 构建后**必须实证**：`eda_platform` 里解析到的 `cline-core` 版本（查 `bun.lock`/`bun.lockb`/`package.json` 的 `dependencies`、`node_modules/@cline/core/package.json` 的 `version`，以及 `apps/cli/node_modules` 下的实际链接）→ 若是 **`0.0.51`** 就照实记录；若解析成别的版本（例如网络拉到最新），**不要偷偷升级**，如实报告并停在这一步等运维确认。
- 工具链：`bun`（cline 上游用 bun，36.15 已装）+ `node`。装依赖走内网镜像（`https://mirrors.aliyun.com/npm/` / 腾讯 npm）。外网命令带 `https_proxy=http://172.19.92.23:13128`；**访问 `agi-gateway.cxmt.com` 必须剥掉 proxy**（`env -u https_proxy -u http_proxy ...`）。
- 🚫 不 clone 别处的 cline 顶替、不 `git checkout` 别人的改动、不改 `eda_platform` 源码（本次只“编译 + 安装 + 跑分”）；**`bun install` 之后先用 `bun pm ls | grep cline` 核对 SDK 版本没被悄悄换掉**。

**② 🔴 硬红线：不碰现有 cline 3.0.51（先取证，再动手）**
1. 先记录基线（原文贴心跳）：
   `which -a cline; cline --version; ls -l $(which cline); readlink -f $(which cline); ls -ld ~/.bun/bin/cline ~/.bun/install/global/node_modules/@cline 2>/dev/null`
   ——3.0.51 是**被测基线**，本轮任何操作都不得让它失效。
2. **禁止**：`curl .../install.sh | bash`、`bun add -g @cline/cli`、`bun link`/`bun pm link` 到 `@cline/cli`、`bun install -g`、`npm i -g @cline/*`、覆盖 `~/.bun/bin/cline`、改 `~/.bun/install/global/node_modules/@cline`、改 `~/.cline/`（配置与 hook）。
3. `eda_platform/apps/cli` 里若本来就叫 `@cline/cli`：**改的都是产物名字与安装位置，不改包里 `bin` 名**（例：把构建产物复制成 `~/.local/bin/zhulong`，不要 `bun install -g` 把 `cline` 重新链过去）。
4. 收尾必须复核一次：`cline --version` 仍为 **3.0.51**、`readlink -f $(which cline)` 与第 1 步一致；否则**立即报告并停止后续步骤**。

**③ 编译 + 安装（只出 `zhulong` / `zl`）**
1. 按 `apps/cli/package.json` 的**原始脚本**构建（如 `bun run build` / `bun build ... --target=bun`），记录命令原文与耗时。
2. 安装到**独立前缀**：`~/.local/zhulong/`（或 `~/.zhulong/bin/`），入口 = `~/.local/bin/zhulong` + `~/.local/bin/zl → zhulong`；`chmod +x`。
3. 验收（原文贴心跳）：`zhulong --version`、`zl --version`、`which -a zhulong zl`、`ls -l ~/.local/bin/{zhulong,zl}`；**并给出 `zhulong --version` 与 `cline --version`(3.0.51) 的对比**（版本不同是正常的，这正是要测的变量）。
4. **SDK 版本三连核验**（原文贴心跳，三处都要）：
   - `eda_platform`：`grep -rn '"@cline/core"' package.json apps/cli/package.json bun.lock 2>/dev/null | head`
   - 实装：`cat node_modules/@cline/core/package.json apps/cli/node_modules/@cline/core/package.json 2>/dev/null | grep '"version"'`
   - 运行期：`zhulong --version`（若 CLI 会带出 SDK 版本就一并贴；不会就明确写"CLI 不暴露"）
   - 判据：**`@cline/core` 应为 `0.0.51`**（老版）。若因 `bun install` 被解析到 `0.0.71` 或更新 ⇒ **不要继续跑分**，先报告（这是"老版改造是否还具备实验意义"的前提，由运维决定）。

**④ 配置底模 = DeepSeek-V4-Pro-Cloud（与 cline 3.0.51 配置隔离）**
- `deepseek-v4-pro-cloud` @ `http://agi-gateway.cxmt.com/cloud/v1`（历史实测 200；**别混 `/v1` 下的 `deepseek-v4-pro-fp4`**，那个是 403/429）。
- `zhulong` 使用**独立 data dir**（`--data-dir ~/.zhulong` 或该版本等价参数），key 复用 `eda_fastmcp/providers.json` / `.env` 里 `02_088EE...` 同批 key，**不许写进 `~/.cline`**。
- 验收：`curl` 一次 chat/completions 得 HTTP 200 + 有 content（当前网关可能仍 401）；贴出生效 `model` / `base url` / key 末 8 位 / data dir。

**⑤ 跑一次评测（口径不变，1 轮）**
- 评测集 `EDA-Eval-pyAether-158`（`benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl`），`Pass@1 = 通过/158`。
- 复用 `eda_fastmcp/scripts/run_cline_script.sh`：**复制一份** `run_zhulong_script.sh`，**只把其中 `cline` 换成 `zhulong`（或 `zl`）这一处**；参数、判定、hook、端口一律不动。
- `-p 8 -n`；若 401/429 致整批作废，按令二十七①「0-token>10%」降 `-p 4` 重跑一次（**只降并发**，心跳注明）。
- 环境照旧：4 端口 `8650/8651/8652/8654`（`SANDBOX_HOST=10.129.32.75`）+ V3 文档 + 自探索 ON + **反作弊 hook canary 必须生效**。
- 日志 `/tmp/ZL_v4procloud_r1.log`；打分 `grep -E 'pass \(|评估结果汇总|PASS_RATE'`，**以 `pass (xx.x%)` 为准**；timeout / 0-token / quota 单列，不算模型分数。

**⑥ 回报（本轮就要，写完再退出）**
1. `eda_platform` 路径 + `git log -1` + 构建命令原文 + 产物大小 + `zhulong`/`zl` 验收原文。
2. **版本对照表（必填）**：`zhulong` 的 `@cline/core` 实测版本（应为 **0.0.51**）vs `cline` 3.0.51 的 `@cline/core` = **0.0.71**；`zhulong --version` vs `cline --version`。
3. **cline 3.0.51 未被改动**的证据：`cline --version` + `readlink -f`（与 ②-1 逐字一致）。
4. 生效配置（model / base / key 末 8 位 / data dir）。
5. **`DeepSeek-V4-Pro-Cloud` 158 题 Pass@1 = xx.x%（通过数/158）** + `pass (` 原文 + timeout/gen-fail/quota 计数。
6. 对照一句：vs `deepseek-v4-flash` 60.1±5.5%（n=5，SDK 0.0.71）· `glm-5.2` 83.3±3.1%（n=5）· 主基座 `deepseek-v4-pro-fp4` 82.1±3.0%（n=5）。**n=1 只报单值并标 `[provisional,n=1]`，禁止写成 ±**；**差异不得归因于模型，须并列写明"SDK 0.0.51 vs 0.0.71"**。
7. 同步 `MEMORY_ZHULONG.md`（STAGE=`ZL`）+ `zhulong_results.md` 新增一行（标 `[provisional,n=1]` + `SDK 0.0.51` 注脚）+ `daily-memories/2026-10-18.md`；commit 前缀 `zhulong zl:`。

**⑦ 纪律（红线）**
- 🚫 覆盖/删除/重链现有 cline 3.0.51、改 `~/.cline`、跑 `curl|bash` 官方安装器。
- 🔢 **`@cline/core` 必须是 `0.0.51`**：若 `bun install` 后变成 `0.0.71`/更新（网络解析到最新），**停下来报告**，不要用升级后的 SDK 跑分（那就不是"老版改造"了）。
- 🚫 不改论文口径、不 kill 本 loop / ops 中继 / 别人在跑的任务。
- 🚫 不把 n=1 的分数写进论文表（只进 `zhulong_results.md` 并标 provisional）。
- ✅ 每轮只推进一步（取证 → 构建 → 安装 → 配置 → canary → 跑 → 打分 → 回报），`WAITING=1` 只在评测真正跑起来时置位。
- 体积：任务书 ≤40KB（超了按常驻规程自己滚归档，**只搬已闭合块原文**）。

<!-- 二十五 消融中文建议书 -->
### 🆕 运维指令 · 2026-10-15（二十五）— ⏰ 催办：消融试验中文建议书（指令二十一）尚未交付 · 现在就要【已完成·2026-10-15 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-15 17:35）。报告 `reports/report_zhulong_next_ablation_plan_zh.html` 已交付（32927B·10节·commit c1a3d177 @ 17:01:57·已push）。


<!-- archived from ZHULONG_TASK.md 2026-10-19 23:1x (batch 2) -->

<!-- 三十二 GLM-5.3 后队列（已被 23:0x 取代） -->
### 🆕 运维指令 · 2026-10-18（三十二）— 🔀 **GLM-5.3 r2-r5 之后的队列**：pro-fp4/pro-cloud → (N′)；否则 DeepSeek-V4-Flash 第二遍 → Qwen3.8-27B【用户直令 · 最高优先】

> 用户令：「ZhuLong：等 GLM-5.3-Flash r2-r5 测完后，再试试 deepseek-v4-pro-fp4 / pro-cloud，如果通了，就测 (N') 5-run；否则测 DeepSeek-V4-Flash 5-run 第二遍，然后 Qwen3.8-27B 5-run。」
> **前置**：先完成令三十一的 B.glm-5.3-flash r2-r5（5/5 + mean±std + 更新 results），再进入本队列。**严格串行**，不得并行抢端口。

**① 先探针（r2-r5 收口后立即做）**
- `deepseek-v4-pro-fp4` @ `/v1` 与 `deepseek-v4-pro-cloud` @ `/cloud/v1`：各用现有 key 做 canary；**HTTP 200 + content = 通**；403 = 封；429 = 等窗口。
- 优先 **pro-fp4**；pro-fp4 不通再试 **pro-cloud**；两者都不通 → 走 ③。
- 记录每路 HTTP 原文/响应头（不打印 key）。

**② 若 pro-fp4 / pro-cloud 任一通 → 跑 (N′) 5-run**
- 严格按 `PLAN_RETEST_READBACK_COST.md` 的 (N′) 规格（readback_none / no observation 成本重测），**不得改配方**；5 次独立 run，同 harness/端口/seed 口径。
- 若用 **pro-cloud** 而非 pro-fp4，必须在报告里注明「模型部署不同（cloud vs fp4）」，不得当作同一模型。
- 每轮打分：Step 7.1 auto-grade 已知 FileNotFoundError → **手动 regrade**（照 r1 模板，`unset proxy + NO_PROXY=10.129.32.75 + EVAL_FW_DIR=/nasdata/.../EDA-Eval-Framework`）；记录 `pass (xx.x%)` + timeout/gen-fail/0-token/quota。
- 5/5 后 mean±std，更新 `zhulong_results.md`；若 429/限流，降 `-p` 或等窗口，不得静默作废。

**③ 若两者都不通 → 按顺序跑**
1. **B.deepseek-v4-flash 第二遍 5-run**：同第一遍复测配置（`-p 4`、`maxTokens=16384`、full harness、V3+自探索 ON、key `c43c1f4a`），5 次独立 run，标签 `retest2`/`second 5-run`；对比 fresh 11.9±2.7、第一遍 60.1±5.5；5/5 有效后 mean±std，更新 results。
2. **Qwen3.8-27B 5-run**：先 canary 确认网关模型名/端点/key（**不要猜模型名**；若网关无此模型/403/429 → 停并贴原文报 blocker，不硬跑、不伪造）；确认后同 full harness + V3 自探索，`-p` 先 4；5 次独立 run；5/5 后 mean±std，更新 results。
- 两段都完成后更新 `zhulong_results.md` + MEMORY + daily；commit `zhulong B:` / `zhulong qwen:`。

**④ 纪律**
- 只有令三十一 r2-r5 收口后才进入本队列；不得并行、不得抢 4 端口。
- `(N′)` / DeepSeek-V4-Flash second / Qwen3.8-27B 都按 5-run mean±std；n<5 不得写 ±。
- 不碰论文口径；不杀 loop/中继；每次只推进一步。

**⑤ 网关探针不需要等 ops 中继（2026-10-18 20:5x 备注）**
- 中继（`ops_relay.sh`）近 1.5h 未消费任何 RUN_ID（137/138/139 均无回执，而 pretrain/zhulong push 正常）⇒ **不要因为「中继没回」就阻塞本队列**。
- 你在 `.29` 本机，**可直接在本机用 curl 做 canary**（剥 proxy + `NO_PROXY`，不打印 key），结果照 ① 记录；只有需要 `.12` 数据侧的日志才走中继。
- 中继重启属 harness 线 P0，不在本任务内处理；🚫 不要在命令行里直接 `pkill -f ops_relay.sh`（会自匹配杀到自己的 shell）。

<!-- 二十七 deepseek-v4-flash 复测（已闭合 60.1±5.5%） -->
### 🆕 运维指令 · 2026-10-17（二十七）— 🔁 复测 B.glm-5.3-flash 和 B.deepseek-v4-flash（trace 诊断发现基础设施问题）【用户直令】

> **用户令（2026-10-17）**：「DeepSeek-V4-Flash 的跑分比预期低，你去看下 trace。复测 GLM-5.3-Flash 和 DeepSeek-V4-Flash。」

**① 背景·trace 诊断结论**（运维侧已完成分析）：

**DeepSeek-V4-Flash fresh 5-run = 11.9±2.7%**，但 trace 分析发现 **73% 失败是基础设施问题，非模型能力**：
- **45% (356/790) 0-token 失败**：API gateway 并发限流，请求 6 秒内被拒（inputTokens=0, outputTokens=0）。时间线证据：r1 首批 8 并发成功，40 秒后后续请求开始 0-token 失败。
- **28% (219/790) null-content 失败**：deepseek-v4-flash 是**推理模型**，先产出 reasoning token 再产出 content。cline 配置 `reasoning: {enabled: false}` + max_tokens 不足 → reasoning 耗尽 token 预算 → content=null → cline 写 `pass` 占位。
- **9.4% (74/790) real-code-fail**：模型真正写错代码。
- **关键**：在模型**实际产出代码**的 178 个任务中，**通过率 = 104/178 = 58.4%**（若算上 gen-success 但 regrade-fail 则更高）。11.9% 被基础设施严重拖低。

**GLM-5.3-Flash 5-run = 66.8±10.5%**，trace 分析：
- GLM-5.3-flash **非推理模型**（8 并发 API 测试全部 HTTP 200 + 有 content），无 reasoning 耗尽问题。
- gen-fail 率 23.4%（含少量 0-token 2.9% + 部分 null-content 14.1% + real-fail 6.2%），gen-success 605/790 = 76.6%。
- 在产出代码的任务中通过率 528/605 = 87.3%。
- **std=10.5 偏大**（r1=80.4 / r2=53.2 / r3=73.4 / r4=65.8 / r5=61.4），复测目标：确认是否为模型真实方差或仍有隐藏 infra 因素。

**② 复测规格**：

**B.deepseek-v4-flash 复测（优先·修复基础设施）**：
- **并行度 8 → 4**（缓解 gateway 并发限流，减少 0-token 失败）
- **maxTokens 8192 → 16384**（方案 A·2026-10-17 16:32 已 apply 到 `providers.json`·`updatedAt=2026-10-17T08:32:44Z`·backup=`providers.json.bak.maxTokens8192`）。**根因**：deepseek-v4-flash 是 reasoning 模型，`max_tokens` 是 `reasoning_tokens + content_tokens` 的合并上限。简单调用 reasoning 就烧 4413 token，复杂调用可烧 8000+ → 8192 被吃光 → content=null。**其它模型没问题**因为：deepseek-v4-pro-fp4 reasoning 极省（简单 44 token）/ glm-5.2 / kimi / doubao / glm-5.3-flash 是非推理模型（reasoning_tokens≈0），全部预算给 content。`reasoning: {enabled: false}` 在 cline 侧只控制是否传 reasoning flag，**不控制 API 端是否推理**——API 网关侧 deepseek-v4-flash 永远是推理模型，实测 `reasoning_tokens=4413` 证实。fresh 5-run（11.9%）时 providers.json **未设 maxTokens** → API 用更紧的默认值（疑 4096）→ null-content 率 28%；retest r1 设 8192 → null-content 降到 7%；r3 起用 16384 → 目标 null-content ≤2%。备选方案 B（`{"thinking":{"type":"disabled"}}` 经 extra_body 禁推理）未采纳——风险是降模型复杂任务表现。
- 其余配置不变：backbone=deepseek-v4-flash @ `/v1` key `c43c1f4a`，full harness（OMEGA=high / READBACK=full / BUDGET=0 / LAGGED=0），V3 文档 + 自探索 ON
- 5-run fresh，判据(十三)：timeout≤10 且无 infra 故障
- **⚠️ 若 0-token 失败仍 >10%，再降并行度到 2**

**②·bis r1 trace 深度诊断（2026-10-17 16:00·用户令「60% 也偏低，再看看 trace」）**：

retest r1 = 60.1% (95/158) 的 63 个失败分解（batch `2026_1017_091724`，-p 4 + maxTokens=8192）：

| 失败类型 | 数量 | 占比 | 根因 | 可修复？ |
|---------|------|------|------|---------|
| 🔴 cancelled + editor=0 | **19** | 12.0% | Agent 用 `run_commands`(shell) 做文件操作，**全部被 anti-leak hook 阻断**（"ACCESS RESTRICTED"），**19/20 从不使用 `editor` 工具保存代码** → 放弃或循环到超时。Agent 已正确 search_apis + get_api_details + 规划方案，但无法保存代码文件 | ✅ 工具引导（prompt 或禁 run_commands） |
| 🟠 0-token | 17 | 10.8% | 全部在 batch 末尾（任务 142-158，03:14-03:15 UTC，batch 最后 1 分钟）。**-p 4 没用**——不是并发限流，是 **API 日配额在跑完 ~140 个任务后耗尽**。紧接的 r2 确认 HTTP 429 | ✅ 配额保障（非降并行度） |
| 🟡 null-content | 11 | 7.0% | Agent **正确使用 MCP 工具**（search 8-154 次 + run_code 4-288 次），但**最后一次 API 调用** reasoning 耗尽 8192 → content=null。复杂任务尤其严重（task 111: 1105 msgs, 288 run_code, 14.7M input tokens） | ✅ maxTokens 16384（方案 A·已 apply） |
| ⚪ regrade-fail | 13 | 8.2% | 代码生成成功但 regrade 未通过 | ❌ 模型能力 |
| ⚪ code-fail | 2 | 1.3% | 代码有误 | ❌ 模型能力 |
| cancelled + editor>0 | 1 | 0.6% | 用了 editor 但未收敛 | ❌ 模型能力 |

**关键证据**：
- PASS 任务全部使用 `editor`（1-39 次）保存代码；CANCELLED 任务 19/20 的 `editor` 调用数 = **0**
- PASS 任务 tool 分布：`pyAether_MCP_server__run_code`=1443 / `search_apis`=767 / `get_api_details`=413 / `editor`=369
- CANCELLED 任务 tool 分布：`search_apis`=539 / `run_code`=371 / `run_commands`=257（全 blocked）/ `editor`=55（仅 1 任务）
- task 044 示例（17 msgs 后 cancelled）：正确 search_apis 找到 `dmLibObj`/`dmGetObjType`/`dmSizeLibrary` + get_api_details + 规划实现 → 调 `run_commands({'commands':['mkdir -p ...']})` → ACCESS RESTRICTED → 再试 5 次 ls/pwd/find/mkdir → 全 ACCESS RESTRICTED → cancelled，**从未尝试 `editor`**

**可修复空间估算**：当前 60.1% → 修复 #1（editor 引导）+19 → 72.8% → 修复 #2（配额）+17 → 83.5% → 修复 #3（maxTokens 16384）+11 → 90.5%。真实模型能力上限（regrade-fail + code-fail 不可修）≈ 90%。

**r2b regrade = 57.0% (90/158)**（batch `2026_1017_135447`·gen 110 ok / 48 fail / 0 timeout / 18 quota-error·判据十三 timeout=0≤10 有效）。r2b 仍用 maxTokens=8192（16384 在 r2b 完成后才 apply）。r2b 比 r1 低 3.1pp，可能因 r2b 的 18 条 quota error 拖低（r1 的 17 条 0-token 全在末尾 142-158，r2b 的 18 条分散在中间）。

**B.glm-5.3-flash 复测**：
- 配置不变：backbone=glm-5.3-flash @ `/v1` key `6903b05e`，full harness，V3 + 自探索 ON
- 并行度保持 8（API 测试确认 8 并发无问题）
- 5-run fresh，判据(十三)
- 目标：确认 std 是否收窄（当前 10.5 → 目标 <8）

**③ 执行顺序**：
1. **当前 wo_selfexpl r1 regrade 已由运维侧手动启动**（PID 1597537 · batch 2026_1017_055109 · 08:45）→ r1 评分出结果即可，**r2-r5 不用再跑**（陈熙元已测 wo_selfexpl = 77.3±2.9%，作为对照，见 `zhulong_results.md`）
2. **B.deepseek-v4-flash 复测 5-run**（本指令②规格）
3. **B.glm-5.3-flash 复测 5-run**（本指令②规格）

**④ 收口后**：
- deepseek-v4-flash：对比 fresh(11.9%) vs 复测，若大幅提升则替换 `tab:llm-comparison` 行 + 在论文注明「初测受 gateway 并发限制影响」
- glm-5.3-flash：对比 66.8% vs 复测，若 std 收窄则替换
- 同步 `zhulong_results.md` + `MEMORY_ZHULONG.md`

**⑤ 纪律**：切配置后 canary 自检；commit 前缀 `zhulong B:`；/home<8G 暂停清理。

<!-- 二十六 wo_selfexpl 排队（已闭合） -->
### 🆕 运维指令 · 2026-10-16（二十六）— 🔜 排队：B.deepseek-v4-flash 之后接 wo_selfexpl 干净 5-run【用户直令·已被二十七①取代·2026-10-18 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-18 02:57）。被运维令二十七①取代：wo_selfexpl r1=83.5%(132/158) 收口（batch 2026_1017_055109·运维侧手动启动 regrade），**r2-r5 不再跑**（陈熙元 77.3±2.9% 作为对照）。


<!-- archived from ZHULONG_TASK.md 2026-10-19 23:2x (batch 3) -->

<!-- 三十一 glm-5.3-flash 复测（已闭合 86.8±1.6%） -->
### 🆕 运维指令 · 2026-10-18（三十一）— ▶️ **启动 B.glm-5.3-flash 复测 5-run**（`-p 4` 起步）【用户直令 · 最高优先】

> 用户令（2026-10-18）：「让 zhulong 启动 B.glm-5.3-flash 复测」。
> 背景：fresh 5/5 = **66.8 ± 10.5%**（std 偏大）；此前 r1 两次在 `-p 8` 因 gateway 并发/quota 作废（0/158、89% 失败）。**本次先 `-p 4`**；若仍 429/0-token >10%，再降 `-p 2` 或等 off-peak，**不得静默作废**。

**① 前置（任一不过就停，贴原文）**
- `glm-5.3-flash` @ `/v1` 单请求 canary：HTTP 200 + 非空 content；`maxTokens=16384`（`providers.json` 已设）。
- 记录并发用户任务（如 `app.t0002147`）；若 canary 429 ⇒ 等 10–20min 重试，**不启动 5-run**。
- 确认 backbone 配置未被改成其它模型；`EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework`（`.env` 已修正）。

**② 起跑（每轮一条，串行 5 轮）**
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
export PYTHON=$PWD/venv/bin/python
setsid bash scripts/run_cline_script.sh -p 4 -n > /tmp/ABL_glm-5.3-flash_retest_r<N>.log 2>&1 < /dev/null &
```
- 每轮 158 题；跑完先 `unset http_proxy https_proxy ALL_PROXY; export NO_PROXY=10.129.32.75,localhost,127.0.0.1`，再用 `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework` 跑 `run_eval.py` 打分（避免 Squid 503）。
- 判据：`timeout≤10`、无 infra 故障；429/quota 不计有效轮，等窗口重试；401/403 立即停贴响应头。
- 每轮记录：`pass (xx.x%)`、timeout/gen-fail/0-token/quota，写 `daily-memories/2026-10-18.md`。

**③ 收口**
- 5/5 有效后算 mean±std；若 std 明显 <10.5，更新 `zhulong_results.md` 的 B.glm-5.3-flash 行（保留 fresh 66.8±10.5 作对照）+ `MEMORY_ZHULONG.md` + commit `zhulong B: glm-5.3-flash retest 5/5 = xx.x±x.x%`。
- 🚫 不动 ZL.glm-5.2 r1=84.2% 的结论；🚫 不改论文口径；🚫 不重启/不经手其它线。
- 完成后按常驻规程自滚归档任务书。


<!-- archived from ZHULONG_TASK.md 2026-10-20 (consolidated closed 1-line pointers, batches 10-11 ~ 10-04) -->

### [归档·2026-10-20] 🧭 本轮（2026-10-11 上午）执行顺序 —— 换回旧 4 端口 + 修 RAG + 删 hook → 推进 r2–r5【已完成·2026-10-13 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。r2–r5 已完成，当前已推进至 C2.phi_k3。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-11（十二）— r5 收割后补跑 5 轮「真正的 full」（自探索开启）【full_v3 5/5✅ 82.1±3.0% 已交付·2026-10-13 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。full_v3 5/5 = 82.1±3.0% 已交付（三组对照表见 `MEMORY_ZHULONG.md`），未复现 r1=88.0%。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-11（十一）— 📊 Deep dive：为什么 `full` r1=88.0%【⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`·报告已交 `reports/R1_ANOMALY_ANALYSIS_2026-10-11.html` @commit 25b27adb】

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-11（十）— 🔎 RAG(9006) 排查【⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`·已收口·报告 `reports/RAG_AUDIT_2026-10-11.md` @commit 84e66335】

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-11（九）— 换回旧 4 端口 + RAG→9006 + 删 hook + .env 回退 + 重跑 r2–r5【已完成·2026-10-13 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。换回 4 端口 8650/8651/8652/8654 + RAG→9006 + 删 hook + .env 回退均已完成，r2–r5 已交付。

### [归档·2026-10-20] （八）10-10 — 保留 4 端口 + `"timeout": 180` + 重跑 r2–r5【已被 (九) 取代·已归档】
### [归档·2026-10-20] （七）10-10 — 剔除 8667 + 补 8650–8654 + 调高 MCP timeout【已被 (八) 取代·已归档】
### [归档·2026-10-20] （六）10-10 — 若 9 端口健康先判别「端口数是否真因」【已被 (七) 取代·已归档】
### [归档·2026-10-20] （四）10-10 — 根因排查：连续多日 timeout【已完成·已归档】
### [归档·2026-10-20] （三）10-10 — 先停 zhulong + 实测沙盒端口【已完成·已归档】
### [归档·2026-10-20] （二）10-10 — 专属沙盒就绪：保 r1 → 重跑 r2–r5【已被 (三)/(四) 取代·已归档】
### [归档·2026-10-20] （一）10-10 — 切专属沙盒 + C1.full 作废重测【已被 (二) 取代·历史】
### [归档·2026-10-20] 🆕 运维指令 · 2026-10-09（五）— ✅ 沙盒已修复，可重跑 C1.full r4【已被 2026-10-10(一) 取代·已归档】
### [归档·2026-10-20] 🆕 运维指令 · 2026-10-09（四）— 🛑 沙盒坏了，r4 已被运维 kill，待命不要重跑【已被(五)取代·历史】
### [归档·2026-10-20] 🆕 运维指令 · 2026-10-09（三）— 🔄 C1.full r2/r3 复测（模型服务不稳定致大量 timeout）【已归档·被(四)取代】
### [归档·2026-10-20] 🆕 运维指令 · 2026-10-09（二）— ✅ 沙盒已就绪，可开跑 C1.full r4【已完成·已归档】
### [归档·2026-10-20] 🆕 运维指令 · 2026-10-09 — ✅ pro-fp4 403 已解决（换 key）+ 🚫 暂不启动 r4（沙盒重启中）【已完成·已归档】

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-08（一）— 📝 HTML 报告【已完成·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-08）。产物 `reports/report_2026-10-08_holiday.html`（21870B，8 节齐全，已 commit a4dc5c3c）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-05（八）— ops 中继恢复【已解决·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。ops relay alive ✅（每次唤醒复检）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-05（七）— 评测侧隔离 config dir【已落地·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。合并线 eval 用 `CLINE_CONFIG_DIR=.cline_eval_zhulong`；编排用 `--config .cline_zhulong`。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-05（六）— 试验次序调换 B→C1→C2→S1【已生效·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前顺序 B→C1→C2→S1（§4 已同步）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-04（五）— legacy 组件 loop 保活【常驻·已稳定·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。legacy loop alive ✅（每次唤醒复检）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-04（四）— 正式起始点 C1.wo_retrieval R2【已越过·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前已推进至 C1.full r1。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-04（三）— 中继已恢复 / loop RUN_ID 6 重启【已解决·已归档】
### [归档·2026-10-20] 🚨 运维指令 · 2026-10-04（二）— 抢救 ops 中继【已解决·勿再执行·已归档】
### [归档·2026-10-20] 🆕 运维指令 · 2026-10-04：环境迁移 + 合并执行方式 + ops 中继独立【已落地·2026-10-18 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-18 02:57）。合并执行已落地（单任务书 + zhulong_loop.sh 运行中）；起始点已远过 init；ops 中继稳定；infra 端口已更新为 **8650/8651/8652/8654@10.129.32.75**（原 8664/8665/8653/8669 过时）。路径见 §6 + MEMORY 状态头。


<!-- archived from ZHULONG_TASK.md 2026-10-20 (consolidated closed 1-line pointers, batch 二十四~十四) -->

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-15（二十四）— 📊 收集 readback 轴 echo 数据强化论文论证【已完成·2026-10-15 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-15 17:35）。echo 数据表+语义注记+tab:readback-cost(表7) 已并入论文 6_exp.tex（commit zhulong S1-echo: @ 15:30·编译 0 error 12页）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-15（二十三）— 🔜 S1.readback_binary 后编排：B.glm-5.3-flash → B.deepseek-v4-flash【用户直令·已被二十七取代·2026-10-18 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-18 02:57）。被运维令二十七取代：fresh 5-run 已出（glm-5.3-flash 66.8±10.5% std 偏大 / deepseek-v4-flash 11.9±2.7% 但 73% 失败为 infra）→ 二十七对两臂启动复测（deepseek-v4-flash 复测 5/5✅=60.1±5.5% 已收口；glm-5.3-flash 复测 r1 两次作废·infra 阻塞·等运维决策）。fresh 值保留为历史对照。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-15（二十二）— 🔁 S1 重测调整：跳过 omega_low，改重测 readback_binary【已完成·2026-10-16 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-16 09:01）。readback_binary fresh 5/5=78.1±1.3% [75.9,79.1,77.8,78.5,79.1] 替换 legacy 66.2±16.1%（std 16.1→1.3·43.0%离群消除）；omega_low/readback_none 采信 legacy → S1 done_all。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-15（二十一）— 🧪 结合进展提「15 天窗口消融建议」· 中文 HTML· 用户直令 · 最高优先【已完成·2026-10-15 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-15 17:35）。报告 `reports/report_zhulong_next_ablation_plan_zh.html` 已交付（32927B·10节·3必做+2建议+2可选·15天排期表·commit c1a3d177 @ 17:01:57·已push）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-15（二十）— 📝 把最新评测结果填入 zhulong_results.md【已完成·2026-10-15 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-15）。phi_k1/phi_lagged/B.deepseek-v4-flash 已填入 zhulong_results.md（commit 见心跳 08:30）。后续新 5/5 收口臂（如 readback_binary）仍需照此口径填入。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-14（十九）— 🖨️ pdflatex 已装好，编译验证论文【已完成·2026-10-15 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-15）。编译验证✅ 11页 0 error（commit fb5e92f8）。改稿后重编译照此口径。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-14（十八）— 🧩 评测集全貌 + SKILL/Tcl 结果并入论文【已完成·2026-10-15 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-15）。SKILL/Tcl 已并入论文（commit b61970a8，12页）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-14（十七）— ✍️ 放行改进论文（执行审视报告修改）【P0-P3 已执行·2026-10-15 归档】
> ⏩ 已归档 → `ZHULONG_TASK_ARCHIVE.md`（P0-P3 已执行、论文已编译；锂点 82.1±3.0% 同步、前缀 `zhulong paper-fix:`、不偏造、未测留 `[TBD]`）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-14（十六）— 📝 实验空窗期审视论文，出改进意见 HTML（中文）【已完成·2026-10-14 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-14）。HTML 报告 `reports/report_zhulong_paper_review_zh.html` 已交付（运维令十七据此放行改稿）。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-13（十五）— ✅ 沙盒已重启完成，恢复试验（撤销 (十四) 暂停令）【已完成·2026-10-14 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-14）。沙盒已重启，phi_k3→phi_k1→phi_lagged 已依次推进，撤销 (十四) 暂停令生效。

### [归档·2026-10-20] 🆕 运维指令 · 2026-10-13（十四）— 🛑 立即暂停所有试验（沙盒重启中）【已被(十五)撤销·2026-10-13 归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。暂停令已被 (十五) 撤销，phi_k3 已恢复试验。


<!-- archived from ZHULONG_TASK.md 2026-10-20 06:3x (batch 5) -->

<!-- 三十 P1 排队：N′ 成本重测 + (B) 5-run 成本（已闭合：(B) 5-run 完成、(N′) 进行中） -->
### 🆕 运维指令 · 2026-10-18（三十）— 🧪 P1 排队：(N') 成本重测 + (B) 5-run 成本【不打断当前 ZL eval】

> 详见 `run/PLAN_RETEST_READBACK_COST.md` + `run/PAPER_RETEST_AUDIT.md`（本轮已提交）。
> **顺序**：① 当前 `ZL.glm-5.2` r1 跑完 → ② 先查 `output_evaluation/2026_1015_*` 的 trace，能提取 `(B)` 5-run 成本就零 GPU 先做 → ③ 再排 `(N')` 5-run（READBACK=none，~7.5h GPU，**必须保留 trace**）→ ④ 更新 `zhulong_results.md` / `6_exp.tex` / 重编译 PDF。
> **预注册**：不假设成本单调；若 `(N')` 成本低于 `(B)/(F)`，如实报告「无反馈→少搜索/早提交」，把成本结论限定在 `(B)→(F)`。
> 🚫 不打断 eval、不改 cline 3.0.51、不换主基座 `deepseek-v4-pro-fp4`、不删 trace、不插补。


<!-- archived 2026-10-20 06:4x: 十三 (75% 下限仅适用 full 锚点) -->
### 🆕 运维指令 · 2026-10-13（十三）— 🔴 紧急修正：75% 下限只适用于 `full` 锚点，消融臂不得用它作废成绩【最高优先 · 用户直令】

> **用户令（2026-10-13）**：「谁说 phi k3 一定要大于 75% 了，限制沙盒执行三次必然影响 Pass@1，72% 在正常范围。75% 是 full 的下限，不要混淆。」

**背景**：任务书 `(十二)`④ 和更早的 `(九)`④ 写了「判据 timeout ≤10 且 Pass@1 ≥75% ⇒ 该轮有效」。该判据**最初是针对 `full` 锚点写的**（目的是验证 infra 健康——如果 full 都跑不到 75%，说明沙盒/模型服务有问题，而非 agent 能力问题）。但 agent **错误地将它推广到了所有消融臂**（C2.phi_k10 / phi_k3 / phi_k1 / phi_lagged 以及 S1），导致消融臂的低分被误判为「无效」而重跑。

**🔴 立即生效的修正（逐字遵守）**：

1. **`Pass@1 ≥ 75%` 下限只适用于 `C1.full`（锚点）**。锚点跑不到 75% = infra 不健康（沙盒/模型/license/端口故障），该轮作废、重跑。
2. **消融臂（C2 的 phi_k10/k3/k1/lagged、S1 的 omega_low/readback_binary/readback_none、C1 的 pure_llm/rag/wo_retrieval/wo_selfexp）的判据 = 仅 `timeout ≤ 10` 且无 infra 故障**（license 耗尽 / 端口宕 / 磁盘 <8G）。**Pass@1 任何值都有效**——低分是消融效应的真实体现，不是 infra 问题。
3. ~~phi_k3 r1 att1 = 72.8% 历史处理~~（已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·phi_k3 已 5/5 收口）。
4. ~~phi_k10 5/5 重试历史~~（已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·phi_k10 已 5/5 收口=77.7±2.2%）。
5. **后续所有消融臂**：只要 `timeout ≤ 10` 且无 infra 故障（license_error / Connection_error / 端口 CLOSED 全 0 条），**一律记为有效，不重跑**。低分 = 真实消融效应。

**红线**：
- 🚫 不得以 `Pass@1 < 75%` 为由作废任何非 full 臂的成绩。
- 🚫 不得以 `Pass@1 < 75%` 为由重跑任何非 full 臂的任何轮次。
- ✅ 唯一的作废理由 = infra 故障（timeout > 10 / license_error / 端口宕 / 磁盘不足）或 auto-grade bug（PASS_RATE=1.3% 等明显异常值）。
- ✅ `ERROR_COUNT` 只计 infra 故障和 grade bug，**不计消融臂的正常低分**。


<!-- archived 2026-10-20 06:4x: 预留追加块 -->
### 🆕 运维指令（后续按需追加）

> （预留：运维批准模型消融、调整起始点、或追加 RQ3 SKILL/Tcl 切片时写在这里。）

---

## 1. 🎯 你是谁 · 任务总目标

你是推进 ZhuLong（DAC2027）EDA 消融评测的自动化 agent。每次被唤醒**只做一步**：

> 读 `MEMORY_ZHULONG.md` 恢复状态 → 读 `daily-memories/$(date +%F).md` 恢复上下文 → 判断下一步 → 执行 → 更新 `MEMORY_ZHULONG.md` 与当日流水 → 立刻退出。

不要 sleep/等待（外层循环负责间隔）。shell 命令直接调用工具，**不要调用任何 MCP 工具**。

**总目标**：把论文 6 张表里所有 `[TBD]` 换成实测 `mean ± std`（口径 README §4.1），共 **56 个 `[TBD]` / 30 行**。本任务书覆盖需要跑量的 4 个消融轴（见 §4）；`tab:selfdoc-cost`（离线自探索日志，1 次无重复）不在本循环内。

## 2. 🔒 冻结项（所有臂共用，不得变动）

- 数据集 `EDA-Eval-PyAether` **158 任务**；通过判据 = 生成代码在 sandbox 无错执行且全断言通过；`Pass@1 = 通过/158×100%`。
- 每配置 **5 次独立运行** → `mean ± std`；每次**重排任务顺序** + **全新 agent context**。
- 单任务单 trace、超时 **2500s**、`-p 8 -n`（8 并发 + 禁 Memory Bank 注入）。
- 主 backbone `deepseek-v4-pro-fp4`（**只有 STAGE=B 模型消融才换**）。
- **反作弊 PreToolUse hook 全程启用、所有臂完全一致（冻结变量，不是消融对象）**。
- `cimi_search` / `cimi_fetch` / `vqa` 永远关闭，不要碰。
- 检索默认 = name+description 索引向量检索（只有 S1 显式改变该索引保真度）。

## 3. ⛔ 红线（不得违反）

1. 不复活被否决表述；不自造符号/定律；不把「轮次」当 Φ 的操作轴。
2. 不改 `tab:llm-comparison` 结构（列/行口径已锁定）。
3. 不承诺开放任务用例（开源只覆盖 harness/schema/protocol，不含 benchmark 任务本体）。
4. 不填未测数字（未测留 `[TBD]` 或显式 provisional）。
5. `tab:omega` 口径：`(N)`=Pure LLM（核心 4 全关）；不采用 ICML 的 `(N)=0.0`。
6. 各 hook `errorMessage` 用唯一前缀区分（反作弊 vs `[PHI-BUDGET-EXHAUSTED]`）。
7. 反作弊内部数据不入论文正文（只定性，不带数字）。

## 4. 🗺️ 合并消融总计划（4 阶段 · 15 臂 · 75 轮 · 单循环串行）

执行顺序（**已调换**：因 pro-fp4 额度 403 阻塞 C1，现将 Phase B 提到最前）：**B → C1 → C2 → S1**。

| 阶段 STAGE | 流 | 臂（顺序）| 轮 | 回填表 |
|:--|:--|:--|:-:|:--|
| `B` 模型 | B | `glm-5.2` → `deepseek-v4-flash` → `kimi-k2.6-cloud` → `doubao-seed-2.0-pro-cloud` | 20 | `tab:llm-comparison`(4 行) |
| `C1` 组件 | C | `pure_llm` → `rag` → `wo_retrieval` → `full`(锚点) | 20 | `tab:main-ablation`(4 行) + 锚点行 |
| `C2` S2 Φ | C | `phi_k10` → `phi_k3` → `phi_k1` → `phi_lagged` | 20 | `tab:phi-bound`(k1/3/10/lagged) |
| `S1` 保真度 | A | `omega_low` → `readback_binary` → `readback_none` | 15 | `tab:omega`(L) · `tab:ablation-harness`(B,N) |

**锚点复用（跑一次、多处引用，禁止重复跑）**：
- `C1.full` ×5 = `tab:main-ablation`(full) + `tab:omega`(H) + `tab:ablation-harness`(F) + `tab:phi-bound`(unbounded) + `tab:llm-comparison`(DeepSeek-V4-Pro 主基座)。
- ∴ S1 的 (H)/(F)、C2 的 `phi_unbounded`、B 的主基座臂**全部跳过，不重跑**。

## 5. ⚙️ 统一状态机（字段写 `MEMORY_ZHULONG.md` 顶部）

| 字段 | 取值与含义 |
|:--|:--|
| `STAGE` | `S1` → `C1` → `C2` → `B`（顺序，交叉衔接）|
| `CONFIG` | 当前臂名（见 §4 表）|
| `ROUND` | 1..5 |
| `PHASE` | `init` / `running` / `just_finished` / `done_all` |
| `WAITING` | 0=无异步阻塞（下轮 ~1min 续跑）；1=一轮 eval 正在跑，或 infra 不就绪（下轮 ~30min）|
| `ERROR_COUNT` | 连续失败计数（≥3 强制推进）|

**臂轮转矩阵（PHASE=just_finished 时查下表切下一臂——已调换为 B→C1→C2→S1）**：

```
B:  glm-5.2 → deepseek-v4-flash → kimi-k2.6-cloud → doubao-seed-2.0-pro-cloud → C1.pure_llm
C1: pure_llm → rag → wo_retrieval → full → C2.phi_k10
C2: phi_k10 → phi_k3 → phi_k1 → phi_lagged → S1.omega_low
S1: omega_low → readback_binary → readback_none → done_all
```

> ⚠️ **Phase B→C1 衔接**：Phase B 使用 full 配置（不切 set_ablation），切到 C1.pure_llm 前**必须先执行** `scripts/set_ablation.py pure_llm` + `stop.sh && start.sh` 将 .env 切为 pure_llm 配置。
> ⚠️ **C1→C2 衔接**：切 C2 前执行 `scripts/set_s2_phi.py <ARM>` + `stop.sh && start.sh`。
> ⚠️ **C2→S1 衔接**：切 S1 前执行 `scripts/set_s1_fidelity.py <ARM>` + `stop.sh && start.sh`。

## 6. 🔧 固定命令（所有 `cd` 用 `BASE_DIR` 展开；`<TAG>`=CONFIG 名，`<N>`=轮次 1..5）

---

## 归档 batch 8 · 2026-10-21 07:3x（r4 家族 6 个已取代运维块·agent 自滚）

> 来源：ZHULONG_TASK.md OPERATOR NOTES 区·2026-10-21 07:33 归档（TASK 书 60KB>40KB 红线）。
> 6 个块均已被 21:4x 令取代或已闭合（r4 家族 r4/r4'/r4''/r4'''/r4⁗ 全 INVALID·BLOCKER 等运维决策）。
> 原文搬入，未改写。

### 🔴 运维指令 · 2026-10-20 21:2x（r4''' 疑似停滞…）— 已被 21:4x 令取代，保留备查

> 用户原话：「r4''' 到底是否健康呢，执行了多久」「都四个多小时了，你跟我说这算健康吗」「让 zhulong 去查」。
> **运维判读（推翻本线 20:38 的"健康"结论）**：r4''' 到 20:38 已 **256min**，而 **19:17 巡检时 worker 已是 task 118/119/122/124，20:38 仍在同一区间**；全程无 completions jsonl；总题量 158。日志仍在长（437 行/min）但**任务编号不推进** ⇒ 疑似空转/反复重试。
> **r4′ 前车之鉴**：同样"进程在、日志长"，实为卡在 task ~118/158，task 139-158 **从未启动** → 整轮 INVALID、产物不完整不可 regrade。r4''' 正处在**同一位置**。

**① 立即只读取证（RUN_ID 97 已由运维下发，中继会跑；你也可以先自己查）**
1. `ps -o pid,etimes,pcpu,stat -p 3112365` —— 真实 etime / CPU。
2. **task 进度（唯一有效判据）**：已完成 task 数、最新完成 task 编号、`*completions*.jsonl` / `*completed_code*.jsonl` 是否落盘。
3. log 尾部 20 行 —— 是否在**反复重试同一题**。
4. 最近 10 分钟 size/lines 两次采样 —— 区分"真进度"与"空转刷日志"。
5. MCP-32001 累计数。

**② 判定与动作**
- **已完成 ≥130 且仍在推进** → 继续跑，等收口。
- **卡在 task ~120 且 30min 无新 task 完成** → 判 **STALLED**：kill 3112365（仅本轮 batch `2026_1020_161451` 相关进程），本轮**作废不可 regrade**；MEMORY/日报写明这是与 r4′ 同型的**第二次停滞**，并给**根因假设 + 修正方案**（先回答：题 120-158 是否天然超长？单题是否无 timeout？`-p 4` 并行度是否够？长题是否需单独设上限？）——🚫 不要不分析就盲重跑。
- **已收口（pgrep 无进程）** → 立刻手动 regrade（模板 `/tmp/run_readback_none_retest_r4_regrade.sh` 改 batch `2026_1020_161451` + 端口 8663/8666/8667/8670 + `unset https_proxy http_proxy` + `NO_PROXY=10.129.32.75` + `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework`）→ 判有效（判据十三条）→ 起 r5'''。

**③ 口径纪律（纠正本线近 3 小时误判）**
🚫 **不得再以「PID 存活 + 日志行数增长 + MCP 率低 + fix 三项为 0」作为健康结论**——这些只证明 licence breaker 没复发，与"题集是否推进"无关。
✅ **健康唯一判据 = task 完成数单调增长**。报告中必须写「**已完成 N/158（较上次 +M）**」，不许只写"日志 437 行/min 健康增长"。

**④ 交付**：查证结论（158 题实际完成数 + 卡点 task 编号）先写 MEMORY + daily + commit（前缀 `zhulong S1:`），再按判定执行动作。

### 🔄 运维指令 · 2026-10-20 10:1x（**09:0x 令作废·继续按 08:2x 跑 r4″→r5″→5/5**）· 用户直令 · 最高优先【已被 15:4x 取代·历史】

> 用户令（10:1x）：「好的」——确认 09:0x 令（先 regrade r4′）作废，继续按 08:2x 执行。
> **背景澄清**：09:0x 令是我基于"r4′ 已自己收口"的误判下发的（ops RUN_ID 94 探针 09:03 看到 PID GONE）。实际是 agent 09:10 拉到 08:2x 令后**主动停了 r4′**（TERM 1462342）+ 清 16 孤儿 worker + 重启 8090 + 换端口 + 起 r4″。**r4′ 已按 08:2x 令标 INVALID(MCP 抬头 110→156)，不 regrade、不进 5-run**。r4″ 09:34 30min 健康报告 ✅ 全绿（real_MCP_32001=0，4 新端口全 OK，超时率 0/26994 ≪ 基线 0.001/行）。
> **本令唯一作用**：作废 09:0x，避免 agent 下轮唤醒时按 09:0x 去 regrade 已作废的 r4′ 造成混乱。

#### 执行路径（继续按 08:2x，不动作）
- **当前**：r4″ 跑中（PID 1760990·batch 新建·端口 8663/8666/8667/8670·fp4/READBACK=none/-p 4·09:09 起）。
- **r4″ 收口**（pgrep 无）→ 手动 regrade（照 `/tmp/run_readback_none_retest_r4_regrade.sh` 改 GEN_FILE=r4″ batch + 端口 8663/8666/8667/8670·unset proxy + NO_PROXY=10.129.32.75 + EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework）→ 判有效（判据十三：task timeout≤10·0 infra·0 exec_err）。
- **起 r5″**（同配置同端口 8663/8666/8667/8670·fp4/READBACK=none/OMEGA=high/BUDGET=0/LAGGED=0/V3自探索ON/-p 4/cline 3.0.51·`export PYTHON=$PWD/venv/bin/python`）。
- **5/5**（r1,r2,r3,r4″,r5″）mean±std → 更新 zhulong_results.md S1.readback_none 节 + 6_exp.tex tab:readback-cost (N′) 行 + tab:ablation-harness (N) Mean read-backs → 重编译 PDF。
- **full@pro-cloud 5 轮**（23:2x ②·MODEL=deepseek-v4-pro-cloud·KEY末8=8aa0785e·READBACK=full·canary 200 才开跑·cloud vs fp4 部署不同须显式注明不可混算）。

#### 纪律
- 🚫 不动 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED。
- 🚫 **不 regrade r4′**（已作废）；🚫 **不 regrade r4 旧轮**（已 INVALID 680 timeout）。
- commit：`zhulong S1: 09:0x 令作废(误判r4'自收口) -> 继续按 08:2x 跑 r4''→r5''→5/5`。

### 🔄 运维指令 · 2026-10-20 09:0x（**先 regrade r4′ 看成绩，再决定是否换端口**）· 用户直令 · 最高优先【已被 10:1x 取代·历史·作废·基于误判】

> 用户令（09:0x 决策）：r4′ 已自己收口，MCP timeout=156 低于基线 r2 的 235，**先 regrade r4′ 看 Pass@1，若有效则用 r4′，不急着换端口重跑**。
> **背景**：08:2x 令「停 r4′ → 换端口重跑」基于"r4′ 有很多沙盒超时"的判断。但 ops RUN_ID 94（09:03:29）实测：
> - r4′ PID 1462342 **已 GONE**（06:31 起跑，09:03 前收口，约 2.5h）—— agent 08:55 那轮 git pull 时机早于 08:50 push，**未拉到 08:2x 令**，r4′ 在旧端口 8666/8667/8669/8670 上自己跑完了。
> - r4′ 最终 **real_MCP_32001=156**（**低于**历史基线 r2 的 235）·run_code_calls=930（正常，r4 旧轮 928）·pass_rate_lines=0（**尚未评分**）。
> - 新端口 8663/8666/8667/8670 **全可达**（6-11ms）；旧端口 8669 也 OK（没坏，之前 BUSY 是 worker 轮换）。
> ⇒ **08:2x 令"停 r4′"动作无意义（r4′ 已不在跑），作废；改为先 regrade r4′ 看成绩再决定**。

#### ① 手动 regrade r4′（batch `2026_1020_063134`）
- 照 r4 regrade 模板 `/tmp/run_readback_none_retest_r4_regrade.sh`，**改 GEN_FILE=batch `2026_1020_063134`** + 端口 8666-8670 + `unset https_proxy http_proxy` + `NO_PROXY=10.129.32.75` + `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework`。
- regrade 前先 grep log 确认 r4′ 收口状态：`grep -ac 'pass ([0-9]' /tmp/ABL_readback_none_retest_r4b.log`（应为 0 或评分行）、`tail -5 /tmp/ABL_readback_none_retest_r4b.log`（看收口尾）。
- regrade 输出到独立目录，**不覆盖 r4′ 原始产物**。
- 记录：Pass@1（pass/158）、task timeout 数、exec_err、infra error、gen-success/fail。

#### ② 判据（判据十三 + 本令补充）
- **r4′ 有效** ⟺ Pass@1 ≥ **75%** 且 task timeout ≤ 10 且 0 infra 且 0 exec_err。
  - ⚠️ 注意：判据十三的 "timeout" 指**任务级 task timeout**（单次执行 2500s 超时），**非** MCP 60s 客户端超时。r4′ 的 156 次 MCP 60s-timeout 是客户端侧，**不计入** task timeout 判据（r1/r2/r3 也有类似量级 MCP timeout 但均判有效）。
- **r4′ 有效** → 用 r4′，**起 r5′**（同 r4′ 配置：fp4/READBACK=none/OMEGA=high/BUDGET=0/LAGGED=0/V3自探索ON/-p 4/**端口 8666/8667/8669/8670 即可，不必换端口**/cline 3.0.51·`export PYTHON=$PWD/venv/bin/python`）→ 5/5 mean±std（r1,r2,r3,r4′,r5′）→ 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮。
- **r4′ 无效**（Pass@1 <75% 或异常）→ 按 08:2x 令换端口 **8663/8666/8667/8670** 重跑 r4″（ops RUN_ID 94 已确认 4 端口全可达）。r4′ 标 INVALID 不用。

#### ③ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env`；🚫 不启 full@pro-cloud（等 5/5 干净后再做）。
- **本令优先级高于 08:2x**：若 r4′ 有效则**不必换端口重跑**（省 3-4h）；仅当 r4′ 无效才回退到 08:2x 换端口方案。
- commit：`zhulong S1: r4' 收口(MCP 156<基线235) -> 先 regrade 看成绩 -> 有效则用 r4' 起 r5' / 无效则换端口重跑`。

### 🔄 运维指令 · 2026-10-20 08:2x（**停 r4′ → 重启 8090 → 换端口 8663/8666/8667/8670 重跑 r4″**）· 用户直令 · 最高优先【已被 09:0x 取代·历史·仅 r4′ 无效时回退】

> 用户令（原文）：「**监测到 r4' 有很多沙盒超时。重启，使用下面4个端口：8663,8666,8667,8670**」
> **背景**：r4′（PID 1462342·batch `2026_1020_063134`）06:3x 起跑，巡检 #1（30min）real_MCP_32001=6 表观正常，但巡检 #2（65min）已升至 62、巡检 #3（100min）升至 110，**率 ~1.33/min 且持续抬头** ⇒ 沙盒后端再次进入降级轨迹（与 r4 旧轮 680 timeout 同型）。用户判定不可继续，令换端口重跑。
> **端口变更**：原 8666/8667/**8669**/8670 → 新 **8663**/8666/8667/8670（**替换 8669 → 8663**；8669 在历次巡检里多次显示 BUSY/worker 占用，疑似被邻居或自身 worker 拖累）。⚠️ **8663 此前在根 `MEMORY.md` §6 标记"作废"**，**本用户直令显式复活该端口**——按运维总则 2026-10-18「与最新用户令冲突时以最新块为准」，本次以本块为最新口径；agent 不必再核对旧"作废"标记。其余 3 端口（8666/8667/8670）不变。
> **本次唯一目标**：把 r4′ 干净停掉 → 重启 8090 wrapper（清累积降级）→ 用新 4 端口起 r4″，使 MCP 超时率回到历史基线（≈235/25 万行 量级，即 ≤ ~0.001/行）。

#### ① 先取证再停 r4′（**先留证再杀**）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
L=/tmp/ABL_readback_none_retest_r4b.log
echo "== r4' 停前取证 | $(date '+%F %T') =="
[ -f "$L" ] && {
  echo "  log_size=$(du -h "$L" | cut -f1)  lines=$(wc -l < "$L")"
  echo "  mention_timeout  = $(grep -ac 'timed out after 60s' "$L")"
  echo "  real_MCP_32001   = $(grep -ac 'MCP error -32001' "$L")"
  echo "  ACCESS_RESTRICTED= $(grep -ac 'ACCESS RESTRICTED' "$L")"
  echo "  run_code_calls   = $(grep -ac 'pyAether_MCP_server__run_code' "$L")"
  echo "  search_apis_calls= $(grep -ac 'pyAether_MCP_server__search_apis' "$L")"
  echo "  pass_rate_lines  = $(grep -ac 'pass ([0-9]' "$L")"
  echo "  32001 对应工具Top:"
  grep -a -B3 'MCP error -32001' "$L" | grep -aoE 'pyAether_MCP_server__[a-z_]+' | sort | uniq -c | head -6
}
echo "== r4' 进程清单（kill 前）=="
pgrep -af 'run_cline_script' | cut -c1-110
```
**停 r4′**：显式 PID 杀主进程 `1462342`，再扫孤儿 worker。⚠️ **教训（10-20 06:3x 已踩）**：`pgrep -f 'run_cline_script\.sh'` 会**误匹配 opencode 进程**（其 cmdline 含 ZHULONG_TASK.md 全文）→ **杀前必须核对 cmdline 是否真的是 `bash scripts/run_cline_script.sh ...`**，不可盲目 `pkill -f`。
```bash
# 只杀 cmdline 真正是 run_cline_script.sh 的进程（避开 opencode 误匹配）
for pid in $(pgrep -f 'run_cline_script\.sh'); do
  cmd=$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null | cut -c1-100)
  case "$cmd" in
    *bash\ scripts/run_cline_script.sh*|*run_cline_script.sh\ -p*)
      kill -TERM "$pid" && echo "TERM $pid :: $cmd" ;;
    *) echo "SKIP $pid (非 run_cline_script 主进程) :: $cmd" ;;
  esac
done
sleep 10
# 复检：剩余 run_cline_script 应只剩 opencode 误匹配（其 PPID 非 1 且 args 含 ZHULONG_TASK）
pgrep -af 'run_cline_script' | cut -c1-110 || echo "r4' 已停（无任何匹配）"
# 清孤儿 cline worker（batch 2026_1020_063134 的残留 task）
for pid in $(pgrep -f '2026_1020_063134'); do kill -TERM "$pid" 2>/dev/null && echo "orphan TERM $pid"; done
```

#### ② 记录 8090 状态 → 重启 → 验证（与 06:3x 块 ② 同型）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
echo "== 重启前 8090 =="
PID=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  pid=$PID etime=$(ps -o etimes= -p $PID 2>/dev/null|tr -d ' ')s nlwp=$(ps -o nlwp= -p $PID 2>/dev/null|tr -d ' ')"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"
echo "== 重启 =="
bash scripts/stop.sh; sleep 3
bash scripts/start.sh; sleep 8
NEW=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  新 PID=$NEW（旧 $PID）"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"
```

#### ③ 起跑前健康冒烟（**必须 5/5 通过才起 r4″**，否则停手报 blocker）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
OK=0; FAIL=0
for i in 1 2 3 4 5; do
  t0=$(date +%s%N)
  r=$(timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp \
      -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null | head -c 200)
  t1=$(date +%s%N); ms=$(( (t1-t0)/1000000 ))
  if [ -n "$r" ]; then OK=$((OK+1)); echo "  #$i OK ${ms}ms"; else FAIL=$((FAIL+1)); echo "  #$i FAIL ${ms}ms"; fi
done
echo "SMOKE: ok=$OK fail=$FAIL"
# 额外：用 run_code 打一次真实 pyAether 代码，确认沙盒端到端秒回
echo "run_code smoke:"
timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"pyAether_MCP_server__run_code","arguments":{"code":"print(1)"}}}' 2>/dev/null | head -c 300
echo ""
```

#### ④ 用新端口起 r4″（**端口 = 8663,8666,8667,8670**）
- **先标 r4′ INVALID**（与 r4 旧轮同处置）：把 batch `2026_1020_063134` 在台账标注 **`INVALID(MCP timeout 抬头, 巡检 #3=110 且率持续上行)`**，**不参与 5-run 统计**；🚫 不覆盖其原始产物与日志（留作诊断证据）。
- **r4″ 起跑**：配置与 r1–r3 **完全一致**，**唯一变更是端口** ——
  - `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / **V3 自探索 ON** / full harness / **`-p 4`** / 模型 **`deepseek-v4-pro-fp4`** / **端口 `8663,8666,8667,8670`** / `export PYTHON=$PWD/venv/bin/python`（**别再漏**）。
  - 日志 `/tmp/ABL_readback_none_retest_r4c.log`；batch 新建。
  - ⚠️ **端口参数传递方式**：照 06:3x 块 r4′ 的起法（`run_cline_script.sh -p 4` + 显式 PORTS 环境变量或脚本参数），**只替换端口列表**；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED。
- **r4″ 跑起来 30 分钟内必须报一次**：`real_MCP_32001` 计数 + `run_code` 调用数 + 4 个新端口各自的可达性（`curl -s -m 5 http://10.129.32.75:<port>/` 或等价探活），确认新超时率回到历史水平（≤ ~0.001/行）、4 端口全部可达。
- r4″ 收口 → 立即起 **r5″**（同配置同端口）→ 5/5 齐（r1,r2,r3,r4″,r5″）→ mean±std → 更新 `zhulong_results.md` / `6_exp.tex` → 接 full@pro-cloud 5 轮。

#### ⑤ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不启 full@pro-cloud（等 5/5 干净后再做）。
- kill 一律**显式 PID + cmdline 核对**（避开 opencode 误匹配）；长输出 `cut`。
- 若重启 + 换端口后冒烟仍大面积超时 → **停手报 blocker**（届时再查 9006/沙盒机本身/8663 是否真可用），不要盲目第三次重跑。
- commit：`zhulong S1: r4' MCP timeout 抬头(110+) -> 停 r4' -> 重启 8090 -> 换端口 8663/8666/8667/8670 起 r4''`。

### 🔄 运维指令 · 2026-10-20 06:3x（**停 r5 → 重启 8090 → 重跑 r4/r5**）· 用户直令 · 最高优先【已被 08:2x 取代·历史】

> 用户令（原文）：「**停 r5 → 重启 8090 → 重跑 r4、r5**」
> **依据（运维实测对照）**：
> - 历史：`ABL_full_r2_new.log` **MCP-32001=235 次**，PASS_RATE **73.4% 仍正常**；`r2_new2` 72 次。
> - r4：**MCP 超时 680 次** ⇒ 结果 **31.0%**，99 个 completion 退化成字面量 `"pass"`。
> ⇒ 存在「超时比例临界点」，r4 已越过；**r4 数据不可用，不能进 5-run 统计**。
> - 「680」是**提及次数**，须与「实际 `error: MCP error -32001` 报错次数」分开计（本轮第 ① 步会分开记录）。
> - 8090 是**无状态 wrapper**（`main.py` + 4 工具透传；重活在 9006 RAG 与 10.129.32.75 沙盒），**重启无副作用**，且是历史常规操作（每次切消融都 `stop.sh && start.sh`）。

#### ① 停 r5 并留证（**先取证再杀**）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
L4=/tmp/ABL_readback_none_retest_r4.log
L5=/tmp/ABL_readback_none_retest_r5.log
# 分开统计：提及 vs 真正报错
for f in "$L4" "$L5"; do [ -f "$f" ] || continue
  echo "== $f ($(du -h "$f"|cut -f1)) =="
  echo "  mention_timeout = $(grep -ac 'timed out after 60s' "$f")"
  echo "  real_MCP_32001  = $(grep -ac 'MCP error -32001' "$f")"
  echo "  ACCESS_RESTRICTED = $(grep -ac 'ACCESS RESTRICTED' "$f")"
  echo "  run_code_calls   = $(grep -ac 'pyAether_MCP_server__run_code' "$f")"
  echo "  search_apis_calls= $(grep -ac 'pyAether_MCP_server__search_apis' "$f")"
  echo "  get_details_calls= $(grep -ac 'pyAether_MCP_server__get_api_details' "$f")"
  echo "  32001 对应工具Top:"
  grep -a -B3 'MCP error -32001' "$f" | grep -aoE 'pyAether_MCP_server__[a-z_]+' | sort | uniq -c | head -6
done
# 停 r5（只杀 run_cline_script 主进程及其子进程，显式 PID）
pgrep -af 'run_cline_script' | cut -c1-100
for pid in $(pgrep -f 'run_cline_script\.sh'); do kill -TERM "$pid" 2>/dev/null && echo "TERM $pid"; done
sleep 10
pgrep -af 'run_cline_script' | cut -c1-100 || echo "r5 已停"
```

#### ② 记录 8090 状态 → 重启 → 验证
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
echo "== 重启前 8090 =="
PID=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  pid=$PID etime=$(ps -o etimes= -p $PID 2>/dev/null|tr -d ' ')s"
ps -o pid,nlwp,rss,pcpu,args -p "$PID" 2>/dev/null | cut -c1-120
echo "  fd_count=$(ls /proc/$PID/fd 2>/dev/null | wc -l)"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"

echo "== 重启 =="
bash scripts/stop.sh; sleep 3
bash scripts/start.sh; sleep 8
NEW=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  新 PID=$NEW（旧 $PID）"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"
echo "  tools=$(curl -s -m 8 http://localhost:8090/tools 2>/dev/null | head -c 300)"
```

#### ③ 起跑前健康冒烟（**必须 5/5 通过才起 r4**，否则停）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
OK=0; FAIL=0
for i in 1 2 3 4 5; do
  t0=$(date +%s%N)
  r=$(timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp \
      -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null | head -c 200)
  t1=$(date +%s%N); ms=$(( (t1-t0)/1000000 ))
  if [ -n "$r" ]; then OK=$((OK+1)); echo "  #$i OK ${ms}ms"; else FAIL=$((FAIL+1)); echo "  #$i FAIL ${ms}ms"; fi
done
echo "SMOKE: ok=$OK fail=$FAIL"
# 若 tools/list 端点不对，改用你已知可用的 MCP 调用方式；核心判据是「5 次全部 <5s 返回」
```

#### ④ 重跑 r4'（替换 r4），收口后接 r5'
- **先删/隔离 r4 旧结果**（🚫 不要覆盖原始产物）：把 `2026_1019_235040` 相关 completion 在台账中标注 **`INVALID(680 MCP timeout, 99 gen-fail)`**，**不参与 5-run 统计**。
- **r4' 起跑**：配置与 r1–r3 **完全一致** —— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3 自探索 ON / full harness / **`-p 4`** / 模型 **`deepseek-v4-pro-fp4`** / 端口 **8666,8667,8669,8670** / `export PYTHON=$PWD/venv/bin/python`（**这次别再漏**）。
- 日志 `/tmp/ABL_readback_none_retest_r4b.log`；batch 新建。
- **r4' 跑起来 30 分钟内必须报一次**：`real_MCP_32001` 计数 + `run_code` 调用数，确认新超时率是否回到历史水平（≈235/25万行 量级）。
- r4' 收口 → 立即起 **r5'**（同配置）→ 5/5 齐（r1,r2,r3,r4',r5'）→ mean±std → 更新 `zhulong_results.md` / `6_exp.tex`。

#### ⑤ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不启 full@pro-cloud（等 5/5 干净后再做）。
- kill 一律 **显式 PID**（🚫 `pkill -f` 带子串）；长输出 `cut`。
- 若重启后冒烟仍大面积超时 → **说明不是 8090 的问题，停手报 blocker**（届时再查 9006/沙盒）。
- commit：`zhulong S1: r4 INVALID(680 MCP timeouts) -> restart 8090 -> rerun r4/r5`。

### 🔬 运维指令 · 2026-10-20 06:0x（**P0：r4=31% 根因排查 —— 680 次 timeout 到底卡在哪个环节**）· 用户直令 · 最高优先

> 用户令（原文）：「zhulong r4 首先需要排查一下。你给我的只有现象，没有根因。比如 680 次 MCP timeout，到底是哪个环节超时？是 8090 的 MCP 服务呢，还是在 RAG 服务，还是在 run code .75 服务器的端口上。总归可以让 zhulong agent 调研一下啊。」
> **本次唯一目标**：把「680 次 `MCP request to pyAether_MCP_server timed out after 60s`」**拆成按调用点的归因表**，不允许只给现象。
> **本次不做**：不重跑 r4、不启 5-run、不改配置。**纯诊断**（可写脚本/可抓日志，但不动 `.env` 与运行中进程）。

#### 0. 已知事实（供你验证/推翻）
- r4 batch `2026_1019_235040`（23:50:40 起，~04:35 收口，约 5h），`-p 4`，端口 8666/8667/8669/8670，模型 fp4。
- gen-success **59** / gen-fail **99**（99 个 completion 是字面量 `"pass"`），exec_err 0。
- 已执行 59 题里 **49 通过（83%）** ⇒ 模型能力本身没问题，指向**调用链某一环降级**。
- eval log 计到 **680 次** `MCP request to pyAether_MCP_server timed out after 60s`。
- ⚠️ 该 60s 是 **MCP 客户端侧超时**，与会话无关，需定位它落在**哪个 server / 哪个工具 / 哪个端口**。

#### 1. 必须产出的「环节级归因表」（核心交付）

先把 log 里 680 次 timeout 的**原始行**抓出来，再按下列维度**逐条归类计数**（要求给出每类的数量 + 2–3 条样例行 + 行号/时间戳区间）：

| # | 环节 | 判定依据（从 timeout 行及其上下文提取） |
|:--|:--|:--|
| **A** | **8090 MCP server 本体**（进程在但无响应/被打满） | timeout 行前后是否有 `EDA_MCP_PORT=8090` 相关；同时查 8090 进程 CPU/线程/连接数随时间曲线 |
| **B** | **9006 RAG 服务**（检索服务超时，会导致 `search_apis`/`get_api_details` 卡住） | timeout 行是否伴随 `RAG`/`recall`/`search_apis`/`get_api_details` 字样；查 9006 进程状态 |
| **C** | **10.129.32.75 沙盒端口**（run_code 执行槽被占/慢） | timeout 行是否伴随 `run_code`/`/v1/run_code`/端口号 8666/8667/8669/8670；查是否出现 150s 级等待 |
| **D** | **本机 CPU/内存/负载**（`.29` 本身被压垮） | 用 r4 时段（23:50–04:35）的 `sar`/`vmstat`/`uptime` 或 dmesg OOM 记录佐证 |
| **E** | **外部争用**（t0002147 等同机邻居） | r4 时段是否有别的用户进程抢 CPU/端口；`/proc/pressure/*` 若有则贴 |

#### 2. 具体取证步骤（按序，全部只读）

**① log 原文挖掘**
```bash
L=/tmp/ABL_readback_none_retest_r4.log
# 1) timeout 总次数与时间分布（按 10 分钟分桶）
grep -a "timed out after 60s" "$L" | wc -l
grep -a "timed out after 60s" "$L" | grep -oE '^[0-9-]+ [0-9]{2}:[0-9]' | sort | uniq -c | tail -40
# 2) 每条 timeout 的上下文（前后 3 行），抽样 30 条
grep -a -n -B3 -A3 "timed out after 60s" "$L" | head -200 | cut -c1-180
# 3) 按工具名归类：timeout 行附近出现的工具名
grep -a "timed out after 60s" "$L" | grep -oE 'run_code|search_apis|search_apis_by_keyword|get_api_details|query_memory_bank|cimi_[a-z]+|probe_pyAether_code' | sort | uniq -c
# 4) 全 log 各工具的调用总数与失败数（做分母）
for t in run_code search_apis search_apis_by_keyword get_api_details; do
  printf "%-26s calls=%s\n" "$t" "$(grep -ac "$t" "$L")"
done
# 5) 是否有 150s / 连接错误 / RAG 字样
grep -acE '150 ?s|150s|Connection refused|ConnectionError|RAG|recall' "$L"
```

**② 三个候选环节的组件级健康（r4 时段是否降级）**
```bash
# 8090 MCP
ss -ltnp 2>/dev/null | grep -E ':8090|:9006' | cut -c1-140
PID8090=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "8090 pid=$PID8090"; ps -o pid,ppid,etimes,pcpu,pmem,nlwp,args -p "$PID8090" 2>/dev/null | cut -c1-160
# 9006 RAG
PID9006=$(ss -ltnp 2>/dev/null | grep ':9006' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "9006 pid=$PID9006"; ps -o pid,ppid,etimes,pcpu,pmem,nlwp,args -p "$PID9006" 2>/dev/null | cut -c1-160
# 关键：这两个进程的「启动时间」是否在 r4 时段内重启过（etimes < 现在-23:50）
date; echo "--- 若 etimes 小于距 23:50 的秒数 => r4 期间重启过 ---"
```

**③ 沙盒端口侧证据（区分「端口慢」与「MCP 侧慢」）**
```bash
# r4 时段端口是否有 150s 级等待（这正是 r3 被 t0002147 抢占的特征）
L=/tmp/ABL_readback_none_retest_r4.log
grep -acE 'run_code.*timed out|Request timeout \(150s\)|/v1/run_code' "$L"
grep -a -E 'Request timeout \(150s\)|8666|8667|8669|8670' "$L" | tail -10 | cut -c1-160
# 现在这 4 个端口是否仍健康（对照）
for p in 8666 8667 8669 8670; do
  ( out=$(timeout 10 curl -s --max-time 8 -X POST "http://10.129.32.75:$p/v1/run_code" -H 'Content-Type: application/json' -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null | head -c 12)
    [ -z "$out" ] && echo "$p BUSY" > /tmp/p20_$p || echo "$p OK" > /tmp/p20_$p ) &
done; wait
for p in 8666 8667 8669 8670; do echo "  $(cat /tmp/p20_$p 2>/dev/null)"; rm -f /tmp/p20_$p; done
```

**④ 系统层佐证（r4 那 5 小时 `.29` 是否被压垮）**
```bash
uptime; free -g | head -3
ps -eo pid,etimes,pcpu,pmem,user,args --sort=-pcpu 2>/dev/null | head -12 | cut -c1-150
dmesg -T 2>/dev/null | grep -iE 'oom|killed process' | tail -10 || echo "dmesg 不可读（正常）"
cat /proc/pressure/cpu /proc/pressure/io 2>/dev/null | cut -c1-120 || true
# 同期邻居占用
ps -eo user,etimes,pcpu,args 2>/dev/null | grep -E 't0002147|t0002997' | grep -v grep | head -6 | cut -c1-130
```

#### 3. 结论要求（**必须分档，不允许只写"MCP 超时"**）

产出下面这张表并给结论：
- 680 次中，**A/B/C/D/E 各占多少**（必须能加总到 680，或说明为何有未归类项）
- **主因是哪个环节** + 证据（贴 log 行号/时间戳 + 进程/端口状态）
- **是否存在「r4 时段某组件重启/降级」的时间吻合**（例如 8090 在 00:xx 重启，而 timeout 集中在那之后）
- **可复现性判断**：现在（诊断时）该环节是否已恢复？若已恢复 ⇒ 支持"瞬时降级"而非"配置错误"
- **对 r4 的处置建议**：**INVALID（infra 降级，应补跑 r4'）** / **有效（属模型方差，保留）** —— 给出你的依据，由运维拍板

#### 4. 纪律
- **纯只读**：不 kill、不重启 8090/9006/沙盒、不改 `.env`、不启任何 eval。
- 长输出 `cut -c1-180`；log grep 必须带 `-a`（二进制/长行），并用 `head`/`tail` 限流。
- 结果写 `MEMORY_ZHULONG.md` 心跳（≤6 行）+ `daily-memories/2026-10-20.md` 详细节，commit `zhulong diag: r4 680 MCP timeout attribution`。
- 🔴 **r5 继续跑，不要打扰**（PID 1296715）；本诊断与 r5 并行、互不影响。


## 归档 batch 9 · 2026-10-21 · 运维令 15:4x（licence fix → r4‴·已被 10:4x 取代·历史·未根治）

> 由 ZHULONG_TASK.md §运维指令区滚出（2026-10-21，r4e 跑中归档）。原文不改。

### 🔄 运维指令 · 2026-10-20 15:4x（**licence fix 已部署 → 验证 4 端口 → 重启 8090 → 重跑 r4‴**）· 用户直令 · 最高优先【已被 10:4x 取代·历史·未根治】

> 用户令（原文）：「**我刚提交了一个沙盒license泄露问题的fix并已部署到8663,8666,8667,8670四个端口。请重启r4，用这四个端口。重启之前先验证这四个端口健康。**」
> **背景**：14:12 BLOCKER 根因 = pyAether licence 断路器 OPEN（100+ 连续失败→深度 cooling-off，4 端口全 0 响应 ~2.5h）。三轮 r4/r4′/r4″ 共 680/156/575 次 MCP timeout → literal "pass" 退化（r4″ 79/158 gen-fail）。**用户已定位根因为 licence 泄露并部署 fix**。本令取代 08:2x 的"停手报 blocker"处置，恢复重跑。
> **端口**：8663/8666/8667/8670（与 08:2x 同，fix 已部署到这 4 个）。

#### ① 先验证 4 端口健康（**必须全过才重启 8090**）
- 用**真实 pyAether run_code 调用**（带 lang=pyAether, host=aether 或你已知正确参数格式）探 4 端口，每个至少 2 次，确认返回 `{"response":...}` 且**无** `licence unavailable` / `circuit breaker` / 空响应。
- 对照 14:56/15:33 的故障态（breaker open / 0 字节空响应），确认 fix 生效。
- **若任一端口仍返回 breaker/空响应 → 停手报运维**（fix 可能未完全生效），不重启 8090、不起 r4‴。
```bash
# 4 端口 run_code 健康探针（lang/host 参数照你已知正确格式）
for P in 8663 8666 8667 8670; do
  echo "=== port $P ==="
  for i in 1 2; do
    T0=$(date +%s%N)
    R=$(timeout 30 curl -s -m 25 -X POST "http://10.129.32.75:$P/v1/run_code" \
        -H 'Content-Type: application/json' \
        -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null | head -c 200)
    T1=$(date +%s%N); MS=$(( (T1-T0)/1000000 ))
    echo "  #$i ${MS}ms :: $(echo "$R" | cut -c1-150)"
  done
done
# 判据：4 端口 × 2 次 = 8 次全返回 {"response":... 且无 licence/breaker/空 → 健康通过
```

#### ② 重启 8090 wrapper（清累积状态，pick up fix 后的端口）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
echo "== 重启前 8090 =="
P8090=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  pid=$P8090 etime=$(ps -o etimes= -p $P8090 2>/dev/null|tr -d ' ')s"
echo "== 重启 =="
bash scripts/stop.sh; sleep 3
bash scripts/start.sh; sleep 8
PNEW=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  新 PID=$PNEW（旧 $P8090）"
echo "== 8090 MCP 冒烟 5/5 =="
OK=0; FAIL=0
for i in 1 2 3 4 5; do
  r=$(timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp \
      -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null | head -c 100)
  if [ -n "$r" ]; then OK=$((OK+1)); echo "  #$i OK"; else FAIL=$((FAIL+1)); echo "  #$i FAIL"; fi
done
echo "SMOKE: ok=$OK fail=$FAIL"
# 额外：8090 透传 run_code 端到端秒回
echo "run_code via 8090:"
timeout 30 curl -s -m 25 -X POST http://localhost:8090/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"pyAether_MCP_server__run_code","arguments":{"code":"print(1)","lang":"pyAether","host":"aether"}}}' 2>/dev/null | head -c 300
echo ""
```

#### ③ 起 r4‴（端口 8663/8666/8667/8670，配置同 r1–r3）
- **先标 r4/r4′/r4″ 全部 INVALID**（680/156/575 MCP timeout → literal "pass" 退化，均不进 5-run）：
  - r4 旧轮 `2026_1019_235040` INVALID(680 timeout, 99 literal-pass, 31.0%)
  - r4′ `2026_1020_063134` INVALID(110→156 timeout 抬头)
  - r4″ `2026_1020_090900` INVALID(575 timeout, 79 literal-pass, licence breaker)
  - 🚫 不覆盖原始产物与日志（留证）。
- **r4‴ 起跑**：配置与 r1–r3 完全一致 —— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / **V3 自探索 ON** / full harness / **`-p 4`** / 模型 **`deepseek-v4-pro-fp4`** / **端口 `8663,8666,8667,8670`** / `export PYTHON=$PWD/venv/bin/python`。
- 日志 `/tmp/ABL_readback_none_retest_r4d.log`；batch 新建。
- **r4‴ 跑起来 30 分钟内必须报一次**：`real_MCP_32001` 计数 + `run_code` 调用数 + 4 端口各自可达性 + **literal "pass" 计数**（grep completed jsonl 中字面量 `"pass"` 数量），确认 fix 生效（超时率 ≤ ~0.001/行 + literal-pass ≈ 0）。
- r4‴ 收口 → 立即起 **r5‴**（同配置同端口）→ 5/5 齐（r1,r2,r3,r4‴,r5‴）→ mean±std → 更新 `zhulong_results.md` / `6_exp.tex` → full@pro-cloud 5 轮。

#### ④ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′/r4″ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED。
- kill 一律显式 PID + cmdline 核对（避 opencode 误匹配）。
- **若 4 端口验证仍不健康（breaker/空响应）→ 停手报运维**，不重启 8090、不起 r4‴（fix 可能未完全生效）。
- **若 r4‴ 30min 内再现 MCP timeout 风暴（率 ≥5/min）或 literal-pass >10 → 停手报运维**（fix 可能未根治）。
- commit：`zhulong S1: licence fix 部署 → 验证 4 端口 → 重启 8090 → 重跑 r4''' (端口 8663/8666/8667/8670)`。


## 归档 batch 9 · 2026-10-21 · 运维令 21:4x（杀 r4/r5/regrade → 端口换 8650-8654 → 重启 r4⁗·r4⁗ 已收口 INVALID·已被 10:4x 取代）

> 由 ZHULONG_TASK.md §运维指令区滚出（2026-10-21，r4e 跑中归档）。r4⁗(r4d4)=batch 2026_1020_215918 已于 10-21 02:48 收口 INVALID(108 literal-pass)。原文不改。

### 🔴 运维指令 · 2026-10-20 21:4x（**用户直令：杀 r4/r5/regrade → 端口换 8650/8651/8652/8654 → 重启 r4**）· 最高优先

> 用户原话：「杀掉 r4/r5，regrade 也杀掉，端口换到 8650,8651,8652,8654，重启 r4」。
> **现状**：r4''' 21:09 已收口但判 INVALID（70/158 字面量 "pass" + breaker OPEN 98 consecutive worker spawn failures@8667）；4 旧端口 8663/8666/8667/8670 全不可达。r4/r4'/r4''/r4''' 全 INVALID ⇒ **本轮 r4 是第 5 次尝试**，编号用 **r4⁗（r4-4）**，batch 自动生成。

**① 执行顺序（运维已下发 RUN_ID 99 做①②，你负责③④⑤）**
1. **杀残留**：`pkill -f 'run_readback_none_retest_r4d3_regrade'`、`pkill -f 'run_pipeline.py.*evaluation'`、`pkill -f 'run_cline_script.*readback_none'`。⚠️ **不碰** t0002147、loop、ops_relay。
2. **端口切换**：`SANDBOX_ENDPOINTS=8650,8651,8652,8654@10.129.32.75`。
   - 🔴 **必须先在 `.env` 或启动脚本中确认这四个端口归本线所有**（历史上 8650/8651/8652/8654 被 **t0002147** 占用，r3 regrade 曾因抢占全 timeout）。若被 t0002147 占用 → **不要抢，报 blocker**。
   - 4 端口逐个 `timeout 5 bash -c "</dev/tcp/10.129.32.75/$p"` 必须 **4/4 OPEN** 才起跑。
3. **起 r4⁗**（与 r4''' 同配置同模型同 readback=none，仅换端口）：
   ```bash
   cd /nasdata/app.e0031982/code/ZhuLong_DAC2027
   export PYTHON=$PWD/venv/bin/python        # 🔴 必须，漏了必崩 pydantic ModuleNotFoundError
   export SANDBOX_ENDPOINTS=8650,8651,8652,8654@10.129.32.75
   unset http_proxy https_proxy ALL_PROXY
   export NO_PROXY=10.129.32.75,localhost,127.0.0.1
   setsid bash scripts/run_cline_script.sh -p 4 -n > /tmp/ABL_readback_none_retest_r4d4.log 2>&1 < /dev/null &
   ```
   起跑后 5 分钟内核验：`pgrep -af run_cline_script` 有 1 launcher + 4 worker、log 在增长、首题已开始。
4. **启动后立刻回报**：PID / batch 号 / 4 端口状态 / 首 5 分钟 log 行数。
5. **监控口径（强制，纠正此前误判）**：
   - ✅ **健康判据 = task 完成数单调增长**（从 **codegen jsonl 行数**数，不是 log 行数）。
   - ✅ **每轮巡检必须 grep codegen jsonl 里字面量 `"pass"` 数量**——这是退化的唯一早期信号（20:30 前四轮巡检都只 grep log，错过 70 条退化的早期发现）。
   - 停手阈值不变：literal-pass >10 或 MCP 率 ≥5/min → 停手报运维。

**② 若有任何一个前置不满足（端口被占 / 端口不可达 / 启动即崩）→ 立刻报 blocker，不要盲重试。**

