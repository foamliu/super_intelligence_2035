# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

### 🟢 运维指令 · 2026-10-28 11:0x（**换端口 8663/8666/8667 重跑 r2 regrade**）· 用户直令 · 最高优先 · 覆盖一切

> 用户原话（10-28 11:0x）：「让 zhulong agent 用 8663/8666/8667 端口 regrade 试试」。
> **背景**：10-28 10:3x 令让 agent 重跑 r2 regrade，但 ops 中继先执行了原版 RUN_ID 129 直接起跑 regrade PID 3608951 @10:44:26。agent 10:56 唤醒诊断出**两个致命问题**：
> 1. **stale-shard bug**：`output_evaluation/tmp/execution_results_shard_3.jsonl` 残留 prior 20:07 run 的 29 行 → `run_eval.py` resume 逻辑判定 shard_3"已完成" → **跳过唯一可用端口 8654**，只在 3 个死端口（8650/8651/8652）空转 → 100% timeout → 注定 INVALID。
> 2. **跨用户争用**：`app.t0002997` 用户的 65 个 cline worker（10:29:44 起）抢占共享 sandbox `10.129.32.75:8650-8654` → license pool 实为 0/4（非之前误判的 1/4）。agent 无权 kill 别用户进程。
> 当前 regrade PID 3608951 在 8650-8654 上注定跑 ~5h 出 INVALID，浪费资源且阻塞新 regrade。**必须先停它**，再用 8663/8666/8667（避开 t0002997 抢占组）重起。

**① 你（agent）要做的（按序）**
1. **读 MEMORY 顶部状态头** → 确认 `STAGE`、`PHASE = running`、`WAITING` 当前为 1（本令要求改 0）。
2. **改 `WAITING = 0`** + commit + push（让 loop 进入 ~1min 续跑模式接手后续）。
3. **停当前注定 INVALID 的 regrade**（精确 PID，**🚫 禁止 `pkill -f zhulong`**，会匹配 loop 自身）：
   - 先 `ps -p 3608951 -o pid,cmd` + `ps -p 3608954 -o pid,cmd` 确认是 regrade + run_eval.py（不是别的进程）
   - 确认后 `kill 3608951 3608954`（若 PID 已 GONE 说明自己收口了，跳过）
   - 再 `pgrep -af 'run_eval.py|run_glm-5.3-flash_zl_clinealigned16384_r2_regrade'` 确认无残留（cut -c1-140）
   - **不要 kill t0002997 的 worker**（无权动别用户进程）
4. **清 stale-shard 文件**（修 stale-shard bug，关键）：
   - `rm -f /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/tmp/execution_results_shard_*.jsonl`
   - 清后 `ls -la /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/tmp/` 确认无 shard_*.jsonl 残留
5. **验证 8663/8666/8667 3 端口健康**（真实 run_code 调用，每端口 2 次）：
   - `for p in 8663 8666 8667; do for i in 1 2; do echo "port $p try $i:"; timeout 15 curl -s -m 12 -X POST "http://10.129.32.75:$p/v1/run_code" -H 'Content-Type: application/json' -d '{"host":"aether","lang":"pyAether","code":"print(\"probe ok\")"}' | head -c 180; echo; done; done`
   - **判据**：3 端口 × 2 次 = 6 次全返回 `{"response":"The code execution was successful..."}` 才过。**任一端口失败 → 停手报运维**（不要用坏端口起 regrade）
   - 同时探测 workdir 映射：`curl -s -m 5 http://10.129.32.75:$p/` 看返回（404 = 端口活）；查 `.env` 或上次 r4″（10-20）的 SANDBOX_ENDPOINTS 记录里 8663/8666/8667 对应的 workdir（参考 `MEMORY.md` §3 / `daily-memories/2026-10-20.md`）
6. **改 regrade 脚本的端口**（用 8663/8666/8667）：
   - 复制脚本：`cp /tmp/run_glm-5.3-flash_zl_clinealigned16384_r2_regrade.sh /tmp/run_glm-5.3-flash_zl_clinealigned16384_r2_regrade_8663.sh`
   - 用 sed 改新脚本的 `SANDBOX_ENDPOINTS` + `PROXY_PORTS`：
     - `SANDBOX_ENDPOINTS=8663:/proj/train/AI/workdir/t0002997_1,8666:/proj/train/AI/workdir/t0002997_2,8667:/proj/train/AI/workdir/t0002997_3`（workdir 若与 8663/8666/8667 实际映射不符，按第 5 步探测结果改；若 t0002997_1/2/3 被 t0002997 占用，尝试用 t0002997_5/6/7 或自方分配的 workdir——**核实后如实写**）
     - `PROXY_PORTS=8663,8666,8667`
   - **改后 `head -25` 贴证据**（确认 sed 生效）
