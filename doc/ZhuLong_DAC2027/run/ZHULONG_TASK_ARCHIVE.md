# ZHULONG_TASK_ARCHIVE.md — ZhuLong（DAC2027）任务书归档（已闭合运维指令块）

> 本文件由 agent 维护（2026-10-06 用户裁定：任务书归档由 agent 自滚）。
> 归档原则：只「搬迁」已闭合内容，【原文】不动，不新增/不改写任何指令。
> 归档时间：2026-10-08 12:27 CST（任务书 39.6KB→超 32KB 阈值，搬出 8 个已闭合运维块至本文件）。

---

### 🆕 运维指令 · 2026-10-08（一）— 📝 写一份「国庆假期试验进展」HTML 报告【本次唤醒优先动作】

> **来源**：用户 2026-10-08 下达。国庆假期（约 10/01–10/08）期间本线持续推进，现需汇总成一份**可读的 HTML 报告**向用户汇报。**本动作优先于新一轮评测推进**（但**不打断正在跑的 `C1.wo_retrieval r5`**——若 r5 仍在跑，先正常巡检/收割，再写报告；报告里把 r5 标为「运行中/收割值待补」即可）。

**目标产物**：一份**自包含**（内联 CSS、无外部依赖、UTF-8）的 HTML 报告，路径 = `run/reports/report_2026-10-08_holiday.html`（`reports/` 目录不存在则自建）。中文撰写。

**数据来源（必须只读引用，不得臆造）**：
1. `run/MEMORY_ZHULONG.md` —— 状态头 / 执行看板 / 成绩记录表 / 操作流水。
2. `run/daily-memories/2026-10-0[1-8].md` —— 假期每日流水（关键事件、转折点）。
3. `run/ops/outbox.md` —— 中继回收的环境/进程诊断（infra 状态佐证）。
4. 本任务书 §0 速览 + 各运维块 —— 试验次序调换、legacy 接管等决策来源。

**报告必须包含的小节**：
1. **概览**：合并消融线设计（15 臂 × 5 轮 = 75 轮，串行 B→C1→C2→S1，回填 6 表 56 个 `[TBD]`）；冻结设置（EDA-Eval-PyAether 158 任务、Pass@1、单 trace、5 次独立运行 mean±std、主 backbone deepseek-v4-pro-fp4）。
2. **假期进度总览表**：15 臂逐行列出 `阶段/臂/轮次进度/N=5 mean±std/各轮原始值/状态`，**数字一字不改地抄成绩表**（已完成的填实数；`full`/C2/S1 未启动的标 ⬜ 待跑；`wo_retrieval` r5 若未收割标「运行中」）。
3. **Phase B（大模型消融）专题**：4 个 backbone（glm-5.2 / deepseek-v4-flash / kimi-k2.6-cloud / doubao-seed-2.0-pro-cloud）的结果与简评（含 flash 异常低分、std 偏大的说明）。
4. **C1（组件消融）专题**：pure_llm / rag / wo_retrieval / full 的进度与含义（pure_llm 复用 legacy、rag 本线重跑、wo_retrieval r5 进行中）。
5. **假期关键事件时间线**：按日期列出转折点（例如：pro-fp4 额度 403 阻塞 → 试验次序调换为先跑 Phase B；ops 中继抢救/重启；legacy 组件 loop 保活；`/home` 磁盘 99% 硬阻塞处置；编排模型切 glm-5.2；pro-fp4 恢复 HTTP 200 等）。**只写有 daily-memory / outbox 证据的事件**。
6. **基础设施状态**：磁盘（/nasdata 充裕、/home 99% 非阻断）、端口（8653/8664/8665/8669）、反作弊 hook（0 Forbidden）、ops 中继与 loop 存活情况。
7. **下一步**：C1.wo_retrieval r5 收割 → 算 mean±std → 切 C1.full 锚点 → C2(S2Φ) → S1(保真度)；以及尚待运维拍板的开放项（若有）。
8. **页脚**：生成时间（用你唤醒时的系统时间）、数据截止点（MEMORY 最后一次提交）、「数字来源：run/MEMORY_ZHULONG.md 成绩记录表」。

**样式要求**：表格有边框、斑马纹、表头深色底；Pass@1 数值右对齐；状态列用 emoji（✅/⬜/▶/⏸）；标题层级清晰；整体宽度 ≤ 1100px、居中。

**红线**：
- 🚫 **不得臆造任何数字**——所有 Pass@1 / std / 轮次值必须能在 `MEMORY_ZHULONG.md` 成绩记录表回溯；未测的显式标「待跑/运行中」。
- 🚫 **不得改动** `ops/` 下任何文件、不得动论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（报告不是回填 `[TBD]`）。
- 🚫 **不得**因写报告而 `git add -A`；只 add 报告文件本身。
- ✅ 报告写完**仍要遵守常驻规程**：更新心跳（`MEMORY_ZHULONG.md` 顶部 + 流水追加 1 行）+ 当日 `daily-memories/2026-10-08.md` + **自己 commit+push**（`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run/reports/report_2026-10-08_holiday.html doc/ZhuLong_DAC2027/run/MEMORY_ZHULONG.md doc/ZhuLong_DAC2027/run/daily-memories/2026-10-08.md` → `git commit -m "zhulong 报告: 国庆假期试验进展 HTML"` → `git push origin main`）。push 失败重试 1 次，仍失败把报错写进心跳、下轮首件事补推。
- ✅ 若 `C1.wo_retrieval r5` 在你唤醒时已可收割，**先收割记成绩再写报告**（让报告里的 wo_retrieval 行尽可能完整）；若仍在跑则按上文标「运行中」。

### 🆕 运维指令 · 2026-10-05（八）— 🚑【优先】请你排查并恢复 ops 中继

**背景**：36.15 的 `zhulong_ops_relay.sh` **自 11:04（RUN_ID 20）后不再响应**（`inbox.md` 已置 `RUN_ID 21`，1 小时+ 未执行）；而 **GitHub 通道本身是通的**（运维与本机都能 `git fetch`）。→ 大概率**中继进程已死/卡住**（很可能是启动时没带 `setsid`，随 ssh 会话断开被带走）。**运维无法登录 36.15，故请你（agent）代为排查并恢复——这是本轮优先动作（先于 Phase B 推进）。**

**步骤**：
1. 查活：`pgrep -af zhulong_ops_relay.sh | cut -c1-140`；记下 `/tmp/zhulong_ops_relay.log` 尾 20 行、`run/ops/.last_run_id`。
2. 测网：`cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run && git pull --rebase --autostash; timeout 60 git fetch origin && echo FETCH_OK || echo FETCH_FAIL`。
3. 若中继**不在**（或 `FETCH_OK` 但中继不动），**用带 `setsid` 的姿势重启**：
   ```bash
   cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
   pkill -f zhulong_ops_relay.sh; sleep 2
   setsid bash zhulong_ops_relay.sh > /tmp/zhulong_ops_relay.log 2>&1 < /dev/null &
   sleep 3
   pgrep -af zhulong_ops_relay.sh | cut -c1-140
   tail -n 8 /tmp/zhulong_ops_relay.log
   ```
4. 复核：`ops/.last_run_id` 应在 1–2 分钟内**变为 21**（中继补跑 `RUN_ID 21`）。
5. **回报**：把以上输出写进 `MEMORY_ZHULONG.md` 操作流水（含新 PID / 时间戳）。

**红线**：① 不改 `ops/` 里的文件内容；② 不动 legacy（`/nasdata/app.e0031982/code/ZhuLong_DAC2027/`）；③ 重启中继**必须带 `setsid` + stdio 重定向**，否则会再随会话断开而死。

### 🆕 运维指令 · 2026-10-05（七）— 🧩 评测侧也隔离 config dir（合并线 ↔ legacy 各干各的）

> **目标**：合并线跑 eval 时，防作弊 hook 只影响**它自己的评测对象**，**不再落进共享的 `~/.cline/hooks`** → legacy 的编排 agent 不被误伤 → **两条线可真正并跑**。

**运维正在落地**：给 `run_cli.sh` 增加 `CLINE_CONFIG_DIR` 支持（hook 装到 `$CLINE_CONFIG_DIR/hooks/`，默认仍 `$HOME/.cline` → legacy 行为不变）；并建 `/nasdata/app.e0031982/.cline_eval_zhulong`。

**落地后，你（agent）的动作**：**起 eval 前** `export CLINE_CONFIG_DIR=/nasdata/app.e0031982/.cline_eval_zhulong`；**合并线评测模型的 `cline auth` 也要写这个目录**（即 `cline --config "$CLINE_CONFIG_DIR" auth …`）。

**红线**：① **不要**给**编排 agent 自己**设 `CLINE_CONFIG_DIR`（编排仍用 `--config /nasdata/app.e0031982/.cline_zhulong`）；② **不要**碰 `~/.cline`（legacy 仍用它）。

**落地前**：（五）·5 仍然有效 —— **起 eval 前先确认 legacy 不在 mid-eval**。

### 🆕 运维指令 · 2026-10-05（六）— 🔄 试验次序调换：先跑 Phase B（大模型消融）【运维追认】

> **来源**：**用户在 36.15 现场下发的安排**（2026-10-05）。此前该条由 agent 代记于本区，现由**运维正式追认并接管署名**——**本区今后只由运维修改，agent 不得再改本节**。
>
> **生效范围**：**取代（四）的「从 `C1.wo_retrieval R2` 起跑」**（见下第 3 点）；与（五）「legacy 保活」不冲突。

**背景**：`deepseek-v4-pro-fp4` 额度 HTTP 403 阻塞 C1/wo_retrieval 无法推进，而 Phase B 的 4 个模型（glm-5.2 / deepseek-v4-flash / kimi-k2.6-cloud / doubao-seed-2.0-pro-cloud）均使用独立 key/endpoint，完全不受 pro-fp4 限制。→ **将 Phase B 提到最前**。

**新顺序**：**B（大模型消融）→ C1（组件）→ C2（S2 Φ）→ S1（保真度）**。

**注意**：
1. Phase B 使用 **full 配置**（检索开 + sandbox 开），不切 `set_ablation`。每个模型仅需 `cline auth` 切换 key/model。
2. 从 Phase B 切到 C1.pure_llm 时，必须先执行 `scripts/set_ablation.py pure_llm` + `stop.sh && start.sh`。
3. **（四）中 `C1.wo_retrieval R2` 起始点暂缓**，标记为 ⏸（暂停），待 Phase B 完成 + pro-fp4 恢复后重试。
4. legacy 组件 loop（PID 2455466）保持运行，不干扰。**并跑前提**：见（七）——**合并线的 eval 与 legacy 的 eval 需各自独立 cline 配置目录**，隔离落地前，起 eval 前先确认 legacy 不在 mid-eval。
5. Phase B 推进逻辑按 `ablation_run_task_model_full.md` §推进逻辑：每个模型跑 5 轮 → 从 glm-5.2 开始，依次 deepseek-v4-flash → kimi-k2.6-cloud → doubao-seed-2.0-pro-cloud → 完成后切 C1。



### 🆕 运维指令 · 2026-10-04（五）— 🚑【优先·补救】若 legacy 组件 loop 没在跑，请把它拉起来

> ⚠️ **本节优先于一切评测推进**；并**部分取代（四）**——（四）里「运维停 legacy」的动作**作废**。

**背景**：运维今晚误把 legacy 组件 loop 的**启停**与**中继操作**耦合在同一块里，**可能已把它停掉**；而运维在家、3 天后才能登机。请你（agent）**在本轮唤醒时代为检查并恢复它**：

1. 检查：`pgrep -af 'ablation_run_loop_component_s2_full.sh'`
2. **若没有在跑**，拉起：
   ```bash
   cd /nasdata/app.e0031982/code/ZhuLong_DAC2027/run
   setsid bash ablation_run_loop_component_s2_full.sh > /tmp/ablation_loop_component_s2_full.log 2>&1 < /dev/null &
   ```
3. 复核进程（`pgrep -af ...` 有输出即成功），并在 `MEMORY_ZHULONG.md` 操作流水追加一条（写 PID + 时间）。
4. **红线**：不要碰 `ablation_run_conductor_serial.sh`、不要动任何**正在跑的 eval**、**不要改** `/nasdata/app.e0031982/code/ZhuLong_DAC2027/`（只读 legacy 副本）里的任何文件。
5. **在你确认 legacy 已恢复后，本轮不要启动合并线自己的 eval**（避免与 legacy 抢同一套 infra：eda_fastmcp / MCP / `.env` / 端口）；**先把 legacy 保住**，它空转或跑完再说。

> ⏸ **接管暂缓**：在运维重新拍板前，**以"保住 legacy 产出"为先**（它没跑就拉起来）。合并线自身若 infra 就绪，照（四）的起始点 `C1.wo_retrieval R2` 正常推进即可。

### 🆕 运维指令 · 2026-10-04（四）— 🎯 正式起始点 = `C1.wo_retrieval R2`（接管 legacy + 复用其数据）

**背景**：用户拍板 → **由本合并线接管** legacy 组件线（`/nasdata/app.e0031982/code/ZhuLong_DAC2027`，**非 git**）。运维动作：① 停其两进程（`ablation_run_loop_component_s2_full.sh` + `ablation_run_conductor_serial.sh`）；② 收割其有效数据；③ 本线从下述起始点续跑。

**✅ 起始点（运维已填实，你按此推进）**：
- `STAGE=C1` · `CONFIG=wo_retrieval` · `ROUND=2` · `PHASE=running`。
- **S1 段跳过**（无 S1 臂要跑/已有旧值）。
- **C1 组件**：`pure_llm ×5 = 10.5±1.9%` **复用 legacy**（已入成绩表）；`rag ×5` legacy 值（68.2±7.4%）**作废**（系 BM25 降级态）→ **须在本线重跑**；`wo_retrieval` **r1=74.1% 复用 legacy，从 r2 续跑到 r5**；`full` 照原计划。
- **C2 S2Φ** 与 **B 模型** 照原计划。

**🔓 `/home` 门槛放宽**：RUN_ID 4 已证我方产物/缓存（`~/eda_code_eval`、`~/.cache` 等）实为 **symlink → `/nasdata`**，`/home` 满主因是别的用户。→ **不再以 `/home ≥8G` 作硬阻断**；改为校验「`/nasdata` 可写 + 四端口 8664/8665/8653/8669 OPEN + `run_code` 可用（license）。

**🔒 本线 cline 配置已隔离**：`zhulong_loop.sh` 已加 `--config /nasdata/app.e0031982/.cline_zhulong`（RUN_ID 17 实测：评测期防作弊 hook 不再拦编排 agent）。**你无需处理。**

**⚠️ 仍须遵守**：反作弊 hook 是冻结变量、每批开跑前 canary；`.env` 切臂串行 `&&`；评测仍走 `run_cli.sh` 原样流程（其 hook 装到 `~/.cline/hooks` 只作用于评测对象，勿改）。

### 🆕 运维指令 · 2026-10-04（三）— ✅ 中继已恢复（**勿再抢救**）；loop 由运维经 RUN_ID 6 重启

> **运维实测（RUN_ID 5，2026-10-04 21:43:20，exit=0，见 `run/ops/outbox.md`）**：
> - ✅ **ops 中继活着且健康**：RUN_ID 1–5 全部 `executed, exit=0`。**下方「（二）抢救中继」<u>已作废、勿再执行</u>**（当时系误判：heavy 版其实已于 17:05:57 跑完，只是 `push` 反复失败在重试）。
> - 🔴 **loop 仍是旧版、静默失效**：`/tmp/zhulong_loop.log` 每次唤醒都 `error: unknown option '-b'`（累计 **352** 次），cline **从未真正运行 → agent 从未被唤醒**。磁盘脚本已是新版（无 `-b`），须**重启 loop 进程**才生效 —— 运维将经 **RUN_ID 6** 直接重启，**你无需操作**。
> - `/home` 仍 **99% / 6G**；但 RUN_ID 4 已证：我方输出/缓存（`~/eda_code_eval`、`~/.cache` 等）实为 **symlink → `/nasdata`**（真实 5.7G 在 `/nasdata`），`/home` 满的主因是**别的用户**。

**你（agent）被唤醒后：直接跳到 §7 常规流程。** infra 校验遇 `/home` 满时，请**如实记录「我方产物实际落 `/nasdata`」**并**保持 `WAITING=1` 原地等**；是否放宽 `/home ≥8G` 硬门槛**待运维拍板**。**不要改 `ops/` 文件。**

### 🚨 运维指令 · 2026-10-04（二）—【已解决 · 勿再执行】抢救 ops 中继

> **背景**：运维侧下发 `RUN_ID 4` 时用了会卡死的命令（`du -sh -L` 跟随 symlink 进 `/nasdata` 大树 + **未加 `timeout`** 的 `df`）→ `zhulong_ops_relay.sh` **卡死**（`timeout` 只杀 leader、子进程占住管道 → 中继读不到 EOF，`.last_run_id` 停摆）。
> **运维人员当前不在公司、无法登录服务器**，因此**请你（agent）代为把中继救回来**。

**⏱ 请把本动作放在<u>一切评测推进之前</u>：先做下面 3 步，做完再回到 §7 的常规流程。**
（本节**明确授权**你重启中继进程 —— 尽管既有指令说"agent 不要碰 ops/"，**本次是唯一例外**；但仍**不要修改 `ops/` 里的文件内容**，那是运维的通道。）

**步骤 1｜杀掉卡死的中继及其残留子进程**
```bash
pkill -f zhulong_ops_relay.sh
pkill -f 'du -sh -L' 2>/dev/null || true
sleep 3
ps -eo pid=,ppid=,etimes=,args= | grep -E 'zhulong_ops_relay|du -sh' | grep -v grep | cut -c1-140
```
> 判据：**最后一条无输出** = 已清干净（若仍有 `bash zhulong_ops_relay.sh`，再 `pkill -f` 一次）。

