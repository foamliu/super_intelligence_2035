# BAIZE_POSTTRAIN_TASK.md

> 🔴 **用户令 · 2026-11-16 20:5x（取消全局排队 · 改用 8650–8670 端口池并行 · 最高优先）· 未完成**
>
> **用户原话**：「为啥要排队，扫一下 8650-8670 之间的沙盒端口，都可以用。」
> ⇒ **run5 不再等「36.15 无 run_cline_script.sh」**。用户已判定该端口段全部可用；本线改为**按端口分配**，与 zhulong eval 分口并行。
>
> **立即动作（按序；做完即起跑，不要再空等）**
> 1. **放宽 gate（只对本次 run5 生效，不改历史语义）**：允许修改本线链脚本，加 `GATE_MODE=ports`（默认仍为旧 `global` 行为）：`gate_wait` 在 `ports` 模式下判据 =「存在 ≥4 个本线可用沙盒口」，不再看 36.15 有没有 `run_cline_script.sh`。🚫 仍然不改 `eda_fastmcp` 源码、🚫 不重启 8090 MCP、🚫 不 kill 任何他线进程。
> 2. **只读扫描（在 36.15 上，经 `ssh -p 3333 app.e0031982@localhost`）**，把结果贴进 daily：
>    ```bash
>    ss -ltn  | grep -E ':86(5|6|7)[0-9]'          # 哪些口在 LISTEN
>    ss -tnp  | grep -E ':86(5|6|7)[0-9]'          # 已被谁 ESTABLISHED（含他线）
>    ss -ltnp | grep 8090                          # MCP 实例/PID
>    grep -nE 'PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|SANDBOX_PORT' <eda_fastmcp>/.env   # 只读
>    ```
> 3. **判「本线可用」**＝该口 LISTEN **且** 无他人 `ESTABLISHED` **且** 不在 zhulong 当前 eval 的占用集合内；同时记下每口绑定的 **workdir**（映射以 `.env` 实际行为准，**禁止臆造**）。
> 4. **关键分叉（先判后动）**：确认 `SANDBOX_ENDPOINTS` / `PROXY_PORTS` 是否可由**客户端**（`run_cline_script.sh` 的 env / MCP 配置块）按 run 指定 —
>    - **能指定** ⇒ 直接用扫出的可用口起跑：`SANDBOX_ENDPOINTS='<port:workdir,...>' PROXY_PORTS='<port,...>' bash scripts/run_cline_script.sh -p N -n -b <bench>`，`N` = 可用口数（≥4 即起，≥8 更佳；不足 4 才报运维）；
>    - **只能在服务端 `.env` 生效** ⇒ **停手，立即报运维**（贴 `PROXY_PORTS=` 现状行 + 8090 PID + zhulong eval 占用端口证据），**不得**改 `.env`、**不得**重启 8090（会打断他线 eval）。
> 5. **必须先冒烟再全量**：用 1–2 题走通 `run_code` → 确认 `execution_results` 有行 → 再放 158 全量；冒烟不通按第 4 条报运维。
> 6. **写 env fingerprint**（新增 `attribution_3615_run5/env_fingerprint.json`）：实际端口集合、各口 workdir、`SANDBOX_HOST`、`.env` 相关行（原样）、起跑命令、`GATE_MODE`。原因：**换 workdir＝换 EDA 环境状态（lib.defs/TECHLIB）**，这是相对 run1–4 的新混杂变量，报告里必须显式标注。
> 7. **纪律不变**：🚫 不启动 `baize_posttrain_clean_5run.sh`；🚫 不改 run1–4 产物；🚫 不 kill 他线；🚫 不得用 n<5 冒充 5-run（若最终只跑成 n=4，如实标 `n=4 recovered`）。
> 8. **交付**：起跑后**立刻 push**（不等跑完），commit 前缀 `posttrain 5run:`；daily 里留上面扫描命令的原始输出。

> 🔴 **用户令 · 2026-11-16 18:3x（恢复「干净 5-run」· 已授权 · 最高优先）· 未完成**
>
> **用户原话**：「post-train 恢复「干净 5-run」」——即 23:0x item5「8 题验证通过后再决定是否恢复 5-run」的**恢复授权已下**。
>
> **前置（运维已核，本线不必重查，只需 `bash -n` 复验一次）**：RCA 六项已交付（`reports/report_posttrain_collapse_rca_zh.html`，主因=抽取器 ws/no-ws 路径失配，非模型 collapse）；回补干净版已落盘 **run1=18.99%(ws-only 锚点) / run2=4.43%(43 行) / run3=2.53%(28 行) / run4=3.80%(35 行)**；**run5 缺失**；修好的链脚本 `run/baize_posttrain_zhulong_baseline_5run_chain.sh` 已接入 `rca_recover_extract.py` 回补 + `run_eval.py -g` 干净重评测 + batch↔eval 精确归属。
>
> **唯一允许的起跑方式（只此一条，其他一律禁止）**
> ```bash
> RUN_DIR=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
> [ -d "$RUN_DIR" ] || RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
> cd "$RUN_DIR" || exit 1
> bash -n baize_posttrain_zhulong_baseline_5run_chain.sh || exit 1
> grep -q rca_recover_extract baize_posttrain_zhulong_baseline_5run_chain.sh || exit 1
> setsid env NUM_NEW_RUNS=4 R2_CHAIN_PID= bash baize_posttrain_zhulong_baseline_5run_chain.sh \
>   > /tmp/posttrain_zhulong_baseline_5run_chain.log 2>&1 < /dev/null &
> ```
> - `NUM_NEW_RUNS=4`：链会幂等跳过已有有效 `final_report.json` 的 run1-4，**只实跑 run5**；
> - `R2_CHAIN_PID=` 置空：R2 链（原 PID 2322797）早已结束，置空避免 PID 复用误判 gate 永不放行；
> - 起跑后**立刻 push**（用户令「跑起来后正常 push 别等全跑完」），之后每唤醒只做监控心跳。
>
> **禁止事项（违者按 23:0x 纪律纠偏处理）**
> 1. 🚫 不得启动 `baize_posttrain_clean_5run.sh`（它会把 run1-4 成品 `mv` 走重跑，破坏封存；该脚本继续留在磁盘作证据，**不删也不用**）。
> 2. 🚫 不得改动 / 删除 / 覆盖 `attribution_3615_run1..run4` 任何既有产物（原坍塌版 `final_report_collapsed.jsonl` 亦保留）。
> 3. 🚫 不得改 `eda_fastmcp` 源码；不得 kill 他线进程（vision / zhulong / pretrain）；gate 只在 36.15 无 `run_cline_script.sh` 时放行，**若被 zhulong eval 连续占用 >6h，报运维，不抢**。
> 4. 🚫 不得用 n=4 冒充 5-run；run5 未落盘前**不得引用任何 5-run mean**。
>
> **验收（run5 完成后一次做完）**
> 1. `attribution_3615_run5/final_report.json` 存在且 `execution_results.jsonl` 行数 ≫1（若只有 1 行 = 回补/评测仍坏，标 `INVALID-partial` 并报运维）；
> 2. `bash run/bpt_zhulong_5run_finalize.sh --num-runs 5` → `run/5run_zhulong_baseline_analysis.json`（n=5 mean±std + 配对检验 vs 旧 .17 3.04%±0.83%），并把 `rca_status` 由 `INVALID` 改为 `CLEAN`；
> 3. 报告 `reports/report_posttrain_zhulong_reattribution_zh.html` §10 改为 5-run 同表，**必须带口径 caveat**：run1=ws-only 锚点（batch 2026_1114_180019 已清理不可回补）、run2-5=recovered 口径（ws+no-ws 回补）；并单列一句「run1 18.99% vs run2-4 2.5-4.4% 的落差待 fresh 5-run 定论」；
> 4. `MEMORY_POSTTRAIN.md` 顶部一行结论 + daily 2026-11-16 + commit 前缀 `posttrain 5run:`。

