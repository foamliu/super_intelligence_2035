# AGENTS.md — ZhuLong（DAC 2027）自动化 agent / loop 状态总表

> **用途**：`run/` 下有**多条** `MEMORY_*.md`、多个 `ablation_run_*` 脚本、多个旧 task book，
> 但**真正在用的只有 1 条正式线**。本文件是**唯一权威**的"谁在跑"清单，避免数错。
>
> ⚠️ **运维记忆在项目根**（`doc/ZhuLong_DAC2027/MEMORY.md`）；**agent 线记忆在 `run/`**——两者不要混。
>
> 最后更新：2026-10-04

---

## 1. 正式线（**1 条**）

| 线 | loop 脚本 | 任务书 | 状态文件 | 流水目录 | 跑什么 | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| **合并消融线** | `zhulong_loop.sh` | `ZHULONG_TASK.md` | `MEMORY_ZHULONG.md` | `daily-memories/` | `S1` 保真度 → `C1` 组件 → `C2` S2-Φ → `B` 模型，**15 臂 × 5 轮 = 75 轮** | 🟠 `PHASE=init` / `WAITING=1`（**未启动**，等 infra 校验 + 起始点拍板） |

> **启动方式**（服务器侧，脱离进程组）：
> ```bash
> # 2.12 开发机（/nas_train/）；36.15 服务器把前缀换成 /nasdata/
> setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/zhulong_loop.sh \
>   > /tmp/zhulong_loop.log 2>&1 < /dev/null &
> ```
> **停止**：`pkill -f zhulong_loop.sh`。

> 🔴 **启动纪律（2026-10-06 血泪 · 必须遵守）**：**务必用「登录 shell」或显式注入 PATH 启动 loop** ——
> ```bash
> setsid bash -lc "exec bash <...>/run/zhulong_loop.sh" > /tmp/zhulong_loop.log 2>&1 < /dev/null &
> # 或：export PATH="/home/app.e0031982/.local/node-20/bin:$HOME/.bun/bin:$PATH"; export https_proxy=http://172.19.92.23:13128
> ```
> **否则**（用非登录 shell 起）：`PATH` 里没有 `cline`（真实路径 **`/home/app.e0031982/.local/node-20/bin/cline`**）、也没有 `~/.bashrc:119` 的 `https_proxy` ⇒ loop 会**每轮 `env: 'cline': No such file or directory` 静默空转**（**2026-10-06 就这样白停了 ~5h**，而进程、git、任务书全都正常，极难察觉）。
> ✅ **启动后必须自检**：`command -v cline` 有输出 + `tail` 日志里出现 `invoking cline ...` 且**无** `No such file`。
> **唤醒间隔自适应**：读 `MEMORY_ZHULONG.md` 行首 `WAITING` —— `0` 约 1 分钟续跑，`1` 约 30 分钟轮询省 token。

---

## 2. ops 中继（**1 条，运维专供，非 agent**）

| 线 | 脚本 | 通道 | 状态 |
|:---|:---|:---|:---|
| **ZhuLong ops relay** | `zhulong_ops_relay.sh` | `ops/{inbox,outbox,README}.md` + `ops/.last_run_id` | ❌ **未启动**（`outbox` 空 / `.last_run_id=0`）；RUN_ID 1（环境摸底）已预置 |

- **用途**：运维经 git 下发 shell 命令、回收结果（~20s 轮询 / ~60s fetch），**零 token**，不必等 45min cline 编排唤醒。
- **启动**：`cd .../run && git pull --rebase && setsid bash zhulong_ops_relay.sh > /tmp/zhulong_ops_relay.log 2>&1 < /dev/null &`；**停止** `pkill -f zhulong_ops_relay.sh`。
- ⚠️ **只执行 `inbox.md` 里第一个 ```bash 块**（新块放最前、旧块降级 ```text、RUN_ID +1）。
- ⚠️ **与 BaiZe ops 独立**：`doc/BaiZe-ISEDA2027/run/ops/` 各有自己的 relay / inbox / outbox / last_run_id。

---

## 3. legacy 线（**只读历史，已被合并线取代**，但可能仍在服务器上跑 → 见根 `MEMORY.md` §3/§4）

| 线 | 任务书 | 状态文件 | 最后活动 | 备注 |
|:---|:---|:---|:---|:---|
| 旧 S1 保真度线 | `ablation_run_task_s1_full.md` | `MEMORY_s1_full.md` | 10-03 | 旧 5-run `omega_low` r1=81.6 / r2=82.3，r3 infra 作废 |
| 旧组件线 | `ablation_run_task_component_s2_full.md` | `MEMORY_component_full.md` | 10-04 | `pure_llm`→`rag`→`wo_retrieval`；与 36.15「旧 agent 冲突」相关 |
| 旧 S2 1-shot 探路线 | `ablation_run_task_s2_1shot.md` | `MEMORY_s2_1shot.md` | — | 已出探路值（各臂 1-shot） |
| 旧模型线 | `ablation_run_task_model_full.md` | `MEMORY.md`（component） | — | Phase B 逐臂详细规格（key 以本文件为唯一源） |

- **旧 loop / 总控（已不再使用，只读参照）**：`ablation_run_loop*.sh` · `ablation_run_conductor_serial.sh`。
- 🚫 **agent 不要碰 `ops/` 目录**（中继专供运维）；legacy 文件**不改**。

---

## 4. 共享资源 / 环境（务必注意）

- **双服务器独立挂载**：2.12 开发机前缀 `/nas_train/`；36.15 服务器前缀 `/nasdata/`。`eda_fastmcp` 在 36.15 位于 `/nasdata/app.e0031982/code/eda_fastmcp`（未迁移）。
- **共享工作副本**：多线共用 `super_intelligence_2035`；陌生未提交改动**可能是别的任务在途文件**，🚫 不要 clean / stash / reset。
- **`.env` 改写脚本必须串行 `&&`**（曾并发截断 `.env`）。
- **重 I/O / 全量扫描**避开评测窗口；**绝不整树 `du`**（175+ TB）。

---

## 5. 相关但独立的项目

- **BaiZe（ISEDA 2027）**：`doc/BaiZe-ISEDA2027/`，有自己的 4 条线 + 运维层（`doc/BaiZe-ISEDA2027/MEMORY.md`）与 ops（`doc/BaiZe-ISEDA2027/run/ops/`）。两项目**互补而非竞争**，互为引用。
