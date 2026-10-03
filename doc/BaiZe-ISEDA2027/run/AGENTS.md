# AGENTS.md — BaiZe 自动化 agent / loop 状态总表

> **用途**：`run/` 下有多个 `*_loop.sh` 与多个 `MEMORY*.md`，但**真正活跃的 agent 只有 3 个**。
> 本文件是**唯一权威**的"谁在跑"清单，避免数错。
>
> 最后更新：2026-10-01

---

## 1. 活跃 agent（**4 个**）

| Agent | loop 脚本 | 任务书 | 状态文件 | 日志目录 | 跑什么 | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| **vision** | `baize_vision_loop.sh` | `BAIZE_VISION_TASK.md` | `MEMORY_VISION.md` | `daily-memories-vision/` | 视觉编码器 R2~R8（已收敛，待运维处置）+ **R9**（训练在 `10.239.2.12`） | ⏹ 收敛/待派 |
| **pretrain** | `baize_pretrain_loop.sh` | `BAIZE_PRETRAIN_2B_TASK.md` | `MEMORY_PRETRAIN_2B.md` | `daily-memories/` | 预训练 R2 P-1~P-8（训练在 `10.239.2.29`） | ✅ 运行中 |
| **data** | `baize_data_loop.sh` | `BAIZE_DATA_TASK.md` | `MEMORY_DATA.md` | `daily-memories-data/` | 数据准备 phase0~phase6 + R2/R3 调研 | ✅ 运行中 |
| **harness** 🆕 | `baize_harness_loop.sh` | `BAIZE_HARNESS_TASK.md` | `MEMORY_HARNESS.md` | `daily-memories-harness/` | **H-A** SWE-bench 横评 · **H-B** harness 源码分析（从 cline 起） | ⬜ 待 ops 启动 |

> 🆕 **harness 线（2026-10-02 新建）**：与三条 BaiZe 训练线**互不干扰** ——
> 它**不占 GPU**（源码分析 + SWE-bench 评测），但**可能吃 CPU/磁盘/Docker**，
> **重 I/O 仍要避让** `10.239.2.12` / `10.239.2.29` 上的训练。

## 2. 已收敛（**2 个，不应再跑**）

| 轮次 | loop 脚本 | 任务书 | 状态文件 | 终态 |
|:---|:---|:---|:---|:---|
| 1B 架构与超参搜索 | `baize_search_loop.sh` | `BAIZE_PRETRAIN_TASK.md` | `MEMORY.md` | `PHASE=step3_done` |
| 2B 架构搜索 | `baize_2b_search_loop.sh` | `BAIZE_2B_ARCH_SEARCH_TASK.md` | `MEMORY_2B.md` | `PHASE=converged` |

> ⚠️ 这两个 loop 的脚本**是 `while true`**，任务收敛后若没 kill 干净会**一直空转烧 token**。
> 到机器上先确认：`pgrep -af 'baize_.*_loop.sh'` —— 预期只应看到 vision / pretrain / data 三个。
> 若还有旧的两个：`pkill -f baize_search_loop.sh` 和 `pkill -f baize_2b_search_loop.sh`。

## 3. 已知的脚本级缺陷（**重启 loop 时顺手修**）

| 脚本 | 缺陷 | 影响 | 状态 / 修法 |
|:---|:---|:---|:---|
| `baize_pretrain_loop.sh` | ① `git_push_if_needed` 只 push 不 pull ② WAITING 正则 `WAITING:[* ]*1` **会误匹配正文散文**（`MEMORY_PRETRAIN_2B.md` 里就有一句 `WAITING: **1**` 被命中） | 远端前进后 push 永久失败；睡眠时长由散文决定 | ✅ **已在仓库修好**（2026-10-01）：改为 `fetch + pull --rebase --autostash`、正则收紧为 `^WAITING:[[:space:]]*1`、兜底提交只 add 本任务文件。`git pull` 后直接启动即可 |
| `baize_vision_loop.sh` | ① 同上 ② WAITING 正则 `^[- ]*WAITING: *1` 偏宽 | 远端前进后 push 永久失败 | 🚫 **暂不修**：它**正在运行**，bash 增量读取脚本，改运行中的脚本有风险。**待停止时再照抄 `baize_pretrain_loop.sh` 的新版** |
| `baize_search_loop.sh` / `baize_2b_search_loop.sh` | 固定间隔、无 git 同步、无 WAITING | 已收敛，无实际影响 | 建议直接停掉（进程疑似已被清理） |

> `baize_data_loop.sh` 是**新建的**，上面三处坑已从设计上避开，可直接作为模板。

## 3.5 ⚠️ 已知的运维级问题（**会复发，需周期性检查**）

### (1) `ops_relay.sh` 的「多个副本」—— ⚠️ **2026-10-03 更正：多半是「子进程」，不是副本**

> **2026-10-03 实测（RUN_ID 8，`.29`）**：`ps -eo pid=,ppid=,etimes=,args=` 看到 2 行，但
> ```
> 2489749       1  155150 bash ops_relay.sh   ← ppid=1（真守护进程）
> 3521816 2489749       0 bash ops_relay.sh   ← **ppid=2489749、etimes≈0 → 它刚派出的子进程**
> ```
> → **`2489749` 是唯一真 relay**；另一行是**它执行命令块时 fork 出来的子 shell**（所以 etimes≈0、每次执行都换 PID —— 这正好解释了旧证据里"另一个 PID 会变、`2489749` 不变"）。
> ✅ **结论：此前记的「会跑出多个副本、需人工清理」很可能是一次误判**（把子进程当成了副本）。
> （当时的清理**没有造成损害**——保留的正是 etimes 最大的真 relay。）