> 🔴 **用户令 · 2026-11-15 23:0x（停止盲跑 · 先查 trace/管线 · 最高优先）· 未完成**
>
> **用户原话**：「post-train：run2/3/4：各只有 1 个有效生成 → 0.0%，都这样了还继续跑呢？不会看一眼trace排查一下吗？」
>
> **立即动作（本轮第一件事，做完再谈别的）**
> 1. **停链**：`kill` 5-run 链 `PID43678` 及当前 run5 的 `run_cline_script` / `run_cli.sh` 子树；**不要再起任何新 run**。run5 若未完成，标 `INVALID-partial`；若 5-run 汇总已自动生成，也标 `INVALID` 并**不得用于任何结论**。产物一律保留，不删。
> 2. **封存现场**：run1–run4 的 `final_report.json` / `execution_results.jsonl` / `completed_code_generation.jsonl` / `codegen_rejection_stats.json`，以及 36.15 对应 batch 的 `output_evaluation/<ts>/`、`eda_code_eval/<batch>/`、`code/EDA-Eval-PyAether-*/`、cline session 日志；记录路径 + mtime + 大小（小文件 sha256）。
> 3. **必须解释的 4 个异常（先复现，再下结论；每条给证据）**：
>    - **A**：run2/3/4 的 `completed_code_generation.jsonl` 都是 **158 行**，但 `execution_results.jsonl` **只有 1 行**（run1 是 36 行）。`run_eval` 的「有效生成」判定在哪一行？依据哪个文件 / glob / 字段？把代码贴出来。
>    - **B**：run2 的 `completed_code_generation.jsonl` 里只有 1 行 `completion` 是代码（task 003），run3 是 1 行（task 107），run1 是 0 行（全 `pass`）——这个文件到底谁写的？`completion` / `status` 字段语义是什么？它和 `run_eval` 读的文件是不是同一个？
>    - **C**：唯一被执行的任务 run2=`003`、run3=`107`、run4=`107`；把它们的 cline session trace 与 20 个 failed task 对比（首尾各 20 条消息、最后 5 次 tool call、是否写文件、`submit.zip` / zip 结构、文件命名/路径）。
>    - **D**：run2/3/4 的 `codegen_rejection_stats.json` 是 **0 字节**（run1 是 1573 B）；这是否意味着 codegen 阶段根本没产出 code / rejection 统计没跑？
> 4. **优先怀疑管线而不是模型**：连续 3 次「恰好 1 条 execution_result」高度可疑；先查 `run_eval` / copy / glob / zip 解包 / 大小写 / 时间戳目录的路径 bug（此前已有 copy-path bug 前科）。**在排除管线 bug 之前，禁止**把 run2/3/4 写成「模型 degenerate collapse」。
> 5. **最小验证**：找到根因后，用 **8 题子集**重跑 `run_eval`，必须能读出 **>=8 条** `execution_results`（若仍只有 1 条即未修好）；通过后再决定是否恢复 5-run。
> 6. **交付**：`reports/report_posttrain_collapse_rca_zh.html`（中文 / 单文件 / 0 外链 / 0 script）：首屏一句话结论 + run1–4 对照表（completed 行数 / execution 行数 / gen_success / 唯一成功 task）+ trace 证据（文件:行）+ 根因（管线 vs 模型）+ 修复 diff + 8 题验证结果；`MEMORY_POSTTRAIN.md` 顶部一行 + daily + commit 前缀 `posttrain rca:`。
>
> **纪律**：RCA 出结论前，**不得**再报 5-run mean、不得起新 run、不得删任何 trace/产物、不得 kill 他线（vision / zhulong / pretrain）进程。若结论是模型行为而非管线 bug，也必须给出可操作缓解（强制写文件 / 工具校验 / 重试）并先用 8 题验证，再恢复 5-run。


> 🔴 **用户令 · 2026-11-15 08:1x — 158 题评测必须改用 zhulong 的方式（36.15 `eda_fastmcp`）· 最高优先 · 未完成**

