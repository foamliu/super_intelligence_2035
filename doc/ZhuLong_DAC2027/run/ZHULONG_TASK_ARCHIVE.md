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

