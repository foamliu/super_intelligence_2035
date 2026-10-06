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
- 外层 loop 每 ~5h 兜底 commit+push（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。