> **用户原话**：「我明白了：post-train 由于早先不是做评测的，对评测的理解远不如 zhulong。由于泄题问题，我们在36.15的评测中，用PreToolUse hook的方式，对评测过程中agent能用的工具进行了白名单限制。只能用三个知识库工具+run_code，本机 run_commands 已经被禁。请它看看36.15 中 eda_fastmcp 这个项目，这个项目有zhulong启动评测的脚本。让post-train使用zhulong相同的方式进行158评测。」

**一、先说清楚：你的归因结论已经站不住了**

你昨夜的核心结论是「损失大头不在会不会写，而在**会不会按 MCP 协议调工具/提交**」——**这个结论的前提是错的**。

| 你报告里的数 | 事实 | 后果 |
|:--|:--|:--|
| 1304 次拒绝，其中 `run_commands` **1051 次 = 80.6%** | 36.15 的 PreToolUse hook **本来就禁掉了 `run_commands`**（白名单只放 3 个知识库工具 + `run_code`） | 这 1051 次「拒绝」**是评测环境的设计行为，不是模型能力缺陷**。你把「撞墙」算成了「不会调工具」 |
| 「模型不会按 MCP 协议调工具」 | `run_commands` 是 **cline 内置工具**，根本不是 MCP 工具；且它被 hook 屏蔽，模型**无论怎么调都会被拒** | 真正的 MCP 工具（`search_apis`/`get_api_details`/`search_apis_by_keyword`/`run_code`）的真实拒绝率**从未被独立统计** |
| 121 个 gen-fail 里 76 个「拒绝致死」 | 其中大部分是反复尝试被禁的 `run_commands` 直到耗尽 turn | P0 补丁「+20pp / +13.4pp」的 ROI 预估**建立在错误归因上，暂不可信** |

⇒ **在换成 zhulong 口径重测之前，不要再用「MCP 协议格式」的说法写结论，报告相应小节要标 `PENDING-REMOTEST`（待重测）。**

**二、你要做的事：照 zhulong 的方式跑 158 题**

1. **读代码（只读，不改）**：`/nasdata/app.e0031982/code/eda_fastmcp`（36.15 上，即 `BASE_DIR`）。重点看：
   - `scripts/cline_hooks/PreToolUse` — **反作弊白名单**，搞清楚放行哪些工具、拒绝时的返回格式
   - `scripts/run_cline_script.sh` — zhulong 的启动入口（`EDA_PROMPT_TEMPLATE` / `EDA_PROMPT_TEMPLATE_PYAETHER` 怎么生效）
   - `scripts/format_eval_task.py` — 题面构造
   - `scripts/set_ablation.py` — 臂的配置切换
   - 判分脚本（`check()` / eval 入口）与 `-p` 并发、`-k` 重试等默认参数
2. **照抄它的调用方式**跑 **EDA-Eval-PyAether-158**：
   - 同一套 **PreToolUse 白名单**（3 个知识库工具 + `run_code`；`run_commands` 保持禁用——**这是防泄题必需，不要在评测里打开**）
   - 同一套 prompt 模板路径与题面构造
   - 同一套判分口径与并发/超时参数
   - **记录 cline 版本**（`cline --version`）——你的 MEMORY 里现在**一条版本记录都没有**，这是硬缺口
3. **产出新的 158 题基线**，并与旧基线**同表并列**（旧基线标「口径非 zhulong 方式 · 含被禁工具」，新基线标「zhulong 口径」）。**不要求新旧相等，但必须解释差异来源。**

**三、重测后必须回答的问题（这才是真归因）**

1. **真 MCP 工具的拒绝率**是多少？（只统计 `search_apis` / `get_api_details` / `search_apis_by_keyword` / `run_code`，**不含 `run_commands`**）——按工具分列拒绝次数与原因。
2. **`run_code` 的拒绝率**（这是白名单里唯一能执行代码的通道，也是真实执行能力的唯一出口）。
3. **「静默未生成」45 题**在 zhulong 口径下还剩多少？它们零拒绝、从不调工具——这部分**不是格式问题，是模型根本没进入 agent 回路**。
4. 新旧基线的 **Pass@1 差异**及差异来源分解（工具面变化 / prompt 变化 / 并发参数变化）。

**四、纪律**
- 🚫 **不要在 36.15 评测里打开 `run_commands`**（泄题风险）——这是用户明确保留的反作弊设计。
- 🚫 **不要改 `eda_fastmcp` 的任何代码**；要复用就复用它的入口，缺什么先问，别自己另造一套评测。
- ✅ 旧报告与旧数字**全部保留**，但要在报告顶部加一行：「**口径失配 · 工具面含被 PreToolUse 禁用的 `run_commands` · 佐证结论 PENDING-REMOTEST**」。
- ✅ 重测跑起来后正常 push，别等全跑完才交。


> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不猜不编、infra≠能力、失败分类由你自己提炼）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主决定 SFT/RL 技术路线、超参与实验设计；结果说话。**

> 🔴 **用户令 · 2026-11-14 23:4x — 隧道怎么坏的？自己查清楚并出报告（最高优先，压过今夜其余动作）**
>
> **用户原话**：「原来隧道好的，现在坏了么？怎么坏的？什么情况？让它自己报告」。
>
> **完整规格 → `run/INFRA_TUNNEL_POSTMORTEM_SPEC.md`（先读再做）**。要点：
> 1. 中继在 **Windows `172.19.195.133`（`tunnel.ps1`）**；运维这台 Win11 **不是**中继，只能由你从 `.17` 侧取证。
> 2. 已知：**20:0x–22:0x 通**（36.15 run1 完整跑出 18.99%）；**22:4x 首次确认断**（`.17` 3333 未监听、直连 `36.15:22` 被防火墙阻）。**中间发生了什么，就是你要查的时间线。**
> 3. 必须回答六问：最后通点 / 首断点 / 时间线 / 故障域（中继机离线·ps1 死·SSH 认证·36.15 拒连·本侧端口） / 是否我们造成 / 修复路径 + 三条验证命令。
> 4. 交付 `reports/report_infra_tunnel_postmortem_zh.html`（首屏三句话：坏没坏 / 怎么坏 / 谁修）+ MEMORY 一行结论。
> 5. 🚫 不猜不编；查不到写「无记录」。**隧道恢复后**立即接回 `POSTTRAIN_PLAN_NEXT.md` 的 A1/A3 与 P0 dev 对比。