**步骤 2｜按 `run/ops/README.md §2` 重启中继（36.15 用 `/nasdata/` 前缀）**
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
git pull --rebase --autostash
setsid bash zhulong_ops_relay.sh > /tmp/zhulong_ops_relay.log 2>&1 < /dev/null &
sleep 3
pgrep -af zhulong_ops_relay.sh | cut -c1-140
tail -n 6 /tmp/zhulong_ops_relay.log
```
> 判据：出现**新的** `bash zhulong_ops_relay.sh` 进程（`ppid=1`），且日志有 `[zhulong-relay] ... started.`。

**步骤 3｜回报（在 `MEMORY_ZHULONG.md` 的「操作流水」追加一条）**
- 写明：**中继已重启** · 新 PID · `/tmp/zhulong_ops_relay.log` 尾行 · 时间。
- **做完这 3 步即算完成本动作**，之后继续你原本的流程。

> ✅ 中继一重启，它会**自动**发现 `run/ops/inbox.md` 里的 `RUN_ID: 4`（**轻量版**，已由运维改成全 `timeout`）并执行 —— **你无需手动触发，也不要改 inbox**。

**（可选，仅在你确有把握时做）修 `-b` 的 loop**
- 已知：**运行中的 `zhulong_loop.sh` 进程是旧版**，cline 调用带**非法 `-b`** → `error: unknown option '-b'`；而**磁盘上的脚本已是新版（无 `-b`）**。bash 已把旧脚本整段读进内存，**改文件对它无效 → 只有重启 loop 进程才生效**。
- 你若判断"自己当前之所以能跑，说明 loop 已正常"，**就不要动它**；若确认日志仍在刷 `unknown option '-b'`，可（在**中继救活之后**）执行：
```bash
pkill -f zhulong_loop.sh; sleep 2
setsid bash /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &
```
- ⚠️ 重启 loop 会**中断你自己的当前会话**（你正是被它唤醒的）——**拿不准就留给运维，只做中继那 3 步**。


---

## 2026-10-10 归档：从 ZHULONG_TASK.md 搬入 4 个已闭合运维块（原文不改）

### 🆕 运维指令 · 2026-10-09（四）— 🛑 沙盒坏了，r4 已被运维 kill，待命不要重跑【已被(五)取代·历史】

> **来源**：用户 2026-10-09 17:00 通知「沙盒坏了，把 r4 停下来，待命」。
> **已执行**：运维已通过 ops 中继 RUN_ID 25 kill 了 r4 进程树（PID 3302534 + run_eval.py 子进程）。

**本次唤醒的动作（按顺序）**：

1. **确认 r4 已被 kill**：`pgrep '^bash scripts/run_cline_script'` → 期望**无输出**（r4 已被运维 kill）。若有残留 → `kill -KILL` 清理，记 MEMORY。

2. **🚫 不要重跑 r4**：沙盒坏了（r4 grading 异常慢 13×+，log 沉默 2h+），用户要求**待命**。**不启动任何 eval、不 run `scripts/run_cline_script`**。

3. **更新 MEMORY 状态头**：
   - `PHASE` → **`standby`**（沙盒坏了，r4 已 kill，待命等运维通知）
   - `WAITING` → **1**
   - 成绩表 `C1.full` 行：r4 状态改为 **「❌作废（沙盒坏了，运维已 kill，待命）」**
   - **下轮第一件事**改为：检查运维指令区是否有「沙盒已修复·可重跑 r4」通知 → 有则重跑 r4（四 override + 新 key），无则继续 `WAITING=1` 待命。

4. **commit + push**（按常驻规程）。

**红线**：
- 🚫 **不要重跑 r4/r5**（沙盒坏了，等运维修复通知）。
- 🚫 **不要启动任何 eval**。
- ✅ r1=88.0% **保留**；r2/r3 仍 **作废待复测**（等沙盒修复后一起跑）。
- ✅ 保持新 key `e13f4f37` + `deepseek-v4-pro-fp4` + `/cloud/v1`。


### 🆕 运维指令 · 2026-10-09（三）— 🔄 C1.full r2/r3 复测（模型服务不稳定致大量 timeout）【已归档·被(四)取代】

> **来源**：用户 2026-10-09 观察。C1.full 锚点 r1=88.0%（0 timeout）vs r2=59.5%（**39 timeouts**）vs r3=63.3%，成绩剧烈波动 = **模型服务不稳定**（大量 timeout 拉低通过率），**非 full 臂真实能力**。用户要求复测 r2/r3。
> **当前状态**：r4 正在跑（batch `b2026_1009_094504`，PID `3302534`，09:45 启动），**不要打断**。

**判定**：
- ✅ r1=88.0%（139/158, 0 timeout）= **有效，保留**（服务正常期跑的）
- ❌ r2=59.5%（94/158, **39 timeouts**）= **作废，需复测**（服务不稳定）
- ❌ r3=63.3%（100/158, 成绩异常低）= **作废，需复测**（疑似服务不稳定，收割时确认 timeout 数量）
- ⏳ r4 = 正在跑，收割后按下方判据判定

**复测流程（r4 跑完后按顺序执行）**：

1. **收割 r4**（`pgrep` 无输出后 `grep -E 'pass \(|PASS_RATE|timeout' /tmp/ABL_full_r4.log | tail -10`）：
   - 记录 r4 成绩 + **timeout 数量**。
   - **判据**：timeout ≤10 **且** 成绩 ≥75% → r4 有效，说明服务已稳定 → 进入步骤 2。
   - 若 r4 timeout >10 或成绩 <75% → **服务仍不稳定** → r4 也作废 → 在 MEMORY 记「r4 仍有 X timeouts，服务不稳定」→ `WAITING=1`，等下轮复检服务稳定性（`curl` 新 key 直连测延迟 + 连续 3 次确认无 timeout）→ 服务稳定后从 r4 重跑。

2. **重跑 r2**（r4 判定有效后）：
   - 同臂 `full`，四 override 齐全（`EVAL_FW_DIR` + `CLI_DATA_DIR=.cline_prof4_eval/data` + `PYTHON` + `https_proxy`），新 key `e13f4f37` + `/cloud/v1` + `deepseek-v4-pro-fp4`。
   - batch ID 记为 `r2-retest`，log 记为 `/tmp/ABL_full_r2_retest.log`。
   - 收割后检查 timeout：**timeout ≤10 且成绩 ≥75%** → r2' 有效，替换 r2=59.5%。若 timeout >10 或成绩 <75% → 重跑（最多 3 次），3 次仍不达标 → 在 MEMORY 记「r2 复测 3 次仍未达标（X timeouts, Y%）」→ 暂停，等运维指示。

3. **重跑 r3**（r2' 有效后）：
   - 同上配置，batch ID 记为 `r3-retest`，log `/tmp/ABL_full_r3_retest.log`。
   - 同样判据：timeout ≤10 且成绩 ≥75% → r3' 有效，替换 r3=63.3%。否则重跑（最多 3 次）。

4. **跑 r5**（r3' 有效后）：
   - 同上配置，batch ID 记为 `r5`。
   - 同样判据：timeout ≤10 且成绩 ≥75% → r5 有效。

5. **5/5 完成 → 算 mean±std**：
   - 最终 5 个有效 run = [r1=88.0%, r2', r3', r4, r5]（r2' r3' 为复测值，替换原 r2/r3）。
   - `PHASE=just_finished` → 回填 5 张表锚点行 → 进入 C2。

**更新 MEMORY（每次收割后）**：
- 成绩表 `C1.full` 行：r2 标注「❌作废(39 timeouts)→复测中」→ 复测后替换为 r2'=X%（Y timeouts）；r3 同理。
- **下轮第一件事**：`pgrep '^bash scripts/run_cline_script'` → 有输出 = 巡检退出；无输出 = 按上方流程收割当前轮次 → 检查 timeout → 按判据决定下一步。
- 每轮收割**必须记录 timeout 数量**（grep `timeout` 或 `timed?out` 或 log 里的 timeout 统计行）。

**红线**：
- ✅ r4 正在跑，**不打断**。
- 🚫 r2=59.5% / r3=63.3% **作废**，不参与最终 mean±std（服务不稳定）。
- ✅ r1=88.0% **保留**（0 timeout，服务正常）。
- ✅ 每轮判据 = timeout ≤10 **且** 成绩 ≥75%（两个条件都满足才算有效）。
- 🚫 若复测 3 次仍不达标 → **不要继续盲跑**，暂停记 MEMORY 等运维指示。
- 🚫 仍保持新 key `e13f4f37` + `deepseek-v4-pro-fp4` + `/cloud/v1`（不要回退）。


### 🆕 运维指令 · 2026-10-09（二）— ✅ 沙盒已就绪，可开跑 C1.full r4【已完成·已归档】

> **来源**：用户 2026-10-09 通知「沙盒重启完成，可以继续」。
> **前提**：上一条指令（pro-fp4 key 已恢复）应已被 agent 执行完毕——eval backbone 已用新 key `e13f4f37` auth、`PHASE=ready`、`WAITING=1`。

**本次唤醒的动作（按顺序）**：

1. **前置复检（3 项，全过才开跑）**：
   - (a) `curl --noproxy '*'` 新 key 直连 pro-fp4 `chat/completions` → 确认 **HTTP 200 + 真 JSON**（`model: deepseek-v4-pro-260813`）。若仍 403 → 不开跑，回 `WAITING=1`，在 MEMORY 记「pro-fp4 又 403」。
   - (b) 沙盒端口可达：`curl -s -o /dev/null -w '%{http_code}' http://10.129.32.75:8650`（及 8651/8652/8654）→ 期望 **404**（可达）。若全 timeout/拒绝 → 沙盒未就绪，不开跑，回 `WAITING=1`。
   - (c) eval IDLE：`pgrep '^bash scripts/run_cline_script'` → 期望**无输出**（无残留 eval）。若有残留 → 先等其结束，不开跑。

2. **启动 C1.full r4**（三项复检全过后）：
   - 切臂配置（若尚未切到 `full`）：`set_ablation` → `full`（run_code ON + 检索 ON + self-expl ON = 全开）。
   - 启动 eval，**四 override 必须齐全**（r2 曾因缺这些而全 Forbidden）：
     ```
     EVAL_FW_DIR=<eda_fastmcp 路径>
     CLI_DATA_DIR=.cline_prof4_eval/data   # eval 隔离 config dir（新 key auth 写入处）
     PYTHON=<正确 python 路径>
     https_proxy=http://172.19.92.23:13128  # git push 需要
     ```
   - 命令格式同前序轮次（`scripts/run_cline_script.sh` + `-p 8 -n` + 全量 158 题）。
   - 记录 batch ID + PID 到 MEMORY。

3. **更新 MEMORY**：
   - `PHASE` → `running`
   - `WAITING` → `1`（eval 运行中，等下轮收割）
   - `ROUND` → `4`（已是 4，确认不变）
   - 成绩表 `C1.full` 行：r4 状态 → **「运行中（batch XXX, PID XXX）」**
   - **下轮第一件事**：`pgrep '^bash scripts/run_cline_script'` → 有输出则巡检（不动作退出）；无输出则 `grep PASS_RATE` 收割 r4 → 记成绩 → 启 r5 → 5/5 后算 mean±std → `PHASE=just_finished` → 回填 5 张表锚点行 → 进入 C2。

4. **commit + push**（按常驻规程）。

**红线**：
- ✅ 沙盒**已就绪**，可以开跑（用户已确认）。
- 🚫 仍保持 `deepseek-v4-pro-fp4` + `/cloud/v1` + 新 key `e13f4f37`（不要回退旧 key、不要换模型名）。
- ✅ r1/r2/r3 全部有效，只跑 r4 → r5。
- 🚫 三项前置复检任一不过 → **不开跑**，回 `WAITING=1` 并在 MEMORY 记原因。


### 🆕 运维指令 · 2026-10-09 — ✅ pro-fp4 403 已解决（换 key）+ 🚫 暂不启动 r4（沙盒重启中）【已完成·已归档】

> **来源**：用户 2026-10-09。经 ops 中继 RUN_ID 23 在 36.15 实测（6 组合 curl `--noproxy '*'` 直连），已确认 403 根因 = **旧 key 额度耗尽**（非模型级、非 endpoint 级）。新 key 可恢复 pro-fp4。

**实测证据**（`run/ops/outbox.md` RUN_ID 23，2026-10-09 09:06:53）：

| # | key | model | endpoint | HTTP | 网关返回 model |
|:--|:--|:--|:--|:--|:--|
| ① | 新 `e13f4f37` | pro-cloud | /cloud/v1 | **200** ✅ | `deepseek-v4-pro-260813` |
| ② | 新 `e13f4f37` | **pro-fp4** | /cloud/v1 | **200** ✅ | `deepseek-v4-pro-260813` |
| ③ | 新 `e13f4f37` | pro-fp4 | /v1 | 403 ❌ | — |
| ④ | 旧 `c2759d74` | pro-fp4 | /cloud/v1 | 403 ❌ | — |
| ⑤ | 旧 `c2759d74` | pro-fp4 | /v1 | 403 ❌ | — |

**关键结论**：
1. **组合 ② = 200** → 新 key + **原模型名 `deepseek-v4-pro-fp4`** + **原 endpoint `/cloud/v1`** 即可恢复。**模型名和 endpoint 都不用改**，只换 key。
2. 网关对 pro-cloud 和 pro-fp4 返回的 `model` 字段**都是 `deepseek-v4-pro-260813`** → **同一个后端模型**，r1/r2/r3（均用 pro-fp4）**全部保持有效**，无需重跑。
3. `/v1` 端点对两个 key 都 403 → **必须用 `/cloud/v1`**。

**本次唤醒的动作（按顺序）**：

1. **用新 key 重新 `cline auth` eval backbone**（写入 eval 隔离 config dir，与 Phase B 同机制）：
   ```bash
   cline auth -p openai \
     -k 02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e \
     -b http://agi-gateway.cxmt.com/cloud/v1 \
     -m deepseek-v4-pro-fp4
   ```
   - ⚠️ 与 Phase B 同理：auth 写入 eval 侧隔离 config dir（`CLI_DATA_DIR=.cline_prof4_eval/data` 或你实际用的隔离目录），**不要污染编排 agent 的 `~/.cline`**。
   - auth 完成后，用新 key `curl --noproxy '*'` 直连复检 pro-fp4 `chat/completions` → 确认 **HTTP 200 + 真 JSON**（应看到 `model: deepseek-v4-pro-260813`）。

2. **🚫 暂不启动 r4**：用户告知**沙盒（sandbox）正在重启**，此刻启动评测会失败。**只做 auth + 复检 + 更新 MEMORY，不启动 eval、不 run `scripts/run_cline_script`。**

3. **更新 MEMORY 状态头**：
   - `基座` 行：eval backbone `deepseek-v4-pro-fp4` → **已恢复 HTTP 200（新 key `e13f4f37`）✅**
   - `PHASE`：从 `blocked` 改为 **`ready`（pro-fp4 已恢复，但沙盒重启中，等运维通知开跑）**
   - `WAITING`：保持 **1**（等运维通知沙盒就绪后再启动 r4）
   - `ERROR_COUNT`：不变
   - 成绩表 `C1.full` 行：r4 状态改为 **「待启动（key 已恢复，沙盒重启中，等运维通知）」**
   - **下轮第一件事**改为：`curl --noproxy '*'` 新 key 直连 pro-fp4 → 确认仍 200 → **检查运维指令区是否有「沙盒就绪·可开跑」通知** → 有则重跑 r4（四 override：`EVAL_FW_DIR` + `CLI_DATA_DIR=.cline_prof4_eval/data` + `PYTHON` + `https_proxy`），无则继续 WAITING=1。

4. **commit + push**（按常驻规程）：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run doc/ZhuLong_DAC2027/ZhuLong_DAC2027` → `git commit -m "zhulong C1.full: pro-fp4 key 已恢复(HTTP 200)→PHASE=ready, 沙盒重启中暂不启动r4"` → `git push origin main`。

**红线**：
- 🚫 **不要启动 r4/r5**（沙盒重启中，会失败作废）。
- 🚫 **不要改模型名**（保持 `deepseek-v4-pro-fp4`，网关已证实 200）。
- 🚫 **不要用 `/v1` 端点**（403）。
- ✅ r1/r2/r3 **全部有效**（同一后端模型 `deepseek-v4-pro-260813`），无需重跑。
- ✅ 等运维在指令区发「沙盒就绪·可开跑」通知后再启动 r4。




---

## 运维指令 · 2026-10-10（二）— 🔄 专属沙盒就绪：先测试新端口 → 保留 r1 锚点 → 重跑 r2→r3→r4→r5【已被(三)/(四)取代·归档 2026-10-10 20:49】

> **来源**：用户 2026-10-10 通知「4 个端口都配置好了，现在重启 full 的 r2-r5 以及后续试验，可以先测试一下」。
> **核心决策**：**r1=88.0% 保留作锚点**（0 timeout、沙盒正常时跑的，不受旧沙盒间歇故障影响）。**只重跑 r2/r3/r4/r5**（均在旧不稳定沙盒上跑过，全部作废）。先做**沙盒端口实测**（非 curl 端口可达，而是**实跑一次 run_code** 确认沙盒能执行代码），全过才启动 r2。
> **已执行**：运维已改 `.env`（`PROXY_PORTS=8663,8666,8667,8670` + `SANDBOX_ENDPOINTS=8663:e0031982_1,8666:e0031982_2,8667:e0031982_3,8670:e0031982_4`）；ops RUN_ID 27/28 已 kill r2-retest#4/#5 + .env 已验证为新端口。
> **取代**：2026-10-10(一)「全部作废从 r1 开始」**作废**——改为本条「保留 r1，重跑 r2-r5」。所有 2026-10-09 指令降级历史。

**本次唤醒的动作（按顺序）**：

1. **确认 eval IDLE**：`pgrep '^bash scripts/run_cline_script'` → 期望**无输出**。若有残留 → `kill -KILL` 清理。

2. **三项前置复检（全过才开跑）**：
   - ① **pro-fp4 直连 200**：新 key `e13f4f37` + `deepseek-v4-pro-fp4` + `/cloud/v1` → HTTP 200 ✅（ops RUN_ID 28 已验证 HTTP=200）
   - ② **新专属沙盒端口实测**（**重点**——不是 curl 端口可达，而是**实跑一次 run_code**）：
     - `.env` 已改为 `8663/8666/8667/8670` @ `10.129.32.75`（workdir `e0031982_1~4`）。
     - **实测方法**：用 `run_code` MCP 工具向**每个端口**发一个最简 pyAether 请求（如 `print("hello from port 8663")`），确认**返回非空 response 且 error_log 为空**。4 端口逐一测。
     - **判据**：4/4 端口均能执行代码并返回正常 response → ✅ 通过；任一端口返回空/超时/error → ❌ 不通过 → `WAITING=1` 报告哪个端口挂了，等运维。
   - ③ **eval IDLE**：`pgrep '^bash scripts/run_cline_script'` 无输出 ✅

3. **沙盒实测全过 → 更新 MEMORY 状态头**：
   - `ROUND` → **2**（从 r2 开始重跑，r1 保留）
   - `PHASE` → **`running`**
   - `WAITING` → **1**
   - 成绩表 `C1.full` 行：
     - **r1=88.0% ✅ 保留**（锚点，不动）
     - **r2=59.5% / r2-retest#1~#5 / r3=63.3% / r4=81.0% → 全部标 ❌作废·换专属沙盒重测**
   - 注明：旧沙盒 8650-8654 已弃用，新沙盒 8663/8666/8667/8670 workdir e0031982_1~4

4. **启动 C1.full r2 重测**（r2-retest on new sandbox，四 override 必带）：
   ```bash
   cd /nasdata/app.e0031982/code/eda_fastmcp
   export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
   export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data
   export PYTHON=/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python
   export https_proxy=http://172.19.92.23:13128
   setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_full_r2_new.log 2>&1 < /dev/null &
   ```
   - 启动后立刻核验：① 四 override 在 `/proc/<pid>/environ` 生效；② `.env` 读到新端口 8663/8666/8667/8670（不是旧 8650-8654）；③ 0 Forbidden。

5. **canary**：本批开跑前确认反作弊 hook live（一次应被拒的调用确实被拒；未被拒 → 立即停、本批作废）。

6. **commit + push**。

**r2 收割后 → 依次推进 r3→r4→r5**：
- 收割：`grep -E 'pass \\(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r2_new.log | tail -10` → 记 Pass@1 + timeout。
- **判据**：`timeout ≤ 10 且 Pass@1 ≥ 75%` → 有效 → 启下一轮（log `/tmp/ABL_full_r3_new.log` → `r4_new` → `r5_new`）。
- 每轮同判据，**最多重跑 3 次**不达标 → 暂停 `WAITING=1` 等运维。
- **4 轮全部有效** → 5-run = `[r1=88.0(保留), r2_new, r3_new, r4_new, r5_new]` → 算 mean±std → 回填 5 张表锚点 → `PHASE=just_finished` → 进 C2。

**红线**：
- ✅ **r1=88.0% 保留**（0 timeout，沙盒正常时跑的，不重跑）。
- 🚫 r2/r3/r4/r5 **全部旧成绩作废**（旧不稳定沙盒上跑的，全部重测）。
- 🚫 **不回退旧沙盒**（8650-8654 已弃用）。
- ✅ 保持新 key `e13f4f37` + `deepseek-v4-pro-fp4` + `/cloud/v1`。
- ✅ **沙盒实测必须 4/4 全过才开跑**（任一端口挂 → WAITING 报告，不将就）。
- ✅ B 阶段 + C1 其他 3 臂（pure_llm/rag/wo_retrieval）**不受影响**（已 5/5 ✅ 完成，不在沙盒切换范围）。


---

## 运维指令 · 2026-10-09（五）— ✅ 沙盒已修复，可重跑 C1.full r4【已被 2026-10-10(一) 取代·归档 2026-10-10 20:49】

> **来源**：用户 2026-10-09 晚通知「沙盒已修复·可重跑 r4」。**取代（四）的待命状态**（(四) 降级为历史）。
> **背景**：r4（batch `b2026_1009_094504`）因沙盒故障 grading 异常慢（`run_eval.py` 跑满 2h35m+ 未出结果）被运维 kill（ops RUN_ID 25/26），判 **❌作废**；**r1=88.0% 保留**，**r2=59.5% / r3=63.3% 作废待复测**。

**本次唤醒的动作（按顺序）**：

1. **三项前置复检（全过才开跑；任一不过 → 不启动，`WAITING=1` 原地等，并把不过项写进 MEMORY）**：
   - ① **pro-fp4 直连 200**：新 key `e13f4f37` + `deepseek-v4-pro-fp4` + `http://agi-gateway.cxmt.com/cloud/v1`，`curl --noproxy '*'` 实测 HTTP=200（网关应回 `model: deepseek-v4-pro-260813`）。
   - ② **沙盒端口可达**（以 `.env` 实际为准：`PROXY_PORTS=8650,8651,8652,8654` @ `SANDBOX_HOST=10.129.32.75`；旧 `8664/8665/8653/8669@127.0.0.1` 已作废）：逐端口探测**非超时/可连**。
   - ③ **eval IDLE**：`pgrep -f '^bash scripts/run_cline_script'` **无输出** 且 `pgrep -f run_eval.py` **无输出**（确认 r4 已彻底 kill、无残留）。

2. **启动 C1.full r4**（同臂 `full`，**不切 `set_ablation`**）—— **四 override 必带**：
   ```bash
   cd /nasdata/app.e0031982/code/eda_fastmcp
   export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
   export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data
   export PYTHON=/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python
   export https_proxy=http://172.19.92.23:13128
   setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_full_r4.log 2>&1 < /dev/null &
   ```
   - 启动后**立刻核验四 override 已在 `/proc/<pid>/environ` 生效**（缺 override 会导致 158 Forbidden + grading crash，见 r2 首启教训）。

3. **canary**：本批开跑前确认反作弊 hook live（一次应被拒的调用**确实被拒**；未被拒 → 立即停、本批作废）。

4. **更新 MEMORY 状态头**：`PHASE=running`、`WAITING=1`、`CONFIG=full`、`ROUND=4`；成绩表 `C1.full` 的 r4 行恢复为「运行中」。

5. **commit + push**（按常驻规程）。

**r4 收割后 → 回到（三）的复测流程**：
- 收割：`grep -E 'pass \\(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r4.log | tail -10` → 记录 **Pass@1 + timeout 数**。
- **判据**：`timeout ≤ 10 且 Pass@1 ≥ 75%` → r4 **有效** → 依序重跑 **`r2-retest` → `r3-retest` → `r5`**（同臂同 override，log `/tmp/ABL_full_r2_retest.log` / `r3_retest` / `r5`）；每轮同判据，**最多重跑 3 次**，3 次仍不达标 → 暂停 `WAITING=1` 等运维。
- 全部有效后：5-run = `[r1=88.0, r2', r3', r4, r5]` → 算 mean±std → 回填 5 张表锚点 → `PHASE=just_finished`。

**红线**：
- ✅ **r1=88.0% 保留**；r2/r3 **作废待复测**（不写进最终 mean±std）。
- ✅ 保持新 key `e13f4f37` + `deepseek-v4-pro-fp4` + `/cloud/v1`（**不回退旧 key / 不改模型名 / 不用 `/v1`**）。
- 🚫 **三项前置复检任一不过 → 不得开跑**。
- 🚫 不新启别的臂 / 不改 `.env` 臂 / 不碰 `ops/`。


---

## 2026-10-11 归档批次（运维指令 (七)/(六)/(四)/(三) — 均已被 (八) 取代或完成）

### 🆕 运维指令 · 2026-10-10（七）— ✅ 按 A 执行：剔除 8667 + 补入 8650–8654（→8 健康端口）+ 调高 MCP timeout → 重跑 r2–r5【已被 (八) 取代】

> 用户令（2026-10-10 晚）：「按 A 下发指令」= 依据 (四) 结论：剔除坏端口 8667 + 补入实测健康的 8650–8654 + 调高 MCP 客户端 timeout → 重跑 r2→r5。

**① 确认停**：pgrep '^bash scripts/run_cline_script' / pgrep run_eval.py 均无输出（r2_new2 已作废）。

**② 改 .env**（/nasdata/app.e0031982/code/eda_fastmcp/.env）
- PROXY_PORTS=8663,8666,8670,8650,8651,8652,8653,8654（剔除 8667 → 共 8 个）。
- SANDBOX_ENDPOINTS 补全 8 条映射：新 3 = 8663/8666/8670（逐个按原 .env 核对各自 workdir，勿臆测）；旧 5 = 8650/8651/8652/8653/8654 → 核对官方 host↔workdir 后填。
- ⚠️ 如实记录：8650–8654 借用 t0002997 workdir（非本账号）的风险。

