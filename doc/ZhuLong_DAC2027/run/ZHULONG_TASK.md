# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_ZHULONG.md` / `daily-memories/` / `run/` 下自建脚本 / 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`）。

### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `wo_sandbox` / `wo_selfexpl`（tab:main-ablation 这两行暂缓）· `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑） |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

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


### 🧭 本轮（2026-10-10 晚）执行顺序 —— **排查已完成 → 现在执行 `(七)`（按 A）**

> ✅ **`(四)` 根因排查已完成**：**`8667` 端口实例退化**（2/3 超时@65s）· `8650–8654` 全健康@0.0s · 根因 = **坏端口 + 客户端 60s 超时太短**（服务端 `SANDBOX_TIMEOUT=150s` 能等）；`PreToolUse` hook **无关**。
> ➡️ **现在执行 `(七)`（用户裁定「按 A」）**：**剔除 `8667` + 补入 `8650–8654`（→8 个全健康端口）+ 调高 MCP 客户端 timeout → 重跑 `r2→r5`**。
> ❌ **`(六)` 作废**（其「9 端口均健康」前提已被 `(四)` 证伪）；`(三)` 已由 ops relay 完成，**勿重复**。

### 🆕 运维指令 · 2026-10-10（七）— ✅ **按 A 执行**：剔除 `8667` + 补入 `8650–8654`（→8 健康端口）+ 调高 MCP timeout → 重跑 r2–r5【最高优先 · 覆盖 (六)】

> **用户令（2026-10-10 晚）**：「**按 A 下发指令**」= 依据 `(四)` 结论：**剔除坏端口 `8667`** + **补入实测健康的 `8650–8654`** + **调高 MCP 客户端 timeout** → **重跑 `r2→r5`**。

**① 确认停**：`pgrep '^bash scripts/run_cline_script'` / `pgrep run_eval.py` **均无输出**（r2_new2 已作废）。

**② 改 `.env`**（`/nasdata/app.e0031982/code/eda_fastmcp/.env`）
- `PROXY_PORTS=8663,8666,8670,8650,8651,8652,8653,8654`（**剔除 8667** → 共 **8** 个）。
- `SANDBOX_ENDPOINTS` 补全 **8 条**映射：新 3 = `8663`/`8666`/`8670`（**逐个按原 `.env` 核对**各自 workdir，勿臆测）；旧 5 = `8650/8651/8652/8653/8654` → **核对官方 host↔workdir 后填**。
- ⚠️ **如实记录**：`8650–8654` 借用 **`t0002997` workdir**（非本账号）的**风险**。

**③ 改 MCP 客户端超时（第 2 条根因）**
- `~/.cline/data/settings/cline_mcp_settings.json` 的 `pyAether_MCP_server` 项：加/改 **`timeout` → `150000`（ms，对齐服务端 `SANDBOX_TIMEOUT=150s`）**。
- ⚠️ **先核对字段名与单位**（`timeout` / `requestTimeout`；秒 vs 毫秒）**再改**，**贴改动前后原文**（脱敏 token）。
- ⚠️ 这是**评测环境改动**（影响评测对象的 cline）⇒ **须在结果报告「披露」节写明**。

**④ 重启 + 核验**：按既定流程重启 `eda_fastmcp`；核验 `ss -lntp | grep 8090` + `grep -E 'PROXY_PORTS|SANDBOX_ENDPOINTS' .env`（**贴行**）。

**⑤ 开跑前自检（硬闸）**：对**新 8 端口**各 `run_code` 1 次 → **8/8 健康才开跑**；任一不健康 → **停、回报**（不得带病开跑）。

**⑥ 重跑 r2→r5（本块授权起动）**
- 依次 `r2_new → r3_new → r4_new → r5_new`；判据 **`timeout ≤ 10` 且 `Pass@1 ≥ 75%`**（每轮最多重跑 3 次）。
- **必带 instrumentation**：每次 `run_code` 记 **`port` + `latency(ms)` + `timeout?(Y/N)`** → 各轮产出 **「timeout × 端口」分布表**。
- 5/5 完成 → `[r1=88.0(保留), r2..r5]` 算 mean±std → 回填 5 张表锚点 → 进 C2。

