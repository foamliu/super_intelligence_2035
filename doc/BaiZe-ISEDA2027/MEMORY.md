# MEMORY.md — BaiZe-ISEDA2027 **运维（operator）** 长期记忆 · **醒来先读本文件**

WAITING: 0

> ⚠️ **本文件在项目根**（`doc/BaiZe-ISEDA2027/`），是**运维侧**（指挥 4 条线的那个"我"）的状态文件。
> **不属于任何 agent 线** —— 4 条线的记忆在 `run/` 下：`MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md` / `MEMORY_VISION.md` / `MEMORY_HARNESS.md`。
> 日流水在根目录 `daily-memories/`（**不要**与 `run/daily-memories*/` 混）。
> 纪律：**`WAITING:` 只在顶部出现一次**；**≤32KB**，超限滚动到 `daily-memories/`。

---

## 0. 我是谁 / 我的角色

- 我是本项目 `doc/BaiZe-ISEDA2027` 的**外部运维**：**不登录训练机**。
- **下达通道** = 各任务书的 `## 🔧 运维指令区（OPERATOR NOTES）`（**改文件 + git commit/push**）。
- **查看通道** = 读各线的 `run/MEMORY_*.md` 顶部「进度快照」/「运维问答」+ `run/` 产物（`git pull` 即可，**不登录服务器**）。
- 我指挥的 4 条线：**pretrain**（`10.239.2.29`）· **data**（`.12`）· **vision**（`.12`）· **harness**（`.29`）。另有 **ops relay**（RUN_ID 机制，见 `run/ops/`）。

---