**③ 改 MCP 客户端超时（第 2 条根因）**
- ~/.cline/data/settings/cline_mcp_settings.json 的 pyAether_MCP_server 项：加/改 timeout → 150000（ms，对齐服务端 SANDBOX_TIMEOUT=150s）。
- ⚠️ 先核对字段名与单位（timeout / requestTimeout；秒 vs 毫秒）再改，贴改动前后原文（脱敏 token）。
- ⚠️ 这是评测环境改动（影响评测对象的 cline）⇒ 须在结果报告「披露」节写明。

**④ 重启 + 核验**：按既定流程重启 eda_fastmcp；核验 ss -lntp | grep 8090 + grep -E 'PROXY_PORTS|SANDBOX_ENDPOINTS' .env（贴行）。

**⑤ 开跑前自检（硬闸）**：对新 8 端口各 run_code 1 次 → 8/8 健康才开跑；任一不健康 → 停、回报（不得带病开跑）。

**⑥ 重跑 r2→r5（本块授权起动）**
- 依次 r2_new → r3_new → r4_new → r5_new；判据 timeout ≤ 10 且 Pass@1 ≥ 75%（每轮最多重跑 3 次）。
- 必带 instrumentation：每次 run_code 记 port + latency(ms) + timeout?(Y/N) → 各轮产出「timeout × 端口」分布表。
- 5/5 完成 → [r1=88.0(保留), r2..r5] 算 mean±std → 回填 5 张表锚点 → 进 C2。

**⑦ 产出**：本块下贴 —— ④ 核验行 + ⑤ 的 8 端口自检表 + ⑥ 各轮 Pass@1 / timeout +「timeout × 端口」表。
**⑧ 归因要求**：本轮同时改 2 个变量（端口池 + 客户端 timeout）—— 若 r2_new 即达标（timeout≤10）则续跑；若仍不达标，须在报告中把两变量分别归因（可补做单变量对照）。

### 🆕 运维指令 · 2026-10-10（六）— ⚖️ 若 9 端口均健康 → 先判别「端口数是否真因」→ 再配全 9 端口重跑 r2–r5【已被 (七) 取代】

> 用户令（2026-10-10 晚）：「如果 9 个端口都没问题，那就把它们都配上，然后重跑 full 的 run2–run5 和后续评测。请评估这个方法能否有效降低 timeout 概率。」
> 运维评估（先读，避免白跑不可归因）：
> - 机制：报错是 cline 的 MCP 客户端 60s 超时（MCP error -32001 ... timed out after 60s，客户端措辞），不是任务级 2500s 超时。
> - 加端口只在「端口级排队/争用」时有效：当前评测并发 -p 8 vs 仅 4 个端口 = 2:1 争用 —— 这是"加端口能救"的唯一机制。
> - 反证：r1=88% 就是在 4 个端口上跑出 0 timeout ⇒ 端口数不是充分解释；更像端点健康度/单次调用本身耗时问题；且 MCP 服务端可能是单进程（EDA_MCP_PORT=8090，0.0.0.0:8090），若是瓶颈则加端口无用。
> - 环境注（2026-10-10 用户提示 · 澄清）：EDA_MCP_PORT=8090 由用户在 36.15 ~/.bashrc 设置。⚠️ ~/.bashrc 只对「交互式非登录 shell」自动生效 —— ops 中继是「非交互 bash」，不读 ~/.bashrc（RUN_ID 29 重启 loop 时 cline 找不到，就是这一条）；凡由中继/loop 启动的进程，须在启动处显式 export（或 source ~/.bashrc / bash -l），不能假设自动继承。（RUN_ID 31 实测：中继 env EDA_MCP_PORT=<UNSET>；但 .env 有 ${EDA_MCP_PORT:=8090} 兜底 + cline 的 cline_mcp_settings.json 硬编码 http://10.251.36.15:8090/sse ⇒ 本例无害。）
> - 混淆：本轮同时删了 PreToolUse hook ⇒ 变量不止一个，直接全量换 9 端口无法归因。
> - 风险：8650–8654 是别的账号 t0002997 的 workdir（非我们 e0031982），且正是此前"坏掉"的那批。
> ⇒ 结论：不保证有效；必须先做判别实验，否则 r2–r5 白跑。

**① 前置**：以 (四) 的 9 端口 run_code 健康结论为准 —— 未得结论前不进入本块。

**② ⭐ 先验判别实验（必做，~30min，便宜）**
- 配置 A = 4 端口（现状 8663/8666/8667/8670）；配置 B = 9 端口（+ 8650/8651/8652/8653/8654）。
- 每种配置做 8 并发 × 30 次最简 run_code（print("ping")）压测，记录每次耗时。
- 报每配置 P50 / P95 延迟 + 超时率（>60s 次数）。
- 判据：B 相对 A，P95 或超时率显著改善（建议阈值：超时率 ↓ ≥50%）→ 端口争用成立 → 进 ③；无显著差异 → 停，回报运维（说明瓶颈在 MCP 服务端/端点慢/调用本身，加端口无用）。

**③ 若判别通过 → 配置 9 端口 + 重启 MCP**
- .env：PROXY_PORTS=8663,8666,8667,8670,8650,8651,8652,8653,8654；SANDBOX_ENDPOINTS 补全 9 条映射（新 4 = e0031982_1~4；旧 5 = 按 host 映射核对后填）。
- 按既定流程重启 eda_fastmcp；核验 .env 生效（贴行）。
- ⚠️ 如实记录：8650–8654 = t0002997 workdir 的借用风险；若判定不宜借用 → 只用 e0031982 系端口（此时"加端口"退化为"无新增"，亦须如实报）。

**④ 重跑 r2→r5（本块授权起动；覆盖 (三)「不启新 run」与「不改 .env」）**
- 依次 r2_new → r3_new → r4_new → r5_new；判据不变：timeout ≤ 10 且 Pass@1 ≥ 75%（每轮最多重跑 3 次）。
- 必带 instrumentation：每次 run_code 记录 port + latency(ms) + timeout?(Y/N)；各轮跑完产出「timeout × 端口」分布表 —— 否则无法验证本改动。
- 5/5 完成 → [r1=88.0(保留), r2..r5] 算 mean±std → 回填 5 张表锚点 → 进 C2。

**⑤ 产出**：本块下贴 —— ② 的判别表（A vs B：P50/P95/超时率）+（若进 ③）④ 的「timeout × 端口」表 + 各轮 Pass@1 / timeout。

### 🆕 运维指令 · 2026-10-10（四）— 🔬 根因排查：连续多日评测 timeout（是否 run_code？哪些端口 run_code 健康？）【最高优先·已完成】

> 用户令（2026-10-10 晚）：「需要 zhulong loop 排查一下重复出现几天的评测的问题，超时是什么原因导致的，是 run_code 吗，是所有端口都有问题吗，上述给到的端口 run_code 有健康的吗。」
> 运维已通过 ops relay（RUN_ID 29）先行处置（agent 侧只需确认，勿重复）：① 删除 ~/.cline/hooks/PreToolUse；② 停 r2_new2；③ 重启 zhulong loop（SLEEP_WAIT 保持 1800s=30min）。

**① 确认停（relay 已做）**：pgrep '^bash scripts/run_cline_script' 与 pgrep run_eval.py 均无输出；~/.cline/hooks/ 下无 PreToolUse。

**② ⭐ 逐端口 run_code 健康测试（核心 —— 直接回答"哪些端口健康 / 是否全坏"）**
- 候选 9 端口：新 8663/8666/8667/8670（workdir e0031982_1~4）+ 旧 8650/8651/8652/8653/8654（t0002997_1~4）；SANDBOX_HOST=10.129.32.75。
- 每端口各发最简 pyAether run_code（print("hello from <port>")，带正确 host/lang，按 15:35 的 patch 口径）：
  - ✅ 健康 = response 非空 且 error_log 空；
  - ❌ 不健康 = 超时 / response 空 / error_log 非空。
- 每端口重复 3 次（探间歇性故障）；记录每次耗时（区分「秒级返回」vs「踩满 60s」）。
- ⚠️ 旧 8650–8654 若需测：先核对 .env/exec_code.py 的 host↔workdir 映射（不改 .env，只读）。

**③ ⭐ 超时根因（给路径:行号级证据 + 命令 + 原始输出）**
1. 量化：从 /tmp/ABL_full_*.log 统计 timeout（总/MCP 32001/ACCESS RESTRICTED/Forbidden/host-error）；按端口分组（若日志带端口）。
2. 是否 run_code：超时是否都发生在 run_code（MCP pyAether）调用？有无非 run_code 的超时（模型服务/网关/grading）？各占多少 —— 给样例 log 行。
3. 是否所有端口都有问题：把超时关联到端口 → 「端口 X 贡献了 N 个 timeout」；指出是否单端口故障（对应 r2_new 的 23 个 gen-fail）。
4. 60s 从哪来：MCP pyAether 的 60s 超时是客户端（哪个文件/哪个常量）还是服务端？为什么慢到 >60s（端口排队/沙盒冷启/workdir 锁/反作弊 hook 延迟）？
5. hook 影响：对比删 PreToolUse 前后的 ACCESS RESTRICTED / timeout 计数；说明反作弊 hook 与 timeout 的因果关系（是真因还是无关）。
6. 历史对照：r1=88.0%(0 timeout) vs r2=59.5%(39) vs r3=63.3% vs r2_new=73.4%(timeout=4 / 23 gen-fail) —— 变化点是什么（沙盒/端口/模型服务/hook/负载）？

**④ 产出**：本块下贴两张表 —— ①【端口 × run_code 健康度（3 次）】；②【timeout 计数 × 阶段 × 端口】+ 根因结论（命令 + 原始输出 + 路径:行号）。
**⑤ 边界**：只排查，🚫 排查完成前不得重启任何评测 run；🚫 不改 .env。

### 🆕 运维指令 · 2026-10-10（三）— 🛑 先停 zhulong + 🔬 逐一实测沙盒端口（新 4 个 8663/8666/8667/8670 + 探旧 8650–8654）【本次唤醒优先动作 · 覆盖(二)·已完成】

> 用户令（2026-10-10 晚）：
> 1. zhulong 先停下来；
> 2. 测试一下沙盒端口 —— 看 4 个新端口（8663/8666/8667/8670）里是否某个有问题（r2_new 73.4% 的 23 个 MCP timeout 疑似单端口故障）；
> 3. 另外测试 8650–8654 之间是否有可用的沙盒端口。
> 本条 (三) 覆盖 (二) 的「开跑」动作：先停再测，测完取证回来等运维裁定，不自动重启 r2。

**① 立即停（本指令第一动作）**
- kill -TERM 当前 r2_new2（retry#1）（/tmp/ABL_full_r2_new2.log 对应的 scripts/run_cline_script.sh 进程组 + 其 child run_eval.py）；10s 未退 → kill -KILL。
- 确认 pgrep '^bash scripts/run_cline_script' 与 pgrep run_eval.py 均无输出（贴原始输出）。
- r2_new2 判 ❌ 作废（人为中止，非有效成绩）；r1=88.0% 仍保留。🚫 停后不自动重启 r2/后续。

**② 逐端口实测（核心：不是 curl 端口可达，而是用 run_code MCP 真跑一次）**
- 候选 = 9 个端口：新 4 = 8663/8666/8667/8670（workdir e0031982_1~4）+ 旧 5 = 8650/8651/8652/8653/8654（旧 range，workdir t0002997_1~4）。
- SANDBOX_HOST = 10.129.32.75。对每个端口单独发一个最简 pyAether 请求（如 print("hello from port <P>")）：
  - ✅ 通过判据：返回非空 response 且 error_log 为空。
  - ❌ 不通过判据：超时 / response 空 / error_log 非空 / 连接被拒。
- （可选交叉印证）nc -zv 10.129.32.75 <port> 或 curl --noproxy '*' 探连通性；但以 run_code 实跑为准（端口 OPEN ≠ 沙盒能跑代码）。
- ⚠️ 探旧 8650–8654 仅作可用性测试（(二) 曾写「8650-8654 已弃用」——本次是测试，是否启用由运维裁定，不改 .env）。

**③ 产出（本指令块下贴表）**

| 端口 | 组 | workdir | 连通(nc/curl) | run_code 实测 | error_log | 结论 |
|:--|:--|:--|:--|:--|:--|:--|
| 8663 | 新 | e0031982_1 | | | | ✅/❌ |
| 8666 | 新 | e0031982_2 | | | | ✅/❌ |
| 8667 | 新 | e0031982_3 | | | | ✅/❌ |
| 8670 | 新 | e0031982_4 | | | | ✅/❌ |
| 8650–8654 | 旧 | t0002997_1~4 | | | | 逐个 ✅/❌ |

- 必须明确：① 4 个新端口里哪个（哪些）有问题；② 8650–8654 里哪些可用。

**④ 停后一并做**
- 更新 run/MEMORY_ZHULONG.md：PHASE=blocked（或 standby）、r2_new2 = ❌作废(人为中止)、附上端口实测结论、WAITING=1。
- commit + push（按常驻规程 zhulong <阶段/轮次>: <一句话>）。

**⑤ 边界**
- 🚫 不启动任何新评测 run（r2 及以后都不启）—— 端口结论回来、运维看过再定。
- 🚫 不改 .env（哪个端口先用由运维裁定）。
- ✅ 本指令只做三件事：停 + 测 + 报。

---

> **归档时间**：2026-10-11（**原文搬迁**，只搬不改；该块已由 2026-10-11 `(九)` 取代 —— 其 4 端口 `8663/8666/8667/8670` 在 10-11 早间再次全部挂死，r2_new 因此无 official Pass@1）。

### 🆕 运维指令 · 2026-10-10（八）— ✅ **按 B′ 执行**：保留 4 端口 + `cline_mcp_settings.json` `"timeout": 180` + 重跑 r2–r5【最高优先 · 覆盖 (七)/(六)】

> **用户令（2026-10-10 晚）**：「zhulong：**用当前 4 端口重跑 r2–r5**；**`cline_mcp_settings.json` 加 `"timeout": 180`（防再挂时 60s 太短）**；**不必配 9 端口**。」
> **依据（`(四)`+`(六)` 实测）**：timeout 根因 = **`8667` 瞬态挂死**（**现已恢复**：9 端口复测 3/3@0.01s ✅）+ **客户端默认 60s 太短**；`(六)` **4-vs-9 判别未见加端口收益**。

**① 确认停**：`pgrep '^bash scripts/run_cline_script'` / `pgrep run_eval.py` **均无输出**。

**② `.env` 不动（覆盖 `(七)②`）**
- 保持 **`PROXY_PORTS=8663,8666,8667,8670`**（**当前 4 端口**，含已恢复的 `8667`）。
- 🚫 **不补 `8650–8654`**（判别未见收益 + 借用 `t0002997` workdir 风险）。

**③ 加 MCP 客户端超时（唯一环境改动）**
- `~/.cline/data/settings/cline_mcp_settings.json` 的 `pyAether_MCP_server` 项：加 **`"timeout": 180`**（**180 秒**）= 服务端 `SANDBOX_TIMEOUT=150s` 之上留余量。
- ⚠️ **先核对字段名/单位与现有 schema** 再改；**贴改动前后原文**（脱敏 token）。
- ⚠️ 属**评测环境改动**（影响评测对象的 cline）⇒ **须在结果报告「披露」节写明**。

**④ 重启（如生效需重启）+ 核验**：按既定流程重启 `eda_fastmcp`；核验 `ss -lntp | grep 8090` + `grep -E 'PROXY_PORTS' .env`（**贴行确认仍是 4 端口**）。

**⑤ 开跑前硬闸（每轮都做）**：对 **4 端口**各 `run_code` 1 次 → **4/4 健康才开跑**；任一不健康 → **停、回报**（防 `8667` 再挂）。

**⑥ 重跑 r2→r5（本块授权起动）**
- 依次 `r2_new → r3_new → r4_new → r5_new`；判据 **`timeout ≤ 10` 且 `Pass@1 ≥ 75%`**（每轮最多重跑 3 次）。
- **必带 instrumentation**：每次 `run_code` 记 **`port` + `latency(ms)` + `timeout?(Y/N)`** → 各轮产出 **「timeout × 端口」分布表**。
- 5/5 完成 → `[r1=88.0(保留), r2..r5]` 算 mean±std → 回填 5 张表锚点 → 进 C2。

**⑦ 产出**：本块下贴 —— ③ 改动前后原文 + ④ 核验行 + ⑤ 的 **4 端口自检表（每轮）** + ⑥ 各轮 `Pass@1 / timeout` + **「timeout × 端口」表**。
**⑧ 备注**：若 `r2_new` 仍出现**大量 task-level timeout** → 回报（届时再议重负载 4-vs-9 判别 / 端口剔除）。

---

> 归档时间：2026-10-12 09:31 CST（任务书 ~38.7KB > 32KB 阈值，搬出 (十一)(十) 两个已闭合运维块至本文件。报告均已提交：(十一) R1_ANOMALY @commit 25b27adb；(十) RAG_AUDIT @commit 84e66335）。

### 🆕 运维指令 · 2026-10-11（十一）— 📊 **Deep dive：为什么 `full` r1=88.0%** + 中文 HTML 报告 + 「轨迹问题·按修复收益降序」表 · 用户直令 · 高优先

> **用户令**：「那**为什么 r1 得 88.0%**？请 ZhuLong agent **深入分析**，写一个 **html 调研报告（中文）**，把这个事情**落实**。对于**检查交互轨迹过程中发现的问题**，最后**按照修复收益从大到小列出表格**。」
> **数据**：`full` = r1 **88.0** / r2 79.1 / r3 77.2 / r4 80.4（r5 running）⇒ **r1 比 r2 高 8.9pp、比 r2–r4 均值(78.9) 高 9.1pp**。
> **性质**：分析 + 写作（**只读**）；🚫 **不重启 / 不改 `.env` / 不碰 r5**。**运维已下发 `RUN_ID 46` 取证块**（batch 清单 / r1×r2 工具集 diff / 配置指纹 / 逐题翻转 / 仓库变更史）⇒ **先读 `run/ops/outbox.md` 的 46 段再动手，别重复劳动**。

**(A) 候选原因逐条裁决（每条给证据 + 成立? + 置信度）**
1. **是否 legacy/复用**：r1 是否为某旧 batch 结果被复用（`wo_retrieval` 的 r1 就标注「复用 legacy 74.1%」）⇒ 给 r1 的**原始 batch id + 生成时间**；
2. **工具集 diff**：r1 vs r2 的 `Available tools` 全表逐项（检索 3 件套 / `probe_pyAether_code` / `query_memory_bank` / `text_to_image` …）；
3. **配置指纹 diff**：`PROXY_PORTS` · `SANDBOX_ENDPOINTS` · `RAG_RECALL_URL` · `API_INFO_MERGED_FILE`(V2/V3) · `EDA_EVOLVE_ENABLED` · `EDA_MEMORY_INJECT_ENABLED` · `PreToolUse` hook · MCP 协议(`/sse` vs `/mcp`)；
4. **逐题翻转**：r1 过而 r2 不过（及反向）的 task 集合 —— **集中在少数题（→ 噪声）还是广布（→ 配置效应）**？给翻转题数 + 前 20 清单；
5. **显著性**：158 题二项分布下，r1 与 r2–r4 均值之差是否显著（给 p / 置信区间估算）；
6. **评分口径**：r1 是否经 re-grade？timeout / exec_err 统计。

**(B) 交付（中文 HTML · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB）**：`doc/ZhuLong_DAC2027/run/reports/R1_ANOMALY_ANALYSIS_2026-10-11.html`
节：HERO 一句话结论 · 5 轮数据(表+SVG) · **候选原因裁决表**(原因｜证据｜成立?｜置信度) · 逐题 diff · 显著性 · **对 N=5 锚点的影响与建议**(是否剔除 r1 / 标注 / 重跑) · 证据索引(`path:line`) · 诚实条款。

**(C) 报告最后一节 = 「轨迹问题清单」表（**按修复收益从大到小排序**）**：每行 `# | 问题 | 证据 | 影响面 | 修复动作 | 工作量 | 风险 | 预期收益`；至少覆盖：① 检索 3 件套边际≈0（`run_code` 冗余）② 模型漏 MCP 前缀 `search_apis`（~1%/轮）③ **`tcl` 两 collection 召回 0 条** ④ `rag` 臂非单变量（同时动了检索 + 沙盒）⑤ 9001–9011 端口乱象（7+ 实例 · 9002 http=500）⑥ r1 异常（本报告定论）⑦ 你在轨迹里**新发现**的问题。

**(D) 收尾**：更新 `MEMORY_ZHULONG.md` + `daily-memories/<date>.md` + commit+push（前缀 `zhulong r1-anomaly:`）。

---

### 🆕 运维指令 · 2026-10-11（十）— 🔎 RAG(9006) 排查【🏁 **已收口**】· 报告已交：`run/reports/RAG_AUDIT_2026-10-11.md`
> **结论（RUN_ID 41/43/44/45 实测）**：① **9006 正常且能召回**（`pyAether+aether` → `dbCreateRect` 5 条 / `hiGetCurrentWindow` 9 条；`skill+virtuoso` → 3/6 条，⚠️ 仅 `tcl+waveview`/`tcl+innovus` 两对 **0 条**）；② 评测**大量在用检索**（`search_apis` **~1800 次/轮成功调用**；漏 MCP 前缀失败仅 ~1%；轨迹空结果仅 2/0/1）；③ 臂定义：`full` = 检索 ON + `run_code` ON + **V3 文档**；`wo_retrieval` = 检索 OFF；`rag` = 检索 ON + **`run_code` OFF**。
> ⇒ **`full`≈`wo_retrieval` 是真实弱结果**（机制：`run_code` 沙盒使显式检索冗余），**不是 bug**；但 ⚠️ **`rag` vs `full` 非单变量**（同时动了检索+沙盒）⇒ 表格注须说明，🚫 **不得**宣称「检索带来提升」。本块全程只读。

---


## 📦 归档批次 · 2026-10-13 22:2x（phi_k3 r3 regrade 跑中·任务书超 40KB 红线·agent 自滚归档）

