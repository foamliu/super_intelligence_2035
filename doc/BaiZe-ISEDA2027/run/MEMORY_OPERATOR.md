# MEMORY_OPERATOR.md — BaiZe **运维（operator）** 长期记忆 · **醒来先读本文件**

WAITING: 0

> ⚠️ 本文件是**运维侧**（指挥 4 条线的那个"我"）的状态文件，**不属于任何 agent 线**。
> 各线有自己的：`MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md` / `MEMORY_VISION.md` / `MEMORY_HARNESS.md`。
> 遵守与各线相同的纪律：**`WAITING:` 只在顶部出现一次**；**≤32KB**，超限滚动到 `daily-memories-operator/`。

---

## 0. 我是谁 / 我的角色

- 我是本项目 `doc/BaiZe-ISEDA2027` 的**外部运维**：**不登录训练机**。
- 我的**下达通道** = 各任务书的 `## 🔧 运维指令区（OPERATOR NOTES）`（**改文件 + git commit/push**）。
- 我的**查看通道** = 读各线的 `MEMORY_*.md` 顶部「进度快照」/「运维问答」+ `run/` 产物（`git pull` 即可，**不需要登录服务器**）。
- 我指挥的 4 条线：**pretrain**（`10.239.2.29`）· **data**（`.12`）· **vision**（`.12`）· **harness**（`.29`）。另有 **ops relay**（RUN_ID 机制，见 `run/ops/`）。

---