> 🟠 **用户令 · 2026-11-14 21:5x — 今晚自己出计划并直接执行，不等批复（明早看结果）**
>
> **用户原话**：「基于这份结果，下一步可以请 post-train 出一份计划，然后按此办理。现在夜了，让 post-train 出计划后直接执行，不用等运维批复，明早我看结果即可。」
>
> **要做的事**：填 `run/POSTTRAIN_PLAN_NEXT.md`（计划 + 时间表 + 判据 + 预算 + 回滚）→ **立刻按计划执行，无需运维批复**。
> **起点数字已订正**：36.15 run1 完整 = **18.99%（30/158）**；生成成功 36 / 生成失败 121 → **生成后通过率 83.3%**；头号失败 **T6_tool_format 占 76.6%**；全局被拒 **1304** 次（`run_commands` 1048 / `missing-field` 527 / `string-not-array` 321）。
> **因此今夜 ROI 排序**：① T6 工具格式/提交协议（最大损失项）② P1/P2/P3 补丁 ③ 口径统一（A1/A3 两臂优先）。
> **明早 09:00 及格线**：A1 与 A3 两臂 40 题结果 + T6 归因表 + 至少一条补丁的 dev 前后对比 + 中文 HTML 报告 + EXPERIMENTS 新节。
> 🚫 不许只写「进行中」；没跑完就写卡在哪、谁在卡、ETA。

## 🎯 本线使命（常驻 · 2026-11-14 用户订正 · **每轮开始先读这一块**）

**一句话**：把 2B 基模在 EDA 脚本任务上的通过率，用 SFT/RL 做**显著提升**。

**唯一主线（四步）**：
1. **基模 = `minicpm5-2b`**（MiniCPM5-2B；2026-11-12 用户令已解除对 BaiZe 预训练模型的依赖）。
2. **测基线**：`EDA-Eval-PyAether` **158 题**（写 PyAether 脚本的能力），5-run Pass@1。
3. **领域适配**：**SFT**（agentic 轨迹）→ **RL**（可验证奖励 GRPO），一步一拍，每步单独测。
4. **交付判据**：**同测法下**，post-SFT / post-RL 的通过率相对基线**显著提升**（预注册判据 + 配对检验），并出中文 HTML 报告。

**不是主业（做了也不算产出）**：造题 / 写 `check.py`（designflow 的活）· 评测框架开发 · 环境排障 · 监控心跳 · 报告美化。这些是**必要手段**，只有当它直接服务于「拿到可信的提升数字」时才值得花轮次。

**每轮自检三问**：
① 本轮是否让「基线 → SFT → RL」这条链更清楚、或更接近交付？
② 我报的数字是否**同测法、可复现、有配对检验**？跨测法的差值一律标「不可比」。
③ 若本轮只做了监控/报告，那「未完成指令」是什么、ETA 多少？

---