**⑦ 产出**：本块下贴 —— ④ 核验行 + ⑤ 的 **8 端口自检表** + ⑥ 各轮 `Pass@1 / timeout` + **「timeout × 端口」表**。
**⑧ 归因要求**：本轮同时改 **2 个变量**（端口池 + 客户端 timeout）—— 若 `r2_new` 即达标（timeout≤10）则续跑；**若仍不达标**，须在报告中把两变量**分别归因**（可补做单变量对照）。

### 🆕 运维指令 · 2026-10-10（六）— ⚖️ 若 9 端口均健康 → **先判别「端口数是否真因」** → 再配全 9 端口重跑 r2–r5【已被 (七) 取代】

> **用户令（2026-10-10 晚）**：「**如果 9 个端口都没问题，那就把它们都配上，然后重跑 full 的 run2–run5 和后续评测**。请评估这个方法能否有效降低 timeout 概率。」
> **运维评估（先读，避免白跑不可归因）**：
> - **机制**：报错是 **cline 的 MCP 客户端 60s 超时**（`MCP error -32001 ... timed out after 60s`，客户端措辞），**不是**任务级 2500s 超时。
> - **加端口只在「端口级排队/争用」时有效**：当前评测并发 **`-p 8`** vs **仅 4 个端口** = **2:1 争用** —— 这是"加端口能救"的**唯一**机制。
> - **反证**：**`r1=88%` 就是在 4 个端口上跑出 0 timeout** ⇒ 端口数**不是充分解释**；更像**端点健康度 / 单次调用本身耗时**问题；且 MCP 服务端可能是**单进程**（`EDA_MCP_PORT=8090`，`0.0.0.0:8090`），若是瓶颈则加端口**无用**。
> - **环境注（2026-10-10 用户提示 · 澄清）**：`EDA_MCP_PORT=8090` 由用户在 36.15 `~/.bashrc` 设置。⚠️ **`~/.bashrc` 只对「交互式非登录 shell」自动生效** —— **ops 中继是「非交互 bash」，不读 `~/.bashrc`**（RUN_ID 29 重启 loop 时 `cline` 找不到，就是这一条）；**凡由中继/loop 启动的进程，须在启动处显式 `export`（或 `source ~/.bashrc` / `bash -l`）**，不能假设自动继承。**（RUN_ID 31 实测：中继 env `EDA_MCP_PORT=<UNSET>`；但 `.env` 有 `${EDA_MCP_PORT:=8090}` 兜底 + cline 的 `cline_mcp_settings.json` **硬编码 `http://10.251.36.15:8090/sse`** ⇒ 本例**无害**。）
> - **混淆**：本轮**同时删了 `PreToolUse` hook** ⇒ 变量不止一个，直接全量换 9 端口**无法归因**。
> - **风险**：`8650–8654` 是**别的账号 `t0002997` 的 workdir**（非我们 `e0031982`），且正是此前"坏掉"的那批。
> ⇒ **结论：不保证有效**；**必须先做判别实验**，否则 r2–r5 白跑。

**① 前置**：以 **(四)** 的 9 端口 `run_code` 健康结论为准 —— **未得结论前不进入本块**。

**② ⭐ 先验判别实验（必做，~30min，便宜）**
- 配置 A = **4 端口**（现状 `8663/8666/8667/8670`）；配置 B = **9 端口**（+ `8650/8651/8652/8653/8654`）。
- 每种配置做 **8 并发 × 30 次**最简 `run_code`（`print("ping")`）压测，记录**每次耗时**。
- 报每配置 **P50 / P95 延迟 + 超时率（>60s 次数）**。
- **判据**：B 相对 A，P95 或超时率**显著改善**（建议阈值：超时率 ↓ ≥50%）→ 端口争用成立 → 进 ③；
  **无显著差异 → 停，回报运维**（说明瓶颈在 MCP 服务端 / 端点慢 / 调用本身，**加端口无用**）。