## 1. 每次「醒来」的固定动作（SOP）

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`
   （远端推进很快——各 agent 每次唤醒都可能 push；**不 pull 直接改会冲突**）。
2. **读本文件**：尤其 §3 在途任务 / §4 待拍板 / §5 铁律。
3. **读 4 条线状态**：各 `run/MEMORY_*.md` 顶部 + `git log --oneline -20` + `run/ops/.last_run_id`。
4. **处理回写**：有 agent 产物/答复 → 读、核、必要时答复（写进对应任务书运维指令区或该线「运维问答」）。
5. **下发新任务**：在对应任务书运维指令区加 **带日期的 block**（**越靠前越优先**；老块不改，留作历史）。
6. **提交**：`git add` **只加自己动的文件** → `commit` → `push`。**不要 `git add -A`**。
7. **回写本文件 + 当日 `daily-memories/<date>.md`**。

---

## 2. 通讯协议 / 接口（关键认知）

- **接口 = 任务书的「运维指令区」**，四条线**现在都有**：
  - `run/BAIZE_PRETRAIN_2B_TASK.md` · `run/BAIZE_DATA_TASK.md` · `run/BAIZE_VISION_TASK.md` · `run/BAIZE_HARNESS_TASK.md`
  - ⚠️ **pretrain / vision 的任务书原本没有该区，是 2026-10-03 由运维补上的**。
- **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；**新块放前面**，写清 **优先级 / 顺序 / 判据 / 铁律**。
- **各线回写位置**：`run/MEMORY_*.md`（状态头 + 进度快照 + 运维问答 + 流水）、`run/daily-memories*/`、`run/EXPERIMENTS_*.md`、各线产物目录。
- **ops relay**：还可经 `run/ops/inbox.md` 下 RUN_ID 命令（⚠️ **只执行第一个 ```bash 块**；下发须把新块放最前、旧块降级为 ```text、RUN_ID +1）。

---

## 3. 在途任务（截至 2026-10-03 ~09:00）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **pretrain** | P-5b 长跑（20B）→ 跑完**立即 P-9**（MBS/精度/seq/profiling） | `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`「P-9」节 | 🔄 P-5b ~57%，ETA 10-04 凌晨 |
| **vision** | R10③ 收尾（4 步）→ **R14**（官方仓库调研·纯CPU）+ **E1**（GPIC 规模实测）→ **R11-E/L/L2**（数据/loss/文本塔）→ **R13/R12**（待批） | `run/EXPERIMENTS_VISION_ROUND10/11.md` · `run/VISION_OFFICIAL_REPOS_SURVEY.md` | 🔄 R10_active |
| **data** | 下载巡检 + **D-CLEAN-2 ✅ 已执行**（**实收 ≈341G**，非 8.6T）+ `servers` 探查完成（=LLaVA 旧部署 974G，待批） | `run/DISK_CLEANUP_INVENTORY.md` §6 | 🔄 |
| **harness** | **H-A′ Aider Polyglot 横评** + **H-D** 5-harness 对比与 cline 机会点 | `run/harness/AIDER_POLYGLOT_COMPARE.html` · `HARNESS_COMPARE_MATRIX.html` · `CLINE_IMPROVEMENT_OPPORTUNITIES.md` | 🔄 |

> ✅ **vision 叙事已决（2026-10-03 用户）：走 A = 保持「从零训练」**（"A 本身也是为了学习"）。
> → R9 的 **~25.1% 渐近 = 从零路线的如实上限**（负结果有价值）；**loss 轴 R11 = 主线**；**架构轴非主要杠杆**。
> → 登记 **R12（候选）**：仅补 **iGVLM 式指令条件化**（TuringViT 低优先 —— attention 仅占 0.7%）；**须先报"值不值得"再批**。
> → 参考 **`run/VISION_ARCH_FRONTIER_2026.md`**（前沿 5 方向 vs 我们 R8 已测 4 个的逐项对照）。

---

## 4. 待拍板 / 我欠的答复

- [ ] **P-9 结果** → 定 **P-8 的 seq(4096/8192) / MBS / 精度(bf16/FP8)**（含 16384 是否 OOM 的长上下文边界）。
- [ ] **D-CLEAN-2 实际回收量** + **`servers`(974G, `/nas_train/app.e0031982/servers`) 是什么** → 用户定夺。
- [ ] **harness 运行主机**（`docker pull` 不通后是否需本地镜像 / 专用仓位）。
- [ ] **GPIC 已下部分的「唯一对」是否 > 18.5M**（R11-D；**按 GPIC 采样外推：GPIC 全量 ≈86M ≈0.1B**；**11:00 实测 tar 已 1198/8000 ≈12.7M 对**）。
- [ ] ⛔ **loop 优化：暂不做（用户 2026-10-03 决定）** —— `SLEEP_WAIT 1800→3600` 与「训练未完成就跳过 cline 调用」的前置检查，**都需在公司重启 loop**（假期内做不了），且 1800→3600 **会让反应变慢**。→ **待回公司后择机**。
- [ ] 🆕 **agent key 是「项目级共用 + 5h 滑动窗口」**（用户 2026-10-03 说明）→ 我们只能**降低自身消耗**；已做**任务书瘦身**（见 §6 备注）。
- [x] ✅ **`ops_relay.sh`「2 副本」= 误判，已结案（2026-10-03 RUN_ID 8 实测）**：第 2 行 `3521816` 的 **`ppid=2489749`（真 relay）且 `etimes≈0`** → 它是 relay **执行命令块时 fork 的子 shell**，不是副本。→ **唯一真 relay = `2489749`（ppid=1）**，**无需清理**；已更正 `run/AGENTS.md` §3.5(1)（判别方法是**看 `ppid`**，不是看进程个数）。
- [x] ✅ **D-CLEAN-2 已执行（唤醒 58）**：**实收 ≈341 G** —— ⚠️ **我此前报的「≈8.6 T」错了**：`laion2B-en-aesthetic` 盘点记 **8.1 T**，**实测只有 7.8 G**（128 parquet 的 **URL 元数据**）→ **G/T 单位误读、差 3 个数量级**。实删：laion2B 7.8G + zhulong 0.49G + pip 3.3G + **nemo Round1 ~310G**（`nemo_experiments` 524G→**214G**，**`p5b` 79G 保留**）。
- [ ] ⭐ **`servers`(974 G) 已探明 = LLaVA-V1.5-Qwen3-4B 旧训练部署** → ✅ **运维已批准删除** → **D-CLEAN-3 已下发**（**带 P1/P2/P3 前置检查**：无进程占用 / 无近期活动 / 无脚本引用；任一不过即停手报告）。
- [x] 🚫 **`nemo_experiments` 的 R2 近期 ckpt（~135 G）：运维决定「先不清」**（保留）。
- [ ] 🚩 **R9 的「本地 53M 上限」是 `r9_scaling.py` 的假设常量（default=53），非实测** → 按 GPIC 采样应为 **≈103M**；**必须用真实 cap 重算所有 "×N 缺口"**（已在 vision 任务书下达「口径修正」）。
- [ ] 🚩 **R8 的 6 架构是「自研 from-scratch 等参改编」，非官方实现** → 「SSM 坍缩」不得推广为对官方架构的否定；要下"前沿行不行"的结论需做 **R13（官方 vs 自研 对照）**。
- [ ] **文档口径统一**：seq 已定 4096（P-8 起），README/论文里残留的 4094 需对齐。
- [ ] 是否把关键决策合并进 `BAIZE_PROGRESS.html`（单一事实来源）。

---

## 5. 铁律与纪律

- 🚫 **绝不打断正在跑的 long-run**（尤其 **P-5b**：改 MBS/精度/seq 会让 20B loss 曲线作废）。
- 🚫 **绝不 kill 各线 watchdog loop**（`baize_*_loop.sh`）；收敛后只置 `WAITING=1` 长睡。
- **`WAITING:` 纪律**：只在各 `MEMORY_*.md` **顶部出现一次**（否则误触发 30 分钟长睡）。
- **记忆体量 ≤32KB**（4 线已达标；超限滚动到 `daily-memories*/`）。
- **不许猜**：源码结论贴 `路径:行号`；实验结论贴 **命令 + 原始输出**。
- 🚫 **不许闭门造车**（**2026-10-03 教训**）：凡涉及"别人怎么做"的结论（架构 / loss / 评测 / 数据），**必须去读官方仓库或论文原文**（能 `git clone` 就 clone），**不得凭印象或二手描述下结论**——当天我就把 R8 的**自研改编**误当成"官方实现"来下了结论。
- **预注册判据先定后测**（P-9a-ext G、R11 都用了）。
- 🔒 **红线**：`EDA-Eval-PyAether` 158 任务只读隔离区**绝不可动**；base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k 均不可删。
- ⚠️ **`run/nemo_experiments` 含 P-5b 正在写的 ckpt**，且 **P-6② 要用其中 6 个里程碑 ckpt** → 只能「先列清单、保住最晚/最优 + 里程碑，再删早期项」。
- **不占 GPU 的线**（data/harness）也要**避让 `.29`/`.12` 的训练 I/O**。

---

## 6. 关键路径与事实速查

- **关键路径**：`P-5b → P-9 → P-6② → P-8`（P-8 = Stage(i) 本体，周级墙钟，仍暂缓等 base + 配比）。
- **两条硬口径（2026-10-03 定）**：
  - **seq 统一 4096**（P-8 起）；`4094` 仅存于正在跑的 P-5b。
  - **每步 ≈ 4M token 不变量**：`4096↔GBS1024` · `8192↔512` · `16384↔256` · `2048↔2048`。**总步数 = 总token/4M，与 seq 无关**。
- **FP8 机制**：`s` 取决于 **GEMM 的 M**，大 GEMM `M = MBS × seq`；**`M≳16K` 才 `s>1`**（seq 与 MBS 是等价杠杆）。
- **vision 现状**：R9 lp 渐近 **25.1%**（当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结CLIP文本塔 + InfoNCE**；⚠️ **不是 GPIC**）；`attention flash` 仅占 GPU 自耗 **0.7%**（P-4 profile）。
- **磁盘**：`/nas_train` 207T/剩 ~31T（86%）· `/nas_inference` 剩 20T · `/nas_user` 剩 29T。
- 🪶 **任务书瘦身（2026-10-03，为省 agent key 的 token）**：loop 是 `prompt="$(< TASK_MD)"` → **任务书全文 = 每次唤醒的 prompt**。
  已把**已完成轮次**移出 prompt：**vision 92.5→11.7KB** · **pretrain 57.1→32.9KB** · **data 60.1→42KB**
  （归档：`run/vision/ARCHIVE_ROUNDS_2-9.md` · `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` · `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md`）。
  → **4 份活跃任务书 237.2 → 114.1 KB（-52%）**，每次全唤醒省 ≈**41K prompt token**。
  ⚠️ 归档文件**不进 prompt**；agent **需要时才去读**（已在各任务书里写明指引）。
- **本机（Windows 侧）**：`C:\Users\liuyu\super_intelligence_2035`（git clone）；**可 fetch/pull/push GitHub**；**不能直连 `.12`/`.29`**（SSH 超时）——**通道就是 git**。

---

## 7. 已知坑（会复发）

- `run/ops/inbox.md` **只执行第一个 ```bash 块**（踩过：RUN_ID 4 静默失效）。
- `ops_relay.sh` 会跑出**多副本**（共享 `.last_run_id` → 重复执行）→ 保留 **`etimes` 最大**者。
- **WAITING 正则**：旧版 `WAITING:[* ]*1` 误匹配正文散文 → 已收紧为行首 `^WAITING:[[:space:]]*1`。
- `baize_vision_loop.sh` 只 push 不 pull 的缺陷**未修**（运行时不宜改脚本）→ 等它停再照抄 pretrain 新版。
- 本机 PowerShell 读 UTF-8 中文会乱码——**只影响显示**；校验用 `read_files`。
- 🌐 **本机外网「时通时断」的原因已查明（2026-10-03 用户确认）**：**用户开 VPN（用于 Google 搜索）时 GitHub 不通，关掉即通** → 抓 GitHub / HF 前先确认 **VPN 已关**；断连**重试即可**，不是仓库/权限问题。
- 🔴 **cline Token 额度会耗尽（2026-10-03 实测，重要）**：`/tmp/baize_harness_loop.log` 原文
  `error: 本次Token额度已用完，请等待16分钟6秒后重试` —— **但 cline 仍返回 `exit 0`** →
  **loop 分辨不出失败，只睡 30min 再试** → 表现为**"静默变慢"**（不是挂了）。4 线**共用同一 cline 模型**时会互相抢额度。
  → 排查入口：`/tmp/baize_*_loop.log`（**注意：`.29` 上只有 pretrain/harness；vision/data 在 `.12`，其日志不在 .29**）。