> 🔴 **用户直令 · 2026-11-14 19:2x — 「3.04% → 15.82%」≈5× 跳升归因 + prompt 迭代（最高优先，压过例行巡检）**
>
> **用户原话**：「请 posttrain 分析一下这 ≈5 倍跳升从何而来……如果系统 PROMPT 差异这么大，那么看看 trace，是否还能继续优化系统 PROMPT 来提分？」
>
> **完整规格 → `run/POSTTRAIN_ENV_ATTRIBUTION_SPEC.md`（含 4 变量前提纠正 / A0–A3 单变量消融 / P1–P3 最小补丁 / train-dev 79:79 / 预注册判据），本令只强调三件事**：
> 1. 目的 = **钉死评测口径**，让「基线 → SFT → RL」三段可比；跨测法的差值一律标「不可比」。
> 2. **不许**把 5× 归给 prompt —— 同时变了「系统提示 / RAG 后端 / 沙盒可达性 / 网络延迟」四件事。
> 3. 🚫 不改 benchmark / check.py / 题面、不挑题、不引用未跑完的 run；commit 前缀 `posttrain attribution:`。
> 4. ⚠️ 本任务书已超 40KB 硬上限 ⇒ 下轮**先**归档已闭合块；**本使命块与本令不得被归档**。

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）（本线现有：`reports/report_posttrain_research_zh.html`）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 📦 2026-11-14 已闭合两条令（16:3x RCA 重写 / 16:1x 看 trace 判定工具调用）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`
> **结论**：v2 RCA 报告已交付并独立复验 PASS（`reports/report_posttrain_pyaether_rca_v2_zh.html`）；工具调用画像已入报告核心章（MCP 6051 / submit_and_exit 13,699 次 91.77% 报错 / degenerate pass 479-790=60.63% / 仅 9.88% 题进入「检索→执行→修错」）。
> **仍有效**：15:4x「在 36.15 启动评测」与 09:0x「先分析基线」两条仍在办（5-run RUNNING），正文保留。需要时再读

### 🔴 用户令 · 2026-11-14 15:4x（**PyAether 评测必须在 36.15 上启动，不是 .17** —— 你的 3.04% 基线口径存疑）· 未完成 · 最高优先

> **用户原话**：「通过阅读报告 `report_posttrain_baseline_pyaether_rca_zh.html` 我发现了问题：
> EDA-Eval-PyAether-v20260311_fixed.jsonl 评测 cline agent 是在 .17 服务器（跟 post-train 相同）启动的吧，这样不对。
> 需要跟 zhulong agent 一样，从 36.15 服务器启动。因为只有 36.15 服务器才：1）部署了 API 文档知识库（RAG）服务；
> 2）部署了可以访问沙盒（EDA 环境）的 MCP。所以需要跟 zhulong agent 协调：
> 1）先 serve minicpm5-2b；2）从 36.15 通过隧道打通到 .17 的大模型调用通道；3）zhulong agent 对于如何启动评测非常熟悉。」

**一、这意味着什么（先想清楚再动手）**

- 若基线评测确实在 **.17** 启动，那么 agent **拿不到 RAG（API 文档知识库）**、**也拿不到沙盒 MCP（EDA 环境）**。
- ⇒ **3.04% 这个数不能代表"模型能力"**：它是在缺少工具与知识库的环境下测的，属于**环境缺失**，不是能力上限。
- ⇒ 你已交付的 RCA 报告（`report_posttrain_baseline_pyaether_rca_zh.html`）里的**失败分类与 fix 方案，全部建立在错误口径上**，必须重新评估。
- ⚠️ **不要**把这个当作"模型就是不行"的结论；也**不要**急着重写 RCA —— 先按下面把评测环境修对、重测，再谈归因。

**二、要做的事（与 zhulong 协调，三步）**

1. **serve minicpm5-2b**：在 36.15 上起模型服务（复用你已有的 serve 脚本口径，注意 36.15 路径前缀是 `/nasdata/` 而非 `/nas_train/`）。
2. **打通隧道**：从 36.15 通过 ssh 隧道，把**模型调用通道**暴露给 .17（或反之，按实际调用方向确定；你是被测端，模型端点要可达）。
3. **学 zhulong 的启动方式**：zhulong 的评测 `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`（36.15），
   它的 RAG 服务在 `:9006`、沙盒 MCP 在 `:18891`、沙盒端口 `8650-8654`。
   **启动命令与环境变量口径参考 zhulong 的**（`RAG_RECALL_URL` / `PROXY_PORTS` / `SANDBOX_ENDPOINTS`），能照抄就省事；若你有更好的做法，说明差异与理由即可。

**三、协作方式（我已下发）**

- 我已通过 zhulong 的 ops 中继下发 **RUN_ID 144**：`doc/ZhuLong_DAC2027/run/ops/inbox.md`
  —— 内容 = 在 36.15 上体检 RAG/MCP/沙盒端口/GPU/现有 serve/.17 隧道/SFT ckpt 路径/eda_fastmcp 启动脚本与环境变量口径。
- **你看它的结果**：`doc/ZhuLong_DAC2027/run/ops/outbox.md` 搜 `RUN_ID 144`，拿到实测现状后按它给的路径起跑。
- 你也可以在本线 MEMORY 写一行协作请求，但**不要改 zhulong 的文件**。

**四、判据**

- 重测后给出**新基线**（同 158 题、同判据），并**明确标注两次评测的环境差异**：
  `旧 = .17 无 RAG/无 MCP` vs `新 = 36.15 有 RAG + 有 MCP + 沙盒可达`。
- **旧 RCA 报告的处置**：在报告顶部加一个显著声明，注明「本次分析基于 .17 环境，缺 RAG/MCP，结论仅作参考；
  `新口径见 <新报告>`」。过期结论要显式标 SUPERSEDED，别让它继续当定论。
- 若新基线与 3.04% 差异很大，**如实写**——那说明旧数字是环境问题，这是重要发现，不是失误。

---

### 🔴 用户令 · 2026-11-14 09:0x（**暂停 RL，改为分析 MiniCPM5-2B 基线在 EDA-Eval-PyAether(158) 的 3.04% 与 trace**）· 未完成 · 最高优先

> **用户原话**：「post-train 先花时间分析基线 MiniCPM5-2B 在 EDA-Eval-PyAether（158）跑出的 3.04% 的结果和 trace，暂时不忙做 RL。把失败逐个统计和归因，绘制饼图和表格，挨个类别提出 fix 方案。先给出这份中文 HTML 报告来。」

> ⚠️ **归类方式由你定**：失败分成哪几类，**由你基于 158 题的实际情况（结果 + trace 原文）自行提炼**。下发方不预设类别、不预设数量——分类本身也是你研究结论的一部分。

- **暂停**：不再起新 RL 轮次/调参/写 RL 论证；5-run eval 链不 kill（自动跑、结果照常归档），R2 负信号暂不处置。
- **唯一交付物**：一份中文 HTML 报告，落 `reports/report_posttrain_baseline_pyaether_rca_zh.html`（单文件自包含、0 外链、0 script、图表用内联 SVG）。
- **必须包含**：
  1. 基线口径（哪个 ckpt / serve 配置）+ **158 题逐题结果**，pass 数用原始文件核对（与 3.04% 对账）；
  2. **失败逐个统计与归因**：类别由你提炼，每个类别给题数、占比、**trace 原文摘引 + 文件路径**；
  3. **饼图 + 表格**；
  4. **逐类别 fix 方案**：根因 → 具体改动点 → 预期提升（说明依据）→ 成本 → 优先级，最后给"先做哪几件"的排序；
  5. 结论：3.04% 主要卡在哪一层。
- **纪律**：所有数字可复算（路径 + 命令）；取不到就标 `TODO`，🚫 不许估、不许编 trace 原文。
- **完成后** MEMORY 心跳一行写结论。

---


### 🔴 用户令 · 2026-11-12（**L4 领域评测改由 post-train 主责**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「既然后训练说『隧道第 4 次复验 OK』，那么 Pretrain 说的 L4 BLOCKED 就不成立了。这件事 Pretrain 不要管，由 Post-Train 负责。」

**背景**：R331 已实测 `ssh -p 3333 app.e0031982@localhost` → TUNNEL_OK（hfeg0tedaap02 = 10.251.36.15），`run_code` 端到端 PASS（2+2=4，py3.9.0）。即 pretrain 报的「.15/.17 SSH 不通 ⇒ L4 BLOCKED」在你这套隧道方案下**不成立**。

**立即执行**（与现有 post-SFT eval 主线并行，不得因此停 SFT eval）：

1. **L4 定义**：① zhulong 消融评测（EDA-Eval-PyAether 158 题，cline harness，`model` 可配）；② designflow（EDA-Flow-Bench，`cline_eval/`，61 任务）。
2. **先出基线**：选 1 个已导出的 BaiZe ckpt（优先 170k/180k HF 目录），经隧道在 36.15 起 OpenAI-compatible 服务（vLLM/SGLang/llama-server 三选一，按可用性），用两个 bench 的 `--model` 指过去，各跑**最小可跑子集**（zhulong 先 5–10 题、designflow 先 5 个任务）→ 出基线数 + 复现命令。
3. **再扩到全量**：最小子集 PASS 后，zhulong 158 题；designflow 按其 README 全量。记录 Pass@1、耗时、失败分类（infra vs 能力）。
4. **落盘**：`MEMORY_POSTTRAIN.md` 关键事实段写清「隧道→36.15→EDA 环境→bench 启动」的实际命令链；结果进 `EXPERIMENTS_POSTTRAIN.md` 与对应报告；勿把凭证写进仓库/日志。
5. **对 pretrain**：L4 数字由你产出后，pretrain 只读引用；不要再让 pretrain 碰 .15/.17。

**边界**：不改变 Phase1/Phase2/Phase3 主线优先级；L4 是并行交付项，出数即可，不为追分改 benchmark 协议。

---


### 📦 用户令 · 2026-11-12 11:2x（沙盒隧道 SSH 到 36.15）· ✅ 已闭合 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：dual-nix-tunnel 已通（TUNNEL_OK 实测、run_code e2e PASS 2+2=4），连通配置已落 eda_fastmcp .env + MEMORY 关键事实段。需要时再读。

### 📦 用户令 · 2026-11-10 17:10（serve 占住 GPU5-7 防挖用）· ✅ 已闭合（前提已消失：沙盒已通）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：占位目的达成后 GPU5 转交 vision R9、GPU6/7 转为 step105/R2 eval serve。需要时再读。

### 🔴 用户令 · 2026-11-10 13:40（**GPU 4-7 已到位，三阶段替身计划启动**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「后四卡已腾出。GPU4 serve MiniCPM5-2B，GPU5 serve Qwen3.5-2B，GPU6-7训练。Qwen3.5-2B先不铺了，剩下的卡用于训练。」

#### 0. 当前 GPU 状态（2026-11-10 实测）

| GPU | 用途 | 状态 |
|:--:|:--|:--|
| 0-3 | root SGLang Qwen3.8-27B（:8099） | 占用中，不可动 |
| **4** | **vLLM serve MiniCPM5-2B（:8098）** | ✅ 已启动，正常响应 |
| 5 | 空闲→**按 17:10 令占住** | 待 serve |
| **6-7** | 空闲→**按 17:10 令占住** | 待 serve |

- vLLM venv：`/tmp/vllm_venv/bin/python`（vLLM 0.7.3 + torch 2.5.1 + CUDA 12.4）
- 环境变量：`HF_HOME=/tmp/hf_home HF_MODULES_CACHE=/tmp/hf_home/modules`
- 驱动限制：NVIDIA 550.54.14 → CUDA 12.4 max（不能用 cu128/cu130）
- 模型路径：`/nas_data/app.e0031982/models/{MiniCPM5-2B,Qwen3.5-2B,gemma-4-E2B-it,Llama-3.2-3B-Instruct}`
- ⚠️ **transformers 版本**：必须 4.49.x；agent 若之前升到 5.x 需降回来（`uv pip install --python /tmp/vllm_venv/bin/python "transformers>=4.45,<4.50"`）

#### 1. Phase 1：基线评测（立即开始，仅用 GPU4 评测 + GPU0-3 的 Qwen3.8-27B）

**目标**：用 EDA-Eval 158 任务，同口径横评三个模型，5-run mean±std。

| 模型 | 端点 | 评测方式 |
|:--|:--|:--|
| MiniCPM5-2B | `http://localhost:8098` (vLLM, GPU4) | cline auth → EDA-Eval harness |
| Qwen3.8-27B | `http://localhost:8099` (root SGLang, GPU0-3) | cline auth → EDA-Eval harness |
| DeepSeek（云端） | `http://agi-gateway.cxmt.com/cloud/v1` (glm-5.2 替身) | 已有 P0 诊断数据 |