7. **重起 regrade**（用新脚本 + 新 log 时间戳）：
   - `cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && unset http_proxy https_proxy ALL_PROXY && export NO_PROXY="10.129.32.75,localhost,127.0.0.1" && export https_proxy="http://172.19.92.23:13128" && unset SANDBOX_PORT_HTTP SANDBOX_PORT_TCP SANDBOX_WORKDIR && setsid bash /tmp/run_glm-5.3-flash_zl_clinealigned16384_r2_regrade_8663.sh > /tmp/ABL_glm-5.3-flash_zl_clinealigned16384_r2_regrade_8663_$(date +%H%M).log 2>&1 < /dev/null &`
   - 8s 后 `kill -0 $PID` 确认存活 + `head -20` log
8. **30min 内报健康**（real_MCP_32001 + sandbox-timeout + licence-unavailable 计数 + 3 端口可达性 + 进度 X/158）。
9. **regrade 收口后判定 r2 有效性**（按判据十三 + infra 作废规则）：
   - **有效**（PASS_RATE 合理 + licence-unavailable ≈ 0 + timeout ≤ 10 + exec_err = 0 + infra 0）→ **记 r2 = pass/158** → 起 r3（用同 8663/8666/8667 端口，generation + regrade）→ r4 → r5 → 5/5 mean±std → 更新报告 §8
   - **无效** → 如实贴 log 末尾 30 行 + 计数 → `WAITING=1` 报 blocker
10. **若 r2 有效，r3-r5 同用 8663/8666/8667 端口**（避开 t0002997 抢占组，直到 t0002997 收口或运维另令）。
11. **每一步 commit + push**（带 `zhulong 8663-port:` 前缀）。

**② 验收判据（不达标要如实报，不得粉饰）**
1. 当前 regrade PID 3608951/3608954 **必须停**（不能让它跑 5h 出 INVALID 浪费资源）；
2. stale-shard 文件**必须清**（否则新 regrade 也会被 resume 逻辑坑）；
3. 8663/8666/8667 3 端口 **6 次 run_code 探针全过**才起 regrade；
4. r2 regrade log 末尾必须贴证据（PASS_RATE + licence-unavailable 计数）；
5. 5/5 mean±std 与 cline 86.8±1.6% 对比，**必须在报告里给出"已排除配置混杂 + 排除跨用户争用"的结论**。

**③ 红线**
- 🚫 **禁止 `pkill -f zhulong`**（会匹配 loop 自身）—— 用精确 PID；
- 🚫 **不 kill t0002997 的 worker**（无权动别用户进程）；
- 不覆盖 r1 产物（r1 ✅ = 71.5% 已收口）；
- 不动 8192 的 5 个 VOIDED batch；
- 不改 providers.json / .env / cline settings（配置已对齐，本令只换 regrade 端口）；
- regrade log 不覆盖 10:44 那次（带时间戳 + 8663 命名）；
- 8663/8666/8667 探针任一失败 → 停手报运维，不强行起 regrade。

**④ 与 10-28 10:3x 令的关系**
- 10:3x 令的"重跑 r2 regrade"由本令接手并**细化**：增加"停旧 regrade + 清 stale shard + 换端口 8663/8666/8667"三步。10:3x 令的 r3-r5 推进 + 报告更新部分继续适用（端口改用 8663/8666/8667）。

**⑤ 8663/8666/8667 端口背景**
- 10-20 r4″ 曾用 8663/8666/8667/8670（用户令复活，原 §6 标记"作废"已过时）→ 8663 当时验证可用；
- 这次用户指定 3 个（无 8670），-p 参数用 3（不是 4）；
- workdir 映射需 agent 实测确认（8663/8666/8667 → t0002997_X 的 X 是什么，或是否需用别的 workdir）。

---

### 🟢 运维指令 · 2026-10-28 10:3x（**重新 regrade r2 + 推进 r3-r5**）· 用户直令 · 已由 11:0x 令接手细化

> 用户原话（10-28 10:3x）：「重新 regrade」（针对 r2 regrade 自 10-27 20:07 INVALID 后已 14h+ 未重试、agent 仅做 21 次单次 curl 探针推理"必然失败"而未实测的情况）。
> **背景**：r2 generation 已于 10-27 19:09 收口（batch `2026_1027_123502`·158 行 jsonl·132 success/21 fail/5 timeout·worker providers.json 实测 = `glm-5.3-flash + 16384 + /v1 + reasoning=false` 与 cline 基线逐字节对齐 ✅）。r2 regrade 20:07 跑过一次但 **INVALID**（93/118 licence unavailable，仅 shard3=8654 那批 25 条能跑 → PASS_RATE=0.1582）。此后 14h+ agent 仅做单次 curl 探针（每次都是 pool 1/4：8654 ✅ / 8650·8651·8652 ❌ hang 或 circuit-breaker OPEN），按 §7 infra 作废规则判定"重跑仍会 ~75% fail"而**未再实测 regrade**。用户判定此推理不充分，要求**直接重跑 regrade 拿真实数据**。