**③ 若判别通过 → 配置 9 端口 + 重启 MCP**
- `.env`：`PROXY_PORTS=8663,8666,8667,8670,8650,8651,8652,8653,8654`；`SANDBOX_ENDPOINTS` 补全 **9 条映射**（新 4 = `e0031982_1~4`；旧 5 = **按 host 映射核对后填**）。
- 按既定流程重启 `eda_fastmcp`；核验 `.env` 生效（贴行）。
- ⚠️ **如实记录**：`8650–8654` = `t0002997` workdir 的**借用风险**；若判定不宜借用 → **只用 `e0031982` 系端口**（此时"加端口"退化为"无新增"，亦须如实报）。

**④ 重跑 r2→r5（本块授权起动；覆盖 (三)「不启新 run」与「不改 `.env`」）**
- 依次 `r2_new → r3_new → r4_new → r5_new`；判据不变：**`timeout ≤ 10` 且 `Pass@1 ≥ 75%`**（每轮最多重跑 3 次）。
- **必带 instrumentation**：每次 `run_code` 记录 **`port` + `latency(ms)` + `timeout?(Y/N)`**；各轮跑完产出 **「timeout × 端口」分布表** —— **否则无法验证本改动**。
- 5/5 完成 → `[r1=88.0(保留), r2..r5]` 算 mean±std → 回填 5 张表锚点 → 进 C2。

**⑤ 产出**：本块下贴 —— ② 的**判别表**（A vs B：P50/P95/超时率）+（若进 ③）④ 的**「timeout × 端口」表** + 各轮 `Pass@1 / timeout`。

### 🆕 运维指令 · 2026-10-10（四）— 🔬 **根因排查：连续多日评测 timeout**（是否 `run_code`？哪些端口 run_code 健康？）【最高优先】

> **用户令（2026-10-10 晚）**：「需要 zhulong loop **排查一下重复出现几天的评测的问题**，**超时是什么原因导致的，是 run_code 吗**，**是所有端口都有问题吗**，上述给到的端口 **run_code 有健康的吗**。」
> **运维已通过 ops relay（RUN_ID 29）先行处置**（agent 侧只需**确认**，勿重复）：① **删除** `~/.cline/hooks/PreToolUse`；② **停** r2_new2；③ **重启** zhulong loop（`SLEEP_WAIT` 保持 **1800s=30min**）。

**① 确认停（relay 已做）**：`pgrep '^bash scripts/run_cline_script'` 与 `pgrep run_eval.py` **均无输出**；`~/.cline/hooks/` 下 **无 `PreToolUse`**。

**② ⭐ 逐端口 `run_code` 健康测试（核心 —— 直接回答"哪些端口健康 / 是否全坏"）**
- 候选 **9 端口**：新 `8663/8666/8667/8670`（workdir `e0031982_1~4`）+ 旧 `8650/8651/8652/8653/8654`（`t0002997_1~4`）；`SANDBOX_HOST=10.129.32.75`。
- 每端口各发**最简 pyAether `run_code`**（`print("hello from <port>")`，**带正确 `host`/`lang`**，按 15:35 的 patch 口径）：
  - ✅ **健康** = response 非空 **且** error_log 空；
  - ❌ **不健康** = 超时 / response 空 / error_log 非空。
- **每端口重复 3 次**（探**间歇性**故障）；记录**每次耗时**（区分「秒级返回」vs「踩满 60s」）。
- ⚠️ 旧 8650–8654 若需测：先核对 `.env`/`exec_code.py` 的 host↔workdir 映射（**不改 `.env`**，只读）。