- 每模型 5-run，报 mean±std + 配对检验
- 采集真实失败轨迹，**用实测替换 P0 D1-D6 的假设值**
- anti-cheat 全程开，报 cheat rate
- 158 任务污染隔离闸门必须 PASS
- 评测协议冻结，不改

**交付物**：`reports/report_posttrain_baseline_3model_zh.html`（里程碑报告，非 rXXXX）

#### 2. Phase 2：替身 SFT 端到端验证（Phase 1 完成后立即开始，GPU6-7 训练 + GPU4 评测）

- 模型：MiniCPM5-2B（2B, Llama 架构, Apache 2.0）作 BaiZe 替身
- 数据：UltraData-SFT-2605 子集（已在 `.29`/`.12` NFS 分词镜像）
- 脚本：`baize_posttrain_anneal.sh` → `baize_posttrain_sft.sh`
- A40 显存约束：48GB/卡，2B SFT 用 2 卡 TP=2 或 DP=2，batch/seq 按 R92 校准配方
- SFT 前后跑 EDA-Eval 评测，验证 SFT recipe 是否提分
- 报告显著标注「替身预演，收益不可迁移到 BaiZe」

**交付物**：`reports/report_posttrain_sft_surrogate_zh.html`

#### 3. Phase 3：替身 RL/GRPO 端到端验证（Phase 2 SFT ckpt 完成后开始，GPU4-7 全部投入）

- 取 Phase 2 SFT ckpt → `baize_posttrain_rl_grpo.sh`
- 激活 R130-R143 设计的 6 个 hook
- 吞吐预估 666 R/hr → ~3000 步约 2-3 天
- 验证：GRPO 是否在 EDA-Eval 上产生正向增益、hook 系统是否稳定
- 报告显著标注「替身预演，收益不可迁移到 BaiZe」

**交付物**：`reports/report_posttrain_rl_surrogate_zh.html`

#### 4. 执行纪律

