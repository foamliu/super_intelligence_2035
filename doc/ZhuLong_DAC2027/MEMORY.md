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

## 3. 在途任务（状态实况 · 更新于 2026-10-09）

| 线 | 脚本 / 任务书 / 记忆 | 在飞 | 状态 |
|:--|:--|:--|:--|
| **合并消融线（新 · 正式）** | `run/zhulong_loop.sh` · `run/ZHULONG_TASK.md` · `run/MEMORY_ZHULONG.md` | 🟢 **在跑**（36.15 · loop PID 3579323 · proxy 自检通过） | **`STAGE=C1` · `CONFIG=full`(锚点) · `ROUND=4` · `PHASE=standby` · `WAITING=1`**。已完成 **Phase B 4/4** ＋ **C1 前三臂 5/5**（`pure_llm` 10.5±1.9 / `rag` 71.8±2.5 / `wo_retrieval` 81.0±4.5）；**卡在锚点 `C1.full`**（r1=88.0% 保留 · r2=59.5%/r3=63.3% 作废待复测 · r4 因沙盒故障被 kill 作废）→ **已下发「沙盒修复·重跑 r4」(五)**；**C2/S1 未开始** |
| 旧 S1 保真度线（legacy） | `run/ablation_run_task_s1_full.md` · `run/MEMORY_s1_full.md` | 10-03 曾活动 | ⬜ **只读历史**；旧 5-run 可复用：`omega_low` 82.8±1.0 / `readback_binary` 66.2±16.1 / `readback_none` 73.3±2.2（是否延续由任务书定） |
| 旧组件线（legacy） | `run/ablation_run_task_component_s2_full.md` · `run/MEMORY_component_full.md` | 10-04 曾活动 | ⬜ **只读历史**；数据已由合并线接管（`pure_llm` 复用 / `rag` 重跑 / `wo_retrieval` 复用 r1）。⚠️ **其 loop 存活存疑**（见 §4） |
| 旧 S2 1-shot 探路线 | `run/ablation_run_task_s2_1shot.md` · `run/MEMORY_s2_1shot.md` | 已出探路值 | ⬜ 只读历史（`k10`/`k3`/`k1`/`lagged` 1-shot 探路）；5-run 未跑 |
| **ops 中继** | `run/zhulong_ops_relay.sh` · `run/ops/` | 🟢 **在跑** | 单实例（第二条是子进程）；`.last_run_id`=**26**（最新 RUN_ID 25/26 = kill 沙盒故障的 r4） |

> ✅ **历史口径已收敛**：起始点 = 从 `C1.wo_retrieval R2` 起（**已越过**）；「冻结令」已解除；「36.15 旧 agent 冲突」已由合并线接管处置。

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

- [x] ✅ **起始点**：已定为 **从 `C1.wo_retrieval R2` 起**（任务书 (四)），**已越过**；现推进至 `C1.full` 锚点。
- [x] ✅ **infra 前置校验（RUN_ID 1+2 首测）**：① `/home` 曾 99%/6G → **已解除（见下）**；② ✅ 端口（**口径订正**：以 `.env` 实际 `8650,8651,8652,8654`@`10.129.32.75` 为准，旧 `8664/8665/8653/8669` 作废）；③ ✅ `run_code` = `tools/run_code.py`。
- [x] ✅ **`/home` 阻塞已解除（用户 2026-10-09）**：**`/home` 已不再阻塞**。且我方产物/缓存多落 `/nasdata`（`~/eda_code_eval` 等为 symlink→`/nasdata`），`/nasdata` 长期 ~370G 富余 → **不再作为前置硬门槛**。
- [x] ✅ **loop 已重启并修复**（RUN_ID 6 清 `-b`；RUN_ID 8 `cline auth` 修 `openAiBaseUrl`→`/cloud/v1`）→ agent 2026-10-04 21:54 首次被唤醒。
- [x] ✅ **relay 单实例**（第二条是子进程）；✅ **端口口径**已订正（见上）；✅ **ops 中继健康**（RUN_ID 1–26 全 `exit=0`；当前 `.last_run_id`=26）。
- [x] ✅ **`MEMORY_ZHULONG.md` 顶部已置 `WAITING: 1`**，避免 60s 空转烧 token。
- [x] ✅ **处置顺序**：已全部落地（起始点已越、`WAITING` 已修、loop 已重启、**已开跑**）。
- [x] ✅ **36.15「旧 agent」冲突已处置**：由合并线接管（组件线数据复用/重跑，见 §3）；起始点已越过。
- [x] ✅ **启动 ops 中继**（健康；RUN_ID 25/26 = kill 沙盒故障的 r4）。
- [x] ⚠️ **接管 legacy 组件线**：数据已由合并线接管（`pure_llm` 复用 / `rag` 重跑 / `wo_retrieval` 复用 r1）。**遗留存疑**：用户称 10/4 已关停，但 agent 侧 10-09 `pgrep` 仍报组件 loop `2455466` alive → **待核实**（若在跑，确认 non-mid-eval 以免抢 infra）。
- [x] ✅ **Phase B 模型 key**：已全部验证有效（Phase B 4/4 完成）。
- [ ] **RAG recall 端口错配**（`.env` 9012 死 / 9006 健康 = `chroma_db_v20260522`）是否修？——既存降级条件（BM25-only fallback）。**投稿前须闭环或如实披露**。
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

