# MEMORY.md — ZhuLong（DAC 2027）**运维（operator）** 长期记忆 · **醒来先读本文件**

WAITING: 0

> ⚠️ **本文件在项目根**（`doc/ZhuLong_DAC2027/`），是**运维侧**（指挥 ZhuLong 任务线的那 个"我"）的状态文件。
> **不属于任何 agent 线** —— 推进 agent 的记忆在 `run/MEMORY_ZHULONG.md`；旧各线记忆在 `run/MEMORY*.md`（**只读历史**）。
> 运维日流水在**本目录** `daily-memories/<YYYY-MM-DD>.md`（**不要**与 `run/daily-memories/` 混淆——后者是各 agent 线的）。
> 纪律：**`WAITING:` 只在顶部出现一次**；**≤32KB**，超限把较早流水滚动到 `daily-memories/`。
> 模板参照：`doc/BaiZe-ISEDA2027/MEMORY.md` + `doc/BaiZe-ISEDA2027/daily-memories/`（BaiZe 的运维层）。

---

## 0. 我是谁 / 我的角色

- 我是本项目 `doc/ZhuLong_DAC2027` 的**外部运维**：**不登录评测 / 开发服务器**（36.15 与 2.12）。
- **下达通道 ①** = 任务书 `run/ZHULONG_TASK.md` 的 `## 🔧 运维指令区（OPERATOR NOTES）`（**改文件 + git commit/push**；新块放最前，老块不改，留作历史）。
- **下达通道 ②** = ops 中继 `run/ops/inbox.md`（RUN_ID 机制，**改文件 + git push**；只执行文件里<u>第一个</u> ```bash 块）。
- **查看通道** = 读 `run/MEMORY_ZHULONG.md`（顶部状态头 / 执行看板 / 成绩表）+ `run/daily-memories/` + `run/ops/outbox.md`（`git pull` 即可，**不登录服务器**）。
- 我指挥的是 **1 条正式线**：**合并消融线**（`S1` 保真度 → `C1` 组件 → `C2` S2-Φ → `B` 模型，**15 臂 × 5 轮 = 75 轮**，单任务书 + 单 loop）。

---

## 1. 每次「醒来」的固定动作（SOP）

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`
   （远端推进快——多线共用一个工作副本，**不 pull 直接改会冲突**）。
2. **读本文件**：尤其 §3 在途 / §4 待拍板 / §5 铁律 / §6 关键事实 / §7 已知坑。
3. **读 agent 侧状态**：`run/MEMORY_ZHULONG.md` 顶部 + `git log --oneline -20` + `run/ops/.last_run_id`（+ 有结果时 `run/ops/outbox.md` 末尾）。
4. **处理回写**：有 agent 产物 / 答复 → 读、核、必要时答复（写进 `ZHULONG_TASK.md` 运维指令区 或经 ops relay）。
5. **下发新任务**：在 `run/ZHULONG_TASK.md` 运维指令区加 **带日期的 block**（**越靠前越优先**；老块不改）。
6. **提交**：`git add` **只加自己动的文件** → `commit` → `push`。**不要 `git add -A`**。
7. **回写本文件 + 当日 `daily-memories/<date>.md`**。

---

## 2. 通讯协议 / 接口（关键认知）

- **接口 ① 任务书运维指令区** = `run/ZHULONG_TASK.md` 顶部 `## 🔧 运维指令区（OPERATOR NOTES）`。
  - **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；**新块放前面**，写清 **优先级 / 顺序 / 判据 / 铁律**。
  - **agent 回写位置**：`run/MEMORY_ZHULONG.md`（状态头 + 执行看板 + 成绩表 + 流水）、`run/daily-memories/`、论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。**agent 不改运维指令区**。
