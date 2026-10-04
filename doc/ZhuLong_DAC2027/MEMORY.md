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
| **ops 中继** | `run/zhulong_ops_relay.sh` · `run/ops/` | 🟢 **在跑**（36.15，自 15:20） | ⚠️ **疑似两个进程**（PID `1071337` / `1239220`，待查 ppid）；**RUN_ID 1 已执行**（16:53，结果见 `outbox.md`） |

> ⚠️ **三处口径需要运维收敛**：① 合并线是否从 `S1.omega_low ROUND=1` 起跑，还是延续旧 S1（`ROUND=3`，复用 r1/r2）？② 36.15「旧 agent」与合并线的切换方式；③ 10-04 报告记「环境冻结」但任务书记「冻结令已解除」——**以任务书为准，冻结解除**（见 §9 流水）。

### 3.1 🆕 36.15 环境摸底结果（**RUN_ID 1，2026-10-04 16:53，host=`hfeg0tedaap02`**）

> 证据留痕：`run/ops/outbox.md`（RUN_ID 1）。**结论：infra 未就绪，且 zhulong_loop 存在静默失效。**

| 项 | 实测 | 判定 |
|:--|:--|:--|
| **host / user / GIT_ROOT** | `hfeg0tedaap02` · uid `app.e0031982` · `/nasdata/app.e0031982/code/super_intelligence_2035` | ✅ |
| **`/home`** | **394G 总 / 371G 用 / 6G 可用 / 99%** | 🔴 **FAIL**（infra 要求 ≥ ~8G）——**旧 S1 停摆的老根因复现** |
| `/nasdata` | 527G / 151G / 377G / **29%** | ✅ 宽裕 |
| `/tmp` | 49G / 25G 可用 / 54% | ✅ |
| **shard 端口 8664/8665/8653/8669** | 四个全 ✅ OPEN | ✅（但见下 `.env` PROXY_PORTS 口径不符） |
| **eda_fastmcp** | `/nasdata/app.e0031982/code/eda_fastmcp` 存在（含 `main.py` / `venv` / `kb` / `logs` / `memory_bank`） | ✅ 代码在 |
| **`run_code` 入口** | ✅ **实为 Python 工具**：`tools/run_code.py`（+ `server/sandbox_server/exec_code.py`），非 shell 脚本（探针误报） | ✅ 代码在（licence 需实跑验） |
| **进程：zhulong_loop** | ✅ **在跑**（PID `1069304`，ppid=1，etimes≈97min）——但**在跑的进程是旧版**（cline 带 `-b`）；**磁盘上的脚本已是新版**（第 112 行 `-P openai-compatible`，无 `-b`）→ **只需重启即修复** | 🔴 **静默失效**（RUN_ID 2 修正） |
| **进程：zhulong_ops_relay** | ✅ **单实例**：真 relay `1071337`（ppid=1）；另一 PID `1245242`（ppid=1071337、etimes=0）= 它 fork 的**子进程** → **不是副本**（与 BaiZe §3.5 结论一致） | ✅ 正常 |
| **`.env` 当前臂** | `EDA_OMEGA_FIDELITY=high` · `EDA_RUNCODE_READBACK=full` · `EDA_PHI_BUDGET=0` · `EDA_PHI_LAGGED=0` · **`EDA_MCP_TOOLS_DISABLED` 含 `get_api_details,search_apis,search_api…`（检索关）** | 🔴 反映**上一个臂 = `wo_retrieval`（检索 OFF + run_code ON）**，`.env` 已被改（git ` M .env`） |
| **端口** | ✅ 任务书口径正确：`ss` 实测监听 `8653/8664/8665/8668/8669/18890/9006`；`.env` 里 `PROXY_PORTS=8650-8654` 是**陈旧行**（未监听、未被使用） | ✅ 以 8664/8665/8653/8669 为准 |
| **机器负载 / `/home` 大头** | `/home` 下**多个其他用户**在跑 `eda_platform` / `eda_fastmcp` / sandbox bootstrap；**`/home` 大头是别的用户**（`app.e0023936` **71G** · `app.e0025768` 41G · `vendor.ai.ruide01` 24G · `app.t0002147/e0041392/e0030544` 各 16G …；**我们自己 `app.e0031982` <7.2G、不在 top-15**） | ⚠️ 高共享；**`/home` 满主因非本用户** → 自己可清空间有限 |