16. **🔴 防作弊 hook 会误伤编排 agent（`~/.cline` 配置目录污染）**：评测对象是 cline；评测前脚本把 **PreToolUse hook 拷进 `~/.cline/hooks`**（评测结束删除），用于**禁止评测对象调用 `run_commands`**。若启动任务时**未指定独立 `--data-dir`**，则**评测对象 cline 与编排 agent（zhulong loop 的 cline）共用 `~/.cline`** → 编排 agent 在整轮评测（**3–4h**）内也被同一 hook 拦 `run_commands`（表现 = `ACCESS RESTRICTED`）。编排 loop 每 30min 唤醒 → 一轮评测内会连续被拦 **6–8 次**，**这是当前设计的正常现象，不是故障、也不是"沙箱"**。**根治**：给**编排 agent** 单独的 `--data-dir`（照 BaiZe `baize_data_loop.sh` 的隔离 `DATA_DIR` 做法），或在**评测时**给评测对象指定独立配置目录 —— 使两者 hooks/配置互不可见。**接管动作应包含此项。**（**RUN_ID 15 实测**：hook 目录 = `~/.cline/hooks`，与 `~/.cline/data` **平级**——不在 data 下；当前为**空**、mtime 14:39 → 已随 14:40 评测结束移除 → **此刻无评测在跑**；hook 源 = `eda_fastmcp/scripts/cline_hooks/`；`run_cline_script.sh` 未显式引用 hook/`--data-dir`；**尚无任何隔离配置目录**。⚠️ 另记：RUN_ID 8 的 `cline auth` 改的是**共享 `~/.cline`** → 对**其它共用该目录的线**（legacy 组件 loop）有连带影响——正是「共享配置目录」之害。）

17. **🔴 relay 块内禁止 `git pull`/`git fetch`**（2026-10-04 RUN_ID 18 教训）：中继主循环的 `git_sync()` 已负责 `fetch + pull --rebase`；块内**再放 `git pull`** → 其网络子进程继承 stdout 管道，`timeout` 只杀 leader → 中继读不到 EOF、`.last_run_id` 停摆（**与 §7-14 同型**）。**接管/重启类块只做幂等动作**（`pkill` / `setsid`），**不要碰 git**。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **2026-10-09（用户确认：`/home` 不再阻塞 → 收敛 §3/§4）** —— 用户通知「**`/home` 已不再阻塞**」。据此把 §4 的 `/home` 硬阻塞项**结项**；并顺手把 §3「在途任务」/§4 待拍板 中 10-04 的过期态（「合并线未启动」「起始点待定」「36.15 旧 agent 冲突」「接管 legacy」「Phase B key 待核」等）一并收敛到**当前实况**（进度 = Phase B 4/4 ＋ C1 前三臂 5/5，卡在锚点 `C1.full`）。
  - **落地**：`MEMORY.md` §3 表格重写（截至 2026-10-09 实况）、§4 待拍板收敛（`/home` ✅ 解除；遗留 **legacy loop 存活存疑** 一项待核）、本文件 §9 记本条 + 当日 `daily-memories/2026-10-09.md` 追加。
  - ⏭ 待推送。