> 以下 4 个已闭合运维块原文搬入：**(十四)** 暂停令（已被(十五)撤销）· **本轮 2026-10-11 执行顺序**（r2-r5 已完成）· **(十二)** full_v3 补跑（5/5✅ 82.1±3.0% 已交付）· **(九)** 换回旧 4 端口（已完成）。原块在任务书留 1 行指针。

### 🆕 运维指令 · 2026-10-13（十四）— 🛑 立即暂停所有试验（沙盒重启中）【已被(十五)撤销·2026-10-13 归档】

> **用户令（2026-10-13）**：「需要重启沙盒，让烛龙 agent 暂停试验。」

**立即执行**：
1. **杀掉当前评测进程**：`pkill -f 'run_cline_script'`（如有残留）。
2. **不启动任何新轮次**。`PHASE=standby` · `WAITING=1` · `ERROR_COUNT=0`。
3. **在 `MEMORY_ZHULONG.md` 顶部状态头记**：`PHASE=standby（运维令(十四)：沙盒重启中，暂停试验）`。
4. **等运维下达「沙盒已就绪，可恢复试验」指令后再继续**。恢复时从 `phi_k3 r1`（att2 成绩或 72.8%）继续推进，不回退已完成的轮次。
5. **⚠️ 不要动 `.env` / 端口 / MCP / hook**——沙盒重启由运维/用户操作，agent 只需等待。

**红线**：
- 🚫 不得启动任何新轮次。
- 🚫 不得修改任何配置文件。
- ✅ 只做：杀残留进程 + 记状态 + commit/push + 退出等待。

### 🧭 本轮（2026-10-11 上午）执行顺序 —— 换回旧 4 端口 + 修 RAG + 删 hook → 推进 r2–r5【已完成·2026-10-13 归档】

> ➡️ **按 `(九)` 执行**（`.env` 端口集换回 `8650/8651/8652/8654` + `RAG_RECALL_URL`→`9006` + 删 `~/.cline/hooks/PreToolUse` + `.env` stash 回退 + **回退 `timeout:180`** → 重跑 r2–r5）。
> ⚠️ **`(九)`⓪ 先自查「中继执行了没有」**（`outbox.md` 有无 RUN_ID 32）——**中继近 11h 无活动、已判「疑似失联」**；若确实失联，`(九)`⓪ 授权你**自己照 `run/ops/inbox.md` 的 RUN_ID 32 块执行**（含重启中继），别干等。
> ❌ `(八)` 已被 `(九)` 取代；`(七)/(六)/(四)/(三)` 已完成或作废 —— **勿重复**。

### 🆕 运维指令 · 2026-10-11（十二）— r5 收割后补跑 5 轮「真正的 full」（自探索开启）【full_v3 5/5✅ 82.1±3.0% 已交付·2026-10-13 归档】

> **用户令（2026-10-11）**：「**在当前 full 的 r5 跑完后，在后续任务开始前，先跑 5 轮「真实」full（自探索开启）配置。**」
> **为什么（已取证 RUN_ID 46/47/48）**：**r1 = `/tmp/ABL_full_r1.log`（10-10 15:32，旧配置）**；而 `e51372ff`（**10-10 16:33** t0002997「**使用未增强文档，无自探索**」）改了 `.env` → `API_INFO_MERGED_FILE=./docs/API_INFO_MERGED_V2.json`；**r2–r5 全在该改动之后** ⇒ 实跑的是 **V2 未增强 + 无自探索**，而 `set_ablation.py` 里 **`full` 的定义 = V3 增强文档**（= 自探索开）⇒ **C1 锚点混了两种配置**（这也解释 r1 88.0 vs r2–r5 ≈79）。

**① 顺序（硬）**：`r5 收割 + 判定` → **【本批】`full_v3` 5 轮** → 之后才进 `C2.phi_k10`（不另等指令）。
**② 配置切到「真 full（自探索开）」**：`python scripts/set_ablation.py full`（托管：检索 3 件套 ON + `run_code` ON + 完整回读 + `API_INFO_MERGED_FILE`）；**并手工恢复"自探索"的两项** —— RUN_ID 48 已拿到 `e51372ff` 的完整 diff，**自探索 = 这两个变量**：`API_INFO_MERGED_FILE=./docs/API_INFO_MERGED_V3.json` ＋ **`SKILL_DATA_DIR=./docs/skill_data_selfexpl`**（⚠️ **`SKILL_DATA_DIR` 不由 `set_ablation.py` 托管，必须手改**）。改前先 `cp .env .env.bak_$(date +%s)`；⇒ **必须 `bash scripts/stop.sh && bash scripts/start.sh` 重启 MCP 才生效**。
**③ 开跑前 5 项自检（缺一不可，**原文贴进心跳**）**：① `.env` 的 `API_INFO_MERGED_FILE` = **V3** **且 `SKILL_DATA_DIR` = `./docs/skill_data_selfexpl`**（并 `ls -l docs/API_INFO_MERGED_V3.json docs/skill_data_selfexpl` 均存在）；② 4 端口 `8650/8651/8652/8654` **4/4 健康**；③ MCP 8090 在听 + 工具含 `search_apis`；④ **反作弊 hook 在位**（`~/.cline/hooks/PreToolUse` + 新 log「已部署沙盒 hook」+ `ACCESS RESTRICTED` >0）—— 🚫 **未部署不得开跑**；⑤ `df -BG /home` ≥8G。
**④ 跑法与判据**：与 r2–r5 **逐字同口径**（`bash scripts/run_cline_script.sh -p 8 -n` · 端口 8650-8654 · log **`/tmp/ABL_full_v3_r{1..5}_8650set.log`**）· 每轮 code-gen 后 **re-grade 同口径**（`--benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl --lang pyAether`；auto-grade 有 benchmark bug）· 判据 **timeout ≤10 且 Pass@1 ≥75%** ⇒ 该轮有效。
**⑤ 交付**：`full_v3` 的 **N=5 mean±std** + **三组对照表**（`r1` 旧时代 V3 / `full` 现配 V2 = r2–r5 / **`full_v3` 新 5 轮**）+ **是否复现 r1 的 ~88%** 的结论。🚫 **不删**旧 batch/log（证据）；提交前缀 `zhulong full_v3:`。

### 🆕 运维指令 · 2026-10-11（九）— 换回旧 4 端口 + RAG→9006 + 删 hook + .env 回退 + 重跑 r2–r5【已完成·2026-10-13 归档】

> **用户令（2026-10-11 上午）**：「停掉当前评测；删 `~/.cline/hooks/PreToolUse`；`eda_fastmcp/.env` 本地改动 stash（回退昨晚改动）；**测试/应用端口 `8650`、`8651`、`8652`、`8654`**；改 `.env`；**ragrecall 端口重新设为 9006**；**重启 full r2-r5 及后续评测**。」
> **本块应交由 ops 中继 `RUN_ID 32` 代做**（停评测/删 hook/`.env` 备份+stash/写新 `.env`/重启 `eda_fastmcp`/4 端口实测/**4/4 健康才起 r2**/**回退两处 `cline_mcp_settings.json` 的 `timeout:180`**）。⚠️ **用户二段令（10-11）：「昨晚的改动都是垃圾，全部回退，没有任何亮点」** ⇒ 32 块的 timeout:180 回退即按此令执行（**已推翻「保留」判断**）。

**⓪ 先自查「中继执行了没有」（30 秒，每次唤醒必做）**
- `grep -c '^## RUN_ID 32' run/ops/outbox.md` **≥1** ⇒ 已执行 → 走 ①（并按 ① 复核 r2 是否已起）。
- **= 0** ⇒ **判中继失联**（**判据**：中继**最后一次成功执行是 10-10 20:59 的 RUN_ID 31**，此后无回写；⚠️ **不要**拿 `inbox.md` 的 mtime 计时 —— 运维会**原地修订** RUN_ID 32 块，修订**不算**重新计时）⇒ **你自己照 `run/ops/inbox.md` 里 RUN_ID 32 那个 bash 块执行**（244 行/幂等；原文即完整食谱：① 停评测——**只杀评测侧**，`pkill -f run_cline_script` 会误杀编排侧 cline；② 删 `~/.cline/hooks/PreToolUse`；③ `.env` 备份 + `git stash push -- .env`；④ 写 `PROXY_PORTS=8650,8651,8652,8654` + `SANDBOX_ENDPOINTS`（按 `.env`/HEAD 既有映射逐条核对，勿臆测 workdir）+ `RAG_RECALL_URL=http://localhost:9006/recall`；⑤ 重启 `eda_fastmcp`；⑥ 4 端口 `run_code` 实跑；⑦ **仅 4/4 健康才** 起 r2；⑧ **回退两处 `cline_mcp_settings.json` 的 `timeout:180`**）。**执行完**：把 `inbox.md` 的 `<!-- RUN_ID: 32 -->` 置 **33**、并把该 bash 块降级为 text 围栏（占位，防中继复活后重复执行）；并顺手重启中继：`pgrep -af zhulong_ops_relay.sh`（无 → `env PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" https_proxy=http://172.19.92.23:13128 setsid bash doc/ZhuLong_DAC2027/run/zhulong_ops_relay.sh > /tmp/zhulong_ops_relay.log 2>&1 < /dev/null &`）。结论写进 `MEMORY_ZHULONG.md`。

**🔧 infra 速记（10-11 实战；详见 `MEMORY.md` §7-18/19）**
- **中继/loop「失联」≠ 进程死**：远端 `.last_run_id`/`outbox` 长期不动，多因 **GitHub/proxy 断 → `push FAILED (will retry next cycle)`**（看 `/tmp/zhulong_ops_relay.log` 尾）。**修法**：`pkill -f 'zhulong_ops_relay[.]sh'` → `setsid bash <脚本>`，**显式注入 `PATH=$HOME/.local/node-20/bin:$HOME/.bun/bin:$PATH` + `https_proxy=http://172.19.92.23:13128`** ⇒ 30–60s 内自 fetch 并补跑积压 RUN_ID（10-11 **08:07:34 重启 → 08:07:38 跑完 RUN_ID 32**）；**loop 同法**（RUN_ID 33 已重拉）。
- **跨机救援桥 = BaiZe 中继（跑在 2.29）**：其块内 `timeout 240 ssh -p 3333 -o BatchMode=yes app.e0031982@localhost 'bash -s' <<'EOS' … EOS 2>&1 | cut -c1-190` 即**在 36.15 执行**（**36.15 ✗ 2.12 不可直连**；桥先例 RUN_ID 83/84/85/86）；**跨通道下发要错开 ≥30s**（push 撞车 → 记录只留本地，要下一次 run 才补推）。

**📌 2026-10-11 08:2x 实况**：中继已救活并跑完 **RUN_ID 32/33**（exit=0）；`bash scripts/start.sh` **仍 exit=1**（`:8090` 未监听，但 `python main.py` 有 3 个进程在），4 端口在 08:14 实测 `run_code` 0 字节、**08:2x 已恢复 4/4 健康**；**loop 已于 08:13:55 重启**（`cline OK`）。⇒ **唯一硬阻塞 = `/home` 100%（4G < 8G 门槛）** ⇒ 未起 r2、`WAITING=1` 回报；**在运维裁定「可否带 4G 起跑」前不要开跑。** **✅ 用户 10-11 已裁定：授权带 4G 起跑 r2**（`/home` ≥8G 门槛放宽，其余硬闸不变）—— **RUN_ID 34 已按此下发**（MCP/RAG → 4 端口 → 起 r2）；另查明 **36.15 的 MCP 实际监听 `:18890`（不是 8090）**，`start.sh exit=1` 只因「18890 已被占用」= 已在跑。

**① 若中继已执行 → 读 `outbox.md` 末尾 RUN_ID 32 的三件事**：(a) 4 端口实测结果；(b) `.env` 最终关键行（应 `PROXY_PORTS=8650,8651,8652,8654` + `RAG_RECALL_URL=http://localhost:9006/recall`）；(c) r2 是否已起（eval PID / log `/tmp/ABL_full_r2_8650set.log` / 四 override / **hook 是否被重新部署**）。

**② 状态记账（先改状态头再干活）**：`CONFIG=full`(锚点) · `ROUND=2` · `.env` 臂配置不动；**`r2_new`（batch `2026_1010_234408`）判 ❌作废**（code-gen 146/158 但 **eval Steps 5–7.1 未跑 = 无 official Pass@1**；log/batch 留证，不并入成绩）；**`r1=88.0%` 保留**；**端口口径 = `8650/8651/8652/8654` @ `10.129.32.75`**。
⚠️ **披露清单**（写进结果报告「披露」节）：`.env` 端口集回退 + `RAG_RECALL_URL`→`9006`（原 `9012` 死）+ 删 `~/.cline/hooks/PreToolUse` + `cline_mcp_settings.json` 的 `"timeout": 180`（`(八)`③）—— **本轮已随 RUN_ID 32「3.6 步」一并回退**（用户 10-11 二段令：「昨晚的改动都是垃圾，全部回退，没有任何亮点」）。

**③ 分支**：已起 → **先核反作弊**（`ls -l ~/.cline/hooks/PreToolUse` + 新 log 出现「已部署沙盒 hook」+ `ACCESS RESTRICTED` >0；**未部署 ⇒ 立即停本批、判作废、回报**）；随后 `pgrep -f '^bash scripts/run_cline_script'` **有输出=巡检退出**、**无输出=收割**。未起 → `WAITING=1` + 回报不健康端口原文，**不得带病开跑**。

**④ 收割/推进（判据不变）**：`grep -E 'pass \(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r2_8650set.log | tail -10` → **`timeout ≤ 10` 且 `Pass@1 ≥ 75%`** ⇒ r2 有效 ⇒ r3→r4→r5（同臂 `full` + **四 override**（见 §6 与旧 `(八)`⑥）+ log `/tmp/ABL_full_r3_8650set.log`…；**每轮开跑前 4 端口复检 + `df -BG /home` ≥8G**；不达标最多重跑 3 次 → 仍不达标 `WAITING=1` 回报）→ 5/5 `[88.0, r2–r5]` 算 mean±std → 回填 5 表锚点 → `PHASE=just_finished` → 进 `C2.phi_k10`。产出：各轮 `Pass@1 / timeout` + **「timeout × 端口」表** + hook/canary 复核结论。


---
## [⏩ 从 ZHULONG_TASK.md 滚出 · 2026-10-14 21:46 归档] 运维指令（十六）+（十五）原文

### 🆕 运维指令 · 2026-10-14（十六）— 📝 实验空窗期审视论文，出改进意见 HTML（中文）【用户直令 · 与评测并行不互斥】

> **用户令（2026-10-14）**：「安排 zhulong agent 在实验进行期间，审视论文（ZhuLong_DAC2027），将改进意见写成 html 报告（中文版）。」

**性质**：零 GPU 的纯「读 + 写」任务。**主线仍是评测**（当前 `phi_k1 r2` 跑中）——本任务只占用**等待评测结果的空窗期**：评测一有结果，立即回归评测（收割/打分/切下一臂）**优先于**论文审视，两者交替推进，🚫 绝不为论文审视而延迟/打断评测。

**① 审视对象**：论文树 `doc/ZhuLong_DAC2027/ZhuLong_DAC2027/`（`main.tex` + `DAC2027/0_abstract.tex`…`8_conclusion.tex` + `reference.bib`/`software.bib` + 已编译 `main.pdf`）。

**② 审视维度（每条意见必须具体，🚫 空泛）**：
1. **论点-证据一致性**：每句核心 claim 是否有实测数字支撑；对照当前评测实况（B 4 臂、C1 4 臂、C2 `phi_k10` 5/5、`phi_k3` 5/5、`phi_k1` r1/r2 进行中）——哪些表/数字还是 `[TBD]`、哪些与实测不符、哪些结论尚缺轮次支撑。
2. **评测口径**：Pass@1 分母（158 全量 vs 生成成功子集）、5-run `mean±std` 是否齐、配对检验（McNemar / paired bootstrap）是否声明、`timeout ≤10` 与 `gen-fail`（生成失败）的处理口径是否在论文里交代清楚。
3. **消融结论一致性**：Φ 预算单调趋势（`k10=77.7% > k3=69.1% > k1≈65%`）、gen-fail 随 k↓ 递增、`full_v3` 锚点 82.1±3.0%——论文的结论句是否与这些实测方向一致，有无过度声称。
4. **贡献边界 / 与 BaiZe 关系**：harness 属 ZhuLong、backbone 属 BaiZe 的边界是否写清；是否按 DAC/ISEDA 双会「互相引用、不重报」的约定表述。
5. **结构与表述**：Abstract/Intro/Conclusion 一致性、Limitations 段是否缺失、图表/交叉引用是否齐全、overfull hbox / 页数是否超限。
6. **可回填项**：列出「**已有实测、可直接回填**」的 `[TBD]` 清单（附目标值），与「**仍缺数据、暂不能填**」的清单（附还缺哪几轮）。

**③ 交付**：中文、自包含 HTML 报告 `doc/ZhuLong_DAC2027/reports/report_zhulong_paper_review_zh.html`（若 `reports/` 不存在则建）；每条意见贴 **`文件:行号`** 或**具体数据**，分「🔴 硬伤 / 🟠 建议 / 🟢 可回填」三级标注；文末附「已回填建议清单」。

**④ 红线**：
- 🚫 **不直接改论文 `.tex`**（只出意见报告；改稿须运维/用户另行批准）。
- 🚫 不得为论文审视而 kill/延迟评测进程；评测优先级更高。
- 🚫 不得空泛（「建议加强实验」这种无效）；每条必须可落到具体位置或数字。
- ✅ 意见里引用实测数据时，须与 `MEMORY_ZHULONG.md` 执行看板/成绩一致，不许凭印象。

**⑤ 纪律**：commit 前缀 `zhulong paper-review:`；产出后 `git add` 报告 + 回写 `MEMORY_ZHULONG.md` 心跳；任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-13（十五）— ✅ 沙盒已重启完成，恢复试验（撤销 (十四) 暂停令）【最高优先 · 用户直令】

> **用户令（2026-10-13）**：「zhulong 沙盒已重启，让它继续试验。」

**立即执行**：
1. **撤销 (十四) 的暂停令**：`PHASE` 从 `standby` 切回运行态。
2. **恢复点（不回退）**：从 `phi_k3 r2` 继续。`r1 = 72.8%`（115/158 · timeout=0）已按 (十三) 判有效；att2 被 (十四) kill 的 114/158 **不重跑、不作为 r1**。
3. **开跑前 5 项自检（沙盒重启可能还原状态，必须重核，缺一不可）**：
   ① `.env` 配置为 `phi_k3`（S2 Φ 预算 k=3 · base=full(V3+selfexpl) 保留，`set_s2_phi.py` 只改预算、不动 V3/SKILL_DATA_DIR）；
   ② 4 端口 `8650/8651/8652/8654` 全健康；
   ③ MCP `8090` 在听且工具含 `search_apis`；
   ④ 反作弊 hook 在位（`~/.cline/hooks/PreToolUse` + 新 log「已部署沙盒 hook」+ `ACCESS RESTRICTED` >0）；
   ⑤ `df -BG /home` ≥8G。
   若任一项缺失，先按 (十二) 口径补齐（`bash scripts/stop.sh && bash scripts/start.sh` 重启 MCP 使生效），再开跑。
4. **跑法与判据（沿用 phi_k3 既有口径）**：`bash scripts/run_cline_script.sh -p 8 -n`；**判据 = `timeout ≤ 10` 且无 infra 故障**（license / 端口 / 磁盘 / auto-grade bug）；`Pass@1` 任何值均有效（低分 = 真实消融效应）→ **不得因 <75% 重跑**。
5. **交付**：phi_k3 `N=5 mean±std` → 继续 C2 其余臂（phi_k1 / phi_lagged）→ 之后 S1。

**红线**：
- 🚫 不得重跑 att2 / 不得回退 r1（72.8% 已定）。
- 🚫 不得以 `Pass@1 < 75%` 作废或重跑任何消融臂。
- ✅ 沙盒重启若致 `.env` / 端口 / MCP / hook 异常，先修复（不动业务逻辑）再开跑，修复过程记进心跳。



---
## [归档 2026-10-15 09:34] 运维指令 (十八)(十九)(二十) — 已闭合，从 ZHULONG_TASK.md 原文搬入

### 🆕 运维指令 · 2026-10-15（二十）— 📝 把最新评测结果填入 zhulong_results.md【用户直令 · 最高优先】

> **用户令（2026-10-15）**：「让 zhulong 把最新评测结果填入 zhulong_results.md。」

**① 填写对象**（`doc/ZhuLong_DAC2027/zhulong_results.md`，以下均为**已 5/5 收口的实测**，与 `MEMORY_ZHULONG.md` 执行看板逐字一致）：
1. **S2.phi_k1**：5/5 = **63.8 ± 3.2%**（r1 65.2 · r2 66.5 · r3 58.2 · r4 64.6 · r5 =? 从台账/日报取准确值），并补各轮 gen-fail（k=1 预算效应：35/30/39/34/?）。
2. **S2.phi_lagged**：5/5 = **73.0 ± 3.2%** [74.7, 76.6, 69.6, 69.6, 74.7]。
3. **更正 B.deepseek-v4-flash**：当前标 `⬜ 0/5` 系漏填 → 应 **✅ 5/5 = 16.7 ± 12.3%** [9.5, 10.1, 19.0, 7.6, 37.3]。

**② 填写规范**：
- 每个臂填 **mean ± std + 5 轮明细 + gen-fail 数**（与论文 `tab:phi-bound` 口径一致）。
- 把「S2 各臂仅有 1-shot 探路值」的旧注**删除/更新**（现在 k10/k3/k1/lagged 均已 5/5）。
- 同步把 `[ ]`（未完成复选框）改成 `[x]`（已完成）。

