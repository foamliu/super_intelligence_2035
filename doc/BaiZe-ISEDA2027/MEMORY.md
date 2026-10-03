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

## 3. 在途任务（截至 2026-10-03 ~23:25）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **pretrain** | ✅ **P-5b 已跑完（10-04 01:37，final ckpt `iter_0004771` 落盘）** → **P-6②**（6 ckpt「能力 vs token」）→ **P-9**（空窗跑 MBS/精度/seq/profiling）→ P-8 暂缓 | `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` | 🔴 曾被 cline 凭据事故**阻塞 ~9h**（GPU 空转 6h）→ **07:29 已修复复工** |
| **vision** | ✅ R9/R10/R14/E1 + **R11-L 四臂全兑现（无一翻盘）** → 🟢 **R11-L2 文本塔解冻（LoRA）已批准 = 下一优先级**（见 `BAIZE_VISION_TASK.md`「运维指令 · 2026-10-03（三）」）→ 之后 **`caption-loss-weight` 三点消融** | `run/EXPERIMENTS_VISION_ROUND11.md` · `VISION_OFFICIAL_REPOS_SURVEY.md` | ✅ **GPU 空**，等唤醒接令 |
| **data** | 下载巡检 —— 🆕 **白名单锁定 = `l1_en_hq` + `zh` + GPIC**；🔴 **立即停 `en_v1_4`**；D-CLEAN 系列 ✅ 全完成（累计回收 **≈1.31 TiB**） | `run/DISK_CLEANUP_INVENTORY.md` · `DATA_MIX_RECIPE.md` | 🔄 **唤醒 75**，等唤醒接令 |
| **harness** | ✅ **R1 无 docker 沙箱路线跑通**（django + sympy **双绿**）· **步3 适配层 + R32 5 drivers 已交付** → **步4：300 × 5 全量按序跑** | `run/harness/SWEBENCH_LITE_FEASIBILITY.md` · `r1_eval.py` | 🔄 待实跑 |

> ✅ **vision 叙事已决（2026-10-03 用户）：走 A = 保持「从零训练」**（"A 本身也是为了学习"）。
> → R9 的 **~25.1% 渐近 = 从零路线的如实上限**（负结果有价值）；**loss 轴 R11 = 主线**；**架构轴非主要杠杆**。
> → 登记 **R12（候选）**：仅补 **iGVLM 式指令条件化**（TuringViT 低优先 —— attention 仅占 0.7%）；**须先报"值不值得"再批**。
> → 参考 **`run/VISION_ARCH_FRONTIER_2026.md`**（前沿 5 方向 vs 我们 R8 已测 4 个的逐项对照）。

---

## 4. 待拍板 / 我欠的答复

- [ ] **P-9 结果** → 定 **P-8 的 seq(4096/8192) / MBS / 精度(bf16/FP8)**（含 16384 是否 OOM 的长上下文边界）。
- [x] ✅ **D-CLEAN-2 回收量已核实**：**实收 ≈341 GB ≈0.33 TiB**（远小于 `~8.6T` 预期，根因 = 盘点把 `laion2B-en-aesthetic` 的 **7.8G 误读成 8.1T**）。
- [x] ✅ **`servers`(974G) 已查清 + 已批准删除**（= `LLaVA-V1.5-Qwen3-4B` 旧训练 ckpt，2026-02 消融）→ **D-CLEAN-3 已执行，回收 ≈972 GB**；symlink 指向的外部数据集**完好**。
  → **D-CLEAN 系列全部完成，累计回收 ≈1.31 TiB**（⚠️ **教训已入库：引用他人清点数字前先核单位/量级**）。
- [x] ✅ **harness 运行主机问题已自行解决（2026-10-03）**：**R1 路线（`unshare` 用户命名空间 chroot 沙箱 + rootfs 落 `/nas_train`）跑通官方 `eval.sh`** —— **django + sympy 双绿**；`docker pull` 不通**已不再是阻塞**（L0/dockerd 配代理**已取消**）。
  → ⚠️ R1 已知风险敞口：沙箱内**挂不了 `/dev` `/proc` `/sys`**（scale 到 300 时留意）。