- **接口 ② ops 中继** = `run/ops/{inbox,outbox,README}.md` + `run/zhulong_ops_relay.sh`。
  - 运维在 `inbox.md` 里写 ```bash 块、`<!-- RUN_ID: N -->` 加 1、`git push`；中继轮询到 RUN_ID 增大即执行，结果**只增不改**追加到 `outbox.md` 末尾（最新在**最下方**）。
  - ⚠️ **只执行文件里第一个 ```bash 块** —— 下发新命令必须把块放**最前**、把旧块降级为 ```text、RUN_ID +1。
- **与 BaiZe 独立**：ZhuLong ops（`doc/ZhuLong_DAC2027/run/ops/`）与 BaiZe ops（`doc/BaiZe-ISEDA2027/run/ops/`）**各有 relay 进程 / inbox / outbox / last_run_id**，互不干扰。共享同一 git 仓库 → 各自只 `git add` 自己的文件。

---

## 3. 在途任务（截至 2026-10-04）

| 线 | 脚本 / 任务书 / 记忆 | 在飞 | 状态 |
|:--|:--|:--|:--|
| **合并消融线（新 · 正式）** | `run/zhulong_loop.sh` · `run/ZHULONG_TASK.md` · `run/MEMORY_ZHULONG.md` | **未启动** | 🟠 `PHASE=init`、`WAITING=1`（仅 bootstrap 一条流水）；等 **infra 三项前置校验** + **起始点拍板** |
| 旧 S1 保真度线（legacy） | `run/ablation_run_task_s1_full.md` · `run/MEMORY_s1_full.md` | 10-03 曾活动 | ⬜ **只读历史**；与合并线**待衔接**（旧 5-run：`omega_low` r1=81.6 / r2=82.3，r3 infra 作废） |
| 旧组件线（legacy） | `run/ablation_run_task_component_s2_full.md` · `run/MEMORY_component_full.md` | 10-04 曾活动 | ⬜ **只读历史**；可能**仍在服务器上跑**（`pure_llm`→`rag`→`wo_retrieval`），**待与 36.15 旧 agent 冲突一并处置** |
| 旧 S2 1-shot 探路线 | `run/ablation_run_task_s2_1shot.md` · `run/MEMORY_s2_1shot.md` | 已出探路值 | ⬜ 只读历史 |
| **ops 中继** | `run/zhulong_ops_relay.sh` · `run/ops/` | ❌ **未启动** | `outbox.md` 空、`.last_run_id=0`；RUN_ID 1（环境摸底）已预置，**待服务器 `setsid` 启动** |

> ⚠️ **三处口径需要运维收敛**：① 合并线是否从 `S1.omega_low ROUND=1` 起跑，还是延续旧 S1（`ROUND=3`，复用 r1/r2）？② 36.15「旧 agent」与合并线的切换方式；③ 10-04 报告记「环境冻结」但任务书记「冻结令已解除」——**以任务书为准，冻结解除**（见 §9 流水）。

---

## 4. 待拍板 / 我欠的答复

- [ ] **起始点**：合并线从 `S1.omega_low ROUND=1` 起，还是延续旧 S1（`CONFIG=omega_low, ROUND=3`，把 r1=81.6 / r2=82.3 写进成绩表、不重跑）？——**须运维在任务书指令区填实**。
- [ ] **infra 三项前置校验是否恢复**：`/home` ≥ ~8G · 端口 `8664/8665/8653/8669` 全 OPEN · `run_code` 可执行（license 可用）。→ 用 **ops RUN_ID 1 摸底**确认。
- [ ] **36.15 旧 agent 冲突**：旧线（S1 / 组件）与新合并线**不能并发**；何时、如何停旧启新？
- [ ] **启动 ops 中继**（服务器侧 `setsid bash zhulong_ops_relay.sh`）——启动后我才能远程探查/下发命令。
- [ ] **Phase B 模型 key 是否仍有效**（`glm-5.2` / `deepseek-v4-flash` / `kimi-k2.6-cloud` / `doubao-seed-2.0-pro-cloud`，见任务书 §6）——启动 Phase B 前须核。
- [ ] **RAG recall 端口错配**（`.env` 9012 死 / 9006 健康 = `chroma_db_v20260522`）是否修？——现为 r1/r2 的既存降级条件（BM25-only fallback）。**投稿前须闭环或如实披露**。
- [ ] **`tab:omega` 的 (H)/(H+E)/(L)**：锚点复用规则下 (H)/(F) 由 `C1.full` 复用；`(H+E)` 已定**不做**；`(L)` 由 `omega_low` 提供——确认无遗漏。
- [ ] **RQ3（SKILL / Tcl 切片）** 是否纳入本轮（依赖最重，任务书列为最后）。

---

## 5. 铁律（不得违反）

1. **文档与论文树分离**：`doc/ZhuLong_DAC2027/ZhuLong_DAC2027/` 是**唯一可改 LaTeX 树**；`Grounding/ICML2028/` 是**理论权威**（理论冲突以它为准）；`ZhuLong_ASPDAC2027/` 与任何 `*.orig` **只读、不改、不引用**。
2. **回填数字同步改**：同一表内 `Δ` 列 + 正文引用的**同一数字必须同步**改，防表文矛盾（README §6）；`78.5` 须全仓库一致。
3. **`±` 只加在 Pass@1**：`Δ` / `Converged (%)` / `Mean read-backs` / `Avg/Trace` 为**单值**，不加 `±`（README §4.1）。
4. **未测不填**：未测留 `[TBD]` 或显式 `provisional`；**绝不臆造数字**。
5. **反作弊 hook 是冻结变量**：所有臂一致、每批开跑前做 **canary**；**失效批一律作废**；**内部反作弊数字（如未隔离 pure LLM >98%）绝不写入论文**。
6. **`Φ` 语义**：预算约束的是「能执行/能观测多少次」，**不是**「何时提交」；`errorMessage` 必须带唯一前缀（`[PHI-BUDGET-EXHAUSTED]`），避免与反作弊 hook 拒绝原因混淆。
7. **`.env` 改写脚本串行**：切臂命令必须 `&&` 串行，**严禁并发**（曾并发截断 `.env`）。
8. **infra 作废规则**：license 耗尽 / 端口宕 / 磁盘 <8G → **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检；**绝不拿作废批冒充有效分**。
9. **git**：只 add 自己动的文件；远端高频抢占时用**后台重试循环**（`fetch → rebase --autostash → push`）。

---

## 6. 关键事实（写给未来的我）

- **交付目标**：把论文 **6 张表、56 个 `[TBD]`（30 行）** 换成实测 `mean ± std`。表 = `tab:selfdoc-cost`(6) · `tab:main-ablation`(7) · `tab:omega`(6) · `tab:ablation-harness`(9) · `tab:phi-bound`(14) · `tab:llm-comparison`(14)。
- **冻结协议**：数据集 `EDA-Eval-PyAether` **158 任务**；`Pass@1 = 通过/158×100%`；单次执行超时 **2500s**；**单 trace 不跨 trace 重启**；**每配置 5 次独立运行**（重排任务序 + 全新 context）→ `mean ± std`；主 backbone `deepseek-v4-pro-fp4`（**只有 `B` 阶段换**）。
- **路径（两台服务器独立挂载）**：36.15（最终目标）前缀 `/nasdata/`，`BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`；2.12（开发机）前缀 `/nas_train/`。旧 task book 里 `/nasdata/` 路径在 36.15 上**仍有效**。
- **repo**：`git@github.com:foamliu/super_intelligence_2035.git`，分支 `main`；仓库根在共享工作副本。
- **编排模型** = `glm-5.2`（`deepseek-v4-pro-fp4` 额度已耗尽，故换）；key 见 `run/zhulong_loop.sh`（**不在本文件重复明文**）。
- **四 shard 端口**：`8664 / 8665 / 8653 / 8669`。
- **锚点复用（跑一次多处引用，禁止重跑）**：`C1.full ×5` = `tab:main-ablation`(full) + `tab:omega`(H) + `tab:ablation-harness`(F) + `tab:phi-bound`(unbounded) + `tab:llm-comparison`(主基座)。
- **不做**：`wo_sandbox` / `wo_selfexpl`（main-ablation 两行暂缓）· `(H+E)` 档 · `phi_unbounded`（≡ full）· 主基座模型消融臂（≡ full）。

---

## 7. 已知坑 / 教训（会复发，需周期检查）

1. **🔴 agent 沙箱周期阻断**：`run_commands` 全量被替换为 `ACCESS RESTRICTED ...`、`read_files` 读 `/tmp` 被改写为 `/dev/null`。**历史规律 3~5 个唤醒周期自动复通**；**连续 ≥4 周期建议人工介入**。（10-03 / 10-04 已多次遇到。）
2. **🔴 token 时额耗尽 → 假低分**：`deepseek-v4-pro-fp4` 时额约每小时复位；故障批（如 10-04 rag r3 `27.8%`）**必须作废并归档无效日志**，不得当有效分。
3. **🔴 infra 三因致整批作废**：`/home` 磁盘满 + license 耗尽 + shard 端口宕。**开跑前必做三项前置校验**（任务书 §7 步骤 0）。
4. **🔴 未隔离 = 抄答案**：反作弊 hook 静默失效时 pure LLM 曾 >98% —— **每批 canary**；**该数字仅限内部，勿入论文**。
5. **🟡 ops inbox 只执行第一个 ```bash 块**：新块放最前、旧块降级 ```text、RUN_ID +1。
6. **🟡 长输出 / 全量扫描危险**：`pgrep -af` 会把整份任务书打出来（加 `cut -c1-140`）；**绝不整树 `du`**（`/nasdata`/`/nas_train` 有 175+ TB），只用 `df` + 有界定向 `du`（每条带 `timeout`）。
7. **🟡 `.env` 并发截断**：切臂脚本串行 `&&`，严禁并发。
8. **🟡 git fetch 在高峰期 >30s**：PowerShell 会把 git stderr 当异常 → 用 `cmd /c "... > log 2>&1"` + **后台重试循环**。
9. **🟡 共享工作副本**：多线共用 `super_intelligence_2035`；陌生未提交改动**可能是别的任务在途文件**，🚫 不要 clean/stash/reset。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **2026-10-04** —— **建立 ZhuLong 运维（operator）层**（对齐 BaiZe）：新建 `doc/ZhuLong_DAC2027/MEMORY.md`（本文件）+ `doc/ZhuLong_DAC2027/daily-memories/`，并在 `run/AGENTS.md` 登记「谁在跑」总表、在 `README.md` 补 `§0.2 运维层`。背景：此前运维侧**没有记忆**，多线（合并线 + 3 条 legacy）状态散落在任务书/报告/各 `MEMORY*.md` 里，易数错。
- **2026-10-04（agent 线侧，供我参考）** —— 建立**合并任务书 + 单 loop + ops 中继**：`run/ZHULONG_TASK.md`（4 阶段 15 臂 75 轮）· `run/zhulong_loop.sh` · `run/zhulong_ops_relay.sh` + `run/ops/`。任务书记「冻结令已解除、编排模型切 `glm-5.2`」；旧报告 `report_10_04.html` 仍记「环境冻结中（36.15 旧 agent 冲突）」——**以任务书为准**，冲突待 §4 拍板处置。