**③ 纪律**：数字从 `MEMORY_ZHULONG.md` 执行看板 / 当日 daily-memories 抄，🚫 凭印象；S1.omega_low 本论仍在跑、**不填**（只填已 5/5 的）；commit 前缀 `zhulong results:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-14（十九）— 🖨️ pdflatex 已装好，编译验证论文【用户直令 · 最高优先】

> **用户令（2026-10-14）**：「zhulong 环境刚刚装好 pdflatex 了。」

**① 现在编译验证论文**（衔接十七的 P0+P1+P2 改稿）：进论文树 → `pdflatex` + `bibtex` + `pdflatex×2`，验证改稿后 `main.pdf` 编译成功。

**② 检查项（逐项报）**：
- **0 error** · **0 undefined reference / citation**；有 warning 也要记录（尤其 bib 缺 page/volume 类）。
- **页数变化**：改稿前 10 页 → 改稿后 ? 页。
- **overfull hbox**：新增与否；>20pt 的必须是 0（README 自检阈值）。

**③ 若编译报错**：先判断是**改稿引入**（如 label/引用、表格语法、`\cite` 错名）还是**环境**（缺 `.sty`/`.cls`/字体/`bibtex` 命令）。改稿引入的能修就修；环境缺件如实报并给等价替代（如缺 `texlive-latex-extra` 包名）。

**④ 纪律**：纯 CPU 编译，不占 GPU；`main.pdf` 编译产物按仓库惯例提交（`.tex`+`.bib` 必交，`.aux/.log` 不入库）；commit 前缀 `zhulong compile:`；任务书 >32KB 自滚归档。主线 `phi_k1 r3 regrade` 照常推进，编译在空窗期做。

### 🆕 运维指令 · 2026-10-14（十八）— 🧩 评测集全貌 + SKILL/Tcl 结果并入论文【用户直令 · 最高优先】

> **用户令（2026-10-14）**：「告知 zhulong agent：它自己在测 PyAether，其它 agent 在同时测 SKILL 和 TCL，结果汇总到 `doc/ZhuLong_DAC2027/zhulong_results.md`。请 zhulong agent 在回填结果、刷新论文时，把 zhulong_results.md 中 SKILL/TCL 的结果带上。补充信息：EDA-Scripting-Bench 评测集中各语言 case 数，pyaether=158，skill=158，tcl=133，共计 449。」

**① 评测集全貌（EDA-Scripting-Bench，三语言）**：
| 语言 | case 数 |
|:--|:--|
| PyAether | 158 |
| SKILL | 158 |
| Tcl | 133 |
| **合计** | **449** |

**② 分工**：你（zhulong）测 **PyAether（158）**；**其它 agent 并行测 SKILL（158）+ Tcl（133）**。三路结果统一汇总到 `doc/ZhuLong_DAC2027/zhulong_results.md`。

**③ 要求（衔接指令十七「放行刷新论文」）**：
- 回填论文结果时，**以 `doc/ZhuLong_DAC2027/zhulong_results.md` 为汇总源**，把 **SKILL/Tcl 的结果一并带上**——论文评测口径从「PyAether 158」扩展为「**EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）**」。
- 具体落地：
  - 回填 **RQ3「SKILL/Tcl 切片」**（此前标 pending）——`zhulong_results.md` 中 SKILL/Tcl 已有结果即填，未齐则如实标 `partial`/`pending`。
  - 回填 intro/abstract 的 **「unified benchmark [X%]」**——按三语言 449 合并 Pass@1 重算（或显式标注口径）。
  - 全文凡涉及「PyAether-only」的主表/轴向，须改口径说明，🚫 避免「158」与「449」混用、避免读者误以为全榜只有 PyAether。
- 🚫 不得只报 PyAether 而继续忽略 SKILL/Tcl；🚫 不得凭印象编 SKILL/Tcl 数字——**只认 `zhulong_results.md` 现存数字**，未齐标 pending。

**④ 纪律**：每次唤醒刷新论文前先 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；数字与之逐字一致；缺数据标 pending 不编造；commit 前缀沿用 `zhulong paper-fix:`；评测主线不变（finish phi_k1 → phi_lagged → S1，改稿仍在空窗期做）。


---
## [归档 2026-10-15 09:35] 运维指令 (十七) — P0-P3 论文改稿已执行+编译验证通过，从 ZHULONG_TASK.md 原文搬入

### 🆕 运维指令 · 2026-10-14（十七）— ✍️ 放行改进论文（执行审视报告修改）【用户直令 · 最高优先】

> **用户令（2026-10-14）**：「zhulong agent 论文改进报告已审视/批准，请 zhulong agent 按此改进论文。」

**性质**：纯写作、零 GPU。**主线仍是评测**（当前 `phi_k1 r3` 跑中）——改稿只在空窗期做，🚫 绝不为改稿延迟/打断评测收割与切臂。

**① 撤销「只报不改」红线**：放行你修改论文 `.tex`，执行审视报告 `reports/report_zhulong_paper_review_zh.html` 的修改（按 §8 优先级 P0→P1→P2→P3）。

**② 🔴 P0 硬伤必须修（先改锚点、再批量同步，避免表文矛盾）**：
- **锚点全局替换** `84.8% → 82.1±3.0%`（`0_abstract` / `1_intro` / `8_conclusion` + 4 表锚点行：main-ablation Full、ablation-harness F、phi-bound unbounded、llm-comparison DeepSeek-V4-Pro）。
- **重算所有 Δ**：main-ablation（Full **+10.3pp**、wo_retrieval **−1.1pp**）· llm-comparison 4 个 Δ（**+1.2 / −65.4 / −5.1 / −18.3**）· §S2 正文（**+10.3pp**）。
- **Error Analysis 重做/重声明**：改用 5-run 代表性 run（建议 full_v3 r3=81.6%、129/158）重计失败数；或显式标注「基于单次代表性 trace」。🚫 不得仍绑 84.8% 那次 134/158。
- **硬伤#3**：`tab:omega` (L)=82.8、`tab:ablation-harness` (N)=73.3、(B)=66.2 无 5-run 支撑 → 一律标 `[provisional, n=1]` 或回退 `[TBD]`，🚫 不得再以 `±` 呈现（尤其 (B) ±16.1 的 std 无 n≥2 支撑）。
- **硬伤#5**：`tab:phi-bound` 增加「Mean gen-fail」列（k10/k3/k1），§S2 正文补「k↓ → gen-fail↑ → Pass@1↓」1–2 句。
- **硬伤#6**：§2（Background/Prior work）或 §3 加 1–2 句 BaiZe 边界，措辞中性如「本工作的 harness（三 MCP 工具 + 评测协议）属 ZhuLong；agent backbone 的底层能力另由互补工作 BaiZe[ref] 详述，二者互引不重报」。

**③ 🟠/🟢 按 §8 清单继续**：
- **P1**：补配对检验（paired bootstrap/McNemar）或在 Limitations 明示「未做配对检验」；§5.3/§6 补 gen-fail 计入分母 + infra 故障 run 剔除规则 + 75% 锚点健康下限；§6.1.4 声明 backbone 量化 `deepseek-v4-pro-fp4`；消歧 (N)→(N′)。
- **P2**：删 ICML 中文注释（`6_exp.tex:132-133`）；加结果可视化图至少 2 张（消融条形 + Φ 折线）；Limitations 独立成节并补「未配对检验」「量化未消融」两条；附录加 75 轮原始值表。
- **P3**：回填后重编译处理 overfull hbox（13.6pt/13.1pt 两处）；核对 DAC 2027 页数上限。

**④ 🟢 可回填（§7.1 第 1–10 项）**：能填即填（k10→`77.7±2.2`、k3→`69.1±2.5`、锚点 `82.1±3.0` 等）。🚫 **仍缺数据项一律保留 `[TBD]`/provisional，不得编造**：phi_k1 r3–r5、phi_lagged、S1 三臂（omega_low/readback_binary/_none）、wo_sandbox、SKILL/Tcl、全部 Converged(%)。

**⑤ 改稿纪律**：改后编译 `main.pdf` 验证 **0 error** + 报页数变化；每个数字与 `MEMORY_ZHULONG.md` 执行看板/成绩一致、🚫 凭印象；完成把「改了哪几处 + 编译结果」写进心跳；commit 前缀 `zhulong paper-fix:`（区别于 paper-review）· 任务书 >32KB 自滚归档。

**红线**：🚫 评测优先于改稿，不得为此 kill/延迟评测；🚫 数字编造；✅ 锚点与全部 Δ 必须同步改，避免表文矛盾。



## [2026-10-15 17:35 归档] 运维令(二十五/二十四/二十一)已闭合·原文搬入

> 归档原因：(二十五)催办=报告已交付 commit c1a3d177；(二十四)echo数据已并入论文✅15:30 commit zhulong S1-echo:；(二十一)15天建议书已交付 commit c1a3d177。保留(二十三)(二十二)为顶部活跃块（readback_binary 5/5 收口后执行）。

### 🆕 运维指令 · 2026-10-15（二十五）— ⏰ 催办：消融试验中文建议书（指令二十一）尚未交付 · 现在就要【用户直令 · 最高优先】

> **用户令（2026-10-15）**：「zhulong：消融实验中文建议书还是没给我。」

**① 现状**：指令(二十一)「15 天窗口消融建议」纯写作、不占评测，但你连续排了(二十二)(二十三)(二十四)后一直没产出，`doc/ZhuLong_DAC2027/reports/report_zhulong_next_ablation_plan_zh.html` 仍未生成。

**② 立即产出**（占 readback_binary r2 code-gen 的空窗期，🚫 不占 GPU、不打断主线评测）：
- 按指令(二十一)要求：结合当前进展（B/C1/C2 12 臂 5/5 + S1 readback_binary 重测中）+ **15 天 deadline**，提出「进一步消融试验」建议。
- 每条四要素：动机 · 做法+成本（GPU/沙盒/墙钟）· 优先级（必做/建议/可选）· 与 S1/B 臂编排。
- 文末附「**15 天排期表**」（S1 收尾 + readback echo + B.glm-5.3-flash/deepseek-v4-flash + 其它候选）。

**③ 交付**：`doc/ZhuLong_DAC2027/reports/report_zhulong_next_ablation_plan_zh.html`（中文自包含）。

**④ 纪律**：纯 CPU 写作、现在就写；数字与 `MEMORY_ZHULONG.md` 看板一致；commit 前缀 `zhulong plan:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-15（二十四）— 📊 收集 readback 轴 echo 数据强化论文论证【用户直令 · 最高优先】

> **用户令（2026-10-15）**：「好的，如果确认有价值，既然我们花了这么多时间，那应该收集更多信息，加入论文，强化论证依据。」

**① 背景**：readback 消融（full/binary/none）有价值，且 binary 档 code-gen 显著变慢（~3×）本身即「保真度↓ → 收敛成本↑」的证据。现收集更多 echo 数据强化论证。

**② 收集（从既有 trace / 日志 / daily-memories 聚合，🚫 不额外起评测）**：
1. 每档 **run_code 平均调用次数**（Φ 执行次数）：full vs binary vs none。
2. **code-gen 墙钟 / 迭代轮次**：full ~1.5h vs binary ~4-5h vs none（待量）。
3. **gen-fail / timeout 率**随保真度下降的变化。
4. **Pass@1**（已有）+ 提交前收敛轨迹（若有）。
5. 代表性 trace 证据：binary 档 agent「盲试 / 反复迭代」的 1–2 条原文片段（截 log）。

**③ 补进论文**（`tab:ablation-harness` 附近 + §S1 正文）：
- **语义注记**：binary PASS = **1-bit exception signal（no exception raised）**，非 assertion-level correctness；none = 仅 `"executed"`。
- **echo 表**：保真度（full/binary/none）× {Pass@1, 平均 run_code 次数, code-gen 墙钟, gen-fail} —— 展示「保真度↓ → 收敛成本↑」的单调证据。

**④ 交付**：echo 数据表 + 论文改动（编译 0 error）+ 简述「强化了什么论证」。

**⑤ 纪律**：🚫 不额外起评测（readback_binary 5-run 按指令二十三继续）；数据从既有 trace 聚合、贴 `文件:行`；commit 前缀 `zhulong S1-echo:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-15（二十一）— 🧪 结合进展提「15 天窗口消融建议」· 中文 HTML· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「安排 zhulong 结合试验进展，提出进一步消融试验的建议，写成 html 中文报告。现在到论文提交 deadline 还有 15 天。」

**① 背景**：距投稿 deadline **15 天**。当前进展：B 4/4、C1 4/4、C2 4/4 已 5/5 收口（12 臂），**S1 三臂为剩余主线**（`omega_low` r1 跑中，`readback_binary` / `readback_none` 未跑）。

**② 任务**：结合**当前试验进展 + 15 天时间约束**，提出「进一步消融试验」建议，写成中文 HTML 报告。每条建议给四要素：
- **动机**：回答论文哪个开放问题 / 审稿人或读者最可能质疑什么
- **做法 + 成本**：GPU/沙盒时延 + 墙钟估算
- **优先级**：15 天窗口内「必做 / 建议 / 可选」三档
- **编排**：与 S1 主线三臂的时间线如何错开（🚫 不与 S1 冲突）

**③ 候选方向（自己 judge、不限于此，结合论文审视报告 §8「仍缺数据」清单）**：
- 可回填但未做的消融（如 `wo_selfexpl` 自探索增益 82.1 vs 79.8、配对显著性检验 McNemar/paired bootstrap、gen-fail 机制深挖、错误分析基于 5-run 代表性 run 重做）
- 其它你认为 15 天内价值最大的补充实验

**④ 交付**：`doc/ZhuLong_DAC2027/reports/report_zhulong_next_ablation_plan_zh.html`（中文自包含），文末附「**15 天排期表**」（按天列出 S1 收尾 + 各项消融）。

**⑤ 纪律**：纯写作零 GPU，在 S1 评测空窗期做，🚫 不打断 S1 主线；数字与 `MEMORY_ZHULONG.md` 执行看板一致；commit 前缀 `zhulong plan:` · 任务书 >32KB 自滚归档。

---

### 🆕 运维指令 · 2026-10-15（二十二）— 🔁 S1 重测调整：跳过 omega_low，改重测 readback_binary【用户直令 · 最高优先】【已完成·2026-10-16 归档】

> ⏩ 归档于 2026-10-16 09:01。执行结果：omega_low 跳过采信 legacy 82.8±1.0%；readback_binary fresh 5/5=78.1±1.3% [75.9,79.1,77.8,78.5,79.1] 替换 legacy 66.2±16.1%（std 16.1→1.3 大幅改善，43.0% 离群消除）；readback_none 跳过采信 legacy 73.3±2.2%。S1 done_all。下方为指令原文。

> **用户令（2026-10-15）**：「为什么要跑 S1.omega_low，这个试验在 zhulong_results 不是已经测好填好了吗？反倒是 S1.readback_binary 标准差过大，需要重测。」

**① 停止 omega_low 重跑（跳过）**：
- omega_low legacy **82.8±1.0%（std=1.0，5-run 高度一致）** 已可信，**不必 fresh 重跑**。
- 当前 omega_low r1（PID 2616015）若已跑完则收该结果即可；若仍在跑则 kill，**取消后续 r2–r5 计划**。
- 采用 legacy **82.8±1.0%** 作为 omega_low 最终值（`zhulong_results.md` 标注来源＝legacy、std 可信）。

**② 重测 readback_binary**：
- legacy **66.2±16.1%** 的 std 过大（含 43.0% 离群 run），**需 fresh 5-run 重测**得到可靠 std。
- 切配置 `readback_binary`（READBACK=binary + 核心 4 工具 + full 锚点 phi=BUDGET0/LAGGED0），`stop.sh && start.sh` 重启后跑满 5 轮。

**③ readback_none**：legacy 73.3±2.2%（std=2.2）同样可信，**暂不重跑**（与 omega_low 同理）。

**④ 纪律**：判据(十三)不变（消融臂 Pass@1 任何值有效、timeout≤10 且无 infra 故障）；重测 binary 后把 fresh 结果替换 `zhulong_results.md` 旧 legacy 值并注明；commit 前缀 `zhulong S1:` · 任务书 >32KB 自滚归档。

---

## [归档 2026-10-18 02:57] 运维令二十六 & 二十三（被运维令二十七取代）

> 搬出原因：运维令二十七（2026-10-17）对 B.glm-5.3-flash 和 B.deepseek-v4-flash 复测做了全新规格（trace 诊断 + maxTokens 16384 + -p 调整），并明确 wo_selfexpl r2-r5 不再跑（r1=83.5% 收口）。运维令二十三（原编排）与二十六（wo_selfexpl 排队）均被取代/闭合，原文搬入此处，TASK 留 1 行指针。

### 运维指令 · 2026-10-16（二十六）— 🔜 排队：B.deepseek-v4-flash 之后接 wo_selfexpl 干净 5-run【用户直令·已被二十七取代·2026-10-18 归档】

> **用户令（2026-10-16）**：「B.deepseek-v4-flash 之后跑 wo_selfexpl，记录排队。」

**① 排队顺序**（如无新指示，**自动接续**）：
1. **B.glm-5.3-flash**（在跑，运维令二十三，r1✅80.4% / r2 跑中）→ 5/5 收口
2. **B.deepseek-v4-flash** fresh 5-run（运维令二十三，替换 legacy 16.7±12.3% std 过大）
3. **🆕 C1.wo_selfexpl 干净 5-run**（本指令新增）→ 替换当前带 † 脚注的 81.4±4.1%

**② wo_selfexpl 干净 5-run 规格**：
- 配置：V2 文档（**自探索 OFF**）+ 检索 ON + 沙盒 ON + 主基座 `deepseek-v4-pro-fp4`
- ⚠️ **关键**：r1 必须**严格 V2**（不得误用 V3 自探索文档——旧 r1=88.0% 即此污染，已在论文 `tab:main-ablation` 标 † 脚注）
- 判据(十三)：timeout≤10 且无 infra 故障，Pass@1 任何值有效
- 5-run 收口后：算 mean±std → 回填 `tab:main-ablation` 的 `ZhuLong w/o Self-Expl.` 行（移除 † 脚注）+ 同步 `zhulong_results.md` C1.wo_selfexpl 节 + 正文 Δ

**③ 纪律**：切配置后 canary 自检；commit 前缀 `zhulong C1:`；/home<8G 暂停清理。

**闭环状态（2026-10-18）**：被运维令二十七①取代——wo_selfexpl r1 regrade 已由运维侧手动启动（batch 2026_1017_055109），r1=83.5%(132/158) 收口，**r2-r5 不再跑**（陈熙元已测 wo_selfexpl = 77.3±2.9% 作为对照）。

### 运维指令 · 2026-10-15（二十三）— 🔜 S1.readback_binary 后编排：B.glm-5.3-flash → B.deepseek-v4-flash【用户直令·已被二十七取代·2026-10-18 归档】

> **用户令（2026-10-15）**：「告诉 zhulong，S1.readback_binary 测完后，如无其它指示，则按次序测 B.glm-5.3-flash（GLM-5.3 Flash）→ B.deepseek-v4-flash（DeepSeek-V4 Flash）。」

**① 编排**（`readback_binary` 5-run 重测完成后，如无新指示，**自动接续**）：
1. **B.glm-5.3-flash**（新加 B 模型消融臂，跑 5-run）：
   - model：`glm-5.3-flash`
   - API Key：`02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f`
   - Base URL：`http://agi-gateway.cxmt.com/v1`（⚠️ `/v1`，非 `/cloud/v1`）
2. **B.deepseek-v4-flash**（重测 5-run）：legacy `16.7±12.3%` 有 r5=37.3 离群、std 过大 → fresh 5-run 修正 std。

**② 做法**：与 B 臂既有口径一致（full harness + V3 自探索，主基座 deepseek-v4-pro-fp4 不变，**仅替换被评测 backbone** key/endpoint）；判据(十三)（消融臂 Pass@1 任何值有效、timeout≤10 且无 infra 故障）。

**③ 完成**：填 `zhulong_results.md` B 臂表（新增 glm-5.3-flash 行 + 替换 deepseek-v4-flash 为 fresh 值）。

**④ 纪律**：每臂切配置后 canary 自检；commit 前缀 `zhulong B:` · 任务书 >32KB 自滚归档。

**闭环状态（2026-10-18）**：被运维令二十七取代——fresh 5-run 已出（glm-5.3-flash 66.8±10.5% std=10.5 偏大 / deepseek-v4-flash 11.9±2.7% 但 73% 失败为 infra 问题）。运维令二十七对两臂分别启动复测（deepseek-v4-flash 复测 5/5✅=60.1±5.5% 已收口；glm-5.3-flash 复测 r1 两次作废·infra 阻塞·等运维决策）。fresh 值保留为历史对照。

---

## [归档 2026-10-18 02:57] 运维指令 · 2026-10-04：环境迁移 + 合并执行方式 + ops 中继独立

> 搬出原因：合并执行已完成（单任务书 + 单 loop 运行中），起始状态已远过 init，ops 中继已稳定 6d+。infra 端口列表（8664/8665/8653/8669）已过时（实际为 8650/8651/8652/8654）。路径信息在 §6 + MEMORY 状态头已存。原文搬入此处，TASK 留 1 行指针。

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

**闭环状态（2026-10-18）**：合并执行已落地（单任务书 + zhulong_loop.sh 运行中·PID81827）；起始点已远过 init（当前 B.glm-5.3-flash 复测）；ops 中继稳定（PID1023764）；infra 端口已更新为 8650/8651/8652/8654@10.129.32.75（原 8664/8665/8653/8669 过时）。

---

## [归档 2026-10-18 02:57] proxy 重启脚本（运维指令 · 2026-10-09 子节·已执行）

> 搬出原因：该 restart 脚本已于 2026-10-08 执行完毕，loop 持续带代理运行（每次巡检确认）。常驻 self-check 规则保留在 TASK，仅 verbose 脚本搬入此处。

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

---

## [归档 2026-10-18 02:57] 运维令十三 items 3-4（phi_k3/phi_k10 历史事件处理·已闭合）

> 搬出原因：phi_k3 与 phi_k10 均已 5/5 收口（见 MEMORY 成绩表）。items 3-4 是当时的事件处理指令，已执行完毕。常驻规则（items 1,2,5 + 红线 + 背景 + 用户令）保留在 TASK。

**原 item 3**：phi_k3 r1 att1 = 72.8%（115/158, timeout=0）应判为有效。立即：
   - 如果 att2 仍在跑 → 等 att2 跑完后取 att2 的成绩（不浪费已投入的算力），记 r1 = att2 成绩；
   - 如果 att2 已跑完 → 取 att2 成绩记 r1；
   - 如果 att2 尚未开始 → 取消 att2，直接记 r1 = 72.8%，推进 r2。
   - 无论哪种情况，ERROR_COUNT 重置为 0，不因 72.8% 计错误。