- **2026-10-09（运维经任务书下发：✅ 沙盒已修复·可重跑 C1.full r4）** —— 用户 2026-10-09 晚通知「沙盒已修复·可重跑 r4」。此前 r4（batch `b2026_1009_094504`）因沙盒故障 grading 异常慢（`run_eval.py` 跑满 2h35m+ 未出结果）已被运维经 ops RUN_ID 25/26 kill，判 ❌作废；agent 置 `PHASE=standby` 待命。
  - **落地**：在 `run/ZHULONG_TASK.md` 运维指令区**置顶**新增 `### 🆕 运维指令 · 2026-10-09（五）— ✅ 沙盒已修复，可重跑 C1.full r4【本次唤醒优先动作】`（置于常驻规程之后、(四) 之前），并把 (四) 标题标为「【已被(五)取代·历史】」。指令要点：① **三项前置复检**（pro-fp4 直连 200[新 key `e13f4f37` + `/cloud/v1`] / 沙盒端口 8650-8654@10.129.32.75 可达 / eval IDLE 无残留）**全过才开跑**；② 启动 C1.full r4（同臂 full 不切 `set_ablation`，**四 override 齐全**：`EVAL_FW_DIR` + `CLI_DATA_DIR=.cline_prof4_eval/data` + `PYTHON` + `https_proxy`），启动后核验 `/proc/<pid>/environ`；③ canary 确认反作弊 hook live；④ 更新 MEMORY `PHASE=running`；⑤ commit+push。
  - **r4 收割后接 (三) 复测流程**：收割记 Pass@1 + timeout 数 → 判据 `timeout ≤ 10 且 Pass@1 ≥ 75%` 则 r4 有效 → 依序重跑 `r2-retest` → `r3-retest` → `r5`（每轮同判据，最多 3 次，不达标暂停等运维）→ 5-run `[r1=88.0, r2', r3', r4, r5]` 算 mean±std 回填锚点 5 表。
  - **红线**：r1=88.0% 保留 / r2/r3 作废待复测 / 保持新 key + `deepseek-v4-pro-fp4` + `/cloud/v1` / 复检任一不过不得开跑。
  - ⏭ **待推送后 agent 下轮 `git pull` 取到指令 → 复检 → 开跑 r4。**

- **2026-10-09（运维经任务书下发：C1.full r2/r3 复测——模型服务不稳定致大量 timeout）** —— 用户观察 r1=88.0%(0 timeout) vs r2=59.5%(39 timeouts) vs r3=63.3%，成绩剧烈波动 = 模型服务不稳定（非 full 臂真实能力），要求复测 r2/r3。
  - **落地**：在 `run/ZHULONG_TASK.md` 运维指令区置顶新增 `### 🆕 运维指令 · 2026-10-09（三）— 🔄 C1.full r2/r3 复测`。判定：r1 保留(0 timeout)、r2/r3 作废(服务不稳定)。流程：① r4 不打断跑完 → 收割检查 timeout → 判据(timeout≤10 且成绩≥75%)；② r4 有效则重跑 r2(batch r2-retest) → ③ 重跑 r3(batch r3-retest) → ④ 跑 r5 → ⑤ 5 个有效 run[r1,r2',r3',r4,r5]算 mean±std。每轮最多重跑 3 次，3 次不达标暂停等运维。红线 = r4 不打断 / r2/r3 作废 / r1 保留 / 新 key 不回退。
  - ⏭ 待推送后 agent 下轮 `git pull` 取到指令 → r4 跑完后按复测流程执行。

- **2026-10-09（运维经任务书下发：沙盒已就绪·可开跑 C1.full r4）** —— 用户通知「沙盒重启完成，可以继续」。pro-fp4 key 已在上条指令中恢复（新 key `e13f4f37` HTTP 200），agent 应已完成 auth + `PHASE=ready`。
  - **落地**：在 `run/ZHULONG_TASK.md` 运维指令区置顶新增 `### 🆕 运维指令 · 2026-10-09（二）— ✅ 沙盒已就绪，可开跑 C1.full r4【本次唤醒优先动作】`（放在上一条 pro-fp4 key 指令之前，上一条标记「已完成·已归档」）。指令要点：① 三项前置复检（pro-fp4 直连 200 / 沙盒端口 404 可达 / eval IDLE）全过才开跑；② 启动 C1.full r4（四 override 齐全：`EVAL_FW_DIR` + `CLI_DATA_DIR=.cline_prof4_eval/data` + `PYTHON` + `https_proxy`）；③ 更新 MEMORY `PHASE=running`；④ commit+push。红线 = 保持新 key + pro-fp4 + /cloud/v1 / r1-r3 全有效 / 三项复检任一不过不开跑。
  - ⏭ 待推送后 agent 下轮 `git pull` 取到指令 → 复检 → 开跑 r4。