**🔴 关键结论 —— zhulong_loop 静默失效（与 BaiZe 的 `Forbidden+exit0` 同类）**：

```
[loop] 2026-10-04 16:53:19 wake up, invoking cline ...
error: error: unknown option '-b'
[loop] 2026-10-04 16:53:20 cline returned (exit 0), checking git sync ...
[loop] 2026-10-04 16:53:20 WAITING=0 (no blocker) → sleep 60s
```

- 36.15 上**正在跑的 `zhulong_loop.sh` 是旧版**，cline 调用里带**非法的 `-b`** → **cline 根本没运行**（`unknown option '-b'` 后直接 `exit 0`）→ **agent 从未被唤醒、任务书零推进**，却被 loop 当成成功。**当前"已启动"实为"空转"。**
- 仓库版本早已修复（`c3d52e9` 删 `-b`、`81d6869` 改 `-P openai-compatible`）→ **需在 36.15 `git pull` 后重启 loop**（bash 增量读脚本，改运行中的脚本无效）。
- 另：`MEMORY_ZHULONG.md` 顶部 `WAITING: 0`（loop 读这行）与状态表 `WAITING=1` 不一致 → loop 按"无阻塞"每 **60s** 空转（应 `1` → 30min）。**两处都要修。**

> 处置建议（待拍板）：**① 评估 `/home`（🔴 大头是别的用户，自己可清空间有限）→ ② 定起始点（R1 起 / 延续 R3）→ ③ 重启 `zhulong_loop.sh`（磁盘已是新版）→ ④ 开跑。**

**✅ RUN_ID 2 修正（2026-10-04 16:57，`outbox.md` RUN_ID 2）**：
- loop **确实在跑**（PID `1069304`/ppid=1）；**磁盘脚本已是新版**（112 行 `-P openai-compatible`，无 `-b`）→ **重启即修复**（证明运行进程没吃到新脚本）。
- relay **不是副本**（`1245242` 是 `1071337` fork 的子进程，etimes=0）。
- `run_code` = `tools/run_code.py`（+ `exec_code.py`）→ **存在**（探针误报）。
- 端口以 **8664/8665/8653/8669** 为准（`.env` 的 8650-8654 未监听 = 陈旧行）。
- loop 日志：**`unknown option '-b'` 计数 69** · `Forbidden` 0 · **16:57 仍报错**。
- **唯一硬阻塞 = `/home` 99%（6G）**，且**大头是别的用户** → 见 §4 待拍板。


---

## 4. 待拍板 / 我欠的答复