**✅ 正确判别（先看 `ppid`，再看 etimes）**：

```bash
ps -eo pid=,ppid=,etimes=,args= | grep 'ops_relay\.sh' | grep -v grep
# 真 relay：ppid=1（或不指向另一个 relay）
# 子进程 ：ppid = <另一个 relay 的 pid>，且 etimes 很小
```

- **只有当两个 `bash ops_relay.sh` 的 `ppid` 都不指向对方**时，才是**真副本**（才需要清理）。
- 清理时**仍保留 `etimes` 最大者**（PID 会回绕，数字小 ≠ 启动早）：
  ```bash
  ps -eo pid=,ppid=,etimes=,args= | grep 'ops_relay\.sh' | grep -v grep | sort -k3 -nr | head -1
  ```
- 🚫 **绝不要把两个都杀掉** —— 那会**切断假期/远程的通讯通道**。

**旧证据（保留备查）**：RUN_ID 2 见 `1276654`·`2489749`；RUN_ID 5 见 `2228582`·`2489749`。
按新判据，那两个"会变"的 PID 更可能是**子进程**，而非"被重启的副本"。

### (2) `ops/inbox.md` 中继**只执行<u>第一个</u> ```bash 块** —— 见 `ops/inbox.md` 顶部
下发新命令**必须**把块放到最前面，并把旧块降级为 ```text，否则新命令**永远不会执行**（已踩过一次）。

## 4. 共享资源（**四个 agent 共用**，务必注意）


- **共享工作副本**：同一个 NFS 路径 `/nas_train/app.e0031982/code/super_intelligence_2035`
  - **只需一个 agent `git pull`，其余立刻看到**——不要重复 pull
  - 工作区里陌生的未提交改动**可能是别的任务的在途文件**，🚫 不要 clean / stash / reset
  - 各 loop 的 `git add -A` 会**互相把对方在途文件一起提交**，这是既有设计的已知副作用
- **共享 NFS 与带宽**：`/nas_inference`（只读源）与 `/nas_train`（产出）
  - vision 的 **R2-4 需要"无争用的干净吞吐测量"** → 其他任务的重 I/O 应**主动避让**
  - 多模态**下载仍在进行** → 下载期间不要做重 I/O / 全量扫描

## 5. 相关但不属于本目录的 agent

- **ZhuLong（DAC 2027）**：`doc/ZhuLong_DAC2027/run/` 下有自己的 loop 与 MEMORY（另一套代码库 `eda_fastmcp`），与本目录无关。

## 6. 📉 记忆体量维护（**2026-10-03 运维新增**）

> **为什么**：loop 脚本对 `MEMORY_*.md` 只做 `grep '^WAITING:'`（近零成本），
> 但 **cline agent 每次唤醒会把整个 `MEMORY_*.md` 读进上下文** → 文件越大，**每次唤醒烧的 token 越多**，且**无上限增长**。

**实测体量（2026-10-03）**：

| 文件 | 体量 | 状态 |
|:--|--:|:--|
| `MEMORY_PRETRAIN_2B.md` | **≈243 KB**（334 行） | 🔴 严重超标 |
| `MEMORY_VISION.md` | ≈94 KB（630 行） | 🟠 超标 |
| `MEMORY_DATA.md` | ≈85 KB | 🟠 超标 |
| `MEMORY_HARNESS.md` | ≈18 KB | 🟢 正常 |
| `MEMORY_2B.md` / `MEMORY.md` | ~13 / ~6 KB | 🟢 已收敛 |

**规程（已写入各任务书「运维指令区」）**：

1. **上限**：每个 `MEMORY_*.md` **≤ 32 KB**。
2. **超限即滚动**：把**较早的流水条目**（**保留最近 ~20 条**）**追加**到对应 `daily-memories*/<条目日期>.md`，
   再从 MEMORY 中删除这些旧条目。**归档文件原文不改**，且**不参与每次唤醒读取**（作为长期归档 / grep 用）。
3. **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条流水。
4. **纪律**：归档**不得改变任何结论**；`WAITING:` 纪律（正文/流水/快照里不得再出现以 `WAITING:` 开头的行）不变。

> 各 loop 的 `git add` **已包含** `MEMORY_*.md` 与 `daily-memories*/`，故滚动后**照常被提交**，无需额外改动脚本。

## 7. 🧭 运维侧记忆（**2026-10-03 新增**）

> §1 的 4 条 agent 线各有自己的 `MEMORY_*.md`；**指挥它们的外部运维（operator）此前没有记忆** → 已补上。

- **主记忆**：**项目根** `MEMORY.md`（即 `doc/BaiZe-ISEDA2027/MEMORY.md`）—— **运维「醒来」先读本文件**（SOP / 通讯协议 / 在途任务 / 待拍板 / 铁律 / 关键事实 / 已知坑）。
- **日流水**：**项目根** `daily-memories/<YYYY-MM-DD>.md`（记录：**用户指令 → 处置 → commit → agent 回报**）。
- **与各线的关系**：operator **不属于**任何 agent 线；它通过**改各任务书的「运维指令区」+ `git push`** 下发，通过**读各线 `MEMORY_*` / `daily-memories*` / 产物** 查看成果（**不登录服务器**）。
- ⚠️ **位置区分**：**运维记忆在项目根**（`MEMORY.md` / `daily-memories/`）；**agent 线的记忆在 `run/`**（`MEMORY_*.md` / `daily-memories*/`）——**两者不要混**。
- **纪律同各线**：`WAITING:` 只在顶部出现一次；**≤32KB**，超限滚动到 `daily-memories/`。