**原 item 4**：phi_k10 已完成的 5/5 = [78.5, 76.6, 77.2, 81.0, 75.3] → 77.7±2.2% 保留不变（已跑完，不追溯重跑）。但须在成绩记录中标注：r3/r4/r5 经历了不必要的重试（att1 低分被误判为无效），最终取的是重试后的值；原始 att1 值（r3=74.1%, r4=63.3%/74.1%）应保留在 daily-memories 中作为证据，不删除。

**闭环状态（2026-10-18）**：phi_k3 5/5=69.1±2.5% ✅；phi_k10 5/5=77.7±2.2% ✅。两臂均收口，事件处理指令已执行。

## 归档 batch 10 · 2026-10-23（agent 自滚·09:4x 活跃块之下的已闭合运维块·原文搬迁·未改写指令）

> 搬迁自 ZHULONG_TASK.md 运维指令区 lines 38-416（09:1x → 10-19 23:2x + 已归档 batch 5~9 指针）。活跃块 09:4x 保留在任务书。

### 🟡 运维指令 · 2026-10-23 09:1x（**r4 起跑：尝试 8663 组，不可用则回退 8650 组**）· 用户直令 ·【已被 09:4x 取代·历史·r1-r3 作废·配置从 N′ 改 full】

> 用户原话：「新线不纳入论文。启动 r4 时尝试使用端口 8663/8666/8667/8670。」
> **背景**：r1-r3 已用 8650 组跑完（r1=67.1%/r2=68.4%/r3 收口待 regrade）。r3 收口于 08:52（158 dirs/136 .py/task_queue 空）。8663 组 09:07 实测：8663/8666/8667 run_code 14-18s 超时（breaker 仍 cooling）、8670 服务未起 → **4/4 不可用**。8650 组 4/4 健康（14ms 秒回）。

**① 立即执行（按序）**
1. **先 regrade r3**（batch `2026_1023_072528`·端口 8650 组·照 r1/r2 regrade 模板·`/tmp/run_glm-5.3-flash_zl_r3_regrade.sh`）。记 r3 Pass@1 + literal-pass 数。
2. **复探 8663 组**（4 端口 × run_code 真实调用，timeout 15s/端口）。判定标准：返回含 `"response"` 且 <5s = 可用；空响应/超时/breaker = 不可用。
3. **根据探活结果起 r4**：
   - **8663 组 4/4 可用** → 改 `.env` 的 `PROXY_PORTS` + `SANDBOX_ENDPOINTS` 为 8663 组（保留 workdir 映射，只换端口号）→ 重启 8090 MCP 服务 → 冒烟 run_code 4/4 OK → 起 r4（`-p 4`/`CLI_AGENT=zhulong`/`glm-5.3-flash`/端口 8663 组）。
   - **8663 组任意端口不可用** → **不换端口**，保持 8650 组起 r4（与 r1-r3 同口径）→ 报告哪些端口不可用。
4. r4 跑完 → regrade → 记 r4 → 续 r5 → 5/5 mean±std。

**② 判据不变（05:0x 令）**：`literal-pass >10 → 只记录+标退化+继续跑`；停手仅 = MCP 率 ≥5/min **且** 4 端口全不可用。

**③ 口径备注**：新线（glm-5.3-flash × zhulong）**不纳入论文**，是独立探索线。论文锚点仍用旧线 (N′) fp4×cline 的 4 轮 mean=76.7% provisional。

**④ 回报**：r3 Pass@1 + literal-pass / 8663 组探活结果（4 端口逐个） / r4 用哪组端口起跑 / r4 batch 号 + 4 端口状态。


### 🟡 运维指令 · 2026-10-23 05:0x（**用户决策 B：放弃 8663 组，用 8650 组继续跑满 5 轮**）· 用户直令 ·【已被 09:1x 取代·历史·r1-r3 已执行完毕】

> 用户原话：「zhulong：B. 用 8650 组继续」（三选中 B，不修 8663、不查根因，先用可用端口拿结果）。
> **背景**：8663/8666/8667/8670 licence breaker 持续 OPEN（548→553 连失恶化），需 ops 在沙盒侧修，**本轮不等**。8650/8651/8652/8654 已 4/4 OPEN（run_code 10-12ms OK）。

**① 判据变更（重要，先读这条）**
- ❌ 旧：`literal-pass >10 → 停手报运维`
- ✅ **新：`literal-pass >10 → 只记录 + 在结果中标注退化，继续跑、继续 regrade`**（用户已决策不中止）
- 仍保留停手条件：MCP 率 ≥5/min **且** 4 端口全不可用（基础设施真故障）

**② 立即执行**
1. **确认 .env 是 8650 组**：`PROXY_PORTS=8650,8651,8652,8654` + `SANDBOX_ENDPOINTS` 对应 `8650:...t0002997_1,...`；4 端口复探 **4/4 OPEN**。
2. **解除 BLOCKER**：r1=67.1%（16 条 literal-pass）按新判据**记为有效轮次并标注退化**，不中止。
3. **继续 r2 → r5**（`-p 4`、`CLI_AGENT=zhulong`、模型 `glm-5.3-flash`、端口 8650 组）：每轮跑完 → regrade → 记录。
4. **5/5 出 mean±std**；r1 的 16 条 literal-pass 需**单列标注**，并说明「若剔除退化题的真实通过率」（另算，供论文引用）。

**③ 每轮回报**：`batch / pass 率(N/158) / literal-pass 数 / 耗时 / 端口状态 / 5-run 累计`。


### 🔴 运维指令 · 2026-10-23 00:3x（**停 r5e3 → agent 换 zl/zhulong → glm-5.3-flash 重跑 → 端口 8663/8666/8667/8670**）· 用户直令 · 最高优先

> 用户原话：「1.zhulong 评测停下 2.重启一轮评测。使用模型 glm-5.3-flash 3.修改 eda_fastmcp/.env，将 cli agent 改成 zl 或 zhulong；重启8090端口的mcp服务.确保评测通过 zl 调用智能体 4.沙盒端口使用 8663/8666/8667/8670」
> **停跑理由**：r5e3 跑 T+12h 仅 77.8%（9.7 tasks/h，r4 是 ~32/h），效率只有 1/3。

**① 已由运维 RUN_ID 110 完成（勿重复）**：停 r5e3、备份 `.env`、探 4 端口、列出 agent 相关键名与 8090 启动脚本。

**② 你要做的（按序）**
1. **改 `.env` 的 cli agent 键** → 值改成 **`zl`** 或 **`zhulong`**（以 `eda_fastmcp` 实际注册名为准；不确定就查 tools 注册表/`sandbox_server` 源码，把键名+候选值写进 MEMORY）。
2. **端口改 8663/8666/8667/8670**：`PROXY_PORTS=8663,8666,8667,8670`；**`SANDBOX_ENDPOINTS` 必须按 `port:workdir` 格式重写**（保留原 workdir 映射，只换端口号）。4 端口必须 **4/4 OPEN**。
3. **重启 8090 MCP 服务**：用 RUN 110 [7] 找到的启动脚本；重启后 `ss -ltnp | grep 8090` 有监听 + `run_code` 冒烟通过。
4. **切换模型为 `glm-5.3-flash`**：参考 2026-10-19「运维令三十一 B.glm-5.3-flash 复测」跑法（providers.json / `cline auth -m`），**MEMORY 写明改了哪个文件**。
5. **起新一轮评测**：`-p 4`（🚫 不要 -p 8，历史证明退化）；启动前 `export PYTHON=$PWD/venv/bin/python`；`unset http_proxy https_proxy` + `NO_PROXY=10.129.32.75,localhost,127.0.0.1`。
6. **关键验证：确认评测确实经 zl 调用** —— 检查 8090 日志出现 zl/zhulong 的 tool 调用记录（不是 cline 直连）。**这条必须贴证据。**

**③ 监控口径（不变）**
- 健康 = **task 完成数单调增长**（从 codegen jsonl / task dir 数），不是 log 行数。
- 每轮 grep codegen jsonl 里字面量 `"pass"` 数（退化早期信号）。
- 停手阈值：literal-pass >10 或 MCP 率 ≥5/min。

**④ 回报**：新 batch 号 / agent 实际值 / 8090 PID / 4 端口状态 / 头 10 分钟进度 / **zl 调用证据**。



### 🔴 运维指令 · 2026-10-20 21:4x（**用户直令：杀 r4/r5/regrade → 端口换 8650/8651/8652/8654 → 重启 r4⁗**）· 最高优先【已归档·历史·r4⁗ 已收口 INVALID·已被 10:4x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 9。

### 🔴 运维指令 · 2026-10-20 21:2x（r4 疑似停滞·只读取证）·【已归档·历史·已被 21:4x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_ZHULONG.md` / `daily-memories/` / `run/` 下自建脚本 / 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`）。

### 🔄 运维指令 · 2026-10-22 10:2x（**r5e3 回到 -p 4 + 端口 8650/8651/8652/8654**）· 用户直令 · 最高优先 · 取代 09:0x

> 用户令（原文）：「好的 r5e3 回到端口 8650/8651/8652/8654 和 p=4」
> **背景**：r5e2（-p8 + 8650-8654）收口 **INVALID** —— agent 09:25 核验：**21 .py（vs r4e 156 .py）+ 593 sandbox "operation timed out" + stats success=149/timeout=9/failure=0** → **-p8 是退化根因**（8 cline 共享 4 sandbox，2×/port 争用打穿服务端 SANDBOX_TIMEOUT=150s；模型反复收 tool-error "The operation timed out" → 无法完成 code-gen → 不写 .py）。
> ⚠️ **数据完整性纠正**：08:43 心跳称"136 literal-pass"是**捏造**（codegen jsonl 从未生成）—— r5e2 退化**真实**但签名是 **.py 缺失**（21/158）非 literal-pass。STOP 阈值以 **.py 落盘率 13.3% << r4e 98.7%** 判 INVALID。
> **对照 r4e（-p4 + 8650-8654 + timeout=600）**：156 .py / 0 sandbox-timeout / **75.9%** → **-p4 是已验证的健康口径**。
> **本令核心**：r5e3 **回到 `-p 4`**（与 r1/r2/r3/r4e 完全一致口径），端口 **8650/8651/8652/8654**。
>
> ⚠️ **agent 注意：这是任务书 ZHULONG_TASK.md 运维指令区，不是 ops inbox。请立即执行本令，不要再等 ops inbox 的 ACTION 令。ops inbox RUN_ID 107 是只读探针（已执行完），与本令无关。**

#### 执行前清理（必做）
1. **清磁盘**：⚠️ /home 仅 4.5G（<8G infra 前置阈值）。r5e3 起跑前**先清磁盘**：
   - 清 r5e2 batch 残留（`/home/app.e0031982/eda_code_eval/2026_1022_001122/` 可删——r5e2 已判 INVALID 留证，但 .py 仅 21 个无 regrade 价值；**先 tar 压缩备份到 /nasdata/ 再删原目录**，或直接删——由你判断）
   - 清 r5e batch 残留（`/home/app.e0031982/eda_code_eval/2026_1021_173249/` 同理，r5e 被杀 47% 无价值）
   - 清 /tmp 旧 log（`/tmp/ABL_readback_none_retest_r5e.log`、`/tmp/ABL_readback_none_retest_r5e2.log` 可删——r5e/r5e2 已作废）
   - 清其它可回收空间（旧 batch、worker ws 临时文件等）
   - **目标**：/home free ≥ 8G（r5e3 起跑前置条件）
2. **清 r5e2 残留进程**：pgrep 确认无 r5e2/r5e 孤儿 worker（r5e2 PID 4026302 GONE·9 孤儿已清过；再核一遍）
3. **重启 4 端口沙盒 worker**：r5e2 收口后 8650/8651/8652/8654 仅 1 LISTEN → 需重启 4 端口确保全 OPEN（run_code 端到端探活 4/4 OK）
4. **8090 健康**：PID 1504991 若活则不重启；若 GONE 则重启

#### r5e3 起跑参数
- **`-p 4`**（4 并发，回到 r1-r4 口径，**关键改动**）
- 端口 `8650,8651,8652,8654`（.env 已是这组）
- 其余配置同 r4e：`READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3自探索ON / full harness / 模型 `deepseek-v4-pro-fp4` / `export PYTHON=$PWD/venv/bin/python` / cline settings timeout=600（10:4x 已改，保持）
- 日志 `/tmp/ABL_readback_none_retest_r5e3.log`；batch 新建（r5e3 编号）
- **r5e3 30min 健康报告**：
  - **.py 落盘率**（r5e2 盲点纠正——用 .py 落盘数/task_dirs，非 log grep，非 codegen jsonl）
  - **sandbox-timeout 计数**（grep log "operation timed out"）
  - **-32001 计数**（grep log "MCP error -32001"）
  - 4 端口可达性
  - **判据**：-32001=0 + sandbox-timeout≈0 + .py 落盘率 ≥80% → -p4 口径健康（与 r4e 一致）
  - **若 30min 内 sandbox-timeout 抬头（率 ≥5/min）或 .py 落盘率 <50% → 停手报运维**（-p4 也退化则需换端口 8663/8666/8667/8670 或换沙盒机/错峰）
- r5e3 收口 → regrade（端口 8650/8651/8652/8654·unset proxy + NO_PROXY=10.129.32.75 + EVAL_FW_DIR）→ 判据十三 → **5/5 mean±std（r1=78.5, r2=70.9, r3=81.5, r4e=75.9, r5e3）** → 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮

#### 纪律
- 🚫 不动 r1/r2/r3 产物与 r3 backup；🚫 不动 r4 家族 + r5e/r5e2 原始产物日志（留证——r5e2 batch 目录若删前必须 tar 备份到 /nasdata/）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不动 cline settings timeout=600。
- 🚫 **不再用 -p 8**（实测打穿服务端 sandbox timeout·21/158 .py·15:3x 令作废）。
- **若 r5e3 -p4 仍退化 → 停手报运维**（-p4 也退化说明 8650-8654 端口/沙盒机有问题，需换端口 8663/8666/8667/8670 或换沙盒机/错峰）。
- commit：`zhulong S1: r5e3 回到 -p4 + 8650/8651/8652/8654 起 (用户直令·r5e2 -p8 退化作废)`。

### 🔄 运维指令 · 2026-10-22 09:0x（**r5e3 回到 -p 4 + 端口 8650/8651/8652/8654**）· 用户直令 · 最高优先【被 10:2x 取代·历史·08:43 "136 literal-pass" 捏造已纠正】

> 用户令（原文）：「好的 r5e3 回到端口 8650/8651/8652/8654 和 p=4」
> **背景**：r5e2（-p8 + 8650-8654）收口 INVALID —— 136 literal-pass / 593 sandbox "operation timed out" / gen-success 仅 8.2% → **-p8 是退化根因**（8 cline 共享 4 sandbox，2×/port 争用打穿服务端 SANDBOX_TIMEOUT=150s）。15:3x 令预警的 -p8 离群风险实测命中。
> **对照 r4e（-p4 + 8650-8654 + timeout=600）**：151 success / 0 literal-pass / 0 sandbox-timeout / **75.9%** → **-p4 是已验证的健康口径**。
> **本令核心**：r5e3 **回到 `-p 4`**（与 r1/r2/r3/r4e 完全一致口径），端口 **8650/8651/8652/8654**（r4e 同端口，已验证 -p4 健康；r5e2 退化是 -p8 导致，非端口问题，残留风险低）。

#### r5e3 起跑参数
- **`-p 4`**（4 并发，回到 r1-r4 口径，**关键改动**）
- 端口 `8650,8651,8652,8654`（.env 已是这组，r5e2 用过但 -p8 退化非端口问题；若需可重启 4 端口沙盒 worker 确保干净）
- 其余配置同 r4e：`READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3自探索ON / full harness / 模型 `deepseek-v4-pro-fp4` / `export PYTHON=$PWD/venv/bin/python` / cline settings timeout=600（10:4x 已改，保持）
- 日志 `/tmp/ABL_readback_none_retest_r5e3.log`；batch 新建（r5e3 编号）
- **r5e3 30min 健康报告**：real_MCP_32001 + literal-pass（**查 codegen jsonl 非 log**，r4⁗/r5e2 盲点纠正）+ 4 端口可达性 + sandbox-timeout 计数
  - **判据**：-32001=0 + literal-pass≈0 + sandbox-timeout≈0 → -p4 口径健康（与 r4e 一致）
  - **若 30min 内 sandbox-timeout 抬头（率 ≥5/min）或 literal-pass >10 → 停手报运维**（-p4 也退化则需换沙盒机/错峰）
- r5e3 收口 → regrade（端口 8650/8651/8652/8654·unset proxy + NO_PROXY=10.129.32.75 + EVAL_FW_DIR）→ 判据十三 → **5/5 mean±std（r1=78.5, r2=70.9, r3=81.5, r4e=75.9, r5e3）** → 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮

#### 执行前清理
- 确认 r5e2 残留进程已清（PID 4026302 GONE·9 孤儿 worker r5e2 起跑时已清过；再核一遍 pgrep 无 r5e2 残留）
- 4 端口 8650/8651/8652/8654 探活（若不全 OPEN 则重启沙盒 worker；r5e2 收口后仅 1 LISTEN，需重启 4 端口）
- 8090 健康确认（PID 1504991 仍活则不重启；若 GONE 则重启）

#### 纪律
- 🚫 不动 r1/r2/r3 产物与 r3 backup；🚫 不动 r4 家族 + r5e/r5e2 原始产物日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不动 cline settings timeout=600。
- 🚫 **不再用 -p 8**（实测打穿服务端 sandbox timeout·136 literal-pass·15:3x 令作废）。
- **若 r5e3 -p4 仍退化 → 停手报运维**（-p4 也退化说明 8650-8654 端口/沙盒机有问题，需换端口 8663/8666/8667/8670 或换沙盒机/错峰）。
- commit：`zhulong S1: r5e3 回到 -p4 + 8650/8651/8652/8654 起 (用户直令·r5e2 -p8 退化作废)`。

### 🔄 运维指令 · 2026-10-21 15:3x（**r5e 改 8 并发**）· 用户直令【r5e2 -p8 实测退化·作废】

> 用户令（原文）：「r4e 是4并发对吧，r5e除了换端口外，改成8并发」
> **本令核心**：r5e **`-p 4` → `-p 8`**（8 cline 并发），端口仍按 14:0x 令换到 **8663/8666/8667/8670**（4 端口，8 cline 共享 4 sandbox，每端口 2 cline 排队，timeout=600 下应扛得住）。
> ⚠️ **口径备注**：r1/r2/r3/r4e 都是 `-p 4`，r5e 改 `-p 8` 会与 r1-r4 口径不完全一致 → 5-run mean±std 时**单独标注 r5e=-p 8**，若 r5e 分数与 r1-r4 离群过大需在论文里说明或考虑剔除。
> ⚠️ **风险监控**：8 cline 共享 4 sandbox + 同一台 10.129.32.75 + 同一 FlexLM → 若 r5e 30min 内出现 -32001 抬头（率 ≥5/min）或 literal-pass >10 → **停手报运维**（可能需降到 -p 6 或加端口）。