- GPU4 的 vLLM serve 是**常驻服务**，不要 kill
- Phase 1 和 Phase 2 可以**并行**：GPU4 评测的同时 GPU6-7 跑 SFT
- 训练脚本用 `--dry-run` 先验证再正式跑
- CUDA 限制：只能用 cu124，不能装 cu128/cu130 的包
- vLLM venv 在 `/tmp`（本地磁盘），重启机器后会丢——需要时重建
- 🚫 不碰 GPU 0-3（root 的 SGLang）
- commit 前缀：`posttrain eval:` / `posttrain sft:` / `posttrain rl:`

---

### 📦 §用户令·2026-11-07 10:10（GPU 11/9 到位是既定安排，不要再问；等待期继续深入调研）· ✅ 已闭合 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：R1-R143 调研全完成（EDA交互RL方案/造题/奖励设计/失败模式/GRPO超参/rollout调度/verl hooks），GPU 11/9 已到位并启动 Phase 1。

> **用户原话**：「posttrain：不是说了11/9吗，还问啥。继续调研啊。」

#### 0. 口径澄清（一次性钉死，之后不得再问）

- `.17` 的 4 张 A40 于 **2026-11-09** 到位，这是**既定安排**，不需要用户再确认、不需要运维协调。
- 后续任何唤醒：🚫 **不得**再把「什么时候给 GPU」「是否现在腾卡」「要不要等 11/9」写成阻塞项或待用户决策。
- 正确做法：按 11/9 倒排准备，**到位当天自动起跑**（不等到下次唤醒再问）。

#### 1. 11-07 -> 11-09 的主任务 = 深入调研（不是例行巡检）

每轮唤醒必须至少产出**一项实质内容**并落盘，从下列任选（鼓励都做）：（🚨 注意：**不是每轮一份 HTML 报告**；HTML 按顶部「报告生成纪律」执行，日常产出写 EXPERIMENTS/MEMORY 即可）

| 编号 | 调研方向 | 必须回答的问题 |
|:--|:--|:--|
| R1 | **EDA 环境交互式 RL 的可执行方案** | 环境接口（SSH/双向隧道/本地 clone）如何稳定调用？奖励如何自动可判定？单题 rollout 预算？超时与部分失败的恢复策略？ |
| R2 | **PyAether 造题与难度分层** | 把 500 题模板扩展到可自动判定正确性的规模（目标 2k-5k）；难度标定方法（pass@8 profiling 还是规则分层）；每档题的区分度证据 |
| R3 | **奖励设计与 GRPO 稳定性** | 连续化/分档混合、省 GPU 的 group 配置、长度与格式作弊的抑制、KL 与 clip 的取值依据；失败模式（对照 vision 线离散奖励教训） |
| R4 | **35% 侧失败模式分类** | 从 MiniCPM5-2B 36% 基线出发，按 API 类别/错误类型（语法错、API 误用、逻辑错、超时、缺依赖）建分类法；等 GPU 后用真实轨迹校正 |

#### 2. 反空转条款

- 🚫 禁止「只写心跳 + 置 `WAITING: 1`」式空转。
- **连续两轮无新增调研产出 = 未完成任务**，必须 `WAITING: 0` 继续做。
- 每轮心跳必须写清：`本轮新增调研产出：<文件/章节/结论>`；没有就说明为什么。

#### 3. 交付物

1. 调研结论写入 `EXPERIMENTS_POSTTRAIN.md` 新节（或扩写既有节），带检索词与来源链接；
2. 需要时产出中文 HTML 报告到 `doc/BaiZe-ISEDA2027/reports/`（单文件自包含）；
3. 可执行脚本/配置/数据落 `run/`，须 `bash -n` / `--help` 可跑通；
4. commit 前缀 `posttrain research:` 或 `posttrain prep:`。

#### 4. 11/9 GPU 到位后的第一件事（预先写死）

1. `vllm serve /tmp/models/MiniCPM5-2B`（venv 已就绪）-> 复测 36% 基线（同口径 5-run）；
2. 采集真实失败轨迹，**用实测替换 R4 调研中的假设**；
3. 按 R1/R2/R3 结论起第一轮 EDA 交互式 RL（替身预演），报告显著标注「收益不可迁移到白泽」。

---


### 📦 §用户令·2026-11-07（替身模型 × EDA 交互式 RL 预演）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：L1.0 eda_fastmcp 本地克隆✅ + L1.1 API 分级(3276纯函数/1652副作用/3535不适用)✅ + L2 500题✅(0污染命中) + synth_rl_plan HTML✅ + Tunnel-SOP✅ + SFT-Verify✅(99.76G=75.87+23.89分词产物,.29/.12 NFS可达)。需要时再读。

---

### 📦 §用户令·2026-11-06 22:5x（后训练各阶段数据调研 + 本机硬盘体检）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`

> 交付：`reports/report_posttrain_stage_data_survey_zh.html`（45.4KB / 10 节 / 0 script / 0 外链）+ `EXPERIMENTS_POSTTRAIN.md` §E + 硬盘体检附节。**关键结论**：`/` 386G 可用(84%)、`/nas_data` 20T 可用(85%)，后训练全流程预估 200–300GB ⇒ **存储非瓶颈**；可清理候选 ≈4.7G（Qwen3.5-2B 4.3G 用途待确认）；`/nas_inference` 与 `/nas_env` 在 .17 **未挂载**。需要细节再读 archive。

### 📦 2026-11-06 运维直令（建立 post-train 线 · P0 诊断 + P1 数据盘点 + P2 方案书 + P3 脚本骨架）· ✅ 已闭合（P0/P1/P2/P3预备 全部 ✅；P3 正式训练 ⏻ 等 pretrain ckpt，已在「阻塞项」单列）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理，沿用）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的「等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X」只在该块任务内有效；与最新用户令或最新任务块冲突时，以最新块为准。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）