- [ ] **起始点**：合并线从 `S1.omega_low ROUND=1` 起，还是延续旧 S1（`CONFIG=omega_low, ROUND=3`，把 r1=81.6 / r2=82.3 写进成绩表、不重跑）？——**须运维在任务书指令区填实**。
- [x] **infra 三项校验（RUN_ID 1+2）**：① 🔴 `/home` **99% / 6G 可用 → FAIL**；② ✅ 四端口 OPEN；③ ✅ `run_code` 实为 `tools/run_code.py`（存在）。
- [ ] 🔴 **`/home`（硬阻塞）**：需 ≥ ~8G。实测**大头是别的用户**（`app.e0023936` 71G · `app.e0025768` 41G …），**我们自己 <7.2G** → 选项：(a) 只清自己可回收缓存（可能不够）；(b) 把评测产物从 `/home` 改到 `/nasdata`（377G 富余）；(c) 找系统管理员/其他用户。**待拍板。**
- [x] ✅ **loop 已重启并修复**（RUN_ID 6 重启清掉非法 `-b`；RUN_ID 8 `cline auth` 修 `openAiBaseUrl`→`/cloud/v1`）→ **agent 已于 2026-10-04 21:54 首次被唤醒**。
- [x] ✅ **relay 无副本**（第二条是子进程）；✅ **端口口径**以 `8664/8665/8653/8669` 为准。
- [x] ✅ **ops 中继健康**（RUN_ID 1–8 全 `exit=0`）；此前"卡死"系误判（heavy 版 17:05:57 已跑完，只是 push 重试）。
- [x] ✅ **`MEMORY_ZHULONG.md` 顶部已置 `WAITING: 1`**（21:44），避免 60s 空转烧 token。
- [ ] **处置顺序**：`/home` → 定起始点 → 修 `WAITING` → 重启 loop → 开跑。
- [ ] **36.15 旧 agent 冲突**：旧线（S1 / 组件）与新合并线**不能并发**；何时、如何停旧启新？
- [x] ✅ **启动 ops 中继** —— 已在 36.15 运行且健康（RUN_ID 1–8 全 `exit=0`）；运维已可用它远程探查/下发命令。
- [ ] 🔴 **接管 legacy 组件线（standalone 非 git `/nasdata/app.e0031982/code/ZhuLong_DAC2027`）**：两进程（组件 loop `2455466` + conductor `1381975`）**均已空转**（沙箱阻断 / `Forbidden`，详见 §9）。方案：① 停两进程；② harvest（`pure_llm×5` / `wo_retrieval r1=74.1%` 保留，`rag×5` 重跑）；③ 由合并线续跑余下臂。**待拍板。**
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
- **四 shard 端口**：`8664 / 8665 / 8653 / 8669`（⚠️ 但 36.15 `.env` 实际写的是 `PROXY_PORTS=8650,8651,8652,8654` —— **待核**）。
- **36.15 = `hfeg0tedaap02`**（uid `app.e0031982`）；**`/home` 是独立 LV、极易满**（2026-10-04 实测 **99% / 6G 可用**）→ **开跑前必查 `/home`**。
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
10. **🔴 loop 版本陈旧 → 静默失效**：36.15 在跑的 `zhulong_loop.sh` 曾带**非法 `-b`** → `error: unknown option '-b'` + `exit 0` → **cline 从未运行、agent 零唤醒**。**`grep -c \"unknown option\\|Forbidden\\|error:\" /tmp/zhulong_loop.log` 应作为日常体检首项**；改脚本后**必须重启 loop**（bash 增量读，改运行中的脚本无效）。
11. **🔴 `-b` / `-k` / `-P` 是 cline CLI 的敏感参数**：`-b` 非法（会中断）；正确是 `-P openai-compatible` + `-k <key>`（见 `zhulong_loop.sh`）。凡 loop 变更后先在服务器 `cline ... ; echo $?` 冒烟。
12. **🟡 pgrep 正则双重转义会漏报**：预置探针里 `'zhulong_loop\\\\.sh'` 在 bash ERE 下变成"要求字面反斜杠" → **匹配不到真实进程**（RUN_ID 1 就漏报了 loop）。写 `pgrep -af 'zhulong_loop'` 更稳。
13. **🟡 `MEMORY_*.md` 的 `WAITING` 只有顶部行被 loop 读取**：表格里的 `WAITING=1` 与顶部 `WAITING: 0` 不一致时，**以顶部为准**（会误判成"无阻塞"而高频空转）。
14. **🔴 ops relay 块内禁止「无 `timeout` 的命令」和「`du -L`/跟随符号链接」**：2026-10-04 **RUN_ID 4 疑似卡死中继** —— 块里用了 `df -h <symlink>`（**未** `timeout`）+ `du -sh -L`（跟随到 `/nasdata` 大树）→ `timeout` 只杀 leader、子进程占住管道 → 中继读不到 EOF、`.last_run_id` 停摆（**同 BaiZe §7 教训**）。**铁律：relay 块里<u>每条</u>命令都要 `timeout`；一律 `du -x` 不跟 symlink；重活丢后台 + 落盘 + `.done`。**