**① 你（agent）要做的（按序）**
1. **读 MEMORY 顶部状态头** → 确认 `STAGE = zhulong×glm-5.3-flash×full×maxTokens=16384 cline-aligned 5-run`、`PHASE = running`、`WAITING` 当前为 1（本令要求改 0）。
2. **改 `WAITING = 0`**（本令解除等待）+ commit + push（让 loop 进入 ~1min 续跑模式接手后续 r3-r5）。
3. **先做一次 4 端口 license 探针**（`curl -m 12 -X POST http://10.129.32.75:$p/v1/run_code -d '{"host":"aether","lang":"pyAether","code":"print(\"probe ok\")"}'`，p = 8650/8651/8652/8654），记录结果。**但无论探针结果如何，都必须继续执行第 4 步重跑 regrade**（探针只留对比数据，不作为是否重跑的判据——这是本令的核心）。
4. **重跑 r2 regrade**：
   - regrade 脚本：`/tmp/run_glm-5.3-flash_zl_clinealigned16384_r2_regrade.sh`（就位·07:34 已校正无路径 bug·直接用）
   - **启动前必须 `unset SANDBOX_PORT_HTTP SANDBOX_PORT_TCP SANDBOX_WORKDIR`**（防 futex 死锁，与 r1 regrade 同口径；20:07 第 1/2 次失败就是 stale SANDBOX_PORT_HTTP env 导致）
   - 启动命令（参考 r1 regrade）：`cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && unset http_proxy https_proxy ALL_PROXY && export NO_PROXY="10.129.32.75,localhost,127.0.0.1" && export https_proxy="http://172.19.92.23:13128" && unset SANDBOX_PORT_HTTP SANDBOX_PORT_TCP SANDBOX_WORKDIR && setsid bash /tmp/run_glm-5.3-flash_zl_clinealigned16384_r2_regrade.sh > /tmp/ABL_glm-5.3-flash_zl_clinealigned16384_r2_regrade_$(date +%H%M).log 2>&1 < /dev/null &`
   - **regrade log 命名带时间戳**（避免覆盖 20:07 那次的 log）
   - regrade 跑完（~10-30min）后**读 log 末尾**拿 `PASS_RATE` + licence-unavailable 计数 + timeout 计数
5. **判定 r2 有效性**（按判据十三 + infra 作废规则）：
   - **有效**（PASS_RATE 合理 + licence-unavailable ≈ 0 + timeout ≤ 10 + exec_err = 0 + infra 0）→ **记 r2 = pass/158** → 起 r3（同 batch 流程：generation → regrade）→ r4 → r5 → 5/5 mean±std → 更新报告 §8
   - **无效**（仍大面积 licence-unavailable，与 20:07 同型）→ **如实报**：贴 regrade log 末尾 30 行 + licence-unavailable 计数 + 4 端口探针结果 → `WAITING=1` 等 license 恢复（但至少有了一份新鲜实测数据，而非 14h 前的旧推理）
   - **futex 死锁**（regrade 起不来）→ 检查 stale env → 修正后重试（最多 2 次）→ 仍不行则报 blocker
6. **若 r2 有效，推进 r3-r5**（每轮同判据十三：timeout ≤ 10、exec_err = 0、infra 0）→ 5/5 mean±std → **与 cline 基线 86.8±1.6% 对比** → 更新 `reports/report_zhulong_agent_compare_cline_vs_zhulongcli_full_zh.html`（新增"maxTokens=16384 cline-aligned 重测"一节，纠正上轮报告"cline 线 8192"的错误说法——cline 基线实测 = 16384，batch `2026_1019_005714` 为证）。
7. **每一步都 commit + push**（带 `zhulong 16384-aligned:` 前缀）。

**② 验收判据（不达标要如实报，不得粉饰）**
1. r2 regrade **必须实测**（不得以"探针推断必然失败"为由跳过）；
2. r2 regrade log 末尾必须贴证据（PASS_RATE + licence-unavailable 计数）；
3. 若 r2 有效，r3-r5 各轮判据十三全过才进 5-run；
4. 5/5 mean±std 与 cline 86.8±1.6% 对比，**必须在报告里给出"已排除配置混杂"的结论**（maxTokens 已逐字节对齐，唯一变量 = CLI 二进制）。

**③ 红线**
- 不覆盖 r1 产物（r1 ✅ = 71.5% 已收口）；
- 不动 8192 的 5 个 VOIDED batch（留证）；
- 不动 `2026_1026_154647`（16384 候补，已恢复）；
- 不改 providers.json / .env / cline settings（配置已对齐，本令只重跑 regrade）；
- 不启 full@pro-cloud（那是另一条线）；
- regrade log 不覆盖 20:07 那次（带时间戳命名）。

**④ 与 10-27 令的关系**
- 10-27 令的 ①②③④ 已全部闭环（8192 VOIDED / 154647 恢复 / r1 收口 / r2 generation 完成）。本令只接手 **r2 regrade + r3-r5**，不重复 10-27 令的已闭环部分。
- 10-27 令的验收判据（maxTokens diff 为空 / gen-fail ≤ 5/158 / 5 轮判据十三有效）继续适用。