- [x] ✅ **GPIC 规模已实测（E1，2026-10-03）**：抽 **8 tar（index 0..1212）→ 12,537 对/tar（±2%）** → **GPIC 全量 ≈100.3M**（**证官方 100M**；旧「5 tar=86M」**因少计 png 作废**）；**已下 1213/8000 ≈15.2M**。
  → **C1 口径定案**：**R9 用过 18.5M / 盘上现有 ≈32M / 本地全量 ≈118M（动态）**；`r9_scaling.py` 的 `--local-cap-m` 已改 **default=118.0**。
  → ⚠️ **R11-E 的可比 N 区间被压到 ≈6.8M**（GPIC-short 已下 < 18.5M）→ **须如实说明「可比区间更窄」**。
- [ ] ⛔ **loop 优化：暂不做（用户 2026-10-03 决定）** —— `SLEEP_WAIT 1800→3600` 与「训练未完成就跳过 cline 调用」的前置检查，**都需在公司重启 loop**（假期内做不了），且 1800→3600 **会让反应变慢**。→ **待回公司后择机**。
- [x] ✅ **H-A′ 已放行（运维 2026-10-03）**：**时间（~150h）与 Token（~1.8–9 亿）均可接受** → **全量 SWE-bench-Lite(300) × 5 harness（顺序跑）**。
  顺序：① 只读核查（硬闸）→ ② **镜像来源走 R1（新增·首选）** → ③ 写适配层（**先 1 个再复制**）→ ④ 顺序跑（低并发、每个跑完即固化）→ ⑤ `SWEBENCH_COMPARE.html`。
- [x] 🚫 **docker 系降为末选（运维 2026-10-03 关切）**：**L0（改 daemon 配代理）彻底取消** —— ① 改 daemon **影响其它 docker 使用者**（全局配置 + `restart` 中断所有容器）；② **root 配置留痕 → 管理员会知道**；③ **L1/L2 还占共享 `/var/lib/docker`**（可能挤爆别人的盘）。
  → **新首选 = R1：`unshare --user --map-root-user --mount --pid` 沙箱 + 每实例 rootfs 落 `/nas_train`（32T）** —— **完全不碰 docker/daemon**，且**一套沙箱同时解决 Aider 的沙箱缺口**（`unshare --user --map-root-user true` 已实测 OK）。
- [x] 🔐 **sudo 口令已确认 = `Ly3960405#`**（`@` 变体无效）；**已入库 → 用完请轮换**。
- [x] ✅ **`ops_relay.sh`「2 副本」= 误判，已结案（2026-10-03 RUN_ID 8 实测）**：第 2 行 `3521816` 的 **`ppid=2489749`（真 relay）且 `etimes≈0`** → 它是 relay **执行命令块时 fork 的子 shell**，不是副本。→ **唯一真 relay = `2489749`（ppid=1）**，**无需清理**；已更正 `run/AGENTS.md` §3.5(1)（判别方法是**看 `ppid`**，不是看进程个数）。
- [x] ✅ **D-CLEAN-2 已执行（唤醒 58）**：**实收 ≈341 G** —— ⚠️ **我此前报的「≈8.6 T」错了**：`laion2B-en-aesthetic` 盘点记 **8.1 T**，**实测只有 7.8 G**（128 parquet 的 **URL 元数据**）→ **G/T 单位误读、差 3 个数量级**。实删：laion2B 7.8G + zhulong 0.49G + pip 3.3G + **nemo Round1 ~310G**（`nemo_experiments` 524G→**214G**，**`p5b` 79G 保留**）。
- [ ] ⭐ **`servers`(974 G) 已探明 = LLaVA-V1.5-Qwen3-4B 旧训练部署** → ✅ **运维已批准删除** → **D-CLEAN-3 已下发**（**带 P1/P2/P3 前置检查**：无进程占用 / 无近期活动 / 无脚本引用；任一不过即停手报告）。
- [x] 🚫 **`nemo_experiments` 的 R2 近期 ckpt（~135 G）：运维决定「先不清」**（保留）。
- [x] ⏸ **论文（ISEDA2027）：已定「冻结不动、等实验结果」（2026-10-03 用户拍板）** —— 本轮刷新（**commit `afa2624`**，审计 `PAPER_STALENESS_AUDIT.md`）**即为当前定稿态**，**不再单独改**；下列 4 项**暂缓**，等 vision/pretrain 出结果后**一次性回填**：
  1. abstract 加 scaling 句（渐近 **25.1%**）
  2. seeds n=3 → n=5
  3. §2 相关工作补视觉线
  4. `tab:visobj` 补「lr-坍缩 vs SSM-坍缩」区分