## 1. 每次「醒来」的固定动作（SOP）

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`
   （远端推进很快——各 agent 每次唤醒都可能 push；**不 pull 直接改会冲突**）。
2. **读本文件**：尤其 §3 在途任务 / §4 待拍板 / §5 纪律。
3. **读 4 条线状态**：各 `MEMORY_*.md` 顶部 + `git log --oneline -20` + `run/ops/.last_run_id`。
4. **处理回写**：有 agent 产物/答复 → 读、核、必要时回一句（写进对应任务书运维指令区或该线「运维问答」）。
5. **下发新任务**：在对应任务书运维指令区加 **带日期的 block**（**越靠前越优先**；老块不改，留作历史）。
6. **提交**：`git add` **只加自己动的文件** → `git commit` → `git push`。**不要 `git add -A`**（会把别的 agent 在途文件卷进来）。

---

## 2. 通讯协议 / 接口（关键认知）

- **接口 = 任务书的「运维指令区」**。四条线**现在都有**该区：
  - `run/BAIZE_PRETRAIN_2B_TASK.md` · `run/BAIZE_DATA_TASK.md` · `run/BAIZE_VISION_TASK.md` · `run/BAIZE_HARNESS_TASK.md`
  - ⚠️ **pretrain / vision 的任务书原本没有该区，是 2026-10-03 由运维（我）补上的**。
- **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；**新块放前面**，并写清 **优先级 / 顺序 / 判据 / 铁律**。
- **各线的回写位置**：`MEMORY_*.md`（状态头 + 进度快照 + 运维问答 + 流水）、`daily-memories*/`、`EXPERIMENTS_*.md`、各线产物目录。
- **ops relay**：外部运维还可经 `run/ops/inbox.md` 下 RUN_ID 命令（⚠️ **只执行第一个 ```bash 块**；下发必须把新块放最前、旧块降级为 ```text、RUN_ID +1）。

---

## 3. 在途任务（截至 2026-10-03 ~09:00）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **pretrain** | P-5b 长跑（20B）→ 跑完**立即 P-9**（MBS/精度/seq/profiling） | `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`「P-9」节 | 🔄 P-5b ~57%，ETA 10-04 凌晨 |
| **vision** | **R10③**（w384/w640 补密 M 轴）→ **R11-D**（GPIC vs CC12M+Amshaker）/ **R11-L**（loss 轴） | `EXPERIMENTS_VISION_ROUND10/11.md` | 🔄 R10_active |
| **data** | 下载巡检 + **D-CLEAN-2**（已批删除 ≈8.6T）+ `servers` 探查 | `DISK_CLEANUP_INVENTORY.md` 更新 | 🔄 |
| **harness** | **H-A′ Aider Polyglot 横评** + **H-D** 5-harness 对比与 cline 机会点 | `harness/AIDER_POLYGLOT_COMPARE.html` · `HARNESS_COMPARE_MATRIX.html` · `CLINE_IMPROVEMENT_OPPORTUNITIES.md` | 🔄 |

---

## 4. 待拍板 / 我欠的答复

- [ ] **P-9 结果** → 定 **P-8 的 seq(4096/8192) / MBS / 精度(bf16/FP8)**（含 16384 是否 OOM 的长上下文边界）。
- [ ] **D-CLEAN-2 实际回收量** + **`servers`(974G, `/nas_train/app.e0031982/servers`) 到底是什么** → 用户定夺是否删。
- [ ] **harness 的运行主机**（`pull` 不通后是否需要本地镜像 / 专用仓位）。
- [ ] **GPIC 下载部分的「唯一对」是否已 > 18.5M**（R11-D 先验证；我的粗估 ≈4–5M，**待实测**）。
- [ ] **README / 论文口径统一**：seq 已定 4096（P-8 起），文档里残留的 4094 需对齐。
- [ ] 是否需要把本次关键决策合并进 `BAIZE_PROGRESS.html`（单一事实来源）。

---

## 5. 铁律与纪律（我必须要求 agent 遵守，自己也遵守）

- 🚫 **绝不打断正在跑的 long-run**（尤其 **P-5b**：改 MBS/精度/seq 会让 20B loss 曲线作废）。
- 🚫 **绝不 kill 各线的 watchdog loop**（`baize_*_loop.sh`）；收敛后只置 `WAITING=1` 长睡。
- **`WAITING:` 纪律**：只在 `MEMORY_*.md` **顶部出现一次**；正文/快照/流水里不得再出现（否则误触发 30 分钟长睡）。
- **记忆体量 ≤32KB**（4 线已全部达标；超限滚动到 `daily-memories*/`）。
- **不许猜**：源码结论贴 `路径:行号`；实验结论贴 **命令 + 原始输出**。
- **预注册判据先定后测**（P-9a-ext G、R11 都用了）。
- 🔒 **红线**：`EDA-Eval-PyAether` 158 任务只读隔离区**绝不可动**；base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k 均不可删。
- ⚠️ **`nemo_experiments` 含 P-5b 正在写的 ckpt**，且 **P-6② 要用其中 6 个里程碑 ckpt** → 只能「先列清单、保住最晚/最优 + 里程碑，再删早期项」。
- **不占 GPU 的线**（data/harness）也要**避让 `.29`/`.12` 的训练 I/O**。

---

## 6. 关键路径与事实速查

- **关键路径**：`P-5b → P-9 → P-6② → P-8`（P-8 = Stage(i) 本体，周级墙钟，仍暂缓等 base + 配比）。
- **两条硬口径（2026-10-03 定）**：
  - **seq 统一 4096**（P-8 起）；`4094` 仅存于正在跑的 P-5b。
  - **每步 ≈ 4M token 不变量**：`seq4096↔GBS1024` · `8192↔512` · `16384↔256` · `2048↔2048`。**总步数 = 总token/4M，与 seq 无关**。
- **FP8 机制**：`s` 取决于 **GEMM 的 M**，大 GEMM `M = MBS × seq`；**`M≳16K` 才 `s>1`**（seq 与 MBS 是等价杠杆）。
- **vision 现状**：R9 lp 渐近 **25.1%**（当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结CLIP文本塔 + InfoNCE**；⚠️ **不是 GPIC**）；`attention flash` 仅占 GPU 自耗时 **0.7%**（P-4 profile）。
- **磁盘**：`/nas_train` 207T/剩 ~31T（用 86%）· `/nas_inference` 剩 20T · `/nas_user` 剩 29T。
- **本机（Windows 侧）**：`C:\Users\liuyu\super_intelligence_2035`（git clone）；**可 fetch/pull/push GitHub**；**不能直连 `.12`/`.29`**（SSH 超时）——这是正常的，通道就是 git。

---

## 7. 已知坑（会复发）

- `ops/inbox.md` **只执行第一个 ```bash 块**（已踩过一次：RUN_ID 4 静默失效）。
- `ops_relay.sh` 会跑出**多副本**（共享 `.last_run_id` → 重复执行）→ 保留 **`etimes` 最大**者。
- **WAITING 正则**：旧版 `WAITING:[* ]*1` 会误匹配正文散文 → 已收紧为行首 `^WAITING:[[:space:]]*1`。
- `baize_vision_loop.sh` 的 push 缺陷（只 push 不 pull）**未修**（因运行时不宜改脚本）→ **等它停止再照抄 pretrain 新版**。
- `python` 路径 / `PYTHONPATH` 见 `DATA_LEDGER.md` §「关键路径速查」。
- 本机 PowerShell 读 UTF-8 中文会显示乱码——**只影响显示，不影响文件**；校验用 `read_files`。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早的流水条目滚动到 `daily-memories-operator/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories-operator/<YYYY-MM-DD>.md`，记录：**用户下发的指令 → 我的处置 → 落地的 commit → agent 的回报**。

---

## 9. 流水（倒序，最近在上）

- **2026-10-03** —— 建本记忆机制。当日我在运维通道共 push **13 个 commit**（见 `daily-memories-operator/2026-10-03.md`），完成：7 项处置下发 · P-9 规格重写（seq4096 + 4M 不变量 + seq 多点 + FP8-by-M + profiling）· 记忆滚动规程（4 线 ≤32KB）· R11（loss 轴）/ R11-D（GPIC vs CC12M）· D-CLEAN/D-CLEAN-2（磁盘回收 ≈8.6T）· harness H-A′ + H-D · 报告 `report_10_03.html`（含刷新）。