**⑤ ops 通道**
- RUN_ID 129（只读探针·不跑 regrade）已下发，结果会落 `run/ops/outbox.md` 末尾。**agent 不要参考 ops 探针结果来决定是否跑 regrade**——无论 ops 探针结果如何，agent 都必须按本令第 4 步重跑 regrade。ops 探针仅用于运维侧体检。

---

### 🟢 运维指令 · 2026-10-27 09:0x（**修正 maxTokens 错配：8192→16384（与 cline 基线对齐）→ 作废 8192 的 5-run → 重起 16384 的 5-run**）· 用户直令 · 已大部分闭环·r2 regrade 由 10-28 令接手

> 用户原话（10-27）：「让 ZL 试验完全使用 cline 相同的配置：glm-5.3-flash+full 配置。把现有评测停下。确保配置完全一致的情况下，启动 ZL 5-run 评测。」
> **背景**：10-24 22:1x 令错误把 cline 基线 maxTokens 归因为 8192（实际 cline 基线 10-18/19 retest r1-r5，batch `2026_1019_005714` 留存 worker config = **16384**，已逐项核对验证）。10-26 15:46 运维已把 providers.json 改 16384 起的 r1 batch `2026_1026_154647`，但**任务书旧块仍写"maxTokens 必须 = 8192"**，agent 按任务书优先原则把 16384 batch 作废、改回 8192 重起 5-run（r1 `2026_1026_160802` / r2-r5 同），封盘 70.8±7.7%。**该 5-run maxTokens 与 cline 基线不一致（8192 vs 16384），不能作为 CLI 回归结论**。

**① 已由运维完成（勿重复）**
1. **修正任务书**：本块置顶，旧块（10-26 08:1x）降级为 `text`；旧块里所有"maxTokens=8192"的硬约束**作废**，以本块为准。
2. **修正配置源**：已把 `~/.zhulong/settings/providers.json` 与 `~/.zhulong/data/settings/providers.json` 的 `maxTokens` 改为 **16384**（两处都已改，已验证）。
3. **停当前 eval + loop**：8192 的 5-run 已封盘不再跑，loop 已停（PID 3659222 由运维停）。

**② 你（agent）要做的（按序）**
1. **读 MEMORY 顶部状态头** → 确认 `STAGE = zhulong×glm-5.3-flash×full 5-run（maxTokens=16384 cline-aligned 重跑）`、`PHASE = running`、`WAITING = 0`。
2. **作废 8192 的 5 个 batch**（写 VOID_REASON.txt，留证不删）：
   - `2026_1026_160802` / `2026_1026_190240`（已确认 8192）+ 其余 3 个 8192 batch（从 `2026_1026_16*` ~ `2026_1026_2*` 范围内 worker config = 8192 的全部作废）
   - VOID_REASON 写明："maxTokens=8192 与 cline 基线 16384 不一致，10-27 令作废，数据留证不进 5-run"
   - **不要作废 `2026_1026_154647`**（它是 16384 的，已被前轮误作废，需<b>恢复</b>：删其 VOID_REASON.txt，它可进 16384 5-run 作为 r1）
3. **起 r1**（zhulong × glm-5.3-flash × full × maxTokens=**16384** × 8650 组 × `-p 4`）：
   - `cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && unset http_proxy https_proxy ALL_PROXY && export NO_PROXY="10.129.32.75,localhost,127.0.0.1" && export https_proxy="http://172.19.92.23:13128" && CLI_AGENT=zhulong EDA_RUNCODE_READBACK=full setsid bash scripts/run_zhulong_script.sh -p 4 -n > /tmp/ABL_glm-5.3-flash_zl_clinealigned16384_r1.log 2>&1 < /dev/null &`
   - **关键**：worker 会复制 `~/.zhulong/settings/providers.json`（= `glm-5.3-flash + 16384` ✅）。
4. **起跑后验证 worker 用的模型**：从 `<batch>/cli_data/worker_1/data/settings/providers.json` grep `maxTokens` 应为 **16384**。**若仍是 8192 立即停跑报错**（这是本线的硬约束）。
5. **r1 → 手动 regrade → 记 `pass/158` + `gen-fail` + 耗时 → r2 → ... → r5 → 5/5 mean±std**。
6. **与 cline 基线 86.8±1.6% 对比**，更新 `reports/report_zhulong_agent_compare_cline_vs_zhulongcli_full_zh.html`（新增"maxTokens=16384 cline-aligned 重测"一节，<b>纠正</b>上轮报告"cline 线 8192"的错误说法——cline 基线实测 = 16384，已留存 batch `2026_1019_005714` 为证）。

**③ 验收判据（不达标要如实报，不得粉饰）**
1. `maxTokens` 等配置 **diff 为空**（除 CLI 名/路径）—— **worker providers.json 必须 = glm-5.3-flash + 16384 + /v1 + reasoning=false**；
2. 单轮 **gen-fail ≤ 5/158**；
3. 5 轮判据十三有效（timeout≤10、exec_err=0、infra 0）；
4. **若 16384 5-run 仍显著低于 cline 86.8±1.6%，必须在报告里给出"已排除配置混杂"的结论**（maxTokens 已逐字节对齐，唯一变量 = CLI 二进制）。