- [x] ✅ **vision 队列已裁定（2026-10-03 用户：按 agent 建议执行）** —— **R11-L2 文本塔解冻（LoRA/Adapter）= 下一优先级、已批准立即执行**；臂⑤ GenLIP **跳过**（→ 改 `caption-loss-weight` 三点消融）；臂⑥ AIMv2 **暂缓**；**R13 仍须单独批**（只做 OV2 单臂）；**R11-E 等 GPIC `short` ≥18.5M**。→ 已写入 `BAIZE_VISION_TASK.md`「运维指令 · 2026-10-03（三）」。
- [x] ✅ **data 下载白名单已锁定（2026-10-03 用户）** —— **只下 `ultrafineweb_l1_en_hq` + `zh`（MiniCPM5 base 族剩余）+ GPIC**；🔴 **立即停 `ultrafineweb_en_v1_4`**（6.7TB / ≈43 天 / 非 P-8 必需 / 阻塞后两项）；🚫 **白名单外一律不下载、不调研**（含 `UltraX-Preview` → 配比实验 **S1 轴降级为「仅 base」**）。→ 已写入 `BAIZE_DATA_TASK.md` 顶部新块。

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
- 🚩 **`launcher` 只暴露 MBS / TP / SP / seq-length / precision**（agent P-9 非 GPU 预研，2026-10-03）→ **P-9 只用已暴露开关、不改 recipe**；B/C/E/F 类（recompute / 通信重叠 / dataloader / attn-backend）**冻结**，其中 **NCCL（P-4 占 41.7%）** 收益最大 → 记录在案、**待批准后另开**。
- **磁盘**：`/nas_train` 207T/剩 ~31T（86%）· `/nas_inference` 剩 20T · `/nas_user` 剩 29T。
- 🪶 **任务书瘦身（2026-10-03，为省 agent key 的 token）**：loop 是 `prompt="$(< TASK_MD)"` → **任务书全文 = 每次唤醒的 prompt**。
  已把**已完成轮次**移出 prompt：**vision 92.5→11.7KB** · **pretrain 57.1→32.9KB** · **data 60.1→42KB**
  （归档：`run/vision/ARCHIVE_ROUNDS_2-9.md` · `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` · `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md`）。
  → **4 份活跃任务书 237.2 → 114.1 KB（-52%）**，每次全唤醒省 ≈**41K prompt token**。
  ⚠️ 归档文件**不进 prompt**；agent **需要时才去读**（已在各任务书里写明指引）。
- **本机（Windows 侧）**：`C:\Users\liuyu\super_intelligence_2035`（git clone）；**可 fetch/pull/push GitHub**；**不能直连 `.12`/`.29`**（SSH 超时）——**通道就是 git**。

---

## 7. 已知坑（会复发）

