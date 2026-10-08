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