#### r5e 起跑参数（取代 14:0x 令第 5 步的 -p 4）
- **`-p 8`**（8 并发，关键改动）
- 端口 `8663,8666,8667,8670`（14:0x 令已指定，RUN_ID 102 验证全 OK 12-16ms）
- 其余配置同 r4e：`READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3自探索ON / full harness / 模型 `deepseek-v4-pro-fp4` / `export PYTHON=$PWD/venv/bin/python` / cline settings timeout=600（10:4x 已改，保持）
- 日志 `/tmp/ABL_readback_none_retest_r5e.log`；batch 新建（r5e = r5 的第 5 次尝试编号）
- r5e 30min 健康报告：real_MCP_32001 + literal-pass + 4 端口可达性 + **8 cline 调度情况**（是否所有 8 worker 都拿到 task）
- r5e 收口 → regrade（用 r5e 端口 8663/8666/8667/8670）→ 5/5 mean±std（r1,r2,r3,r4e,r5e，**r5e=-p 8 单独标注**）→ 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮

#### 纪律
- 🚫 不动 r1/r2/r3 产物；🚫 不动 r4 家族原始产物日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不动 cline settings timeout=600。
- **若 r5e 30min 内 MCP timeout 风暴（率 ≥5/min）或 literal-pass >10 → 停手报运维**（降并发或加端口）。
- commit：`zhulong S1: r4e 收口 regrade -> r5e -p 8 + 换端口 8663/8666/8667/8670 起 (用户直令)`。

### 🔄 运维指令 · 2026-10-21 14:0x（**r5e 换端口 8663/8666/8667/8670**）· 用户直令 · 最高优先【r5e -p 4 部分被 15:3x 取代】

> 用户令（原文）：「现在使用的是哪些端口，r5 使用 8663,8666,8667,8670 吧」
> **背景**：r4e 当前用 8650/8651/8652/8654（健康跑中，76% 进度，-32001=0，fix 根治）。用户要求 **r5e 换到 8663/8666/8667/8670**（r4‴ 曾用这组，换走后应空出）。ops RUN_ID 101 已下发验证这 4 端口可达性。
> **本令核心**：r4e 收口 regrade 判有效后，起 r5e 时**端口从 8650/8651/8652/8654 换到 8663/8666/8667/8670**，其余配置不变。

#### r4e 收口后执行路径
1. **r4e 收口**（pgrep 无）→ 手动 regrade（照 r4 模板改 GEN_FILE=batch `2026_1021_104432` + 端口 **8650/8651/8652/8654**·unset proxy + NO_PROXY=10.129.32.75 + EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework）
2. 判 r4e 有效（判据十三：task timeout≤10·0 infra·0 exec_err·literal-pass≈0）
3. **改 .env 端口**：`PROXY_PORTS=8650,8651,8652,8654` → `PROXY_PORTS=8663,8666,8667,8670`；`SANDBOX_ENDPOINTS` 对应改为 `8663:...,8666:...,8667:...,8670:...`（workdir 仍用 t0002997_1..4 或按现有绑定）
4. **重启 8090**（pick up 新端口）+ MCP 冒烟 5/5 + 4 端口健康探针（8663/8666/8667/8670 × 2，确认全 OK）
5. **起 r5e**：配置同 r4e **仅换端口** —— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3自探索ON / full harness / `-p 4` / 模型 `deepseek-v4-pro-fp4` / **端口 `8663,8666,8667,8670`** / `export PYTHON=$PWD/venv/bin/python` / cline settings timeout=600（10:4x 已改，保持）
6. r5e 30min 健康报告（real_MCP_32001 + literal-pass + 4 端口可达性）
7. r5e 收口 → regrade → 5/5 mean±std（r1,r2,r3,r4e,r5e）→ 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮

#### 纪律
- 🚫 不动 r1/r2/r3 产物与 r3 backup；🚫 不动 r4 家族原始产物日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不动 cline settings 的 timeout=600（10:4x 修复保持）。
- **若 8663/8666/8667/8670 验证不健康（breaker/空响应）→ 停手报运维**，不强行起 r5e（继续用 8650/8651/8652/8654 或等运维另指定）。
- **若 r5e 30min 内再现 MCP timeout 风暴（率 ≥5/min）或 literal-pass >10 → 停手报运维**。
- commit：`zhulong S1: r4e 收口 regrade -> r5e 换端口 8663/8666/8667/8670 起 (用户直令)`。

### 🔄 运维指令 · 2026-10-21 10:4x（**参考 t0002147 配置修复 cline settings + .env → 重跑 r4⁗**）· 用户直令 · 最高优先【r4e 跑中·r5e 部分被 14:0x 取代】

> 用户令（原文）：「请你分析一下代码，看看问题能否修复」+「好的 按照 t0002147（陈熙元）的做法改 cline settings 好了。其它的配置也可以参考他们」
> **根因分析结论**（代码层面，带行号证据）：r4 家族 5/5 全 INVALID 的根因 = **cline 客户端 MCP 60s 缺省超时**（`~/.cline/data/settings/cline_mcp_settings.json` 无 `timeout` 字段 → 回退 60s）× **t0002147 的 64 worker 在同一台 10.129.32.75 + 同一 FlexLM 并发争用** → run_code P95 从 <60s 抬到 >60s → cline 单方面 abort 产生 -32001 风暴 → 模型在持续 tool-call 失败后退化为输出 literal "pass"。
> - **对照 t0002147**：他们的 `cline_mcp_settings.json` 有 `"timeout": 600`（10min）→ 所以他们的 64 worker 不中招。**这就是现成的成功案例。**
> - **服务端无 60s 超时**：eda_fastmcp `SANDBOX_TIMEOUT=150s` + eda_sandbox_lite `EXEC_TIMEOUT` 都 >60s → 客户端先放弃。
> - **换端口无效**：8650/8651/8652/8654 都在同一台 10.129.32.75 + 同一 FlexLM → 端口隔离不了 CPU/licence。
> - **licence fix（15:4x）已压住 breaker**：r4‴/r4⁗ 的 circuit_breaker=0 → 剩下的纯粹是 client-side 60s timeout。
> - **退化签名**：literal "pass" 不是 eda_fastmcp 返回的（`tools/run_code.py:62` 成功路径只回 `{"response":"executed"}`），是 cline 在 60s abort 后把 -32001 喂回模型 → 模型退化为输出文本 "pass" 结束 turn。

#### ① 参考 t0002147 改 cline_mcp_settings.json（核心修复）

t0002147 的配置（`/home/app.t0002147/.cline/data/settings/cline_mcp_settings.json`，已实测读取）：
```json
{
  "mcpServers": {
    "EDA_MCP_server": {
      "url": "http://10.251.36.15:18889/mcp",
      "type": "streamableHttp",
      "timeout": 600,
      "disabled": false,
      "autoApprove": [
        "search_apis",
        "get_api_details",
        "search_apis_by_keyword",
        "run_code"
      ]
    }
  }
}
```

**ZhuLong 当前配置**（`/home/app.e0031982/.cline/data/settings/cline_mcp_settings.json`）缺 `timeout` 字段 + autoApprove 用旧工具名 `run_pyAether_code_tool`（0731 已改名 `run_code`）。

**改成**（对齐 t0002147，但 url 指向 ZhuLong 自己的 8090）：
```json
{
  "mcpServers": {
    "pyAether_MCP_server": {
      "url": "http://10.251.36.15:8090/mcp",
      "type": "streamableHttp",
      "timeout": 600,
      "disabled": false,
      "autoApprove": [
        "search_apis",
        "get_api_details",
        "search_apis_by_keyword",
        "run_code"
      ]
    }
  }
}
```

**改动点**：
1. **加 `"timeout": 600`**（对齐 t0002147，10min，>服务端 150s HTTP timeout，让服务端先返回真实结果）
2. **autoApprove 改 `run_pyAether_code_tool` → `run_code`**（0731 改名后的正确工具名，t0002147 用的是 `run_code`）
3. **autoApprove 加 `search_apis_by_keyword`**（t0002147 有，ZhuLong 缺）

**备份**：改前 `cp ~/.cline/data/settings/cline_mcp_settings.json ~/.cline/data/settings/cline_mcp_settings.json.bak.20261021_104x`。

#### ② 参考 t0002147 改 .env（辅助配置对齐）

t0002147 的 `.env`（`/home/app.t0002147/mcp_0917/eda_fastmcp/.env`，已实测）与 ZhuLong 对比，**以下对齐**（仅加缺失项，不动已有值）：

| 配置项 | t0002147 | ZhuLong 当前 | 操作 |
|:--|:--|:--|:--|
| `RAG_RECALL_TIMEOUT` | `25` | **未设** | 加 `RAG_RECALL_TIMEOUT=25` |
| `EDA_RUNCODE_GUARDRAILS` | `false` | **未设** | 加 `EDA_RUNCODE_GUARDRAILS=false` |
| `EDA_RUNCODE_READBACK` | **未设**（t0002147 不做 readback 消融）| `none` | **不动**（ZhuLong (N′) 唯一变量，保留）|
| `PROXY_PORTS` | `8656,8658,8661,8662`（他们的）| `8650,8651,8652,8654` | **不动**（ZhuLong 自己的端口，与 t0002147 不冲突）|
| `SANDBOX_ENDPOINTS` | `8656:t0002441_9,...`（他们的）| `8650:t0002997_1,...` | **不动**（同上）|
| `EDA_OMEGA_FIDELITY` | `high` | `high` | 已一致 ✅ |
| `EDA_PHI_BUDGET` | `0` | `0` | 已一致 ✅ |
| `EDA_PHI_LAGGED` | `0` | `0` | 已一致 ✅ |
| `SKILL_DATA_DIR` | `./docs/skill_data_selfexpl` | `./docs/skill_data_selfexpl` | 已一致 ✅ |
| `SANDBOX_TIMEOUT` | `150` | `150` | 已一致 ✅ |
| `EVAL_SANDBOX_WORKERS` | `4` | `4` | 已一致 ✅ |

**注意**：
- t0002147 用 cline 3.0.66，ZhuLong 用 cline 3.0.51。**不升级 cline 版本**（3.0.51 是 ZhuLong 锚点臂的复用基线，升级会破坏与 r1/r2/r3 的口径一致性）。
- t0002147 用自己的端口 8656/8658/8661/8662（workdir t0002441_9..12），ZhuLong 用 8650/8651/8652/8654（workdir t0002997_1..4）→ **端口不冲突，各用各的**。

#### ③ 重启 8090 + 验证 4 端口健康
- 改完 .env 后重启 8090（pick up 新配置）。
- 4 端口 run_code 健康探针（8650/8651/8652/8654 × 2 次，确认返回 `{"response":...}` 且无 breaker/空响应）。
- MCP 冒烟 5/5。

#### ④ 重跑 r4⁗（第 6 次，配置同 r1-r3 + 新 cline settings）
- **先标 r4 家族 5/5 全 INVALID**（r4/r4′/r4″/r4‴/r4⁗ 均作废不进 5-run，产物日志留证）。
- **r4⁗ 起跑**：配置与 r1-r3 完全一致 + 新 cline settings（timeout=600）—— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3自探索ON / full harness / `-p 4` / 模型 `deepseek-v4-pro-fp4` / 端口 `8650,8651,8652,8654` / `export PYTHON=$PWD/venv/bin/python`。
- 日志 `/tmp/ABL_readback_none_retest_r4e.log`（r4⁗ 已用 r4d4，本次用 r4e）；batch 新建。
- **r4⁗ 30min 内必报**：real_MCP_32001 计数 + literal "pass" 计数 + 4 端口可达性。
  - **判据**：超时率 ≤ ~0.001/行 + literal-pass ≈ 0 → fix 根治。
  - **若 30min 内仍 MCP timeout 风暴（率 ≥5/min）或 literal-pass >10 → 停手报运维**（client timeout 修复无效，需考虑换沙盒机）。
- r4⁗ 收口 → r5⁗（同配置同端口）→ 5/5 mean±std（r1,r2,r3,r4⁗,r5⁗）→ 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮。

#### ⑤ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′/r4″/r4‴/r4⁗ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不升级 cline 版本（保持 3.0.51）。
- 改 cline settings + .env 前**先备份**。
- **若 r4⁗ 30min 仍退化 → 停手报运维**，不盲目第 7 次重跑（考虑换沙盒机/错峰）。
- commit：`zhulong S1: 参考 t0002147 修复 cline settings(timeout=600) + .env 对齐 -> 重跑 r4''''`。

### 🔄 运维指令 · 2026-10-20 15:4x（**licence fix 已部署 → 验证 4 端口 → 重启 8090 → 重跑 r4‴**）· 用户直令 · 最高优先【已归档·历史·已被 10:4x 取代·未根治】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 9。

### 🔄 运维指令 · 2026-10-20 10:1x（09:0x 令作废·继续按 08:2x 跑 r4″→r5″）·【已归档·历史·已被 15:4x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。


### 🔄 运维指令 · 2026-10-20 09:0x（先 regrade r4′ 看成绩）·【已归档·历史·作废·基于误判·已被 10:1x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。


### 🔄 运维指令 · 2026-10-20 08:2x（停 r4′→重启 8090→换端口 8663/8666/8667/8670 重跑 r4″）·【已归档·历史·已被 09:0x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。


### 🔄 运维指令 · 2026-10-20 06:3x（停 r5→重启 8090→重跑 r4/r5）·【已归档·历史·已被 08:2x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。



### 🔬 运维指令 · 2026-10-20 06:0x（P0：r4=31% 根因排查·680 timeout 归因）·【已归档·历史·已闭合】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。



### 🔒 运维指令 · 2026-10-19 23:2x（**模型口径锁定：r4/r5 用 fp4；full 用 pro-cloud**）· 用户直令 · 与 23:0x 块同等最高优先

> 用户确认（原文）：「**r4/r5 继续用 fp4，但跑 full 的时候，切换到 deepseek-v4-pro-cloud。**」
> 这是对 23:0x 块的**最终口径裁定**，覆盖任何歧义。

**① 臂 × 模型对照（严格照此执行，不得自行调换）**

| 阶段 | readback 档 | **模型 / endpoint / key** | 轮数 |
|:--|:--|:--|:--:|
| r4, r5 | (N′) `READBACK=none` | **`deepseek-v4-pro-fp4`** @ `/cloud/v1`，key 末 8 = **`8aa0785e`** | 各 1 轮 → 凑满 5/5 |
| full 复测 | (F) `READBACK=full` | **`deepseek-v4-pro-cloud`** @ `/cloud/v1`，key 末 8 = **`8aa0785e`** | 5 轮 |

> ⚠️ **两臂用的可能是同一个 key `...8aa0785e`**（03:50 探针显示该 key 对 fp4 与 cloud 都返回 200）。**“用 deepseek-v4-pro-cloud 的 apikey” = 换模型名 + 用能访问 pro 族的那个 key**；`88ea2f23`（glm 的）对 pro 族**必 403**，禁用。

**② 起跑前必做「模型落点自检」（防止模板复制带错模型）**
> 背景：源码注释显示 worker 的 `settings/providers.json` 由 `prepare_cli_env` 从 `$CLI_DATA_DIR(~/.zhulong)` 复制而来，而 `~/.zhulong/settings/providers.json` 当前是 **`glm-5.2`**（那是**编排模型**，给 opencode 用）。RUN_ID 89 实测该字段确实是 `glm-5.2` —— 所以**不能只看它**，必须看 **worker 实际生效的那份**。
- **r4/r5 起跑前**：`ls -dt ${CLI_ISOLATION_DIR}/worker_*/data/settings/providers.json | head -1 | xargs grep -o '"model"[^,]*'`
  → **必须是 `deepseek-v4-pro-fp4`**；若是 `glm-5.2` / `pro-cloud` / 其它 → **先修正模板再起跑**，并把 before/after 原文贴进回报。
- **full 臂起跑前**：同一检查点 → **必须是 `deepseek-v4-pro-cloud`**。
- 同时贴 `/proc/<cline worker pid>/environ` 里与模型相关的键（若有），双证。

**③ 口令（两臂都要在日志首行写明）**
- r4/r5：`ARM=(N') MODEL=deepseek-v4-pro-fp4 KEY=...8aa0785e READBACK=none`
- full：`ARM=(F) MODEL=deepseek-v4-pro-cloud KEY=...8aa0785e READBACK=full`

**④ 报告口径**
- `(N′) 5/5` 与 `(F)@pro-cloud 5/5` **分表列示**，不得合并计算。
- full 臂须注明：「**与既有 (F)（fp4）相比，模型部署不同（cloud vs fp4），不可直接混算**」。
- n<5 不写 ±。

**⑤ 端口（两臂统一·用户 23:3x 直令）**
- **`8666 / 8667 / 8669 / 8670` @ 10.129.32.75** —— RUN_ID 90 普查（23:21，21 端口 × TCP+真实执行）：这 4 个 `TCP_OPEN` 且 **14/15/15/14 ms**，全部 USABLE；**远离 t0002147 长期占用的 8650/8652/8654**，撞车概率最低。
- 起跑前逐端口 10s 内 POST 探活；BUSY 按序降级：`8665 → 8664 → 8663 → 8662 → 8661 → 8660 → 8658 → 8657`。
- 🚫 禁用 `8650/8652/8654`（占）、`8659/8668`（7.1–7.3s 慢，会拖慢整轮）。
- 报告里列出**实际使用的 4 个端口 + 每次探活结果**。



> 用户令（原文）：「zhulong 启动 r4/r5。跑完 (N′) 5-run后，再测一次 full，这次用 deepseek-v4-pro-cloud 的apikey」
> 前置已达成：**r3 ✅ 81.5% (123/151)**（Path A 修复，4 shard 31/30/31/31 极一致）；当前 3/5，mean 76.97% provisional。

**① r4 + r5（串行，先把 (N′) 5-run 补齐）**
- 配置**完全不变**：(N′) 唯一变量 `EDA_RUNCODE_READBACK=none`、OMEGA=high、BUDGET=0、LAGGED=0、V3 自探索 ON、full harness、`-p 4`、模型 **`deepseek-v4-pro-fp4`**（**不要换**）、cline 3.0.51 不动。
- **端口**：**统一用 `8666 / 8667 / 8669 / 8670`**（用户 23:3x 直令；RUN_ID 90 实测 14–19ms 全可用，且远离 t0002147 占用的 8650/8652/8654 段）⇒ **起跑前对每个端口做 1 次 10s 内 POST 探活，BUSY 的按序换下一组：`8665 → 8664 → 8663 → 8662 → 8661 → 8660 → 8658 → 8657`**（🚫 **禁用** 8650/8652/8654 被占、8659/8668 慢 7s）。
- 每轮结束：`ps -p <PID>` 判 GONE → 若 Step 7.1 auto-grade 报 FileNotFoundError，**沿用 r1/r2 的手动 regrade 模板**（`unset proxy` + `NO_PROXY=10.129.32.75` + `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework`）。
- **若 regrade 再次出现 shard 全 timeout**：直接复用 r3 成功的 Path A 手法 —— `run_on_sandbox.py` 按 shard 直跑、绕开 `run_eval.py` 分片，写**独立输出文件**（`execution_results_shard_N_retest.jsonl`），不覆盖原产物。
- 判据（十三）：`timeout ≤ 10`、0 infra、0 exec_err。Pass@1 任何值有效，**不因低分重跑**。
- 收口后：**5/5 mean ± std** 写入 `zhulong_results.md` S1.readback_none 节 + `6_exp.tex` `tab:readback-cost` (N′) 行 + `tab:ablation-harness` (N) Mean read-backs；**n<5 不得写 ±**。

**② 5-run 收口后 → 再测一次 full（用 `deepseek-v4-pro-cloud` 的 key）**
> ⚠️ 用户指定「用 deepseek-v4-pro-cloud 的 apikey」。**执行前必须先做 canary**，不许直接开 5-run：
> 1. **canary**（本机 `.29` 直连、剥 proxy、**不打印 key**）：`deepseek-v4-pro-cloud` @ `/cloud/v1`，用**现有 key 逐个试**，记录 `HTTP` + `model` 字段 + `content` 是否非空。
>    - 已知可用：key 末 8 位 **`8aa0785e`**（`02_088EE9...e13f4f37-...-044c8aa0785e`）→ 10-19 03:50 探针 `deepseek-v4-pro-cloud` **HTTP 200** ✅。
>    - 已知不可用：`88ea2f23`（glm 的 key）访问 pro 族 **必 403**（该 key 无 pro 家族权限）。
> 2. **只有 canary 200 且 content 非空**才开跑；403/429/空内容 → **报 blocker，贴 HTTP 原文，不自行改用其他 key 硬跑**。
> 3. **「full」= readback 的 F 档（`EDA_RUNCODE_READBACK=full`）**，不是 (N′)。这是**新的对照臂**：`(F) 档 × deepseek-v4-pro-cloud`。
>    - 其余配置对齐现有 (F) fresh 5-run（OMEGA=high / BUDGET=0 / LAGGED=0 / V3 自探索 ON / full harness / `-p 4`）。
>    - 跑 **5 轮**，每轮同 ① 的 regrade 与 Path A 兜底手法。
> 4. **口径披露（必须写进报告）**：这一臂与既有 (F) 的差别是 **模型部署不同（cloud vs fp4）**，须在 `zhulong_results.md` 与论文表**显式注明**「cloud vs fp4 部署不同，不可与既有 (F) 行直接混算」；n<5 不写 ±。
> 5. 5 轮收口后：mean±std → 新表行 `(F) @ pro-cloud` → 更新 MEMORY + `zhulong_results.md`，commit `zhulong B: full × pro-cloud 5/5`。

**③ 纪律**
- 串行：先 r4→r5 收口，**再**做 ②，不得交叉并行抢端口。
- 🚫 不改 `run_cli.sh` / `run_cline_script.sh` / cline 版本；🚫 不动 t0002147；🚫 不杀 loop/relay。
- 端口探活与 kill 一律**显式 PID**（🚫 `pkill -f` 带自身子串）；长输出必须 `cut`。
- MEMORY 心跳 **≤6 行**（文件已 33KB，每次唤醒先滚 1-2 条旧 📦 块到 daily）。


### 📦 已归档（06:3x，batch 5）：三十（P1 排队 N′/B 成本）

> **已闭合**：(B) 成本 5-run 零 GPU 完成（22.3±3.3 / 3.73±0.72h / 7.6±3.4）；(N′) 5-run 进行中（本文件 06:3x 块承接）。原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。



---

## 归档 batch 11 · 2026-10-24（10:3x 活跃块之下的已闭合论文块·原文搬入）

> 以下 7 个论文运维块均已闭合（6p 精简 + §4.2 A 路线重写 + 价值主张重定位 + 长鑫落地口径 + 否决保 6 backbone → 全部执行于 commit `d2d9bb7a`「zhulong paper: 按精简报告改 6 页版 (12p->6p)」）。原文搬入此处，留 1 行指针在 ZHULONG_TASK.md。

### ✅ 最终裁定 · 2026-10-24 10:2x（**走 A 路线最终写法：3-4 行引理 + 场景论证 + 实验对应，不推导**）· 用户直令 · 覆盖前一块的(a)(b)待确认

> 用户原话：「我建议**走 A 路线，但把 A 写成一个"有引用支撑的命题"，而不是"直接抄一个已知界"**……**你确认"转移确定性"这个论证可以写，我就把 4.2 按 A 重写成 3-4 行的引理 + 场景论证 + 实验对应**」
> **裁定：走 A。用户已认可"转移确定性"论证可写。按下面三句话落地，🚫 不要自行推导。**

**① 为什么是 A（写进 MEMORY 备查，不进论文）**
1. **A 的风险不在严谨性，而在"审稿人是否接受简化"** —— 而 EDA 场景下这个简化**是真实属性，不是妥协**（见 ②-a）。
2. **B 的代价是"自己推的界会被逐行审"** —— 6 页论文里为 3-4 行引理承担"推导被挑错"的风险性价比低；自己推最好的结果≈文献、最坏是常数错。
3. **A 的独特优势：ε 同时成为理论与实验的变量** —— 回读三档就是在操纵 ε，backbone 轴改变 K，**理论与实验共用同一个变量**。B 路线若 ε 定义（KL vs TV / 不同范数）与实验对不上，会导致理论与实验脱节。

**② §4.2 的最终写法（3-4 行，严格按此，不要展开推导）**

**a) 场景论证（替代"简化假设"的辩护，这是关键）**
> EDA 设计数据库的转移是**确定性的**：`run_code` 执行一段脚本，对设计库的改动是确定的 —— **同一动作在同一状态下产生同一结果，不存在动作随机性**。故 **T 精确不是简化，而是场景的真实属性**。唯一失配在观测似然 Ω：检索返回的文档可能不完整、执行回读可能截断 —— **这正是 ε 要刻画的**。

**b) 引理（引用支撑，不推导）**
> 设观测保真度 `ε ≜ sup_θ ‖p(·|θ) − p̂(·|θ)‖_TV`（真实与 agent 所用观测似然的全变差）。由标准 POMDP 鲁棒性结果 [引用]，`D_grounding ≤ g(ε)`，其中 **g 只依赖 ε、不依赖先验 K 的复杂度**，且**当 ε→0 时 g(ε)→0**。
> - 引用要求：**引 1-2 篇支撑"ε 形式界"的文献**（POMDP 模型失配鲁棒性 / 近似 POMDP 误差传播 / Bayesian robustness）。**必须核对文献真实存在且结论对口，不许硬凑。**

**c) 实验对应（把理论和实验缝起来）**
> 回读三档（**N′ / B / F**）操纵 ε **由大到小**，**Table 5 的单调增益即 g(ε) 的单调性**；**backbone 轴（Table 8）改变 K 而 ε 固定**，其 **22.0 pp 跨度远小于 ε 轴的 57.4 pp**，与"**g 不依赖 K**"一致。

**③ 必须修的符号错误（上一块已提，此处强调）**
- Eq.2 右边改 **纯先验 `p_K(·)`**，**去掉 `|o_{1:t}`**（当前写法"仅先验却条件在观测上"自相矛盾，是硬伤）。

**④ 必须保留的**
- **Eq.1 保留**，但要在公式旁点一句：**"Ω 的具体实现 = 检索 + 执行回读"这个映射才是本工作对 POMDP 栈的贡献**（否则审稿人会问"这不就是 Kaelbling 1998"）。
- **§4.3 映射压成 3 句但保留** —— **ε 的定义需要 Ω 的实现作落点**，不能全删。
- **四处措辞统一**：Abstract / Intro / §4.2 / Conclusion 统一说 **"Bayesian argument"** 或 **"formal bound"**，不许一处 Bayesian 一处只说 argue。

**⑤ 篇幅**
理论章 0.45p → **约 0.8p（+0.35p）**，从实验章省（`tab:cost` 移附录 −0.45p + Table 9 改文字 −0.25p），**净余 0.35p 给 deployment**；总体仍 **≤6.0 页**。
🚫 backbone 6 个模型不许删（见否决令）。

**⑥ 交付**：改完编译 → 贴页数 → 贴 §4.2 全文（含引理与引用）→ commit+push。


### 📐 理论章重写令 · 2026-10-24 10:0x（**保留公式 + 修 Eq.2 符号 + 补 ε-bound 引理 + 4.3 映射压缩保留**）· 用户直令 + 同行意见 · 最高优先

> 用户原话：「我赞同保留公式。在 agent 落地这个方向，理论严谨性确实是稀缺品……但是朋友对于理论如何跟实验结果形成合力，有一些意见，供 zhulong agent 参考」
> **结论：公式保留，但当前 Eq.1/Eq.2 是"定义"不是"论证"，直接留会被审稿人挑符号错误和"bound 没证"。必须重写 §4.2。**

**① 先看三个弱点（同行指出，已核实成立）**

| # | 问题 | 严重度 |
|:--:|---|---|
| 1 | **Eq.1 是标准 POMDP 滤波，没有 EDA 特化**。审稿人会问"这不就是 Kaelbling 1998？"。**新的是 "Ω 的实现 = 检索+执行回读" 这个映射，但公式里没体现**（只在 §4.3 文字说） | 🟠 中 |
| 2 | **Eq.2 符号错误（硬伤）**：`D_KL(p(·\|o_{1:t},K,env) \|\| p_K(·\|o_{1:t}))` —— **右边"仅先验"却条件在 `o_{1:t}` 上，定义自相矛盾**。严格应为 `D_KL(p(·\|o_{1:t},K,env) \|\| p_K(·))`，**右边纯先验，不条件任何观测** | 🔴 **高（一眼可见）** |
| 3 | **"bounded by observation fidelity" 在公式里没有证明**：Eq.2 只**定义** gap，没**证明**它被 Ω 保真度约束。**这是理论与实证之间最大的裂缝** | 🔴 **高** |

**② 必须补的引理（把"定义"变"论证"，这是核心）**

设观测通道保真度
```
ε ≜ sup_θ ‖ p(·|θ) − p̂(·|θ) ‖_TV
```
（真实观测似然 vs agent 使用的似然之间的全变差距离），则对任意先验：
```
D_grounding ≤ 2ε / (1 − ε)    （量级界）
```
**关键性质必须写明**：**该上界只依赖 ε（观测保真度），不依赖先验 K 的复杂度**。
- 先验再强，ε≠0 时 gap 下不去；
- ε→0 时 gap→0，与 K 无关。

**这就是核心 claim 的形式化**：`bounded by observation fidelity, not model scale`。

**③ 理论与实验的闭环（必须写进 §4.2 或 §4.4，这是加分项）**
> **理论预测 = gap 随 ε 减而减、与 K 无关**
> **实验验证 = 两侧同时验证**
> - **Table 5 的 N′→B→F 轴 = 在减小 ε**（回读保真度：无→二值→全观测）
> - **Table 8 的 backbone 轴 = 在改变 K**
> → 实验正好从 ε 和 K 两个方向验证同一命题。**这个闭环比"公式定义 gap + 实验报数字"强得多。**

**④ 具体三处改动**
1. **修 Eq.2 符号**：右边改纯先验 `p_K(·)`，去掉 `|o_{1:t}`。
2. **补 bound 引理（3–4 行）**：引入 ε，给 `D_grounding ≤ g(ε)`，明确写"g 不依赖 K 的复杂度"。**可引用 POMDP 鲁棒性/模型失配的标准结果**（省事、审稿人接受）或自行推导。
3. **§4.3 映射压缩但保留**：Ω/Φ/T/Π → 四工具映射压成 **3 句**，**不能全删** —— 因为 **ε 的定义需要 Ω 的具体实现作落点**（ε 就是"检索+执行回读"的保真度）。

**⑤ ⚠️ 需要用户确认的两个技术选择（**先提出问题，未确认前按默认执行并标注**）**
- **(a) 是否接受简化假设**：`转移模型 T 精确、只有观测似然失配`（这是 `2ε/(1−ε)` 成立的前提之一）。
- **(b) 引用现成的界 vs 自己推**：
  - **省事路线（默认）**：引用已知 POMDP 鲁棒性/模型失配结果 → 3–4 行引理 + cite
  - **硬路线**：自己推 → 工作量大，"稀缺品"更纯
- **默认先走 (a) 接受 + (b) 引用现成界**，并在 MEMORY 里写「待用户确认；若选硬路线再改」。

**⑥ 篇幅与账怎么算**
- 理论章 **0.45p → ~0.8p（+0.35p）**
- **这 0.35p 从实验章省**：`tab:cost` 移附录（−0.45p）+ Table 9 改文字（−0.25p）= **−0.7p**，**净余 0.35p 给 deployment**，**总账是平的**。
- ⚠️ 仍然不能删 backbone（见上一块否决令），仍要 **≤6.0 页**。

**⑦ 摘要/Intro/Conclusion 措辞必须统一（重点）**
- 既然保留公式，**"Bayesian argument" 必须保留**（先前那版删了，**要改回来**）：
  > `...and a Bayesian argument bounds the resulting "grounding gap" by observation fidelity, not model scale.`
- Intro 同理。
- **四处（Abstract / Intro / §4.2 / Conclusion）措辞必须一致**：统一说 **"Bayesian argument"** 或 **"formal bound"**，**不许一处说 Bayesian、一处只说 argue**（这正是之前"摘要说 Bayesian、正文没公式"的反向矛盾）。


### ⛔ 用户否决 · 2026-10-24 09:5x（**报告 §② #3 与"清中文注释"两条作废，改稿时不得执行**）· 用户直令 · 最高优先

> 用户原话：「1. 它的 **#3（删 2 个弱 backbone，Table 8 只留 4 模型）我不认同**。它说"保留 4 模型仍呈 22pp 跨度"——但**如果删掉 DeepSeek-V4-Flash 和 Doubao，跨度就从 22.0 缩到 8.4**，这会让"backbone 跨度 22.0 pp"这个数字在正文里**失去表格支撑**。2. 它说"**清掉所有中文翻译注释**"：**这个没必要，中文注释不占篇幅**。」

**① 否决项 A：`tab:llm-comparison` 必须保留 6 个 backbone，禁止删减**
- 报告 §② #3（第 117 行）与 §③（第 143 行）关于「删 2 弱模型（DeepSeek-V4-Flash / Doubao-Seed-2.0-Pro 移附录）」的建议 **🚫 作废**。
- **理由（用户指出，报告自相矛盾）**：删掉这两个后，backbone 跨度会从 **22.0pp 缩到 8.4pp**，而摘要/引言里 **"backbone axis spans only 22.0 pp"** 这句核心证据就**没有表格支撑**了 —— 审稿人一查表就会发现数字对不上。
- **必须做**：**Table（llm-comparison）保留全部 6 个 backbone**。若为省版面，**改为紧凑排版**（如 6 行、精简列名、去掉多余指标列），**但一个模型都不能删**。省版面请从别处找（见 ②）。

**② 否决项 B：中文翻译注释不要删**
- 报告 §② 末尾（第 107 行）「建议改稿时一并清掉中文注释」**🚫 作废**。
- **理由**：中文注释是 `%` 开头的 LaTeX 注释，**不参与渲染、不占页数**，删了纯粹白费功夫且有丢信息风险。
- **必须做**：改稿时**保留中文翻译注释**；但**可以**（可选）把它们统一压成同样缩进以保持源码整洁，**不必删除**。

**③ 替代方案：这 0.3p 从哪里补回来（按优先级）**
既然不能删 backbone，请从报告 §② 里**性价比更高且无副作用**的条目补：
1. **`tab:cost` 移附录**（报告 #?，省 ~0.3p，且不影响任何正文数字）
2. **`tab:error-categories` 改文字一句**（省 ~0.2p）
3. **`tab:phi-bound` 删 [TBD] 空列**（省 ~0.1p，不影响有效数据）
4. **Error Analysis 4 case → 1 段**（省 ~0.25p）
5. 实验章 S1–S4 正文各压到 1 段（这是原计划的主体，省 ~2p+）

**④ 复核要求（改稿后必须做）**
- ✅ 编译后**逐个核对正文里出现的所有关键数字**都能在表格里找到出处：
  `75.7%` / `18.3%` / `62.5%` / **`57.4pp`** / **`22.0pp`** / `449 tasks` / `four commercial runtimes`
- ✅ 特别确认：**`22.0pp` 必须能由保留下来的表逐行算出**（最强 - 最弱 = 22.0），**贴出这 6 个模型的完整数值 + 极差计算**。
- ✅ 页数仍需 **≤6.0**；若保留 6 模型后超页，**按 ③ 的顺序继续砍**，不许回头删模型。


### 🔨 执行令 · 2026-10-24 09:3x（**按精简报告改一版论文 → 编译 → 提交并推送，供用户审阅**）· 用户直令 · 最高优先

> 用户原话：「zhulong 精简论文的报告我看了，**安排他按此改一版，提交 & 推送我看看**。」

**① 依据**：`run/reports/report_zhulong_paper_trim_advice_zh.html`（28,389B，commit `c32342e4`）
按它的 **① 逐章诊断表 + ② 可删清单（16 条）+ ④ 6 页预算 + ⑤ 摘要/引言草稿** 执行。

**② 硬指标**
| 项 | 目标 |
|---|---|
| **正文页数** | **≤ 6.0 页**（当前 12.0 页）——编译后必须实测页数并贴出 |
| 行预算 | 按报告 §④：Abstract ~16 / Intro ~30 / Bg ~10 / Design ~26 / Grounding ~34 / Bench ~22 / **Exp ~95** / Disc ~5 / Concl ~6 ≈ **244 行** |
| 表/图 | 正文 **1 图 + 3 主表**（main-ablation + phi-bound 精简 + llm 4 模型）；其余移附录或合并 |

**③ 关键改动（按报告执行，不得走样）**
1. **实验章 6_exp.tex 从 248 非注释行 → ~95 行**（最硬一刀）：
   - `tab:cost` → 移附录；`tab:configurations` → 并入正文文字；`tab:error-categories` → 改一句文字
   - `tab:phi-bound` → 删 [TBD] 空列；`tab:llm-comparison` → 6 模型留 4
   - S1–S4 各压到 ~1 段；Error Analysis 4 case → 1 段
2. **摘要用 §⑤-A 草稿**（含末句落地佐证"hundreds of design engineers"）
3. **引言用 §⑤-B 草稿**（3 条 contribution 各一行）
4. **理论章 4_grounding 81 → ~34 行**：砍 "Two clarifications" 整段 + L99–105 设计原则展开
5. **discussion 6 条 limitations → 3 条**

**④ ⚠️ 必须同时并入 09:2x 令的价值主张（这条比报告更新）**
摘要与引言要体现：
> **coding agent 天生会做 design flow 编排**（写 Makefile/tcl 驱动/调度，串起现有 EDA 工具）
> **+ EDA scripting 能力补全工具断链**（现成工具覆盖不到、要手写胶水处，现场生成代码接上）
> **= 真实 DE 价值：flow 能完整跑通**

即：在报告的 "execution grounding" 主线之外，**把"编排 + 补断链"作为更高层的价值表现写进去**，形成「scripting → flow 编排」的递进。报告是 09:2x 之前生成的，摘要/引言草稿需按此再调整一遍。

**⑤ 交付与验证**
1. **改完后编译**（`pdflatex`/`latexmk`，与现有构建方式一致），**必须贴最终页数**（`pdfinfo` 或 pdf 页数）。
2. **若仍 > 6.0 页**：继续按报告 §② 清单再砍（每轮只砍最长的 2 条），**直到 ≤6.0 页**；每轮贴页数变化。
3. **不要破坏参考文献/图表编号**（`\ref`/`\cite` 编译无 undefined）。
4. **commit + push**：
   ```
   zhulong paper: 按精简报告改 6 页版（12p→6p）· Exp 248→95 行 / 摘要+引言重写(含编排+补断链 与 落地"数百") / 3 主表
   ```
5. **推送后回报**：页数 / 各章实际行数 / 砍掉的 16 条中执行了哪些 / 编译告警（undefined ref 等）

**⑥ 纪律**
- ✅ 原 12 页版本**先备份**（`git tag paper_12p_backup` 或复制到 `paper_12p_backup/`），不要覆盖丢失
- 🚫 不打断正在跑的评测（`dsv4pro-cline-full r1` 若仍在跑，评测不受影响，改稿是纯文件操作）
- 🚫 不改实验数据与结论数字（只精简表述，不删关键数字：75.7% / 18.3% / 62.5% / 57.4pp / 22.0pp 必须保留）


### 🎯 补正 · 2026-10-24 09:2x（**论文核心价值主张重定位：从 "EDA scripting" 升维到 "design flow 编排"**）· 用户直令 · 最高优先

> 用户原话：「zhulong 设计初衷是 EDA scripting，但 DE 用户使用最多的场景还是 **design flow 的编排**。这是 coding agent **天生具备的能力**，而 EDA scripting 能力可以支持 design flow 编排是**补全断链**（有些现成工具无法覆盖的断链，可以被 EDA scripting 轻易接上）。」
> **⚠️ 这是论文的叙事主干，必须体现在摘要/引言/结论**，不只是"落地一句话"。

**① 重新定义的价值链条（写入报告，作为论文立论）**

```
coding agent 的通用能力  →  直接可做 design flow 编排（写 Makefile/tcl 驱动/调度脚本，
                             串起现有 EDA 工具）—— 这是"天生具备"，不需要特殊训练
        +
EDA scripting 专业能力  →  补全断链（现有工具覆盖不到、或需要手写胶水的地方，
                             agent 用 pyAether/SKILL/Tcl 现场写代码接上）
        ↓
    真正的用户价值 = design flow 能被完整跑通
    （断链是 flow 跑不通的头号原因，而接断链正是 LLM 最擅长的事：写一小段新代码）
```

**② 为什么这个论点对 DAC 有说服力（报告里要论证清楚）**
- **DE 的真实工作分布**：不是天天写全新脚本，而是**编排 + 补洞**（flow 串不起来时现场补一段）。这一点决定"通用 coding 能力 > 纯 EDA 专用模型"。
- **"补全断链"是本工作的独特切入点**：现成商用工具是**闭合的**（不给你改），断链只能靠**现场生成胶水代码**；而 LLM 恰好能把"自然语言意图 → 可执行脚本"这段补上。
- **解释了为什么 benchmark 要这样设计**：我们的 benchmark 不只是"写脚本题"，而是**模拟真实 flow 中的断链场景**（如果现有 benchmark 是这样设计的，请明确指出并引用 RQ；如果不是，在报告里建议补一节说明）。
- **与落地规模自洽**：数百名工程师的价值不在于"人人写脚本"，而在于**每个人的 flow 都有跑不通的时刻**，agent 在那里补位。

**③ 报告里必须给出（中英各一）**
1. **一句话价值主张（paper pitch，≤30 词）**：
   - 中文草稿方向："ZhuLong 让通用 coding agent 直接承担 design flow 编排，并用 EDA scripting 能力补全工具间的断链——这正是 DE 日常工作中最耗时、最被忽视的一环。"
   - 英文草稿方向："ZhuLong lets a general coding agent orchestrate design flows and, where existing tools leave gaps, synthesizes the missing glue in domain scripts — precisely where DEs lose the most time."
2. **摘要重写草稿（6 页版，150-180 词）**：按「问题（flow 编排 + 断链）→ 洞察（coding agent 天生会编排，EDA 能力补断链）→ 方法 → 结果（benchmark + 落地）→ 意义」组织。
3. **引言动机段（3-4 句）**：把"DE 天天补断链"的痛点写实，再引出"为什么通用 coding agent 是正确选择"。
4. **结论段**：回扣"编排 + 补断链"这个定位，而不是只谈脚本准确率。

**④ 与既有内容的衔接（不要冲突）**
- 现有论文若以 "EDA scripting" 为标题/主线，**不必改标题**（`ZhuLong: An Execution-Grounded LLM Agent for EDA Scripting` 可保留），但在摘要与引言里**把"编排 + 补断链"作为 scripting 的更高价值表现**写出来，形成"从 scripting 到 flow"的递进。
- 6 页预算紧张，**优先保摘要 + 引言的这个叙事**，实验章可以更精简。


### 🟢 补正 · 2026-10-24 09:0x（**"长鑫落地"融入口径修正：轻描淡写提分量、留余地，不写具体 500**）· 用户直令

> 用户原话：「领导已经在跟外部厂商沟通时介绍了 ZhuLong 落地的情况，但在论文需要轻描淡写留有余地，比如不说 500（因为一直变化），而写成**数百**（就算全量 2000 人都使用数百也说得过去）」。
> **⚠️ 修正 08:3x 令 §③ 的方向**：不是去评估"能不能用/有什么风险"，而是——**这个信息有价值，要自然地融进论文，提高成果分量与录用概率，同时措辞留有余地**。

**① 写法口径（硬约束）**
- ✅ 用 **"数百"（hundreds of）** 表述用户规模，**🚫 不写具体数字 500**（用户数持续变化，写死会被质疑）。
- ✅ 用 **"已在量产级 EDA 设计流程中部署"（deployed in production EDA flows）** 这类表述，强调**工业环境 + 真实设计流**，不强调人数。
- ✅ 强调**质量维度**而非数量：覆盖 Tcl / waveview / SKILL 等多种脚本接口、真实设计数据流、长时间稳定运行。
- ✅ **轻描淡写、克制**：一句话带过即可，不单开小节炫耀；放在摘要末句 / 引言动机段 / 结论任一处（择一，不必都写）。
- 🚫 不吹"领先""首个""大规模"这类易被审稿人挑战的绝对化表述。
- 🚫 不写具体公司名吗？——**按投稿匿名要求处理**（DAC 双盲则写 "a leading memory-chip manufacturer / a production memory design house"；非双盲可直接写 CXMT）。

**② 报告里给 3 版可直接插入的句子（中英各一）**
- **版本 A（摘要末句，最克制）**：一句话点出"已在工业 EDA 流程部署，服务数百名设计工程师"。
- **版本 B（引言动机，强调痛点真实）**：从"真实设计流中的脚本编写痛点"引出，落地作为佐证。
- **版本 C（结论/实验章，强调可信度）**：作为"结果不仅在 benchmark 上成立，也在生产环境中被使用"的背书。
每版给出中英文，并标注字数占用（6 页预算下建议 **≤ 25 词**）。

**③ 一句话回答（不要再展开风险论述）**：这个信息对录用有帮助，理由 1-2 条即可（工业落地 = DAC 重视的实用性；真实部署 = 方法可信度背书）。


### 📄 运维指令 · 2026-10-24 08:3x（**审视 ZhuLong 论文 → 出中文 HTML 精简意见（DAC 正文 6 页）+ "长鑫落地"如何轻描淡写融入**）· 用户直令 · 最高优先

> 用户原话：「zhulong：安排它审视 zhulong 论文，提出精简意见（DAC 要求正文 6 页）。另外 ZhuLong 已经在长鑫落地，当前用户 500 左右。这个信息对论文是否有价值，如何融入，也写在精简意见中文 HTML 报告中。」

**① 背景**
- 论文当前 **12 页**（`cccc49c2` 从 13p 压到 12p），**DAC 正文限 6 页** → **还需砍掉约 50%**。
- 现状：`6_exp.tex` 319 行（占全文 53%）、`4_grounding.tex` 105 行，其余章节合计 ~184 行。

**② 交付物（一份中文 HTML，自包含单文件）**
`reports/report_zhulong_paper_trim_advice_zh.html`，必须包含：
1. **逐章诊断表**：`文件 | 当前行数/占比 | 建议目标 | 拟删/合并的具体段落（标行号或小节名）| 理由`
2. **可直接砍的清单**（按"性价比"排序：先砍低信息密度的过程性描述、重复叙述、legacy 对比；保留主表 + 核心结论）
3. **挪到附录/补充材料的建议**（若 DAC 允许）
4. **6 页预算分配建议**（摘要/引言/方法/实验/结论各占多少行）
5. **⚠️ 重写的摘要与引言草稿**（6 页版本，需体现"执行落地"卖点而不是压缩后的残篇）

**③ 关于「长鑫已落地」—— 按 09:0x 补正令执行（见上方最新一块）**
> ⚠️ **本节已被 09:0x 补正令取代**，请以补正令的写法口径为准：**轻描淡写融入论文、提高分量与录用概率、措辞留有余地**（用"数百"而非 500），**不要**写成"风险评估 / 审稿人会不会质疑"的论述。

**④ 纪律**
- 🚫 不改论文 .tex 源文件（本轮**只出建议报告**，改稿等用户确认）。
- ✅ 报告里的"建议删除"必须能对上具体小节名/行号，不许泛泛说"精简实验部分"。
- ⏭ 不打断正在跑的评测（`dsv4pro-cline-full r1` 仍在收尾，别 kill）。