- 🟡 **`baize_vision_loop.sh` 无 `git pull`**（2026-10-03 复核脚本原文：只做 `git add -A` + `commit` + `push`，每 5h）—— **✅ 但不构成阻塞（用户 2026-10-03 确认）**：
  → **机制**：**仓库是共享的** —— **别的线（`baize_pretrain_loop.sh` / `baize_data_loop.sh` 都会 `fetch + pull --rebase --autostash`）拉一次，vision 在同一工作副本上就看到**我的任务书更新。→ 所以 `84d7990`（R11-L2 批准）**会经由 pretrain/data 的 pull 自然到达**，**无需任何专门处理**。
  → 🔧 **可选根治（需登机；非必须）**：`pkill -f baize_vision_loop.sh` → 照抄 `baize_pretrain_loop.sh`（自带 pull + 行首 `^WAITING:` 正则 + 只 add 本任务文件）→ 再 `setsid` 起。
  → ⚠️ 附带注意：它的 `git add -A` 会把**整棵树**的改动一起提交（不只 vision 文件）——共享副本上叠加时**可能误提交别线在途文件**。
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
- 🔴🔴 **cline 凭据被轮换 → 全 loop 静默停摆（2026-10-04 实发 ~9h，迄今最隐蔽的一次）**：
  - **现象**：`.29` 的 pretrain/harness **~9 小时零产出**（文件一个没改），而 `/tmp/baize_*_loop.log` 每个 30min 周期只打印 **`error: Forbidden`**，紧接着 **`cline returned (exit 0)`** → **loop 判定"成功"**、继续睡 → **完全静默**（pretrain 18 次 / harness 37 次）。同段 `.12` 的 vision/data **整夜正常**。
  - **根因**：**`.29` 的 cline 凭据失效** —— env `OPENAI_API_KEY` → 网关 `chat/completions` **403**；`~/.cline/data/secrets.json` 里的 key **也 403**；而 **`.12` 的 secrets key → 200**（两者 prefix6 都是 `02_088` 但**值不同**）→ **key 在 10-03 22:12 之后被轮换，只更新了 `.12`**。（harness 10-03 22:12 用 `-k $OPENAI_API_KEY` 的 smoke **还是成功的** → 时间线严丝合缝。）
  - **已排除（均实测）**：❌ proxy（虽然 `直连 200 / 走代理 503`）· ❌ `OPENAI_API_URL`/`API_TYPE` · ❌ 模型名 · ❌ `globalState.json`（与 `.12` **完全一致**）· ❌ token 额度。
  - **可复用排查法（ops relay 只读块）**：① `pgrep -af 'baize_.*_loop.sh'` ② `tail /tmp/baize_*_loop.log` + **`grep -c Forbidden`**（**首选探针**）③ `nvidia-smi` 看 GPU 是否空转 ④ **多把 key 分别 `curl /v1/chat/completions`** ⑤ 用有效 key 跑 cline smoke。
  - **修法（2026-10-04 已执行 ✅）**：备份 `.29` secrets → **把 `.12` 的 key 经 stdin 管道写入 `.29`**（key 不回显）→ loop 的 cline 调用行加 **`env -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE -u *_PROXY`**（防失效 env key 覆盖 secrets）→ **重启两条 loop** → 验证 `Forbidden=0` 且 cline 真在推理。
  - ⚠️ **复发预防**：**轮换 cline key 时必须同时更新 `.12` 与 `.29` 两台**；并把 `grep -c Forbidden /tmp/baize_*_loop.log` 纳入日常体检。
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

- **2026-10-04（🔴 重大事故 + 修复）** —— **`.29` 的 pretrain + harness 静默停摆 ≈9 小时（10-03 22:10 → 10-04 07:29）**：
  - **现象**：两线文件零变更；`/tmp/baize_*_loop.log` 每 30min 周期只有 **`error: Forbidden` + `cline returned (exit 0)`**（pretrain 18 次 / harness 37 次）→ loop 当成功、继续睡 = **完全静默**；同期 `.12` 的 vision/data **整夜正常**。
  - **探查**（ops relay RUN_ID 9→14，全只读）：① 两 loop 进程**活着** ② **P-5b 已于 01:37 跑完**（`saved checkpoint from iteration 4771`）→ **8×H100 空转 ~6h** ③ 逐条否证 proxy / `OPENAI_*` / `API_TYPE` / 模型名 / `globalState` / 额度 ④ **`curl /v1/chat/completions` 带 `.29` 的 key → `403`**
  - **根因（RUN_ID 14 一锤定音）**：**`.29` 的 cline 凭据被轮换吊销，只更新了 `.12`** —— `.12` key → **200** + cline smoke **OK**；`.29` 的 env key 与 secrets key **都 403**（prefix6 同为 `02_088` 但**值不同**）。
  - **修复（RUN_ID 15，用户批准）**：备份 `.29` secrets → **把 `.12` 的 key 经 stdin 管道写入 `.29`**（不回显）→ loop 的 cline 行补 **`-u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE -u *_PROXY`** → **重启两条 loop** → 校验 **`Forbidden=0`** 且两个 `bun cline` 正在推理 ✅ → **两线复工**（pretrain 自查发现训练已结束、直奔 P-6②；harness 直奔步3 收尾）。
  - 详见 `daily-memories/2026-10-04.md`；**坑已入 §7**（含复发预防：**轮换 key 必须同时更新 `.12` 与 `.29`**）。