**④ 关键判据：cline 基线真实配置（不可篡改，已留证）**
- cline 基线 = 10-18/19 retest r1-r5，batch `2026_1019_005714` 留存
- worker config 实测：`model=glm-5.3-flash / maxTokens=16384 / baseUrl=http://agi-gateway.cxmt.com/v1 / reasoning.enabled=false / apiKey=02_088EE...BF697`
- regrade 脚本注释（`/tmp/run_glm-5.3-flash_retest_r1_regrade.sh`）：`运维令三十一·2026-10-18·-p 4 起步`
- **结论**：cline 基线 maxTokens = **16384**（不是 8192），-p = **4**，benchmark = PyAether 158
- ZL 5-run 必须与此逐字节对齐，唯一变量 = CLI 二进制（cline vs zhulong）

**⑤ ⚠️ loop 自杀防护（不变）**
- 禁止 `pkill -f 'zhulong'`（会匹配 loop 自身）。用精确 PID 或 `pkill -f 'run_zhulong_script.sh'`。

**⑥ 口径备注**
- 本线 = **zhulong×glm-5.3-flash×full×maxTokens=16384**（与 cline 基线逐字节对齐），目的是与 **cline×glm-5.3-flash×full×maxTokens=16384**（基线 86.8±1.6%）做"只差 CLI 二进制"的干净对比。
- 8192 的 5-run（70.8±7.7%）<b>作废</b>，不进对比；数据留证。
- 上轮 `2026_1026_154647`（16384，被前轮误作废）<b>恢复</b>，可作为 16384 5-run 的 r1。

**⑦ 与 10-25 论文改稿令的关系**
- 10-25 改稿令**并行**，不冲突。5-run 照跑，论文改稿在等待空档推进。

---

### 🟠 历史指令 · 2026-10-26 08:1x（**作废 224219（配置错误）→ 已修复 worker 配置源 → 重启 loop → 用正确配置重跑 zhulong×glm-5.3-flash×full 5-run**）· 已被 10-27 令覆盖

> ⚠️ **本块已被 10-27 令覆盖**：本块里所有"maxTokens=8192"的硬约束**作废**，cline 基线实测 maxTokens = 16384（见 10-27 令 ④）。本块保留仅供历史追溯。

```text

> 用户原话（10-26）：「作废224219，重启 agent loop。你现在 36.15机器上，可以直接操作。」
> **背景**：10-24 22:1x 令要求「停 cline-full → zhulong 配置对齐 cline（maxTokens 8192）→ zhulong 重跑 5-run」。但 224219 起跑时 **worker 复制了 stale providers.json**（`~/.cline/data/settings/providers.json` = `deepseek-v4-pro + maxTokens=16384`），而非令要求的 `glm-5.3-flash + maxTokens=8192`。根因：`run_cli.sh` 默认 `CLI_DATA_DIR=~/.cline/data`，而 `run_zhulong_script.sh` 的 `export CLI_DATA_DIR=~/.zhulong` 在某些启动路径下未生效。此外 agent loop 在 10-24 22:46 执行 `pkill -f 'zhulong'` 杀 cline-full r1 时**误杀了自己**（zhulong_loop.sh 匹配了 `zhulong`），导致 loop 死亡 ~34h。

**① 已由运维完成（勿重复）**
1. **作废 224219**：已写 `VOID_REASON.txt` 到 `2026_1024_224219/`；数据留证不删；不进 5-run。
2. **修复 worker 配置源**：已把 `~/.zhulong/settings/providers.json`（正确值 `glm-5.3-flash + maxTokens=8192 + baseUrl /v1`）复制到 `~/.zhulong/data/settings/providers.json`（run_cli.sh 复制源）。验证：模拟 worker 复制 → 得 `glm-5.3-flash + 8192` ✅。
3. **确认当前配置全对**：`.env` `CLI_AGENT=zhulong / READBACK=full / PROXY_PORTS=8650,8651,8652,8654`；`~/.zhulong/settings/providers.json` `model=glm-5.3-flash / maxTokens=8192 / baseUrl=http://agi-gateway.cxmt.com/v1 / reasoning.enabled=false`；8090 PID 2778637 活 + full readback 四字段 ✅；4 端口 8650/8651/8652/8654 全 OK。
4. **重启 agent loop**：用**登录 shell** 启动（`setsid bash -lc "exec bash <...>/zhulong_loop.sh" > /tmp/zhulong_loop.log 2>&1 < /dev/null &`），确保 PATH 有 `zhulong`。启动后自检 `command -v zhulong` 有输出 + log 无 `No such file`。