> ⚠️ **红线（违反则整节作废，见总纲 §5）**：
> 1. **污染隔离**：EDA-Eval-PyAether 的 158 个任务（prompt + 函数签名 + 断言代码）**绝对不能进任何训练集**。允许用 API 参考文档合成训练对，但必须按 API 名/函数签名隔离，论文写明隔离规则。
> 2. **反作弊**：`PreToolUse` hook 全程启用，所有实验臂逐字一致；BaiZe 的 RL 也挂同一套 anti-cheat；必须报告 cheat rate。
> 3. **口径一致**：5-run mean ± std，不得报单次值；158 任务固定集上两系统比较优先用配对检验（McNemar / paired bootstrap）。
> 4. **评测协议冻结项不得改动**（总纲 §2）：158 任务 / Pass@1 / 2500s 超时 / 单 trace 原则 / 5 次独立运行 / `-p 8 -n`。

> 📋 **评测关键资产**（总纲 §3）：
> - 代码生成 driver：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh`
> - 评分：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py`
> - 158-case 数据集：`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`
> - `BASE_DIR`：`/nasdata/app.e0031982/code/eda_fastmcp`
> - BaiZe 接入：通过 vLLM/SGLang 暴露 OpenAI-compatible endpoint，`cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，换 backbone 成本≈0。

> 🎯 **成功阶梯（预注册 · 先定后测 · 总纲 §4 步骤 4）**：
> | 里程碑 | Pass@1 | 含义 | 先验判断 |
> |:--|:--|:--|:--|
> | 起点 | 36% | MiniCPM5-2B，通用模型，零适配 | ✅ 已实测 |
> | M1 | 50% | 工具协议修好（D1/D2/D6 改善） | 几近必然 |
> | M2 | 65% | + 领域继续预训练 + SFT | 大概率 |
> | M3 | 75% | + RL | 有望，已是强结果 |
> | M4 | 85%+ | 逼近 DeepSeek-V4-Pro | 惊喜级别 |
> 阶梯意义：无论落在哪一档，结论都能成立且都值得发表（落在 M1/M2 则支持「规模非瓶颈」论，与 ZhuLong 互证）。

### 🧭 运维规程 · 2026-10-06（agent 归档 MEMORY + 任务书，常驻）

> 用户裁定：MEMORY + 任务书两样都由 agent 自己滚。
> 判据：两者均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交。
> 做法 = 只「搬迁」、不改内容：① 已闭合运维块原文搬入 `run/ARCHIVE_OPERATOR_POSTTRAIN.md`（无则新建）；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块；冲突保留双方；提交用 `posttrain 归档:` 前缀。

## ⚠️ git 同步规则（必读，每次唤醒都要走）

## ══════════════ Stage (ii) 任务定义 ══════════════

你是推进 BaiZe Stage(ii) LLM Post-Training（领域退火 → SFT → RLVR-GRPO → EDA-Eval-PyAether 评测）的自动化 agent（Cline），被唤醒时按 `MEMORY_POSTTRAIN.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

### 阶段总览（与论文 `5_llm_posttrain.tex` 对齐）

| 步骤 | 名称 | 论文节 | 依赖 | 状态 |
|:--|:--|:--|:--|:--|
| 0 | 领域退火（Domain Annealing） | §5.1 | pretrain ckpt | ⬜ 等 pretrain |
| 1 | SFT | §5.2 | 退火 ckpt 或 pretrain ckpt + SFT 数据 | ⬜ 等 P0/P1/P2 |
| 2 | RLVR + GRPO（4 臂奖励 R1–R4） | §5.3 | SFT ckpt + 沙盒 | ⬜ 等 SFT |
| 3 | EDA-Eval-PyAether 评测（backbone × harness 网格） | §5.5 | 各阶段 ckpt | ⬜ 等 ckpt |
| — | Anima 协议 + 本地自纠错（部署） | §5.4 | RL ckpt | ⬜ 部署阶段 |

### 当前可做（不依赖 pretrain ckpt，零/低 GPU）

- **P0**：§7.0 诊断清单 D1–D6（从已有 36% 运行的 `final_report.json` 提取，零 GPU）。
- **P1**：数据盘点 + PyAether 语料调研 + 污染隔离规则草案（零/低 GPU）。
- **P2**：三步训练方案书（纯设计，零 GPU）。
- **P3 预备**：训练/评测脚本骨架（零 GPU，只写不跑）。

### 阻塞项（等依赖就绪）

- **正式训练（退火/SFT/RL/评测）** 阻塞于 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。
- **GPU**：post-train 线在 `10.252.32.17`；正式训练的 GPU 待 pretrain 完成或运维协调分卡（见 `GPU29_ALLOC.md`）。P0/P1/P2/P3预备 纯 CPU/IO 在 `.17` 本机跑。

### 红线（违反则整节作废）

1. **污染隔离**（总纲 §5.1）：158 任务的 prompt + 函数签名 + 断言代码绝对不能进任何训练集。
2. **反作弊**（总纲 §5.2）：`PreToolUse` hook 全程启用；RL 挂同一套 anti-cheat；报告 cheat rate。
3. **口径一致**（总纲 §5.3）：5-run mean ± std；配对检验；引用 ZhuLong 数字前确认口径。
4. **评测协议冻结**（总纲 §2）：158 任务 / Pass@1 / 2500s / 单 trace / 5-run / `-p 8 -n` 不得改动。
5. **预注册**：成功阶梯 M1–M4 + 判定阈值先定后测，避免事后合理化。

### 与他线边界

- **pretrain 线**：提供 base ckpt；post-train 从其收敛 ckpt resume。不 kill pretrain 训练。
- **data 线**：提供 SFT/退火语料的分词镜像；PyAether 语料若需新分词，提需求给 data 线或自行分词（避免重 I/O 撞训练）。
- **harness 线**：提供评测 driver / 评分脚本 / 158-case 数据集的接入方式；post-train 评测复用同一套，只换 backbone。
- **vision 线**：独立，post-train（纯文本）不与 vision 交叉；Stage(iv) MLLM 对齐是另一阶段。

---

> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_POSTTRAIN.md`、`EXPERIMENTS_POSTTRAIN.md` 和 `daily-memories-posttrain/`。