15. **🔴 cline `error: Forbidden` = `openAiBaseUrl` 与模型不匹配**：2026-10-04 RUN_ID 7/8 —— 36.15 的 cline `globalState.json` 里 `openAiBaseUrl=http://agi-gateway.cxmt.com/v1`，而 **glm-5.2 必须用 `/cloud/v1`**（`/v1` → `Forbidden`）。且 loop 只传 `-k/-P`、**不提供 base URL**，必须靠 cline 配置（`cline auth -b ...`，或 BaiZe 那种隔离 `--data-dir`）。**修法**：`cline auth -p openai -k <key> -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` → 重启 loop。**对照** `baize_data_loop.sh` §46（flash@/v1=200 但 @/cloud/v1=403）。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **2026-10-04（22:1x 侦察 + 接管尽调：查明"另一个 agent"= legacy 组件线，两进程均已空转）** —— 用户告知另有 agent 在 `/nasdata/app.e0031982/code/ZhuLong_DAC2027` 跑任务，要求观摩、理解、准备接管。经 ops 中继 **RUN_ID 10–14** 只读侦察：
  - **身份**：**legacy 组件线**（旧「Phase 1 组件消融 + Phase 2 S2 Φ」5-run 线），跑在**独立、非 git** 的项目副本 `/nasdata/app.e0031982/code/ZhuLong_DAC2027`（与 git 仓库 `super_intelligence_2035/doc/ZhuLong_DAC2027` 平行）。
  - **两个 driver 都空转**：① `ablation_run_loop_component_s2_full.sh`（PID 2455466，`MODEL=deepseek-v4-pro-fp4`，30min/轮）—— 其 cline 会话**连续 ≥4 周期被沙箱阻断**（`run_commands`→ACCESS RESTRICTED），无法推进；② `ablation_run_conductor_serial.sh`（PID 1381975，**已跑 3.3 天**）—— 日志每 30min `error: Forbidden`，**3.3 天零产出**。
  - **已产出的真实数据（接管应 harvest）**：`pure_llm ×5 = 10.5±1.9%`、`rag ×5 = 68.2±7.4%`（**BM25 降级态，需重跑**）、`wo_retrieval r1 = 74.1%`（117/158，10-04 14:40 已跑完，但 agent 被阻断读不到）；另有 1-shot：full 84.8 / k10 75.3 / k3 69.0 / k1 60.8 / lagged 80.4·84.2 / omega_low r2 82.3。
  - **冲突**：两线共用同一评测 infra（eda_fastmcp + MCP 8090 + `.env`），**不能并发跑 eval**；合并线（git、glm-5.2 编排）本就设计为**取代** legacy 线。
  - **接管方案（待拍板）**：停 legacy 两进程 → harvest 有效数据 → 由合并线续跑余下臂。