**② 你（agent）要做的（按序）**
1. **读 MEMORY 顶部状态头** → 确认 `STAGE = zhulong×glm-5.3-flash×full 5-run（配置对齐后重跑）`、`PHASE = running`、`WAITING = 0`（loop 刚重启，需起 r1）。
2. **起 r1**（zhulong × glm-5.3-flash × full × maxTokens=8192 × 8650 组 × `-p 4`）：
   - `cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && unset http_proxy https_proxy ALL_PROXY && export NO_PROXY="10.129.32.75,localhost,127.0.0.1" && export https_proxy="http://172.19.92.23:13128" && CLI_AGENT=zhulong EDA_RUNCODE_READBACK=full setsid bash scripts/run_zhulong_script.sh -p 4 -n > /tmp/ABL_glm-5.3-flash_zl_aligned_r1.log 2>&1 < /dev/null &`
   - **关键**：`run_zhulong_script.sh` 会 `export CLI_DATA_DIR=~/.zhulong`（已确认 line 28），worker 会复制 `~/.zhulong/settings/providers.json`（= `glm-5.3-flash + 8192` ✅）。
3. **起跑后验证 worker 用的模型**：从 `<batch>/cli_data/worker_1/data/settings/providers.json` grep `model` 应为 `glm-5.3-flash`、`maxTokens` 应为 `8192`。**这条必须贴证据**（若仍是 `deepseek-v4-pro` 或 `16384` 立即停跑报错）。
4. **r1 → 手动 regrade（Step7.1 auto-grade 有已知 bug）→ 记 `pass/158` + `gen-fail` + 耗时 + `-32001` + `sandbox-timeout` → r2 → ... → r5 → 5/5 mean±std**。
5. **与 cline 基线 86.8±1.6% 对比**，更新 `reports/report_zhulong_agent_compare_cline_vs_zhulongcli_full_zh.html`（新增"配置对齐后重测"一节）。

**③ 验收判据（不达标要如实报，不得粉饰）**
1. `maxTokens` 等配置 **diff 为空**（除 CLI 名/路径）—— **worker providers.json 必须 = glm-5.3-flash + 8192**；
2. 单轮 **gen-fail ≤ 5/158**（对齐前 12–27）—— 这是本次对齐最该改善的指标；
3. 5 轮判据十三有效（timeout≤10、exec_err=0、infra 0）；
4. 若对齐后 zhulong 仍显著低于 cline，**必须**在报告里给出"已排除配置混杂"的结论。

**④ ⚠️ loop 自杀防护（血泪教训）**
- **禁止用 `pkill -f 'zhulong'`**（会匹配 `zhulong_loop.sh` 自己 → loop 自杀）。如需停 eval，用**精确 PID**：`kill <launcher_PID>`，或 `pkill -f 'run_zhulong_script.sh'`（不含 `zhulong` 字样）。
- **禁止用 `pkill -f 'cline'`**（同理会匹配 cline 相关非目标进程）。停 cline eval 用 `pkill -f 'run_cline_script.sh'`。

**⑤ 作废明细（留证不删）**
- `2026_1024_224219`：worker stale providers.json = `deepseek-v4-pro + maxTokens=16384`（应为 `glm-5.3-flash + 8192`）→ ❌ 作废（已写 `VOID_REASON.txt`）。
- 上一线 ZL-flash full 5/5（10-23，原始配置 maxTokens=16384）= **75.6±4.4%** ✅ 已收口（但 maxTokens 未对齐，不作为 CLI 对比锚点）。
- cline-full r1 `2026_1023_231253` / r2 `2026_1024_141148`：被 22:1x 令停，r2 未 regrade（可补 regrade 留档，但不进 5-run）。

**⑥ 口径备注**
- 本线 = **zhulong×glm-5.3-flash×full×maxTokens=8192**（配置对齐 cline 后），目的是与 **cline×glm-5.3-flash×full×maxTokens=8192**（基线 86.8±1.6%）做"只差 CLI 二进制"的干净对比。
- 新线（glm-5.3-flash × zhulong）**不纳入论文**（用户 10-23 直令）。论文锚点仍用旧线 (N′) fp4×cline 4 轮 mean=76.7% provisional。
- 论文已砍到正文 6 页（DAC 限制达成，commit `e7de188d` + `3651b322`）。

