# AGENTS.md — BaiZe 自动化 agent / loop 状态总表

> **用途**：`run/` 下有多个 `*_loop.sh` 与多个 `MEMORY*.md`，但**真正活跃的 agent 只有 3 个**。
> 本文件是**唯一权威**的"谁在跑"清单，避免数错。
>
> 最后更新：2026-10-01

---

## 1. 活跃 agent（**3 个**）

| Agent | loop 脚本 | 任务书 | 状态文件 | 日志目录 | 跑什么 | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| **vision** | `baize_vision_loop.sh` | `BAIZE_VISION_TASK.md` | `MEMORY_VISION.md` | `daily-memories-vision/` | 视觉编码器 R2-0~R2-5（训练在 `10.239.2.12`） | ✅ 运行中 |
| **pretrain** | `baize_pretrain_loop.sh` | `BAIZE_PRETRAIN_2B_TASK.md` | `MEMORY_PRETRAIN_2B.md` | `daily-memories/` | 预训练 R2 P-1/P-2/P-3（训练在 `10.239.2.29`） | ✅ 运行中 |
| **data** | `baize_data_loop.sh` | `BAIZE_DATA_TASK.md` | `MEMORY_DATA.md` | `daily-memories-data/` | 数据准备 phase0~phase6 | ⬜ 待启动 |

## 2. 已收敛（**2 个，不应再跑**）

| 轮次 | loop 脚本 | 任务书 | 状态文件 | 终态 |
|:---|:---|:---|:---|:---|
| 1B 架构与超参搜索 | `baize_search_loop.sh` | `BAIZE_PRETRAIN_TASK.md` | `MEMORY.md` | `PHASE=step3_done` |
| 2B 架构搜索 | `baize_2b_search_loop.sh` | `BAIZE_2B_ARCH_SEARCH_TASK.md` | `MEMORY_2B.md` | `PHASE=converged` |

> ⚠️ 这两个 loop 的脚本**是 `while true`**，任务收敛后若没 kill 干净会**一直空转烧 token**。
> 到机器上先确认：`pgrep -af 'baize_.*_loop.sh'` —— 预期只应看到 vision / pretrain / data 三个。
> 若还有旧的两个：`pkill -f baize_search_loop.sh` 和 `pkill -f baize_2b_search_loop.sh`。

## 3. 已知的脚本级缺陷（**重启 loop 时顺手修**）

| 脚本 | 缺陷 | 影响 | 修法 |
|:---|:---|:---|:---|
| `baize_vision_loop.sh` | ① `git_push_if_needed` 只 push 不 pull ② WAITING 正则 `^[- ]*WAITING: *1` 偏宽 | 远端前进后 push 永久失败 | 照抄 `baize_data_loop.sh` 的 `git_sync_and_push`（fetch + `pull --rebase --autostash`） |
| `baize_pretrain_loop.sh` | ① 同上 ② WAITING 正则 `WAITING:[* ]*1` **会误匹配正文散文**（`MEMORY_PRETRAIN_2B.md` 第 8 行就有一句 `WAITING: **1**` 被命中） | 睡眠时长由散文决定，不是状态驱动 | 同上；并把正则收紧为 `^WAITING:[[:space:]]*1` |
| `baize_search_loop.sh` / `baize_2b_search_loop.sh` | 固定间隔、无 git 同步、无 WAITING | 已收敛，无实际影响 | 建议直接停掉 |

> `baize_data_loop.sh` 是**新建的**，上面三处坑已从设计上避开，可直接作为模板。

## 4. 共享资源（**三个 agent 共用**，务必注意）

- **共享工作副本**：同一个 NFS 路径 `/nas_train/app.e0031982/code/super_intelligence_2035`
  - **只需一个 agent `git pull`，其余立刻看到**——不要重复 pull
  - 工作区里陌生的未提交改动**可能是别的任务的在途文件**，🚫 不要 clean / stash / reset
  - 各 loop 的 `git add -A` 会**互相把对方在途文件一起提交**，这是既有设计的已知副作用
- **共享 NFS 与带宽**：`/nas_inference`（只读源）与 `/nas_train`（产出）
  - vision 的 **R2-4 需要"无争用的干净吞吐测量"** → 其他任务的重 I/O 应**主动避让**
  - 多模态**下载仍在进行** → 下载期间不要做重 I/O / 全量扫描

## 5. 相关但不属于本目录的 agent

- **ZhuLong（DAC 2027）**：`doc/ZhuLong_DAC2027/run/` 下有自己的 loop 与 MEMORY（另一套代码库 `eda_fastmcp`），与本目录无关。