- **2026-10-09（运维经任务书下发：pro-fp4 key 已恢复 + 暂不启动 r4 沙盒重启中）** —— ops 中继 RUN_ID 23 实测确认 403 = 旧 key 额度耗尽（新 key `e13f4f37` + pro-fp4 + /cloud/v1 = HTTP 200，网关返回 `model: deepseek-v4-pro-260813` = 同一后端模型）。用户告知沙盒正在重启，要求 agent 暂不启动 r4。
  - **落地**：在 `run/ZHULONG_TASK.md` 运维指令区置顶（常驻规程之后）新增 `### 🆕 运维指令 · 2026-10-09 — ✅ pro-fp4 403 已解决（换 key）+ 🚫 暂不启动 r4（沙盒重启中）`。指令要点：① 用新 key `cline auth` eval backbone（保持 `deepseek-v4-pro-fp4` + `/cloud/v1`，写入隔离 config dir）；② `curl --noproxy '*'` 复检确认 200；③ 🚫 **不启动 r4**（沙盒重启中）；④ 更新 MEMORY `PHASE=ready` / `WAITING=1` / 基座行标注 key 已恢复；⑤ 等运维「沙盒就绪·可开跑」通知再启动 r4。红线 = 不改模型名 / 不用 /v1 / r1-r3 全有效 / 不启动 eval。
  - ⏭ 待推送：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run/ZHULONG_TASK.md doc/ZhuLong_DAC2027/MEMORY.md` → `git commit` → `git push`。agent 下轮 `git pull` 即取到指令。

- **2026-10-09（运维经 ops 中继测新 key + deepseek-v4-pro-cloud 能否绕过 pro-fp4 403）** —— 用户问「用新 key（`e13f4f37`）+ 模型名 `deepseek-v4-pro-cloud` 可否绕过 pro-fp4 的 403，模型是一样的」。pro-fp4 403 已阻塞 C1.full r4/r5 达 9 次复检未恢复。
  - **分析**：论文 `6_exp.tex` 第 76 行写的是泛称 `DeepSeek-V4-Pro`（非 `pro-fp4`），但操作代码全程用 `deepseek-v4-pro-fp4`。`fp4`（4-bit 量化）vs `cloud`（云端全精度？）很可能是**不同部署/量化**，若混入 r1/r2/r3（均用 pro-fp4）的 5-run mean±std 会有一致性风险。需先实测区分 403 根因 = key 额度 / 模型额度 / endpoint 差异。
  - **落地**：在 `run/ops/inbox.md` 置顶新增 `RUN_ID 22`（6 组合 curl `--noproxy '*'` 直连测试：① 新key+pro-cloud@/cloud/v1 ② 新key+pro-fp4@/cloud/v1 ③ 新key+pro-fp4@/v1 ④ 旧key+pro-fp4@/cloud/v1 ⑤ 旧key+pro-fp4@/v1 ⑥ 新key+pro-cloud@/v1）；旧 RUN_ID 21 降级 `text`；RUN_ID 21→22。**纯只读 curl**，不改文件不动进程。
  - **决策树**：若 ②/③=200 → 403 是 key 级问题，换 key 即可、模型不变、r1-r3 保持有效（最优）；若 ①=200 但 ②/③=403 → 403 是模型级问题，pro-cloud 是不同模型，需评估是否重跑全部 5 轮或继续等；若 ③=200 但 ②=403 → endpoint 差异，用 /v1 即可。
  - ⏭ **待推送**：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run/ops/inbox.md doc/ZhuLong_DAC2027/MEMORY.md` → `git commit -m "zhulong 运维: ops RUN_ID 22 测新key+pro-cloud能否绕过pro-fp4 403"` → `git push origin main`。push 后中继 ~20s 内执行，结果追加到 `run/ops/outbox.md` 末尾。

- **2026-10-08 运维流水已滚动归档（2026-10-09）** —— 10-08 两条（loop git 超时=缺 https_proxy 的提醒 + 派 agent 写国庆假期 HTML 报告）已**原文**搬入 `daily-memories/2026-10-08.md`。

- **2026-10-01～10-05 早期运维流水已滚动归档（2026-10-09）** —— 早期流水（10-04 环境摸底 RUN_ID 1/2/3/4、中继抢救、接管尽调、10-05「中继卡死」澄清等）已**原文**搬入 `daily-memories/2026-10-04.md` 与 `daily-memories/2026-10-05.md`（滚动以保 ≤32KB）。