**⑦ 与 10-25 论文改稿令的关系**
- 10-25 00:0x 令（按外部评审意见改论文）**与 5-run 并行**，不冲突。5-run 照跑，论文改稿在等待空档推进。
- 若论文改稿需打断 5-run 验证关键点，按 10-25 令「先落盘 + 记 MEMORY + 事后 regrade 补记」执行。
```

---

### 📕 改稿任务令 · 2026-10-25 00:0x（**按外部评审意见改论文（含 57.4pp 归因硬伤）**）· 用户直令 · 与 5-run 并行 ·【保留·与 10-26 令并行】
> **评审原文（必读，逐条对照）**：`doc/ZhuLong_DAC2027/reviews/REVIEW_DAC2027_external_2026-10-24.md`
> 评审结论：**Borderline / major revision**。核心建议 = 「把论文做成**实证 EDA 自动化论文**，grounding-gap 只作**有边界的框架/假设**，不要当成已证明的定理」。

**对：逐条核对（必须先做，别急着改）**
1. 对每条意见给出判定：**成立 / 部分成立 / 不成立**，并**锚定证据**（论文节号/表号/页码，或 `zhulong_results.md` 的行）；
2. **重点核对第 2 条（57.4pp）**：Table 3 里 `no read-back 62.2 → binary 65.5 → full 75.7`，**受控 read-back 轴只有 13.5pp**；57.4pp = 75.7−18.3（含检索+沙盒+自探索的系统级增益）。若核对成立 ⇒ **这是必须改的硬伤**（abstract / 贡献条 / §4.2 / §6.2.1 四处都要改）；
3. 核对第 5 条（SKILL 60.3 vs w/o Self-Expl. 61.5；PyAether 去检索后 81.0 vs 77.3）是否与 `zhulong_results.md` 的 C1/S1 表一致。

**改（P0，必须落地）**
- **A. 57.4pp 归因**：按上面口径拆成三个数并分别表述（受控 read-back 13.5pp / binary 3.3pp / 系统级 57.4pp）；
- **B. 理论降级或补证**：二选一 ——（i）给出显式假设下的 Proposition + 证明；或（ii）把 `D_grounding ≤ g(ε)` 明确写成 **hypothesis/framework**，并把 §4.2 的措辞改到与证据相称（评审给了可直接用的替代句式，见评审 §5）；
- **C. benchmark 可复现性**：补一小节写明「可公开什么 / 受许可限制不能公开什么 / 独立研究者能复现到哪一步 / assertion 如何设计与防假阳性」；
- **D. related work 加强**：对 ChatEDA / AutoEDA / MCP4EDA / LayoutCopilot / ChaTCL / RAG-EDA 逐条写**三句差异**（目标环境 / 统一接口 / 实证贡献），别再只说"我们不同"；
- **E. 参考文献占位符**：修掉 `In Proceedings of . ACM` 这类空字段（ACM-Reference-Format + 缺字段导致）。

**补（强烈建议，能做就做）**
- **F. 成本/延迟/token**：⚠️ **用户提示：陈熙元的版本里已有 cost 数字，可在 git 历史里查到**。请先在 git 里检索（如 `git log --all -S 'cost' -- doc/ZhuLong_DAC2027`、`git log --all --author=Chen`、grep `cost|token|latency|耗时|成本` 于历史版本/`daily-memories`），**找到就直接复用并注明出处 commit**；确实找不到再从 eval log 统计（每任务 token / 墙钟 / tool calls / 约当成本）并标"需补测"。
- **G. SKILL 回归**：回答"为什么离线自探索在 SKILL 上反而 −1.2pp"（给假设 + 可从日志验证的判据）；
- **H. Tcl 拆开报**：WaveView(77) 与 Innovus(57) 分别给数，不要只给 pooled 87.2%；
- **I. 统计**：给 5-run 的 **Wilson CI + 配对 McNemar**（数据已有，不用重跑）；
- **J. 部署声明**：把"服务数百名工程师"改成可核验的表述，或标为"内部部署（细节受限）"。

**交付**
1. `reports/report_zhulong_review_response_zh.html`（中文 HTML，**response-letter 风格**：意见 → 判定 → 证据位置 → 具体改动（原文/新文对照）→ 若未改要写理由）；用 cimi search 时可引用外部资料（给出处）。
2. 论文修订：改完必须 `pdflatex×1 + bibtex + pdflatex×2` 通过，且保持 **7 页（正文 6 + refs 1）**、`0 undefined`、无 Overfull/Underfull 告警（`main.log` 自查）。
3. 更新 `zhulong_results.md` / `MEMORY_ZHULONG.md` 的对应行；commit 前缀 `zhulong paper-review:`。
> 允许为验证关键点打断正在跑的 5-run（先落盘 + 记 MEMORY + 事后 regrade 补记）。**不得编造任何数字或文献**；凡"待补"必须写明怎么补。


### 📦 已归档 batch 13 · 2026-10-27（10-24 全批 + 10-23 22:1x + 10-23 09:4x 等已闭合块原文搬入 ZHULONG_TASK_ARCHIVE.md §归档 batch 13）

> 以下均已闭合/已被取代，1-line 指针，需要时读 archive §归档 batch 13。**当前活跃块 = 上方 🟢 2026-10-26 08:1x 与 📕 2026-10-25 00:0x**。
>
> - 🩺 2026-10-26 ops 中继修复（已修复·relay PID118463 活·.last_run_id=128=inbox 顶部）→ archive §batch 13
> - 🔧 2026-10-26 cimi_search/cimi_fetch 挂载（已通过 research MCP server 可用·无需再修）→ archive §batch 13
> - 📝 2026-10-24 23:0x DAC 标准审稿 + 改稿方案（已交付 `reports/report_zhulong_dac_readiness_review_zh.html` 41.6KB）→ archive §batch 13
> - 📐 2026-10-24 19:0x 论文排版（commit 3651b322·已闭合）→ archive §batch 13
> - ✅ 2026-10-24 22:23 配置对齐（maxTokens 16384→8192·已被 10-26 令覆盖）→ archive §batch 13
> - 🔬 2026-10-24 22:15 已核实事实（RUN_ID 115/117 实测·历史参考）→ archive §batch 13
> - 🔴 2026-10-24 22:1x 停 cline-full + zhulong 对齐 + 重跑 5-run（已被 10-26 令覆盖）→ archive §batch 13
> - 📊 2026-10-24 20:2x cline vs zhulong-CLI 差异归因报告（已交付 25.9KB）→ archive §batch 13
> - 📐 2026-10-24 15:4x 引用修正（Lemma→Claim + delage2010percentile·已执行）→ archive §batch 13
> - 📄 2026-10-24 16:1x refs 单独起页（已执行·commit 3651b322）→ archive §batch 13
> - ✅ 2026-10-24 13:0x 执行令（②A+③删附录B+④TikZ 重画·已执行 commit d2d9bb7a）→ archive §batch 13
> - 🆕 2026-10-23 22:1x cline×deepseek-v4-pro×full 5-run（**部分活跃·pending 用户决策 (b) 引用·r1 batch 2026_1023_231253 已硬切留证·是否起 r2-r5 待裁决**）→ archive §batch 13
> - 🟢 2026-10-23 09:4x 作废 r1-r3 + 改 full + 重跑 5 轮（已被 10-26 令覆盖·r1-r3 N′ 数据作废留证）→ archive §batch 13
> - 📦 batch 12 / batch 10 / batch 11 等更早归档指针 → 见 ZHULONG_TASK_ARCHIVE.md 各 §归档 batch N

> 📄 **报告格式常驻规程（2026-10-24 用户令·保留）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑）。**注**：`wo_sandbox`(=rag 已测) / `wo_selfexpl`(已测·运维令二十六排队干净重测) 不再「暂缓」。 |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 📦 已归档（2026-10-20，batch 6）：运维令 十四 ~ 二十四（10-13 ~ 10-15 批次）

> 均已闭合（echo 数据/消融建议书/paper 编译/SKILL-Tcl 并入/沙盒暂停-恢复撤销等）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（06:4x，batch 7）：十三（75% 下限规则）+ 预留追加块

> 均已闭合/长期未使用，原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_ZHULONG.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ZHULONG_TASK_ARCHIVE.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `zhulong 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**29KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动。