- **2026-10-04（19:0x–21:54 运维亲自经 ops 中继打通整条链路：中继正常 + loop 修复 + agent 终被唤醒）** ——
  - ✅ **中继"恢复正常"**（此前"RUN_ID 4 卡死"系**误判**）：亲手实测 `run/ops/outbox.md` RUN_ID 1–8 **全部 `exit=0`**；RUN_ID 4 heavy 其实 **17:05:57 就跑完**，只是 `push` 反复失败在重试。**反思**：把"push 失败"错当成"卡死"，并据错误判断写了"抢救中继"指令。
  - 🔴 **发现 loop 静默失效（比 `-b` 更深一层）**：RUN_ID 5/6 实测 —— 运行中的 loop 是**旧版**（`error: unknown option '-b'`，累计 **352** 次，cline 从未真正运行）→ RUN_ID 6 重启 loop 后 `-b` 消除，但**新 loop 改报 `error: Forbidden`**。
  - ✅ **定位并修复 Forbidden**（RUN_ID 7/8）：`curl -H "Authorization: Bearer <key>" http://agi-gateway.cxmt.com/cloud/v1/models` = **HTTP 200**（key 有效、网关可达），但 cline `globalState.json` 的 `openAiBaseUrl` = **`http://agi-gateway.cxmt.com/v1`（错）** —— glm-5.2 需 **`/cloud/v1`**（对照 `baize_data_loop.sh` §46 教训）。`cline auth -p openai -k <key> -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` → "Provider configured: openai-compatible (glm-5.2)" → 重启 loop → **agent 首次被唤醒**（loop 日志出现真实推理）。
  - 落地：dispatch `c588835`/`864eb86`/`2e4fa8c`/`0ca6cb2`；结果 `0638999`/`33089f2`/`bfedfc7`/`5be7be1`。任务书新增「（三）中继已恢复·勿再抢救」；`MEMORY_ZHULONG.md` 顶部置 `WAITING: 1`。
  - ⏭ 待办：agent 已在跑，将做 infra 校验；**`/home` 处置 + 起始点**仍待拍板。
- **2026-10-04（运维不在场 → 经任务书派 agent 抢救中继）** —— 用户告知**无法登录服务器**（不在公司），但 ZhuLong agent 应仍可被任务书驱动 → 指令我**把中继救回来**。
  - 落地：在 `run/ZHULONG_TASK.md` 运维指令区**置顶**新增 **`### 🚨 运维指令 · 2026-10-04（二）【本次唤醒的首要动作】抢救 ops 中继`**（`18587bf`）：
    ① `pkill -f zhulong_ops_relay.sh` + `pkill -f 'du -sh -L'` → ② `git pull` + `setsid bash zhulong_ops_relay.sh` 重启 → ③ 在 `MEMORY_ZHULONG.md` 流水回报；**明确授权 agent 本次可动中继进程**（突破既有"agent 不要碰 ops/"），但**不许改 `ops/` 文件**。
    另附**可选**：重启 `zhulong_loop.sh` 以清 `-b`（谨慎，会中断其自身会话）。
  - ⚠️ **前提风险**：该指令只有**agent 真的被唤醒**才生效。而 RUN_ID 2 证据显示**运行中的 loop 仍报 `-b`**（旧脚本被 bash 整段缓存）→ 若它一直没吃到新版脚本，则 **task book 改动会一直躺着**，仍需**人工重启 loop**（唯一能远程解卡的手段 = 中继/loop 重启，而我们已无中继）。**观察点**：中继恢复后 `outbox.md` 应出现 RUN_ID 4（轻量版）结果。
- **2026-10-04（RUN_ID 3 我方 home 盘点 → 结论：清不出空间；RUN_ID 4 重块卡死中继）** ——
  - ✅ **RUN_ID 3（17:01）**：`/home/app.e0031982` 同文件系统**仅 3.8M**；`.cache`/`.cline`/`.npm`/`.local`/`.vscode-server` 的 `du -x` 全 **0**、`eda_code_eval`（87 批次）也是 **0** → **疑似 symlink 到 `/nasdata`**。→ **自己 home 清不出 ≥8G**，`/home` 满纯属别的用户。
  - ⚠️ **RUN_ID 4（17:03）我写的重块卡死中继**（`du -sh -L` 跟随 symlink + 未 `timeout` 的 `df`）→ 已**重写为轻量版**（`a450ead`）+ heavy 版降级 `text`；坑入 §7-14。**恢复**：等 `du -L` 结束，或 `pkill -f zhulong_ops_relay.sh` 后重启（会自动补跑轻量 RUN_ID 4）。
  - 待拍板收敛为：`/home` 选项 (b)/(c) + 起始点。