- ⚠️ **`.29` 与 `.12` 的 `/tmp` 不共享** → 诊断 loop 日志必须**指明机器**；而**共享工作副本在 NFS**，所以**跨机能看到"别的线未提交的在途文件"**（这正是判断"某线是否在干活"的好办法）。
- ⚠️ **`ops_relay.sh` 的「多副本」是误判（2026-10-03 更正）**：`ps | grep ops_relay` 会看到 **2 行**，但其中一行是 relay **执行命令块时 fork 的子 shell**（`ppid` = 真 relay、`etimes≈0`）。→ **判别看 `ppid`**；**唯一真 relay 的 `ppid=1`**。🚫 **绝不要"把两个都杀掉"**（会切断远程通讯）。详见 `run/AGENTS.md` §3.5(1)。
- 💡 **诊断教训**：`baize_p5b_train.log` **只在 START/END 写**；**逐迭代日志是 `/tmp/baize_p5b.log`**（我 tail 错了文件，下次注意）。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **2026-10-03** —— 建本记忆机制（先放 `run/`，按用户要求**迁到项目根**）。当日运维侧 push **14 个 commit**（见 `daily-memories/2026-10-03.md`）：7 项处置 · P-9 规格重写（seq4096 + 4M 不变量 + seq 多点 + FP8-by-M + profiling）· 记忆滚动规程 · R11/R11-D · D-CLEAN/D-CLEAN-2（≈8.6T）· harness H-A′+H-D · `report_10_03.html`（含刷新）。