**③ ⭐ 超时根因（给**路径:行号**级证据 + 命令 + 原始输出）**
1. **量化**：从 `/tmp/ABL_full_*.log` 统计 `timeout`（总/MCP `32001`/`ACCESS RESTRICTED`/`Forbidden`/`host-error`）；**按端口**分组（若日志带端口）。
2. **是否 `run_code`**：超时**是否都发生在 `run_code`（MCP pyAether）调用**？有无**非 run_code** 的超时（模型服务/网关/grading）？各占多少 —— 给**样例 log 行**。
3. **是否所有端口都有问题**：把超时**关联到端口** → 「端口 X 贡献了 N 个 timeout」；指出**是否单端口故障**（对应 r2_new 的 23 个 gen-fail）。
4. **`60s` 从哪来**：MCP pyAether 的 60s 超时是**客户端**（哪个文件/哪个常量）还是**服务端**？为什么慢到 >60s（端口排队 / 沙盒冷启 / workdir 锁 / 反作弊 hook 延迟）？
5. **hook 影响**：对比**删 `PreToolUse` 前后**的 `ACCESS RESTRICTED` / timeout 计数；说明反作弊 hook 与 timeout 的因果关系（是真因还是无关）。
6. **历史对照**：`r1=88.0%(0 timeout)` vs `r2=59.5%(39)` vs `r3=63.3%` vs `r2_new=73.4%(timeout=4 / 23 gen-fail)` —— **变化点是什么**（沙盒/端口/模型服务/hook/负载）？

**④ 产出**：本块下贴两张表 —— ①【端口 × run_code 健康度（3 次）】；②【timeout 计数 × 阶段 × 端口】+ 根因结论（**命令 + 原始输出 + 路径:行号**）。
**⑤ 边界**：**只排查**，🚫 **排查完成前不得重启任何评测 run**；🚫 不改 `.env`。

### 🆕 运维指令 · 2026-10-10（三）— 🛑 先停 zhulong + 🔬 逐一实测沙盒端口（新 4 个 8663/8666/8667/8670 + 探旧 8650–8654）【本次唤醒优先动作 · 覆盖(二)】

> **用户令（2026-10-10 晚）**：
> 1. **zhulong 先停下来**；
> 2. **测试一下沙盒端口** —— 看 **4 个新端口（8663/8666/8667/8670）里是否某个有问题**（r2_new 73.4% 的 23 个 MCP timeout 疑似单端口故障）；
> 3. 另外**测试 `8650`–`8654` 之间是否有可用的沙盒端口**。
> **本条 `(三)` 覆盖 `(二)` 的「开跑」动作**：先停再测，**测完取证回来等运维裁定**，**不自动重启 r2**。

**① 立即停（本指令第一动作）**
- `kill -TERM` 当前 **r2_new2（retry#1）**（`/tmp/ABL_full_r2_new2.log` 对应的 `scripts/run_cline_script.sh` 进程组 + 其 child `run_eval.py`）；10s 未退 → `kill -KILL`。
- 确认 **`pgrep '^bash scripts/run_cline_script'` 与 `pgrep run_eval.py` 均无输出**（贴原始输出）。
- **r2_new2 判 ❌ 作废（人为中止，非有效成绩）**；**r1=88.0% 仍保留**。🚫 **停后不自动重启** r2/后续。

**② 逐端口实测（**核心**：不是 curl 端口可达，而是用 `run_code` MCP **真跑一次**）**
- 候选 = **9 个端口**：**新 4** = `8663`/`8666`/`8667`/`8670`（workdir `e0031982_1~4`）+ **旧 5** = `8650`/`8651`/`8652`/`8653`/`8654`（旧 range，workdir `t0002997_1~4`）。
- `SANDBOX_HOST = 10.129.32.75`。对**每个端口单独**发一个最简 pyAether 请求（如 `print("hello from port <P>")`）：
  - ✅ **通过判据**：**返回非空 response** 且 **error_log 为空**。
  - ❌ **不通过判据**：超时 / response 空 / error_log 非空 / 连接被拒。