- **2026-10-04（RUN_ID 2 聚焦诊断 → 收敛为"唯一硬阻塞 = `/home`"）** —— 经 ops 中继跑只读诊断（`outbox.md` RUN_ID 2，16:57，exit=0）：
  - ✅ **loop 确实在跑**（PID `1069304`，ppid=1，etimes≈97min）；**磁盘上的 `zhulong_loop.sh` 已是新版**（112 行 `-P openai-compatible`，**无 `-b`**）→ **运行进程没吃到新脚本 → 重启即修复**（loop 日志 16:57 仍在报 `-b`，`unknown option` 计数 **69**、`Forbidden` 0）。
  - ✅ **relay 不是副本**：`1245242`（ppid=`1071337`、etimes=0）= 真 relay fork 的**子进程**（同 BaiZe §3.5 结论）。
  - ✅ **`run_code` 存在**：`tools/run_code.py`（+ `server/sandbox_server/exec_code.py`），非 shell 脚本（RUN_ID 1 探针误报）。
  - ✅ **端口**以 `8664/8665/8653/8669` 为准（`.env` 里 `PROXY_PORTS=8650-8654` 未监听 = 陈旧行）。
  - 🔴 **`/home` 99%（6G）= 唯一硬阻塞**，且**大头是别的用户**（`app.e0023936` 71G · `app.e0025768` 41G · `vendor.ai.ruide01` 24G …；**我方 `<7.2G`**）。
  - 下一步：**定 `/home` 处置 + 起始点 → 修 `WAITING` → 重启 loop**（见 §4）。
- **2026-10-04（RUN_ID 1 环境摸底 → 发现两处致命问题）** —— 经 ops 中继在 36.15（`hfeg0tedaap02`）跑环境摸底，结果见 §3.1 / `run/ops/outbox.md`：
  - 🔴 **`/home` 99%（仅 6G 可用）→ infra 前置校验 FAIL**（旧 S1 停摆老根因复现）。
  - 🔴 **`zhulong_loop.sh` 静默失效**：在跑的版本 cline 带非法 `-b` → `unknown option '-b'` + `exit 0` → **agent 从未被唤醒**（"已启动"实为"空转"）。
  - ⚠️ relay 疑似两个进程；`MEMORY_ZHULONG.md` 顶部 `WAITING: 0` 与表 `1` 不一致（loop 读顶部 → 60s 空转）；`.env` `PROXY_PORTS=8650-8654` 与任务书口径不符；四端口 8664/8665/8653/8669 实测 OPEN。
  - 处置建议见 §3.1 末尾（清 `/home` → 修 `WAITING` → `git pull`+重启 loop → 查 relay → 定起始点）。
- **2026-10-04** —— **建立 ZhuLong 运维（operator）层**（对齐 BaiZe）：新建 `doc/ZhuLong_DAC2027/MEMORY.md`（本文件）+ `doc/ZhuLong_DAC2027/daily-memories/`，并在 `run/AGENTS.md` 登记「谁在跑」总表、在 `README.md` 补 `§0.2 运维层`。背景：此前运维侧**没有记忆**，多线（合并线 + 3 条 legacy）状态散落在任务书/报告/各 `MEMORY*.md` 里，易数错。
- **2026-10-04（agent 线侧，供我参考）** —— 建立**合并任务书 + 单 loop + ops 中继**：`run/ZHULONG_TASK.md`（4 阶段 15 臂 75 轮）· `run/zhulong_loop.sh` · `run/zhulong_ops_relay.sh` + `run/ops/`。任务书记「冻结令已解除、编排模型切 `glm-5.2`」；旧报告 `report_10_04.html` 仍记「环境冻结中（36.15 旧 agent 冲突）」——**以任务书为准**，冲突待 §4 拍板处置。
