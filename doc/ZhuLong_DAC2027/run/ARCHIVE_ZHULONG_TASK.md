

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