- **2026-10-03（晚 · 三项拍板，全部落地）** —— 用户下达三条指令：
  - **① 📄 论文冻结**：**「论文不动，等实验结果」** → `afa2624`（§6 重写）+ 已推送即为**定稿态**；4 项润色（abstract scaling / seeds n=5 / §2 视觉线 / `tab:visobj` 区分）**暂缓**，等结果后一次性回填。
  - **② 🟢 vision 按 agent 建议执行** → **commit `84d7990`**：**R11-L2 文本塔解冻（LoRA/Adapter）已批准 = 下一优先级、立即执行**（必须重跑 R4 坍缩判据 C1–C4）；臂⑤ GenLIP **跳过**（→ 改 `caption-loss-weight` {0.5,1.0,2.0} 三点消融）；臂⑥ AIMv2 **暂缓**；**R13 仍须单独批**（批准后只做 OV2 单臂）；**R11-E 等 GPIC `short` ≥18.5M**。同步**修掉陈旧 §0 速览**（原还写"在跑 R10-③"）+ 重写 §3 队列（8 行）。
  - **③ 🎯 data 下载白名单锁定** → **commit `1c2f248`**：**只下 `ultrafineweb_l1_en_hq`(478G) + `zh`(324G) + GPIC**；🔴 **立即停 `ultrafineweb_en_v1_4`**（6.7TB / @1.8MB/s ≈ **43 天** / **非 P-8 必需**（base-en 1T tok 已够）/ **阻塞后两项**）；带宽优先级 **GPIC > l1_en_hq > zh**；🚫 **白名单外一律不下载、不调研、不推荐**。⚠️ **如实记录的后果**：配方 Stable 段原列的 **`UltraX-Preview` 因此出局** → 配比实验 **S1 轴（base vs UltraX 占比）降级为「仅 base」**，需要时由运维点名再议。
  - 🔧 **工具教训（本次踩到）**：`git fetch` 一度 **>30s**（7 线高频抢占的窗口期），超单条命令超时 → 可靠做法 = **`cmd /c "... > log 2>&1"`**（PowerShell 会把 git stderr 当异常）**+ 脱离进程的后台重试循环**（`fetch → rebase --autostash → push` ×20）；本轮 2 次 push 均 **attempt=1~2 成功**。
- **2026-10-03** —— 建本记忆机制（先放 `run/`，按用户要求**迁到项目根**）。当日运维侧 push **14 个 commit**（见 `daily-memories/2026-10-03.md`）：7 项处置 · P-9 规格重写（seq4096 + 4M 不变量 + seq 多点 + FP8-by-M + profiling）· 记忆滚动规程 · R11/R11-D · D-CLEAN/D-CLEAN-2（≈8.6T）· harness H-A′+H-D · `report_10_03.html`（含刷新）。
- **2026-10-03（补）** —— **论文陈旧性审计 + 刷新**（**commit `afa2624`**）：⭐ 查出 **§6 整节停留在 R1/R2 坍缩期**（4 表全是 **4.456x** 坍缩读数，被 R3 自我推翻）→ 已**整节重写**（6 架构 + 纠正 recipe + R8/IN-1k + 新增 scaling 子节，渐近 **25.1%** 诚实负结果）；连带修 §3 `4094`/`six`、§1 补"为什么小"、§7 去掉"resolution immaterial"。产物 `PAPER_STALENESS_AUDIT.md`。编译 **7 页 / 0 error / 0 undef / 0 overfull**。⚠️ 推送插曲：远端 7 线高频抢占致 `fetch`>30s、push 被拒 ×3 → **后台重试循环**第 2 次成功。