- （可选交叉印证）`nc -zv 10.129.32.75 <port>` 或 `curl --noproxy '*'` 探连通性；**但以 `run_code` 实跑为准**（端口 OPEN ≠ 沙盒能跑代码）。
- ⚠️ 探旧 8650–8654 **仅作可用性测试**（`(二)` 曾写「8650-8654 已弃用」——本次是**测试**，**是否启用由运维裁定**，不改 `.env`）。

**③ 产出（本指令块下贴表）**

| 端口 | 组 | workdir | 连通(nc/curl) | `run_code` 实测 | error_log | 结论 |
|:--|:--|:--|:--|:--|:--|:--|
| 8663 | 新 | e0031982_1 | | | | ✅/❌ |
| 8666 | 新 | e0031982_2 | | | | ✅/❌ |
| 8667 | 新 | e0031982_3 | | | | ✅/❌ |
| 8670 | 新 | e0031982_4 | | | | ✅/❌ |
| 8650–8654 | 旧 | t0002997_1~4 | | | | 逐个 ✅/❌ |

- **必须明确**：① **4 个新端口里哪个（哪些）有问题**；② **8650–8654 里哪些可用**。

**④ 停后一并做**
- 更新 `run/MEMORY_ZHULONG.md`：`PHASE=blocked`（或 `standby`）、`r2_new2 = ❌作废(人为中止)`、**附上端口实测结论**、`WAITING=1`。
- **commit + push**（按常驻规程 `zhulong <阶段/轮次>: <一句话>`）。

**⑤ 边界**
- 🚫 **不启动任何新评测 run**（r2 及以后都不启）—— 端口结论回来、运维看过再定。
- 🚫 **不改 `.env`**（哪个端口先用由运维裁定）。
- ✅ 本指令只做三件事：**停 + 测 + 报**。

### 🆕 运维指令 · 2026-10-10（二）— 🔄 专属沙盒就绪：先测试新端口 → 保留 r1 锚点 → 重跑 r2→r3→r4→r5【已被(三)/(四)取代·已归档】
> ⎩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-10 20:49）。


### 🆕 运维指令 · 2026-10-10（一）— 🔄 切换专属沙盒 + C1.full 全部作废从头重测 r1→r5【已被(二)取代·历史】


### 🆕 运维指令 · 2026-10-09（五）— ✅ 沙盒已修复，可重跑 C1.full r4【已被 2026-10-10(一) 取代·已归档】
> ⎩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-10 20:49）。


### 🆕 运维指令 · 2026-10-09（四）— 🛑 沙盒坏了，r4 已被运维 kill，待命不要重跑【已被(五)取代·历史】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-10）。

### 🆕 运维指令 · 2026-10-09（三）— 🔄 C1.full r2/r3 复测（模型服务不稳定致大量 timeout）【已归档·被(四)取代】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-10）。

### 🆕 运维指令 · 2026-10-09（二）— ✅ 沙盒已就绪，可开跑 C1.full r4【已完成·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-10）。

### 🆕 运维指令 · 2026-10-09 — ✅ pro-fp4 403 已解决（换 key）+ 🚫 暂不启动 r4（沙盒重启中）【已完成·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-10）。


> **来源**：用户 2026-10-08 观察。`zhulong_loop.sh` 的 git fetch/push 经常超时，根因 = **loop 进程环境里没有 `https_proxy`**（脚本本身不 export 代理，完全继承启动 shell 的环境；而脚本只在调 cline 时 `env -u` 剥代理——内网网关不该走代理——但 **git 访问 GitHub 是外网，必须走代理**）。

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

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**：
   ```bash
   cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
   git pull --rebase --autostash origin main          # 先同步（这次用你当前 shell 的代理）
   pkill -f zhulong_loop.sh; sleep 3
   export https_proxy=http://172.19.92.23:13128
   export http_proxy=http://172.19.92.23:13128
   setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &
   sleep 4
   # 复核：新 loop 进程应带代理
   _NPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   tr '\0' '\n' < /proc/$_NPID/environ | grep -iE 'https_proxy'
   ```

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 🆕 运维指令 · 2026-10-08（一）— 📝 HTML 报告【已完成·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-08）。产物 `reports/report_2026-10-08_holiday.html`（21870B，8 节齐全，已 commit a4dc5c3c）。