### 🧭 运维规程 · 2026-10-06（**【每轮唤醒必须自己 commit+push】** —— 不许依赖 loop 兜底）· 常驻

> **用户指令（2026-10-06）**：与 BaiZe 四线同口径 —— **每条线每次唤醒都要推送**。本线此前明文写「靠外层 loop 每 ~5h 兜底」⇒ **自本轮起作废该口径**（§11 已同步修改）。
> **为什么**：运维**只能靠 git 判断你是死是活** —— 2026-10-06 data 线心跳文件近 2h 未更新，被**误判成卡死并上机排查**。🚫「loop 每 N 小时兜底」**不再作为交付保障**，只是保险丝。
> **每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡**：
> 1. **写心跳**：更新 `run/MEMORY_ZHULONG.md` 顶部状态头 / 执行看板 / 成绩表 + 追加 1 行操作流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮（**当天文件必须建**）。
> 3. **自己提交 + 推送**（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run doc/ZhuLong_DAC2027/ZhuLong_DAC2027` → `git commit -m "zhulong <阶段/轮次>: <一句话>"` → `git push origin main`。🚫 **绝不用 `git add -A`**（多项目共用工作副本，会卷入别线在途文件）。
> 4. **闭环自检**：`git status -sb` ⇒ 无 ahead / 无 behind。**push 失败**（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下轮第一件事补推**。
> ⏱️ **判死判据（硬）**：**心跳文件 >60min 无新提交 ⇒ 按卡死处理**（不再等你）。**你干得再多，心跳不动 = 仍会被判死。**


### 📦 已归档（2026-10-20，batch 4）：运维令 十二 / 十一 / 十 / 九 / (一)~(八)10-10 / (二)~(五)10-09

> 均已闭合（full_v3 5/5=82.1±3.0% 已交付、r2–r5 已完成、RAG/沙盒排查已收口）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。需要时再读。


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**（详细 bash 脚本已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·该修复已于 10-08 执行完毕，loop 持续带代理运行）：核心 = `pkill -f zhulong_loop.sh` → `export https_proxy=http://172.19.92.23:13128 http_proxy=...` → `setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &` → 复核 `/proc/$PID/environ` 含 `https_proxy`。

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 📦 已归档（2026-10-20，batch 5）：运维令 10-08(一) / 10-05(四~八) / 10-04(全)

> 均已闭合（HTML 报告已交、ops 中继稳定、config dir 隔离已落地、试验次序 B→C1→C2→S1 已生效、环境迁移已落地）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。
   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（红线 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