### 🆕 运维指令 · 2026-10-05（八）— ops 中继恢复【已解决·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。ops relay alive ✅（每次唤醒复检）。

### 🆕 运维指令 · 2026-10-05（七）— 评测侧隔离 config dir【已落地·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。合并线 eval 用 `CLINE_CONFIG_DIR=.cline_eval_zhulong`；编排用 `--config .cline_zhulong`。

### 🆕 运维指令 · 2026-10-05（六）— 试验次序调换 B→C1→C2→S1【已生效·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前顺序 B→C1→C2→S1（§4 已同步）。

### 🆕 运维指令 · 2026-10-04（五）— legacy 组件 loop 保活【常驻·已稳定·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。legacy loop alive ✅（每次唤醒复检）。

### 🆕 运维指令 · 2026-10-04（四）— 正式起始点 C1.wo_retrieval R2【已越过·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前已推进至 C1.full r1。

### 🆕 运维指令 · 2026-10-04（三）— 中继已恢复 / loop RUN_ID 6 重启【已解决·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。

### 🚨 运维指令 · 2026-10-04（二）— 抢救 ops 中继【已解决·勿再执行·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。
### 🆕 运维指令 · 2026-10-04：环境迁移 + 合并执行方式 + ops 中继独立

> 本次把 4 个 phase（S1 保真度 / 组件 / S2 Φ / 模型）**合并进本单一任务书 + 单一 loop**，不再按 `ablation_run_conductor_serial.sh` 拆 3 个 task book + 4 个 loop。**执行顺序不变**（README §8）：S1 → 组件 → S2 Φ → 模型。

1. **环境（agent 最终跑在 36.15 服务器，必须用下表 `/nasdata/` 路径）**：
   - `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
   - `PAPER=/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/ZhuLong_DAC2027`（唯一可改 LaTeX 树）
   - `GIT_ROOT=/nasdata/app.e0031982/code/super_intelligence_2035`
   - **注意**：当前 2.12 开发机路径前缀为 `/nas_train/`（与 36.15 的 `/nasdata/` 独立挂载，互不关联）。旧 task book 中的 `/nasdata/` 路径在 36.15 上仍然有效，并非迁移关系。
2. **infra 前置校验（PHASE=init 首次启动前必做，不满足则 `WAITING=1` 原地等）**：
   - `df -h /home` 可用 **≥ ~8G**；四 shard 端口 **8664/8665/8653/8669 全 OPEN**；`run_code` 可正常执行（license 可用）。
   - 旧停摆根因即此三项，**没恢复就别开跑，跑出来也作废**。
3. **起始状态（运维在此填实）**：默认 `PHASE=init`，从 `STAGE=S1, CONFIG=omega_low, ROUND=1` 开始；若要延续旧 S1 进度，改填 `CONFIG=omega_low, ROUND=3`，并把 r1=81.6 / r2=82.3 写进 MEMORY 成绩表，r1/r2 不重跑。
4. **ops 中继通道已就绪**：`run/zhulong_ops_relay.sh` + `run/ops/{inbox,outbox,README}.md`。运维通过 git 下发 shell 命令（~20s 轮询），与 BaiZe ops 相互独立。启动命令见 `run/ops/README.md` 或本报告 §6。
   - ⚠️ 只有本区（运维指令区）的 ops 提及是写给人看的。**agent 不要碰 ops/ 目录**（中继专供运维下发命令，agent 写 MEMORY 和日常记录即可）。

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